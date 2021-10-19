# Generated by Django 2.2.24 on 2021-10-19 11:36

from django.db import migrations
import ietf.utils.db


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0048_has_session_materials'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupfeatures',
            name='admin_roles',
            field=ietf.utils.db.IETFJSONField(default=['chair'], max_length=64),
        ),
        migrations.AlterField(
            model_name='groupfeatures',
            name='default_used_roles',
            field=ietf.utils.db.IETFJSONField(default=[], max_length=256),
        ),
        migrations.AlterField(
            model_name='groupfeatures',
            name='docman_roles',
            field=ietf.utils.db.IETFJSONField(default=['ad', 'chair', 'delegate', 'secr'], max_length=128),
        ),
        migrations.AlterField(
            model_name='groupfeatures',
            name='groupman_authroles',
            field=ietf.utils.db.IETFJSONField(default=['Secretariat'], max_length=128),
        ),
        migrations.AlterField(
            model_name='groupfeatures',
            name='groupman_roles',
            field=ietf.utils.db.IETFJSONField(default=['ad', 'chair'], max_length=128),
        ),
        migrations.AlterField(
            model_name='groupfeatures',
            name='material_types',
            field=ietf.utils.db.IETFJSONField(default=['slides'], max_length=64),
        ),
        migrations.AlterField(
            model_name='groupfeatures',
            name='matman_roles',
            field=ietf.utils.db.IETFJSONField(default=['ad', 'chair', 'delegate', 'secr'], max_length=128),
        ),
        migrations.AlterField(
            model_name='groupfeatures',
            name='role_order',
            field=ietf.utils.db.IETFJSONField(default=['chair', 'secr', 'member'], help_text='The order in which roles are shown, for instance on photo pages.  Enter valid JSON.', max_length=128),
        ),
    ]
