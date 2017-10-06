
from __future__ import unicode_literals
import datetime
from django.db import models
from django.contrib.auth.models import User
from api.models import *
#from api import models as apimodels
from django.contrib.auth.models import Group
from voice_service.constrants import *

class Agent(models.Model):
    name       = models.CharField(max_length=255, blank=True)
    project    = models.ForeignKey(Project, related_name='agents')
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)

    class Meta:
        index_together = (('name', 'project'), )


class Skill(models.Model):
    name       = models.CharField(max_length=16, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)


class Location(models.Model):
    name       = models.CharField(max_length=16, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)


class InboundDailyCall(models.Model):
    agent               = models.ForeignKey(Agent, related_name='inbound_daily_calls') 
    date                = models.DateField(default=datetime.date.today)
    daily_duration      = models.IntegerField(default=0)
    daily_handling_time = models.IntegerField(default=0)
    created_at          = models.DateTimeField(auto_now_add=True, null=True)
    updated_at          = models.DateTimeField(auto_now=True,null=True)

    class Meta:
        #unique_together = (('agent', 'date'), )
        index_together  = (('agent', 'date'), )


class InboundHourlyCall(models.Model):
    call_id             = models.CharField(max_length=32, primary_key=True)
    inbound_daily_calls = models.ForeignKey(InboundDailyCall, blank=True, null=True, related_name='daily_calls')
    campaign            = models.CharField(max_length=255, blank=True)
    #skill              = models.ForeignKey(Skill, related_name='inbound_skills')
    skill               = models.CharField(max_length=255, blank=False)
    #location           = models.ForeignKey(Center, related_name='inbound_centers')
    location            = models.CharField(max_length=255, blank=False)
    caller_no           = models.CharField(max_length=50, blank=False)
    call_date           = models.DateField(default=datetime.date.today)
    start_time          = models.IntegerField(default=0)
    time_to_answer      = models.IntegerField(blank=True)
    end_time            = models.IntegerField(default=0)
    talk_time           = models.IntegerField(default=0)
    hold_time           = models.IntegerField(default=0)
    duration            = models.IntegerField(default=0)
    call_flow           = models.CharField(max_length=255, blank=True)
    agent               = models.ForeignKey(Agent, related_name='inbound_agents')
    wrapup_duration     = models.IntegerField(default=0)
    disposition         = models.CharField(max_length=128, blank=True)
    handling_time       = models.IntegerField(default=0)
    status              = models.CharField(max_length=50, choices=STATUS_OPTIONS)
    dial_status         = models.CharField(max_length=128, default = 'answered')
    hangup_by           = models.CharField(max_length=32, choices=HANGUP_OPTIONS)
    transfer            = models.CharField(max_length=255, null=True)
    uui                 = models.CharField(max_length=255, blank=True)
    comments            = models.CharField(max_length=255, blank=True)
    audio_url           = models.CharField(max_length=255, blank=True)
    project             = models.ForeignKey(Project, null=True)
    center              = models.ForeignKey(Center, null=True)
    created_at          = models.DateTimeField(auto_now_add=True,null=True)
    updated_at          = models.DateTimeField(auto_now=True,null=True)


class InboundHourlyCallAuthoring(models.Model):
    call_id         = models.CharField(max_length=255, blank=False)
    campaign        = models.CharField(max_length=255, blank=False)
    skill           = models.CharField(max_length=255, blank=False)
    location        = models.CharField(max_length=255, blank=False)
    caller_no       = models.CharField(max_length=255, blank=False)
    call_date       = models.CharField(max_length=255, blank=False, default='Call Date')
    start_time      = models.CharField(max_length=255, blank=False)
    time_to_answer  = models.CharField(max_length=255, blank=False)
    end_time        = models.CharField(max_length=255, blank=False)
    talk_time       = models.CharField(max_length=255, blank=False)
    hold_time       = models.CharField(max_length=255, blank=False)
    duration        = models.CharField(max_length=255, blank=False)
    call_flow       = models.CharField(max_length=255, blank=False)
    agent           = models.CharField(max_length=255, blank=False)
    wrapup_duration = models.CharField(max_length=255, blank=False)
    disposition     = models.CharField(max_length=255, blank=False)
    handling_time   = models.CharField(max_length=255, blank=False)
    status          = models.CharField(max_length=255, blank=False)
    dial_status     = models.CharField(max_length=255, blank=False)
    hangup_by       = models.CharField(max_length=255, blank=False)
    transfer        = models.CharField(max_length=255, blank=False)
    uui             = models.CharField(max_length=255, blank=False, default='UUI')
    comments        = models.CharField(max_length=255, blank=False)
    audio_url       = models.CharField(max_length=255, blank=False)
    sheet_name      = models.CharField(max_length=255, blank=False)
    project         = models.ForeignKey(Project, null=True)
    center          = models.ForeignKey(Center, null=True)
    created_at      = models.DateTimeField(auto_now_add=True,null=True)
    updated_at      = models.DateTimeField(auto_now=True,null=True)


