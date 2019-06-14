
import datetime
import datetime as dt
import calendar
from api.models import *
from api.basics import *
from collections import OrderedDict
LOCAL_ZONE = "Asia/Kolkata"
from common.utils import getHttpResponse as json_HttpResponse

def data_dict(variable):
    """It generates common code required for all the widgets"""
    
    main_data_dict = {}
    from_date = datetime.datetime.strptime(variable['from'],'%Y-%m-%d').date()
    to_date = datetime.datetime.strptime(variable['to'],'%Y-%m-%d').date()
    project_name = variable.get('project','')
    if project_name:
        project_name = project_name.split(' -')[0]
    center_name = variable.get('center','')
    if center_name:
        center_name = center_name.split(' -')[0]
    pro_cen_mapping = []
    pro_cen_mapping.append(Project.objects.filter(name=project_name).values_list('id', 'name')[0])
    pro_cen_mapping.append(Center.objects.filter(name=center_name).values_list('id', 'name')[0])
    main_data_dict['pro_cen_mapping'] = pro_cen_mapping
    main_data_dict['work_packet'] = variable.get('work_packet',[])
    main_data_dict['sub_project'] = variable.get('sub_project','')
    main_data_dict['sub_packet'] = variable.get('sub_packet','')
    dwm_dict= {}
    date_list=num_of_days(to_date,from_date)
    type = variable.get('type','')
    if type == '':
        type = 'day'
    is_clicked = variable.get('is_clicked','NA')
    if type == 'day':
        if 'yes' not in is_clicked:
            date_count = len(date_list)
            if date_count > 15:
                type = 'week'
            if date_count > 60:
                type = 'month'
            if date_count == 1 and Project.objects.get(name = project_name).is_hourly_dashboard == True:
                type = 'hour'
            if date_count == 1 and Project.objects.get(name = project_name).is_hourly_dashboard == False:
                type = 'day'
                
        dwm_dict['day']= date_list
        main_data_dict['dwm_dict'] = dwm_dict
    
    if type == 'hour':
        hours_data = []
        data = [(i, dt.time(i).strftime('%I %p')) for i in range(24)]
        for i in data:
            hours_data.append(i[0])
        dwm_dict['hour'] = hours_data
    main_data_dict['dates'] = date_list
    main_data_dict['dwm_dict'] = dwm_dict

    if type == 'week':
        months_dict = {}
        weeks_data = [] 
        days = (to_date - from_date).days
        days = days+1
        for i in xrange(days):
            date = from_date + datetime.timedelta(i)
            weeks_data.append(str(date))
        weeks = [] 
        weekdays = []   
        fro_mon = datetime.datetime.strptime(weeks_data[0],'%Y-%m-%d').date()
        to_mon = datetime.datetime.strptime(weeks_data[-1],'%Y-%m-%d').date()
        no_of_days = to_mon - fro_mon
        num_days = int(re.findall('\d+', str(no_of_days))[0]) + 1
        week_list=[]
        start = 1
        end = 7 - fro_mon.weekday()
        while start <= num_days:
            weeks.append({'start': start, 'end': end})
            sdate = fro_mon + datetime.timedelta(start - 1)
            edate = fro_mon + datetime.timedelta(end - 1)
            weekdays.append({'start': sdate, 'end': edate})
            start = end + 1
            end = end + 7
            if end > num_days:
                end = num_days
        if weekdays[-1]['end'] > to_mon :
            weekdays[-1]['end'] = to_mon
        for w_days in weekdays:
            date_list = num_of_days(w_days['end'],w_days['start'])
            week_list.append(date_list)

    if type == 'week':
        employe_dates = {}
        dwm_dict['week'] = week_list
        for week in week_list:
            if week and  employe_dates.has_key('days'):
                employe_dates['days'] = employe_dates['days']+week

            else:
                employe_dates['days'] = week
        
        main_data_dict['dwm_dict'] = dwm_dict

    if type == 'month':
        months_dict = {}
        month_list = [[]]
        month_names_list = []
        month_count = 0
        days = (to_date - from_date).days
        days = days+1

        for i in xrange(0, days):
            date = from_date + datetime.timedelta(i)
            month = date.strftime("%B")
            month = month+'_'+str(date).split('-')[0]
            if month not in month_names_list:
                month_names_list.append(month)
            if month in months_dict:
                months_dict[month].append(str(date))
                month_list[month_count].append(str(date))
            else:
                months_dict[month] = [str(date)]
                month_count = month_count + 1
                month_list.append([str(date)])
        if month_list[0] == []:
            del month_list[0]
            
    if type == 'month':
        dwm_dict['month'] = {'month_names':month_names_list, 'month_dates':month_list}
        main_data_dict['dwm_dict'] = dwm_dict
    main_data_dict['type'] = type
    return main_data_dict 

