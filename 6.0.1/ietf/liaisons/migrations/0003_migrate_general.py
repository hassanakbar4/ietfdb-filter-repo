# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def migrate_tags(apps, schema_editor):
    LiaisonStatement = apps.get_model("liaisons", "LiaisonStatement")
    for s in LiaisonStatement.objects.filter(action_taken=True):
        s.tags.add('taken')

def migrate_state(apps, schema_editor):
    LiaisonStatement = apps.get_model("liaisons", "LiaisonStatement")
    for s in LiaisonStatement.objects.all():
        if s.approved:
            s.state_id='approved'
        else:
            s.state_id='pending'
        s.save()
        
def create_events(apps, schema_editor):
    LiaisonStatement = apps.get_model("liaisons", "LiaisonStatement")
    LiaisonStatementEvent = apps.get_model("liaisons", "LiaisonStatementEvent")
    Person = apps.get_model("person","Person")
    system = Person.objects.get(name="(system)")
    for s in LiaisonStatement.objects.all():
        if s.submitted:
            event = LiaisonStatementEvent.objects.create(
                type_id='submitted',
                by=system,
                statement=s,
                desc='Statement Submitted')
            event.time=s.submitted
            event.save()
        if s.modified:
            event = LiaisonStatementEvent.objects.create(
                type_id='modified',
                by=system,
                statement=s,
                desc='Statement Modified')
            event.time=s.modified
            event.save()
        if s.approved:
            event = LiaisonStatementEvent.objects.create(
                type_id='approved',
                by=system,
                statement=s,
                desc='Statement Approved')
            event.time=s.approved
            event.save()

def migrate_relations(apps, schema_editor):
    LiaisonStatement = apps.get_model("liaisons", "LiaisonStatement")
    RelatedLiaisonStatement = apps.get_model("liaisons", "RelatedLiaisonStatement")
    for liaison in LiaisonStatement.objects.filter(related_to__isnull=False):
        RelatedLiaisonStatement.objects.create(
            source=liaison,
            target=liaison.related_to,
            relationship_id='reference')

def merge_reply_to(apps, schema_editor):
    """Merge contents of reply_to field into response_contact and create comment Event"""
    LiaisonStatement = apps.get_model("liaisons", "LiaisonStatement")
    LiaisonStatementEvent = apps.get_model("liaisons", "LiaisonStatementEvent")
    Person = apps.get_model("person","Person")
    system = Person.objects.get(name="(system)")
    for liaison in LiaisonStatement.objects.exclude(reply_to=''):
        if liaison.reply_to in liaison.response_contacts:
            continue
        LiaisonStatementEvent.objects.create(
            type_id='comment',
            statement=liaison,
            desc='Merged reply_to field into response_contacts\nOriginal reply_to: %s\nOriginal response_contacts: %s' % (liaison.reply_to, liaison.response_contacts),
            by=system
        )
        liaison.response_contacts += ',%s' % liaison.reply_to
        liaison.save()

class Migration(migrations.Migration):

    dependencies = [
        ('liaisons', '0002_schema_changes'),
    ]

    operations = [
        migrations.RunPython(migrate_tags),
        migrations.RunPython(migrate_state),
        migrations.RunPython(create_events),
        migrations.RunPython(migrate_relations),
        migrations.RunPython(merge_reply_to),
    ]
