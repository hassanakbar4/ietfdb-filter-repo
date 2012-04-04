import re, os, string, datetime

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse as urlreverse
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django import forms
from django.forms.util import ErrorList
from django.utils import simplejson
from django.utils.html import strip_tags
from django.conf import settings

from ietf.utils.mail import send_mail_text, send_mail_preformatted
from ietf.ietfauth.decorators import has_role, role_required
from ietf.iesg.models import TelechatDate
from ietf.doc.models import *
from ietf.name.models import *
from ietf.person.models import *
from ietf.group.models import *
from ietf.group.utils import save_group_in_history
from ietf.wgcharter.mails import *
from ietf.wgcharter.utils import *


class ChangeStateForm(forms.Form):
    charter_state = forms.ModelChoiceField(State.objects.filter(type="charter", slug__in=["infrev", "intrev", "extrev", "iesgrev", "approved"]), label="Charter state", empty_label=None, required=False)
    initial_time = forms.IntegerField(initial=0, label="Review time", help_text="(in weeks)", required=False)
    message = forms.CharField(widget=forms.Textarea, help_text="Optional message to the Secretariat", required=False)
    comment = forms.CharField(widget=forms.Textarea, help_text="Optional comment for the charter history", required=False)
    def __init__(self, *args, **kwargs):
        self.hide = kwargs.pop('hide', None)
        super(ChangeStateForm, self).__init__(*args, **kwargs)
        # hide requested fields
        if self.hide:
            for f in self.hide:
                self.fields[f].widget = forms.HiddenInput

