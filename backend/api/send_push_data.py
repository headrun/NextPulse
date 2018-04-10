
import datetime

from django.db.models import Sum,Max
from api.generate_accuracy_values import generate_internal_and_external_values 
from api.models import *
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from common.utils import getHttpResponse as json_HttpResponse

import json
import urllib2

def generate_data_required_for_push(project):
    
    result = {}  
  
    prj_name = Project.objects.filter(id=project).values_list('name',flat=True).distinct()
    last_updated_date = RawTable.objects.filter(project=project).aggregate(Max('date'))
    date = str(last_updated_date['date__max'])
    raw_data = RawTable.objects.filter(project=project, date=date).aggregate(Sum('per_day'))
    raw_value = raw_data['per_day__sum']
    if raw_value == None:
        raw_value = 0
    raw_target_data = Targets.objects.filter(project=project,from_date__lte=date,to_date__gte=date)
    raw_target_value = raw_target_data.filter(target_type='production').aggregate(Sum('target_value'))
    target_type = 'Internal accuracy'
    table_name = Internalerrors
    internal_data = generate_internal_and_external_values(\
                    project, table_name, date, raw_value, target_type)
    target_type = 'External accuracy'
    table_name = Externalerrors
    external_data = generate_internal_and_external_values(\
                    project, table_name, date, raw_value, target_type)
    raw_target = raw_target_value['target_value__sum']
    int_acc = internal_data['accuracy']
    int_target = internal_data['target']
    ext_acc = external_data['accuracy']
    ext_target = external_data['target']

    if (int_acc == 'No data' and ext_acc == 'No data') or (int_acc > int_target and ext_acc > ext_target):
        result['prod_target'] = raw_target
        result['prod_actual'] = raw_value
    elif (int_acc < int_target) and (ext_acc < ext_target):
        result['int_acc'] = int_acc
        result['int_target'] = int_target
        result['ext_acc'] = ext_acc
        result['ext_target'] = ext_target
    elif (int_acc < int_target):
        result['int_acc'] = int_acc
        result['int_target'] = int_target
    elif (ext_acc < ext_target):
        result['ext_acc'] = ext_acc
        result['ext_target'] = ext_target
    else:
        result['prod_actual'] = raw_value
        result['prod_target'] = raw_target
    result.update({'project': prj_name[0], 'date': str(datetime.datetime.now().date())})
    return result    


def get_user_id(request):
    
    player_id = request.POST.get('userid', '')
    user = request.user.id
    user_group = request.user.groups.values_list('name', flat=True)[0]
    if user_group in ['team_lead', 'customer']:
        if user_group == 'team_lead':
            table_name = TeamLead       
        elif user_group == 'customer':
            table_name = Customer 
        project = table_name.objects.filter(name = user).values_list('project',flat=True)
        project = project[0]
        check_data = OneSignal.objects.filter(user_id = user).values_list('device_id', flat=True)

        if check_data:
            user = user
            device_id = player_id
        else:
            details = OneSignal(user_id = user, device_id = player_id)
            details.save()
            device_id = OneSignal.objects.filter(user_id = user).values_list('device_id', flat=True)
        values = generate_data_required_for_push(project)
    return values, device_id


def send_push_notification(request):

    user_group = request.user.groups.values_list('name', flat=True)[0]
    if user_group in ['team_lead', 'customer']:
        values, device_id = get_user_id(request)
        data_1 = values['project'] + "\n" + values['date'] + "\n"
        if ('prod_actual' in values) and ('int_acc' not in values) and ('ext_acc' not in values):
            metric = 'Production' + ": " + "Target = " + str(values['prod_target']) + ",  Actual = " + str(values['prod_actual'])
        elif 'int_acc' and 'ext_acc' in values:
            metric_1 = 'Internal Accuracy' + ": " + "Target = " + str(values['int_target']) + ",  Actual = " + str(values['int_acc']) + "\n"
            metric_2 = 'External Accuracy' + ": " + "Target = " + str(values['ext_target']) + ",  Actual = " + str(values['ext_acc'])
            metric = metric_1 + metric_2
        elif 'int_acc' in values:
            metric = 'Internal Accuracy' + ": " + "Target = " + str(values['int_target']) + "  Actual = " + str(values['int_acc'])
        elif 'ext_acc' in values:
            metric = 'External Accuracy' + ": " + "Target = " + str(values['ext_target']) + "  Actual = " + str(values['ext_acc'])
        data = data_1 + metric
        header = {"Content-Type": "application/json; charset=utf-8",
                  "Authorization": "Basic MWNhMjliMjAtNzAxMy00N2Y4LWIxYTUtYzdjNjQzMDkzOTZk"}

        payload = {"app_id": "d0d6000e-27ee-459b-be52-d65ed4b3d025",
                   "include_player_ids": [device_id],
                   #"included_segments": ["All"],
                   "contents": {"en": data}}
            
        url = "https://onesignal.com/api/v1/notifications"
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(url, data=json.dumps(payload))
        request.add_header("Content-Type", "application/json; charset=utf-8") #Header, Value
        request.add_header("Authorization", "Basic MWNhMjliMjAtNzAxMy00N2Y4LWIxYTUtYzdjNjQzMDkzOTZk")                                        
        print opener.open(request)
    else:
        payload = {}
    return json_HttpResponse(payload)
