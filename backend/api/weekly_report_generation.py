import datetime
from django.db.models import Sum,Max, Count, F
from django.core import mail
from django.core.mail import send_mail, BadHeaderError
from django.core.mail import EmailMessage
from api.models import *


def weekly_mail_data(user_details, user, user_group):
    
    mail_data = ''
    prj_count = []
    user_data = User.objects.filter(id=user.name_id)
    user_name = user_data[0].first_name
    today = datetime.date.today()
    week_from_date = today - datetime.timedelta(days=today.weekday(),weeks=1)
    week_to_date = week_from_date + datetime.timedelta(days=6)
    from_date = week_from_date
    to_date = week_to_date
    from_d = datetime.datetime.strftime(from_date,"%d  %b  %Y")
    to_d = datetime.datetime.strftime(to_date,"%d  %b  %Y")
    w_dates = str(from_d)+ " to " +str(to_d)
    _data = "Dear %s, <p>Please find below the high level weekly Metrics from %s</p>"\
                    % (user_name, w_dates)   

    if user_group in ["team_lead","customer","NW_manager","C_manager"]:        
        for data in user_details:
            project = data                                          
            result = generate_targets_data(project, user_group, from_date, to_date)
            project_name = Project.objects.get(id=project).name                
            mail_table_data = generate_mail_table_format(result,project,from_date, to_date,user_group)                    
            if mail_table_data != '':
                mail_data = mail_data + '<html></br></html>' + "%s"%(project_name) + mail_table_data
                prj_count.append(project)                       

        if len(prj_count) >= 1:
            dashboard_url = "https://nextpulse.nextwealth.in"
            mail_logos = generate_logos_format(dashboard_url)
            mail_body = _data + mail_data + mail_logos
            to = [user_data[0].email]
            msg = EmailMessage("NextPulse High Level Metrics - Weekly Report", mail_body, 'nextpulse@nextwealth.in', to)
            msg.content_subtype = "html"
            msg.send()
    
    return "success"


def get_target_query(prj_id, from_date, to_date):    
    query, pro_query = {}, {}    
    query.update({'from_date__lte':from_date,'to_date__gte':to_date,'project':prj_id})
    pro_query.update({'from_date__gte':from_date,'to_date__lte':to_date,'project':prj_id})             
    targ_query = Targets.objects.filter(**pro_query)    
    if targ_query:
        targ_query = targ_query
    else:               
        targ_query = Targets.objects.filter(**query)        
    return targ_query


def generate_targets_data(project, user_group, from_date, to_date):    
    common_dict = {}
    if project == 1:
        work_done_query = Worktrack.objects.filter(project=project, date__range=[from_date, to_date])
        work_done = work_done_query.aggregate(prod_sum=Sum('completed'))  
        work_done = work_done['prod_sum']
        worked_dates = work_done_query.values_list('date', flat=True).distinct()
    elif project == 28:
        work_done_query = UploadDataTable.objects.filter(project=project, date__range=[from_date, to_date])
        work_done = work_done_query.aggregate(prod_sum=Sum('upload'))  
        work_done = work_done['prod_sum']                
        worked_dates = work_done_query.values_list('date', flat=True).distinct()
    else:
        work_done_query = RawTable.objects.filter(project=project,date__range=[from_date, to_date])
        work_done = work_done_query.aggregate(Sum('per_day'))    
        work_done = work_done['per_day__sum']        
        worked_dates = work_done_query.values_list('date', flat=True).distinct()    
    if work_done != None:
        work_done = int(work_done)
    else:
        pass        
    target_filter_query = get_target_query(project, from_date, to_date)
    target_query = target_filter_query.values_list('target_type','target_method').distinct()               
    for _type in target_query:
        if (_type[0] == 'FTE Target' or _type[0] == 'Target') and (work_done != None):
            production = get_production_data(project, from_date, to_date, _type[0], work_done, worked_dates)
            production['prod_target_method'] = "SLA"
            common_dict['production'] = production

        elif _type[1] == 'SLA' and 'Accuracy' in _type[0]:
            table_name = Externalerrors
            sla = get_accuracy_data(project, from_date, to_date, _type, table_name)
            sla['sla_target_method'] = _type[1]
            common_dict['sla'] = sla

        elif _type[1] == 'KPI' and 'Accuracy' in _type[0]:
            table_name = Internalerrors
            kpi = get_accuracy_data(project, from_date, to_date, _type, table_name)            
            kpi['kpi_target_method'] = _type[1]
            common_dict['kpi'] = kpi

        # elif (_type[0] == 'Productivity') or (_type[0] == 'Productivity%'):
        #     productivity = get_productivity_data(project, last_date, _type[0])
        #     productivity['productivity_target_method'] = _type[1]
        #     common_dict['productivity'] = productivity

        # elif _type[0] == 'AHT':
        #     aht = get_aht_data(project, last_date)
        #     aht['aht_target_method'] = _type[1]
        #     common_dict['aht'] = aht

        # elif _type[0] == 'TAT':
        #     tat = get_tat_data(project, last_date)
        #     tat['tat_target_method'] = _type[1]
        #     common_dict['tat'] = tat
    
    return common_dict



def get_target_query_format(prj_id, from_date, to_date):    
    query, raw_data = {}, {}
    pro_query, pro_data = {}, {}
    _term = ''
    _type = Targets.objects.filter(project=prj_id, to_date__gte=from_date).values_list('target_type',flat=True).distinct()         
    if 'FTE Target' in _type:
        query.update({'from_date__lte':from_date,'to_date__gte':to_date,'target_type':'FTE Target',\
                        'project':prj_id})
        pro_query.update({'from_date__gte':from_date,'to_date__lte':to_date,'target_type':'FTE Target',\
                        'project':prj_id})
        _type = 'FTE Target'
    elif 'Target' in _type:
        pro_query.update({'from_date__gte':from_date,'to_date__lte':to_date,'target_type':'Target',\
                        'project':prj_id})
        query.update({'from_date__lte':from_date,'to_date__gte':to_date,'target_type':'Target',\
                            'project':prj_id})
        _type = 'Target'                  
    
    targets = Targets.objects.filter(**pro_query).values_list('from_date','to_date').\
                annotate(target=Sum('target_value'))    
    targ_query = Targets.objects.filter(**pro_query)    
    if targets:
        targets = targets
    else:        
        targets = Targets.objects.filter(**query).values_list('from_date','to_date').\
                    annotate(target=Sum('target_value'))
        targ_query = Targets.objects.filter(**query)        
    m_count = targ_query.filter(from_date=F('to_date')).count()
    return targets, targ_query, m_count


def get_production_data(project, from_date, to_date, _type, work_done, worked_dates):
    result = {}   
    if _type == 'FTE Target':
        actual_target = generate_target_calculations(project,from_date, to_date, worked_dates)
    else:
        if project == 28:
            target_query = UploadDataTable.objects.filter(project=project, date__range=[from_date, to_date])
            target = target_query.aggregate(target=Sum('target'))
            actual_target = target['target']            
        else:
            targets, target_query, m_count = get_target_query_format(project, from_date, to_date)            
            target = target_query.aggregate(Sum('target_value'))                
            actual_target = target['target_value__sum']         
            if actual_target != None and m_count == 0:
                actual_target = actual_target * worked_dates.count()
            else:
                actual_target = actual_target    
                
    if actual_target != None:
        actual_target = int(actual_target)    
    else:
        pass
    color = 'black'
    if actual_target > work_done:
        color = 'Red'
    result['production_target'] = actual_target
    result['workdone'] = work_done
    result['prod_color'] = color     
    return result


