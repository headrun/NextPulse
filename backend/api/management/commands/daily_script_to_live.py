
from django.core.management.base import BaseCommand, CommandError

from api.models import *

from datetime import datetime

from django.db.models.functions import *

from django.db.models import *

from django.db.models import Count

class Command(BaseCommand):
    
    help = 'Daily script to save from live transaction table to RawTable'

    def handle(self, *args, **options):
        
        dt = datetime.today().date()
        proj = live_transaction_table.objects.annotate(s_day = Trunc('end_time','date',output_field=DateField())).\
                exclude(s_day__isnull=True).filter(s_day__gte="2019-05-20").values('project','center','sub_project','work_packet','sub_packet','s_day','emp_name').annotate(trans = Count('transaction_id'))
        if proj != None:
            for val in proj:
                center = Center.objects.get(id = val['center'])
                proj = Project.objects.get(id = val['project'])
                if val['sub_packet'] == None:
                    val['sub_packet'] = ''
                if val['sub_project'] == None:
                    data_val = {'date':val['s_day'],'employee_id':val['emp_name'],'project':proj,'center':center,'work_packet':val['work_packet'],'sub_packet':val['sub_packet'],'per_day':val['trans'],'norm':0}
                    obj = RawTable(**data_val)
                else:
                    data_val = {'date':val['s_day'],'employee_id':val['emp_name'],'project':proj,'center':center,'sub_project':val['sub_project'],'work_packet':val['work_packet'],'sub_packet':val['sub_packet'],'per_day':val['trans'],'norm':0}
                    obj = RawTable(**data_val)
                obj.save()