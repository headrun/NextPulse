
import datetime
import redis
from api.models import *
from api.commons import data_dict
from django.db.models import Max, Sum
from collections import OrderedDict
from api.utils import *
from api.basics import *
from api.fte_related import *
from api.weekly_graph import *
from api.graph_settings import *
from api.voice_widgets import date_function
from common.utils import getHttpResponse as json_HttpResponse


def generate_day_type_formats_multiple(request, result_name, function_name, sub_name1, sub_name2, config_1, config_2):

    final_dict = {}
    final_dict[result_name] = {}
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
        if function_name == headcount_widgets:
            data = function_name(center, prj_id, date_list, level_structure_key)
            final_dict['utilization_fte_details'] =  graph_data_alignment_color(data['FTE Utilization'],'data',\
                                                     level_structure_key,prj_id,center,'fte_utilization')
            final_dict['utilization_operational_details'] = graph_data_alignment_color(data['Operational Utilization'],'data',\
                                                            level_structure_key,prj_id,center,'operational_utilization')
            final_dict['original_utilization_graph'] = graph_data_alignment_color(data['Overall Utilization'],'data',\
                                                       level_structure_key,prj_id,center,'utilisation_wrt_work_packet')
        else:
            data = function_name(date_list, prj_id, center, level_structure_key)
            if data:
                sub_result1 = data[sub_name1]
                sub_result2 = data[sub_name2]
                final_dict[result_name][sub_name1] = graph_data_alignment_color(sub_result1,'data',level_structure_key,prj_id,center,config_1)
                final_dict[result_name][sub_name2] = graph_data_alignment_color(sub_result2,'data',level_structure_key,prj_id,center,config_2)
        final_dict['date'] = new_date_list
       
    elif main_data_dict['dwm_dict'].has_key('week') and main_data_dict['type'] == 'week':
        dates_list = main_data_dict['dwm_dict']['week']
        if function_name == headcount_widgets:
            week_data, week_data_1, week_data_2 = week_calculations_multi(dates_list,prj_id,center,level_structure_key,\
                                                  function_name,sub_name1,sub_name2)
            final_dict['utilization_fte_details'] = graph_data_alignment_color(week_data,'data',\
                                                    level_structure_key,prj_id,center,'fte_utilization')
            final_dict['utilization_operational_details'] = graph_data_alignment_color(week_data_1,'data',\
                                                            level_structure_key,prj_id,center,'operational_utilization')
            final_dict['original_utilization_graph'] = graph_data_alignment_color(week_data_2,'data',\
                                                       level_structure_key,prj_id,center,'utilisation_wrt_work_packet')
        else:
            week_data, week_data_1, week_data2 = week_calculations_multi(dates_list,prj_id,center,level_structure_key,\
                                                 function_name,sub_name1,sub_name2)
            if week_data and week_data_1:
                final_dict[result_name][sub_name1] = graph_data_alignment_color(week_data,'data',level_structure_key,prj_id,center,config_1) 
                final_dict[result_name][sub_name2] = graph_data_alignment_color(week_data_1,'data',level_structure_key,prj_id,center,config_2)
        final_dict['date'] = date_function(dates_list, _type)
    
    else:
        dates_list = main_data_dict['dwm_dict']['month']
        if function_name == headcount_widgets:
            month_data, month_data_1, month_data_2 = month_calculations_multi(dates_list,prj_id,center,level_structure_key,\
                                                     function_name,sub_name1,sub_name2)
            final_dict['utilization_fte_details'] = graph_data_alignment_color(month_data,'data',\
                                                    level_structure_key,prj_id,center,'fte_utilization')
            final_dict['utilization_operational_details'] = graph_data_alignment_color(month_data_1,'data',\
                                                            level_structure_key,prj_id,center,'operational_utilization')
            final_dict['original_utilization_graph'] = graph_data_alignment_color(month_data_2,'data',\
                                                       level_structure_key,prj_id,center,'utilisation_wrt_work_packet')
        else:
            month_data, month_data_1, month_data2 = month_calculations_multi(dates_list,prj_id,center,level_structure_key,\
                                                    function_name,sub_name1,sub_name2)
            final_dict[result_name][sub_name1] = graph_data_alignment_color(month_data,'data',level_structure_key,prj_id,center,config_1)
            final_dict[result_name][sub_name2] = graph_data_alignment_color(month_data_1,'data',level_structure_key,prj_id,center,config_2)
        final_dict['date'] = date_function(dates_list, _type)

    final_dict['type'] = main_data_dict['type']
    final_dict['is_annotation'] = annotation_check(request)
    return json_HttpResponse(final_dict)