def generate_target_calculations(project,from_date, to_date, worked_dates):
    query_dict = {}
    targets, target_query, m_count = get_target_query_format(project, from_date, to_date)     
    packet_check = target_query.values('sub_project','work_packet').distinct()    
    if packet_check[0]['sub_project'] != '':
        packet_check = 'sub_project'
    elif packet_check[0]['work_packet'] != '':
        packet_check = 'work_packet'    
    total_target, pack_target, hc_billable = 0, 0, 0
    target_packets = target_query.values_list(packet_check,flat=True).distinct() 
    total_target = 0     
    for packet in target_packets:
        packet_params = {packet_check: packet}
        target_value = target_query.filter(**packet_params).values('from_date','to_date').annotate(t_sum=Sum('target_value'))                                    
        hc_params = {'project': project,'date__range': [from_date,to_date], packet_check: packet}
        hc_value = Headcount.objects.filter(**hc_params).values('date').annotate(head_c=Sum('billable_agents'))                    
        for dates in worked_dates:            
            for trg_val in target_value:
                for hc_val in hc_value:
                    if m_count == 0:
                        if trg_val['from_date'] <= hc_val['date'] and trg_val['to_date'] >= hc_val['date'] and hc_val['date'] == dates:
                            targ_value = trg_val['t_sum'] * hc_val['head_c']
                            total_target += targ_value                                  
                    else:
                        if trg_val['from_date'] == hc_val['date'] and trg_val['from_date'] == dates:
                            targ_value = trg_val['t_sum'] * hc['head_c'] 
                            total_target += targ_value 
                            
    total_target = float("%.2f"%round(total_target,2))
    return total_target     


def get_target_query_type(prj_id, from_date, to_date, acc_type):    
    query, raw_data = {}, {}
    pro_query, pro_data = {}, {}
    _term, tar_type = '', ''
    if acc_type == Internalerrors:
        tar_type = "Internal Accuracy"
    elif acc_type == Externalerrors:
        tar_type = "External Accuracy"
    elif acc_type == "AHT":
        tar_type = "AHT"
    elif acc_type == "TAT":
        tar_type = "TAT"
    
    query.update({'from_date__lte':from_date,'to_date__gte':to_date,'target_type':tar_type,\
                    'project':prj_id})
    pro_query.update({'from_date__gte':from_date,'to_date__lte':to_date,'target_type':tar_type,\
                    'project':prj_id})                  
    
    targets = Targets.objects.filter(**pro_query).values_list('from_date','to_date').\
                annotate(target=Sum('target_value'))    
    targ_query = Targets.objects.filter(**pro_query)    
    if targets:
        targets = targets        
    else:        
        targets = Targets.objects.filter(**query).values_list('from_date','to_date').\
                    annotate(target=Sum('target_value'))
        targ_query = Targets.objects.filter(**query)    
    m_count = targ_query.filter(from_date=F('to_date')).count()    
    return targets, targ_query, m_count



def get_accuracy_data(project, from_date, to_date, _type, table_name):    
    result = {}
    work_done = RawTable.objects.filter(project=project,date__range=[from_date, to_date]).aggregate(Sum('per_day'))    
    work_done = work_done['per_day__sum']    
    error_data = table_name.objects.filter(project=project,date__range=[from_date, to_date]).\
                    aggregate(audited=Sum('audited_errors'), errors = Sum('total_errors'))   
    
    if error_data['audited'] != None and error_data['errors'] != 0  and error_data['errors'] != None:
        if error_data['audited'] != 0: 
            audit_data = error_data['audited']
        else:
            audit_data = work_done
        if error_data['errors'] != None:
            total_errors = error_data['errors']
        else:
            total_errors = 0
        if audit_data:
            accuracy = (float(total_errors)/float(audit_data))*100
            accuracy =  100 - accuracy
            accuracy = float('%.2f' % round(accuracy, 2))
            accuracy = str(accuracy) + " %"
        else:
            accuracy = str(0) + " %"
    else:
        accuracy = 'No data'
    
    targets, target_query, m_count = get_target_query_type(project, from_date, to_date, table_name)        
    target = target_query.aggregate(acc=Sum('target_value'))   
    
    if project == 30:
        m_count = target_query.count()
    if target and m_count >0:
        if project == 30:            
            target = (target['acc']/m_count)
        else:            
            target = (target['acc']/m_count)
    elif target and m_count == 0:
        target = target['acc']
    else:
        target = 'No data'
    color = 'black'
    if target > accuracy:
        color = 'Red'
    result[_type[1]+'_'+'accuracy'] = accuracy
    result[_type[1]+'_'+'target'] = str(target *100) + " %"
    result[_type[1]+'_'+'color'] = color    
    return result


# def get_productivity_data(project,date,_type):
#     result = {}
#     work_done = RawTable.objects.filter(project=project,date=date).aggregate(Sum('per_day'))
#     work_done = work_done['per_day__sum']
#     billable_agents = Headcount.objects.filter(project=project,date=date).aggregate(Sum('billable_agents'))
#     billable_agents = billable_agents['billable_agents__sum']    
#     if billable_agents == None:
#         billable_agents = 0    
    
#     if _type == 'Productivity':
#         target = Targets.objects.filter(project=project,to_date__gte=date,target_type=_type).\
#                     values_list('target_value',flat=True)        
#         if target:
#             target = target[0]
#         else:
#             target = 'No data'
#         if billable_agents:
#             productivity = work_done/billable_agents
#             productivity = round(productivity, 2)
#         else:
#             productivity = 0
        
#     else:
#         target_data = Targets.objects.filter(project=project,to_date__gte=date,target_type=_type)
#         _target_type = Targets.objects.filter(project=project,to_date__gte=date).\
#                         values_list('target_type',flat=True).distinct()
#         target = target_data.values_list('target_value',flat=True)
#         if target:
#             target = target[0]
#         else:
#             target = 'No Data'

#         if 'FTE Target' in _target_type:
#             target_value = Targets.objects.filter(project=project,to_date__gte=date,\
#                             target_type='FTE Target').aggregate(Sum('target_value'))
#             target_packets = Targets.objects.filter(project=project,to_date__gte=date,\
#                             target_type='FTE Target').values_list('')
#             target_value = target_value['target_value__sum']
#             if target_value == None:
#                 target_value = 0
#             final_target = target_value * billable_agents
#             if final_target:
#                 productivity = (work_done/final_target) * 100
#                 productivity = round(productivity, 2)
#             else:
#                 productivity = 0 
#         else:
#             target_value = Targets.objects.filter(project=project,to_date__gte=date,\
#                             target_type='Target').aggregate(Sum('target_value'))
#             target_value = target_value['target_value__sum']
#             _target = target_value
#             if _target:
#                 productivity = (work_done/_target) * 100
#                 productivity = round(productivity, 2)
#             else:
#                 productivity = 0

