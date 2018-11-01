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
        if function_name in [Valid_Customer_Approved, Invalid_Customer_Reject,Time_Ready_Busy_Percentage]:
            volume_week = week_month_data_acculate(main_dates ,prj_id, center, level_structure_key, dates_list, request, _type, function_name)
            final_dict[result_name] = graph_data_alignment_color(volume_week, 'data', level_structure_key, \
                                        prj_id, center, result_name)
            final_dict['min_max'] = min_max_num(volume_week,result_name)

        elif function_name in [AHT_Comp_id, AHT_Comp_identity,Comparison_identity_verif, Comparison_ID_verif]:
            week_data = week_calculations(dates_list, prj_id, center, level_structure_key, function_name, main_dates,request)
            final_dict[result_name] = graph_data_alignment_color(week_data, 'data', level_structure_key, \
                                        prj_id, center, result_name)
            final_dict['min_max'] = min_max_num(week_data,result_name)
        final_dict['date'] = date_function(dates_list, _type)

    elif main_data_dict['dwm_dict'].has_key('month') and main_data_dict['type'] == 'month':
        dates_list = main_data_dict['dwm_dict']['month']
        if function_name in [Valid_Customer_Approved, Invalid_Customer_Reject, Time_Ready_Busy_Percentage]:
            volume_month = week_month_data_acculate(main_dates ,prj_id, center, level_structure_key, dates_list, request, _type, function_name)
            final_dict[result_name] = graph_data_alignment_color(volume_month, 'data', level_structure_key, \
                                        prj_id, center, result_name)
            final_dict['min_max'] = min_max_num(volume_month,result_name)

        elif function_name in [AHT_Comp_id, AHT_Comp_identity, Comparison_identity_verif, Comparison_ID_verif]:
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
    elif function_name in [AHT_Comp_id, AHT_Comp_identity]:
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
    elif function_name in [AHT_Comp_id, AHT_Comp_identity]:
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
    if len(int_value_range) > 0 and (result_name in ['valid_customer_approve','invalid_customer_reject','custo_time_busy','custo_time_ready']):
        values_list = []
        data = int_value_range.values()
        for value in data:
            values_list = values_list + value
        if (min(values_list) > 0):
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



def Valid_customer_approved(request):

    result_name = 'valid_customer_approve'
    function_name = Valid_Customer_Approved
    model_name = 'IVR_VCR'
    result = generate_day_week_month_format(request, result_name, function_name, model_name)
    return result


def Invalid_customer_reject(request):

    result_name = 'invalid_customer_reject'
    function_name = Invalid_Customer_Reject
    model_name = 'IVR_VCR'
    result = generate_day_week_month_format(request, result_name, function_name, model_name)
    return result


def Cutomer_Time_Ready_Busy(request):

    result_name = 'custo_time_ready_busy'
    function_name = Time_Ready_Busy_Percentage
    model_name = 'Time'
    result = generate_day_week_month_format(request, result_name, function_name, model_name)
    return result


def Volume_identity_verif(request):

    result_name = 'comp_volume_identity'
    function_name = Comparison_identity_verif
    model_name = 'Risk'
    result = generate_day_week_month_format(request, result_name, function_name, model_name)
    return result


def Volume_Comparison_id(request):

    result_name = 'volume_comp_id'
    function_name = Comparison_ID_verif
    model_name = 'Risk'
    result = generate_day_week_month_format(request, result_name, function_name, model_name)
    return result


def AHT_Comparison_id(request):

    result_name = 'aht_comp_id'
    function_name = AHT_Comp_id
    model_name = 'Risk'
    result = generate_day_week_month_format(request, result_name, function_name, model_name)
    return result


def AHT_Comparison_identity(request):

    result_name = 'identity_aht_comp'
    function_name = AHT_Comp_identity
    model_name = 'Risk'
    result = generate_day_week_month_format(request, result_name, function_name, model_name)
    return result


