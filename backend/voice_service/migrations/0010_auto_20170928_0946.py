# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-09-28 09:46
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('voice_service', '0009_auto_20170928_0943'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inboundhourlycallauthoring',
            name='date',
        ),
        migrations.RemoveField(
            model_name='outboundhourlycall',
            name='call_date',
        ),
        migrations.RemoveField(
            model_name='outboundhourlycallauthoring',
            name='call_date',
        ),
    ]