#     color = 'black'
#     if target > productivity:
#         color = 'Red'
#     result['productivity'] = productivity
#     result['productivity_target'] = target
#     result['productivity_color'] = color

#     return result


def get_aht_data(project,date):
    result = {}
    aht_value = AHTTeam.objects.filter(project=project,date=date).aggregate(Sum('AHT'))
    aht = aht_value['AHT__sum']
    targets, target_query, m_count = get_target_query_type(project, from_date, to_date, 'AHT')    
    target = target_query.aggregate(Sum('target_value'))
    target = target['target_value__sum']
    if aht != None:
        aht = round(aht,2)
    if target != None:
        target = int(target)
    color = 'black'

    if target > aht:
        color = 'Red'
    result['aht_color'] = color
    result['aht_target'] = target
    result['aht'] = aht
    return result


def get_tat_data(project,date):
    result = {}
    targets, target_query, m_count = get_target_query_type(project, from_date, to_date, 'TAT')    
    target = target_query.aggregate(Sum('target_value'))
    target = target['target_value__sum']
    tat_data = TatTable.objects.filter(project=project,date=date).values_list('date').\
        annotate(met=Sum('met_count'), not_met=Sum('not_met_count'))
    if tat_data[0]:
        tat = (float(tat[0])/float(tat[0]+tat[1])) *100
        tat = round(tat, 2)
    else:
        tat = 0
    color = 'black'
    if target > tat:
        color = 'Red'
    result['tat_color'] = color
    result['tat'] = tat
    result['tat_target'] = int(target)
    return result


def get_senior_customer_data(_data):

    result = {}
    for key, value in _data.iteritems():
        for tar_key, tar_value in value.iteritems():
            if tar_value == 'SLA':
                if key == 'production':
                    if _data['production']['production_target'] > _data['production']['workdone']:
                        result[key] = value
                elif key == 'aht':
                    if _data['aht']['aht_target'] > _data['aht']['aht']:
                        result[key] = value
                elif key == 'productivity':
                    if _data['productivity']['productivity_target'] > _data['productivity']['productivity']:
                        result[key] = value
                elif key == 'sla':
                    if _data['sla']['SLA_target'] > _data['sla']['SLA_accuracy']:
                        result[key] = value
                elif key == 'tat':
                    if _data['tat']['tat_target'] > _data['tat']['tat']:
                        result[key] = value
    return result


def get_customer_data(_data):    
    result = {}
    for key, value in _data.iteritems():
        for tar_key, tar_value in value.iteritems():
            if tar_value == 'SLA':
                result[key] = value
    return result


def generate_mail_table_format(final_data,project,from_date,to_date,user_group):

    date = str(from_date)+ "-" +str(to_date)
    if user_group in ["team_lead","NW_manager","C_manager"]:
        mail_body = "<html>\
                        <head>\
                            <style>\
                                table {\
                                    font-family: arial, sans-serif;\
                                    border-collapse: collapse;\
                                    width: 50%;\
                                }\
                                td, th {\
                                    text-align: center;\
                                    padding: 8px;\
                                    color: black;\
                                }\
                                tr:nth-child(even) {\
                                    background-color: #dddddd;\
                                }\
                                img {\
                                    width: 20%;\
                                    height: 25%;\
                                }\
                                span>a>img {\
                                    width: 4%;\
                                    height: 9%;\
                                }\
                                span>a {\
                                    margin-right: 10%;\
                                    color: white !important;\
                                }\
                            </style>\
        </head>\
        <body>\
            <table align='center' border='1'>"

        headers = "<tr>\
                    <th>Name</th>\
                    <th>Target</th>\
                    <th>Actual</th>\
                    <th>KPI/SLA</th>\
                </tr>"        
        body =  "</body>\
                </html>"    
    else:
        mail_body = "<html>\
                        <head>\
                            <style>\
                                table {\
                                    font-family: arial, sans-serif;\
                                    border-collapse: collapse;\
                                    width: 50%;\
                                }\
                                td, th {\
                                    text-align: center;\
                                    padding: 8px;\
                                    color: black;\
                                }\
                                tr:nth-child(even) {\
                                    background-color: #dddddd;\
                                }\
                                img {\
                                    width: 20%;\
                                    height: 25%;\
                                }\
                                span>a>img {\
                                    width: 4%;\
                                    height: 9%;\
                                }\
                                span>a {\
                                    margin-right: 10%;\
                                    color: white !important;\
                                }\
                            </style>\
        </head>\
        <body>\
            <table align='center' border='1'>"

        headers = "<tr>\
                    <th>Name</th>\
                    <th>Target</th>\
                    <th>Actual</th>\
                </tr>"        
        body =  "</body>\
                </html>"

    
    if user_group == 'customer':
        result = get_customer_data(final_data)
    else:
        result = final_data
    _keys = result.keys()
    if user_group in ["team_lead","NW_manager","C_manager"]:
        if (('production' in _keys) and ('aht' in _keys) and ('productivity' in _keys) and ('sla' in _keys)) or \
            (('production' in _keys) and ('sla' in _keys) and ('productivity' in _keys) and ('kpi' in _keys)):
            result_data = get_prod_sla_productivity(result)
            _text = mail_body + headers + result_data 
        elif (('production' in _keys) and ('sla' in _keys) and ('productivity' in _keys)) or (('production' in _keys) and ('sla' in _keys) and ('aht' in _keys))\
            or (('aht' in _keys) and ('sla' in _keys) and ('productivity' in _keys)) or (('production' in _keys) and ('sla' in _keys) and ('kpi' in _keys)):
            result_data = get_prod_sla_productivity(result)
            _text = mail_body + headers + result_data
        elif ((('production' in _keys) and ('aht' in _keys)) or (('production' in _keys) and ('sla' in _keys))\
            or (('productivity' in _keys) and ('sla' in _keys)) or (('production' in _keys) and ('productivity' in _keys))\
                or (('production'in _keys) and ('kpi' in _keys))):
            result_data = get_fields_data(result)
            _text = mail_body + headers + result_data
        elif (('production' in _keys)):
            result_data = get_individual_fields(result)
            _text = mail_body + headers + result_data
        else:
            _text = ''
    else:
        if (('production' in _keys) and ('aht' in _keys) and ('productivity' in _keys) and ('sla' in _keys)) or \
            (('production' in _keys) and ('sla' in _keys) and ('productivity' in _keys) and ('kpi' in _keys)):
            result_data = get_prod_sla_productivity_customer(result)
            _text = mail_body + headers + result_data 
        elif (('production' in _keys) and ('sla' in _keys) and ('productivity' in _keys)) or (('production' in _keys) and ('sla' in _keys) and ('aht' in _keys))\
            or (('aht' in _keys) and ('sla' in _keys) and ('productivity' in _keys)) or (('production' in _keys) and ('sla' in _keys) and ('kpi' in _keys)):
            result_data = get_prod_sla_productivity_customer(result)
            _text = mail_body + headers + result_data
        elif ((('production' in _keys) and ('aht' in _keys)) or (('production' in _keys) and ('sla' in _keys))\
            or (('productivity' in _keys) and ('sla' in _keys)) or (('production' in _keys) and ('productivity' in _keys))\
                or (('production'in _keys) and ('kpi' in _keys))):
            result_data = get_fields_data_customer(result)
            _text = mail_body + headers + result_data
        elif (('production' in _keys)):
            result_data = get_individual_fields_customer(result)
            _text = mail_body + headers + result_data
        else:
            _text = ''

    return _text