@role_required("Area Director", "Secretariat")
def change_state(request, name, option=None):
    """Change state of WG and charter, notifying parties as necessary
    and logging the change as a comment."""
    # Get WG by acronym, redirecting if there's a newer acronym
    try:
        wg = Group.objects.get(acronym=name)
    except Group.DoesNotExist:
        old = GroupHistory.objects.filter(acronym=name)
        if old:
            return redirect('wg_change_state', name=old[0].group.acronym)
        else:
            raise Http404()

    charter = set_or_create_charter(wg)

    initial_review = charter.latest_event(InitialReviewDocEvent, type="initial_review")
    if charter.get_state_slug() != "infrev" or (initial_review and initial_review.expires < datetime.datetime.now()):
        initial_review = None

    login = request.user.get_profile()

    if request.method == 'POST':
        form = ChangeStateForm(request.POST)
        if form.is_valid():
            clean = form.cleaned_data
            if option == "initcharter" or option == "recharter":
                charter_state = State.objects.get(type="charter", slug="infrev")
                charter_rev = charter.rev
            elif option == "abandon":
                if wg.state_id == "proposed":
                    charter_state = State.objects.get(type="charter", slug="notrev")
                else:
                    charter_state = State.objects.get(type="charter", slug="approved")
                charter_rev = approved_revision(charter.rev)
            else:
                charter_state = clean['charter_state']
                charter_rev = charter.rev

            comment = clean['comment'].rstrip()
            message = clean['message']

            if charter_state != charter.get_state():
                # Charter state changed
                save_document_in_history(charter)

                prev = charter.get_state()
                charter.set_state(charter_state)
                charter.rev = charter_rev

                if option != "abandon":
                    log_state_changed(request, charter, login, prev)
                else:
                    # Special log for abandoned efforts
                    e = DocEvent(type="changed_document", doc=charter, by=login)
                    e.desc = "IESG has abandoned the chartering effort"
                    e.save()

                if comment:
                    c = DocEvent(type="added_comment", doc=charter, by=login)
                    c.desc = comment
                    c.save()

                charter.time = datetime.datetime.now()
                charter.save()

                if message:
                    email_secretariat(request, wg, "state-%s" % charter_state.slug, message)

                if charter_state.slug == "intrev" and not charter.latest_event(BallotDocEvent, type="created_ballot", ballot_type__slug="r-extrev"):
                    e = BallotDocEvent(type="created_ballot", by=login, doc=charter)
                    e.ballot_type = BallotType.objects.get(doc_type=charter.type, slug="r-extrev")
                    e.desc = u"Created ballot for approving charter for external review"
                    e.save()
                elif charter_state.slug == "iesgrev" and not charter.latest_event(BallotDocEvent, type="created_ballot", ballot_type__slug="approve"):
                    e = BallotDocEvent(type="created_ballot", by=login, doc=charter)
                    e.ballot_type = BallotType.objects.get(doc_type=charter.type, slug="approve")
                    e.desc = u"Created ballot for approving charter"
                    e.save()

            if charter_state.slug == "infrev" and clean["initial_time"] and clean["initial_time"] != 0:
                e = InitialReviewDocEvent(type="initial_review", by=login, doc=charter)
                e.expires = datetime.datetime.now() + datetime.timedelta(weeks=clean["initial_time"])
                e.desc = "Initial review time expires %s" % e.expires.strftime("%Y-%m-%d")
                e.save()

            return redirect('doc_view', name=charter.name)
    else:
        if option == "recharter":
            hide = ['charter_state']
            init = dict(initial_time=1, message="%s has initiated a recharter effort on the WG %s (%s)" % (login.plain_name(), wg.name, wg.acronym))
        elif option == "initcharter":
            hide = ['charter_state']
            init = dict(initial_time=1, message="%s has initiated chartering of the proposed WG %s (%s)" % (login.plain_name(), wg.name, wg.acronym))
        elif option == "abandon":
            hide = ['initial_time', 'charter_state']
            init = dict(message="%s has abandoned the chartering effort on the WG %s (%s)" % (login.plain_name(), wg.name, wg.acronym))
        else:
            hide = ['initial_time']
            s = charter.get_state()
            init = dict(charter_state=s.pk if s else None)
        form = ChangeStateForm(hide=hide, initial=init)

    prev_charter_state = None
    charter_hists = DocHistory.objects.filter(doc=charter).exclude(states__type="charter", states__slug=charter.get_state_slug()).order_by("-time")[:1]
    if charter_hists:
        prev_charter_state = charter_hists[0].get_state()

    title = {
        "initcharter": "Initiate chartering of WG %s" % wg.acronym,
        "recharter": "Recharter WG %s" % wg.acronym,
        "abandon": "Abandon effort on WG %s" % wg.acronym,
        }.get(option)
    if not title:
        title = "Change state of WG %s" % wg.acronym

    def state_pk(slug):
        return State.objects.get(type="charter", slug=slug).pk

    messages = {
        state_pk("infrev"): "The WG %s (%s) has been set to Informal IESG review by %s." % (wg.name, wg.acronym, login.plain_name()),
        state_pk("intrev"): "The WG %s (%s) has been set to Internal review by %s. Please place it on the next IESG telechat and inform the IAB." % (wg.name, wg.acronym, login.plain_name()),
        state_pk("extrev"): "The WG %s (%s) has been set to External review by %s. Please send out the external review announcement to the appropriate lists.\n\nSend the announcement to other SDOs: Yes\nAdditional recipients of the announcement: " % (wg.name, wg.acronym, login.plain_name()),
        }

    return render_to_response('wgcharter/change_state.html',
                              dict(form=form,
                                   wg=wg,
                                   login=login,
                                   option=option,
                                   prev_charter_state=prev_charter_state,
                                   title=title,
                                   initial_review=initial_review,
                                   messages=simplejson.dumps(messages)),
                              context_instance=RequestContext(request))

