from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import Group
#from datetime import datetime


class Center(models.Model):
    name = models.CharField(max_length=255, unique=True,db_index=True)

    class Meta:
        db_table = u'center'
    def __unicode__(self):
        return self.name


class Project(models.Model):
    name    = models.CharField(max_length=255,db_index=True)
    center  = models.ForeignKey(Center, null=True, db_index=True)
    days_week = models.IntegerField(default=5)
    days_month = models.IntegerField(default=21)
    project_db_handlings_choices = (('update','Update'),('aggregate','Aggregate'),('ignore','Ignore'),)
    project_db_handling = models.CharField(max_length=30,choices=project_db_handlings_choices,default='ignore',) 
    sub_project_check = models.BooleanField(default=None)
    is_voice = models.BooleanField(default = False)
    display_value = models.BooleanField(default = False)
    is_enable_push = models.BooleanField(default = False)
    no_of_packets = models.IntegerField(default=5)
    no_of_agents = models.IntegerField(default=5)

    class Meta:
        db_table = u'project'
        index_together = (('name', 'center',), ('name', 'sub_project_check', 'center'),)
    def __unicode__(self):
        return self.name


class TeamLead(models.Model):
    name    = models.ForeignKey(User, null=True, db_index=True)
    project = models.ManyToManyField(Project, null=True)
    center = models.ManyToManyField(Center, null=True)

    class Meta:
        db_table = u'agent'
    def __unicode__(self):
        user_obj = User.objects.filter(id=self.name_id).values_list('username',flat=True)
        return user_obj[0]


class ChartType(models.Model):
    chart_type = models.CharField(max_length=512)

    class Meta:
        db_table = u'chart_type'

    def __unicode__(self):
        return self.chart_type


class Customer(models.Model):
    name    = models.ForeignKey(User, null=True, db_index=True)
    center  = models.ManyToManyField(Center, null=True, db_index=True)
    project = models.ManyToManyField(Project, null=True, db_index=True)
    is_drilldown = models.BooleanField(default=None)
    is_senior = models.BooleanField(default=None)
    is_enable_push_email = models.BooleanField(default=None)

    class Meta:
        db_table = u'customer'
    def __unicode__(self):
        user_obj = User.objects.filter(id=self.name_id).values_list('username',flat=True)
        return user_obj[0]


class Widgets(models.Model):
    config_name = models.CharField(max_length=255,db_index=True)
    name = models.CharField(max_length=255,db_index=True)
    api = models.CharField(max_length=255,null=True, blank=True)
    opt = models.CharField(max_length=225)
    id_num = models.IntegerField()
    day_type_widget = models.BooleanField(default=None)
    priority = models.IntegerField(null=True, blank=True)
    chart_type_name = models.ForeignKey(ChartType, null=True)

    class Meta:
        db_table = u'widgets'
        index_together = (('name', 'config_name',),)
    def __unicode__(self):
        return self.name


class Widgets_group(models.Model):
    User_Group = models.ForeignKey(Group)
    project = models.ForeignKey(Project, null=True,db_index=True)
    center = models.ForeignKey(Center, null=True,db_index=True)
    widget_name = models.ForeignKey(Widgets, null=True,db_index=True)
    col = models.IntegerField(default=0)
    widget_priority = models.IntegerField()
    is_display = models.BooleanField(default=None)
    is_drilldown = models.BooleanField(default = None)
    display_value = models.BooleanField(default = True)

    class Meta:
        db_table = u'Widgets_group'
        index_together = (('project', 'center',), ('User_Group', 'project', 'center'), )
    def __unicode__(self):
        return u''


class Headcount(models.Model):
    date   = models.DateField()
    sub_project = models.CharField(max_length=255, blank=True)
    work_packet = models.CharField(max_length=255,blank=True)
    sub_packet = models.CharField(max_length=255, blank=True)
    center = models.ForeignKey(Center, null=True)
    project = models.ForeignKey(Project, null=True)
    billable_hc = models.FloatField(max_length=255, db_index=True)
    billable_agents = models.FloatField(max_length=255, db_index=True)
    buffer_agents = models.FloatField(max_length=255,db_index=True)
    qc_or_qa = models.FloatField(max_length=255,db_index=True)
    teamlead = models.FloatField(max_length=255, blank=True,db_index=True)
    trainees_and_trainers = models.FloatField(max_length=255,blank=True,db_index=True)
    managers = models.FloatField(max_length=255, blank=True,db_index=True)
    mis = models.FloatField(max_length=255, blank=True,db_index=True)

    class Meta:
        db_table = u'headcount_table'
        index_together = (('project', 'center','sub_project','work_packet','sub_packet','date',), ('project', 'center', 'date'))

    def __unicode__(self):
        return self.work_packet


