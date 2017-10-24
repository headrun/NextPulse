
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
from common.utils import getHttpResponse as json_HttpResponse

def alloc_and_compl(request):
    final_dict = {}
    vol_graph_line_data, vol_graph_bar_data = {}, {}
    final_vol_graph_line_data, final_vol_graph_bar_data = {}, {}
    data_date, new_date_list = [], []
    week_names = []
    week_num = 0
    month_names = []
    final_dict['volume_graphs'] = {}
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
                if total_val > 0:
                    new_date_list.append(date_va)
            #for date_va in sing_list:
                #total_done_value = RawTable.objects.filter(project=prj_id,center=center,date=date_va).aggregate(Max('per_day'))
                #if total_done_value['per_day__max'] > 0:
                    #new_date_list.append(date_va)
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'], main_data_dict['pro_cen_mapping'])
            volume_graph = volume_graph_data(sing_list, main_data_dict['pro_cen_mapping'][0][0], main_data_dict['pro_cen_mapping'][1][0], level_structure_key)
            vol_graph_line_data = volume_graph['line_data']
            vol_graph_bar_data = volume_graph['bar_data']
            #final_dict['date'] = volume_graph['date']
            final_dict['volume_graphs']['bar_data'] = graph_data_alignment_color(vol_graph_bar_data,'data',level_structure_key,
                                           main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0],'volume_bar_graph')
            final_dict['volume_graphs']['line_data'] = graph_data_alignment_color(vol_graph_line_data,'data', level_structure_key,
                                          main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0],'volume_productivity_graph')
            final_dict['date'] = new_date_list
    elif main_data_dict['dwm_dict'].has_key('week') and main_data_dict['type'] == 'week':
        for sing_list in main_dates_list:
            data_date.append(sing_list[0] + ' to ' + sing_list[-1])
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            volume_graph = volume_graph_data_week_month(sing_list, main_data_dict['pro_cen_mapping'][0][0], main_data_dict['pro_cen_mapping'][1][0], level_structure_key)
            vol_graph_line_data[week_name] = volume_graph['line_data']
            vol_graph_bar_data[week_name] = volume_graph['bar_data']
            final_vol_graph_bar_data = volume_status_week(week_names, vol_graph_bar_data, final_vol_graph_bar_data)
            final_vol_graph_line_data = received_volume_week(week_names, vol_graph_line_data, final_vol_graph_line_data)
            final_dict['volume_graphs']['bar_data'] = graph_data_alignment_color(final_vol_graph_bar_data,'data', level_structure_key,prj_id,center,'volume_bar_graph')
            final_dict['volume_graphs']['line_data'] = graph_data_alignment_color(final_vol_graph_line_data,'data', level_structure_key,prj_id,center,'volume_productivity_graph')
            final_dict['date'] = data_date
    else:
        for month_na,month_va in zip(main_data_dict['dwm_dict']['month']['month_names'],main_data_dict['dwm_dict']['month']['month_dates']):
            month_name = month_na
            month_dates = month_va
            data_date.append(month_dates[0] + ' to ' + month_dates[-1])
            month_names.append(month_name)
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            volume_graph = volume_graph_data_week_month(month_dates, prj_id, center, level_structure_key)
            vol_graph_line_data[month_name] = volume_graph['line_data']
            vol_graph_bar_data[month_name] = volume_graph['bar_data']
            final_vol_graph_bar_data = volume_status_week(month_names, vol_graph_bar_data, final_vol_graph_bar_data)
            final_vol_graph_line_data = received_volume_week(month_names, vol_graph_line_data, final_vol_graph_line_data)
            final_dict['volume_graphs'] = {}
            final_dict['volume_graphs']['bar_data'] = graph_data_alignment_color(final_vol_graph_bar_data,'data', level_structure_key,prj_id,center,'volume_bar_graph')
            final_dict['volume_graphs']['line_data'] = graph_data_alignment_color(final_vol_graph_line_data,'data', level_structure_key,prj_id,center,'volume_productivity_graph')
            final_dict['date'] = data_date
    final_dict['type'] = main_data_dict['type']    
    return json_HttpResponse(final_dict)

