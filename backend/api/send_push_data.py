
import datetime
import json
import urllib2

from django.db.models import Sum,Max
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from common.utils import getHttpResponse as json_HttpResponse

from api.models import *
from api.generate_accuracy_values import *

def send_push_notification(request):
    
    date = str(datetime.datetime.now().date())
    user_group = request.user.groups.values_list('name', flat=True)[0]
    if user_group in ['team_lead', 'customer']:
        player_id = request.POST.get('userid', '')
        user = request.user.id
        user_group = request.user.groups.values_list('name', flat=True)[0]
        if user_group == 'team_lead':
            table_name = TeamLead
            is_senior = True       
        elif user_group == 'customer':
            table_name = Customer
            customer_data = Customer.objects.filter(name=user).values_list('is_senior','is_enable_push_email')
            is_senior = customer_data[0][0]
            is_send_push = customer_data[0][1] 
        projects = table_name.objects.filter(name = user).values_list('project',flat=True)
        
        for project in projects:
            check_data = OneSignal.objects.filter(user_id=user).values_list('device_id', flat=True)
            project_data = Project.objects.filter(id=project).values_list('name','is_enable_push')
            is_send_mail = project_data[0][1]
            project_name = project_data[0][0]
            if is_send_mail:
                if check_data:
                    user = user
                    device_id = player_id
                else:
                    details = OneSignal(user_id = user, device_id = player_id)
                    details.save()
                    device_id = OneSignal.objects.filter(user_id = user).values_list('device_id', flat=True)
                values = generate_targets_data(project,user_group,is_senior)
                
                if user_group == 'customer' and is_senior:
                    push_data = get_senior_customer_data(values)
                elif user_group == 'customer':
                    push_data = get_customer_data(values)
                else:
                    push_data = values
                _keys = push_data.keys()
                data_1 = project_name + "\n" + date+ "\n"
                if (('production' in _keys) and ('aht' in _keys) and ('productivity' in _keys) and ('sla' in _keys)) or\
                    (('production' in _keys) and ('sla' in _keys) and ('productivity' in _keys)) or \
                    (('production' in _keys) and ('sla' in _keys) and ('aht' in _keys)) or (('aht' in _keys) and ('sla' in _keys) and ('productivity' in _keys)):
                    
                    metric = get_required_data_for_notification(push_data)
                elif (('production' in _keys) and ('aht' in _keys)) or (('production' in _keys) and ('sla' in _keys)) or\
                     (('productivity' in _keys) and ('sla' in _keys)) or (('production' in _keys) and ('productivity' in _keys))\
                     or (('productivity' in _keys) and ('aht' in _keys)):
                    metric = get_fields_data_for_push(push_data)
                elif (('production' in _keys) or ('sla' in _keys) or ('productivity' in _keys) \
                    or ('aht' in _keys) or ('kpi' in _keys)):
                    metric = get_individual_fields_for_push(push_data)
                
                data = data_1 + metric
                if metric:
                    header = {"Content-Type": "application/json; charset=utf-8",
                              "Authorization": "Basic MWNhMjliMjAtNzAxMy00N2Y4LWIxYTUtYzdjNjQzMDkzOTZk"}

                    payload = {"app_id": "d0d6000e-27ee-459b-be52-d65ed4b3d025",
                               "include_player_ids": [device_id],
                               "contents": {"en": data},
                               "web_push_topic": project_name}
                        
                    url = "https://onesignal.com/api/v1/notifications"
                    opener = urllib2.build_opener(urllib2.HTTPHandler)
                    request = urllib2.Request(url, data=json.dumps(payload))
                    request.add_header("Content-Type", "application/json; charset=utf-8") #Header, Value
                    request.add_header("Authorization", "Basic MWNhMjliMjAtNzAxMy00N2Y4LWIxYTUtYzdjNjQzMDkzOTZk")                                                                               
                    
    else:
        payload = {}
    return json_HttpResponse(payload)