def Valid_Customer_Approved(main_dates ,prj_id, center_obj, level_structure_key, dates_list, request, _type):
    dict_t, date_pack = {}, []
    if _type == 'day':
        filter_params, _term = getting_required_params(level_structure_key, prj_id, center_obj, dates_list)
        if filter_params and _term :
            ivr_query = IVR_VCR.objects.filter(**filter_params)
            valid_approv = ivr_query.values_list('date',_term).annotate(grs_one=Sum('grossed_up_one'), app_vrf=Sum('approved_verified'))
            valid_approv = filter(lambda v: v[1] != u'', valid_approv)
            full_ivr_query = IVR_VCR.objects.filter(project=prj_id,center=center_obj, date__range=[main_dates[0],main_dates[-1]])
            date_pack = full_ivr_query.order_by('date').values_list('date',flat=True).distinct()
            pack_list = full_ivr_query.values_list(_term,flat=True).distinct()
            if valid_approv:
                for date in date_pack:
                    packets = []
                    for val in valid_approv:
                        if date == val[0]:
                            if val[3] > 0:
                                lid_app = float(val[2]/val[3])*100
                                lid_app = 100 - float(lid_app)
                                lid_app = float('%.2f' % round(lid_app, 2))
                            else:
                                lid_app = 0
                            if not dict_t.has_key(val[1]):
                                dict_t[val[1]] = [lid_app]
                            else:
                                dict_t[val[1]].append(lid_app)
                            packets.append(val[1])

                    if len(packets) > 0:
                        for pack in pack_list:
                            if pack not in packets:
                                if not dict_t.has_key(pack):
                                    dict_t[pack] = [0]
                                else:
                                    dict_t[pack].append(0)

    elif _type in ["week","month"]:
        dict_t = {}
        filter_params, _term = getting_required_params(level_structure_key, prj_id, center_obj, dates_list)
        if filter_params and _term :
            ivr_query = IVR_VCR.objects.filter(**filter_params)
            valid_approv = ivr_query.values_list(_term).annotate(grs_one=Sum('grossed_up_one'), app_vrf=Sum('approved_verified'))
            valid_approv = filter(lambda v: v[0] != u'', valid_approv)
            pack_list = IVR_VCR.objects.filter(project=prj_id,center=center_obj, date__range=[main_dates[0],main_dates[-1]]).values_list(_term,flat=True).distinct()
            packets = []
            if valid_approv:
                for val in valid_approv:
                    if val[2] > 0:
                        lid_app = float(val[1]/val[2])*100
                        lid_app = 100 - float(lid_app)
                        lid_app = float('%.2f' % round(lid_app, 2))
                    else:
                        lid_app = 0
                    dict_t[val[0]] = lid_app
                    packets.append(val[0])
                if len(packets) > 0:
                    for pack in pack_list:
                        if pack not in packets:
                            dict_t[pack] = 0
    return dict_t




def Invalid_Customer_Reject(main_dates ,prj_id, center_obj, level_structure_key, dates_list, request, _type):
    dict_t, date_pack = {}, []
    if _type == 'day':
        filter_params, _term = getting_required_params(level_structure_key, prj_id, center_obj, dates_list)
        if filter_params and _term :
            ivr_query = IVR_VCR.objects.filter(**filter_params)
            invalid_reject = ivr_query.order_by('date').values_list('date',_term).annotate(grs_two=Sum('grossed_up_two'), count=Sum('count'))
            invalid_reject = filter(lambda v: v[1] != u'', invalid_reject)
            full_ivr_query = IVR_VCR.objects.filter(project=prj_id,center=center_obj, date__range=[main_dates[0],main_dates[-1]])
            date_pack = full_ivr_query.order_by('date').values_list('date',flat=True).distinct()
            pack_list = full_ivr_query.values_list(_term,flat=True).distinct()
            if invalid_reject:
                for date in date_pack:
                    packets = []
                    for val in invalid_reject:
                        if date == val[0]:
                            if (val[3] + val[2]) > 0:
                                lid_app = float(val[2]/(val[3]+val[2]))*100
                                lid_app =float(lid_app)
                                lid_app = float('%.2f' % round(lid_app, 2))
                            else:
                                lid_app = 0
                            if not dict_t.has_key(val[1]):
                                dict_t[val[1]] = [lid_app]
                            else:
                                dict_t[val[1]].append(lid_app)
                            packets.append(val[1])

                    if len(packets) > 0:
                        for pack in pack_list:
                            if pack not in packets:
                                if not dict_t.has_key(pack):
                                    dict_t[pack] = [0]
                                else:
                                    dict_t[pack].append(0)

    elif _type in ["week","month"]:
        dict_t = {}
        filter_params, _term = getting_required_params(level_structure_key, prj_id, center_obj, dates_list)
        if filter_params and _term :
            ivr_query = IVR_VCR.objects.filter(**filter_params)
            invalid_reject = ivr_query.values_list(_term).annotate(grs_two=Sum('grossed_up_two'), count=Sum('count'))
            invalid_reject = filter(lambda v: v[0] != u'', invalid_reject)
            pack_list = IVR_VCR.objects.filter(project=prj_id,center=center_obj, date__range=[main_dates[0],main_dates[-1]]).values_list(_term,flat=True).distinct()
            packets = []
            if invalid_reject:
                for val in invalid_reject:
                    if (val[2] + val[1]) > 0:
                        lid_app = float(val[1]/(val[1]+val[2]))*100
                        lid_app = float(lid_app)
                        lid_app = float('%.2f' % round(lid_app, 2))
                    else:
                        lid_app = 0
                    dict_t[val[0]] = lid_app
                    packets.append(val[0])
                if len(packets) > 0:
                    for pack in pack_list:
                        if pack not in packets:
                            dict_t[pack] = 0
    return dict_t



