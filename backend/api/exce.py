
import datetime
from api.models import *
from api.basics import *
from api.utils import *
from api.commons import data_dict
from django.db.models import Max
from api.graph_settings import graph_data_alignment_color
from common.utils import getHttpResponse as json_HttpResponse

def nw_exce(request):
    final_dict = {}
    data_date = [] 
    week_names,month_names = [], []
    week_num = 0
    new_date_list = []
    nw_exception_dt = {}
    main_data_dict = data_dict(request.GET)
    if main_data_dict['dwm_dict'].has_key('day') and main_data_dict['type'] == 'day':
        main_dates_list = [ main_data_dict['dwm_dict']['day']]
    elif main_data_dict['dwm_dict'].has_key('week') and main_data_dict['type'] == 'week':
        main_dates_list = main_data_dict['dwm_dict']['week']
    elif main_data_dict['dwm_dict'].has_key('month') and main_data_dict['type'] == 'month':
        main_dates_list = main_data_dict['dwm_dict']['month']['month_dates']
    prj_id = main_data_dict['pro_cen_mapping'][0][0]
    center = main_data_dict['pro_cen_mapping'][1][0]
    date_value = []
    if main_data_dict['dwm_dict'].has_key('day') and main_data_dict['type'] == 'day':
        for sing_list in main_dates_list:
            for date_va in sing_list:
                total_done_value = RawTable.objects.filter(project=prj_id,center=center,date=date_va).aggregate(Max('per_day'))
                if total_done_value['per_day__max'] > 0:
                    new_date_list.append(date_va)
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            nw_exception_details = nw_exception_data(sing_list, prj_id, center,level_structure_key)
        final_dict['nw_exception_details'] = graph_data_alignment_color(nw_exception_details,'data',level_structure_key,prj_id,center,'')
        final_dict['date'] = new_date_list
    elif main_data_dict['dwm_dict'].has_key('week') and main_data_dict['type'] == 'week':
        for sing_list in main_dates_list:
            data_date.append(sing_list[0] + ' to ' + sing_list[-1])
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            nw_exception_details = nw_exception_data(sing_list, prj_id, center,level_structure_key)
            nw_exception_dt[week_name] = nw_exception_details
        final_nw_exception = prod_volume_week_util(prj_id,week_names,nw_exception_dt, {},'week')
        final_dict['nw_exception_details'] = graph_data_alignment_color(final_nw_exception,'data', level_structure_key, prj_id, center,'')
        final_dict['date'] = data_date
    else:
        for month_na,month_va in zip(main_data_dict['dwm_dict']['month']['month_names'],main_data_dict['dwm_dict']['month']['month_dates']):
            month_name = month_na
            month_dates = month_va
            data_date.append(month_dates[0] + ' to ' + month_dates[-1])
            month_names.append(month_name)
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            nw_exception_details = nw_exception_data(month_dates, prj_id, center,level_structure_key)
            nw_exception_dt[month_name] = nw_exception_details
        final_nw_exception = prod_volume_week_util(prj_id,month_names, nw_exception_dt, {},'month')
        final_dict['nw_exception_details'] = graph_data_alignment_color(final_nw_exception, 'data',level_structure_key, prj_id, center,'')
        final_dict['date'] = data_date
    final_dict['type'] = main_data_dict['type']    
    return json_HttpResponse(final_dict)

