# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-20 10:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import ietf.utils.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CommunityList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='EmailSubscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notify_on', models.CharField(choices=[(b'all', b'All changes'), (b'significant', b'Only significant state changes')], default=b'all', max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='SearchRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rule_type', models.CharField(choices=[(b'group', b'All I-Ds associated with a particular group'), (b'area', b'All I-Ds associated with all groups in a particular Area'), (b'group_rfc', b'All RFCs associated with a particular group'), (b'area_rfc', b'All RFCs associated with all groups in a particular Area'), (b'state_iab', b'All I-Ds that are in a particular IAB state'), (b'state_iana', b'All I-Ds that are in a particular IANA state'), (b'state_iesg', b'All I-Ds that are in a particular IESG state'), (b'state_irtf', b'All I-Ds that are in a particular IRTF state'), (b'state_ise', b'All I-Ds that are in a particular ISE state'), (b'state_rfceditor', b'All I-Ds that are in a particular RFC Editor state'), (b'state_ietf', b'All I-Ds that are in a particular Working Group state'), (b'author', b'All I-Ds with a particular author'), (b'author_rfc', b'All RFCs with a particular author'), (b'ad', b'All I-Ds with a particular responsible AD'), (b'shepherd', b'All I-Ds with a particular document shepherd'), (b'name_contains', b'All I-Ds with particular text/regular expression in the name')], max_length=30)),
                ('text', models.CharField(blank=True, default=b'', max_length=255, verbose_name=b'Text/RegExp')),
                ('community_list', ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='community.CommunityList')),
            ],
        ),
    ]