class TelechatForm(forms.Form):
    telechat_date = forms.TypedChoiceField(coerce=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').date(), empty_value=None, required=False)

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        dates = [d.date for d in TelechatDate.objects.active().order_by('date')]
        init = kwargs['initial'].get("telechat_date")
        if init and init not in dates:
            dates.insert(0, init)

        self.fields['telechat_date'].choices = [("", "(not on agenda)")] + [(d, d.strftime("%Y-%m-%d")) for d in dates]
        

@role_required("Area Director", "Secretariat")
def telechat_date(request, name):
    wg = get_object_or_404(Group, acronym=name)
    doc = set_or_create_charter(wg)
    login = request.user.get_profile()

    e = doc.latest_event(TelechatDocEvent, type="scheduled_for_telechat")

    initial = dict(telechat_date=e.telechat_date if e else None)
    if request.method == "POST":
        form = TelechatForm(request.POST, initial=initial)

        if form.is_valid():
            update_telechat(request, doc, login, form.cleaned_data['telechat_date'])
            return redirect("doc_view", name=doc.name)
    else:
        form = TelechatForm(initial=initial)

    return render_to_response('wgcharter/edit_telechat_date.html',
                              dict(doc=doc,
                                   form=form,
                                   user=request.user,
                                   login=login),
                              context_instance=RequestContext(request))

class UploadForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea, label="Charter text", help_text="Edit the charter text", required=False)
    txt = forms.FileField(label=".txt format", help_text="Or upload a .txt file", required=False)

    def clean_content(self):
        return self.cleaned_data["content"].replace("\r", "")

    def save(self, wg, rev):
        fd = self.cleaned_data['txt']
        filename = os.path.join(settings.CHARTER_PATH, 'charter-ietf-%s-%s.txt' % (wg.acronym, rev))
        if fd:
            # A file was specified. Save it.
            destination = open(filename, 'wb+')
            for chunk in fd.chunks():
                destination.write(chunk)
            destination.close()
        else:
            # No file, save content
            destination = open(filename, 'wb+')
            content = self.cleaned_data['content']
            destination.write(content)
            destination.close()

@role_required('Area Director','Secretariat')
def submit(request, name):
    # Get WG by acronym, redirecting if there's a newer acronym
    try:
        wg = Group.objects.get(acronym=name)
    except Group.DoesNotExist:
        wglist = GroupHistory.objects.filter(acronym=name)
        if wglist:
            return redirect('charter_submit', name=wglist[0].group.acronym)
        else:
            raise Http404()
    # Get charter
    charter = set_or_create_charter(wg)
    
    login = request.user.get_profile()

    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            save_document_in_history(charter)
            # Also save group history so we can search for it
            save_group_in_history(wg)

            # Search history for possible collisions with abandoned efforts
            rev_list = list(charter.history_set.order_by('-time').values_list('rev', flat=True))
            next_rev = next_revision(charter.rev)
            while next_rev in rev_list:
                next_rev = next_revision(next_rev)

            charter.rev = next_rev

            e = DocEvent()
            e.type = "new_revision"
            e.by = login
            e.doc = charter
            e.desc = "New version available: <b>charter-ietf-%s-%s.txt</b>" % (wg.acronym, charter.rev)
            e.save()
            
            # Save file on disk
            form.save(wg, charter.rev)

            charter.time = datetime.datetime.now()
            charter.save()

            return HttpResponseRedirect(reverse('doc_view', kwargs={'name': charter.name}))
    else:
        filename = os.path.join(settings.CHARTER_PATH, 'charter-ietf-%s-%s.txt' % (wg.acronym, wg.charter.rev))
        try:
            charter_text = open(filename, 'r')
            init = dict(content=charter_text.read())
        except IOError:
            init = {}
        form = UploadForm(initial = init)
    return render_to_response('wgcharter/submit.html',
                              {'form': form,
                               'next_rev': next_revision(wg.charter.rev),
                               'wg': wg},
                              context_instance=RequestContext(request))

