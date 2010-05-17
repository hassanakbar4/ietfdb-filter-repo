import re, os
from datetime import datetime, date, time, timedelta
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.template import RequestContext
from django import forms
from django.utils.html import strip_tags

from ietf.ietfauth.decorators import group_required
from ietf.idtracker.templatetags.ietf_filters import in_group
from ietf.idtracker.models import *
from ietf.iesg.models import *
#from ietf.idrfc.idrfc_wrapper import BallotWrapper, IdWrapper, RfcWrapper
from ietf import settings
from ietf.idrfc.mails import *

class ChangeStateForm(forms.Form):
    state = forms.ModelChoiceField(IDState.objects.all(), empty_label=None, required=True)
    substate = forms.ModelChoiceField(IDSubState.objects.all(), required=False)

def add_document_comment(request, doc, text):
    login = IESGLogin.objects.get(login_name=request.user.username)
    if not 'Earlier history' in text:
        text += " by %s" % login

    c = DocumentComment()
    c.document = doc.idinternal
    c.public_flag = True
    c.version = doc.revision_display()
    c.comment_text = text
    c.created_by = login
    c.rfc_flag = doc.idinternal.rfc_flag
    c.save()

def make_last_call(request, doc):
    try:
        ballot = doc.idinternal.ballot
    except BallotInfo.DoesNotExist:
        ballot = BallotInfo()
        ballot.ballot = doc.idinternal.ballot_id
        ballot.active = False
        ballot.last_call_text = generate_last_call_announcement(request, doc)
        ballot.approval_text = generate_approval_mail(request, doc)
        ballot.ballot_writeup = render_to_string("idrfc/ballot_writeup.txt")
        ballot.save()

    send_last_call_request(request, doc, ballot)
    add_document_comment(request, doc, "Last Call was requested")
    

@group_required('Area_Director','Secretariat')
def change_state(request, name):
    doc = get_object_or_404(InternetDraft, filename=name)
    if not doc.idinternal or doc.status.status == "Expired":
        raise Http404()

    login = IESGLogin.objects.get(login_name=request.user.username)

    if request.method == 'POST':
        form = ChangeStateForm(request.POST)
        if form.is_valid():
            state = form.cleaned_data['state']
            sub_state = form.cleaned_data['substate']
            internal = doc.idinternal
            if state != internal.cur_state or sub_state != internal.cur_sub_state:
                internal.change_state(state, sub_state)

                change = u"State changed to <b>%s</b> from <b>%s</b> by <b>%s</b>" % (internal.docstate(), format_document_state(internal.prev_state, internal.prev_sub_state), login)
                
                c = DocumentComment()
                c.document = internal
                c.public_flag = True
                c.version = doc.revision_display()
                c.comment_text = change
                c.created_by = login
                c.result_state = internal.cur_state
                c.origin_state = internal.prev_state
                c.rfc_flag = internal.rfc_flag
                c.save()

                internal.event_date = date.today()
                internal.mark_by = login
                internal.save()

                email_state_changed(request, doc, strip_tags(change))
                email_owner(request, doc, internal.job_owner, login, change)

                if internal.cur_state.document_state_id == IDState.LAST_CALL_REQUESTED:
                    make_last_call(request, doc)

                    return render_to_response('idrfc/last_call_requested.html',
                                              dict(doc=doc),
                                              context_instance=RequestContext(request))
                
            return HttpResponseRedirect(internal.get_absolute_url())

    else:
        init = dict(state=doc.idinternal.cur_state_id,
                    substate=doc.idinternal.cur_sub_state_id)
        form = ChangeStateForm(initial=init)

    next_states = IDNextState.objects.filter(cur_state=doc.idinternal.cur_state)
    prev_state_formatted = format_document_state(doc.idinternal.prev_state, doc.idinternal.prev_sub_state)

    return render_to_response('idrfc/change_state.html',
                              dict(form=form,
                                   doc=doc,
                                   prev_state_formatted=prev_state_formatted,
                                   next_states=next_states),
                              context_instance=RequestContext(request))

def dehtmlify_textarea_text(s):
    return s.replace("<br>", "\n").replace("<b>", "").replace("</b>", "").replace("  ", " ")