def utilisation_all(request):
    final_dict = {}
    data_date, new_date_list = [], []
    week_names = []
    week_num = 0
    month_names = []
    utilization_operational_dt , utilization_fte_dt , utilization_ovearll_dt = {}, {}, {}
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
                if total_val > 0:
                #if total_done_value['per_day__max'] > 0:
                    new_date_list.append(date_va)
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],
                                                  main_data_dict['pro_cen_mapping'])
            utilization_details = modified_utilization_calculations(main_data_dict['pro_cen_mapping'][1][0],main_data_dict['pro_cen_mapping'][0][0],
                                                            sing_list,level_structure_key)
            final_dict['utilization_fte_details'] = graph_data_alignment_color(utilization_details['FTE Utilization'], 'data',level_structure_key, main_data_dict['pro_cen_mapping'][0][0], main_data_dict['pro_cen_mapping'][1][0],'fte_utilization')            
            final_dict['utilization_operational_details'] = graph_data_alignment_color(utilization_details['Operational Utilization'], 'data',level_structure_key, main_data_dict['pro_cen_mapping'][0][0], main_data_dict['pro_cen_mapping'][1][0],'operational_utilization')
            final_dict['original_utilization_graph'] = graph_data_alignment_color(utilization_details['Overall Utilization'], 'data', level_structure_key,main_data_dict['pro_cen_mapping'][0][0], main_data_dict['pro_cen_mapping'][1][0],'utilisation_wrt_work_packet')
            final_dict['date'] = new_date_list
            utili_fte_min_max = adding_min_max('utilization_fte_details', utilization_details['FTE Utilization'])
            utili_oper_min_max = adding_min_max('utilization_operational_details', utilization_details['Operational Utilization'])
            utili_all_min_max = adding_min_max('original_utilization_graph', utilization_details['Overall Utilization'])
            final_dict.update(utili_fte_min_max)
            final_dict.update(utili_oper_min_max)
            final_dict.update(utili_all_min_max)

    elif main_data_dict['dwm_dict'].has_key('week') and main_data_dict['type'] == 'week':
        for sing_list in main_dates_list:
            data_date.append(sing_list[0] + ' to ' + sing_list[-1])
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            utilization_details = modified_utilization_calculations(main_data_dict['pro_cen_mapping'][1][0],main_data_dict['pro_cen_mapping'][0][0],sing_list,level_structure_key)
            utilization_operational_dt[week_name] = utilization_details['Operational Utilization']
            utilization_fte_dt[week_name] = utilization_details['FTE Utilization']
            utilization_ovearll_dt[week_name] = utilization_details['Overall Utilization']
            final_utlil_operational = prod_volume_week_util_headcount(week_names, utilization_operational_dt, {})
            final_util_fte = prod_volume_week_util_headcount(week_names, utilization_fte_dt, {})
            final_overall_util = prod_volume_week_util_headcount(week_names, utilization_ovearll_dt, {})
            final_dict['utilization_fte_details'] = graph_data_alignment_color(final_util_fte, 'data',level_structure_key, prj_id, center,'fte_utilization')
            final_dict['utilization_operational_details'] = graph_data_alignment_color(final_utlil_operational,'data', level_structure_key, prj_id,center,'operational_utilization')
            final_dict['original_utilization_graph'] = graph_data_alignment_color(final_overall_util, 'data',level_structure_key, prj_id, center,'utilisation_wrt_work_packet')
            final_dict['date'] = data_date
            utili_fte_min_max = adding_min_max('utilization_fte_details', final_util_fte)
            utili_oper_min_max = adding_min_max('utilization_operational_details', final_utlil_operational)
            utili_all_min_max = adding_min_max('original_utilization_graph', final_overall_util)
            final_dict.update(utili_fte_min_max)
            final_dict.update(utili_oper_min_max)
            final_dict.update(utili_all_min_max)

    else:
        for month_na,month_va in zip(main_data_dict['dwm_dict']['month']['month_names'],main_data_dict['dwm_dict']['month']['month_dates']):
            month_name = month_na
            month_dates = month_va
            data_date.append(month_dates[0] + ' to ' + month_dates[-1])
            month_names.append(month_name)
            prj_id = main_data_dict['pro_cen_mapping'][0][0]
            center = main_data_dict['pro_cen_mapping'][1][0]
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            utilization_details = modified_utilization_calculations(center, prj_id, month_dates, level_structure_key)
            utilization_operational_dt[month_name] = utilization_details['Operational Utilization']
            utilization_fte_dt[month_name] = utilization_details['FTE Utilization']
            utilization_ovearll_dt[month_name] = utilization_details['Overall Utilization']
            final_utlil_operational = prod_volume_week_util_headcount(month_names, utilization_operational_dt, {})
            final_util_fte = prod_volume_week_util_headcount(month_names, utilization_fte_dt, {})
            final_overall_util = prod_volume_week_util_headcount(month_names, utilization_ovearll_dt, {})
            final_dict['utilization_fte_details'] = graph_data_alignment_color(final_util_fte, 'data',level_structure_key, prj_id, center,'fte_utilization')
            final_dict['utilization_operational_details'] = graph_data_alignment_color(final_utlil_operational,'data', level_structure_key, prj_id,center,'operational_utilization')
            final_dict['original_utilization_graph'] = graph_data_alignment_color(final_overall_util, 'data',level_structure_key, prj_id, center,'utilisation_wrt_work_packet')
            final_dict['date'] = data_date
            utili_fte_min_max = adding_min_max('utilization_fte_details', final_util_fte)
            utili_oper_min_max = adding_min_max('utilization_operational_details', final_utlil_operational)
            utili_all_min_max = adding_min_max('original_utilization_graph', final_overall_util)
            final_dict.update(utili_fte_min_max)
            final_dict.update(utili_oper_min_max)
            final_dict.update(utili_all_min_max)

    final_dict['type'] = main_data_dict['type']
    return json_HttpResponse(final_dict)

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
    final_dict['type'] = main_data_dict['type']    
    return json_HttpResponse(result_dict)
 

