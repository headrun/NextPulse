# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2018-01-16 10:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voice_service', '0002_auto_20180116_0930'),
    ]

    operations = [
        migrations.AddField(
            model_name='inbounddaily',
            name='status',
            field=models.CharField(choices=[(b'Answered', b'Answered'), (b'Unanswered', b'Unanswered')], db_index=True, default='Answered', max_length=50),
        ),
    ]
