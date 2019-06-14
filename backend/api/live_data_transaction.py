
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from api.models import live_transaction_table,Center,Project,live_error_table,live_agent_login_table,live_break_time
from datetime import datetime
from django.utils.timezone import localtime,now
import pytz

@csrf_exempt
def live_data_store(request):
    if request.method == "POST":
        data_val = json.loads(request.body)
        for key,value in data_val.iteritems():
            center = Center.objects.get(name=value[0]['center'])
            proj = Project.objects.get(name=value[0]['project'])
            dt = {'center':center,'project':proj,'sub_project':value[0]['batch_name'],'work_packet':value[0]['status'],\
            'transaction_id':value[0]['id'],'agent_role':value[0]['role'],'start_time':value[0]['start_time'].split('.')[0],'end_time':value[0]["end_time"].split('.')[0],\
            'emp_name':value[0]['emp_name']}
            obj1, created = live_transaction_table.objects.update_or_create(transaction_id = value[0]['id'],agent_role = value[0]['role'],defaults={'center':center,'project':proj,'sub_project':value[0]['batch_name'],'work_packet':value[0]['status'],\
            'transaction_id':value[0]['id'],'agent_role':value[0]['role'],'start_time':value[0]['start_time'].split('.')[0],'end_time':value[0]["end_time"].split('.')[0],\
            'emp_name':value[0]['emp_name']})
            if created:
                obj1.save()
        
        return HttpResponse("sucess")

@csrf_exempt
def live_error_data(request):
    if request.method == "POST":
        data_val = json.loads(request.body)
        for key,value in data_val.iteritems():            
            center = Center.objects.get(name=value[0]['center'])
            proj = Project.objects.get(name=value[0]['project'])
            dt = {'date':value[0]['date'],'center':center,'project':proj,'sub_project':value[0]['batch_name'],'work_packet':value[0]['status'],\
            'transaction_id':value[0]['id'],'production_agent':value[0]['prod_agent'],'audit_agent':value[0]['audit_agent'],'prod_start_time':value[0]['start_time'].split('.')[0],\
            'prod_end_time':value[0]["end_time"].split('.')[0],'total_errors':value[0]["count"]}
            obj1, created = live_error_table.objects.update_or_create(transaction_id = value[0]['id'], work_packet = value[0]['status'],defaults={'date':value[0]['date'],'center':center,'project':proj,'sub_project':value[0]['batch_name'],'work_packet':value[0]['status'],\
            'transaction_id':value[0]['id'],'production_agent':value[0]['prod_agent'],'audit_agent':value[0]['audit_agent'],'prod_start_time':value[0]['start_time'].split('.')[0],\
            'prod_end_time':value[0]["end_time"].split('.')[0],'total_errors':value[0]["count"]})
            if created:
                obj1.save()
        return HttpResponse("success")

@csrf_exempt
def live_login_data(request):
    if request.method == "POST":
        data_val = json.loads(request.body)
        for key,value in data_val.iteritems():
            if key == 'login':
                for val in value:
                    center = Center.objects.get(name=val['center'])
                    proj = Project.objects.get(name=val['project'])
                    dt = {'date':val['date'],'center':center,'project':proj,'agent_id':val['id'],'login_time':val['login'].split('.')[0],\
                    'host_name':val['host_name'],'session_key':val['session_key']}
                    obj = live_agent_login_table(**dt)
                    obj.save()
            else:
                for val in value:                    
                    obj = live_agent_login_table.objects.get(session_key=val['session_key'])
                    if obj:
                        obj.logout_time = val['logout'].split('.')[0]
                        obj.save()
        return HttpResponse("success")

@csrf_exempt
def live_break_funct(request):
    if request.method == "POST":
        data_val = json.loads(request.body)
        for key,value in data_val.iteritems():
            if key == "from_time":
                for val in value:
                    center = Center.objects.get(name=val['center'])
                    proj = Project.objects.get(name=val['project'])
                    dt = { 'date':val['date'], 'center':center, 'project':proj, 'from_time':val['from_time'].split('+')[0], 'trans_id':val['id']}
                    
                    obj = live_break_time(**dt)
                    obj.save()
            else:
                for val in value:
                    obj = live_break_time.objects.get(trans_id=val['id'])
                    if obj:
                        obj.to_time = val['to_time'].split('+')[0]
                        obj.save()
        return HttpResponse("success")