class HeadcountAuthoring(models.Model):
    date = models.CharField(max_length=255)
    sub_project = models.CharField(max_length=255, blank=True,db_index=True)
    work_packet = models.CharField(max_length=255, blank=True,db_index=True)
    sub_packet = models.CharField(max_length=255, blank=True,db_index=True)
    center = models.ForeignKey(Center, null=True,db_index=True)
    project = models.ForeignKey(Project, null=True,db_index=True)
    billable_hc = models.CharField(max_length=255, db_index=True)
    billable_agents = models.CharField(max_length=255, db_index=True)
    buffer_agents = models.CharField(max_length=255, db_index=True)
    qc_or_qa = models.CharField(max_length=255, db_index=True)
    teamlead = models.CharField(max_length=255, db_index=True)
    trainees_and_trainers = models.CharField(max_length=255, db_index=True)
    managers = models.CharField(max_length=255, db_index=True)
    mis = models.CharField(max_length=255, db_index=True)
    sheet_name = models.CharField(max_length=255, default='')

    class Meta:
        db_table = u'headcount_authoring'
        index_together = (('project', 'center',),)
    def __unicode__(self):
        return self.work_packet


class Centermanager(models.Model):
    name    = models.ForeignKey(User, null=True,db_index=True)
    center  = models.ForeignKey(Center, null=True,db_index=True)

    class Meta:
        db_table = u'center_manager'
    def __unicode__(self):
        user_obj = User.objects.filter(id=self.name_id).values_list('username',flat=True)
        return user_obj[0]


class Nextwealthmanager(models.Model):
    name    = models.ForeignKey(User, null=True, db_index=True)
    center  = models.ManyToManyField(Center)

    class Meta:
        db_table = u'nextwealthmanager'
    def __unicode__(self):
        user_obj = User.objects.filter(id=self.name_id).values_list('username',flat=True)
        return user_obj[0]


class RawTable(models.Model):
    team_lead   = models.ForeignKey(TeamLead, null=True,db_index=True)
    employee_id = models.CharField(max_length=255, blank=True)
    sub_project = models.CharField(max_length=255, blank=True,db_index=True)
    work_packet = models.CharField(max_length=255,db_index=True)
    sub_packet  = models.CharField(max_length=255, blank=True,db_index=True)
    per_hour    = models.IntegerField(max_length=255, default=0)
    per_day     = models.IntegerField(max_length=255, default=0,db_index=True)
    date = models.DateField()
    norm        = models.IntegerField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True, null=True)
    modified_at = models.DateTimeField(auto_now=True,null=True)
    center      = models.ForeignKey(Center, null=True,db_index=True)
    project     = models.ForeignKey(Project, null=True,db_index=True)

    class Meta:
        db_table = u'raw_table'
        index_together = (('project', 'sub_project','work_packet','sub_packet','date', 'center'), ('project', 'center'),
                ('project', 'center', 'date'), ('project', 'sub_project', 'date'), ('project', 'sub_project', 'work_packet', 'date'),
                ('project', 'work_packet', 'date'), ('project', 'center', 'date', 'work_packet'), 
                ('project', 'center', 'date', 'work_packet', 'employee_id'), ('employee_id', 'date', 'work_packet', 'sub_project'),
                ('project', 'sub_project', 'work_packet', 'sub_packet', 'employee_id', 'date', 'center'),
                ('project', 'center', 'date', 'work_packet', 'sub_packet'), ('employee_id','date','work_packet'),
                ('employee_id','date','work_packet'), ('employee_id','date','work_packet','sub_packet'),
                ('project','center', 'date','sub_project'), ('project','center', 'date','work_packet'),)


class RawtableAuthoring(models.Model):
    employee_id = models.CharField(max_length=255, blank=True)
    sub_project = models.CharField(max_length=255, blank=True)
    work_packet = models.CharField(max_length=255)
    sub_packet  = models.CharField(max_length=255, blank=True)
    per_hour    = models.CharField(max_length=255, blank=True)
    per_day     = models.CharField(max_length=255, blank=True)
    date = models.CharField(max_length=255)
    norm        = models.CharField(max_length=255, blank=True)
    center      = models.ForeignKey(Center, null=True,db_index=True)
    project     = models.ForeignKey(Project, null=True,db_index=True)
    sheet_name = models.CharField(max_length=255, default='')
    ignorable_fileds = models.CharField(max_length=255, blank=True,default='')

    class Meta:
        db_table = u'rawtable_authoring'
        index_together = (('project', 'center',),)

    def __unicode__(self):
        return self.work_packet