def default_action_text(wg, charter, user, action):
    e = WriteupDocEvent(doc=charter, by=user)
    e.by = user
    e.type = "changed_action_announcement"
    e.desc = "WG action text was changed"

    info = {}
    info['chairs'] = [{ 'name': x.person.plain_name(), 'email': x.email.address} for x in wg.role_set.filter(name="Chair")]
    info['secr'] = [{ 'name': x.person.plain_name(), 'email': x.email.address} for x in wg.role_set.filter(name="Secr")]
    info['techadv'] = [{ 'name': x.person.plain_name(), 'email': x.email.address} for x in wg.role_set.filter(name="Techadv")]
    info['ad'] = {'name': wg.ad.plain_name(), 'email': wg.ad.role_email("ad").address } if wg.ad else None,
    info['list'] = wg.list_email if wg.list_email else None,
    info['list_subscribe'] = str(wg.list_subscribe) if wg.list_subscribe else None,
    info['list_archive'] = str(wg.list_archive) if wg.list_archive else None,

    filename = os.path.join(settings.CHARTER_PATH, '%s-%s.txt' % (wg.charter.canonical_name(), wg.charter.rev))
    try:
        charter_text = open(filename, 'r')
        info['charter_txt'] = charter_text.read()
    except IOError:
        info['charter_txt'] = "Error: couldn't read charter text"

    e.text = render_to_string("wgcharter/action_text.txt",
                              dict(wg=wg,
                                   charter_url=settings.IDTRACKER_BASE_URL + charter.get_absolute_url(),
                                   action_type=action,
                                   info=info,
                                   ))

    e.save()
    return e

def default_review_text(wg, charter, user):
    e = WriteupDocEvent(doc=charter, by=user)
    e.by = user
    e.type = "changed_review_announcement"
    e.desc = "WG review text was changed"
    info = {}
    info['chairs'] = [{ 'name': x.person.plain_name(), 'email': x.email.address} for x in wg.role_set.filter(name="Chair")]
    info['secr'] = [{ 'name': x.person.plain_name(), 'email': x.email.address} for x in wg.role_set.filter(name="Secr")]
    info['techadv'] = [{ 'name': x.person.plain_name(), 'email': x.email.address} for x in wg.role_set.filter(name="Techadv")]
    info['ad'] = {'name': wg.ad.plain_name(), 'email': wg.ad.role_email("ad").address } if wg.ad else None,
    info['list'] = wg.list_email if wg.list_email else None,
    info['list_subscribe'] = wg.list_subscribe if wg.list_subscribe else None,
    info['list_archive'] = wg.list_archive if wg.list_archive else None,

    info['bydate'] = (date.today() + timedelta(weeks=1)).isoformat()

    filename = os.path.join(settings.CHARTER_PATH, '%s-%s.txt' % (wg.charter.canonical_name(), wg.charter.rev))
    try:
        charter_text = open(filename, 'r')
        info['charter_txt'] = charter_text.read()
    except IOError:
        info['charter_txt'] = "Error: couldn't read charter text"

    e.text = render_to_string("wgcharter/review_text.txt",
                              dict(wg=wg,
                                   charter_url=settings.IDTRACKER_BASE_URL + charter.get_absolute_url(),
                                   info=info,
                                   review_type="new" if wg.state_id == "proposed" else "recharter",
                                   )
                              )
    e.save()
    return e

class AnnouncementTextForm(forms.Form):
    announcement_text = forms.CharField(widget=forms.Textarea, required=True)

    def clean_announcement_text(self):
        return self.cleaned_data["announcement_text"].replace("\r", "")

