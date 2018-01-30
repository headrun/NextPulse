# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2018-01-29 12:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('voice_service', '0006_remove_dispositiontransfercall_call'),
    ]

    operations = [
        migrations.AddField(
            model_name='dispositiontransfercall',
            name='call',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='disposition_transfer_calls', to='voice_service.InboundHourlyCall'),
            preserve_default=False,
        ),
    ]
