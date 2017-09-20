
from __future__ import unicode_literals
import datetime
from django.db import models
from django.contrib.auth.models import User
from api.models import *
from django.contrib.auth.models import Group
from voice_service.constrants import *

class Agent(models.Model):
    name                  = models.CharField(max_length=128, blank=True)
    project               = models.ForeignKey(Project, related_name='project')


class Skill(models.Model):
    name                  = models.CharField(max_length=16, db_index=True)


class InboundDailyCalls(models.Model):
    agent                   = models.ForeignKey(Agent, related_name='inbound_daily_agent') 
    date                    = models.DateField(default=datetime.date.today)
    daily_duration          = models.IntegerField(default=0)
    daily_handling_time     = models.IntegerField(default=0)

    class Meta:
        unique_together = (('agent', 'date'), )
        index_together  = (('agent', 'date'), )


class InboundHourlyCalls(models.Model):
    call_id                 = models.CharField(max_length=32, primary_key=True)
    inbound_daily_calls     = models.ForeignKey(InboundDailyCalls, blank=True, null=True, related_name='daily_call')
    campaign                = models.CharField(max_length=128, blank=True)
    skill                   = models.ForeignKey(Skill, related_name='inbound_skill')
    location                = models.ForeignKey(Center, related_name='inbound_center')
    caller_no               = models.CharField(max_length=128, blank=True)
    start_time              = models.DateTimeField()
    time_to_answer          = models.IntegerField(max_length=128, blank=True)
    end_time                = models.DateTimeField()
    talk_time               = models.IntegerField(default=0)
    hold_time               = models.IntegerField(default=0)
    duration                = models.IntegerField(default=0)
    call_flow               = models.CharField(max_length=128, blank=True)
    agent                   = models.ForeignKey(Agent, related_name='inbound_agent')
    wrapup_duration         = models.IntegerField(default=0)
    disposition             = models.CharField(max_length=128, blank=True)
    handling_time           = models.IntegerField(default=0)
    status                  = models.CharField(max_length=16, choices=STATUS_OPTIONS)
    dial_status             = models.CharField(max_length=128, blank=True)
    hangup_by               = models.CharField(max_length=32, choices=HANGUP_OPTIONS)
    transfer                = models.CharField(max_length=128, blank=True)
    UUI                     = models.CharField(max_length=128, blank=True)
    comments                = models.CharField(max_length=128, blank=True)
    audio_url               = models.CharField(max_length=128, blank=True)


class AgentTransferCall(models.Model):
    call                    = models.ForeignKey(InboundHourlyCalls, related_name='agent_tranfer_call')
    from_agent              = models.ForeignKey(Agent, related_name='from_agent')
    to_agent                = models.ForeignKey(Agent, related_name='to_agent')


class SkillTransferCall(models.Model):
    call                    = models.ForeignKey(InboundHourlyCalls, related_name='skill_transfer_call')
    from_skill              = models.ForeignKey(Skill, related_name='from_skill')
    to_skill                = models.ForeignKey(Skill, related_name='to_skill')


class LocationTransferCall(models.Model):
    call                    = models.ForeignKey(InboundHourlyCalls, related_name='location_transfer_call')
    from_location              = models.ForeignKey(Center, related_name='from_location')
    to_location                = models.ForeignKey(Center, related_name='to_location')


class InboundHourlyCallsAuthoring(models.Model):
    call_id                 = models.CharField(max_length=128, blank=True)
    campaign                = models.CharField(max_length=128, blank=True)
    skill                   = models.CharField(max_length=128, blank=True)
    location                = models.CharField(max_length=128, blank=True)
    caller_no               = models.CharField(max_length=128, blank=True)
    start_time              = models.CharField(max_length=128, blank=True)
    time_to_answer          = models.CharField(max_length=128, blank=True)
    end_time                = models.CharField(max_length=128, blank=True)
    talk_time               = models.CharField(max_length=128, blank=True)
    hold_time               = models.CharField(max_length=128, blank=True)
    duration                = models.CharField(max_length=128, blank=True)
    call_flow               = models.CharField(max_length=128, blank=True)
    agent                   = models.CharField(max_length=128, blank=True)
    wrapup_duration         = models.CharField(max_length=128, blank=True)
    disposition             = models.CharField(max_length=128, blank=True)
    handling_time           = models.CharField(max_length=128, blank=True)
    status                  = models.CharField(max_length=128, blank=True)
    dial_status             = models.CharField(max_length=128, blank=True)
    hangup_by               = models.CharField(max_length=128, blank=True)
    transfer                = models.CharField(max_length=128, blank=True)
    UUI                     = models.CharField(max_length=128, blank=True)
    comments                = models.CharField(max_length=128, blank=True)
    audio_url               = models.CharField(max_length=128, blank=True)


