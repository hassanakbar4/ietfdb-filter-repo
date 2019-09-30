# Copyright The IETF Trust 2019, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-08 10:29


from __future__ import absolute_import, print_function, unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import ietf.utils.models


class Migration(migrations.Migration):

    dependencies = [
        ('doc', '0014_set_document_docalias_id'),
    ]

    operations = [
        # Fix name and id fields first
        migrations.AlterField(
            model_name='docalias',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='docalias',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='document',
            name='name',
            field=models.CharField(max_length=255, unique=True, validators=[django.core.validators.RegexValidator('^[-a-z0-9]+$', 'Provide a valid document name consisting of lowercase letters, numbers and hyphens.', 'invalid')]),
        ),
        migrations.AlterField(
            model_name='document',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),

        # Then remaining fields
        migrations.AddField(
            model_name='docalias',
            name='document2',
            field=ietf.utils.models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='doc.Document', to_field=b'id'),
        ),
        migrations.AddField(
            model_name='dochistory',
            name='doc2',
            field=ietf.utils.models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='history_set', to='doc.Document', to_field=b'id'),
        ),
        migrations.AddField(
            model_name='documentauthor',
            name='document2',
            field=ietf.utils.models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='doc.Document', to_field=b'id'),
        ),
        migrations.AddField(
            model_name='documenturl',
            name='doc2',
            field=ietf.utils.models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='doc.Document', to_field=b'id'),
        ),
        migrations.AddField(
            model_name='relateddochistory',
            name='target2',
            field=ietf.utils.models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reversely_related_document_history_set', to='doc.DocAlias', to_field=b'id'),
        ),
        migrations.AddField(
            model_name='relateddocument',
            name='source2',
            field=ietf.utils.models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='doc.Document', to_field=b'id'),
        ),
        migrations.AddField(
            model_name='relateddocument',
            name='target2',
            field=ietf.utils.models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='doc.DocAlias', to_field=b'id'),
        ),
        migrations.AddField(
            model_name='docevent',
            name='doc2',
            field=ietf.utils.models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='doc.Document', to_field='id'),
        ),
        migrations.AlterField(
            model_name='docalias',
            name='document',
            field=ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='old_docalias', to='doc.Document', to_field=b'name'),
        ),
        migrations.AlterField(
            model_name='dochistory',
            name='doc',
            field=ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='old_hist', to='doc.Document', to_field=b'name'),
        ),
        migrations.AlterField(
            model_name='documentauthor',
            name='document',
            field=ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='old_doc_auth', to='doc.Document', to_field=b'name'),
        ),
        migrations.AlterField(
            model_name='documenturl',
            name='doc',
            field=ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='old_doc_url', to='doc.Document', to_field=b'name'),
        ),
        migrations.AlterField(
            model_name='relateddochistory',
            name='target',
            field=ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='old_hist_target', to='doc.DocAlias', to_field=b'name'),
        ),
        migrations.AlterField(
            model_name='relateddocument',
            name='source',
            field=ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='old_rel_source', to='doc.Document', to_field=b'name'),
        ),
        migrations.AlterField(
            model_name='relateddocument',
            name='target',
            field=ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='old_rel_target', to='doc.DocAlias', to_field=b'name'),
        ),
        migrations.AlterField(
            model_name='docevent',
            name='doc',
            field=ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='old_docevent', to='doc.Document', to_field=b'name'),
        ),
    ]
