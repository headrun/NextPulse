
import datetime
from api.models import *
from api.query_generations import *
from api.basics import *
from api.utils import *
from api.graph_settings import *
from api.per_day_calc import *
from django.db.models import Max
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from collections import OrderedDict
from common.utils import getHttpResponse as json_HttpResponse


def static_production_data(request):

    result = {}
    project = request.GET['project']
    center = request.GET['center'].split('-')[0]
    pro_cen_mapping = []
    pro_cen_mapping.append(Project.objects.filter(name=project).values_list('id', 'name')[0])
    pro_cen_mapping.append(Center.objects.filter(name=center).values_list('id', 'name')[0])

    project_id = pro_cen_mapping[0][0]
    center_id = pro_cen_mapping[1][0]

    work_packet = []
    sub_project = ''
    sub_packet = ''
    
    level_structure_key = get_level_structure_key(work_packet, sub_project, sub_packet, pro_cen_mapping)
    #days_code
    to_date = datetime.date.today() - timedelta(1)
    from_dates = to_date - timedelta(6)
    days_list = num_of_days(to_date, from_dates)
    final_data = production_avg_perday(days_list,project_id,center_id,level_structure_key)
    #final_data = production_avg_perday_week_month(days_list, project_id, center_id, level_structure_key)
    dates_list = get_dates(days_list, project_id, center_id)
    result['data'] = graph_data_alignment_color(final_data, 'data',level_structure_key, project_id, center_id)
    result['date'] = dates_list
    
    #weeks_code
    date = datetime.date.today()
    last_date = date - relativedelta(months=1)
    start_date = datetime.datetime(date.year, date.month, 1)
    from_date = datetime.datetime(last_date.year, last_date.month, 1).date()
    to_date = start_date.date() - relativedelta(days=1)
    days = (to_date - from_date).days
    days = days + 1
    months_dict = {}
    for i in xrange(0, days):
        date = from_date + datetime.timedelta(i)
        month = date.strftime("%B")
        if month in months_dict:
            months_dict[month].append(str(date))
        else:
            months_dict[month] = [str(date)]
    weeks = []
    weekdays = []
    if months_dict == {}:
        num_days = to_date.day
        start = 1
        end = 7 - from_date.weekday()
        while start <= num_days:
            weeks.append({'start': start, 'end': end})
            sdate = from_date + datetime.timedelta(start - 1)
            edate = from_date + datetime.timedelta(end - 1)
            weekdays.append({'start': sdate, 'end': edate})
            start = end + 1
            end = end + 7
            if end > num_days:
                end = num_days

    month_lst = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October','November', 'December']
    month_order = OrderedDict(sorted(months_dict.items(), key=lambda x: month_lst.index(x[0])))
    for month_na in tuple(month_order):
        one_month = months_dict[month_na]
        fro_mon = datetime.datetime.strptime(one_month[0], '%Y-%m-%d').date()
        to_mon = datetime.datetime.strptime(one_month[-1:][0], '%Y-%m-%d').date()
        no_of_days = to_mon - fro_mon
        num_days = int(re.findall('\d+', str(no_of_days))[0]) + 1
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
    week_list = []
    for w_days in weekdays:
        date_list = num_of_days(w_days['end'], w_days['start'])
        week_list.append(date_list)

    data_date, week_names = [], []
    week_num = 0
    productivity_list, final_production = {}, {}
    for week in week_list:
        data = production_avg_perday(week,project_id,center_id,level_structure_key)
        #data = production_avg_perday_week_month(week, project_id, center_id, level_structure_key)
        data_date.append(week[0] + ' to ' + week[-1])
        week_name = str('week' + str(week_num))
        week_names.append(week_name)
        week_num = week_num + 1
        productivity_list[week_name] = data
    final_data = prod_volume_week(week_names, productivity_list, final_production)
    result['week_productivity_data'] = {}
    result['week_productivity_data']['data'] = graph_data_alignment_color(final_data, 'data',level_structure_key, project_id, center_id)
    result['week_productivity_data']['date'] = data_date

    #month_code
    current_date = datetime.date.today()
    last_mon_date = current_date - relativedelta(months=3)
    from_date = datetime.datetime(last_mon_date.year, last_mon_date.month, 1).date()
    start_date = datetime.datetime(current_date.year, current_date.month, 1)
    to_date = start_date.date() - relativedelta(days=1)
    days = (to_date - from_date).days
    days = days + 1
    months_dict = {}
    month_list = [[]]
    month_names_list = []
    month_count = 0
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
    new_month_dict, dwm_dict = {}, {}
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October','November', 'December']
    k = OrderedDict(sorted(months_dict.items(), key=lambda x: months.index(x[0])))
    dwm_dict['month'] = months_dict
    month_names, data_date = [], []
    final_month_productivity, production_list = {}, {}
    for month_na,month_va in zip(month_names_list,month_list):
        month_name = month_na
        month_dates = month_va
        data_date.append(month_dates[0] + ' to ' + month_dates[-1])
        month_names.append(month_name)
        #data = production_avg_perday_week_month(month_dates, project_id, center_id, level_structure_key)
        data = production_avg_perday(month_dates,project_id,center_id,level_structure_key)
        production_list[month_name] = data
    final_data = prod_volume_week(month_names, production_list, final_month_productivity)
    result['month_productivity_data'] = {}
    result['month_productivity_data']['data'] = graph_data_alignment_color(final_data, 'data',level_structure_key, project_id, center_id)
    result['month_productivity_data']['date'] = data_date
    return json_HttpResponse(result)