class AgentTransferCall(models.Model):
    call       = models.ForeignKey(InboundHourlyCall, related_name='agent_tranfer_calls')
    from_agent = models.ForeignKey(Agent, related_name='from_agents')
    to_agent   = models.ForeignKey(Agent, related_name='to_agents')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        index_together = (('call', 'from_agent', 'to_agent'), )


class SkillTransferCall(models.Model):
    call       = models.ForeignKey(InboundHourlyCall, related_name='skill_transfer_calls')
    from_skill = models.ForeignKey(Skill, related_name='from_skills')
    to_skill   = models.ForeignKey(Skill, related_name='to_skills')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        index_together = (('call', 'from_skill', 'to_skill'), )


class LocationTransferCall(models.Model):
    call               = models.ForeignKey(InboundHourlyCall, related_name='location_transfer_calls')
    from_location      = models.ForeignKey(Location, related_name='from_locations')
    to_location        = models.ForeignKey(Location, related_name='to_locations')

    class Meta:
        index_together = (('call', 'from_location', 'to_location'), )


class OutboundDailyCall(models.Model):
    agent               = models.ForeignKey(Agent, related_name='outbound_daily_calls')
    date                = models.DateField(default=datetime.date.today)
    daily_duration      = models.IntegerField(default=0)
    daily_handling_time = models.IntegerField(default=0)
    created_at          = models.DateTimeField(auto_now_add=True,null=True)
    updated_at          = models.DateTimeField(auto_now=True,null=True)

    class Meta:
        #unique_together = (('agent', 'date'), )
        index_together  = (('agent', 'date'), )


class OutboundHourlyCall(models.Model):
    call_id              = models.CharField(max_length=50, primary_key=True)
    outbound_daily_calls = models.ForeignKey(OutboundDailyCall, blank=True, null=True, related_name='daily_calls')
    campaign             = models.CharField(max_length=255, blank=True)
    call_type            = models.CharField(max_length=32,  choices=CALL_TYPE_OPTIONS)
    agent                = models.ForeignKey(Agent, related_name='outbound_agents')
    called_no            = models.CharField(max_length=50, blank=False)
    call_date            = models.DateField(default=datetime.date.today)
    start_time           = models.DateTimeField()
    end_time             = models.DateTimeField()
    talk_time            = models.IntegerField(default=0)
    hold_time            = models.IntegerField(default=0)
    duration             = models.IntegerField(default=0)
    wrapup_duration      = models.IntegerField(default=0)
    handling_time        = models.IntegerField(default=0)
    call_flow            = models.CharField(max_length=255, blank=False)
    #agent               = models.CharField(max_length=255, blank=True)
    disposition          = models.CharField(max_length=255, blank=True)
    dial_status          = models.CharField(max_length=255, blank=True)
    customer_dial_status = models.CharField(max_length=255, blank=True)
    agent_dial_status    = models.CharField(max_length=255, blank=True)
    hangup_by            = models.CharField(max_length=32,  choices=HANGUP_OPTIONS)
    transfer             = models.CharField(max_length=255, blank=True)
    uui                  = models.CharField(max_length=255, blank=True)
    comments             = models.CharField(max_length=255, blank=True)
    audio_url            = models.CharField(max_length=255, blank=True)
    project              = models.ForeignKey(Project, null=True)
    center               = models.ForeignKey(Center, null=True)
    created_at           = models.DateTimeField(auto_now_add=True,null=True)
    updated_at           = models.DateTimeField(auto_now=True,null=True)


class OutboundHourlyCallAuthoring(models.Model):
    call_id              = models.CharField(max_length=255, blank=False)
    campaign             = models.CharField(max_length=255, blank=False)
    call_type            = models.CharField(max_length=255, blank=False)
    called_no            = models.CharField(max_length=255, blank=False)
    call_date            = models.CharField(max_length=255, blank=False, default='Call Date')
    start_time           = models.CharField(max_length=255, blank=False)
    end_time             = models.CharField(max_length=255, blank=False)
    talk_time            = models.CharField(max_length=255, blank=False)
    hold_time            = models.CharField(max_length=255, blank=False)
    duration             = models.CharField(max_length=255, blank=False)
    wrapup_duration      = models.CharField(max_length=255, blank=False)
    handling_time        = models.CharField(max_length=255, blank=False)
    call_flow            = models.CharField(max_length=255, blank=False)
    disposition          = models.CharField(max_length=255, blank=False)
    dial_status          = models.CharField(max_length=255, blank=False)
    customer_dial_status = models.CharField(max_length=255, blank=False)
    agent_dial_status    = models.CharField(max_length=255, blank=False)
    hangup_by            = models.CharField(max_length=255, blank=False)
    transfer             = models.CharField(max_length=255, blank=False)
    uui                  = models.CharField(max_length=255, blank=False, default='UUI')
    comments             = models.CharField(max_length=255, blank=False)
    audio_url            = models.CharField(max_length=255, blank=False)
    sheet_name           = models.CharField(max_length=255, blank=False)
    project              = models.ForeignKey(Project, null=True)
    center               = models.ForeignKey(Center, null=True)
    created_at           = models.DateTimeField(auto_now_add=True,null=True)
    updated_at           = models.DateTimeField(auto_now=True,null=True)