class Internalerrors(models.Model):
    sub_project = models.CharField(max_length=255, blank=True,db_index=True)
    work_packet = models.CharField(max_length=255,db_index=True)
    sub_packet = models.CharField(max_length=255, blank=True,db_index=True)
    type_error = models.CharField(max_length=255, blank=True)
    sub_error_count = models.CharField(max_length=512, blank=True)
    error_types = models.CharField(max_length=512, blank=True)
    error_values = models.CharField(max_length=512, blank=True)
    audited_errors = models.IntegerField(blank=True,default=0)
    total_errors = models.IntegerField(default=0,verbose_name='total_errors')
    date = models.DateField()
    employee_id = models.CharField(max_length=255,blank=True)
    center      = models.ForeignKey(Center, null=True,db_index=True)
    project     = models.ForeignKey(Project, null=True,db_index=True)

    class Meta:
        db_table = u'internal_error'
        index_together = (('project', 'center','sub_project','work_packet','sub_packet','date'), ('project', 'center', 'date'),
                            ('project', 'center','sub_project','work_packet','sub_packet', 'employee_id', 'date'),
                            ('project', 'center', 'date', 'work_packet'), ('project', 'center', 'work_packet'),
                            ('project', 'center', 'sub_project'), ('project', 'center', 'date', 'sub_project'),
                            ('project', 'center'), ('project', 'center', 'employee_id', 'date'),
                            ('project', 'center', 'date', 'sub_project', 'work_packet'),
                            ('center', 'project', 'date','work_packet','sub_packet'), )

    def __unicode__(self):
        return self.employee_id


class InternalerrorsAuthoring(models.Model):
    sub_project = models.CharField(max_length=255, blank=True)
    work_packet = models.CharField(max_length=255)
    sub_packet = models.CharField(max_length=255, blank=True)
    audited_errors = models.CharField(max_length=255,blank=True,verbose_name='Audited_errors')
    total_errors = models.CharField(max_length=255,default=0,verbose_name='total_errors')
    type_error = models.CharField(max_length=255, blank=True)
    error_category = models.CharField(max_length=255, blank=True)
    error_count = models.CharField(max_length=255, blank=True)
    date = models.CharField(max_length=255)
    employee_id = models.CharField(max_length=255,blank=True)
    center      = models.ForeignKey(Center, null=True,db_index=True)
    project     = models.ForeignKey(Project, null=True,db_index=True)
    sheet_name = models.CharField(max_length=255, default='')
    total_errors_require = models.BooleanField(default=None)

    class Meta:
        db_table = u'internalerrors_authoring'
        index_together = (('project', 'center',),)

    def __unicode__(self):
        return self.work_packet


class Externalerrors(models.Model):
    sub_project = models.CharField(max_length=255, blank=True)
    work_packet = models.CharField(max_length=255)
    sub_packet = models.CharField(max_length=255, blank=True)
    type_error = models.CharField(max_length=255, blank=True)
    sub_error_count = models.CharField(max_length=512, blank=True)
    error_types = models.CharField(max_length=512, blank=True)
    error_values = models.CharField(max_length=512, blank=True)
    audited_errors = models.IntegerField(blank=True, default=0)
    total_errors = models.IntegerField(default=0, verbose_name='total_errors')
    date = models.DateField()
    employee_id = models.CharField(max_length=255, blank=True)
    center = models.ForeignKey(Center, null=True)
    project = models.ForeignKey(Project, null=True)

    class Meta:
        db_table = u'external_error'
        index_together = (('project', 'center', 'date'), ('project', 'center', 'sub_project', 'date'),
                ('project', 'center', 'work_packet', 'date'), ('project', 'center', 'sub_packet', 'date'),
                ('project', 'center', 'sub_project', 'work_packet', 'sub_packet', 'date'), ('project', 'center'),
                ('project', 'center', 'sub_project', 'work_packet', 'sub_packet', 'employee_id', 'date'),
                ('project', 'center', 'employee_id', 'date', 'work_packet', 'sub_packet'), 
                ('project', 'center', 'employee_id', 'date', 'sub_project'),
                ('project', 'center', 'date','sub_project','work_packet'),
                ('center', 'project', 'date', 'work_packet', 'sub_packet'),
                )

    def __unicode__(self):
        return self.employee_id