def fte_graphs(request):

    function_name = fte_trend_scope
    result_name = "fte_calc_data"
    sub_name1 = 'fte_scope'
    sub_name2 = 'fte_trend'
    config_name = 'sum_total_fte'
    config_name_1 = 'total_fte'
    result = generate_day_type_formats_multiple(request,result_name,function_name,sub_name1,sub_name2,config_name,config_name_1)

    return result


def week_calculations_multi(dates,project,center,level_structure_key,function_name,sub_name1,sub_name2):

    week_dict, week_dict_1, week_dict_2 = {}, {}, {}
    final_dict, final_dict_1 = {}, {}
    week_names = []
    week_num = 0
    week_or_month = 'week'
    for date in dates:
        week_name = str('week' + str(week_num))
        week_names.append(week_name)
        week_num = week_num + 1
        if function_name == headcount_widgets:
            data = function_name(center,project,date,level_structure_key)
            if data:
                week_dict[week_name] = data['FTE Utilization']
                week_dict_1[week_name] = data['Operational Utilization']
                week_dict_2[week_name] = data['Overall Utilization']
                result = prod_volume_week_util_headcount(week_names, week_dict, {})
                result_1 = prod_volume_week_util_headcount(week_names, week_dict_1, {})
                result_2 = prod_volume_week_util_headcount(week_names, week_dict_2, {})
        else:
            data = function_name(date, project, center, level_structure_key)
            if data:
                week_dict[week_name] = data[sub_name1]
                week_dict_1[week_name] = data[sub_name1]
                if function_name == fte_trend_scope:
                    result = prod_volume_week_util(project, week_names, week_dict, {}, week_or_month)
                    result_1 = prod_volume_week_util(project ,week_names ,week_dict_1, {}, week_or_month)
                    result_2 = ''
                else:
                    result = volume_status_week(week_names, week_dict, final_dict)
                    result_1 = received_volume_week(week_names, week_dict_1, final_dict_1)
                    result_2 = ''
            else:
                result, result_1, result_2 = {}, {}, {}
    return result, result_1, result_2


def month_calculations_multi(dates,project,center,level_structure_key,function_name,sub_name1,sub_name2):            
           
    month_names = []
    month_dict, month_dict_1, month_dict_2 = {}, {}, {}
    final_dict, final_dict_1 = {}, {}
    week_or_month = 'month'
    for month_na,month_va in zip(dates['month_names'],dates['month_dates']):
        month_name = month_na
        month_dates = month_va
        month_names.append(month_name)
        if function_name == headcount_widgets:
            data = function_name(center, project, month_dates, level_structure_key)
            if data:
                month_dict[month_name] = data['FTE Utilization']
                month_dict_1[month_name] = data['Operational Utilization']
                month_dict_2[month_name] = data['Overall Utilization']
                result = prod_volume_week_util_headcount(month_names, month_dict, {})
                result_1 = prod_volume_week_util_headcount(month_names, month_dict_1, {})
                result_2 = prod_volume_week_util_headcount(month_names, month_dict_2, {})
        else:
            data = function_name(month_dates, project, center, level_structure_key)
            if data:
                month_dict[month_name] = data[sub_name1]
                month_dict_1[month_name] = data[sub_name2]
                if function_name == fte_trend_scope:
                    result = prod_volume_week_util(project, month_names, month_dict, {}, week_or_month)
                    result_1 = prod_volume_week_util(project, month_names, month_dict_1, {}, week_or_month)
                    result_2 = ''
                else:
                    result = volume_status_week(month_names, month_dict, final_dict)
                    result_1 = received_volume_week(month_names, month_dict, final_dict_1)
                    result_2 = ''
            else:
                result, result_1, result_2 = {}, {}, {}
    return result, result_1, result_2


def alloc_and_compl(request):

    function_name = work_track_data
    result_name = 'volume_graphs'
    sub_name1 = 'bar_data'
    sub_name2 = 'line_data'
    config_name = 'volume_bar_graph'
    config_name_1 = 'volume_productivity_graph'

    result = generate_day_type_formats_multiple(request,result_name,function_name,sub_name1,sub_name2,config_name,config_name_1)
    return result