def get_prod_sla_productivity(result):

    values = result.keys()
    if ('production' in values) and ('sla' in values) and ('productivity' in values) and ('aht' in values):
        production_data = "<tr>\
            <td>Production</td>\
            <td>%s</td>\
            <td><font color=%s>%s</font></td>\
            <td>SLA</td>\
            </tr>" % (result['production']['production_target'], result['production']['prod_color'], result['production']['workdone'])

        sla_data = "<tr>\
                <td>External Accuracy</td>\
                <td>%s</td>\
                <td><font color=%s>%s</font></td>\
                <td>SLA</td>\
            </tr>" % (result['sla']['SLA_target'], result['sla']['SLA_color'], result['sla']['SLA_accuracy'])

        productivity_data = "<tr>\
                <td>Productivity</td>\
                <td>%s</td>\
                <td><font color=%s>%s</font></td>\
                <td>SLA</td>\
            </tr>" % (result['productivity']['productivity_target'], result['productivity']['productivity_color'], result['productivity']['productivity'])

        aht_data = "<tr>\
                        <td>AHT</td>\
                        <td>%s</td>\
                        <td><font color=%s>%s</font></td>\
                        <td>SLA</td>\
                    </tr></table>" % (result['aht']['aht_target'], result['aht']['aht_color'], result['aht']['aht'])

        _text = production_data + sla_data + productivity_data + aht_data

    elif ('production' in values) and ('sla' in values) and ('productivity' in values) and ('kpi' in values):
        production_data = "<tr>\
            <td>Production</td>\
            <td>%s</td>\
            <td><font color=%s>%s</font></td>\
            <td>SLA</td>\
            </tr>" % (result['production']['production_target'], result['production']['prod_color'], result['production']['workdone'])

        sla_data = "<tr>\
                <td>External Accuracy</td>\
                <td>%s</td>\
                <td><font color=%s>%s</font></td>\
                <td>SLA</td>\
            </tr>" % (result['sla']['SLA_target'], result['sla']['SLA_color'], result['sla']['SLA_accuracy'])

        productivity_data = "<tr>\
                <td>Productivity</td>\
                <td>%s</td>\
                <td><font color=%s>%s</font></td>\
                <td>SLA</td>\
            </tr>" % (result['productivity']['productivity_target'], result['productivity']['productivity_color'], result['productivity']['productivity'])

        kpi_data = "<tr>\
            <td>Internal Accuracy</td>\
            <td>%s</td>\
            <td><font color=%s>%s</font></td>\
            <td>KPI</td>\
            </tr></table>" % (result['kpi']['KPI_target'], result['kpi']['KPI_color'], result['kpi']['KPI_accuracy'])

        _text = production_data + sla_data + productivity_data + kpi_data

    elif ('production' in values) and ('sla' in values) and ('productivity' in values):
        production_data = "<tr>\
            <td>Production</td>\
            <td>%s</td>\
            <td><font color=%s>%s</font></td>\
            <td>SLA</td>\
            </tr>" % (result['production']['production_target'], result['production']['prod_color'], result['production']['workdone'])

        sla_data = "<tr>\
                <td>External Accuracy</td>\
                <td>%s</td>\
                <td><font color=%s>%s</font></td>\
                <td>SLA</td>\
            </tr>" % (result['sla']['SLA_target'], result['sla']['SLA_color'], result['sla']['SLA_accuracy'])

        productivity_data = "<tr>\
                <td>Productivity</td>\
                <td>%s</td>\
                <td><font color=%s>%s</font></td>\
                <td>SLA</td>\
            </tr></table>" % (result['productivity']['productivity_target'], result['productivity']['productivity_color'], result['productivity']['productivity'])
        _text = production_data + sla_data + productivity_data    

    elif ('production' in values) and ('sla' in values) and ('aht' in values):
        production_data = "<tr>\
            <td>Production</td>\
            <td>%s</td>\
            <td><font color=%s>%s</font></td>\
            <td>SLA</td>\
            </tr>" % (result['production']['production_target'], result['production']['prod_color'], result['production']['workdone'])
        sla_data = "<tr>\
                <td>External Accuracy</td>\
                <td>%s</td>\
                <td><font color=%s>%s</font></td>\
                <td>SLA</td>\
            </tr>" % (result['sla']['SLA_target'], result['sla']['SLA_color'], result['sla']['SLA_accuracy'])
        aht_data = "<tr>\
                        <td>AHT</td>\
                        <td>%s</td>\
                        <td><font color=%s>%s</font></td>\
                        <td>SLA</td>\
                    </tr></table>" % (result['aht']['aht_target'], result['aht']['aht_color'], result['aht']['aht'])        
        _text = production_data + sla_data + aht_data

    elif ('production' in values) and ('sla' in values) and ('kpi' in values):
        production_data = "<tr>\
            <td>Production</td>\
            <td>%s</td>\
            <td><font color=%s>%s</font></td>\
            <td>SLA</td>\
            </tr>" % (result['production']['production_target'], result['production']['prod_color'], result['production']['workdone'])
        sla_data = "<tr>\
                <td>External Accuracy</td>\
                <td>%s</td>\
                <td><font color=%s>%s</font></td>\
                <td>SLA</td>\
            </tr>" % (result['sla']['SLA_target'], result['sla']['SLA_color'], result['sla']['SLA_accuracy'])
        aht_data = "<tr>\
                <td>Internal Accuracy</td>\
                <td>%s</td>\
                <td><font color=%s>%s</font></td>\
                <td>KPI</td>\
            </tr></table>" % (result['kpi']['KPI_target'], result['kpi']['KPI_color'], result['kpi']['KPI_accuracy'])
        _text = production_data + sla_data + aht_data


    elif ('productivity' in values) and ('sla' in values) and ('aht' in values):
        productivity_data = "<tr>\
            <td>Productivity</td>\
            <td>%s</td>\
            <td><font color=%s>%s</font></td>\
            <td>SLA</td>\
            </tr>" % (result['productivity']['productivity_target'], result['productivity']['productivity_color'], result['productivity']['productivity'])
        sla_data = "<tr>\
                <td>External Accuracy</td>\
                <td>%s</td>\
                <td><font color=%s>%s</font></td>\
                <td>SLA</td>\
            </tr>" % (result['sla']['SLA_target'], result['sla']['SLA_color'], result['sla']['SLA_accuracy'])
        aht_data = "<tr>\
                        <td>AHT</td>\
                        <td>%s</td>\
                        <td><font color=%s>%s</font></td>\
                        <td>SLA</td>\
                    </tr></table>" % (result['aht']['aht_target'], result['aht']['aht_color'], result['aht']['aht'])        
        _text = productivity_data + sla_data + aht_data
    return _text

