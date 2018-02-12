
import datetime
import redis
from api.models import *
from api.basics import *
from api.utils import *
from api.commons import *
from django.db.models import Max, Sum
from collections import OrderedDict
from api.query_generations import query_set_generation
from api.graph_settings import graph_data_alignment_color
from api.voice_widgets import date_function
from common.utils import getHttpResponse as json_HttpResponse


def generate_day_week_month_format(request, result_name, function_name):

    final_dict = {}
    new_date_list = []
    main_data_dict = data_dict(request.GET)
    prj_id = main_data_dict['pro_cen_mapping'][0][0]
    center = main_data_dict['pro_cen_mapping'][1][0]
    work_packet = main_data_dict['work_packet']
    sub_project = main_data_dict['sub_project']
    sub_packet = main_data_dict['sub_packet']
    pro_center = main_data_dict['pro_cen_mapping']
    _type = main_data_dict['type']

    level_structure_key = get_level_structure_key(work_packet, sub_project, sub_packet, pro_center)


    if main_data_dict['dwm_dict'].has_key('day') and main_data_dict['type'] == 'day':
        date_list = main_data_dict['dates']
        done_value = RawTable.objects.filter(\
                     project=prj_id, center=center, date__range=[date_list[0], date_list[-1]])\
                     .values('date').annotate(total=Sum('per_day'))
        values = OrderedDict(zip(map(lambda p: str(p['date']), done_value), map(lambda p: str(p['total']), done_value)))
        for date_va, total_val in values.iteritems():
            if total_val > 0:
                new_date_list.append(date_va)
        data = function_name(date_list, prj_id, center, level_structure_key)
        final_dict[result_name] = graph_data_alignment_color(data, 'data', level_structure_key, prj_id, center)
        final_dict['date'] = new_date_list

    elif main_data_dict['dwm_dict'].has_key('week') and main_data_dict['type'] == 'week':
        dates_list = main_data_dict['dwm_dict']['week']
        week_data = week_calculations(dates_list, prj_id, center, level_structure_key, function_name)
        final_dict[result_name] = graph_data_alignment_color(week_data, 'data', level_structure_key, prj_id, center)
        final_dict['date'] = date_function(dates_list, _type)
    else:
        dates_list = main_data_dict['dwm_dict']['month']
        month_data = month_calculations(dates_list, prj_id, center, level_structure_key, function_name)
        final_dict[result_name] = graph_data_alignment_color(month_data, 'data', level_structure_key, prj_id, center)
        final_dict['date'] = date_function(dates_list, _type)

    final_dict['type'] = main_data_dict['type']
    final_dict['is_annotation'] = annotation_check(request)  
    return json_HttpResponse(final_dict)


def prod_avg_perday(request):

    result_name = 'production_avg_details'
    function_name = production_avg_perday
    result = generate_day_week_month_format(request, result_name, function_name)
    return result


def main_prod(request):
    
    result_name = 'productivity_data'
    function_name = product_total_graph
    result = generate_day_week_month_format(request, result_name, function_name)
    return result


def week_calculations(dates, project, center, level_structure_key, function_name):
    
    week_dict = {}
    week_names = []
    week_num = 0
    for date in dates:
        week_name = str('week' + str(week_num))
        week_names.append(week_name)
        week_num = week_num + 1
        data = function_name(date, project, center, level_structure_key)
        week_dict[week_name] = data
    if function_name != product_total_graph:
        result = prod_volume_week_util(project, week_names, week_dict, {}, 'week')
    else:
       result = prod_volume_week(week_names, week_dict, {}) 
    return result  


def month_calculations(dates, project, center, level_structure_key, function_name):

    month_names = []
    month_dict = {}
    for month_na,month_va in zip(dates['month_names'],dates['month_dates']):
        month_name = month_na
        month_dates = month_va
        month_names.append(month_name)
        data = function_name(month_dates, project, center, level_structure_key)
        month_dict[month_name] = data
    if function_name != product_total_graph:
        result = prod_volume_week_util(project, month_names, month_dict, {}, 'month')
    else:
        result = prod_volume_week(month_names, month_dict, {})
    return result
        

def production_avg_perday(date_list,prj_id,center_obj,level_structure_key):
    
    result_dict = {}
    new_date_list = []
    
    filter_params, _term = getting_required_params(level_structure_key, prj_id, center_obj, date_list)
    query_values = RawTable.objects.filter(**filter_params)
    data_values = query_values.values_list('date',_term).annotate(total=Sum('per_day'))
    packets = query_values.values_list(_term, flat=True).distinct()
    for packet, packet_1 in zip(packets, data_values):
        if packet == packet_1[1]:
            if result_dict.has_key(packet_1[1]):
                result_dict[packet_1[1]].append(packet_1[2])
            else:
                result_dict[packet_1[1]] = [packet_1[2]]
        else:
            if result_dict.has_key(packet):
                result_dict[packet].append(0)
            else:
                result_dict[packet] = [0]
    return result_dict