class ExternalerrorsAuthoring(models.Model):
    sub_project = models.CharField(max_length=255, blank=True)
    work_packet = models.CharField(max_length=255)
    sub_packet = models.CharField(max_length=255, blank=True)
    type_error = models.CharField(max_length=255, blank=True)
    audited_errors = models.CharField(max_length=255,blank=True,verbose_name='Audited_errors')
    total_errors = models.CharField(max_length=255,default=0,verbose_name='total_errors')
    error_category = models.CharField(max_length=255, blank=True)
    error_count = models.CharField(max_length=255, blank=True)
    date = models.CharField(max_length=255)
    employee_id = models.CharField(max_length=255,blank=True)
    center      = models.ForeignKey(Center, null=True,db_index=True)
    project     = models.ForeignKey(Project, null=True,db_index=True)
    sheet_name = models.CharField(max_length=255, default='')
    total_errors_require = models.BooleanField(default=None)


    class Meta:
        db_table = u'externalerrors_authoring'
        index_together = (('project', 'center',),)

    def __unicode__(self):
        return self.work_packet


class Authoringtable(models.Model):
    project = models.ForeignKey(Project, null=True)
    sheet_name = models.CharField(max_length=255, default='')
    table_schema = models.CharField(max_length=255, default='')
    sheet_field = models.CharField(max_length=255, default='')
    center = models.ForeignKey(Center, null=True)
    table_type_choices = (('raw_table', 'Raw_table'), ('external_error', 'External_error'), ('internal_error', 'Internal_error'),('target', 'targets'), ('other', 'Other'),('internal_external','Error'))
    table_type = models.CharField(max_length=30, choices=table_type_choices, default='other', )


    class Meta:
        db_table = u'authoring_table'
        index_together = (('project', 'center',),)
    def __unicode__(self):
        return self.table_schema