def tat_data(request):
    final_dict = {}
    data_date, new_date_list = [], []
    week_names = []
    week_num = 0
    tat_graph_dt = {}
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
            #for date_va in sing_list:
            for date_va, total_val in values.iteritems():
                #total_done_value = RawTable.objects.filter(project=prj_id,center=center,date=date_va).aggregate(Max('per_day'))
                #if total_done_value['per_day__max'] > 0:
                if total_val > 0:
                    new_date_list.append(date_va)
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            tat_graph_details = tat_graph(sing_list, main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0], level_structure_key)
            #final_dict['date'] = tat_graph_details['date']
            final_dict['tat_graph_details'] = graph_data_alignment_color(tat_graph_details,'data', level_structure_key,main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0])
            final_dict['date'] = new_date_list
    elif main_data_dict['dwm_dict'].has_key('week') and main_data_dict['type'] == 'week':
        for sing_list in main_dates_list:
            data_date.append(sing_list[0] + ' to ' + sing_list[-1])
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            tat_graph_details = tat_graph(sing_list, main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0], level_structure_key)  
            tat_graph_dt[week_name] = tat_graph_details
        final_tat_details = prod_volume_week_util_headcount(week_names,tat_graph_dt, {})
        final_dict['tat_graph_details'] = graph_data_alignment_color(final_tat_details, 'data',level_structure_key, prj_id, center)
        final_dict['date'] = data_date
    else:
        for month_na,month_va in zip(main_data_dict['dwm_dict']['month']['month_names'],main_data_dict['dwm_dict']['month']['month_dates']):
            month_name = month_na
            month_dates = month_va
            data_date.append(month_dates[0] + ' to ' + month_dates[-1])
            month_names.append(month_name)
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            tat_graph_details = tat_graph(month_dates,prj_id,center,level_structure_key)
            tat_graph_dt[month_name] = tat_graph_details
        final_tat_details = prod_volume_week_util_headcount(month_names, tat_graph_dt, {})
        final_dict['tat_graph_details'] = graph_data_alignment_color(final_tat_details,'data',level_structure_key, prj_id, center)
        final_dict['date'] = data_date
    final_dict['type'] = main_data_dict['type']
    return json_HttpResponse(final_dict)


