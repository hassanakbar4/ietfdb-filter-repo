# Copyright The IETF Trust 2019-2020, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-09-05 05:03


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0015_populate_completed_on_for_rejected'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalreviewersettings',
            name='remind_days_open_reviews',
            field=models.PositiveIntegerField(blank=True, name="Periodic reminder of open reviews every X days", help_text="To get a periodic email reminder of all your open reviews, enter the number of days between these reminders. Clear the field if you don't want these reminders.", null=True),
        ),
        migrations.AddField(
            model_name='reviewersettings',
            name='remind_days_open_reviews',
            field=models.PositiveIntegerField(blank=True, verbose_name="Periodic reminder of open reviews every X days", help_text="To get a periodic email reminder of all your open reviews, enter the number of days between these reminders. Clear the field if you don't want these reminders.", null=True),
        ),
    ]
