
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
            if date_count == 1:
                type = 'hour'
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
        employe_dates = {}
        new_month_dict = {}
        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July','August', 'September', 'October', 'November', 'December']
        k = OrderedDict(sorted(months_dict.items(), key=lambda x: months.index(x[0])))
        for month_na in tuple(k):
            new_month_dict[month_na] = {}
            if employe_dates.has_key('days'):
                employe_dates['days'] = employe_dates['days']+months_dict[month_na]
            else:
                employe_dates['days']= months_dict[month_na]
        dwm_dict['month'] = {'month_names':month_names_list, 'month_dates':month_list}
        main_data_dict['dwm_dict'] = dwm_dict
    main_data_dict['type'] = type
    return main_data_dict 

def get_packet_details(request):
    """It will generate all the list of packets, projects and sub packets for the project"""
    main_data_dict = data_dict(request.GET)
    dates = [main_data_dict['dwm_dict']['day'][:-1][0], main_data_dict['dwm_dict']['day'][-1:][0]]
    final_dict = {}
    raw_master_set = RawTable.objects.filter(project=main_data_dict['pro_cen_mapping'][0][0], center=main_data_dict['pro_cen_mapping'][1][0], 
                                             date__range=dates)
    sub_pro_level = filter(None, raw_master_set.values_list('sub_project',flat=True).distinct())
    sub_project_level = [i for i in sub_pro_level]
    if sub_project_level:
        sub_project_level.append('all')
    else:
        sub_project_level = ''
    work_pac_level = filter(None, raw_master_set.values_list('work_packet',flat=True).distinct())
    work_packet_level = [j for j in work_pac_level]
    if work_packet_level:
        work_packet_level.append('all')
    else:
        work_packet_level = ''
    sub_pac_level = filter(None, raw_master_set.values_list('sub_packet',flat=True).distinct())
    sub_packet_level = [k for k in sub_pac_level]
    if sub_packet_level:
        sub_packet_level.append('all')
    else:
        sub_packet_level = ''
    prj_type = request.GET['voice_project_type']
    inbound_hourly_master_set = InboundHourlyCall.objects.filter(project=main_data_dict['pro_cen_mapping'][0][0], center=main_data_dict['pro_cen_mapping'][1][0], date__range = dates)
    outbound_hourly_master_set = OutboundHourlyCall.objects.filter(project=main_data_dict['pro_cen_mapping'][0][0], center=main_data_dict['pro_cen_mapping'][1][0], date__range = dates)
    if prj_type == 'inbound':
        location_names = filter(None, inbound_hourly_master_set.values_list('location',flat=True).distinct())
    elif prj_type == 'outbound':
        location_names = ''
    else:
        location_names = ''
    location_list, skill_list, dispo_list = [], [], []
    for location in location_names:
        if '->' not in location:
            location_list.append(location)
    if prj_type == 'inbound':
        skill_names = filter(None, inbound_hourly_master_set.values_list('skill',flat=True).distinct())
    elif prj_type == 'outbound':
        skill_names = ''
    else:
        skill_names = ''
    for skill in skill_names:
        if '->' not in skill:
            skill_list.append(skill)
    if prj_type == 'inbound':
        disposition_names = filter(None, inbound_hourly_master_set.values_list('disposition',flat=True).distinct())
    elif prj_type == 'outbound':
        disposition_names = filter(None, outbound_hourly_master_set.values_list('disposition',flat=True).distinct())
    else:
        disposition_names = ''
    is_voice = Project.objects.filter(id=main_data_dict['pro_cen_mapping'][0][0], center=main_data_dict['pro_cen_mapping'][1][0]).values_list('is_voice', flat=True).distinct()[0]
    for dispo in disposition_names:
        if '->' not in dispo:
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
    if work_pac_level:
        final_details['work_packet'] = 1
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
    big_dict = {}
    if final_details['sub_project']:
        if final_details['work_packet']:
            first = raw_master_set.values_list('sub_project').distinct()
            big_dict = {}
            total = {}
            for i in first:
                list_val = RawTable.objects.filter(project=prj_id, sub_project=i[0], date__range=dates).values_list('work_packet').distinct()
                for j in list_val:
                    total[j[0]] = []
                    sub_pac_data = RawTable.objects.filter(project=prj_id, sub_project=i[0], work_packet=j[0], date__range=dates).values_list('sub_packet').distinct()
                    for l in sub_pac_data:
                        total[j[0]].append(l[0])
                big_dict[i[0]] = total
                total = {}
    elif final_details['work_packet']:
        if final_details['sub_packet']:
            first = raw_master_set.values_list('work_packet').distinct()
            big_dict = {}
            total = {}
            for i in first:
                list_val = RawTable.objects.filter(project=prj_id, work_packet=i[0], date__range=dates).values_list('sub_packet').distinct()
                for j in list_val:
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
    """
    import time
    now_timestamp = time.time()
    offset = datetime.datetime.fromtimestamp(now_timestamp) - datetime.datetime.utcfromtimestamp(now_timestamp)
    return utc_dt + offset
    """
    localtime = utc_dt + datetime.timedelta(hours = 5, minutes = 30)
    return localtime

"""    
def local_to_utc(local_date):
    "" convert local time to UTC ""
    local = pytz.timezone(LOCAL_ZONE)
    local_dt = local.localize(local_date, is_dst=None)
    return local_dt.astimezone(pytz.utc)
"""
