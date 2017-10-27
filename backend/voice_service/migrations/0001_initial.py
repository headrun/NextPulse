# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-09-20 09:20
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('api', '0003_auto_20170911_1604'),
    ]

    operations = [
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=128)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project', to='api.Project')),
            ],
        ),
        migrations.CreateModel(
            name='AgentTransferCall',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='InboundDailyCalls',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date.today)),
                ('daily_duration', models.IntegerField(default=0)),
                ('daily_handling_time', models.IntegerField(default=0)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inbound_daily_agent', to='voice_service.Agent')),
            ],
        ),
        migrations.CreateModel(
            name='InboundHourlyCalls',
            fields=[
                ('call_id', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('campaign', models.CharField(blank=True, max_length=128)),
                ('caller_no', models.CharField(blank=True, max_length=128)),
                ('start_time', models.DateTimeField()),
                ('time_to_answer', models.IntegerField(blank=True, max_length=128)),
                ('end_time', models.DateTimeField()),
                ('talk_time', models.IntegerField(default=0)),
                ('hold_time', models.IntegerField(default=0)),
                ('duration', models.IntegerField(default=0)),
                ('call_flow', models.CharField(blank=True, max_length=128)),
                ('wrapup_duration', models.IntegerField(default=0)),
                ('disposition', models.CharField(blank=True, max_length=128)),
                ('handling_time', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[(b'Answered', b'Answered'), (b'Unanswered', b'Unanswered')], max_length=16)),
                ('dial_status', models.CharField(blank=True, max_length=128)),
                ('hangup_by', models.CharField(choices=[(b'Caller Disconnect', b'Caller Disconnect'), (b'Agent Disconnect', b'Agent Disconnect')], max_length=32)),
                ('transfer', models.CharField(blank=True, max_length=128)),
                ('UUI', models.CharField(blank=True, max_length=128)),
                ('comments', models.CharField(blank=True, max_length=128)),
                ('audio_url', models.CharField(blank=True, max_length=128)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inbound_agent', to='voice_service.Agent')),
                ('inbound_daily_calls', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='daily_call', to='voice_service.InboundDailyCalls')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inbound_center', to='api.Center')),
            ],
        ),
        migrations.CreateModel(
            name='InboundHourlyCallsAuthoring',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('call_id', models.CharField(blank=True, max_length=128)),
                ('campaign', models.CharField(blank=True, max_length=128)),
                ('skill', models.CharField(blank=True, max_length=128)),
                ('location', models.CharField(blank=True, max_length=128)),
                ('caller_no', models.CharField(blank=True, max_length=128)),
                ('start_time', models.CharField(blank=True, max_length=128)),
                ('time_to_answer', models.CharField(blank=True, max_length=128)),
                ('end_time', models.CharField(blank=True, max_length=128)),
                ('talk_time', models.CharField(blank=True, max_length=128)),
                ('hold_time', models.CharField(blank=True, max_length=128)),
                ('duration', models.CharField(blank=True, max_length=128)),
                ('call_flow', models.CharField(blank=True, max_length=128)),
                ('agent', models.CharField(blank=True, max_length=128)),
                ('wrapup_duration', models.CharField(blank=True, max_length=128)),
                ('disposition', models.CharField(blank=True, max_length=128)),
                ('handling_time', models.CharField(blank=True, max_length=128)),
                ('status', models.CharField(blank=True, max_length=128)),
                ('dial_status', models.CharField(blank=True, max_length=128)),
                ('hangup_by', models.CharField(blank=True, max_length=128)),
                ('transfer', models.CharField(blank=True, max_length=128)),
                ('UUI', models.CharField(blank=True, max_length=128)),
                ('comments', models.CharField(blank=True, max_length=128)),
                ('audio_url', models.CharField(blank=True, max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='LocationTransferCall',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('call', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='location_transfer_call', to='voice_service.InboundHourlyCalls')),
                ('from_location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_location', to='api.Center')),
                ('to_location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_location', to='api.Center')),
            ],
        ),
        migrations.CreateModel(
            name='OutboundDailyCalls',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date.today)),
                ('daily_duration', models.IntegerField(default=0)),
                ('daily_handling_time', models.IntegerField(default=0)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outbound_daily_agent', to='voice_service.Agent')),
            ],
        ),
        migrations.CreateModel(
            name='OutboundHourlyCalls',
            fields=[
                ('call_id', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('campaign', models.CharField(blank=True, max_length=128)),
                ('call_type', models.CharField(choices=[(b'Manual', b'Manual'), (b'Automatic', b'Automatic')], max_length=32)),
                ('called_no', models.CharField(blank=True, max_length=16)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('talk_time', models.IntegerField(default=0)),
                ('hold_time', models.IntegerField(default=0)),
                ('duration', models.IntegerField(default=0)),
                ('wrapup_duration', models.IntegerField(default=0)),
                ('handling_time', models.IntegerField(default=0)),
                ('call_flow', models.CharField(blank=True, max_length=128)),
                ('disposition', models.CharField(blank=True, max_length=128)),
                ('dial_status', models.CharField(blank=True, max_length=128)),
                ('customer_dial_status', models.CharField(blank=True, max_length=128)),
                ('agent_dial_status', models.CharField(blank=True, max_length=128)),
                ('hangup_by', models.CharField(choices=[(b'Caller Disconnect', b'Caller Disconnect'), (b'Agent Disconnect', b'Agent Disconnect')], max_length=32)),
                ('transfer', models.CharField(blank=True, max_length=128)),
                ('UUI', models.CharField(blank=True, max_length=128)),
                ('comments', models.CharField(blank=True, max_length=128)),
                ('audio_url', models.CharField(blank=True, max_length=128)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outbound_agent', to='voice_service.Agent')),
                ('outbound_daily_calls', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='daily_call', to='voice_service.OutboundDailyCalls')),
            ],
        ),
        migrations.CreateModel(
            name='OutboundHourlyCallsAuthoring',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('call_id', models.CharField(blank=True, max_length=128)),
                ('campaign', models.CharField(blank=True, max_length=128)),
                ('call_type', models.CharField(blank=True, max_length=128)),
                ('called_no', models.CharField(blank=True, max_length=128)),
                ('start_time', models.CharField(blank=True, max_length=128)),
                ('end_time', models.CharField(blank=True, max_length=128)),
                ('talk_time', models.CharField(blank=True, max_length=128)),
                ('hold_time', models.CharField(blank=True, max_length=128)),
                ('duration', models.CharField(blank=True, max_length=128)),
                ('wrapup_duration', models.CharField(blank=True, max_length=128)),
                ('handling_time', models.CharField(blank=True, max_length=128)),
                ('call_flow', models.CharField(blank=True, max_length=128)),
                ('disposition', models.CharField(blank=True, max_length=128)),
                ('dial_status', models.CharField(blank=True, max_length=128)),
                ('customer_dial_status', models.CharField(blank=True, max_length=128)),
                ('agent_dial_status', models.CharField(blank=True, max_length=128)),
                ('hangup_by', models.CharField(blank=True, max_length=128)),
                ('transfer', models.CharField(blank=True, max_length=128)),
                ('UUI', models.CharField(blank=True, max_length=128)),
                ('comments', models.CharField(blank=True, max_length=128)),
                ('audio_url', models.CharField(blank=True, max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='SkillTransferCall',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('call', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='skill_transfer_call', to='voice_service.InboundHourlyCalls')),
                ('from_skill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_skill', to='voice_service.Skill')),
                ('to_skill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_skill', to='voice_service.Skill')),
            ],
        ),
        migrations.AddField(
            model_name='inboundhourlycalls',
            name='skill',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inbound_skill', to='voice_service.Skill'),
        ),
        migrations.AddField(
            model_name='agenttransfercall',
            name='call',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agent_tranfer_call', to='voice_service.InboundHourlyCalls'),
        ),
        migrations.AddField(
            model_name='agenttransfercall',
            name='from_agent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_agent', to='voice_service.Agent'),
        ),
        migrations.AddField(
            model_name='agenttransfercall',
            name='to_agent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_agent', to='voice_service.Agent'),
        ),
        migrations.AlterUniqueTogether(
            name='outbounddailycalls',
            unique_together=set([('agent', 'date')]),
        ),
        migrations.AlterIndexTogether(
            name='outbounddailycalls',
            index_together=set([('agent', 'date')]),
        ),
        migrations.AlterUniqueTogether(
            name='inbounddailycalls',
            unique_together=set([('agent', 'date')]),
        ),
        migrations.AlterIndexTogether(
            name='inbounddailycalls',
            index_together=set([('agent', 'date')]),
        ),
    ]
