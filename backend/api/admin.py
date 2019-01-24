from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django import forms
from django.utils.translation import ugettext_lazy as _
from api.models import *


class ProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'UserProfile'
    fk_name = 'user'


def enable_is_active(modeladmin, request, queryset):
    queryset.update(is_active=True)        
enable_is_active.short_description = 'Enable active to selected ones'


def disable_is_active(modeladmin, request, queryset):
    queryset.update(is_active=False)
disable_is_active.short_description = 'Disable active to selected ones'


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )
    list_display = ["username","email","first_name","last_name",'get_phone_no',"is_active"]
    list_select_related = ('userprofile', )
    actions = [enable_is_active,disable_is_active]

    def get_phone_no(self, instance):
        return instance.userprofile.phone_number
    get_phone_no.short_description = 'Phone No'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


def pro_enable_push_notifications(modeladmin, request, queryset):
        queryset.update(is_enable_push=True)
pro_enable_push_notifications.short_description = "Enable web push for selected ones"

def pro_disable_push_notifications(modeladmin, request, queryset):
        queryset.update(is_enable_push=False)
pro_disable_push_notifications.short_description = "Disable web push for selected ones"

def pro_enable_mail_notifications(modeladmin, request, queryset):
        queryset.update(is_enable_mail=True)
pro_enable_mail_notifications.short_description = "Enable mail for selected ones"

def pro_disable_mail_notifications(modeladmin, request, queryset):
        queryset.update(is_enable_mail=False)
pro_disable_mail_notifications.short_description = "Disable mail for selected ones"

def pro_enable_sms_notifications(modeladmin, request, queryset):
        queryset.update(is_enable_sms=True)
pro_enable_sms_notifications.short_description = "Enable sms for selected ones"

def pro_disable_sms_notifications(modeladmin, request, queryset):
        queryset.update(is_enable_sms=False)
pro_disable_sms_notifications.short_description = "Disable sms for selected ones"

def enable_mail_notifications(modeladmin, request, queryset):
        queryset.update(enable_push_email=True)
enable_mail_notifications.short_description = "Enable mail for selected ones"

def disable_mail_notifications(modeladmin, request, queryset):
        queryset.update(enable_push_email=False)
disable_mail_notifications.short_description = "Disable mail for selected ones"


class ProjectAdmin(admin.ModelAdmin):
    list_display = ['id','name','display_project','is_voice', 'is_enable_mail','is_enable_push','is_enable_sms']
    list_filter = ['center']
    actions = [pro_enable_mail_notifications, pro_disable_mail_notifications,pro_enable_push_notifications,pro_disable_push_notifications,pro_enable_sms_notifications,pro_disable_sms_notifications]
admin.site.register(Project,ProjectAdmin)


class AnnotationAdmin(admin.ModelAdmin):
    list_display = ['project','created_by','dt_created','chart_id','text','epoch','start_date','end_date','id']
admin.site.register(Annotation,AnnotationAdmin)


class CenterAdmin(admin.ModelAdmin):
    list_display = ['name']
admin.site.register(Center,CenterAdmin)


def L_enable_push_notifications(modeladmin, request, queryset):
        queryset.update(enable_push=True)
L_enable_push_notifications.short_description = "Enable web push for selected ones"

def L_disable_push_notifications(modeladmin, request, queryset):
        queryset.update(enable_push=False)
L_disable_push_notifications.short_description = "Disable web push for selected ones"

def L_enable_mail_notifications(modeladmin, request, queryset):
        queryset.update(enable_mail=True)
L_enable_mail_notifications.short_description = "Enable mail for selected ones"

def L_disable_mail_notifications(modeladmin, request, queryset):
        queryset.update(enable_mail=False)
L_disable_mail_notifications.short_description = "Disable mail for selected ones"

def L_enable_sms_notifications(modeladmin, request, queryset):
        queryset.update(enable_sms=True)
L_enable_sms_notifications.short_description = "Enable sms for selected ones"

def L_disable_sms_notifications(modeladmin, request, queryset):
        queryset.update(enable_sms=False)
L_disable_sms_notifications.short_description = "Disable sms for selected ones"


class TeamleadAdmin(admin.ModelAdmin):
    list_display = ['id','name','get_projects','enable_mail','enable_push','enable_sms']
    actions = [L_enable_mail_notifications, L_disable_mail_notifications, L_enable_sms_notifications, L_disable_sms_notifications, L_enable_push_notifications, L_disable_push_notifications ]
    def get_projects(self, obj):
        return ", \n".join([p.name for p in obj.project.all()])
    get_projects.short_description = "Projects"
admin.site.register(TeamLead,TeamleadAdmin)


class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id','name','get_projects','enable_mail','enable_push','enable_sms']
    actions = [L_enable_mail_notifications, L_disable_mail_notifications, L_enable_sms_notifications, L_disable_sms_notifications, L_enable_push_notifications, L_disable_push_notifications ]
    def get_projects(self, obj):
        return ", \n".join([p.name for p in obj.project.all()])
    get_projects.short_description = "Projects"