def get_prod_sla_productivity_customer(result):

    values = result.keys()
    if ('production' in values) and ('sla' in values) and ('productivity' in values) and ('aht' in values):
        production_data = "<tr>\
            <td>Production</td>\
            <td>%s</td>\
            <td><font color=%s>%s</font></td>\
            </tr>" % (result['production']['production_target'], result['production']['prod_color'], result['production']['workdone'])

        sla_data = "<tr>\
                <td>External Accuracy</td>\
                <td>%s</td>\
                <td><font color=%s>%s</font></td>\
            </tr>" % (result['sla']['SLA_target'], result['sla']['SLA_color'], result['sla']['SLA_accuracy'])

        productivity_data = "<tr>\
                <td>Productivity</td>\
                <td>%s</td>\
                <td><font color=%s>%s</font></td>\
            </tr>" % (result['productivity']['productivity_target'], result['productivity']['productivity_color'], result['productivity']['productivity'])

        aht_data = "<tr>\
                        <td>AHT</td>\
                        <td>%s</td>\
                        <td><font color=%s>%s</font></td>\
                    </tr></table>" % (result['aht']['aht_target'], result['aht']['aht_color'], result['aht']['aht'])

        _text = production_data + sla_data + productivity_data + aht_data

    elif ('production' in values) and ('sla' in values) and ('productivity' in values) and ('kpi' in values):
        production_data = "<tr>\
            <td>Production</td>\
            <td>%s</td>\
            <td><font color=%s>%s</font></td>\
            </tr>" % (result['production']['production_target'], result['production']['prod_color'], result['production']['workdone'])

        sla_data = "<tr>\
                <td>External Accuracy</td>\
                <td>%s</td>\
                <td><font color=%s>%s</font></td>\
            </tr>" % (result['sla']['SLA_target'], result['sla']['SLA_color'], result['sla']['SLA_accuracy'])

        productivity_data = "<tr>\
                <td>Productivity</td>\
                <td>%s</td>\
                <td><font color=%s>%s</font></td>\
            </tr>" % (result['productivity']['productivity_target'], result['productivity']['productivity_color'], result['productivity']['productivity'])

        kpi_data = "<tr>\
            <td>Internal Accuracy</td>\
            <td>%s</td>\
            <td><font color=%s>%s</font></td>\
            </tr></table>" % (result['kpi']['KPI_target'], result['kpi']['KPI_color'], result['kpi']['KPI_accuracy'])

        _text = production_data + sla_data + productivity_data + kpi_data

    elif ('production' in values) and ('sla' in values) and ('productivity' in values):
        production_data = "<tr>\
            <td>Production</td>\
            <td>%s</td>\
            <td><font color=%s>%s</font></td>\
            </tr>" % (result['production']['production_target'], result['production']['prod_color'], result['production']['workdone'])

        sla_data = "<tr>\
                <td>External Accuracy</td>\
                <td>%s</td>\
                <td><font color=%s>%s</font></td>\
            </tr>" % (result['sla']['SLA_target'], result['sla']['SLA_color'], result['sla']['SLA_accuracy'])

        productivity_data = "<tr>\
                <td>Productivity</td>\
                <td>%s</td>\
                <td><font color=%s>%s</font></td>\
            </tr></table>" % (result['productivity']['productivity_target'], result['productivity']['productivity_color'], result['productivity']['productivity'])
        _text = production_data + sla_data + productivity_data    

    elif ('production' in values) and ('sla' in values) and ('aht' in values):
        production_data = "<tr>\
            <td>Production</td>\
            <td>%s</td>\
            <td><font color=%s>%s</font></td>\
            </tr>" % (result['production']['production_target'], result['production']['prod_color'], result['production']['workdone'])
        sla_data = "<tr>\
                <td>External Accuracy</td>\
                <td>%s</td>\
                <td><font color=%s>%s</font></td>\
            </tr>" % (result['sla']['SLA_target'], result['sla']['SLA_color'], result['sla']['SLA_accuracy'])
        aht_data = "<tr>\
                        <td>AHT</td>\
                        <td>%s</td>\
                        <td><font color=%s>%s</font></td>\
                    </tr></table>" % (result['aht']['aht_target'], result['aht']['aht_color'], result['aht']['aht'])        
        _text = production_data + sla_data + aht_data

    elif ('production' in values) and ('sla' in values) and ('kpi' in values):
        production_data = "<tr>\
            <td>Production</td>\
            <td>%s</td>\
            <td><font color=%s>%s</font></td>\
            </tr>" % (result['production']['production_target'], result['production']['prod_color'], result['production']['workdone'])
        sla_data = "<tr>\
                <td>External Accuracy</td>\
                <td>%s</td>\
                <td><font color=%s>%s</font></td>\
            </tr>" % (result['sla']['SLA_target'], result['sla']['SLA_color'], result['sla']['SLA_accuracy'])
        aht_data = "<tr>\
                <td>Internal Accuracy</td>\
                <td>%s</td>\
                <td><font color=%s>%s</font></td>\
            </tr></table>" % (result['kpi']['KPI_target'], result['kpi']['KPI_color'], result['kpi']['KPI_accuracy'])
        _text = production_data + sla_data + aht_data


    elif ('productivity' in values) and ('sla' in values) and ('aht' in values):
        productivity_data = "<tr>\
            <td>Productivity</td>\
            <td>%s</td>\
            <td><font color=%s>%s</font></td>\
            </tr>" % (result['productivity']['productivity_target'], result['productivity']['productivity_color'], result['productivity']['productivity'])
        sla_data = "<tr>\
                <td>External Accuracy</td>\
                <td>%s</td>\
                <td><font color=%s>%s</font></td>\
            </tr>" % (result['sla']['SLA_target'], result['sla']['SLA_color'], result['sla']['SLA_accuracy'])
        aht_data = "<tr>\
                        <td>AHT</td>\
                        <td>%s</td>\
                        <td><font color=%s>%s</font></td>\
                    </tr></table>" % (result['aht']['aht_target'], result['aht']['aht_color'], result['aht']['aht'])        
        _text = productivity_data + sla_data + aht_data
    return _text

