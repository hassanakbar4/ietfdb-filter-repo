# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-01 03:32
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0010_iab_programs'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='role',
            options={'ordering': ['name_id']},
        ),
    ]