class InboundDaily(models.Model):
    call_date       = models.DateField(null=True)
    agent           = models.ForeignKey(Agent, related_name = 'inbound_daily_agents')
    hours_worked    = models.IntegerField(default=0)
    total_calls     = models.IntegerField()
    connects_per_hr = models.IntegerField()
    calls_answered  = models.IntegerField()
    wrapup_time     = models.IntegerField(default=0)
    hold_time       = models.IntegerField(default=0)
    talk_time       = models.IntegerField(default=0)
    time_to_answer  = models.IntegerField(default=0)
    skill           = models.CharField(max_length=255, blank=True)
    location        = models.CharField(max_length=255, blank=True)
    disposition     = models.CharField(max_length=255, blank=True)
    project         = models.ForeignKey(Project, null=True)
    center          = models.ForeignKey(Center, null=True)
    created_at      = models.DateTimeField(auto_now_add=True,null=True)
    updated_at      = models.DateTimeField(auto_now=True,null=True)
 

class OutboundDaily(models.Model):
    call_date       = models.DateField(null=True)
    agent           = models.ForeignKey(Agent, related_name = 'outbound_daily_agents')
    hours_worked    = models.IntegerField(default=0)
    total_calls     = models.IntegerField()
    connects_per_hr = models.IntegerField()
    calls_answered  = models.IntegerField()
    wrapup_time     = models.IntegerField(default=0)
    hold_time       = models.IntegerField(default=0)
    talk_time       = models.IntegerField(default=0)
    time_to_answer  = models.IntegerField(default=0)
    disposition     = models.CharField(max_length=255, blank=True)
    project         = models.ForeignKey(Project, null=True)
    center          = models.ForeignKey(Center, null=True)
    created_at      = models.DateTimeField(auto_now_add=True,null=True)
    updated_at      = models.DateTimeField(auto_now=True,null=True)


class InboundDailyAuthoring(models.Model):
    call_date       = models.CharField(max_length=255, blank=True)
    agent           = models.CharField(max_length=255, blank=True)
    hours_worked    = models.CharField(max_length=255, blank=True)    
    calls           = models.CharField(max_length=255, blank=True)
    connects_per_hr = models.CharField(max_length=255, blank=True)
    calls_answered  = models.CharField(max_length=255, blank=True)
    wrapup_time     = models.CharField(max_length=255, blank=True)
    hold_time       = models.CharField(max_length=255, blank=True)
    talk_time       = models.CharField(max_length=255, blank=True)
    time_to_answer  = models.CharField(max_length=255, blank=True)
    skill           = models.CharField(max_length=255, blank=True)
    location        = models.CharField(max_length=255, blank=True)
    disposition     = models.CharField(max_length=255, blank=True)
    sheet_name      = models.CharField(max_length=255, blank=True)
    project         = models.ForeignKey(Project, null=True)
    center          = models.ForeignKey(Center, null=True)
    created_at      = models.DateTimeField(auto_now_add=True,null=True)
    updated_at      = models.DateTimeField(auto_now=True,null=True)


class OutboundDailyAuthoring(models.Model):
    call_date       = models.CharField(max_length=255, blank=True)
    agent           = models.CharField(max_length=255, blank=True)
    hours_worked    = models.CharField(max_length=255, blank=True)     
    calls           = models.CharField(max_length=255, blank=True)
    connects_per_hr = models.CharField(max_length=255, blank=True)
    calls_answered  = models.CharField(max_length=255, blank=True)
    wrapup_time     = models.CharField(max_length=255, blank=True)
    hold_time       = models.CharField(max_length=255, blank=True)
    talk_time       = models.CharField(max_length=255, blank=True)
    time_to_answer  = models.CharField(max_length=255, blank=True)
    disposition     = models.CharField(max_length=255, blank=True)
    sheet_name      = models.CharField(max_length=255, blank=True)
    project         = models.ForeignKey(Project, null=True)
    center          = models.ForeignKey(Center, null=True)
    created_at      = models.DateTimeField(auto_now_add=True,null=True)
    updated_at      = models.DateTimeField(auto_now=True,null=True)

