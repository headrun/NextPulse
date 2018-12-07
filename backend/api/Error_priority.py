from __future__ import division
import datetime, collections
from api.models import *
from api.basics import *
from django.db.models import *
from api.query_generations import *
from collections import OrderedDict
from api.commons import data_dict
from api.utils import *
from django.apps import apps
from api.voice_widgets import date_function
from api.graph_settings import graph_data_alignment_color
from common.utils import getHttpResponse as json_HttpResponse


def customer_data_date_generation(project, center, date_lt, model_name):
    model_class = apps.get_model('api',model_name)
    date_lt = model_class.objects.filter(project=project,center=center, date__range=[date_lt[0], date_lt[-1]]).\
                                    order_by('date').values_list('date', flat=True).distinct()
    date_lt = map(str, date_lt)
    return date_lt



def generate_day_week_month_format(request, result_name, function_name, model_name):
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
    main_dates = main_data_dict['dates']
    level_structure_key = get_level_structure_key(work_packet, sub_project, sub_packet, pro_center)

    if main_data_dict['dwm_dict'].has_key('day') and main_data_dict['type'] == 'day':
        dates_list = main_data_dict['dwm_dict']['day']
        date_lst = customer_data_date_generation(prj_id, center, main_dates, model_name)

        data= function_name(main_dates, prj_id, center, level_structure_key, dates_list, request, _type)
        final_dict[result_name] = graph_data_alignment_color(data, 'data', level_structure_key, prj_id, center)
        final_dict['date'] = date_lst
        final_dict['min_max'] = min_max_num(data,result_name)

    elif main_data_dict['dwm_dict'].has_key('week') and main_data_dict['type'] == 'week':
        dates_list = main_data_dict['dwm_dict']['week']
        if function_name in []:
            volume_week = week_month_data_acculate(main_dates ,prj_id, center, level_structure_key, dates_list, request, _type, function_name)
            final_dict[result_name] = graph_data_alignment_color(volume_week, 'data', level_structure_key, \
                                        prj_id, center, result_name)
            final_dict['min_max'] = min_max_num(volume_week,result_name)

        elif function_name in [external_count_cal]:
            week_data = week_calculations(dates_list, prj_id, center, level_structure_key, function_name, main_dates,request)
            final_dict[result_name] = graph_data_alignment_color(week_data, 'data', level_structure_key, \
                                        prj_id, center, result_name)
            final_dict['min_max'] = min_max_num(week_data,result_name)
        final_dict['date'] = date_function(dates_list, _type)

    elif main_data_dict['dwm_dict'].has_key('month') and main_data_dict['type'] == 'month':
        dates_list = main_data_dict['dwm_dict']['month']
        if function_name in []:
            volume_month = week_month_data_acculate(main_dates ,prj_id, center, level_structure_key, dates_list, request, _type, function_name)
            final_dict[result_name] = graph_data_alignment_color(volume_month, 'data', level_structure_key, \
                                        prj_id, center, result_name)
            final_dict['min_max'] = min_max_num(volume_month,result_name)

        elif function_name in [external_count_cal]:
            month_data = month_calculations(dates_list, prj_id, center, level_structure_key, function_name, main_dates,request)
            final_dict[result_name] = graph_data_alignment_color(month_data, 'data', level_structure_key, \
                                        prj_id, center, result_name)
            final_dict['min_max'] = min_max_num(month_data,result_name)

        final_dict['date'] = date_function(dates_list, _type)
    final_dict['type'] = main_data_dict['type']
    final_dict['is_annotation'] = annotation_check(request)
    return json_HttpResponse(final_dict)



def week_calculations(dates, project, center, level_structure_key, function_name, main_dates,request):
    _type = 'week'
    week_dict = {}
    week_names = []
    week_num = 0
    for date in dates:
        week_name = str('week' + str(week_num))
        week_names.append(week_name)
        week_num = week_num + 1
        data = function_name(main_dates ,project, center, level_structure_key, date, request, _type)
        week_dict[week_name] = data
    if function_name in []:
        result = prod_volume_week_util(project, week_names, week_dict, {}, 'week')
    elif function_name in []:
        result = prod_volume_week_util_headcount(week_names, week_dict, {})
    else:
       result = prod_volume_week(week_names, week_dict, {})
    return result