def utilisation_all(request):

    function_name = headcount_widgets
    result_name = ''
    sub_name1 = ''
    sub_name2 = ''
    config_name = ''
    config_name_1 = ''

    result = generate_day_type_formats_multiple(request,result_name,function_name,sub_name1,sub_name2,config_name,config_name_1)
    return result
    

def adding_min_max(high_chart_key,final_dict):
    result = {}
    min_max_values = error_timeline_min_max(final_dict)
    result['min_'+high_chart_key] = min_max_values['min_value']
    result['max_' + high_chart_key] = min_max_values['max_value']
    return result


def work_track_data(date_list,prj_id,center_obj,level_structure_key):

    _dict = OrderedDict()
    line_dict = OrderedDict()
    volume_graph_data = {}

    filter_params = get_query_parameters(level_structure_key, prj_id, center_obj, date_list)
    if filter_params:
        track_query = Worktrack.objects.filter(**filter_params)
        query_data = track_query.values_list('date').annotate(open_val=Sum('opening'), \
                     receive=Sum('received'), hold=Sum('non_workable_count'), done=Sum('completed'), \
                     balance=Sum('closing_balance'))
        for value in query_data:
            if _dict.has_key('Opening'):
                _dict['Opening'].append(value[4])
                _dict['Received'].append(value[1])
                _dict['Non Workable Count'].append(value[3])
                _dict['Completed'].append(value[2])
                _dict['Closing balance'].append(value[5])
                line_dict['Received'].append(value[4]+value[1])
                line_dict['Completed'].append(value[2])
            else:
                _dict['Opening'] = [value[4]]
                _dict['Received'] = [value[1]]
                _dict['Non Workable Count'] = [value[3]]
                _dict['Completed'] = [value[2]]
                _dict['Closing balance'] = [value[5]]
                line_dict['Received'] = [value[4]+value[1]]
                line_dict['Completed'] = [value[2]]
        volume_graph_data['bar_data'] = _dict
        volume_graph_data['line_data'] = line_dict
    return volume_graph_data


def headcount_widgets(center_obj,prj_id,date_list,level_structure_key):

    final_utilization_result = {}
    final_utilization_result['FTE Utilization'] = {}
    final_utilization_result['FTE Utilization']['FTE Utilization'] = []
    final_utilization_result['Operational Utilization'] = {}
    final_utilization_result['Operational Utilization']['Operational Utilization'] = []
    final_utilization_result['Overall Utilization'] = {}
    final_utilization_result['Overall Utilization']['Overall Utilization'] = []

    filter_params = get_query_parameters(level_structure_key, prj_id, center_obj, date_list)
    if filter_params:
        query_values = Headcount.objects.filter(**filter_params).values_list('date').\
                       annotate(bill_hc=Sum('billable_hc'),bill_age=Sum('billable_agents'),\
                       buff_age=Sum('buffer_agents'),qc=Sum('qc_or_qa'),tl=Sum('teamlead'),\
                       trainees=Sum('trainees_and_trainers'),manager=Sum('managers'),mis=Sum('mis'))
        for value in query_values:
            util_numerator = value[7]
            fte_denominator = value[7] + value[8] + value[4] + value[5]
            operational_denominator = fte_denominator + value[3]
            overall_util_denominator = operational_denominator + value[1] + value[6]
            if fte_denominator > 0: 
                fte_value = (float(float(util_numerator) / float(fte_denominator))) * 100
                fte_value = float('%.2f' % round(fte_value, 2))
            else:
                fte_value = 0
            if operational_denominator > 0:
                operational_value = (float(float(util_numerator) / float(operational_denominator))) * 100
                operational_value = float('%.2f' % round(operational_value, 2))
            else:
                operational_value = 0
            if overall_util_denominator > 0:
                overall_util_value = (float(float(util_numerator) / float(overall_util_denominator))) * 100
                overall_util_value = float('%.2f' % round(overall_util_value, 2))
            else:
                overall_util_value = 0
            final_utilization_result['FTE Utilization']['FTE Utilization'].append(fte_value)
            final_utilization_result['Operational Utilization']['Operational Utilization'].append(operational_value)
            final_utilization_result['Overall Utilization']['Overall Utilization'].append(overall_util_value)

    return final_utilization_result


