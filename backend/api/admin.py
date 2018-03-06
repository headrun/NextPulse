from django.contrib import admin
# Register your models here.
from .models import *

class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name']
admin.site.register(Project,ProjectAdmin)

#admin.site.register(Annotation)
class AnnotationAdmin(admin.ModelAdmin):
    list_display = ['project','created_by','dt_created']
admin.site.register(Annotation,AnnotationAdmin)
class CenterAdmin(admin.ModelAdmin):
    list_display = ['name']
admin.site.register(Center,CenterAdmin)

class TeamleadAdmin(admin.ModelAdmin):
    list_display = ['name','project','center']
    list_filter = ('project','center')
admin.site.register(TeamLead,TeamleadAdmin)

class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name']
    #list_filter = ['project']
admin.site.register(Customer,CustomerAdmin)

class HeadcountAdmin(admin.ModelAdmin):
    list_display = ['project','work_packet','sub_packet','date']
    list_filter = ['project','center','work_packet','sub_packet']
admin.site.register(Headcount,HeadcountAdmin)

class CentermanagerAdmin(admin.ModelAdmin):
    list_display = ['name','center']
    list_filter = ['center']
admin.site.register(Centermanager,CentermanagerAdmin)

class NextwealthmanagerAdmin(admin.ModelAdmin):
    list_display = ['name']
    
admin.site.register(Nextwealthmanager,NextwealthmanagerAdmin)

class RawtableAdmin(admin.ModelAdmin):
    list_display = ['work_packet','sub_project','sub_packet','per_day','employee_id','norm','date','created_at','modified_at']
    list_filter = ('work_packet', 'date','project','center','sub_packet')
admin.site.register(RawTable,RawtableAdmin)

class WidgetsAdmin(admin.ModelAdmin):
    list_display = ['config_name','name','api','opt','id_num','day_type_widget','priority']
admin.site.register(Widgets,WidgetsAdmin)

'''
class Widget_MappingAdmin(admin.ModelAdmin):
    list_display = ['widget_name','user_name','widget_priority','is_display','is_drilldown']
    list_filter = ['user_name']
admin.site.register(Widget_Mapping,Widget_MappingAdmin)
'''

class Widgets_groupAdmin(admin.ModelAdmin):
    list_display = ['User_Group','widget_name','widget_priority','is_display','is_drilldown','display_value','project','col']
    #list_display = ['User_Group','widget_name','widget_priority','is_display','is_drilldown','project','col']
    list_filter = ['User_Group','project']
admin.site.register(Widgets_group,Widgets_groupAdmin)

class RawtableAuthoringAdmin(admin.ModelAdmin):
    list_display = ['sub_project','work_packet','sub_packet','employee_id','per_day','norm','date','project','center','sheet_name']
    list_filter = ('project','center')
    list_display_links = ('work_packet',)
admin.site.register(RawtableAuthoring,RawtableAuthoringAdmin)


class InternalerrorsAdmin(admin.ModelAdmin):
    list_display = ['work_packet','sub_project','sub_packet','audited_errors','total_errors','date','employee_id']
    list_filter = ('sub_project','work_packet','sub_packet','project','center')
    list_display_links = ('work_packet',)
admin.site.register(Internalerrors,InternalerrorsAdmin)

class InternalerrorsAuthoringAdmin(admin.ModelAdmin):
    list_display = ['sub_project','work_packet','sub_packet','employee_id','audited_errors','total_errors','date','project','center','sheet_name']
    list_filter = ('project',)
    list_display_links = ('work_packet',)
admin.site.register(InternalerrorsAuthoring,InternalerrorsAuthoringAdmin)


class ExternalerrorsAdmin(admin.ModelAdmin):
    list_display = ['sub_project','work_packet','sub_packet','audited_errors','total_errors','date','employee_id']
    list_filter = ('sub_project','work_packet','sub_packet','project','center')
    list_display_links = ('work_packet',)
admin.site.register(Externalerrors,ExternalerrorsAdmin)

class ExternalerrorsAuthoringAdmin(admin.ModelAdmin):
    #list_display = ['work_packet', 'sub_project', 'sub_packet', 'audited_errors', 'total_errors', 'date', 'employee_id','project', 'center', 'sheet_name']
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
    list_display = ['work_packet','sub_project','sub_packet','from_date','to_date','target_type','target_value','target_method']
    list_filter = ['project','work_packet','sub_packet']
admin.site.register(Targets,TargetsAdmin)


class TargetsAuthoringAdmin(admin.ModelAdmin):
    list_display = ['work_packet','sub_project','sub_packet','project']
    list_filter = ['project']
admin.site.register(TargetsAuthoring,TargetsAuthoringAdmin)

class WorktrackAdmin(admin.ModelAdmin):
    list_display = ['work_packet', 'opening', 'received', 'completed','date', 'sub_packet']
    list_filter = ['project','work_packet','sub_packet']
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
    list_filter = ['project','date']
    list_display_links = ('project',)
admin.site.register(TatTable,TatTableAdmin)

class Alias_WidgetAdmin(admin.ModelAdmin):
    list_display = ['project','alias_widget_name']
    list_filter = ['project']
admin.site.register(Alias_Widget,Alias_WidgetAdmin)

class Alias_packetsAdmin(admin.ModelAdmin):
    #list_display = ['alias_name','widget','existed_name']
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
    list_filter = ['project','work_packet','sub_packet']
admin.site.register(IncomingerrorAuthoring,IncomingerrorAuthoringAdmin)

class IncomingerrorAdmin(admin.ModelAdmin):
    list_display = ['project','center','work_packet','sub_packet','error_values','date']
    list_filter = ['project','work_packet','sub_packet']
admin.site.register(Incomingerror,IncomingerrorAdmin)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['review_name', 'project', 'team_lead']
    list_filter =  ['review_name', 'project', 'team_lead']
admin.site.register(Review,ReviewAdmin)

class ReviewMembersAdmin(admin.ModelAdmin):
    list_display = ['review', 'member']
    list_filter = ['review', 'member']
admin.site.register(ReviewMembers, ReviewMembersAdmin)
"""
class ReviewFilesAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'review__review_name', 'updation_date']
    list_filter =  ['file_name', 'review__review_name', 'updation_date']
admin.site.register(ReviewFiles, ReviewFilesAdmin)
"""



from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

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

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(ChartType)