def Time_Busy_Percentage(main_dates ,prj_id, center_obj, level_structure_key, dates_list, request, _type):
    result = {}
    if _type == 'day':
        filter_params, _term = getting_required_params(level_structure_key, prj_id, center_obj, dates_list)
        if filter_params and _term:
            time_full_query = Time.objects.filter(project=prj_id,center=center_obj,date__range=[main_dates[0], main_dates[-1]])
            time_query = Time.objects.filter(**filter_params)
            date_pack = time_query.order_by('date').values_list('date',flat=True).distinct()
            pack_list = time_full_query.values_list(_term,flat=True).distinct()
            def concat(x): return str(x+" Busy %")
            pack_list = list(map(concat, pack_list))
            time_data = time_query.order_by('date').values_list('date',_term).annotate(busy=Sum('busy'),total=Sum('total'))
            time_data = filter(lambda t: t[1] != u'', time_data)
            if time_data:
                for date in date_pack:
                    packet_list = []
                    for time_v in time_data:
                        if date == time_v[0]:
                            if time_v[2] > 0:                                
                                b_t_per = (time_v[3]/time_v[2])*100
                                b_t_per = float(100 - float(b_t_per))
                                b_t_per = float('%.2f'% round(b_t_per, 2))
                            else:
                                b_t_per = 0
                            if not result.has_key(time_v[1]+" Busy %"):
                                result[time_v[1]+" Busy %"] = [b_t_per]                            
                            else:
                                result[time_v[1]+" Busy %"].append(b_t_per)
                            packet_list.append(time_v[1]+" Busy %")

                    for pack in pack_list:
                        if pack not in packet_list:
                            if not result.has_key(pack):
                                result[pack] = [0]
                            else:
                                result[pack].append(0)

    elif _type in ["week","month"]:
        result = {}
        filter_params, _term = getting_required_params(level_structure_key, prj_id, center_obj, dates_list)
        if filter_params and _term:
            time_query = Time.objects.filter(project=prj_id,center=center_obj, date__range=[dates_list[0],dates_list[-1]])           
            time_query = Time.objects.filter(**filter_params)
            time_busy = time_query.values_list(_term).annotate(grs_one=Sum('busy'), app_vrf=Sum('total'))
            time_busy = filter(lambda v: v[0] != u'', time_busy)
            pack_list = time_query.values_list('sub_project',flat=True).distinct()
            def concat(x): return str(x+" Busy %")
            pack_list = list(map(concat, pack_list))
            packets = []
            if time_busy:
                for val in time_busy:
                    if val[2] > 0:
                        lid_app = float(val[1]/val[2])*100
                        lid_app = 100 - float(lid_app)
                        lid_app = float('%.2f' % round(lid_app, 2))
                    else:
                        lid_app = 0
                    result[val[0]+" Busy %"] = lid_app
                    packets.append(val[0]+" Busy %")
                if len(packets) > 0:
                    for pack in pack_list:
                        if pack not in packets:
                            result[pack] = 0
    return result