def main_prod(request):
    final_dict = {}
    data_date = []
    week_names = []
    month_names = []
    week_num = 0
    productivity_list = {}
    final_productivity = {}
    main_data_dict = data_dict(request.GET)
    if main_data_dict['dwm_dict'].has_key('day') and main_data_dict['type'] == 'day':
        main_dates_list = [ main_data_dict['dwm_dict']['day']]
    elif main_data_dict['dwm_dict'].has_key('week') and main_data_dict['type'] == 'week':
        main_dates_list = main_data_dict['dwm_dict']['week']
    elif main_data_dict['dwm_dict'].has_key('month') and main_data_dict['type'] == 'month':
        main_dates_list = main_data_dict['dwm_dict']['month']['month_dates']
    if main_data_dict['dwm_dict'].has_key('day') and main_data_dict['type'] == 'day':
        for sing_list in main_dates_list:
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            final_dict = product_total_graph(sing_list, main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0],level_structure_key)
            if final_dict['prod_days_data']:
                final_dict['productivity_data'] = graph_data_alignment_color(final_dict['prod_days_data'], 'data',level_structure_key,main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0])
            else:
                final_dict['productivity_data'] = []

    elif main_data_dict['dwm_dict'].has_key('week') and main_data_dict['type'] == 'week':
        for sing_list in main_dates_list:
            data_date.append(sing_list[0] + ' to ' + sing_list[-1])
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            final_dict = product_total_graph(sing_list, main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0],level_structure_key)
            if final_dict['prod_days_data']: 
                productivity_list[week_name] = final_dict['volumes_data']['volume_values']
            else:
                productivity_list[week_name] = {} 
            week_num = week_num
        final_productivity = prod_volume_week(week_names, productivity_list, final_productivity)
        error_volume_data = {}
        volume_new_data = []
        prj_id = main_data_dict['pro_cen_mapping'][0][0]
        center = main_data_dict['pro_cen_mapping'][1][0]
        for key, value in final_productivity.iteritems():
            error_graph = []
            error_volume_data[key] = sum(value)
            error_graph.append(key.replace('NA_', '').replace('_NA', ''))
            error_graph.append(sum(value))
            volume_new_data.append(error_graph)
        final_dict['productivity_data'] = graph_data_alignment_color(final_productivity, 'data', level_structure_key,prj_id, center)
        final_dict['volumes_data'] = {}
        final_dict['volumes_data']['volume_new_data'] = volume_new_data
        final_dict['data']['date'] = data_date
    else:
        for month_na,month_va in zip(main_data_dict['dwm_dict']['month']['month_names'],main_data_dict['dwm_dict']['month']['month_dates']):
            month_name = month_na
            month_dates = month_va
            data_date.append(month_dates[0] + ' to ' + month_dates[-1])
            prj_id = main_data_dict['pro_cen_mapping'][0][0]
            center = main_data_dict['pro_cen_mapping'][1][0]
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            final_dict = product_total_graph(month_dates,prj_id,center,level_structure_key)
            if len(final_dict['prod_days_data']) > 0:
                productivity_list[month_name] = final_dict['volumes_data']['volume_values']
            else:
                productivity_list[month_name] = {}
            month_names.append(month_name)
        final_productivity = prod_volume_week(month_names, productivity_list, final_productivity)
        error_volume_data = {}
        volume_new_data = []
        for key, value in final_productivity.iteritems():
            error_graph = []
            error_volume_data[key] = sum(value)
            error_graph.append(key.replace('NA_', '').replace('_NA', ''))
            error_graph.append(sum(value))
            volume_new_data.append(error_graph)
        final_dict['productivity_data'] = graph_data_alignment_color(final_productivity, 'data', level_structure_key,prj_id, center)
        final_dict['volumes_data'] = {}
        final_dict['volumes_data']['volume_new_data'] = volume_new_data
        final_dict['data']['date'] = data_date
    final_dict['type'] = main_data_dict['type']    
    return json_HttpResponse(final_dict)


def volume_graph_data(date_list,prj_id,center_obj,level_structure_key):
    conn = redis.Redis(host="localhost", port=6379, db=0)
    result, volumes_dict, date_values = {}, {}, {}
    new_date_list = []
    #prj_name = Project.objects.filter(id=prj_id).values_list('name',flat=True)
    #center_name = Center.objects.filter(id=center_obj).values_list('name', flat=True)
    project = Project.objects.filter(id=prj_id)
    prj_name = project[0].name
    center_name = project[0].center.name
    query_set = query_set_generation(prj_id,center_obj,level_structure_key,date_list)
    volume_list = worktrack_internal_external_workpackets_list(level_structure_key,'Worktrack',query_set)
    total_done_value = RawTable.objects.filter(project=prj_id, center=center_obj, date__range=[date_list[0], date_list[-1]]).values('date').annotate(total=Sum('per_day'))
    values = OrderedDict(zip(map(lambda p: str(p['date']), total_done_value), map(lambda p: str(p['total']), total_done_value)))
    #for date_va in date_list:
    for date_key, total_val in values.iteritems():
        #total_done_value = RawTable.objects.filter(project=prj_id, center=center_obj, date=date_va).aggregate(Max('per_day'))
        #if total_done_value['per_day__max'] > 0:
        if total_val > 0:
            count =0
            new_date_list.append(date_key)
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

        worktrack_volumes = OrderedDict()
        worktrack_volumes['Opening'] = [sum(i) for i in zip(*opening)]
        worktrack_volumes['Received'] = [sum(i) for i in zip(*received)]
        worktrack_volumes['Non Workable Count'] = [sum(i) for i in zip(*nwc)]
        worktrack_volumes['Completed'] = [sum(i) for i in zip(*completed)]
        worktrack_volumes['Closing balance'] = [sum(i) for i in zip(*closing_bal)]
        worktrack_timeline = OrderedDict()
        day_opening =[worktrack_volumes['Opening'], worktrack_volumes['Received']]
        worktrack_timeline['Opening'] = [sum(i) for i in zip(*day_opening)]
        worktrack_timeline['Completed'] = worktrack_volumes['Completed']
        final_volume_graph = {}
        final_volume_graph['bar_data']  = worktrack_volumes
        final_volume_graph['line_data'] = worktrack_timeline
        final_volume_graph['date'] = new_date_list
        return final_volume_graph
    else:
        final_volume_graph ={}
        final_volume_graph['bar_data'] = {}
        final_volume_graph['line_data'] = {}
        return final_volume_graph


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