def production_avg_perday_week_month(date_list,prj_id,center_obj,level_structure_key):

    result_dict = {}
    new_date_list = []
    
    filter_params, _term = getting_required_params(level_structure_key, prj_id, center_obj, date_list)
    query_values = RawTable.objects.filter(**filter_params)
    data_values = query_values.values_list('date',_term).annotate(total=Sum('per_day'))

    for key in data_values:
        if result_dict.has_key(key[1]):
            result_dict[key[1]].append(key[2])
        else:
            result_dict[key[1]] = [key[2]]
    return result_dict


def product_total_graph(date_list,prj_id,center_obj,level_structure_key):

    result = production_avg_perday_week_month(date_list,prj_id,center_obj,level_structure_key)

    return result

def common_function_dict(date_list, values):
    _dict = {}
    for i in range(0, len(date_list)):
        for key in values:
            if _dict.has_key(key):
                _dict[key].append(0)
            else:
                _dict[key] = [0]
    return _dict


"""def production_avg_perday(date_list,prj_id,center_obj,level_structure_key):
    conn = redis.Redis(host="localhost", port=6379, db=0)
    result, volumes_dict, date_values = {}, {}, {}
    #prj_name = Project.objects.filter(id=prj_id).values_list('name', flat=True)
    #center_name = Center.objects.filter(id=center_obj).values_list('name', flat=True)
    project = Project.objects.filter(id=prj_id)
    prj_name = project[0].name
    center_name = project[0].center.name
    query_set = query_set_generation(prj_id, center_obj, level_structure_key, date_list)
    new_date_list = []
    total_done_value = RawTable.objects.filter(project=prj_id, center=center_obj, date__range=[date_list[0], date_list[-1]]).values('date').annotate(total=Sum('per_day'))
    values = OrderedDict(zip(map(lambda p: str(p['date']), total_done_value), map(lambda p: str(p['total']), total_done_value)))
    for date_key, total_val in values.iteritems():
    #for date_va in date_list:
        #total_done_value = RawTable.objects.filter(project=prj_id, center=center_obj, date=date_va).aggregate(Max('per_day'))
        #if total_done_value['per_day__max'] > 0:
        if total_val > 0:
            #new_date_list.append(date_va)
            new_date_list.append(date_key)
            if level_structure_key.has_key('sub_project'):
                if level_structure_key['sub_project'] == "All":
                    volume_list = RawTable.objects.filter(**query_set).values('sub_project').distinct()
                else:
                    if level_structure_key.has_key('work_packet'):
                        if level_structure_key['work_packet'] == "All":
                            volume_list = RawTable.objects.filter(**query_set).values('sub_project','work_packet').distinct()
                        else:
                            volume_list = RawTable.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()
            elif level_structure_key.has_key('work_packet') and len(level_structure_key) == 1:
                if level_structure_key['work_packet'] == "All":
                    volume_list = RawTable.objects.filter(**query_set).values('sub_project', 'work_packet').distinct()
                else:
                    volume_list = RawTable.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()
            elif level_structure_key.has_key('work_packet') and level_structure_key.has_key('sub_packet'):
                volume_list = RawTable.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()
            else:
                volume_list = [] 
            count = 0
            for vol_type in volume_list:
                final_work_packet = level_hierarchy_key(level_structure_key, vol_type)
                if not final_work_packet:
                    final_work_packet = level_hierarchy_key(volume_list[count], vol_type)
                count = count + 1
                #date_pattern = '{0}_{1}_{2}_{3}'.format(prj_name[0], str(center_name[0]), str(final_work_packet),date_va)
                date_pattern = '{0}_{1}_{2}_{3}'.format(prj_name, center_name, str(final_work_packet), date_key)
                key_list = conn.keys(pattern=date_pattern)
                if not key_list:
                    if date_values.has_key(final_work_packet):
                        date_values[final_work_packet].append(0)
                    else:
                        date_values[final_work_packet] = [0]
                for cur_key in key_list:
                    var = conn.hgetall(cur_key)
                    for key, value in var.iteritems():
                        if value == 'None':
                            value = 0
                        if date_values.has_key(key):
                            date_values[key].append(int(value))
                        else:
                            date_values[key] = [int(value)]
    return date_values"""
