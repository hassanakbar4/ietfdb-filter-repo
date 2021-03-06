# Copyright The IETF Trust 2020, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-02-11 04:47
from __future__ import unicode_literals

from django.db import migrations, models


def forward(apps, schema_editor):
    ConstraintName = apps.get_model("name", "ConstraintName")
    ConstraintName.objects.create(slug="timerange", desc="", penalty=100000,
                                  name="Can't meet within timerange")
    ConstraintName.objects.create(slug="time_relation", desc="", penalty=1000,
                                  name="Preference for time between sessions")
    ConstraintName.objects.create(slug="wg_adjacent", desc="", penalty=10000,
                                  name="Request for adjacent scheduling with another WG")


def reverse(apps, schema_editor):
    ConstraintName = apps.get_model("name", "ConstraintName")
    ConstraintName.objects.filter(slug__in=["timerange", "time_relation", "wg_adjacent"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('name', '0010_timerangename'),
        ('meeting', '0026_cancel_107_sessions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='constraint',
            name='day',
        ),
        migrations.AddField(
            model_name='constraint',
            name='time_relation',
            field=models.CharField(blank=True, choices=[('subsequent-days', 'Schedule the sessions on subsequent days'), ('one-day-seperation', 'Leave at least one free day in between the two sessions')], max_length=200),
        ),
        migrations.AddField(
            model_name='constraint',
            name='timeranges',
            field=models.ManyToManyField(to='name.TimerangeName'),
        ),
        migrations.AddField(
            model_name='session',
            name='joint_with_groups',
            field=models.ManyToManyField(related_name='sessions_joint_in', to='group.Group'),
        ),
        migrations.RunPython(forward, reverse),
    ]