def month_calculations(dates, project, center, level_structure_key, function_name, main_dates,request):
    _type = 'month'
    month_names = []
    month_dict = {}
    for month_na,month_va in zip(dates['month_names'],dates['month_dates']):
        month_name = month_na
        month_dates = month_va
        month_names.append(month_name)
        data = function_name(main_dates ,project, center, level_structure_key, month_dates, request, _type)
        month_dict[month_name] = data
    if function_name in []:
        result = prod_volume_week_util(project, month_names, month_dict, {}, 'month')
    elif function_name in []:
        result = prod_volume_week_util_headcount(month_names, month_dict, {})
    else:
        result = prod_volume_week(month_names, month_dict, {})
    return result



def week_month_data_acculate(main_dates , prj_id, center_obj, level_structure_key, dates_list, request, _type, func_name):
    if _type == 'week':
        week_dict = {}
        week_names = []
        week_num = 0
        for date in dates_list:
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            data = func_name(main_dates ,prj_id, center_obj, level_structure_key, date,request,_type)
            week_dict[week_name] = data
        final_result = Customer_week_fn(week_names, week_dict, {})
    elif _type == 'month':
        month_dict = {}
        month_names = []
        month_num = 0
        for month_na,month_va in zip(dates_list['month_names'],dates_list['month_dates']):
            month_name = month_na
            month_dates = month_va
            month_names.append(month_name)
            data = func_name(main_dates ,prj_id, center_obj, level_structure_key, month_dates, request, _type)
            month_dict[month_name] = data
        final_result = Customer_week_fn(month_names, month_dict, {})
    return final_result



def Customer_week_fn(week_names,productivity_list,final_productivity):
    for final_key, final_value in productivity_list.iteritems():
        for week_key, week_value in final_value.iteritems():
            if week_key not in final_productivity.keys():
                final_productivity[week_key] = []
    for prod_week_num in week_names:
        if productivity_list.has_key(prod_week_num):
            if len(productivity_list[prod_week_num]) > 0:
                for vol_key, vol_values in productivity_list[prod_week_num].iteritems():
                    if final_productivity.has_key(vol_key):
                        final_productivity[vol_key].append(vol_values)
                    else:
                        final_productivity[vol_key] = [vol_values]

                for prod_key, prod_values in final_productivity.iteritems():
                    if prod_key not in productivity_list[prod_week_num].keys():
                        final_productivity[prod_key].append(0)
            else:
                for vol_key, vol_values in final_productivity.iteritems():
                    final_productivity[vol_key].append(0)
    return final_productivity



def min_max_num(int_value_range, result_name):
    min_max_dict = {}    
    if len(int_value_range) > 0 and (result_name in ["external_error_count"]):
        values_list = []
        data = int_value_range.values()
        for value in data:
            values_list = values_list + value
        
        if (min(values_list) > 2):
            min_value = (min(values_list) - 2)
            max_value = (max(values_list) + 2)
        else:
            min_value = (min(values_list) - 0)
            max_value = (max(values_list) + 2)
    else:
        min_value, max_value = 0, 0
    min_max_dict['min_value'] = min_value
    min_max_dict['max_value'] = max_value    
    return min_max_dict




def External_Error_proj(request):

    result_name = 'external_error_count'
    function_name = external_count_cal
    model_name = 'Externalerrors'
    result = generate_day_week_month_format(request, result_name, function_name, model_name)
    return result



def external_count_cal(main_dates, prj_id, center, level_structure_key, dates_list, request, _type):
    result = {}
    filter_params, _term = getting_required_params(level_structure_key, prj_id, center, dates_list)
    if filter_params and _term:
        ext_full_query = Externalerrors.objects.filter(project=prj_id,center=center,date__range=[main_dates[0], main_dates[-1]])
        ext_query = Externalerrors.objects.filter(**filter_params)
        date_pack = ext_query.order_by('date').values_list('date',flat=True).distinct()
        pack_list = ext_full_query.values_list('error_types',flat=True).distinct()
        ext_data = ext_query.order_by('date').filter(error_values__gt=0).values_list('date','error_types').annotate(total_errors=Sum('error_values'))                                        
        ext_data = filter(lambda t: t[1] != u'', ext_data)
        if ext_data:
            for date in date_pack:
                packet_list = []
                for ext_v in ext_data:
                    if date == ext_v[0]:
                        if ext_v[2] != 'None':
                            ext_out = int(ext_v[2])                            
                        else:
                            ext_out = 0                            
                        if not result.has_key(ext_v[1].lower()):
                            result[ext_v[1].lower()] = [ext_out]                            
                        else:   
                            result[ext_v[1].lower()].append(ext_out)
                        packet_list.append(ext_v[1].lower())                       


                if len(packet_list):
                    for pack in pack_list:
                        if pack.lower() not in packet_list:
                            if not result.has_key(pack.lower()):
                                result[pack.lower()] = [0]
                            else:
                                result[pack.lower()].append(0)
    
    return result

