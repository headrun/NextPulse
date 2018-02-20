
import datetime
import redis
from api.models import *
from api.commons import data_dict
from django.db.models import Max, Sum
from collections import OrderedDict
from api.utils import *
from api.basics import *
from api.query_generations import query_set_generation
from api.fte_related import fte_calculation
from api.production import main_productivity_data
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



def week_calculations_multi(dates,project,center,level_structure_key,function_name,sub_name1,sub_name2):

    week_dict, week_dict_1, week_dict_2 = {}, {}, {}
    final_dict, final_dict_1 = {}, {}
    week_names = []
    week_num = 0
    for date in dates:
        week_name = str('week' + str(week_num))
        week_names.append(week_name)
        week_num = week_num + 1
        if function_name == headcount_widgets:
            data = function_name(center,project,date,level_structure_key)
            week_dict[week_name] = data['FTE Utilization']
            week_dict_1[week_name] = data['Operational Utilization']
            week_dict_2[week_name] = data['Overall Utilization']
            result = prod_volume_week_util_headcount(week_names, week_dict, {})
            result_1 = prod_volume_week_util_headcount(week_names, week_dict_1, {})
            result_2 = prod_volume_week_util_headcount(week_names, week_dict_2, {})
        else:
            data = function_name(date, project, center, level_structure_key)
            week_dict[week_name] = data[sub_name1]
            result = volume_status_week(week_names, week_dict, final_dict)
            result_1 = received_volume_week(week_names, week_dict, final_dict_1)
            result_2 = ''
    return result, result_1, result_2


def month_calculations_multi(dates,project,center,level_structure_key,function_name,sub_name1,sub_name2):            
           
    month_names = []
    month_dict, month_dict_1, month_dict_2 = {}, {}, {}
    final_dict, final_dict_1 = {}, {}
    for month_na,month_va in zip(dates['month_names'],dates['month_dates']):
        month_name = month_na
        month_dates = month_va
        month_names.append(month_name)
        if function_name == headcount_widgets:
            data = function_name(center, project, month_dates, level_structure_key)
            month_dict[month_name] = data['FTE Utilization']
            month_dict_1[month_name] = data['Operational Utilization']
            month_dict_2[month_name] = data['Overall Utilization']
            result = prod_volume_week_util_headcount(month_names, month_dict, {})
            result_1 = prod_volume_week_util_headcount(month_names, month_dict_1, {})
            result_2 = prod_volume_week_util_headcount(month_names, month_dict_2, {})
        else:
            data = function_name(month_dates, project, center, level_structure_key)
            month_dict[month_name] = data[sub_name1]
            month_dict_1[month_name] = data[sub_name2]
            result = volume_status_week(month_names, month_dict, final_dict)
            result_1 = received_volume_week(month_names, month_dict, final_dict_1)
            result_2 = ''
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