admin.site.register(Customer,CustomerAdmin)


class HeadcountAdmin(admin.ModelAdmin):
    list_display = ['project','sub_project','work_packet','sub_packet','date']
    list_filter = ['project','center']
admin.site.register(Headcount,HeadcountAdmin)


class CentermanagerAdmin(admin.ModelAdmin):
    list_display = ['name','center','enable_mail','enable_push']
    list_filter = ['center']
    actions = [L_enable_mail_notifications, L_disable_mail_notifications, L_enable_push_notifications, L_disable_push_notifications ]
admin.site.register(Centermanager,CentermanagerAdmin)


class NextwealthmanagerAdmin(admin.ModelAdmin):
    list_display = ['name','enable_mail','enable_push']
    actions = [L_enable_mail_notifications, L_disable_mail_notifications, L_enable_push_notifications, L_disable_push_notifications ]
admin.site.register(Nextwealthmanager,NextwealthmanagerAdmin)


class RawtableAdmin(admin.ModelAdmin):
    list_display = ['work_packet','sub_project','sub_packet','per_day','employee_id','norm','date','created_at','modified_at']
    list_filter = ('project','center','sub_project')
admin.site.register(RawTable,RawtableAdmin)


class WidgetsAdmin(admin.ModelAdmin):
    list_display = ['config_name','name','api','opt','id_num','day_type_widget','priority']
admin.site.register(Widgets,WidgetsAdmin)


class Widgets_groupAdmin(admin.ModelAdmin):
    list_display = ['User_Group','widget_name','widget_priority','is_display','is_drilldown','display_value','project','col']
    list_filter = ['User_Group','project']
admin.site.register(Widgets_group,Widgets_groupAdmin)


class RawtableAuthoringAdmin(admin.ModelAdmin):
    list_display = ['sub_project','work_packet','sub_packet','employee_id','per_day','norm','date','project','center','sheet_name']
    list_filter = ('project','center')
    list_display_links = ('work_packet',)
admin.site.register(RawtableAuthoring,RawtableAuthoringAdmin)


class InternalerrorsAdmin(admin.ModelAdmin):
    list_display = ['work_packet','sub_project','sub_packet','audited_errors','total_errors','date','employee_id']
    list_filter = ('sub_project','project','center')
    list_display_links = ('work_packet',)
admin.site.register(Internalerrors,InternalerrorsAdmin)


class InternalerrorsAuthoringAdmin(admin.ModelAdmin):
    list_display = ['sub_project','work_packet','sub_packet','employee_id','audited_errors','total_errors','date','project','center','sheet_name']
    list_filter = ('project',)
    list_display_links = ('work_packet',)
admin.site.register(InternalerrorsAuthoring,InternalerrorsAuthoringAdmin)


class ExternalerrorsAdmin(admin.ModelAdmin):
    list_display = ['sub_project','work_packet','sub_packet','audited_errors','total_errors','date','employee_id']
    list_filter = ('sub_project','project','center')
    list_display_links = ('work_packet',)
admin.site.register(Externalerrors,ExternalerrorsAdmin)


class ExternalerrorsAuthoringAdmin(admin.ModelAdmin):
    list_display = ['sub_project','work_packet','sub_packet','employee_id','audited_errors','total_errors','date','project','center','sheet_name']
    list_filter = ('project',)
    list_display_links = ('work_packet',)
admin.site.register(ExternalerrorsAuthoring,ExternalerrorsAuthoringAdmin)


class AuthoringtableAdmin(admin.ModelAdmin):
    list_display = ['sheet_name','table_schema','sheet_field','project','center','table_type']
    list_filter = ['sheet_name','project','center']
admin.site.register(Authoringtable,AuthoringtableAdmin)


class HeadcountAuthoringAdmin(admin.ModelAdmin):
    list_display = ['project','center','work_packet','sub_packet']
    list_filter = ['project','center']
admin.site.register(HeadcountAuthoring,HeadcountAuthoringAdmin)


class TargetsAdmin(admin.ModelAdmin):
    list_display = ['project','work_packet','sub_project','sub_packet','from_date','to_date','target_type','target_value']
    list_filter = ['project','sub_project']
admin.site.register(Targets,TargetsAdmin)


class TargetsAuthoringAdmin(admin.ModelAdmin):
    list_display = ['work_packet','sub_project','sub_packet','project']
    list_filter = ['project']
admin.site.register(TargetsAuthoring,TargetsAuthoringAdmin)


class WorktrackAdmin(admin.ModelAdmin):
    list_display = ['work_packet', 'opening', 'received', 'completed','date', 'sub_packet']
    list_filter = ['project']
admin.site.register(Worktrack,WorktrackAdmin)


class WorktrackAuthoringAdmin(admin.ModelAdmin):
    list_display = ['work_packet','sub_project','sub_packet','project']
    list_filter = ['project']
admin.site.register(WorktrackAuthoring,WorktrackAuthoringAdmin)