@role_required('Area Director','Secretariat')
def announcement_text(request, name, ann):
    """Editing of announcement text"""
    try:
        wg = Group.objects.get(acronym=name)
    except Group.DoesNotExist:
        wglist = GroupHistory.objects.filter(acronym=name)
        if wglist:
            return redirect('wg_announcement_text', name=wglist[0].group.acronym)
        else:
            raise Http404

    charter = set_or_create_charter(wg)

    login = request.user.get_profile()

    if ann == "action":
        existing = charter.latest_event(WriteupDocEvent, type="changed_action_announcement")
    elif ann == "review":
        existing = charter.latest_event(WriteupDocEvent, type="changed_review_announcement")
    if not existing:
        if ann == "action":
            if next_approved_revision(wg.charter.rev) == "01":
                existing = default_action_text(wg, charter, login, "Formed")
            else:
                existing = default_action_text(wg, charter, login, "Rechartered")
        elif ann == "review":
            existing = default_review_text(wg, charter, login)

    form = AnnouncementTextForm(initial=dict(announcement_text=existing.text))

    if request.method == 'POST':
        form = AnnouncementTextForm(request.POST)
        if "save_text" in request.POST and form.is_valid():
            t = form.cleaned_data['announcement_text']
            if t != existing.text:
                e = WriteupDocEvent(doc=charter, by=login)
                e.by = login
                e.type = "changed_%s_announcement" % ann
                e.desc = "WG %s text was changed" % ann
                e.text = t
                e.save()
                
                charter.time = e.time
                charter.save()
            return redirect('doc_writeup', name=charter.name)

        if "regenerate_text" in request.POST:
            if ann == "action":
                if next_approved_revision(wg.charter.rev) == "01":
                    e = default_action_text(wg, charter, login, "Formed")
                else:
                    e = default_action_text(wg, charter, login, "Rechartered")
            elif ann == "review":
                e = default_review_text(wg, charter, login)
            # make sure form has the updated text
            form = AnnouncementTextForm(initial=dict(announcement_text=e.text))

        if "send_text" in request.POST and form.is_valid():
            msg = form.cleaned_data['announcement_text']
            import email
            parsed_msg = email.message_from_string(msg.encode("utf-8"))

            send_mail_text(request, parsed_msg["To"],
                           parsed_msg["From"], parsed_msg["Subject"],
                           parsed_msg.get_payload())
            return redirect('doc_writeup', name=charter.name)

    return render_to_response('wgcharter/announcement_text.html',
                              dict(charter=charter,
                                   announcement=ann,
                                   back_url=charter.get_absolute_url(),
                                   announcement_text_form=form,
                                   ),
                              context_instance=RequestContext(request))

class BallotWriteupForm(forms.Form):
    ballot_writeup = forms.CharField(widget=forms.Textarea, required=True)

    def clean_ballot_writeup(self):
        return self.cleaned_data["ballot_writeup"].replace("\r", "")
        
@role_required('Area Director','Secretariat')
def ballot_writeupnotes(request, name):
    """Editing of ballot write-up and notes"""
    try:
        wg = Group.objects.get(acronym=name)
    except Group.DoesNotExist:
        wglist = GroupHistory.objects.filter(acronym=name)
        if wglist:
            return redirect('wg_ballot_writeupnotes', name=wglist[0].group.acronym)
        else:
            raise Http404

    charter = set_or_create_charter(wg)

    started_process = charter.latest_event(type="started_iesg_process")
    if not started_process:
        raise Http404()

    login = request.user.get_profile()

    approval = charter.latest_event(WriteupDocEvent, type="changed_action_announcement")
    
    existing = charter.latest_event(WriteupDocEvent, type="changed_ballot_writeup_text")
    if not existing:
        existing = generate_ballot_writeup(request, charter)

    reissue = charter.latest_event(DocEvent, type="sent_ballot_announcement")
        
    form = BallotWriteupForm(initial=dict(ballot_writeup=existing.text))

    if request.method == 'POST' and "save_ballot_writeup" in request.POST or "issue_ballot" in request.POST:
        form = BallotWriteupForm(request.POST)
        if form.is_valid():
            t = form.cleaned_data["ballot_writeup"]
            if t != existing.text:
                e = WriteupDocEvent(doc=charter, by=login)
                e.by = login
                e.type = "changed_ballot_writeup_text"
                e.desc = "Ballot writeup was changed"
                e.text = t
                e.save()

            if "issue_ballot" in request.POST and approval:
                if has_role(request.user, "Area Director") and not charter.latest_event(GroupBallotPositionDocEvent, ad=login, time__gte=started_process.time):
                    # sending the ballot counts as a yes
                    pos = GroupBallotPositionDocEvent(doc=charter, by=login)
                    pos.type = "changed_ballot_position"
                    pos.ad = login
                    pos.pos_id = "yes"
                    pos.desc = "[Ballot Position Update] New position, %s, has been recorded for %s" % (pos.pos.name, pos.ad.plain_name())
                    pos.save()

                msg = generate_issue_ballot_mail(request, charter)
                send_mail_preformatted(request, msg)

                e = DocEvent(doc=charter, by=login)
                e.by = login
                e.type = "sent_ballot_announcement"
                e.desc = "Ballot has been issued"
                e.save()

                return render_to_response('wgcharter/ballot_issued.html',
                                          dict(charter=charter,
                                               back_url=charter.get_absolute_url()),
                                          context_instance=RequestContext(request))
                        

    return render_to_response('wgcharter/ballot_writeupnotes.html',
                              dict(charter=charter,
                                   back_url=charter.get_absolute_url(),
                                   ballot_issued=bool(charter.latest_event(type="sent_ballot_announcement")),
                                   ballot_writeup_form=form,
                                   reissue=reissue,
                                   approval=approval,
                                   ),
                              context_instance=RequestContext(request))