def parse_date(s):
    return date(*tuple(int(x) for x in s.split('-')))

class EditInfoForm(forms.Form):
    intended_status = forms.ModelChoiceField(IDIntendedStatus.objects.all(), empty_label=None, required=True)
    status_date = forms.DateField(required=False)
    group = forms.ModelChoiceField(Acronym.objects.filter(area__status=Area.ACTIVE), label="Area acronym", required=False)
    via_rfc_editor = forms.BooleanField(required=False, label="Via IRTF or RFC Editor")
    job_owner = forms.ModelChoiceField(IESGLogin.objects.filter(user_level__in=(1, 2)).order_by('user_level', 'last_name'), label="Responsible AD", empty_label=None, required=True)
    state_change_notice_to = forms.CharField(max_length=255, label="Notice emails", help_text="Separate email addresses with commas", required=False)
    note = forms.CharField(widget=forms.Textarea, label="IESG note", required=False)
    telechat_date = forms.TypedChoiceField(coerce=parse_date, empty_value=None, required=False)
    returning_item = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        # separate active ADs from inactive
        choices = []
        objects = IESGLogin.objects.in_bulk([t[0] for t in self.fields['job_owner'].choices])
        separated = False
        for t in self.fields['job_owner'].choices:
            if objects[t[0]].user_level != 1 and not separated:
                choices.append(("", "----------------"))
                separated = True
            choices.append(t)
        self.fields['job_owner'].choices = choices
        
        # telechat choices
        today = date.today()
        dates = TelechatDates.objects.all()[0].dates()
        init = self.fields['telechat_date'].initial
        if init and init not in dates:
            dates.insert(0, init)

        choices = [(d, d.strftime("%Y-%m-%d")) for d in dates]
        choices.insert(0, ("", "(not on agenda)"))

        self.fields['telechat_date'].choices = choices
    
    def clean_status_date(self):
        d = self.cleaned_data['status_date']
        if d:
            if d < date.today():
                raise forms.ValidationError("Date must not be in the past.")
            if d >= date.today() + timedelta(days=365 * 2):
                raise forms.ValidationError("Date must be within two years.")
        
        return d

    def clean_note(self):
        # note is stored munged in the database
        return self.cleaned_data['note'].replace('\n', '<br>').replace('\r', '').replace('  ', '&nbsp; ')


