# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2018-09-07 05:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ColorCoding',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.CharField(blank=True, choices=[(b'January', b'January'), (b'February', b'February'), (b'March', b'March'), (b'April', b'April'), (b'May', b'May'), (b'June', b'June'), (b'July', b'July'), (b'August', b'August'), (b'September', b'September'), (b'October', b'October'), (b'November', b'November'), (b'December', b'Docember')], max_length=15)),
                ('hard_limit', models.FloatField(blank=True, default=0.0, null=True)),
                ('soft_limit', models.FloatField(blank=True, default=0.0, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects_color_codings', to='api.Project')),
                ('widget', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='widgets_color_codings', to='api.Widgets')),
            ],
        ),
        migrations.AlterIndexTogether(
            name='colorcoding',
            index_together=set([('project', 'widget', 'month')]),
        ),
    ]