@role_required("Secretariat")
def approve_ballot(request, name):
    """Approve ballot, changing state, copying charter"""
    try:
        wg = Group.objects.get(acronym=name)
    except Group.DoesNotExist:
        wglist = GroupHistory.objects.filter(acronym=name)
        if wglist:
            return redirect('wg_approve_ballot', name=wglist[0].group.acronym)
        else:
            raise Http404

    charter = set_or_create_charter(wg)

    login = request.user.get_profile()

    e = charter.latest_event(WriteupDocEvent, type="changed_action_announcement")
    if not e:
        if next_approved_revision(wg.charter.rev) == "01":
            announcement = default_action_text(wg, charter, login, "Formed").text
        else:
            announcement = default_action_text(wg, charter, login, "Rechartered").text
    else:
        announcement = e.text

    if request.method == 'POST':
        new_state = GroupStateName.objects.get(slug="active")
        new_charter_state = State.objects.get(type="charter", slug="approved")

        save_document_in_history(charter)
        save_group_in_history(wg)

        prev_state = wg.state
        prev_charter_state = charter.get_state()
        wg.state = new_state
        charter.set_state(new_charter_state)

        e = DocEvent(doc=charter, by=login)
        e.type = "iesg_approved"
        e.desc = "IESG has approved the charter"
        e.save()
        
        change_description = e.desc + " and WG state has been changed to %s" % new_state.name
        
        e = log_state_changed(request, charter, login, prev_state)
        
        wg.time = e.time
        wg.save()

        ch = get_charter_for_revision(wg.charter, wg.charter.rev)

        filename = os.path.join(charter.get_file_path(), ch.name+"-"+ch.rev+".txt")
        try:
            source = open(filename, 'rb')
            raw_content = source.read()

            new_filename = os.path.join(charter.get_file_path(), 'charter-ietf-%s-%s.txt' % (wg.acronym, next_approved_revision(ch.rev)))
            destination = open(new_filename, 'wb+')
            destination.write(raw_content)
            destination.close()
        except IOError:
            raise Http404("Charter text %s" % filename)

        charter.rev = next_approved_revision(charter.rev)
        charter.save()
        
        email_secretariat(request, wg, "state-%s" % new_charter_state.slug, change_description)

        # send announcement
        send_mail_preformatted(request, announcement)

        return HttpResponseRedirect(charter.get_absolute_url())
    
    return render_to_response('wgcharter/approve_ballot.html',
                              dict(charter=charter,
                                   announcement=announcement,
                                   wg=wg),
                              context_instance=RequestContext(request))