def overall_exce(request):
    final_dict = {}
    data_date = []
    week_names,month_names = [], []
    week_num = 0
    new_date_list = []
    overall_exception_dt = {} 
    main_data_dict = data_dict(request.GET)
    if main_data_dict['dwm_dict'].has_key('day') and main_data_dict['type'] == 'day':
        main_dates_list = [ main_data_dict['dwm_dict']['day']]
    elif main_data_dict['dwm_dict'].has_key('week') and main_data_dict['type'] == 'week':
        main_dates_list = main_data_dict['dwm_dict']['week']
    elif main_data_dict['dwm_dict'].has_key('month') and main_data_dict['type'] == 'month':
        main_dates_list = main_data_dict['dwm_dict']['month']['month_dates']
    prj_id = main_data_dict['pro_cen_mapping'][0][0]
    center = main_data_dict['pro_cen_mapping'][1][0]
    date_value = []
    if main_data_dict['dwm_dict'].has_key('day') and main_data_dict['type'] == 'day':
        for sing_list in main_dates_list:
            for date_va in sing_list:
                total_done_value = RawTable.objects.filter(project=prj_id,center=center,date=date_va).aggregate(Max('per_day'))
                if total_done_value['per_day__max'] > 0:
                    new_date_list.append(date_va)
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            overall_exception_details = overall_exception_data(sing_list, prj_id, center,level_structure_key)
        final_dict['overall_exception_details'] = graph_data_alignment_color(overall_exception_details,'data',level_structure_key,prj_id,center,'')
        final_dict['date'] = new_date_list
    elif main_data_dict['dwm_dict'].has_key('week') and main_data_dict['type'] == 'week':
        for sing_list in main_dates_list:
            data_date.append(sing_list[0] + ' to ' + sing_list[-1])
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            overall_exception_details = overall_exception_data(sing_list, prj_id, center,level_structure_key)
            overall_exception_dt[week_name] = overall_exception_details
        final_overall_exception = prod_volume_week_util(prj_id,week_names,overall_exception_dt, {},'week')
        final_dict['overall_exception_details'] = graph_data_alignment_color(final_overall_exception,'data', level_structure_key, prj_id, center,'')
        final_dict['date'] = data_date
    else:
        for month_na,month_va in zip(main_data_dict['dwm_dict']['month']['month_names'],main_data_dict['dwm_dict']['month']['month_dates']):
            month_name = month_na
            month_dates = month_va
            data_date.append(month_dates[0] + ' to ' + month_dates[-1])
            month_names.append(month_name)
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            overall_exception_details = overall_exception_data(month_dates, prj_id, center,level_structure_key)
            overall_exception_dt[month_name] = overall_exception_details
        final_overall_exception = prod_volume_week_util(prj_id,month_names, overall_exception_dt, {},'month')
        final_dict['overall_exception_details'] = graph_data_alignment_color(final_overall_exception, 'data',level_structure_key, prj_id, center,'')
        final_dict['date'] = data_date
    final_dict['type'] = main_data_dict['type']    
    return json_HttpResponse(final_dict)




def pre_scan_exce(request):
    final_dict = {}
    data_date = []
    week_names,month_names = [], []
    week_num = 0
    new_date_list = []
    pre_scan_exception_dt = {}
    main_data_dict = data_dict(request.GET)
    if main_data_dict['dwm_dict'].has_key('day') and main_data_dict['type'] == 'day':
        main_dates_list = [ main_data_dict['dwm_dict']['day']]
    elif main_data_dict['dwm_dict'].has_key('week') and main_data_dict['type'] == 'week': 
        main_dates_list = main_data_dict['dwm_dict']['week']
    elif main_data_dict['dwm_dict'].has_key('month') and main_data_dict['type'] == 'month':
        main_dates_list = main_data_dict['dwm_dict']['month']['month_dates']
    prj_id = main_data_dict['pro_cen_mapping'][0][0]
    center = main_data_dict['pro_cen_mapping'][1][0]
    date_value = []
    if main_data_dict['dwm_dict'].has_key('day') and main_data_dict['type'] == 'day':
        for sing_list in main_dates_list:
            for date_va in sing_list:
                total_done_value = RawTable.objects.filter(project=prj_id,center=center,date=date_va).aggregate(Max('per_day'))
                if total_done_value['per_day__max'] > 0:
                    new_date_list.append(date_va)

            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            pre_scan_exception_details = pre_scan_exception_data(sing_list, main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0])
            final_dict['pre_scan_exception_data'] = pre_scan_exception_details
            final_dict['date'] = new_date_list
    elif main_data_dict['dwm_dict'].has_key('week') and main_data_dict['type'] == 'week':
        for sing_list in main_dates_list:
            data_date.append(sing_list[0] + ' to ' + sing_list[-1])
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            pre_scan_exception_details = pre_scan_exception_data(sing_list, main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0])
            pre_scan_exception_dt[week_name] = pre_scan_exception_details
        final_pre_scan_exception_details = prod_volume_prescan_week_util(week_names,pre_scan_exception_dt, {})
        final_dict['pre_scan_exception_data'] = [final_pre_scan_exception_details]
        final_dict['date'] = data_date
    else:
        for month_na,month_va in zip(main_data_dict['dwm_dict']['month']['month_names'],main_data_dict['dwm_dict']['month']['month_dates']):
            month_name = month_na
            month_dates = month_va
            data_date.append(month_dates[0] + ' to ' + month_dates[-1])
            month_names.append(month_name)
            pre_scan_exception_details = pre_scan_exception_data(month_dates, prj_id, center)
            pre_scan_exception_dt[month_name] = pre_scan_exception_details
        final_pre_scan_exception_details = prod_volume_prescan_week_util(month_names,pre_scan_exception_dt, {})
        final_dict['pre_scan_exception_data'] = [final_pre_scan_exception_details]
        final_dict['date'] = data_date
    final_dict['type'] = main_data_dict['type']
    return json_HttpResponse(final_dict)