def get_fields_data(result):

    values = result.keys()
    
    if ('sla' in values) and ('productivity' in values):
        sla_data = "<tr>\
                    <td>External Accuracy</td>\
                    <td>%s</td>\
                    <td><font color=%s>%s</font></td>\
                    <td>SLA</td>\
                </tr>" % (result['sla']['SLA_target'], result['sla']['SLA_color'], result['sla']['SLA_accuracy'])
        productivity_data = "<tr>\
                    <td>Productivity</td>\
                    <td>%s</td>\
                    <td><font color=%s>%s</font></td>\
                    <td>SLA</td>\
                </tr></table>" % (result['productivity']['productivity_target'], result['productivity']['productivity_color'], result['productivity']['productivity'])
        _text = sla_data + productivity_data

    elif ('production' in values) and ('sla' in values):
        sla_data = "<tr>\
                    <td>External Accuracy</td>\
                    <td>%s</td>\
                    <td><font color=%s>%s</font></td>\
                    <td>SLA</td>\
                </tr></table>" % (result['sla']['SLA_target'], result['sla']['SLA_color'], result['sla']['SLA_accuracy'])
        production_data = "<tr>\
            <td>Production</td>\
            <td>%s</td>\
            <td><font color=%s>%s</font></td>\
            <td>SLA</td>\
            </tr>" % (result['production']['production_target'], result['production']['prod_color'], result['production']['workdone'])
        _text =  production_data + sla_data 

    elif ('sla' in values) and ('aht' in values):
        sla_data = "<tr>\
                    <td>External Accuracy</td>\
                    <td>%s</td>\
                    <td><font color=%s>%s</font></td>\
                    <td>SLA</td>\
                </tr>" % (result['sla']['SLA_target'], result['sla']['SLA_color'], result['sla']['SLA_accuracy'])
        aht_data = "<tr>\
                        <td>AHT</td>\
                        <td>%s</td>\
                        <td><font color=%s>%s</font></td>\
                        <td>SLA</td>\
                </tr></table>" % (result['aht']['aht_target'], result['aht']['aht_color'], result['aht']['aht'])
        _text = sla_data + aht_data

    elif ('production' in values) and ('aht' in values):
        aht_data = "<tr>\
                    <td>AHT</td>\
                    <td>%s</td>\
                    <td><font color=%s>%s</font></td>\
                    <td>SLA</td>\
                </tr></table>" % (result['aht']['aht_target'], result['aht']['aht_color'], result['aht']['aht'])
        production_data = "<tr>\
            <td>Production</td>\
            <td>%s</td>\
            <td><font color=%s>%s</font></td>\
            <td>SLA</td>\
            </tr>" % (result['production']['production_target'], result['production']['prod_color'], result['production']['workdone'])
        _text =  production_data + aht_data

    elif ('production' in values) and ('productivity' in values):
        production_data = "<tr>\
                    <td>Production</td>\
                    <td>%s</td>\
                    <td><font color=%s>%s</font></td>\
                    <td>SLA</td>\
                </tr>" % (result['production']['production_target'], result['production']['prod_color'], result['production']['workdone'])
        productivity_data = "<tr>\
                    <td>Productivity</td>\
                    <td>%s</td>\
                    <td><font color=%s>%s</font></td>\
                    <td>SLA</td>\
                </tr></table>" % (result['productivity']['productivity_target'], result['productivity']['productivity_color'], result['productivity']['productivity'])
        _text = production_data + productivity_data

    elif ('production' in values) and ('kpi' in values):
        kpi_data = "<tr>\
                    <td>Internal Accuracy</td>\
                    <td>%s</td>\
                    <td><font color=%s>%s</font></td>\
                    <td>KPI</td>\
                </tr></table>" % (result['kpi']['KPI_target'], result['kpi']['KPI_color'], result['kpi']['KPI_accuracy'])
        production_data = "<tr>\
            <td>Production</td>\
            <td>%s</td>\
            <td><font color=%s>%s</font></td>\
            <td>SLA</td>\
            </tr>" % (result['production']['production_target'], result['production']['prod_color'], result['production']['workdone'])
        _text =  production_data + kpi_data 
    return _text    

def get_fields_data_customer(result):

    values = result.keys()
    
    if ('sla' in values) and ('productivity' in values):
        sla_data = "<tr>\
                    <td>External Accuracy</td>\
                    <td>%s</td>\
                    <td><font color=%s>%s</font></td>\
                </tr>" % (result['sla']['SLA_target'], result['sla']['SLA_color'], result['sla']['SLA_accuracy'])
        productivity_data = "<tr>\
                    <td>Productivity</td>\
                    <td>%s</td>\
                    <td><font color=%s>%s</font></td>\
                </tr></table>" % (result['productivity']['productivity_target'], result['productivity']['productivity_color'], result['productivity']['productivity'])
        _text = sla_data + productivity_data

    elif ('production' in values) and ('sla' in values):
        sla_data = "<tr>\
                    <td>External Accuracy</td>\
                    <td>%s</td>\
                    <td><font color=%s>%s</font></td>\
                </tr></table>" % (result['sla']['SLA_target'], result['sla']['SLA_color'], result['sla']['SLA_accuracy'])
        production_data = "<tr>\
            <td>Production</td>\
            <td>%s</td>\
            <td><font color=%s>%s</font></td>\
            </tr>" % (result['production']['production_target'], result['production']['prod_color'], result['production']['workdone'])
        _text =  production_data + sla_data 

    elif ('sla' in values) and ('aht' in values):
        sla_data = "<tr>\
                    <td>External Accuracy</td>\
                    <td>%s</td>\
                    <td><font color=%s>%s</font></td>\
                </tr>" % (result['sla']['SLA_target'], result['sla']['SLA_color'], result['sla']['SLA_accuracy'])
        aht_data = "<tr>\
                        <td>AHT</td>\
                        <td>%s</td>\
                        <td><font color=%s>%s</font></td>\
                </tr></table>" % (result['aht']['aht_target'], result['aht']['aht_color'], result['aht']['aht'])
        _text = sla_data + aht_data

    elif ('production' in values) and ('aht' in values):
        aht_data = "<tr>\
                    <td>AHT</td>\
                    <td>%s</td>\
                    <td><font color=%s>%s</font></td>\
                </tr></table>" % (result['aht']['aht_target'], result['aht']['aht_color'], result['aht']['aht'])
        production_data = "<tr>\
            <td>Production</td>\
            <td>%s</td>\
            <td><font color=%s>%s</font></td>\
            </tr>" % (result['production']['production_target'], result['production']['prod_color'], result['production']['workdone'])
        _text =  production_data + aht_data

    elif ('production' in values) and ('productivity' in values):
        production_data = "<tr>\
                    <td>Production</td>\
                    <td>%s</td>\
                    <td><font color=%s>%s</font></td>\
                </tr>" % (result['production']['production_target'], result['production']['prod_color'], result['production']['workdone'])
        productivity_data = "<tr>\
                    <td>Productivity</td>\
                    <td>%s</td>\
                    <td><font color=%s>%s</font></td>\
                </tr></table>" % (result['productivity']['productivity_target'], result['productivity']['productivity_color'], result['productivity']['productivity'])
        _text = production_data + productivity_data

    elif ('production' in values) and ('kpi' in values):
        kpi_data = "<tr>\
                    <td>Internal Accuracy</td>\
                    <td>%s</td>\
                    <td><font color=%s>%s</font></td>\
                </tr></table>" % (result['kpi']['KPI_target'], result['kpi']['KPI_color'], result['kpi']['KPI_accuracy'])
        production_data = "<tr>\
            <td>Production</td>\
            <td>%s</td>\
            <td><font color=%s>%s</font></td>\
            </tr>" % (result['production']['production_target'], result['production']['prod_color'], result['production']['workdone'])
        _text =  production_data + kpi_data 
    return _text