class OutboundDailyCalls(models.Model):
    agent                   = models.ForeignKey(Agent, related_name='outbound_daily_agent')
    date                    = models.DateField(default=datetime.date.today)
    daily_duration          = models.IntegerField(default=0)
    daily_handling_time     = models.IntegerField(default=0)

    class Meta:
        unique_together = (('agent', 'date'), )
        index_together  = (('agent', 'date'), )


class OutboundHourlyCalls(models.Model):
    call_id                 = models.CharField(max_length=32, primary_key=True)
    outbound_daily_calls    = models.ForeignKey(OutboundDailyCalls, blank=True, null=True, related_name='daily_call')
    campaign                = models.CharField(max_length=128, blank=True)
    call_type               = models.CharField(max_length=32, choices=CALL_TYPE_OPTIONS)
    agent                   = models.ForeignKey(Agent, related_name='outbound_agent')
    called_no               = models.CharField(max_length=16, blank=True)
    start_time              = models.DateTimeField()
    end_time                = models.DateTimeField()
    talk_time               = models.IntegerField(default=0)
    hold_time               = models.IntegerField(default=0)
    duration                = models.IntegerField(default=0)
    wrapup_duration         = models.IntegerField(default=0)
    handling_time           = models.IntegerField(default=0)
    call_flow               = models.CharField(max_length=128, blank=True)
    disposition             = models.CharField(max_length=128, blank=True)
    dial_status             = models.CharField(max_length=128, blank=True)
    customer_dial_status    = models.CharField(max_length=128, blank=True)
    agent_dial_status       = models.CharField(max_length=128, blank=True)
    hangup_by               = models.CharField(max_length=32, choices=HANGUP_OPTIONS)
    transfer                = models.CharField(max_length=128, blank=True)
    UUI                     = models.CharField(max_length=128, blank=True)
    comments                = models.CharField(max_length=128, blank=True)
    audio_url               = models.CharField(max_length=128, blank=True)


class OutboundHourlyCallsAuthoring(models.Model):
    call_id                 = models.CharField(max_length=128, blank=True)
    campaign                = models.CharField(max_length=128, blank=True)
    call_type               = models.CharField(max_length=128, blank=True)
    called_no               = models.CharField(max_length=128, blank=True)
    start_time              = models.CharField(max_length=128, blank=True)
    end_time                = models.CharField(max_length=128, blank=True)
    talk_time               = models.CharField(max_length=128, blank=True)
    hold_time               = models.CharField(max_length=128, blank=True)
    duration                = models.CharField(max_length=128, blank=True)
    wrapup_duration         = models.CharField(max_length=128, blank=True)
    handling_time           = models.CharField(max_length=128, blank=True)
    call_flow               = models.CharField(max_length=128, blank=True)
    disposition             = models.CharField(max_length=128, blank=True)
    dial_status             = models.CharField(max_length=128, blank=True)
    customer_dial_status    = models.CharField(max_length=128, blank=True)
    agent_dial_status       = models.CharField(max_length=128, blank=True)
    hangup_by               = models.CharField(max_length=128, blank=True)
    transfer                = models.CharField(max_length=128, blank=True)
    UUI                     = models.CharField(max_length=128, blank=True)
    comments                = models.CharField(max_length=128, blank=True)
    audio_url               = models.CharField(max_length=128, blank=True)





