# Copyright The IETF Trust 2018-2019, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-25 12:07


from __future__ import absolute_import, print_function, unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ipr', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='iprdisclosurebase',
            options={'ordering': ['-time', '-id']},
        ),
    ]