def Time_Ready_Percentage(main_dates ,prj_id, center_obj, level_structure_key, dates_list, request, _type):
    result = {}
    if _type == 'day':
        filter_params, _term = getting_required_params(level_structure_key, prj_id, center_obj, dates_list)
        if filter_params and _term:
            time_full_query = Time.objects.filter(project=prj_id,center=center_obj,date__range=[main_dates[0], main_dates[-1]])
            time_query = Time.objects.filter(**filter_params)
            date_pack = time_query.order_by('date').values_list('date',flat=True).distinct()
            pack_list = time_full_query.values_list(_term,flat=True).distinct()
            def concat(x): return str(x+" Ready %")
            pack_list = list(map(concat, pack_list))
            time_data = time_query.order_by('date').values_list('date',_term).annotate(ready=Sum('ready'),total=Sum('total'))
            time_data = filter(lambda t: t[1] != u'', time_data)
            if time_data:
                for date in date_pack:
                    packet_list = []
                    for time_v in time_data:
                        if date == time_v[0]:
                            if time_v[3] > 0:
                                a_t_per = (time_v[2]/time_v[3])*100
                                a_t_per = float(100 - float(a_t_per))
                                a_t_per = float('%.2f'% round(a_t_per, 2))
                            else:
                                a_t_per = 0
                            if not result.has_key(time_v[1]+" Ready %"):
                                result[time_v[1]+" Ready %"] = [a_t_per]                            
                            else:
                                result[time_v[1]+" Ready %"].append(a_t_per)
                            packet_list.append(time_v[1]+" Ready %")

                    for pack in pack_list:
                        if pack not in packet_list:
                            if not result.has_key(pack):
                                result[pack] = [0]
                            else:
                                result[pack].append(0)

    elif _type in ["week","month"]:
        result = {} 
        filter_params, _term = getting_required_params(level_structure_key, prj_id, center_obj, dates_list)
        if filter_params and _term:
            time_full_query = Time.objects.filter(project=prj_id,center=center_obj, date__range=[dates_list[0],dates_list[-1]])
            time_query = Time.objects.filter(**filter_params)               
            time_ready = time_query.values_list(_term).annotate(grs_one=Sum('ready'), app_vrf=Sum('total'))
            time_ready = filter(lambda v: v[0] != u'', time_ready)            
            pack_list = time_full_query.values_list(_term,flat=True).distinct()
            def concat(x): return str(x+" Ready %")
            pack_list = list(map(concat, pack_list))
            packets = []
            if time_ready:
                for val in time_ready:
                    if val[2] > 0:
                        lid_app = float(val[1]/val[2])*100
                        lid_app = 100 - float(lid_app)
                        lid_app = float('%.2f' % round(lid_app, 2))
                    else:
                        lid_app = 0
                    result[val[0]+" Ready %"] = lid_app
                    packets.append(val[0]+" Ready %")
                
                for pack in pack_list:
                    if pack not in packets:
                        result[pack] = 0

    return result



def Time_Ready_Busy_Percentage(main_dates ,prj_id, center_obj, level_structure_key, dates_list, request, _type):        
    if _type == 'day':
        ready_dict = Time_Ready_Percentage(main_dates ,prj_id, center_obj, level_structure_key, dates_list, request, _type)        
        busy_dict = Time_Busy_Percentage(main_dates ,prj_id, center_obj, level_structure_key, dates_list, request, _type)        
        result = ready_dict.copy()
        result.update(busy_dict)

    elif _type in ["week","month"]:
        ready_dict = Time_Ready_Percentage(main_dates ,prj_id, center_obj, level_structure_key, dates_list, request, _type)        
        busy_dict = Time_Busy_Percentage(main_dates ,prj_id, center_obj, level_structure_key, dates_list, request, _type)        
        result = ready_dict.copy()
        result.update(busy_dict)        

    return result



def Comparison_ID_verif(main_dates ,prj_id, center_obj, level_structure_key, dates_list, request, _type):
    result = {}     
    risk_query = Risk.objects.filter(project=prj_id, center=center_obj, date__range=[dates_list[0],dates_list[-1]],sub_project__contains="ID Verification")
    risk_data = risk_query.order_by('date').values_list('date').annotate(high=Sum('high_volume'), medium=Sum('medium_volume'), low=Sum('low_volume'))        
    full_risk_query = Risk.objects.filter(project=prj_id,center=center_obj, date__range=[main_dates[0],main_dates[-1]])
    date_pack = risk_query.order_by('date').values_list('date', flat=True).distinct()    
    if risk_data:
        for date in date_pack:            
            for risk_v in risk_data:
                if date == risk_v[0]:
                    if risk_v[1]:
                        high = float('%.2f' % round(risk_v[1], 2))
                    else:
                        high = 0
                    if risk_v[2]:
                        medium = float('%.2f' % round(risk_v[2], 2))
                    else:
                        medium = 0
                    if risk_v[3]:
                        low = float('%.2f' % round(risk_v[3], 2))
                    else:
                        low = 0                     
                    if not result.has_key("High Volume"):
                        result["High Volume"] = [high]
                    else:
                        result["High Volume"].append(high)
                    if not result.has_key("Medium Volume"):
                        result["Medium Volume"] = [medium]
                    else:
                        result["Medium Volume"].append(medium)
                    if not result.has_key("Low Volume"):
                        result["Low Volume"] = [low]
                    else:
                        result["Low Volume"].append(low)
              
    
    return result
    
    