def productivity(request):
    final_dict = {}
    productivity_week_num = 0
    main_productivity_timeline = {}
    data_date, new_date_list = [], []
    week_names = []
    week_num = 0
    month_names = []
    main_data_dict = data_dict(request.GET)
    if main_data_dict['dwm_dict'].has_key('day') and main_data_dict['type'] == 'day':
        main_dates_list = [ main_data_dict['dwm_dict']['day']]
    elif main_data_dict['dwm_dict'].has_key('week') and main_data_dict['type'] == 'week':
        main_dates_list = main_data_dict['dwm_dict']['week']
    elif main_data_dict['dwm_dict'].has_key('month') and main_data_dict['type'] == 'month':
        main_dates_list = main_data_dict['dwm_dict']['month']['month_dates']
    prj_id = main_data_dict['pro_cen_mapping'][0][0]
    center = main_data_dict['pro_cen_mapping'][1][0]
    if main_data_dict['dwm_dict'].has_key('day') and main_data_dict['type'] == 'day':
        for sing_list in main_dates_list:
            total_done_value = RawTable.objects.filter(project=prj_id, center=center, date__range=[sing_list[0], sing_list[-1]]).values('date').annotate(total=Sum('per_day'))
            values = OrderedDict(zip(map(lambda p: str(p['date']), total_done_value), map(lambda p: str(p['total']), total_done_value)))
            for date_va, total_val in values.iteritems():
            #for date_va in sing_list:
                #total_done_value = RawTable.objects.filter(project=prj_id,center=center,date=date_va).aggregate(Max('per_day'))
                #if total_done_value['per_day__max'] > 0:
                if total_val > 0:
                    new_date_list.append(date_va)
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            productivity_utilization_data = main_productivity_data(main_data_dict['pro_cen_mapping'][1][0],main_data_dict['pro_cen_mapping'][0][0],                                         sing_list, level_structure_key)
            #final_dict['date'] = productivity_utilization_data['date']
            final_dict['original_productivity_graph'] = graph_data_alignment_color(productivity_utilization_data['productivity'], 'data',level_structure_key,main_data_dict['pro_cen_mapping'][0][0], main_data_dict['pro_cen_mapping'][1][0],'productivity_trends')
            final_dict['date'] = new_date_list
    elif main_data_dict['dwm_dict'].has_key('week') and main_data_dict['type'] == 'week':
        for sing_list in main_dates_list:
            data_date.append(sing_list[0] + ' to ' + sing_list[-1])
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            productivity_utilization_data = main_productivity_data(main_data_dict['pro_cen_mapping'][1][0],main_data_dict['pro_cen_mapping'][0][0],                                         sing_list, level_structure_key)
            productivity_week_name = str('week' + str(productivity_week_num))
            main_productivity_timeline[productivity_week_name] = productivity_utilization_data['productivity']
            productivity_week_num = productivity_week_num + 1
        final_main_productivity_timeline = prod_volume_week_util(prj_id,week_names, main_productivity_timeline, {},'week')
        final_dict['original_productivity_graph'] = graph_data_alignment_color(final_main_productivity_timeline,'data', level_structure_key, prj_id,center,'productivity_trends')
        final_dict['date'] = data_date
    else:
        for month_na,month_va in zip(main_data_dict['dwm_dict']['month']['month_names'],main_data_dict['dwm_dict']['month']['month_dates']):
            month_name = month_na
            month_dates = month_va
            data_date.append(month_dates[0] + ' to ' + month_dates[-1])
            month_names.append(month_name)
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            productivity_utilization_data = main_productivity_data(center, prj_id, month_dates, level_structure_key)
            main_productivity_timeline[month_name] = productivity_utilization_data['productivity']
        final_main_productivity_timeline = prod_volume_week_util(prj_id,month_names, main_productivity_timeline, {},'month')
        final_dict['original_productivity_graph'] = graph_data_alignment_color(final_main_productivity_timeline,'data', level_structure_key, prj_id,center,'productivity_trends')
        final_dict['date'] = data_date
    final_dict['type'] = main_data_dict['type']
    final_dict['is_annotation'] = annotation_check(request)
    return json_HttpResponse(final_dict)

