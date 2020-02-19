# Copyright The IETF Trust 2018-2019, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-05-21 12:07


from __future__ import absolute_import, print_function, unicode_literals

from django.db import migrations

def forward(apps, schema_editor):
    MailTrigger = apps.get_model('mailtrigger','MailTrigger')
    Recipient = apps.get_model('mailtrigger', 'Recipient')

    conflrev_ad_changed = MailTrigger.objects.create(
        slug = 'conflrev_ad_changed',
        desc = 'Recipients when the responsible AD for a conflict review is changed',
    )
    conflrev_ad_changed.to.set(Recipient.objects.filter(slug='iesg-secretary'))
    conflrev_ad_changed.cc.set(Recipient.objects.filter(slug__in=[
            'conflict_review_steering_group',
            'conflict_review_stream_manager',
            'doc_affecteddoc_authors',
            'doc_affecteddoc_group_chairs',
            'doc_affecteddoc_notify',
            'doc_notify',
            'iesg',
        ]))


def reverse(apps, schema_editor):
    MailTrigger = apps.get_model('mailtrigger','MailTrigger')
    MailTrigger.objects.filter(slug='conflrev_ad_changed').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('mailtrigger', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forward, reverse)
    ]