def get_dates(dates, project, center):

    dates_list = []
    query_check = RawTable.objects.filter(project=project,center=center,date__range=[dates[0],dates[-1]])\
                  .values('date').annotate(total=Sum('per_day'))
    values = OrderedDict(zip(map(lambda p: str(p['date']), query_check), map(lambda p: str(p['total']), query_check)))
    for date_va, total_val in values.iteritems():
        if total_val > 0:
            dates_list.append(date_va)
    return dates_list


def top_five_emp(center,prj_id,dwm_dict,level_key_structure):
    all_details_list = []
    final_list = []
    emplyee_packet_query = query_set_generation(prj_id,center,level_key_structure,dwm_dict['days'])
    packets_list = RawTable.objects.filter(**emplyee_packet_query).values_list('work_packet',flat=True).distinct()
    for i in packets_list:
        dict_to_render = []
        employee_name = RawTable.objects.filter(project=prj_id,center=center,date__range=[dwm_dict['days'][0],dwm_dict['days'][-1:][0]],work_packet=i).values_list('employee_id').distinct()
        for name in employee_name:
            values = RawTable.objects.filter(project=prj_id,center=center,date__range=[dwm_dict['days'][0],dwm_dict['days'][-1:][0]],work_packet=i,employee_id=name[0]).values_list('per_day','date')
            result = 0
            for val in values:
                tar = Targets.objects.filter(project=prj_id,center=center,work_packet=i,from_date__lte=val[1],to_date__gte=val[1]).values_list('target',flat=True)
                if tar:
                    if tar[0]>0:
                        productivity = float(val[0]) / int(tar[0])
                    else:
                        productivity = 0
                    result = result + productivity
            result = float('%.2f' % round(result, 2))
            dict_to_render.append({'employee_id':name[0],'work_packet':i,'productivity':result})
            all_details_list.append({'employee_id':name[0],'work_packet':i,'productivity':result})
        max_in_packet = max([i['productivity'] for i in dict_to_render])
        top_in = [i if i['productivity'] == max_in_packet else '' for i in dict_to_render]
        required_top = [x for x in top_in if x]
        for i in required_top:
            final_list.append(i)
    if len(packets_list) > 1:
        return final_list
    else:
        return all_details_list