def fte_graphs(request):
    final_dict = {}
    result_dict = {}
    total_fte_list = {}
    wp_fte_list = {}
    fte_week_num = 0
    data_date, new_date_list = [], []
    week_names, month_names = [] , []
    week_num = 0
    main_data_dict = data_dict(request.GET)

    if main_data_dict['dwm_dict'].has_key('day') and main_data_dict['type'] == 'day':
        main_dates_list = [ main_data_dict['dwm_dict']['day']]
    elif main_data_dict['dwm_dict'].has_key('week') and main_data_dict['type'] == 'week':
        main_dates_list = main_data_dict['dwm_dict']['week']
    elif main_data_dict['dwm_dict'].has_key('month') and main_data_dict['type'] == 'month':
        main_dates_list = main_data_dict['dwm_dict']['month']['month_dates']
    prj_id = main_data_dict['pro_cen_mapping'][0][0]
    center = main_data_dict['pro_cen_mapping'][1][0]
    #result_dict['type'] = main_data_dict['type']
    result_dict['is_annotation'] = annotation_check(request)
    if main_data_dict['dwm_dict'].has_key('day') and main_data_dict['type'] == 'day':
        for sing_list in main_dates_list:
            total_done_value = RawTable.objects.filter(project=prj_id, center=center, date__range=[sing_list[0], sing_list[-1]]).values('date').annotate(total=Sum('per_day'))
            values = OrderedDict(zip(map(lambda p: str(p['date']), total_done_value), map(lambda p: str(p['total']), total_done_value)))
            for date_va, total_val in values.iteritems():
            #for date_va in sing_list:
                #total_done_value = RawTable.objects.filter(project=prj_id,center=center,date=date_va).aggregate(Max('per_day'))
                #if total_done_value['per_day__max'] > 0:
                if total_val > 0:
                    new_date_list.append(date_va)
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            fte_graph_data = fte_calculation(request, main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0],sing_list, level_structure_key)
            result_dict['fte_calc_data'] = {} 
            result_dict['fte_calc_data']['total_fte'] = graph_data_alignment_color(fte_graph_data['total_fte'], 'data',level_structure_key, main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0],'sum_total_fte')
            result_dict['fte_calc_data']['work_packet_fte'] = graph_data_alignment_color(fte_graph_data['work_packet_fte'],'data', level_structure_key,main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0])
            result_dict['date'] = new_date_list
    elif main_data_dict['dwm_dict'].has_key('week') and main_data_dict['type'] == 'week':
        for sing_list in main_dates_list:
            data_date.append(sing_list[0] + ' to ' + sing_list[-1])
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            fte_graph_data = fte_calculation(request, main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0],sing_list, level_structure_key)
            fte_week_name = str('week' + str(fte_week_num))
            total_fte_list[fte_week_name] = fte_graph_data['total_fte']
            wp_fte_list[fte_week_name] = fte_graph_data['work_packet_fte']
            fte_week_num = fte_week_num + 1
            final_total_fte_calc = prod_volume_week_util(prj_id,week_names, total_fte_list, {},'week')
            final_total_wp_fte_calc = prod_volume_week_util(prj_id,week_names, wp_fte_list, {},'week')
            result_dict['fte_calc_data'] = {}
            result_dict['fte_calc_data']['total_fte'] = graph_data_alignment_color(final_total_fte_calc, 'data',level_structure_key, prj_id, center,'sum_total_fte')
            result_dict['fte_calc_data']['work_packet_fte'] = graph_data_alignment_color(final_total_wp_fte_calc, 'data',level_structure_key, prj_id,center,'total_fte')
            result_dict['date'] = data_date
    else:
        for month_na,month_va in zip(main_data_dict['dwm_dict']['month']['month_names'],main_data_dict['dwm_dict']['month']['month_dates']):
            month_name = month_na
            month_dates = month_va
            data_date.append(month_dates[0] + ' to ' + month_dates[-1])
            month_names.append(month_name)
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            fte_graph_data = fte_calculation(request, prj_id, center, month_dates, level_structure_key)
            total_fte_list[month_name] = fte_graph_data['total_fte']
            wp_fte_list[month_name] = fte_graph_data['work_packet_fte']
        final_total_fte_calc = prod_volume_week_util(prj_id,month_names, total_fte_list, {},'month')
        final_total_wp_fte_calc = prod_volume_week_util(prj_id,month_names, wp_fte_list, {},'month')
        result_dict['fte_calc_data'] = {}
        result_dict['fte_calc_data']['total_fte'] = graph_data_alignment_color(final_total_fte_calc, 'data',level_structure_key, prj_id, center,'sum_total_fte')
        result_dict['fte_calc_data']['work_packet_fte'] = graph_data_alignment_color(final_total_wp_fte_calc, 'data',level_structure_key, prj_id,center,'total_fte')
        result_dict['date'] = data_date
    return json_HttpResponse(result_dict)
 

def work_track_data(date_list,prj_id,center_obj,level_structure_key):

    _dict = OrderedDict()
    line_dict = OrderedDict()
    volume_graph_data = {}

    filter_params = get_query_parameters(level_structure_key, prj_id, center_obj, date_list)
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


