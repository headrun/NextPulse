# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-10-23 05:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_auto_20171023_0503'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='widgets_group',
            name='display_value',
        ),
    ]