def get_individual_fields(result):
    values = result.keys()

    if ('production' in values):
        production_data = "<tr>\
                            <td>Production</td>\
                            <td>%s</td>\
                            <td><font color=%s>%s</font></td>\
                            <td>SLA</td>\
                            </tr>\
                        </table>" % (result['production']['production_target'], result['production']['prod_color'], result['production']['workdone'])
        result = production_data
    elif ('productivity' in values):
        productivity_data = "<tr>\
                    <td>Productivity</td>\
                    <td>%s</td>\
                    <td><font color=%s>%s</font></td>\
                    <td>SLA</td>\
                </tr>\
                </table>" % (result['productivity']['productivity_target'], result['productivity']['productivity_color'], result['productivity']['productivity'])
        result = productivity_data
    elif ('sla' in values):
        sla_data =  "<tr>\
                    <td>External Accuracy</td>\
                    <td>%s</td>\
                    <td><font color=%s>%s</font></td>\
                    <td>SLA</td>\
                </tr>\
                </table>" % (result['sla']['SLA_target'], result['sla']['SLA_color'], result['sla']['SLA_accuracy'])
        result = sla_data
    elif ('aht' in values):
        aht_data = "<tr>\
                    <td>AHT</td>\
                    <td>%s</td>\
                    <td><font color=%s>%s</font></td>\
                    <td>SLA</td>\
                </tr>\
                </table>" % (result['aht']['aht_target'], result['aht']['aht_color'], result['aht']['aht'])
        result = aht_data
    elif('kpi' in values):
        kpi_data = "<tr>\
                    <td>Internal Accuracy</td>\
                    <td>%s</td>\
                    <td><font color=%s>%s</font></td>\
                    <td>KPI</td>\
                </tr>\
                </table>" % (result['kpi']['KPI_target'], result['kpi']['KPI_color'], result['kpi']['KPI_accuracy'])
        result = kpi_data
    return result

def get_individual_fields_customer(result):
    values = result.keys()

    if ('production' in values):
        production_data = "<tr>\
                            <td>Production</td>\
                            <td>%s</td>\
                            <td><font color=%s>%s</font></td>\
                            </tr>\
                        </table>" % (result['production']['production_target'], result['production']['prod_color'], result['production']['workdone'])
        result = production_data
    elif ('productivity' in values):
        productivity_data = "<tr>\
                    <td>Productivity</td>\
                    <td>%s</td>\
                    <td><font color=%s>%s</font></td>\
                </tr>\
                </table>" % (result['productivity']['productivity_target'], result['productivity']['productivity_color'], result['productivity']['productivity'])
        result = productivity_data
    elif ('sla' in values):
        sla_data =  "<tr>\
                    <td>External Accuracy</td>\
                    <td>%s</td>\
                    <td><font color=%s>%s</font></td>\
                </tr>\
                </table>" % (result['sla']['SLA_target'], result['sla']['SLA_color'], result['sla']['SLA_accuracy'])
        result = sla_data
    elif ('aht' in values):
        aht_data = "<tr>\
                    <td>AHT</td>\
                    <td>%s</td>\
                    <td><font color=%s>%s</font></td>\
                </tr>\
                </table>" % (result['aht']['aht_target'], result['aht']['aht_color'], result['aht']['aht'])
        result = aht_data
    elif('kpi' in values):
        kpi_data = "<tr>\
                    <td>Internal Accuracy</td>\
                    <td>%s</td>\
                    <td><font color=%s>%s</font></td>\
                </tr>\
                </table>" % (result['kpi']['KPI_target'], result['kpi']['KPI_color'], result['kpi']['KPI_accuracy'])
        result = kpi_data
    return result