def Comparison_identity_verif(main_dates ,prj_id, center_obj, level_structure_key, dates_list, request, _type):
    result = {}     
    risk_query = Risk.objects.filter(project=prj_id, center=center_obj, date__range=[dates_list[0],dates_list[-1]],sub_project__contains="Identity Verification")
    risk_data = risk_query.order_by('date').values_list('date').annotate(high=Sum('high_volume'), medium=Sum('medium_volume'), low=Sum('low_volume'))        
    date_pack = risk_query.order_by('date').values_list('date', flat=True).distinct()    
    if risk_data:
        for date in date_pack:            
            for risk_v in risk_data:
                if date == risk_v[0]:
                    if risk_v[1]:
                        high = float('%.2f' % round(risk_v[1], 2))
                    else:
                        high = 0
                    if risk_v[2]:
                        medium = float('%.2f' % round(risk_v[2], 2))
                    else:
                        medium = 0
                    if risk_v[3]:
                        low = float('%.2f' % round(risk_v[3], 2))
                    else:
                        low = 0   
                    if not result.has_key("High Volume"):
                        result["High Volume"] = [high]
                    else:
                        result["High Volume"].append(high)
                    if not result.has_key("Medium Volume"):
                        result["Medium Volume"] = [medium]
                    else:
                        result["Medium Volume"].append(medium)
                    if not result.has_key("Low Volume"):
                        result["Low Volume"] = [low]
                    else:
                        result["Low Volume"].append(low)     
    
    return result     
    


def AHT_Comp_id(main_dates ,prj_id, center_obj, level_structure_key, dates_list, request, _type):
    result = {}    
    risk_query = Risk.objects.filter(project=prj_id, center=center_obj, date__range=[dates_list[0],dates_list[-1]],sub_project__contains="ID Verification")
    risk_data = risk_query.order_by('date').values_list('date').annotate(high=Sum('high_aht'), medium=Sum('medium_aht'), low=Sum('low_aht'))        
    print risk_data
    date_pack = risk_query.order_by('date').values_list('date', flat=True).distinct()    
    if risk_data:
        for date in date_pack:
            packet_list = []
            for risk_v in risk_data:
                if date == risk_v[0]:
                    if risk_v[1]:
                        high = float('%.2f' % round(risk_v[1], 2))
                    else:
                        high = 0
                    if risk_v[2]:
                        medium = float('%.2f' % round(risk_v[2], 2))
                    else:
                        medium = 0
                    if risk_v[3]:
                        low = float('%.2f' % round(risk_v[3], 2))
                    else:
                        low = 0
                    if not result.has_key("High AHT"):
                        result["High AHT"] = [high]
                    else:
                        result["High AHT"].append(high)
                    if not result.has_key("Medium AHT"):
                        result["Medium AHT"] = [medium]
                    else:
                        result["Medium AHT"].append(medium)
                    if not result.has_key("Low AHT"):
                        result["Low AHT"] = [low]
                    else:
                        result["Low AHT"].append(low)                    
            
    return result



def AHT_Comp_identity(main_dates ,prj_id, center_obj, level_structure_key, dates_list, request, _type):
    result = {}    
    risk_query = Risk.objects.filter(project=prj_id, center=center_obj, date__range=[dates_list[0],dates_list[-1]],sub_project="Identity Verification")
    risk_data = risk_query.order_by('date').values_list('date').annotate(high=Sum('high_aht'), medium=Sum('medium_aht'), low=Sum('low_aht'))            
    date_pack = risk_query.order_by('date').values_list('date', flat=True).distinct()    
    if risk_data:
        for date in date_pack:
            packet_list = []
            for risk_v in risk_data:
                if date == risk_v[0]:
                    if risk_v[1]:
                        high = float('%.2f' % round(risk_v[1], 2))
                    else:
                        high = 0
                    if risk_v[2]:
                        medium = float('%.2f' % round(risk_v[2], 2))
                    else:
                        medium = 0
                    if risk_v[3]:
                        low = float('%.2f' % round(risk_v[3], 2))
                    else:
                        low = 0                     
                    if not result.has_key("High AHT"):
                        result["High AHT"] = [high]
                    else:
                        result["High AHT"].append(high)
                    if not result.has_key("Medium AHT"):
                        result["Medium AHT"] = [medium]
                    else:
                        result["Medium AHT"].append(medium)
                    if not result.has_key("Low AHT"):
                        result["Low AHT"] = [low]
                    else:
                        result["Low AHT"].append(low)                    
            
    return result

                                


