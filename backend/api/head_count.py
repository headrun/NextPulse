from django.db.models import Max, Sum
from api.models import *
from api.basics import *
from api.commons import *
from api.graph_settings import graph_data_alignment_color
from api.voice_widgets import date_function
from api.monthly_graph import *
from api.utils import *
from common.utils import getHttpResponse as json_HttpResponse


def generate_dates(date_list, prj_id, center):

    dates = []
    date_values = Headcount.objects.filter(\
                       project=prj_id, center=center, date__range=[date_list[0], date_list[-1]]).\
                       values_list('date',flat=True).distinct() 
    for date in date_values:
        dates.append(str(date))
    return dates




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
    main_dates = main_data_dict['dates']
    level_structure_key = get_level_structure_key(work_packet, sub_project, sub_packet, pro_center)
    
    if main_data_dict['dwm_dict'].has_key('day') and main_data_dict['type'] == 'day':
        date_list = main_data_dict['dates']        
        new_date_list = generate_dates(date_list, prj_id, center) 
        data = function_name(date_list, prj_id, center, level_structure_key, main_dates, request)

        if function_name == pre_scan_exception_data:
            final_dict[result_name] = data
        else:
            final_dict[result_name] = graph_data_alignment_color(data, 'data', level_structure_key, prj_id, center)
        final_dict['date'] = new_date_list
        final_dict['min_max'] = min_max_num(data,result_name)        
    elif main_data_dict['dwm_dict'].has_key('week') and main_data_dict['type'] == 'week':
        dates_list = main_data_dict['dwm_dict']['week']
        if function_name == volume_cumulative_data:
            volume_week = week_monthly_calulations(dates_list, prj_id, center, level_structure_key, function_name,main_dates,request)
            final_dict[result_name] = graph_data_alignment_color(volume_week, 'data', level_structure_key, \
                                        prj_id, center, 'monthly_volume')
        else:
            week_data = week_calculations(dates_list, prj_id, center, level_structure_key, function_name, main_dates,request)
            if function_name == pre_scan_exception_data:
                final_dict[result_name] = [week_data]
            else:
                final_dict[result_name] = graph_data_alignment_color(week_data, 'data', level_structure_key, prj_id, center)
            final_dict['min_max'] = min_max_num(week_data,result_name)
        final_dict['date'] = date_function(dates_list, _type)
    else:
        dates_list = main_data_dict['dwm_dict']['month']
        if function_name == volume_cumulative_data:
            volume_month = month_monthly_calculations(dates_list, prj_id, center, level_structure_key, function_name,main_dates,request)
            final_dict[result_name] = graph_data_alignment_color(volume_month, 'data', level_structure_key, \
                                        prj_id, center, 'monthly_volume')
        else:
            month_data = month_calculations(dates_list, prj_id, center, level_structure_key, function_name, main_dates,request)
            if function_name == pre_scan_exception_data:
                final_dict[result_name] = [month_data]
            else:
                final_dict[result_name] = graph_data_alignment_color(month_data, 'data', level_structure_key, prj_id, center)
            final_dict['min_max'] = min_max_num(month_data,result_name)
        final_dict['date'] = date_function(dates_list, _type)

    return json_HttpResponse(final_dict)


def week_calculations(dates, project, center, level_structure_key, function_name, main_dates,request):
    
    week_dict = {}
    week_names = []
    week_num = 0
    for date in dates:
        week_name = str('week' + str(week_num))
        week_names.append(week_name)
        week_num = week_num + 1
        data = function_name(date, project, center, level_structure_key,main_dates,request)
        week_dict[week_name] = data
    if function_name in []:
        result = prod_volume_week_util(project, week_names, week_dict, {}, 'week')
    elif function_name in []:
        result = prod_volume_week_util_headcount(week_names, week_dict, {})
    elif function_name == pre_scan_exception_data:
        result = prod_volume_prescan_week_util(week_names,week_dict, {})
    else:
       result = prod_volume_week(week_names, week_dict, {}) 
    return result  


def month_calculations(dates, project, center, level_structure_key, function_name, main_dates,request):

    month_names = []
    month_dict = {}
    for month_na,month_va in zip(dates['month_names'],dates['month_dates']):
        month_name = month_na
        month_dates = month_va
        month_names.append(month_name)
        data = function_name(month_dates, project, center, level_structure_key, main_dates, request)
        month_dict[month_name] = data
    if function_name in []:
        result = prod_volume_week_util(project, month_names, month_dict, {}, 'month')
    elif function_name in []:
        result = prod_volume_week_util_headcount(month_names, month_dict, {})
    elif function_name == pre_scan_exception_data:
        result = prod_volume_prescan_week_util(month_names, month_dict, {})
    else:
        result = prod_volume_week(month_names, month_dict, {})
    return result

def min_max_num(int_value_range, widget_name):
    min_max_dict = {}
    if len(int_value_range) > 0 and (widget_name in ['aht_team_data', 'tat_graph_details', 'aht_percentage']):
        values_list = []
        data = int_value_range.values()
        for value in data:
            values_list = values_list + value
        if (min(values_list) > 0): 
            min_value = round(min(values_list) - 2)
            max_value = round(max(values_list) + 2)
        else:
            min_value = round(min(values_list))
            max_value = round(max(values_list))
    else:
        min_value, max_value = 0, 0
    min_max_dict['min_value'] = min_value
    min_max_dict['max_value'] = max_value
    return min_max_dict



def head_count(request):
    result_name = 'head_value'
    function_name = head_func
    result = generate_day_week_month_format(request, result_name, function_name)
    return result



def head_func(date_list,prj_id,center_obj,level_structure_key, main_dates, request):
    result_dict, dct = {}, {}
    filter_params, _term = getting_required_params(level_structure_key, prj_id, center_obj, date_list)    
    if _term and filter_params:
        print _term
        head_full_query = Headcount.objects.filter(project=prj_id,center=center_obj,date__range=[date_list[0],date_list[-1]])
        dates = head_full_query.values_list('date',flat=True).distinct()                  
        query_values = Headcount.objects.filter(**filter_params)
        data_values = query_values.values_list('date',_term).annotate(total=Sum('billable_agents'))
        print data_values                        
        data_values = filter(lambda x:x[1] != '', data_values)        
        print data_values        
        packets = head_full_query.values_list(_term,flat=True).distinct()
        if data_values:
            for date in dates:
                _dict_packets = []
                content_list = []            
                for value in data_values:                
                    if str(date) == str(value[0]):                    
                        pack = value[1].lower().title()
                        if result_dict.has_key(pack):
                            result_dict[pack].append(value[2])
                        else:
                            result_dict[pack] = [value[2]]
                        _dict_packets.append(pack)                
                        content_list.append(value[2])

                if len(_dict_packets) > 0:                
                    for pack in packets:
                        pack = pack.lower().title()
                        if pack not in _dict_packets:
                            if result_dict.has_key(pack):
                                result_dict[pack].append(0)
                            else:
                                result_dict[pack] = [0]    
                
                if len(content_list) == 0:
                    for pack in packets:   
                        pack = pack.lower().title()         
                        if result_dict.has_key(pack):
                            result_dict[pack].append(0)
                        else:
                            result_dict[pack] = [0]    

        
    return result_dict