class Document(models.Model):
    document = models.FileField(upload_to='media/preprocessing/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = u'upload_table'

    def __unicode__(self):
        return self.description


class Targets(models.Model):
    from_date = models.DateField()
    to_date   = models.DateField()
    sub_project = models.CharField(max_length=255, blank=True,db_index=True)
    work_packet = models.CharField(max_length=255,db_index=True)
    sub_packet  = models.CharField(max_length=255, blank=True,db_index=True)
    target      = models.IntegerField()
    fte_target  = models.IntegerField(default=0)
    target_type = models.CharField(max_length=255, blank=True, db_index=True)
    target_value = models.FloatField(default=0)
    target_method = models.CharField(max_length=125, blank=True, db_index=True)
    center = models.ForeignKey(Center, null=True)
    project = models.ForeignKey(Project, null=True,db_index=True)

    class Meta:
        db_table = u'target_table'
        index_together = (('project', 'center','sub_project','work_packet','sub_packet','from_date','to_date'),
                        ('project', 'center', 'work_packet', 'from_date', 'to_date'),
                        ('project', 'work_packet', 'sub_project', 'from_date', 'to_date', 'target_type', 'center'),)

    def __unicode__(self):
        return self.work_packet


class TargetsAuthoring(models.Model):
    from_date = models.CharField(max_length=255)
    to_date   = models.CharField(max_length=255)
    sub_project = models.CharField(max_length=255, blank=True)
    work_packet = models.CharField(max_length=255, blank=True)
    sub_packet  = models.CharField(max_length=255, blank=True)
    target      = models.CharField(max_length=125)
    fte_target = models.CharField(max_length=125, blank=True)
    target_type = models.CharField(max_length=255, blank=True)
    target_value = models.CharField(max_length=125, blank=True)
    target_method = models.CharField(max_length=125, blank=True)
    center = models.ForeignKey(Center, null=True,db_index=True)
    project = models.ForeignKey(Project, null=True,db_index=True)
    sheet_name = models.CharField(max_length=255, default='')
    class Meta:
        db_table = u'targets_authoring'
        index_together = (('project', 'center',),)

    def __unicode__(self):
        return self.work_packet


class Worktrack(models.Model):
    date = models.DateField()
    sub_project = models.CharField(max_length=255, blank=True,db_index=True)
    work_packet = models.CharField(max_length=255,db_index=True)
    sub_packet = models.CharField(max_length=255, blank=True,db_index=True)
    opening    = models.IntegerField()
    received   = models.IntegerField()
    non_workable_count = models.IntegerField(blank=True,default=0)
    completed   = models.IntegerField()
    closing_balance  = models.IntegerField()
    center = models.ForeignKey(Center, null=True,db_index=True)
    project = models.ForeignKey(Project, null=True,db_index=True)

    class Meta:
        db_table = u'worktrack_table'
        index_together = (('project', 'center', 'date'), ('project', 'center', 'sub_project', 'date'),
                ('project', 'center', 'work_packet', 'date'), ('project', 'center', 'sub_packet', 'date'),
                ('project', 'center', 'sub_project', 'work_packet', 'sub_packet', 'date'), ('project', 'center'),)

    def __unicode__(self):
        return self.work_packet


class WorktrackAuthoring(models.Model):
    date = models.CharField(max_length=255, blank=True)
    sub_project = models.CharField(max_length=255, blank=True)
    work_packet = models.CharField(max_length=255)
    sub_packet = models.CharField(max_length=255, blank=True)
    opening    = models.CharField(max_length=125)
    received   = models.CharField(max_length=125)
    non_workable_count = models.CharField(max_length=125,blank=True)
    completed   = models.CharField(max_length=125)
    closing_balance  = models.CharField(max_length=125)
    center = models.ForeignKey(Center, null=True,db_index=True)
    project = models.ForeignKey(Project, null=True,db_index=True)
    sheet_name = models.CharField(max_length=255, default='')

    class Meta:
        db_table = u'worktrack_authornig'
        index_together = (('project', 'center',),)

    def __unicode__(self):
        return self.work_packet


class Color_Mapping(models.Model):
    sub_project = models.CharField(max_length=255, blank=True)
    work_packet = models.CharField(max_length=255, blank=True)
    sub_packet = models.CharField(max_length=255, blank=True)
    color_code = models.CharField(max_length=255)
    center = models.ForeignKey(Center, null=True,db_index=True)
    project = models.ForeignKey(Project, null=True,db_index=True)
    class Meta:
        db_table = u'color_mappping'
        index_together = (('project', 'center','sub_project','work_packet','sub_packet',),)

    def __unicode__(self):
        return self.work_packet


class Annotation(models.Model):
    epoch = models.CharField(max_length=40,verbose_name='selected_date')
    text = models.TextField()
    key = models.CharField(max_length=512, null=True)
    dt_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User,db_index=True)
    center = models.ForeignKey(Center,db_index=True)
    project = models.ForeignKey(Project,db_index=True)
    chart_type_name = models.ForeignKey(ChartType, null=True)
    chart_id = models.IntegerField(default=0)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)

    class Meta:
        db_table = u'annotations'
        index_together = (('project', 'center',), ('epoch', 'created_by', 'key'),)
        unique_together = (('project', 'center', 'epoch', 'key'))

    def __unicode__(self):
        return self.epoch


class Alias_Widget(models.Model):
    project = models.ForeignKey(Project,db_index=True)
    widget_name = models.ForeignKey(Widgets,db_index=True)
    alias_widget_name = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = u'alias_widget'
        index_together = (('project', 'widget_name',),)

    def __unicode__(self):
        return '%s - %s' % (str(self.project),str(self.widget_name))


class Profile(models.Model):
    user = models.ForeignKey(User, db_index=True)
    activation_key = models.CharField(max_length=40)
    status = models.BooleanField(default=0)

    class Meta:
        db_table = u'profile'


class Alias_packets(models.Model):
    widget = models.ForeignKey(Alias_Widget, null=True,db_index=True)
    existed_name = models.CharField(max_length=255, blank=True,db_index=True)
    alias_name = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = u'alias_packets'

    def __unicode__(self):
        return self.alias_name


class UploadAuthoring(models.Model):
    date = models.CharField(max_length=255, blank=True)
    sub_project = models.CharField(max_length=255, blank=True)
    target = models.CharField(max_length=255, blank=True)
    upload = models.CharField(max_length=255, blank=True)
    center = models.ForeignKey(Center, null=True,db_index=True)
    project = models.ForeignKey(Project, null=True,db_index=True)
    sheet_name = models.CharField(max_length=255, default='')

    class Meta:
        db_table = u'upload_authoring'

    def __unicode__(self):
        return u''


