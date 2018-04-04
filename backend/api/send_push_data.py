
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
  
    #project = project.id
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
    #result.update({'internal_target': internal_data['target'], 'internal_actual': internal_data['accuracy']})
    target_type = 'External accuracy'
    table_name = Externalerrors
    external_data = generate_internal_and_external_values(\
                    project, table_name, date, raw_value, target_type)
    if internal_data['accuracy'] == 'No data' and external_data['accuracy'] == 'No data':
	result.update({'Production details':'You Achieved this much Production ' + str(raw_value) + ' for the given Target ' + str(raw_target_value['target_value__sum'])})
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
    #print values, device_id
    return values, device_id


def send_push_notification(request):

    values, device_id = get_user_id(request)
    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Basic MWNhMjliMjAtNzAxMy00N2Y4LWIxYTUtYzdjNjQzMDkzOTZk"}

    payload = {"app_id": "d0d6000e-27ee-459b-be52-d65ed4b3d025",
               "include_player_ids": [device_id],
               #"included_segments": ["All"],
               "contents": {"en": values['Production details']}}
        
    url = "https://onesignal.com/api/v1/notifications"
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request(url, data=json.dumps(payload))
    request.add_header("Content-Type", "application/json; charset=utf-8") #Header, Value
    request.add_header("Authorization", "Basic MWNhMjliMjAtNzAxMy00N2Y4LWIxYTUtYzdjNjQzMDkzOTZk")                                        
    print opener.open(request)
    return json_HttpResponse(payload)