def volumes_graphs_data_table(date_list,prj_id,center,level_structure_key):
    conn = redis.Redis(host="localhost", port=6379, db=0)
    result, volumes_dict, date_values = {}, {}, {}
    #prj_name = Project.objects.filter(id=prj_id).values_list('name',flat=True)
    #center_name = Center.objects.filter(id=center).values_list('name', flat=True)
    project = Project.objects.filter(id=prj_id)
    prj_name = project[0].name
    center_name = project[0].center.name
    query_set = query_set_generation(prj_id,center,level_structure_key,date_list)
    volume_list = worktrack_internal_external_workpackets_list(level_structure_key,'Worktrack',query_set)
    total_done_value = RawTable.objects.filter(project=prj_id, center=center, date__range=[date_list[0], date_list[-1]]).values('date').annotate(total=Sum('per_day'))
    values = OrderedDict(zip(map(lambda p: str(p['date']), total_done_value), map(lambda p: str(p['total']), total_done_value)))
    for date_key, total_val in values.iteritems():
    #for date_va in date_list:
        #total_done_value = RawTable.objects.filter(project=prj_id, center=center, date=date_va).aggregate(Max('per_day'))
        #if total_done_value['per_day__max'] > 0:
        if total_val > 0:
            count =0
            for vol_type in volume_list:
                final_work_packet = level_hierarchy_key(level_structure_key,vol_type)
                if not final_work_packet:
                    final_work_packet = level_hierarchy_key(volume_list[count],vol_type)
                count = count+1
                #date_pattern = '{0}_{1}_{2}_{3}_worktrack'.format(prj_name[0], str(center_name[0]), str(final_work_packet), date_va)
                date_pattern = '{0}_{1}_{2}_{3}_worktrack'.format(prj_name, center_name, str(final_work_packet), date_key)
                key_list = conn.keys(pattern=date_pattern)
                if not key_list:
                    if date_values.has_key(final_work_packet):
                        date_values[final_work_packet]['opening'].append(0)
                        date_values[final_work_packet]['received'].append(0)
                        date_values[final_work_packet]['completed'].append(0)
                        date_values[final_work_packet]['non_workable_count'].append(0)
                        date_values[final_work_packet]['closing_balance'].append(0)
                    else:
                        date_values[final_work_packet] = {}
                        date_values[final_work_packet]['opening']= [0]
                        date_values[final_work_packet]['received']= [0]
                        date_values[final_work_packet]['completed'] = [0]
                        date_values[final_work_packet]['non_workable_count'] = [0]
                        date_values[final_work_packet]['closing_balance']= [0]
                for cur_key in key_list:
                    var = conn.hgetall(cur_key)
                    for key,value in var.iteritems():
                        if (value == 'None') or (value == ''):
                            value = 0
                        if not date_values.has_key(final_work_packet):
                            date_values[final_work_packet] = {}
                        if date_values.has_key(final_work_packet):
                            if date_values[final_work_packet].has_key(key):
                                date_values[final_work_packet][key].append(int(value))
                            else:
                                date_values[final_work_packet][key]=[int(value)]

                    volumes_dict['data'] = date_values
                    volumes_dict['date'] = date_list
                    result['data'] = volumes_dict
    if result.has_key('data'):
        opening,received,nwc,closing_bal,completed = [],[],[],[],[]
        for vol_key in result['data']['data'].keys():
            for volume_key,vol_values in result['data']['data'][vol_key].iteritems():
                if volume_key == 'opening':
                    opening.append(vol_values)
                elif volume_key == 'received':
                    received.append(vol_values)
                elif volume_key == 'completed':
                    completed.append(vol_values)
                elif volume_key == 'closing_balance':
                    closing_bal.append(vol_values)
                elif volume_key == 'non_workable_count':
                    nwc.append(vol_values)

        worktrack_volumes= {}
        worktrack_volumes['opening'] = [sum(i) for i in zip(*opening)]
        worktrack_volumes['received'] = [sum(i) for i in zip(*received)]
        worktrack_volumes['non_workable_count'] = [sum(i) for i in zip(*nwc)]
        worktrack_volumes['completed'] = [sum(i) for i in zip(*completed)]
        worktrack_volumes['closing_balance'] = [sum(i) for i in zip(*closing_bal)]
        worktrack_timeline = {}
        day_opening =[worktrack_volumes['opening'], worktrack_volumes['received']]
        worktrack_timeline['day opening'] = [sum(i) for i in zip(*day_opening)]
        worktrack_timeline['day completed'] = worktrack_volumes['completed']
        final_volume_graph = {}
        final_volume_graph['bar_data']  = worktrack_volumes
        volume_status_table = {}
        volume_status_final_table = {}
        volume_status_final_table['volume_data'] = []
        new_dates = []
        status_count = 0
        total_done_value = RawTable.objects.filter(project=prj_id, center=center, date__range=[date_list[0], date_list[-1]]).values('date').annotate(total=Sum('per_day'))
        values = OrderedDict(zip(map(lambda p: str(p['date']), total_done_value), map(lambda p: str(p['total']), total_done_value)))
        for date_key, total_val in values.iteritems():
        #for date_va in date_list:
            #total_done_value = RawTable.objects.filter(project=prj_id, center=center, date=date_va).aggregate(Max('per_day'))
            #if total_done_value['per_day__max'] > 0:
            if total_val > 0:
                volume_status_table[date_va] = {}
                volume_status_table[date_va]['opening'] = worktrack_volumes['opening'][status_count]
                volume_status_table[date_va]['completed'] = worktrack_volumes['completed'][status_count]
                volume_status_table[date_va]['received'] = worktrack_volumes['received'][status_count]
                volume_status_table[date_va]['closing_balance'] = worktrack_volumes['closing_balance'][status_count]
                volume_status_table[date_va]['non_workable_count'] = worktrack_volumes['non_workable_count'][status_count]
                volume_status_table[date_va]['date'] = date_key
                status_count = status_count +1
                new_dates.append(volume_status_table[date_key])
        return new_dates
    else:
        final_volume_graph ={}
        volume_status_table = {}
        final_volume_graph['bar_data'] = {}
        return volume_status_table
