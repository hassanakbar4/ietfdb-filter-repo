# Copyright The IETF Trust 2019, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-01-16 05:53


from __future__ import absolute_import, print_function, unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0005_group_features_list_data_to_json'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupfeatures',
            name='docman_roles',
            field=jsonfield.fields.JSONField(default=['ad', 'chair', 'delegate', 'secr'], max_length=128),
        ),
        migrations.AddField(
            model_name='groupfeatures',
            name='groupman_roles',
            field=jsonfield.fields.JSONField(default=['ad', 'chair'], max_length=128),
        ),
        migrations.AddField(
            model_name='historicalgroupfeatures',
            name='docman_roles',
            field=jsonfield.fields.JSONField(default=['ad', 'chair', 'delegate', 'secr'], max_length=128),
        ),
        migrations.AddField(
            model_name='historicalgroupfeatures',
            name='groupman_roles',
            field=jsonfield.fields.JSONField(default=['ad', 'chair'], max_length=128),
        ),
        migrations.AlterField(
            model_name='groupfeatures',
            name='admin_roles',
            field=jsonfield.fields.JSONField(default=['chair'], max_length=64),
        ),
        migrations.AlterField(
            model_name='groupfeatures',
            name='custom_group_roles',
            field=models.BooleanField(default=False, verbose_name='Cust. Roles'),
        ),
        migrations.AlterField(
            model_name='groupfeatures',
            name='has_nonsession_materials',
            field=models.BooleanField(default=False, verbose_name='Other Matrl.'),
        ),
        migrations.AlterField(
            model_name='groupfeatures',
            name='has_session_materials',
            field=models.BooleanField(default=False, verbose_name='Sess Matrl.'),
        ),
        migrations.AlterField(
            model_name='groupfeatures',
            name='material_types',
            field=jsonfield.fields.JSONField(default=['slides'], max_length=64),
        ),
        migrations.AlterField(
            model_name='groupfeatures',
            name='matman_roles',
            field=jsonfield.fields.JSONField(default=['ad', 'chair', 'delegate', 'secr'], max_length=128),
        ),
        migrations.AlterField(
            model_name='groupfeatures',
            name='role_order',
            field=jsonfield.fields.JSONField(default=['chair', 'secr', 'member'], help_text='The order in which roles are shown, for instance on photo pages.  Enter valid JSON.', max_length=128),
        ),
        migrations.AlterField(
            model_name='historicalgroupfeatures',
            name='admin_roles',
            field=jsonfield.fields.JSONField(default=['chair'], max_length=64),
        ),
        migrations.AlterField(
            model_name='historicalgroupfeatures',
            name='custom_group_roles',
            field=models.BooleanField(default=False, verbose_name='Cust. Roles'),
        ),
        migrations.AlterField(
            model_name='historicalgroupfeatures',
            name='has_nonsession_materials',
            field=models.BooleanField(default=False, verbose_name='Other Matrl.'),
        ),
        migrations.AlterField(
            model_name='historicalgroupfeatures',
            name='has_session_materials',
            field=models.BooleanField(default=False, verbose_name='Sess Matrl.'),
        ),
        migrations.AlterField(
            model_name='historicalgroupfeatures',
            name='material_types',
            field=jsonfield.fields.JSONField(default=['slides'], max_length=64),
        ),
        migrations.AlterField(
            model_name='historicalgroupfeatures',
            name='matman_roles',
            field=jsonfield.fields.JSONField(default=['ad', 'chair', 'delegate', 'secr'], max_length=128),
        ),
        migrations.AlterField(
            model_name='historicalgroupfeatures',
            name='role_order',
            field=jsonfield.fields.JSONField(default=['chair', 'secr', 'member'], help_text='The order in which roles are shown, for instance on photo pages.  Enter valid JSON.', max_length=128),
        ),
    ]
