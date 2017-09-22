from django.contrib import admin

# Register your models here.
from .models import *

class InboundHourlyCallAuthoringAdmin(admin.ModelAdmin):
    list_display = ['call_id', 'campaign', 'skill', 'location', 'caller_no', 'start_time', 'time_to_answer', 'end_time', 'talk_time',\
                    'hold_time', 'duration', 'call_flow', 'agent', 'wrapup_duration', 'disposition', 'handling_time', 'status',\
                    'dial_status', 'hangup_by', 'transfer', 'uui', 'comments', 'audio_url']
    list_filter  = ['skill', 'location', 'status']
admin.site.register(InboundHourlyCallAuthoring, InboundHourlyCallAuthoringAdmin)

class InboundHourlyCallAdmin(admin.ModelAdmin):
    list_display = ['call_id', 'skill', 'location', 'caller_no', 'agent', 'status']
    list_filter  = ['skill', 'location']
admin.site.register(InboundHourlyCall, InboundHourlyCallAdmin)

class OutboundHourlyCallAuthoringAdmin(admin.ModelAdmin):
    list_display = ['call_id', 'campaign', 'call_type', 'called_no', 'start_time', 'end_time', 'talk_time', 'hold_time', 'duration',\
                    'wrapup_duration', 'handling_time', 'call_flow', 'disposition', 'dial_status', 'customer_dial_status', \
                    'agent_dial_status', 'hangup_by', 'transfer', 'uui', 'comments', 'audio_url']
admin.site.register(OutboundHourlyCallAuthoring, OutboundHourlyCallAuthoringAdmin)

class OutboundHourlyCallAdmin(admin.ModelAdmin):
    list_display = ['call_id', 'call_type', 'called_no', 'call_flow', 'disposition', 'dial_status']
admin.site.register(OutboundHourlyCall, OutboundHourlyCallAdmin)

class InboundDailyCallAdmin(admin.ModelAdmin):
    list_display = ['agent', 'date', 'daily_duration', 'daily_handling_time']
admin.site.register(InboundDailyCall, InboundDailyCallAdmin)

class OutboundDailyCallAdmin(admin.ModelAdmin):
    list_display = ['agent', 'date', 'daily_duration', 'daily_handling_time']
admin.site.register(OutboundDailyCall, OutboundDailyCallAdmin)

class AgentAdmin(admin.ModelAdmin):
    list_display = ['name', 'project']
    list_filter  = ['project']
admin.site.register(Agent, AgentAdmin)

class SkillAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_filter  = ['name']
admin.site.register(Skill, SkillAdmin)

class AgentTransferCallAdmin(admin.ModelAdmin):
    list_display = ['call', 'from_agent', 'to_agent']
admin.site.register(AgentTransferCall, AgentTransferCallAdmin)

class SkillTransferCallAdmin(admin.ModelAdmin):
    list_display = ['call', 'from_skill', 'to_skill']
    list_filter  = ['from_skill', 'to_skill'] 
admin.site.register(SkillTransferCall, SkillTransferCallAdmin)

class LocationTransferCallAdmin(admin.ModelAdmin):
    list_display = ['call', 'from_location', 'to_location']
    list_filter  = ['from_location', 'to_location']
admin.site.register(LocationTransferCall, LocationTransferCallAdmin)