class UploadDataTable(models.Model):
    date = models.DateField()
    sub_project = models.CharField(max_length=255, blank=True)
    target = models.IntegerField(default = 0)
    upload = models.IntegerField()
    center = models.ForeignKey(Center, null=True,db_index=True)
    project = models.ForeignKey(Project, null=True,db_index=True)

    class Meta:
        db_table = u'upload_data_table'
        index_together = (('project', 'center', 'date'), ('project', 'sub_project', 'center', 'date'), )
    def __unicode__(self):
        return u''


class IncomingerrorAuthoring(models.Model):
    date = models.CharField(max_length=255, blank=True)
    sub_project = models.CharField(max_length=255, blank=True)
    work_packet = models.CharField(max_length=255, blank=True)
    sub_packet = models.CharField(max_length=255, blank=True)
    project = models.ForeignKey(Project, null=True)
    center = models.ForeignKey(Center, null=True)
    error_values = models.CharField(max_length=255, blank=True)
    sheet_name = models.CharField(max_length=255, default='')

    class Meta:
        db_table = u'incoming_error_authoring'

    def __unicode__(self):
        return self.work_packet


class Incomingerror(models.Model):
    date = models.DateField()
    sub_project = models.CharField(max_length=255, blank=True,db_index=True)
    work_packet = models.CharField(max_length=255,db_index=True)
    sub_packet = models.CharField(max_length=255, blank=True,db_index=True)
    error_values = models.IntegerField()
    project = models.ForeignKey(Project, null=True)
    center = models.ForeignKey(Center, null=True)

    class Meta:
        db_table = u'incoming_error'
        index_together = (('project', 'center', 'sub_project', 'work_packet', 'sub_packet', 'date'),
                            ('project', 'center', 'work_packet', 'date'), ('project', 'center', 'sub_packet', 'date'),
                            ('project', 'center', 'work_packet','sub_packet', 'date'), )

    def __unicode__(self):
        return self.work_packet


class TatAuthoring(models.Model):
    sub_project = models.CharField(max_length=255, blank=True)
    work_packet = models.CharField(max_length=255, blank=True)
    sub_packet = models.CharField(max_length=255, blank=True)
    center = models.ForeignKey(Center, null=True)
    project = models.ForeignKey(Project, null=True)
    date = models.CharField(max_length=125, default='Date')
    total_received = models.CharField(max_length=255, blank=True)
    met_count = models.CharField(max_length=125, blank = True)
    non_met_count = models.CharField(max_length=125, blank= True)
    tat_status = models.CharField(max_length=255, blank=True)
    sheet_name = models.CharField(max_length=255, default='')

    class Meta:
        db_table = u'tat_authoring'

    def __unicode__(self):
        return self.tat_status


class TatTable(models.Model):
    sub_project = models.CharField(max_length=255, blank=True)
    work_packet = models.CharField(max_length=255)
    sub_packet = models.CharField(max_length=255, blank=True)
    center = models.ForeignKey(Center, null=True)
    project = models.ForeignKey(Project, null=True)
    date = models.DateField()
    total_received = models.IntegerField()
    met_count = models.IntegerField()
    non_met_count = models.IntegerField(blank= True)
    tat_status = models.CharField(max_length=255)

    class Meta:
        db_table = u'tats_table'
        index_together = (('project', 'center', 'date'), ('project', 'center', 'sub_project', 'work_packet', 'sub_packet', 'date'), )

    def __unicode__(self):
        return self.tat_status


class AHTIndividualAuthoring(models.Model):
    date = models.CharField(max_length=255)
    emp_name = models.CharField(max_length=255, blank=True)
    sub_project = models.CharField(max_length=255, blank=True)
    work_packet = models.CharField(max_length=255, blank=True)
    sub_packet = models.CharField(max_length=255, blank=True)
    center = models.ForeignKey(Center)
    project = models.ForeignKey(Project)
    AHT = models.CharField(max_length=255)
    sheet_name = models.CharField(max_length=255, default='AHT Individual')

    class Meta:
        db_table = u'AHT_individual_authoring'
        
    def __unicode__(self):
        return self.work_packet
 