def get_packet_details(request):
    """It will generate all the list of packets, projects and sub packets for the project"""

    main_data_dict = data_dict(request.GET)
   
    if main_data_dict['type'] == 'hour':
        dates = main_data_dict['dwm_dict']['day']
    else:
        if len(main_data_dict['dwm_dict']['day']) > 1:
            dates = [main_data_dict['dwm_dict']['day'][:-1][0], main_data_dict['dwm_dict']['day'][-1:][0]]
        else:
            dates = [main_data_dict['dwm_dict']['day'][0]]
    final_dict = {}
    is_hourly = Project.objects.get(id=main_data_dict['pro_cen_mapping'][0][0]).is_hourly_dashboard

    if is_hourly:
        if len(dates) == 1:
            raw_master_set1 = live_transaction_table.objects.filter(project=main_data_dict['pro_cen_mapping'][0][0],\
            center=main_data_dict['pro_cen_mapping'][1][0], date__in=dates).values('sub_project','work_packet','sub_packet').distinct()

            raw_master_set2 = RawTable.objects.filter(project=main_data_dict['pro_cen_mapping'][0][0],\
            center=main_data_dict['pro_cen_mapping'][1][0], date__in=dates).values('sub_project','work_packet','sub_packet').distinct()

            raw_master_set3 = live_error_table.objects.filter(project=main_data_dict['pro_cen_mapping'][0][0],\
            center=main_data_dict['pro_cen_mapping'][1][0], date__in=dates).values('sub_project','work_packet','sub_packet').distinct()

            raw_master_set = raw_master_set1.union(raw_master_set2,raw_master_set3)
        else:
            raw_master_set1 = live_transaction_table.objects.filter(project=main_data_dict['pro_cen_mapping'][0][0],\
            center=main_data_dict['pro_cen_mapping'][1][0], date__range=dates).values('sub_project','work_packet','sub_packet').distinct()
                        
            raw_master_set2 = RawTable.objects.filter(project=main_data_dict['pro_cen_mapping'][0][0],\
            center=main_data_dict['pro_cen_mapping'][1][0], date__range=dates).values('sub_project','work_packet','sub_packet').distinct()
            
            raw_master_set3 = live_error_table.objects.filter(project=main_data_dict['pro_cen_mapping'][0][0],\
            center=main_data_dict['pro_cen_mapping'][1][0], date__range=dates).values('sub_project','work_packet','sub_packet').distinct()
            
            raw_master_set = raw_master_set1.union(raw_master_set2,raw_master_set3)
            
    else:
        raw_master_set = RawTable.objects.filter(\
                         project=main_data_dict['pro_cen_mapping'][0][0], center=main_data_dict['pro_cen_mapping'][1][0], \
                         date__range=dates)    
    if is_hourly:
        sub_pro_level = filter(lambda x: x['sub_project'] not in [None, u''], raw_master_set)
        sub_pro_level = [i['sub_project'] for i in sub_pro_level]
        sub_pro_level = list(dict.fromkeys(sub_pro_level))
        work_pac_level = filter(lambda x: x['work_packet'] not in [None, u''], raw_master_set)
        work_pac_level = [i['work_packet'] for i in work_pac_level]
        work_pac_level = list(dict.fromkeys(work_pac_level))
        sub_pac_level =  filter(lambda x: x['sub_packet'] not in [None, u''], raw_master_set)
        sub_pac_level = [i['sub_packet'] for i in sub_pac_level]
        sub_pac_level = list(dict.fromkeys(sub_pac_level))
    else:
        sub_pro_level = filter(None, raw_master_set.values_list('sub_project',flat=True).distinct())
        work_pac_level = filter(None, raw_master_set.values_list('work_packet',flat=True).distinct())
        sub_pac_level = filter(None, raw_master_set.values_list('sub_packet',flat=True).distinct())
    
    sub_project_level = [i for i in sub_pro_level]
   
    if sub_project_level:
        sub_project_level.append('all')
    else:
        sub_project_level = ''
    
    
    work_packet_level = [j for j in work_pac_level]
    
    if work_packet_level:
        work_packet_level.append('all')
    else:
        if sub_project_level:
            work_packet_level.append('all')
        else:
            work_packet_level = ''
    
    
    sub_packet_level = [k for k in sub_pac_level]
   
    if sub_packet_level:
        sub_packet_level.append('all')
    else:
        if work_packet_level:
            sub_packet_level.append('all')
        else:
            sub_packet_level = ''

    prj_type = request.GET.get('voice_project_type', '')
    if main_data_dict['type'] == 'hour':
        inbound_hourly_master_set = InboundDaily.objects.filter(\
                                    project=main_data_dict['pro_cen_mapping'][0][0], center=main_data_dict['pro_cen_mapping'][1][0],\
                                    date = dates[0])
        outbound_hourly_master_set = OutboundDaily.objects.filter(\
                                     project=main_data_dict['pro_cen_mapping'][0][0], center=main_data_dict['pro_cen_mapping'][1][0],\
                                     date = dates[0])
    else:
        if len(dates) == 1:
            inbound_hourly_master_set = InboundDaily.objects.filter(\
                                        project=main_data_dict['pro_cen_mapping'][0][0], center=main_data_dict['pro_cen_mapping'][1][0],\
                                        date__in = dates)
            outbound_hourly_master_set = OutboundDaily.objects.filter(\
                                        project=main_data_dict['pro_cen_mapping'][0][0], center=main_data_dict['pro_cen_mapping'][1][0],\
                                        date__in = dates)
        else:
            inbound_hourly_master_set = InboundDaily.objects.filter(\
                                        project=main_data_dict['pro_cen_mapping'][0][0], center=main_data_dict['pro_cen_mapping'][1][0],\
                                        date__range = dates)
            outbound_hourly_master_set = OutboundDaily.objects.filter(\
                                        project=main_data_dict['pro_cen_mapping'][0][0], center=main_data_dict['pro_cen_mapping'][1][0],\
                                        date__range = dates)
    if prj_type == 'inbound' or prj_type == '':
        location_names = filter(None, inbound_hourly_master_set.values_list('location',flat=True).distinct())
    elif prj_type == 'outbound':
        location_names = ''
    else:
        location_names = ''
    location_list, skill_list, dispo_list = [], [], []
    for location in location_names:
        location_list.append(location)
    if prj_type == 'inbound' or prj_type == '':
        skill_names = filter(None, inbound_hourly_master_set.values_list('skill',flat=True).distinct())
    elif prj_type == 'outbound':
        skill_names = ''
    else:
        skill_names = ''
    for skill in skill_names:
        skill_list.append(skill)
    if prj_type == 'inbound' or prj_type == '':
        disposition_names = filter(None, inbound_hourly_master_set.values_list('disposition',flat=True).distinct())
    elif prj_type == 'outbound':
        disposition_names = filter(None, outbound_hourly_master_set.values_list('disposition',flat=True).distinct())
    else:
        disposition_names = ''
    is_voice = Project.objects.filter(id=main_data_dict['pro_cen_mapping'][0][0], center=main_data_dict['pro_cen_mapping'][1][0])\
                                   .values_list('is_voice', flat=True).distinct()
    is_hourly = Project.objects.filter(id=main_data_dict['pro_cen_mapping'][0][0], center=main_data_dict['pro_cen_mapping'][1][0])\
                                   .values_list('is_hourly_dashboard', flat=True).distinct()
    if is_voice:
        is_voice = is_voice[0]
    else:
        is_voice = ''
    if is_hourly:
        is_hourly = is_hourly[0]
    else:
        is_hourly = ''
    for dispo in disposition_names:
        dispo_list.append(dispo)
    if location_list:
        location_list.append('All')
        location_list.sort()
    else:
        location_list = ''
    if skill_list:
        skill_list.append('All')
        skill_list.sort()
    else:
        skill_list = ''
    if dispo_list:
        dispo_list.append('All')
        dispo_list.sort()
    else:
        dispo_list = ''
    final_details = {}
    final_details['sub_project'] = 0
    final_details['work_packet'] = 0
    final_details['sub_packet'] = 0
    if sub_pro_level:
        final_details['sub_project'] = 1
        final_details['work_packet'] = 1
    if work_pac_level:        
        final_details['work_packet'] = 1
        final_details['sub_packet'] = 1
    if sub_pac_level:
        final_details['sub_packet'] = 1
    
    prj_id = main_data_dict['pro_cen_mapping'][0][0]
    center = main_data_dict['pro_cen_mapping'][1][0]
    final_dict['sub_project_level'] = sub_project_level
    final_dict['work_packet_level'] = work_packet_level
    final_dict['sub_packet_level'] = sub_packet_level
    final_dict['location'] = location_list
    final_dict['skill'] = skill_list
    final_dict['disposition'] = dispo_list
    final_dict['is_voice'] = is_voice
    final_dict['is_hourly'] = is_hourly
    final_dict['type'] = main_data_dict['type']
    big_dict = {}
    
    if final_details['sub_project']:
        if final_details['work_packet']:
            first = raw_master_set.values_list('sub_project').distinct()
            big_dict = {}
            total = {}
           
            for i in first:
                if len(dates) == 1:
                    if is_hourly:
                        list_val1 = RawTable.objects.filter(project=prj_id, sub_project=i[0], date__in=dates)\
                                                        .values_list('work_packet').distinct()

                        list_val2 = live_transaction_table.objects.filter(project=prj_id,sub_project=i[0], date__in=dates)\
                                                        .values_list('work_packet').distinct()

                        list_val3 = live_error_table.objects.filter(project=prj_id, sub_project=i[0], date__in=dates)\
                                                        .values_list('work_packet').distinct()

                        list_val = list_val1.union(list_val2,list_val3)
                    else:
                        list_val = RawTable.objects.filter(project=prj_id, sub_project=i[0], date__in=dates)\
                                                        .values_list('work_packet').distinct()
                else:
                    if is_hourly:
                        list_val1 = RawTable.objects.filter(project=prj_id, sub_project=i[0], date__range=dates)\
                                                    .values_list('work_packet').distinct()

                        list_val2 = live_transaction_table.objects.filter(project=prj_id,sub_project=i[0], date__range=dates)\
                                                        .values_list('work_packet').distinct()

                        list_val3 = live_error_table.objects.filter(project=prj_id,sub_project=i[0], date__range=dates)\
                                                        .values_list('work_packet').distinct()
                       
                        list_val = list_val1.union(list_val2,list_val3)
                    else:
                        list_val = RawTable.objects.filter(project=prj_id, sub_project=i[0], date__range=dates)\
                                                        .values_list('work_packet').distinct()
                for j in list_val:
                    if j[0] != "":
                        total[j[0]] = []
                        if len(dates) == 1:
                            sub_pac_data = RawTable.objects.filter(project=prj_id, sub_project=i[0], work_packet=j[0], date__in=dates)\
                                                            .values_list('sub_packet').distinct()
                        else:
                            sub_pac_data = RawTable.objects.filter(project=prj_id, sub_project=i[0], work_packet=j[0], date__range=dates)\
                                                            .values_list('sub_packet').distinct()
                        for l in sub_pac_data:
                            if l[0] != "":
                                total[j[0]].append(l[0])
                big_dict[i[0]] = total
                total = {}
    elif final_details['work_packet']:
        if final_details['sub_packet']:
            if is_hourly:
                sub_pro_level = filter(lambda x: x['work_packet'] not in [None, u''], raw_master_set)
                sub_pro_level = [i['work_packet'] for i in sub_pro_level]
                first = list(dict.fromkeys(sub_pro_level))
            else:
                first = raw_master_set.values_list('work_packet').distinct()
            big_dict = {}
            total = {}
            for i in first:
               
                if is_hourly:
                    if len(dates) == 1:
                        list_val1 = live_transaction_table.objects.filter(project=prj_id, work_packet=i, date__in=dates).\
                                                        values_list('sub_packet').distinct()
                        list_val2 = RawTable.objects.filter(project=prj_id, work_packet=i, date__in=dates).\
                                                        values_list('sub_packet').distinct()
                        list_val3 = live_error_table.objects.filter(project=prj_id, work_packet=i, date__in=dates).\
                                                        values_list('sub_packet').distinct()
                        list_val = list(list_val1.union(list_val2,list_val3))
                    else:
                        list_val1 = live_transaction_table.objects.filter(project=prj_id, work_packet=i, date__range=dates).\
                                                       values_list('sub_packet').distinct()
                        list_val2 = RawTable.objects.filter(project=prj_id, work_packet=i, date__range=dates).\
                                                       values_list('sub_packet').distinct()
                        list_val3 = live_error_table.objects.filter(project=prj_id, work_packet=i, date__range=dates).\
                                                        values_list('sub_packet').distinct()
                        list_val = list(list_val1.union(list_val2,list_val3))
                    
                else:
                    if len(dates) == 1:
                        list_val = RawTable.objects.filter(project=prj_id, work_packet=i[0], date__in=dates).\
                                                        values_list('sub_packet').distinct()
                    else:
                        list_val = RawTable.objects.filter(project=prj_id, work_packet=i[0], date__range=dates).\
                                                        values_list('sub_packet').distinct()
                
                for j in list_val:
                    if is_hourly:
                        total[j['sub_packet']] = []
                        big_dict[i] = total
                    else:  
                        total[j[0]] = []  
                        big_dict[i[0]] = total
                total = {}
        else:
            big_dict = {}
            work_pac_level = raw_master_set.values_list('work_packet').distinct()
            for i in work_pac_level:
                big_dict[i[0]] = {}
   
    final_dict['level'] = [1, 2]
    final_dict['fin'] = final_details
    final_dict['drop_value'] = big_dict
    return json_HttpResponse(final_dict)

def utc_to_local(utc_dt):
    """convert utc time to local time """
    localtime = utc_dt + datetime.timedelta(hours = 5, minutes = 30)
    return localtime