class TatAuthoringAdmin(admin.ModelAdmin):
    list_display = ['work_packet','sub_project','sub_packet','tat_status']
    list_filter = ['project']
admin.site.register(TatAuthoring,TatAuthoringAdmin)


class TatTableAdmin(admin.ModelAdmin):
    list_display = ['work_packet','sub_project','tat_status','project','date']
    list_filter = ['project']
    list_display_links = ('project',)
admin.site.register(TatTable,TatTableAdmin)


class AHTIndividualAuthoringAdmin(admin.ModelAdmin):
    list_display = ['project','center','date','emp_name','work_packet','AHT']
    list_filter = ['project']
admin.site.register(AHTIndividualAuthoring,AHTIndividualAuthoringAdmin)


class AHTIndividualAdmin(admin.ModelAdmin):
    list_display = ['project','center','date','emp_name','work_packet','AHT']
    list_filter = ['project']
admin.site.register(AHTIndividual,AHTIndividualAdmin)


class AHTTeamAuthoringAdmin(admin.ModelAdmin):
    list_display = ['project','center','date','work_packet','AHT']
    list_filter = ['project']
admin.site.register(AHTTeamAuthoring,AHTTeamAuthoringAdmin)


class AHTTeamAdmin(admin.ModelAdmin):
    list_display = ['project','center','date','work_packet','AHT']
    list_filter = ['project']
admin.site.register(AHTTeam,AHTTeamAdmin)


class Alias_WidgetAdmin(admin.ModelAdmin):
    list_display = ['project','alias_widget_name']
    list_filter = ['project']
admin.site.register(Alias_Widget,Alias_WidgetAdmin)


class Alias_packetsAdmin(admin.ModelAdmin):
    list_display = ['widget','existed_name','alias_name']
    list_filter = ['alias_name']
admin.site.register(Alias_packets,Alias_packetsAdmin)


class UploadAuthoringAdmin(admin.ModelAdmin):
    list_display = ['project','target','upload']
admin.site.register(UploadAuthoring,UploadAuthoringAdmin)


class UploadDataTableAdmin(admin.ModelAdmin):
    list_display = ['project','target','upload','date']
admin.site.register(UploadDataTable,UploadDataTableAdmin)


class IncomingerrorAuthoringAdmin(admin.ModelAdmin):
    list_display = ['project','center','work_packet','sub_packet','error_values']
    list_filter = ['project']
admin.site.register(IncomingerrorAuthoring,IncomingerrorAuthoringAdmin)


class IncomingerrorAdmin(admin.ModelAdmin):
    list_display = ['project','center','work_packet','sub_packet','error_values','date']
    list_filter = ['project']
admin.site.register(Incomingerror,IncomingerrorAdmin)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ['review_name', 'project', 'team_lead']
    list_filter =  ['review_name', 'project', 'team_lead']
admin.site.register(Review,ReviewAdmin)


class ReviewMembersAdmin(admin.ModelAdmin):
    list_display = ['review', 'member']
    list_filter = ['review', 'member']
admin.site.register(ReviewMembers, ReviewMembersAdmin)


class IVR_VCRAdmin(admin.ModelAdmin):
    list_display = ['date', 'center','project']
    list_filter = ['center', 'project']
admin.site.register(IVR_VCR, IVR_VCRAdmin)


class IVR_VCR_authoringAdmin(admin.ModelAdmin):
    list_display = ["date","center","project"]
    list_filter = ['center', 'project']
admin.site.register(IVR_VCR_authoring, IVR_VCR_authoringAdmin)


class RiskAdmin(admin.ModelAdmin):
    list_display = ['date', 'center','project']
    list_filter = ['center', 'project']
admin.site.register(Risk, RiskAdmin )


class Risk_authoringAdmin(admin.ModelAdmin):
    list_display = ["date","center","project"]
    list_filter = ['center', 'project']
admin.site.register(Risk_authoring, Risk_authoringAdmin)


class TimeAdmin(admin.ModelAdmin):
    list_display = ['date', 'center','project']
    list_filter = ['center', 'project']
admin.site.register(Time, TimeAdmin )


class Time_authoringAdmin(admin.ModelAdmin):
    list_display = ["date","center","project"]
    list_filter = ['center', 'project']
admin.site.register(Time_authoring, Time_authoringAdmin)




class UserCreationFormExtended(UserCreationForm): 
    def __init__(self, *args, **kwargs): 
        super(UserCreationFormExtended, self).__init__(*args, **kwargs) 
        self.fields['first_name'] = forms.CharField(label=_("First Name"), max_length=30)
        self.fields['last_name'] = forms.CharField(label=_("Last Name"), max_length=30)
        self.fields['email'] = forms.EmailField(label=_("E-mail"), max_length=75)

UserAdmin.add_form = UserCreationFormExtended
UserAdmin.add_fieldsets = (
    (None, {
        'classes': ('wide',),
        'fields': ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',)
    }),
)


admin.site.register(ChartType)