def get_required_data_for_notification(push_data):

    _keys = push_data.keys()

    if ('production' in _keys) and ('aht' in _keys) and ('productivity' in _keys) and ('sla' in _keys):

        metric_1 = 'Production' + ": " + "Target = " + str(push_data['production']['production_target']) + ",  Actual = " + str(push_data['production']['workdone']) + "\n"
        metric_2 = 'AHT' + ": " + "Target = " + str(push_data['aht']['aht_target']) + ",  Actual = " + str(push_data['aht']['aht']) + "\n"
        metric_3 = 'Productivity' + ": " + "Target = " + str(push_data['productivity']['productivity_target']) + ",  Actual = " + str(push_data['productivity']['productivity']) + "\n"
        metric_4 = 'SLA' + ": " + "Target = " + str(push_data['sla']['SLA_target']) + ",  Actual = " + str(push_data['sla']['SLA_accuracy'])
        metric = metric_1 + metric_2 + metric_3 + metric_4 

    elif (('production' in _keys) and ('sla' in _keys) and ('productivity' in _keys)):

        metric_1 = 'Production' + ": " + "Target = " + str(push_data['production']['production_target']) + ",  Actual = " + str(push_data['production']['workdone']) + "\n"
        metric_2 = 'SLA' + ": " + "Target = " + str(push_data['sla']['SLA_target']) + ",  Actual = " + str(push_data['sla']['SLA_accuracy']) + "\n"
        metric_3 = 'Productivity' + ": " + "Target = " + str(push_data['productivity']['productivity_target']) + ",  Actual = " + str(push_data['productivity']['productivity'])
        metric = metric_1 + metric_2 + metric_3

    elif (('production' in _keys) and ('sla' in _keys) and ('aht' in _keys)):

        metric_1 = 'Production' + ": " + "Target = " + str(push_data['production']['production_target']) + ",  Actual = " + str(push_data['production']['workdone']) + "\n"
        metric_2 = 'SLA' + ": " + "Target = " + str(push_data['sla']['SLA_target']) + ",  Actual = " + str(push_data['sla']['SLA_accuracy']) + "\n"
        metric_3 = 'AHT' + ": " + "Target = " + str(push_data['aht']['aht_target']) + ",  Actual = " + str(push_data['aht']['aht'])
        metric = metric_1 + metric_2 + metric_3

    elif (('aht' in _keys) and ('sla' in _keys) and ('productivity' in _keys)):

        metric_1 = 'AHT' + ": " + "Target = " + str(push_data['aht']['aht_target']) + ",  Actual = " + str(push_data['aht']['aht']) + "\n"
        metric_2 = 'SLA' + ": " + "Target = " + str(push_data['sla']['SLA_target']) + ",  Actual = " + str(push_data['sla']['SLA_accuracy']) + "\n"
        metric_3 = 'Productivity' + ": " + "Target = " + str(push_data['productivity']['productivity_target']) + ",  Actual = " + str(push_data['productivity']['productivity'])
        metric = metric_1 + metric_2 + metric_3

    else:
        metric = ''
    return metric

def get_fields_data_for_push(push_data):

    _keys = push_data.keys()

    if ('production' in _keys) and ('aht' in _keys):
        metric_1 = 'AHT' + ": " + "Target = " + str(push_data['aht']['aht_target']) + ",  Actual = " + str(push_data['aht']['aht']) + "\n"
        metric_2 = 'Production' + ": " + "Target = " + str(push_data['production']['production_target']) + ",  Actual = " + str(push_data['production']['workdone'])
        metric = metric_1 + metric_2

    elif ('production' in _keys) and ('sla' in _keys):
        metric_1 = 'Production' + ": " + "Target = " + str(push_data['production']['production_target']) + ",  Actual = " + str(push_data['production']['workdone']) + "\n"
        metric_2 = 'SLA' + ": " + "Target = " + str(push_data['sla']['SLA_target']) + ",  Actual = " + str(push_data['sla']['SLA_accuracy'])
        metric = metric_1 + metric_2

    elif ('productivity' in _keys) and ('sla' in _keys):
        metric_1 = 'Productivity' + ": " + "Target = " + str(push_data['productivity']['productivity_target']) + ",  Actual = " + str(push_data['productivity']['productivity']) + "\n"
        metric_2 = 'SLA' + ": " + "Target = " + str(push_data['sla']['SLA_target']) + ",  Actual = " + str(push_data['sla']['SLA_accuracy'])
        metric = metric_1 + metric_2

    elif ('production' in _keys) and ('productivity' in _keys):
        metric_1 = 'Production' + ": " + "Target = " + str(push_data['production']['production_target']) + ",  Actual = " + str(push_data['production']['workdone']) + "\n"
        metric_2 = 'Productivity' + ": " + "Target = " + str(push_data['productivity']['productivity_target']) + ",  Actual = " + str(push_data['productivity']['productivity'])
        metric = metric_1 + metric_2

    elif ('productivity' in _keys) and ('aht' in _keys):
        metric_1 = 'AHT' + ": " + "Target = " + str(push_data['aht']['aht_target']) + ",  Actual = " + str(push_data['aht']['aht'])  + "\n"
        metric_2 = 'Productivity' + ": " + "Target = " + str(push_data['productivity']['productivity_target']) + ",  Actual = " + str(push_data['productivity']['productivity'])
        metric = metric_1 + metric_2

    else:
        metric = ''

    return metric

def get_individual_fields_for_push(push_data):

    _keys = push_data.keys()

    if ('production' in _keys):
        metric = 'Production' + ": " + "Target = " + str(push_data['production']['production_target']) + ",  Actual = " + str(push_data['production']['workdone'])
    elif ('sla' in _keys):
        metric = 'SLA' + ": " + "Target = " + str(push_data['sla']['SLA_target']) + ",  Actual = " + str(push_data['sla']['SLA_accuracy'])
    elif ('productivity' in _keys):
        metric = 'Productivity' + ": " + "Target = " + str(push_data['productivity']['productivity_target']) + ",  Actual = " + str(push_data['productivity']['productivity'])
    elif ('aht' in _keys):
        metric = 'AHT' + ": " + "Target = " + str(push_data['aht']['aht_target']) + ",  Actual = " + str(push_data['aht']['aht'])
    elif ('kpi' in _keys):
        metric = 'Internal Accuracy' + ": " + "Target = " + str(push_data['kpi']['KPI_target']) + ",  Actual = " + str(push_data['kpi']['KPI_accuracy'])
    else:
        metric = ''    

    return metric