class AHTIndividual(models.Model):
    date = models.DateField()
    emp_name = models.CharField(max_length=255, blank=True)
    sub_project = models.CharField(max_length=255, blank=True)
    work_packet = models.CharField(max_length=255, blank=True)
    sub_packet = models.CharField(max_length=255, blank=True)
    center = models.ForeignKey(Center)
    project = models.ForeignKey(Project)
    AHT = models.FloatField(max_length=125, default=0)

    class Meta:
        db_table = u'AHT_individual'
        index_together = (('project', 'center', 'date'), ('project', 'center', 'work_packet', 'date'),
                            ('project', 'center', 'sub_project', 'work_packet', 'date'), ('project', 'center', 'date', 'emp_name'),
                            ('project', 'center', 'sub_project', 'work_packet', 'sub_packet', 'date'), 
                            ('project', 'center', 'date', 'work_packet', 'emp_name'),
                            ('project', 'center', 'date', 'work_packet', 'sub_packet', 'emp_name'),
                            ('project', 'center', 'date', 'sub_project', 'work_packet', 'sub_packet', 'emp_name'), )

    def __unicode__(self):
        return self.work_packet


class AHTTeamAuthoring(models.Model):
    date = models.CharField(max_length=255)
    sub_project = models.CharField(max_length=255, blank=True)
    work_packet = models.CharField(max_length=255, blank=True)
    sub_packet = models.CharField(max_length=255, blank=True)
    center = models.ForeignKey(Center)
    project = models.ForeignKey(Project)
    AHT = models.CharField(max_length=255)
    sheet_name = models.CharField(max_length=255, default='AHT Team')
    
    class Meta:
        db_table = u'AHT_team_authoring'

    def __unicode__(self):
        return self.work_packet


class AHTTeam(models.Model):
    date = models.DateField()
    sub_project = models.CharField(max_length=255, blank=True)
    work_packet = models.CharField(max_length=255, blank=True)
    sub_packet = models.CharField(max_length=255, blank=True)
    center = models.ForeignKey(Center)
    project = models.ForeignKey(Project)
    AHT = models.FloatField(max_length=125, default=0)

    class Meta:
        db_table = u'AHT_team'
        index_together = (('project', 'center', 'date'), ('project', 'center', 'work_packet', 'date'),
                            ('project', 'center', 'sub_project', 'work_packet', 'date'),
                            ('project', 'center', 'sub_project', 'work_packet', 'sub_packet', 'date'), )

    def __unicode__(self):
        return self.work_packet


