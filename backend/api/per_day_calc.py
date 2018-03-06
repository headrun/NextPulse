
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
from api.monthly_graph import *
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
        new_date_list = generate_dates(date_list, prj_id, center) 
        data = function_name(date_list, prj_id, center, level_structure_key)
        if function_name == pre_scan_exception_data:
            final_dict[result_name] = data
        else:
            final_dict[result_name] = graph_data_alignment_color(data, 'data', level_structure_key, prj_id, center)
        final_dict['date'] = new_date_list

    elif main_data_dict['dwm_dict'].has_key('week') and main_data_dict['type'] == 'week':
        dates_list = main_data_dict['dwm_dict']['week']
        if function_name == volume_cumulative_data:
            volume_week = week_monthly_calulations(dates_list, prj_id, center, level_structure_key, function_name)
            final_dict[result_name] = graph_data_alignment_color(volume_week, 'data', level_structure_key, prj_id, center, 'monthly_volume')
        else:    
            week_data = week_calculations(dates_list, prj_id, center, level_structure_key, function_name)
            if function_name == pre_scan_exception_data:
                final_dict[result_name] = [week_data]
            else:
                final_dict[result_name] = graph_data_alignment_color(week_data, 'data', level_structure_key, prj_id, center)
        final_dict['date'] = date_function(dates_list, _type)
    else:
        dates_list = main_data_dict['dwm_dict']['month']
        if function_name == volume_cumulative_data:
            volume_month = month_monthly_calculations(dates_list, prj_id, center, level_structure_key, function_name)
            final_dict[result_name] = graph_data_alignment_color(volume_month, 'data', level_structure_key, prj_id, center, 'monthly_volume')
        else:
            month_data = month_calculations(dates_list, prj_id, center, level_structure_key, function_name)
            if function_name == pre_scan_exception_data:
                final_dict[result_name] = [month_data]
            else:
                final_dict[result_name] = graph_data_alignment_color(month_data, 'data', level_structure_key, prj_id, center)
        final_dict['date'] = date_function(dates_list, _type)

    final_dict['type'] = main_data_dict['type']
    final_dict['is_annotation'] = annotation_check(request)  
    return json_HttpResponse(final_dict)


def monthly_volume(request):

    result_name = 'monthly_volume_graph_details'
    function_name = volume_cumulative_data
    result = generate_day_week_month_format(request, result_name, function_name)
    return result


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


def productivity(request):

    result_name = 'productivity'

    function_name = productivity_day

    result = generate_day_week_month_format(request, result_name, function_name)

    return result


def tat_data(request):

    result_name = 'tat_graph_details'
    function_name = tat_graph
    result = generate_day_week_month_format(request, result_name, function_name)
    return result


def overall_exce(request):

    result_name = 'overall_exception_details'
    function_name = overall_exception_data
    result = generate_day_week_month_format(request, result_name, function_name)
    return result


def nw_exce(request):

    result_name = 'nw_exception_details'
    function_name = nw_exception_data
    result = generate_day_week_month_format(request, result_name, function_name)
    return result


def pre_scan_exce(request):

    result_name = 'pre_scan_exception_data'
    function_name = pre_scan_exception_data
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
    if function_name in [production_avg_perday,overall_exception_data,nw_exception_data,productivity_day]:
        result = prod_volume_week_util(project, week_names, week_dict, {}, 'week')
    elif function_name == tat_graph:
        result = prod_volume_week_util_headcount(week_names, week_dict, {})
    elif function_name == pre_scan_exception_data:
        result = prod_volume_prescan_week_util(week_names,week_dict, {})
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
    if function_name in [production_avg_perday,overall_exception_data,nw_exception_data,productivity_day]:
        result = prod_volume_week_util(project, month_names, month_dict, {}, 'month')
    elif function_name == tat_graph:
        result = prod_volume_week_util_headcount(month_names, month_dict, {})
    elif function_name == pre_scan_exception_data:
        result = prod_volume_prescan_week_util(month_names, month_dict, {})
    else:
        result = prod_volume_week(month_names, month_dict, {})
    return result
        

def production_avg_perday(date_list,prj_id,center_obj,level_structure_key):

    result_dict, dct = {}, {}
    
    filter_params, _term = getting_required_params(level_structure_key, prj_id, center_obj, date_list)
    query_values = RawTable.objects.filter(**filter_params)
    data_values = query_values.values_list('date',_term).annotate(total=Sum('per_day'))
    packets = [data[1] for data in data_values]
    packets = set(packets)
    for key in packets:
       result_dict.update({key:[]})
    for i, val in enumerate(data_values):
        date,packet,done = val
        if i < len(data_values)-1:
            nxt_date, nxt_packet, nxt_done = data_values[i+1]
            dct.update({packet:done})
            if nxt_date != date:
                for packet in packets:
                    dict_val = result_dict[packet]
                    dict_val.append(dct.setdefault(packet,0))
                    result_dict.update({packet:dict_val})
                dct = {}
        else:
            p_date, p_packet, p_done = data_values[i-1]
            if p_date != date:
                dct = {}
            dct.update({packet:done})
            for packet in packets:
                dict_val = result_dict[packet]
                dict_val.append(dct.setdefault(packet,0))
                result_dict.update({packet:dict_val})
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

    result = production_avg_perday(date_list,prj_id,center_obj,level_structure_key)

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


def week_monthly_calulations(dates, project, center, level_structure_key, function_name):

    monthly_vol_data = {}
    monthly_vol_data['total_workdone'] = []
    monthly_vol_data['total_target'] = []
    week_names = []
    week_num = 0 
    for date in dates:
        week_name = str('week' + str(week_num))
        week_names.append(week_name)
        week_num = week_num + 1 
        data = function_name(date, project, center, level_structure_key)
        for vol_cumulative_key,vol_cumulative_value in data.iteritems():
            if len(vol_cumulative_value) > 0:
                monthly_vol_data[vol_cumulative_key].append(vol_cumulative_value[-1])
            else:
                monthly_vol_data[vol_cumulative_key].append(0)
    monthly_work_done = monthly_vol_data['total_workdone'].count(0)
    monthly_total_target = monthly_vol_data['total_target'].count(0)
    if monthly_work_done == len(monthly_vol_data['total_workdone']) and monthly_total_target == len(monthly_vol_data['total_target']) :
        monthly_vol_data = {}
    final_montly_vol_data = previous_sum(monthly_vol_data)
    return final_montly_vol_data


def month_monthly_calculations(dates, project, center, level_structure_key, function_name):

    monthly_vol_data = {}
    month_names = []
    month_dict = {}
    monthly_vol_data['total_workdone'] = []
    monthly_vol_data['total_target'] = []
    for month_na,month_va in zip(dates['month_names'],dates['month_dates']):
        month_name = month_na
        month_dates = month_va
        month_names.append(month_name)
        monthly_volume_graph_details = volume_cumulative_data(month_dates, project, center, level_structure_key)
        for vol_cumulative_key,vol_cumulative_value in monthly_volume_graph_details.iteritems():
            if len(vol_cumulative_value) > 0:
                monthly_vol_data[vol_cumulative_key].append(vol_cumulative_value[-1])
            else:
                monthly_vol_data[vol_cumulative_key].append(0)
    monthly_work_done = monthly_vol_data['total_workdone'].count(0)
    monthly_total_target = monthly_vol_data['total_target'].count(0)
    if monthly_work_done == len(monthly_vol_data['total_workdone']) and monthly_total_target == len(monthly_vol_data['total_target']) :
        monthly_vol_data = {}
    final_montly_vol_data = previous_sum(monthly_vol_data)
    return final_montly_vol_data

