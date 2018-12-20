from django.db.models import Max, Sum, F, IntegerField, FloatField, ExpressionWrapper
from api.models import *
from api.basics import *
from api.commons import *
from api.graph_settings import graph_data_alignment_color
from api.voice_widgets import date_function
from api.monthly_graph import *
from api.utils import *
from common.utils import getHttpResponse as json_HttpResponse


# def generate_dates(date_list, prj_id, center):

#     dates = []
#     date_values = Headcount.objects.filter(\
#                        project=prj_id, center=center, date__range=[date_list[0], date_list[-1]]).\
#                        values_list('date',flat=True).distinct() 
#     for date in date_values:
#         dates.append(str(date))
#     return dates

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
        date_list = main_data_dict['dates']        
        new_date_list = customer_data_date_generation(prj_id, center, date_list, model_name)        
        data = function_name(date_list, prj_id, center, level_structure_key, main_dates, request)
        final_dict[result_name] = graph_data_alignment_color(data, 'data', level_structure_key, prj_id, center)
        final_dict['date'] = new_date_list
        final_dict['min_max'] = min_max_num(data,result_name)        
    elif main_data_dict['dwm_dict'].has_key('week') and main_data_dict['type'] == 'week':
        dates_list = main_data_dict['dwm_dict']['week']        
        week_data = week_calculations(dates_list, prj_id, center, level_structure_key, function_name, main_dates,request)        
        final_dict[result_name] = graph_data_alignment_color(week_data, 'data', level_structure_key, prj_id, center)
        final_dict['min_max'] = min_max_num(week_data,result_name)
        final_dict['date'] = date_function(dates_list, _type)
    else:
        dates_list = main_data_dict['dwm_dict']['month']            
        month_data = month_calculations(dates_list, prj_id, center, level_structure_key, function_name, main_dates,request)        
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
    elif function_name in [head_func, overall_head_fn]:
        result = prod_volume_week_util_headcount(week_names, week_dict, {})    
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
    elif function_name in [head_func,overall_head_fn]:
        result = prod_volume_week_util_headcount(month_names, month_dict, {})    
    else:
        result = prod_volume_week(month_names, month_dict, {})
    return result


def min_max_num(int_value_range, widget_name):
    min_max_dict = {}
    if len(int_value_range) > 0 and (widget_name in ['head_value','overall_head_count','overall_prod']):
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
    model_name = 'Headcount'
    result = generate_day_week_month_format(request, result_name, function_name, model_name)
    return result


def Overall_headcount(request):
    result_name = 'overall_head_count'
    function_name = overall_head_fn
    model_name = 'Headcount'
    result = generate_day_week_month_format(request, result_name, function_name, model_name)
    return result


def Overall_production(request):
    result_name = 'overall_prod'
    function_name = overall_production_fn
    model_name = 'RawTable'
    result = generate_day_week_month_format(request, result_name, function_name, model_name)
    return result


def head_func(date_list,prj_id,center_obj,level_structure_key, main_dates, request):
    result_dict, dct = {}, {}
    filter_params, _term = getting_required_params(level_structure_key, prj_id, center_obj, date_list)    
    if _term and filter_params:
        head_full_query = Headcount.objects.filter(project=prj_id,center=center_obj,date__range=[date_list[0],date_list[-1]])
        dates = head_full_query.values_list('date',flat=True).distinct()                  
        query_values = Headcount.objects.filter(**filter_params)
        data_values = query_values.values_list('date',_term).annotate(total=Sum('billable_agents'))
        data_values = filter(lambda x:x[1] != '', data_values)
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



def overall_head_fn(date_list,prj_id,center_obj,level_structure_key, main_dates, request):
    result_dict = {}
    filter_params, _term = getting_required_params(level_structure_key, prj_id, center_obj, date_list)    
    if _term and filter_params:        
        head_full_query = Headcount.objects.filter(project=prj_id,center=center_obj,date__range=[date_list[0],date_list[-1]])
        dates = head_full_query.values_list('date',flat=True).distinct()                  
        query_values = Headcount.objects.filter(**filter_params)
        data_values = query_values.values_list('date').annotate(total=Sum('billable_agents'))                               
        data_values = filter(lambda x:x[1] != '', data_values)         
        if data_values:
            for date in dates:                
                content_list = []            
                for value in data_values:                
                    if str(date) == str(value[0]):                       
                        if result_dict.has_key("Head Count"):
                            result_dict["Head Count"].append(value[1])
                        else:
                            result_dict["Head Count"] = [value[1]]                          
                        content_list.append(value[1])                    
                
                if len(content_list) == 0:                            
                    if result_dict.has_key("Head Count"):
                        result_dict["Head Count"].append(0)
                    else:
                        result_dict["Head Count"] = [0]  
        
    return result_dict


