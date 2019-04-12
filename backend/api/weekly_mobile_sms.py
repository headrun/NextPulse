import datetime
import json
import urllib2
import requests
from django.db.models import Sum,Max
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from common.utils import getHttpResponse as json_HttpResponse
from api.models import *
from api.weekly_report_generation import *


def weekly_mobile_notifications(proj_list, user_obj, user_group):   
    if user_group in ['team_lead', 'customer']:      
        week_dates = []
        today = datetime.date.today()
        week_from_date = today - datetime.timedelta(days=today.weekday(),weeks=1)        
        for i in range(7): week_dates.append(week_from_date + datetime.timedelta(days=i))                
        from_date = week_from_date
        to_date = week_dates[-1]  
        sr_fdate = datetime.datetime.strftime(from_date,'%b %d %Y')
        sr_tdate = datetime.datetime.strftime(to_date,'%b %d %Y')
        date = str(sr_fdate)+" to "+str(sr_tdate)
        phone_no = UserProfile.objects.get(user=user_obj.name_id).phone_number                  
        if user_group in ['team_lead']:            
            is_senior  = False
        elif user_group == 'customer':            
            customer_data = Customer.objects.filter(id=user_obj.id).values_list('is_senior', flat=True)
            is_senior = customer_data[0]              
        full_data, data_1 = "", ""
        for project in proj_list:            
            project_name = Project.objects.get(id=project).name            
            values = generate_targets_data(project,user_group,week_dates)                                    
            if values:
                if user_group   == 'customer' and is_senior:
                    push_data   = get_senior_customer_data(values)
                elif user_group == 'customer':
                    push_data   = get_customer_data(values)
                else:
                    push_data   = values                
                _keys  = push_data.keys()                                        
                if (('production' in _keys) and ('aht' in _keys) and ('productivity' in _keys) and ('sla' in _keys)) or\
                    (('production' in _keys) and ('sla' in _keys) and ('productivity' in _keys)) or \
                        (('production' in _keys) and ('sla' in _keys) and ('kpi' in _keys)) or \
                            (('production' in _keys) and ('sla' in _keys) and ('aht' in _keys)) or\
                                (('aht' in _keys) and ('sla' in _keys) and ('productivity' in _keys)):                    
                    metric = get_required_data_for_notification(push_data)
                elif (('production' in _keys) and ('aht' in _keys)) or (('production' in _keys) and ('sla' in _keys)) or\
                    (('productivity' in _keys) and ('sla' in _keys)) or (('production' in _keys) and ('productivity' in _keys))\
                    or (('productivity' in _keys) and ('aht' in _keys) or (('production' in _keys) and ('kpi' in _keys))):
                    metric = get_fields_data_for_push(push_data)
                elif (('production' in _keys)):
                    metric = get_individual_fields_for_push(push_data)
                else:
                    metric = ''                
                if metric != '':
                    data_1 = project_name +" - "+ date+ "\n"    
                    data = data_1 + metric+"\n" 
                    full_data = full_data + data                
                else:
                    pass
            else:
                payload = {}            
        
        if full_data:            
            full_data = full_data +" "+ "FMI.,https://nextpulse.nextwealth.in/"
            url = "http://roundsms.com/api/sendhttp.php?authkey=MGZhZTA4YTQ4ZTd&mobiles=%s&message=%s&sender=NXTWTH&type=2&route=3"%(phone_no, full_data)                                        
            request = requests.post(url)
            msg_obj = json.loads(request._content)            
            url_status = "http://roundsms.in/api/reports.php?authkey=MGZhZTA4YTQ4ZTd&msg_id=%s"%(msg_obj['msg_id'])            
            status = requests.post(url_status)
            sub_obj = json.loads(status._content)            
            payload = {}   
        else:
            payload = {}
    else:
        payload = {}
    return json_HttpResponse(payload)



def weekly_mobile_metric_notifications(proj_list, user_obj):
    phone_no = UserProfile.objects.get(user=user_obj.name_id).phone_number
    user_data = User.objects.get(id=user_obj.name_id).first_name 
    week_dates = []
    today = datetime.date.today()
    week_from_date = today - datetime.timedelta(days=today.weekday(),weeks=1)        
    for i in range(7): week_dates.append(week_from_date + datetime.timedelta(days=i))                    
    from_date = week_from_date
    to_date = week_dates[-1]           
    full_data = ""
    proj = []
    for project in proj_list:
        week_count = RawTable.objects.filter(project=project,date__in=week_dates).count()                
        proj_data = Project.objects.get(id=project).name                
        if week_count > 0:
            proj.append(proj_data)
    
    if len(proj) > 0:
        proj_data = ' , '.join(proj)
        data = "Dear %s,Recent Week's Data has been uploaded for following the project %s, Please find the Details on NextPulse Dashboard."\
                                % (user_data, proj_data)
        full_data = full_data + data
        if full_data:
            full_data = full_data +" "+ "FMI.,https://nextpulse.nextwealth.in/"    
            url = "http://roundsms.com/api/sendhttp.php?authkey=MGZhZTA4YTQ4ZTd&mobiles=%s&message=%s&sender=NXTWTH&type=2&route=3"%(phone_no, full_data)                                        
            request = requests.post(url)                                                                       
            payload = {}   
        else:
            payload = {}
    else:
        payload = {}
    
    return json_HttpResponse(payload)





