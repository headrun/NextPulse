
from django.core.management.base import BaseCommand, CommandError

from api.models import *

from datetime import datetime

from django.db.models.functions import *

from django.db.models import *

from django.db.models import Count

class Command(BaseCommand):

    help = "Daily script for error data from live error table to Internal error table"

    def handle(self, *args, **options):

        dt = datetime.today().date()
        proj = live_error_table.objects.annotate(s_day = Trunc('prod_end_time','date',output_field=DateField())).\
                exclude(s_day__isnull=True).filter(s_day__gte="2019-05-20").values('project','center','sub_project','work_packet','sub_packet','s_day','production_agent','error_type').annotate(trans = Count('transaction_id'))
        if proj != None:
                dict_val = {}
                for obj in proj:
                        key = "%s_%s_%s_%s_%s"%(obj['s_day'],obj['production_agent'],obj['sub_project'],obj['work_packet'],obj['sub_packet'])
                        dict_obj = {}
                        if dict_val.has_key(key):
                                dict_val[key]['error_type'] = dict_val[key]['error_type']+'#<>#'+obj['error_type']
                                dict_val[key]['error_values'] = str(dict_val[key]['error_values'])+'#<>#'+str(obj['trans'])
                                dict_val[key]['total_errors'] = int(dict_val[key]['total_errors'])+int(obj['trans'])
                        else:
                                dict_obj['project']=obj['project']
                                dict_obj['center']=obj['center']
                                dict_obj['sub_project']=obj['sub_project']
                                dict_obj['work_packet']=obj['work_packet']
                                dict_obj['sub_packet']=obj['sub_packet']
                                dict_obj['s_day']=obj['s_day']
                                dict_obj['prod_agent']=obj['production_agent']
                                dict_obj['error_type']=obj['error_type']
                                dict_obj['error_values']=obj['trans']
                                dict_obj['total_errors']=obj['trans']
                                dict_val[key] = dict_obj
                for key,val in dict_val.iteritems():
                        project = Project.objects.get(id=val['project'])
                        center = Center.objects.get(id=val['center'])
                        if val['sub_packet'] == None:
                                val['sub_packet'] = ''
                        if val['sub_project'] == None:
                                val['sub_project'] = ''
                        if val['work_packet'] == None:
                                val['work_packet'] = ''
                        params = {'sub_project':val['sub_project'],'work_packet':val['work_packet'],'sub_packet':val['sub_packet'],'project':project,'center':center,'employee_id':val['prod_agent'],'total_errors':val['total_errors'],'error_types':val['error_type'],'error_values':val['error_values'],'date':val['s_day']}
                        obj = Internalerrors(**params)
                        obj.save()
                