class Review(models.Model):
    """ model to store Reviews """
    review_name = models.CharField(max_length=255, db_index=True)
    review_agenda = models.TextField(null=True, blank = True)
    project = models.ForeignKey(Project, db_index=True)
    team_lead = models.ForeignKey(TeamLead, db_index=True)
    review_date = models.DateTimeField(null=True, db_index=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    updation_date = models.DateTimeField(auto_now=True)
    review_type = models.CharField(max_length=16, blank = True)
    venue = models.TextField(null=True, blank = True)
    bridge = models.CharField(max_length=64, blank = True)

    class Meta:
        db_table = u'review_system'
        unique_together = (('review_name', 'project', 'review_date'), )
        index_together = (('project', 'review_name', 'review_date'), )

    def __unicode__(self):
        return self.review_name


class ReviewFiles(models.Model):
    """ model to store files for reviews """
    file_name = models.FileField(upload_to='reviews/%Y%m', db_index=True)
    review = models.ForeignKey(Review, db_index=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    updation_date = models.DateTimeField(auto_now=True)
    original_file_name = models.CharField(max_length=64)

    class Meta:
        db_table = u'review_files'
        index_together = (('review', 'file_name'), ('original_file_name', 'review') )
        unique_together = (('review', 'file_name'), )


class ReviewMembers(models.Model):
    """ Model to store name of all persons associated in a review """
    review = models.ForeignKey(Review, db_index=True)
    member = models.ForeignKey(User, null=True, db_index=True)
    reminder_mail = models.BooleanField(default = False, db_index=True)
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = u'review_members'


class HRMMovementTracker(models.Model):
    recordid = models.AutoField(primary_key=True)
    empid = models.CharField(max_length = 20, null = False)
    oldteam = models.CharField(max_length = 100, null = False)
    oldscope = models.CharField(max_length = 100, null = False)
    oldrole = models.CharField(max_length = 100, null = False)
    newteam = models.CharField(max_length = 100, null = False)
    newscope =models.CharField(max_length = 100, null = False)
    newrole = models.CharField(max_length = 100, null = False)
    movedate = models.DateField(null = False)
    reason = models.CharField(max_length = 500, null = False)
    approval = models.CharField(max_length = 3, null = False)
    hc_tracker = models.CharField(max_length = 3, null = False)
    misreport = models.CharField(max_length = 3, null = False)
    e4e = models.CharField(max_length = 3, null = False)
    boimetric = models.CharField(max_length = 3, null = False)
    domain = models.CharField(max_length = 3, null = False)
    teamdata = models.CharField(max_length = 3, null = False)
    risedfrom = models.CharField(max_length = 150, null = False)
    approvedby = models.CharField(max_length = 150, null = False)
    time_stamp = models.DateTimeField(auto_now_add = True, null=False)

    class Meta:
        db_table = u'hrm_movement_tracker'


class HRMAttendance(models.Model):
    sno =  models.AutoField(primary_key=True)
    empid = models.CharField(max_length = 20, null = False)
    A01 = models.CharField(max_length = 5, null = False)
    A02 = models.CharField(max_length = 5, null = False)
    A03 = models.CharField(max_length = 5, null = False)
    A04 = models.CharField(max_length = 5, null = False)
    A05 = models.CharField(max_length = 5, null = False)
    A06 = models.CharField(max_length = 5, null = False)
    A07 = models.CharField(max_length = 5, null = False)
    A08 = models.CharField(max_length = 5, null = False)
    A09 = models.CharField(max_length = 5, null = False)
    A10 = models.CharField(max_length = 5, null = False)
    A11 = models.CharField(max_length = 5, null = False)
    A11 = models.CharField(max_length = 5, null = False)
    A12 = models.CharField(max_length = 5, null = False)
    A13 = models.CharField(max_length = 5, null = False)
    A14 = models.CharField(max_length = 5, null = False)
    A15 = models.CharField(max_length = 5, null = False)
    A16 = models.CharField(max_length = 5, null = False)
    A17 = models.CharField(max_length = 5, null = False)
    A18 = models.CharField(max_length = 5, null = False)
    A19 = models.CharField(max_length = 5, null = False)
    A20 = models.CharField(max_length = 5, null = False)
    A21 = models.CharField(max_length = 5, null = False)
    A22 = models.CharField(max_length = 5, null = False)
    A23 = models.CharField(max_length = 5, null = False)
    A24 = models.CharField(max_length = 5, null = False)
    A25 = models.CharField(max_length = 5, null = False)
    A26 = models.CharField(max_length = 5, null = False)
    A27 = models.CharField(max_length = 5, null = False)
    A28 = models.CharField(max_length = 5, null = False)
    A29 = models.CharField(max_length = 5, null = False)
    A30 = models.CharField(max_length = 5, null = False)
    A31 = models.CharField(max_length = 5, null = False)
    month = models.CharField(max_length = 20, null = False)
    time_stamp = models.DateTimeField(auto_now_add = True, null=False)

    class Meta:
        db_table = u'hrm_attendance'


class HRMEmployeeProcess(models.Model):
    empid = models.CharField(max_length = 10, null = False)
    team = models.CharField(max_length = 50, null = False)
    start_date = models.DateField(null = False)
    end_date = models.DateField(null = False)
    time_stamp = models.DateTimeField(auto_now_add  = True, null = False)

    class Meta:
        db_table = u'hrm_employee_process'


class HRMEmployeeReportingPerson(models.Model):
    empid = models.CharField(max_length = 12, primary_key=True)
    name = models.CharField(max_length = 150, null = False)
    reporting_person = models.CharField(max_length = 12, null = False)
    time_stamp = models.DateTimeField(auto_now_add = True, null=False)

    class Meta:
        db_table = u'hrm_employee_reportingperson'


class HRMEmployeeResignation(models.Model):
    empid =  models.CharField(max_length = 15, null = False)
    relivingtype =  models.CharField(max_length = 25, null = False)
    resignedon =  models.CharField(max_length = 10, null = False)
    noticeperiod =  models.CharField(max_length = 5, null = False)
    ulsince =  models.CharField(max_length = 10, null = False)
    memoon =  models.CharField(max_length = 10, null = False)
    raplymemo =  models.CharField(max_length = 5, null = False)
    lastday =  models.CharField(max_length = 10, null = False)
    idcard = models.CharField(max_length = 10, null = False)
    resion =  models.CharField(max_length = 1000, null = False)
    status =  models.CharField(max_length = 5, null = False)
    #rdate =  models.CharField(max_length = 50, null = False)
    rdate = models.DateTimeField(auto_now_add = True, null=False)

    class Meta:
        db_table = u'hrm_employee_resignation'


class OneSignal(models.Model):
    device_id = models.CharField(max_length = 125, null=False)
    user = models.ForeignKey(User, null=False)

    class Meta:
        db_table = u'onesignal_deviceid'