def get_required_data_for_notification(push_data):

    _keys = push_data.keys()

    if ('production' in _keys) and ('aht' in _keys) and ('productivity' in _keys) and ('sla' in _keys):

        metric_1 = 'Production' + ": " + "Target = " + str(push_data['production']['production_target']) + ",  Actual = " + str(push_data['production']['workdone']) + "\n"
        metric_2 = 'AHT' + ": " + "Target = " + str(push_data['aht']['aht_target']) + ",  Actual = " + str(push_data['aht']['aht']) + "\n"
        metric_3 = 'Productivity' + ": " + "Target = " + str(push_data['productivity']['productivity_target']) + ",  Actual = " + str(push_data['productivity']['productivity']) + "\n"
        metric_4 = 'External Accuracy' + ": " + "Target = " + str(push_data['sla']['SLA_target']) + ",  Actual = " + str(push_data['sla']['SLA_accuracy'])
        metric = metric_1 + metric_2 + metric_3 + metric_4 

    elif (('production' in _keys) and ('sla' in _keys) and ('productivity' in _keys)):

        metric_1 = 'Production' + ": " + "Target = " + str(push_data['production']['production_target']) + ",  Actual = " + str(push_data['production']['workdone']) + "\n"
        metric_2 = 'External Accuracy' + ": " + "Target = " + str(push_data['sla']['SLA_target']) + ",  Actual = " + str(push_data['sla']['SLA_accuracy']) + "\n"
        metric_3 = 'Productivity' + ": " + "Target = " + str(push_data['productivity']['productivity_target']) + ",  Actual = " + str(push_data['productivity']['productivity'])
        metric = metric_1 + metric_2 + metric_3
    
    elif (('production' in _keys) and ('sla' in _keys) and ('kpi' in _keys)):

        metric_1 = 'Production' + ": " + "Target = " + str(push_data['production']['production_target']) + ",  Actual = " + str(push_data['production']['workdone']) + "\n"
        metric_2 = 'External Accuracy' + ": " + "Target = " + str(push_data['sla']['SLA_target']) + ",  Actual = " + str(push_data['sla']['SLA_accuracy']) + "\n"
        metric_3 = 'Internal Accuracy' + ": " + "Target = " + str(push_data['kpi']['KPI_target']) + ",  Actual = " + str(push_data['kpi']['KPI_accuracy'])
        metric = metric_1 + metric_2 + metric_3

    elif (('production' in _keys) and ('sla' in _keys) and ('aht' in _keys)):

        metric_1 = 'Production' + ": " + "Target = " + str(push_data['production']['production_target']) + ",  Actual = " + str(push_data['production']['workdone']) + "\n"
        metric_2 = 'External Accuracy' + ": " + "Target = " + str(push_data['sla']['SLA_target']) + ",  Actual = " + str(push_data['sla']['SLA_accuracy']) + "\n"
        metric_3 = 'AHT' + ": " + "Target = " + str(push_data['aht']['aht_target']) + ",  Actual = " + str(push_data['aht']['aht'])
        metric = metric_1 + metric_2 + metric_3

    elif (('aht' in _keys) and ('sla' in _keys) and ('productivity' in _keys)):

        metric_1 = 'AHT' + ": " + "Target = " + str(push_data['aht']['aht_target']) + ",  Actual = " + str(push_data['aht']['aht']) + "\n"
        metric_2 = 'External Accuracy' + ": " + "Target = " + str(push_data['sla']['SLA_target']) + ",  Actual = " + str(push_data['sla']['SLA_accuracy']) + "\n"
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
        metric_2 = 'External Accuracy' + ": " + "Target = " + str(push_data['sla']['SLA_target']) + ",  Actual = " + str(push_data['sla']['SLA_accuracy'])
        metric = metric_1 + metric_2

    elif ('production' in _keys) and ('kpi' in _keys):
        metric_1 = 'Production' + ": " + "Target = " + str(push_data['production']['production_target']) + ",  Actual = " + str(push_data['production']['workdone']) + "\n"
        metric_2 = 'Internal Accuracy' + ": " + "Target = " + str(push_data['kpi']['KPI_target']) + ",  Actual = " + str(push_data['kpi']['KPI_accuracy'])
        metric = metric_1 + metric_2

    elif ('productivity' in _keys) and ('sla' in _keys):
        metric_1 = 'Productivity' + ": " + "Target = " + str(push_data['productivity']['productivity_target']) + ",  Actual = " + str(push_data['productivity']['productivity']) + "\n"
        metric_2 = 'External Accuracy' + ": " + "Target = " + str(push_data['sla']['SLA_target']) + ",  Actual = " + str(push_data['sla']['SLA_accuracy'])
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
        metric = 'External Accuracy' + ": " + "Target = " + str(push_data['sla']['SLA_target']) + ",  Actual = " + str(push_data['sla']['SLA_accuracy'])
    elif ('productivity' in _keys):
        metric = 'Productivity' + ": " + "Target = " + str(push_data['productivity']['productivity_target']) + ",  Actual = " + str(push_data['productivity']['productivity'])
    elif ('aht' in _keys):
        metric = 'AHT' + ": " + "Target = " + str(push_data['aht']['aht_target']) + ",  Actual = " + str(push_data['aht']['aht'])
    elif ('kpi' in _keys):
        metric = 'Internal Accuracy' + ": " + "Target = " + str(push_data['kpi']['KPI_target']) + ",  Actual = " + str(push_data['kpi']['KPI_accuracy'])
    else:
        metric = ''    

    return metric