def generate_logos_format(dashboard_url):

    _text1 = "<html>\
              <body>"
    _text2 = "<p> For further details on metrics and graphs click on NextPulse link     %s"\
            "<br>\
            <p>Thanks and Regards</p>\
            <p>NextPulse Team</p>\
            <p>NextWealth Entrepreneurs Pvt Ltd</p>" % dashboard_url

    logo = "<table class=NormalTable border=0 cellspacing=0 cellpadding=0>\
                <tbody>\
                    <tr>\
                        <td width=450 style=width:337.5px; padding: 0px 0px 0px 0px;>\
                            <div align=center>\
                                <table class=NormalTable border=0 cellspacing=0 cellpadding=0>\
                                    <tbody>\
                                        <tr>\
                                            <td valign=top style=padding: 0px 0px 0px 0px;>\
                                                <p class=MsoNormal>\
                                                    <span>\
                                                        <u></u>\
                                                        <u></u>\
                                                        <u></u>\
                                                    </span>\
                                                </p>\
                                            </td>\
                                            <td>\
                                                <span></span>\
                                            </td>\
                                            <td style=padding:0px 0px 0px 0px;>\
                                                <p class=MsoNoraml>\
                                                    <span>\
                                                        <span style=font-size:1.0pt;>\
                                                            <u></u>\
                                                            <u></u>\
                                                            <u></u>\
                                                        </span>\
                                                    </span>\
                                                </p>\
                                            </td>\
                                            <td>\
                                                <span></span>\
                                            </td>\
                                            <td valign=top style=padding: 0px 0px 0px 0px;>\
                                                <p class=MsoNormal>\
                                                    <span>\
                                                        <u></u>\
                                                        <u></u>\
                                                        <u></u>\
                                                    </span>\
                                                </p>\
                                            </td>\
                                            <td>\
                                                <span></span>\
                                            </td>\
                                        </tr>\
                                        <tr style=height:132.0pt;>\
                                            <td width=130 valign=top style=width:97.5pt;padding:0px 0px 0px 0px;>\
                                                <table class=MsoNormalTable border=0 cellspacing=0 cellpadding=0>\
                                                    <tbody>\
                                                        <tr>\
                                                            <td style=padding:7.5pt 0in 0in 0in;>\
                                                                <p class=MsoNormal>\
                                                                    <span>\
                                                                    </span>\
                                                                    <span style=font-size:10.5pt;font-family:Arial,sans-serif;color:#7f7f7f>\
                                                                    <img width=127 height=81 style=width:1.3229in;height:.8437in src=http://stats.headrun.com/images/nextwealth.png>\
                                                                    <u></u>\
                                                                    <u></u>\
                                                                    </span>\
                                                                </p>\
                                                            </td>\
                                                            <td>\
                                                                <span></span>\
                                                            </td>\
                                                        </tr>\
                                                    </tbody>\
                                                </table>\
                                                <span></span>\
                                            </td>\
                                            <td>\
                                                <span></span>\
                                            </td>\
                                            <td width=10 style=width:7.5pt;padding:0in 0in 0in 0in;height:132.0pt>\
                                                <p class=MsoNormal>\
                                                    <span>\
                                                        <span style=font-size:1.0pt>\
                                                            <u></u>\
                                                            <u></u>\
                                                            <u></u>\
                                                        </span>\
                                                    </span>\
                                                </p>\
                                            </td>\
                                            <td>\
                                                <span></span>\
                                            <td>\
                                            <td width=240 valign=top style=width:2.5in;padding:0in 0in 0in 0in;height:132.0pt>\
                                                <table class=NormalTable border=0 cellspacing=0 cellpadding=0>\
                                                    <tbody>\
                                                        <tr>\
                                                            <td style=padding:7.5pt 0in 0in 0in>\
                                                                <table class=NormalTable border=0 cellspacing=0 cellpadding=0 width=100% style=width:100.0%>\
                                                                    <tbody>\
                                                                        <tr></tr>\
                                                                        <tr>\
                                                                            <td width=7% style=width:7.0%;padding:0in 0in 0in 0in>\
                                                                                <p class=MsoNoraml>\
                                                                                    <span>\
                                                                                        <img width=9 height=18 style=width:.125in;height:.2083in src=http://stats.headrun.com/images/location_new.jpg>\
                                                                                        <u></u>\
                                                                                        <u></u>\
                                                                                    </span>\
                                                                                </p>\
                                                                            </td>\
                                                                            <td>\
                                                                                <span></span>\
                                                                            </td>\
                                                                            <td width=110% style=width:110%;padding:0in 0in 7.5pt 0in>\
                                                                                <p class=MsoNormal>\
                                                                                    <span></span>\
                                                                                    <a href=https://www.google.com/maps?q=728,+6th+B+Cross+Road,+Koramangala,+3rd+Block&entry=gmail&source=g target=_blank>\
                                                                                        <span>\
                                                                                            <span style=font-size:9.0pt;font-family:Arial,sans-serif;> 6th B Cross Road, Koramangala, 3rd Block, Bengaluru - 560034, Karnataka, INDIA\
                                                                                            </span>\
                                                                                        </span>\
                                                                                        <span></span>\
                                                                                    </a>\
                                                                                    <span>\
                                                                                        <span style=font-size:9.0pt;font-family:Arial,sans-serif>\
                                                                                            <u></u>\
                                                                                            <u></u>\
                                                                                        </span>\
                                                                                    </span>\
                                                                                </p>\
                                                                            </td>\
                                                                            <td>\
                                                                                <span></span>\
                                                                            </td>\
                                                                        </tr>\
                                                                        <tr>\
                                                                            <td width=7% style=width:7.0%;padding:0in 0in 0in 0in>\
                                                                                <p class=MsoNoraml>\
                                                                                    <span>\
                                                                                        <img width=9 height=18 style=width:.125in;height:.2083in src=http://stats.headrun.com/images/office_new.jpg>\
                                                                                        <u></u>\
                                                                                        <u></u>\
                                                                                    </span>\
                                                                                </p>\
                                                                            </td>\
                                                                            <td>\
                                                                                <span></span>\
                                                                            </td>\
                                                                            <td width=93% style=width:93.0%;padding:0in 0in 0in 0in;height:15.0pt>\
                                                                                <p class=MsoNormal>\
                                                                                    <span></span>\
                                                                                    <a href=www.nextwealth.in target=_blank>\
                                                                                        <span>\
                                                                                            <span style=font-size:9.0pt;font-family:Arial,sans-serif;>www.nextwealth.in\
                                                                                            </span>\
                                                                                        </span>\
                                                                                        <span></span>\
                                                                                    </a>\
                                                                                    <span>\
                                                                                        <span style=font-size:9.0pt;font-family:Arial,sans-serif>\
                                                                                            <u></u>\
                                                                                            <u></u>\
                                                                                        </span>\
                                                                                    </span>\
                                                                                </p>\
                                                                            </td>\
                                                                            <td>\
                                                                                <span></span>\
                                                                            </td>\
                                                                        </tr>\
                                                                    </tbody>\
                                                                </table>\
                                                                <span></span>\
                                                                <p class=MsoNormal>\
                                                                    <span>\
                                                                        <u></u>\
                                                                        <u></u>\
                                                                    </span>\
                                                                </p>\
                                                            </td>\
                                                            <td>\
                                                                <span></span>\
                                                            </td>\
                                                        </tr>\
                                                    </tbody>\
                                                </table>\
                                                <span></span>\
                                            </td>\
                                            <td>\
                                                <span></span>\
                                            </td>\
                                        </tr>\
                                    </tbody>\
                                </table>\
                            </div>\
                            <span></span>\
                        </td>\
                        <td>\
                            <span></span>\
                        </td>\
                    </tr>\
                    <tr>\
                        <td style=background:#f7f7f7;padding:0in 0in 0in 0in>\
                            <div align=center>\
                                <table class=MsoNormalTable border=0 cellpadding=0>\
                                    <tbody>\
                                        <tr>\
                                            <td style=padding:.75pt .75pt .75pt 7.5pt>\
                                                <p class=MsoNormal>\
                                                    <span></span>\
                                                    <a href=https://www.facebook.com/NextWealth/ target=_blank>\
                                                        <span>\
                                                            <span style=text-decoration:none>\
                                                                <img border=0 width=20 height=27 style=width:.2083in;height:.2812in src=http://stats.headrun.com/images/facebook.png>\
                                                            </span>\
                                                        </span>\
                                                        <span></span>\
                                                    </a>\
                                                    <span>\
                                                        <u></u>\
                                                        <u></u>\
                                                    </span>\
                                                </p>\
                                            </td>\
                                            <td></td>\
                                            <td style=padding:.75pt .75pt .75pt 7.5pt>\
                                                <p class=MsoNormal>\
                                                    <span></span>\
                                                    <a href=https://twitter.com/NextWealth target=_blank>\
                                                        <span>\
                                                            <span style=text-decoration:none>\
                                                                <img border=0 width=20 height=27 style=width:.2083in;height:.2812in src=http://stats.headrun.com/images/twitter.png>\
                                                            </span>\
                                                        </span>\
                                                        <span></span>\
                                                    </a>\
                                                    <span>\
                                                        <u></u>\
                                                        <u></u>\
                                                    </span>\
                                                </p>\
                                            </td>\
                                            <td></td>\
                                            <td style=padding:.75pt .75pt .75pt 7.5pt>\
                                                <p class=MsoNormal>\
                                                    <span></span>\
                                                    <a href=https://www.linkedin.com/company-beta/3512470/?pathWildcard=3512470 target=_blank>\
                                                        <span>\
                                                            <span style=text-decoration:none>\
                                                                <img border=0 width=20 height=27 style=width:.2083in;height:.2812in src=http://stats.headrun.com/images/linkedin.png>\
                                                            </span>\
                                                        </span>\
                                                        <span></span>\
                                                    </a>\
                                                    <span>\
                                                        <u></u>\
                                                        <u></u>\
                                                    </span>\
                                                </p>\
                                            </td>\
                                            <td></td>\
                                        </tr>\
                                    </tbody>\
                                </table>\
                            </div>\
                            <span></span>\
                        </td>\
                        <td>\
                            <span></span>\
                        </td>\
                    </tr>\
                </tbody>\
            </table><br>\
            </body>\
            </html>"

    urls = "<div class=row>\
                <span>\
                    <a href=%s>\
                        <img id=fb_icon, src=http://stats.headrun.com/images/facebook.png\
                        alt=facebook_logo />\
                    </a>\
                </span>\
                <span>\
                    <a href=%s>\
                        <img id=tw_icon, src=http://stats.headrun.com/images/twitter.png\
                        alt=twitter_logo />\
                    </a>\
                </span>\
                <span>\
                    <a href=%s>\
                        <img id=li_icon, src=http://stats.headrun.com/images/linkedin.png\
                        alt=linkedin_logo />\
                    </a>\
                </span>\
            </div>\
            </body>\
            </html>" %("www.facebook.com/NextWealth/", "twitter.com/NextWealth", \
                    "https://www.linkedin.com/company-beta/3512470/?pathWildcard=3512470")
    mail_body = _text1 + _text2 + logo
    return mail_body
