# Copyright The IETF Trust 2019, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-08-07 12:07
from __future__ import unicode_literals

from django.db import migrations

def forward(apps, schema_editor):
    StateType = apps.get_model('doc','StateType')
    State = apps.get_model('doc','State')

    StateType.objects.create(slug='draft-iana-experts',label='IANA Experts State')
    State.objects.create(type_id='draft-iana-experts',
                         slug='need-experts',
                         name='Need IANA Expert(s)',
                         used=True,
                         desc='One or more registries need experts assigned',
                         order=0
                        )
    State.objects.create(type_id='draft-iana-experts',
                         slug='reviews-assigned',
                         name='Reviews assigned',
                         used=True,
                         desc='One or more expert reviews have been assigned',
                         order=1
                        )
    State.objects.create(type_id='draft-iana-experts',
                         slug='expert-issues',
                         name='Issues identified',
                         used=True,
                         desc='Some expert reviewers have identified issues',
                         order=2
                        )
    State.objects.create(type_id='draft-iana-experts',
                         slug='reviewers-ok',
                         name='Expert Reviews OK',
                         used=True,
                         desc='All expert reviews have been completed with no blocking issues',
                         order=2
                        )

def reverse(apps, schema_editor):
    StateType = apps.get_model('doc','StateType')
    State = apps.get_model('doc','State')

    State.objects.filter(type_id='draft-iana-experts', slug__in=('need-experts','reviews-assigned','reviews-complete')).delete()
    StateType.objects.filter(slug='draft-iana-experts').delete()



class Migration(migrations.Migration):

    dependencies = [
        ('doc', '0023_one_to_many_docalias'),
    ]

    operations = [
        migrations.RunPython(forward, reverse)
    ]