@group_required('Area_Director','Secretariat')
def edit_info(request, name):
    doc = get_object_or_404(InternetDraft, filename=name)
    if not doc.idinternal or doc.status.status == "Expired":
        raise Http404()

    login = IESGLogin.objects.get(login_name=request.user.username)

    initial_telechat_date = doc.idinternal.telechat_date if doc.idinternal.agenda else None

    if request.method == 'POST':
        form = EditInfoForm(request.POST,
                            initial=dict(telechat_date=initial_telechat_date,
                                         group=doc.group_id))
        if form.is_valid():
            changes = []
            r = form.cleaned_data
            entry = "%s has been changed to <b>%s</b> from <b>%s</b>"
            orig_job_owner = doc.idinternal.job_owner
            
            if r['intended_status'] != doc.intended_status:
                changes.append(entry % ("Intended Status", r['intended_status'], doc.intended_status))
                doc.intended_status = r['intended_status']

            if r['status_date'] != doc.idinternal.status_date:
                changes.append(entry % ("Status date",
                                        r['status_date'],
                                        doc.idinternal.status_date))
                doc.idinternal.status_date = r['status_date']

            if 'group' in r and r['group'] and r['group'] != doc.group and doc.group_id == Acronym.INDIVIDUAL_SUBMITTER:
                changes.append(entry % ("Area acronym", r['group'], doc.group))
                doc.group = r['group']
                
            if r['job_owner'] != doc.idinternal.job_owner:
                changes.append(entry % ("Responsible AD",
                                        r['job_owner'],
                                        doc.idinternal.job_owner))
                doc.idinternal.job_owner = r['job_owner']

            if r['state_change_notice_to'] != doc.idinternal.state_change_notice_to:
                changes.append(entry % ("State Change Notice email list",
                                        r['state_change_notice_to'],
                                        doc.idinternal.state_change_notice_to))
                doc.idinternal.state_change_notice_to = r['state_change_notice_to']

            # coalesce some of the changes into one comment
            if changes:
                add_document_comment(request, doc, "<br>".join(changes))
                
            if r['note'] != doc.idinternal.note:
                if not r['note']:
                    if doc.idinternal.note:
                        add_document_comment(request, doc, "Note field has been cleared")
                else:
                    if doc.idinternal.note:
                        add_document_comment(request, doc, "[Note]: changed to '%s'" % r['note'])
                    else:
                        add_document_comment(request, doc, "[Note]: '%s' added" % r['note'])
                    
                doc.idinternal.note = r['note']


            on_agenda = bool(r['telechat_date'])

            updated_internal_item = False
            if doc.idinternal.returning_item != bool(r['returning_item']):
                doc.idinternal.returning_item = bool(r['returning_item'])
                updated_internal_item = True

            # update returning item
            if on_agenda and doc.idinternal.agenda and r['telechat_date'] != doc.idinternal.telechat_date and not updated_internal_item:
                doc.idinternal.returning_item = True
                
            if doc.idinternal.agenda != on_agenda:
                if on_agenda:
                    add_document_comment(request, doc, "Placed on agenda for telechat - %s" % r['telechat_date'])
                else:
                    add_document_comment(request, doc, "Removed from agenda for telechat")
                doc.idinternal.agenda = on_agenda
            elif on_agenda and r['telechat_date'] != doc.idinternal.telechat_date:
                add_document_comment(request, doc, entry % ("Telechat date", r['telechat_date'], doc.idinternal.telechat_date))
                doc.idinternal.telechat_date = r['telechat_date']

            if in_group(request.user, 'Secretariat'):
                doc.idinternal.via_rfc_editor = bool(r['via_rfc_editor'])
                
            doc.idinternal.token_name = doc.idinternal.email_display = str(doc.idinternal.job_owner)
            doc.idinternal.token_email = doc.idinternal.job_owner.person.email()[1]
            doc.idinternal.mark_by = login
            doc.idinternal.event_date = date.today()

            if changes:
                email_owner(request, doc, orig_job_owner, login, "\n".join(changes))
            doc.idinternal.save()
            doc.save()
            return HttpResponseRedirect(doc.idinternal.get_absolute_url())
    else:
        init = dict(intended_status=doc.intended_status_id,
                    status_date=doc.idinternal.status_date,
                    group=doc.group_id,
                    job_owner=doc.idinternal.job_owner_id,
                    state_change_notice_to=doc.idinternal.state_change_notice_to,
                    note=dehtmlify_textarea_text(doc.idinternal.note),
                    telechat_date=initial_telechat_date,
                    returning_item=doc.idinternal.returning_item,
                    )
        form = EditInfoForm(initial=init)

    form.standard_fields = [x for x in form.visible_fields() if x.name not in ('returning_item',)]

    if not in_group(request.user, 'Secretariat'):
        form.standard_fields = [x for x in form.standard_fields if x.name != "via_rfc_editor"]
        
    # show group only if none has been assigned yet
    if doc.group_id != Acronym.INDIVIDUAL_SUBMITTER:
        form.standard_fields = [x for x in form.standard_fields if x.name != "group"]
        
    return render_to_response('idrfc/edit_info.html',
                              dict(form=form,
                                   user=request.user,
                                   login=login),
                              context_instance=RequestContext(request))


@group_required('Area_Director','Secretariat')
def request_resurrect(request, name):
    doc = get_object_or_404(InternetDraft, filename=name)
    if not doc.idinternal or doc.status.status != "Expired":
        raise Http404()

    login = IESGLogin.objects.get(login_name=request.user.username)

    if request.method == 'POST':
        email_resurrect_requested(request, doc, login)
        add_document_comment(request, doc, "Resurrection was requested")
        doc.idinternal.resurrect_requested_by = login
        doc.idinternal.save()
        return HttpResponseRedirect(doc.idinternal.get_absolute_url())
  
    return render_to_response('idrfc/request_resurrect.html',
                              dict(doc=doc),
                              context_instance=RequestContext(request))