def overall_production_fn(date_list, prj_id, center_obj, level_structure_key, main_dates, request):
    result_dict, dct = {}, {}
    filter_params, _term = getting_required_params(level_structure_key, prj_id, center_obj, date_list)
    if filter_params and _term:
        query_values = RawTable.objects.filter(**filter_params)
        data_values = query_values.values_list('date').annotate(total=Sum('per_day'))
        dates = RawTable.objects.filter(project=prj_id, center=center_obj, date__range=[date_list[0], date_list[-1]]) \
            .values_list('date', flat=True).distinct()
        targets, targ_query, raw_query, E_data, _type, _term = get_target_query_format(level_structure_key, prj_id,
                                                                                       center_obj, date_list)
        for date in dates:
            content_list = []
            for value in data_values:
                if str(date) == str(value[0]):
                    if result_dict.has_key('Production'):
                        result_dict['Production'].append(value[1])
                    else:
                        result_dict['Production'] = [value[1]]
                    content_list.append(value[1])

            if len(content_list) == 0:
                if result_dict.has_key('Production'):
                    result_dict['Production'].append(0)
                else:
                    result_dict['Production'] = [0]

        if not all("All" in x for x in level_structure_key.values()):
            if _type == "Target":
                Date_type = targ_query.filter(from_date=F('to_date'))
                if (len(targ_query) > 0 and len(Date_type) > 0) or len(targ_query) == 0:
                    targ_value = targ_query.values('from_date', 'to_date').annotate(target=Sum('target_value'))
                    for date in dates:
                        content_list = []
                        for targ_v in targ_value:
                            if date == targ_v['from_date'] and date == targ_v['to_date']:
                                if targ_v["target"] != None:
                                    target = targ_v["target"]
                                    target = float("%.2f" % round(target))
                                else:
                                    target = 0
                                if not result_dict.has_key("Target"):
                                    result_dict['Target'] = [target]
                                result_dict['Target'].append(target)
                                content_list.append(target)

                        if len(content_list) == 0:
                            if not result_dict.has_key("Target"):
                                result_dict['Target'] = [0]
                            else:
                                result_dict['Target'].append(0)

                elif len(targ_query) > 0 and len(Date_type) == 0:
                    targ_value = targ_query.values('from_date', 'to_date').annotate(total=Sum('target_value'),
                                                                                    targ_count=Count('target_value'))
                    if len(targ_value) > 0:
                        targ_value = targ_value.aggregate(
                            target=ExpressionWrapper(F('total') / F('targ_count'), output_field=FloatField()))
                        targ_value = targ_value['target']
                    else:
                        targ_value = 0
                    for date in dates:
                        if targ_value != None:
                            target = targ_value
                            target = float("%.2f" % round(target))
                        else:
                            target = 0
                        if not result_dict.has_key("Target"):
                            result_dict['Target'] = [target]
                        result_dict['Target'].append(target)


            elif _type == "FTE Target":
                Date_type = targ_query.filter(from_date=F('to_date'))
                if (len(targ_query) > 0 and len(Date_type) == 0) or len(targ_query) == 0:
                    targ_value = targ_query.values('from_date', 'to_date').annotate(total=Sum('target_value'),
                                                                                    targ_count=Count('target_value'))
                    if len(targ_value) > 0:
                        targ_value = targ_value.aggregate(
                            target=ExpressionWrapper(F('total') / F('targ_count'), output_field=FloatField()))
                        targ_value = targ_value['target']
                    else:
                        targ_value = 0
                    head_count = Headcount.objects.filter(**filter_params).values('date').annotate(
                        headc=Sum('billable_agents'))
                    for date in dates:
                        content_list = []
                        for head_v in head_count:
                            if date == head_v['date']:
                                if head_v['headc'] != None and targ_value != None:
                                    target = targ_value * head_v['headc']
                                    target = float("%.2f" % round(target))
                                else:
                                    target = 0
                                if not result_dict.has_key("Target"):
                                    result_dict['Target'] = [target]
                                else:
                                    result_dict['Target'].append(target)
                                content_list.append(target)

                        if len(content_list) == 0:
                            if not result_dict.has_key("Target"):
                                result_dict['Target'] = [0]
                            else:
                                result_dict['Target'].append(0)

                elif len(targ_query) > 0 and len(Date_type) > 0:
                    targ_value = targ_query.values('from_date', 'to_date').annotate(target=Sum('target_value'))
                    head_count = Headcount.objects.filter(**filter_params).values('date').annotate(
                        headc=Sum('billable_agents'))
                    for date in dates:
                        content_list = []
                        for targ_v in targ_value:
                            for head_v in head_count:
                                if date == targ_v['from_date'] and date == targ_v['to_date'] and date == head_v["date"]:
                                    if targ_v["target"] != None:
                                        target = targ_v["target"] * head_v["headc"]
                                        target = float("%.2f" % round(target))
                                    else:
                                        target = 0
                                    if not result_dict.has_key("Target"):
                                        result_dict['Target'] = [target]
                                    result_dict['Target'].append(target)
                                    content_list.append(target)

                        if len(content_list) == 0:
                            if not result_dict.has_key("Target"):
                                result_dict['Target'] = [0]
                            else:
                                result_dict['Target'].append(0)

        if result_dict.has_key('Production') and result_dict.has_key('Target'):
            result = result_dict.copy()
            result_dict['Production'], result_dict['Target'] = [], []
            for prod_val, targ_val in zip(result['Production'], result['Target']):
                if prod_val > 0:
                    result_dict['Production'].append(prod_val)
                    result_dict['Target'].append(targ_val)
                else:
                    result_dict['Production'].append(0)
                    result_dict['Target'].append(0)

    return result_dict