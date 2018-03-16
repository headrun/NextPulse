from django.contrib import admin

# Register your models here.
from .models import *

class InboundHourlyCallAuthoringAdmin(admin.ModelAdmin):
    list_display = ['call_id', 'campaign', 'skill', 'location', 'caller_no', 'start_time', 'time_to_answer', 'end_time',\
                    'talk_time','hold_time', 'duration', 'call_flow', 'agent', 'wrapup_duration', 'disposition', 'handling_time', \
                    'status','dial_status', 'hangup_by', 'transfer', 'uui', 'comments', 'audio_url']
    list_filter  = ['skill', 'location', 'status']
admin.site.register(InboundHourlyCallAuthoring, InboundHourlyCallAuthoringAdmin)

class InboundHourlyCallAdmin(admin.ModelAdmin):
    list_display = ['skill', 'location', 'caller_no', 'agent', 'status']
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

class InboundDailyAuthoringAdmin(admin.ModelAdmin):
    list_display = ['agent', 'hours_worked', 'calls', 'connects_per_hr', 'project', 'center']
admin.site.register(InboundDailyAuthoring, InboundDailyAuthoringAdmin)

class OutboundDailyAuthoringAdmin(admin.ModelAdmin):
    list_display = ['agent', 'hours_worked', 'calls', 'connects_per_hr', 'project', 'center']
admin.site.register(OutboundDailyAuthoring, OutboundDailyAuthoringAdmin)


class InboundDailyAdmin(admin.ModelAdmin):
    list_display = ['total_calls', 'calls_answered', 'date', 'project', 'center']
    list_filter  = ['project', 'center']
admin.site.register(InboundDaily, InboundDailyAdmin)

class OutboundDailyAdmin(admin.ModelAdmin):
    list_display = ['agent', 'hours_worked', 'connects_per_hr', 'project', 'center']
    list_filter  = ['project', 'center']
admin.site.register(OutboundDaily, OutboundDailyAdmin)


class AgentAdmin(admin.ModelAdmin):
    list_display = ['name', 'project']
    list_filter  = ['project']
admin.site.register(Agent, AgentAdmin)

class AgentTransferCallAdmin(admin.ModelAdmin):
    list_display = ['call', 'transfers']
admin.site.register(AgentTransferCall, AgentTransferCallAdmin)

class SkillTransferCallAdmin(admin.ModelAdmin):
    list_display = ['call', 'transfers'] 
admin.site.register(SkillTransferCall, SkillTransferCallAdmin)

class LocationTransferCallAdmin(admin.ModelAdmin):
    list_display = ['call', 'transfers']
admin.site.register(LocationTransferCall, LocationTransferCallAdmin)


class AgentPerformanceAuthoringAdmin(admin.ModelAdmin):
    list_display = ['date', 'agent', 'call_type']
    list_filter  = ['date', 'agent', 'call_type']
admin.site.register(AgentPerformanceAuthoring, AgentPerformanceAuthoringAdmin)

class AgentPerformanceAdmin(admin.ModelAdmin):
    list_display = ['date', 'agent', 'call_type']
    list_filter  = ['date', 'agent', 'call_type']
admin.site.register(AgentPerformance, AgentPerformanceAdmin)



