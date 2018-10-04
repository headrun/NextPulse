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
        if function_name in [Valid_Customer_Approved, Invalid_Customer_Reject,Time_Busy_Percentage,Time_Ready_Percentage]:
            volume_week = week_month_data_acculate(main_dates ,prj_id, center, level_structure_key, dates_list, request, _type, function_name)
            final_dict[result_name] = graph_data_alignment_color(volume_week, 'data', level_structure_key, \
                                        prj_id, center, result_name)
            final_dict['min_max'] = min_max_num(volume_week,result_name)

        elif function_name in [AHT_Comparison, Volume_Comparison,Pre_Populated_Vol, Data_Entry_AHT, Data_Entry_Vol, Pre_Populated_AHT]:
            week_data = week_calculations(dates_list, prj_id, center, level_structure_key, function_name, main_dates,request)
            final_dict[result_name] = graph_data_alignment_color(week_data, 'data', level_structure_key, \
                                        prj_id, center, result_name)
            final_dict['min_max'] = min_max_num(week_data,result_name)
        final_dict['date'] = date_function(dates_list, _type)

    elif main_data_dict['dwm_dict'].has_key('month') and main_data_dict['type'] == 'month':
        dates_list = main_data_dict['dwm_dict']['month']
        if function_name in [Valid_Customer_Approved, Invalid_Customer_Reject,Time_Busy_Percentage, Time_Ready_Percentage]:
            volume_month = week_month_data_acculate(main_dates ,prj_id, center, level_structure_key, dates_list, request, _type, function_name)
            final_dict[result_name] = graph_data_alignment_color(volume_month, 'data', level_structure_key, \
                                        prj_id, center, result_name)
            final_dict['min_max'] = min_max_num(volume_month,result_name)

        elif function_name in [AHT_Comparison, Volume_Comparison,Pre_Populated_Vol,Data_Entry_AHT,Data_Entry_Vol, Pre_Populated_AHT]:
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
    elif function_name in [AHT_Comparison,Data_Entry_AHT, Pre_Populated_AHT]:
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
    elif function_name in [AHT_Comparison, Data_Entry_AHT, Pre_Populated_AHT]:
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


def Customer_AHT_Comparison(request):

    result_name = 'custo_aht_comparison'
    function_name = AHT_Comparison
    model_name = 'Risk'
    result = generate_day_week_month_format(request, result_name, function_name, model_name)
    return result


def Customer_Volume_Comparison(request):

    result_name = 'custo_volume_comparison'
    function_name = Volume_Comparison
    model_name = 'Risk'
    result = generate_day_week_month_format(request, result_name, function_name, model_name)
    return result


def Cutomer_Time_Busy(request):

    result_name = 'custo_time_busy'
    function_name = Time_Busy_Percentage
    model_name = 'Time'
    result = generate_day_week_month_format(request, result_name, function_name, model_name)
    return result


def Cutomer_Time_Ready(request):

    result_name = 'custo_time_ready'
    function_name = Time_Ready_Percentage
    model_name = 'Time'
    result = generate_day_week_month_format(request, result_name, function_name, model_name)
    return result


def data_entry_aht(request):

    result_name = 'data_entry_details'
    function_name = Data_Entry_AHT
    model_name = 'Risk'
    result = generate_day_week_month_format(request, result_name, function_name, model_name)
    return result



def pre_pop_vol(request):

    result_name = 'pre_pop_vol_details'
    function_name = Pre_Populated_Vol
    model_name = 'Risk'
    result = generate_day_week_month_format(request, result_name, function_name, model_name)
    return result



def pre_pop_aht(request):

    result_name = 'pre_popul_aht'
    function_name = Pre_Populated_AHT
    model_name = 'Risk'
    result = generate_day_week_month_format(request, result_name, function_name, model_name)
    return result



def data_entry_vol(request):

    result_name = 'data_ent_vol'
    model_name = 'Risk'
    function_name = Data_Entry_Vol
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




def AHT_Comparison(main_dates ,prj_id, center_obj, level_structure_key, dates_list, request, _type):
    result = {}
    filter_params, _term = getting_required_params(level_structure_key, prj_id, center_obj, dates_list)
    if filter_params and _term:
        risk_query = Risk.objects.filter(**filter_params)
        risk_data = risk_query.order_by('date').values_list('date',_term).annotate(high=Sum('high_aht'), medium=Sum('medium_aht'), low=Sum('low_aht'))
        risk_data = filter(lambda v: v[1] != u'', risk_data)
        full_risk_query = Risk.objects.filter(project=prj_id,center=center_obj, date__range=[main_dates[0],main_dates[-1]])
        date_pack = full_risk_query.order_by('date').values_list('date', flat=True).distinct()
        pack_list = full_risk_query.values_list(_term, flat=True).distinct()
        if risk_data:
            for date in date_pack:
                packet_list = []
                for risk_v in risk_data:
                    if date == risk_v[0]:
                        high = float('%.2f' % round(risk_v[2], 2))
                        medium = float('%.2f' % round(risk_v[3], 2))
                        low = float('%.2f' % round(risk_v[4], 2))
                        if not result.has_key(str(risk_v[1])+"_High AHT"):
                            result[str(risk_v[1])+"_High AHT"] = [high]
                        else:
                            result[str(risk_v[1])+"_High AHT"].append(high)
                        if not result.has_key(str(risk_v[1])+"_Medium AHT"):
                            result[str(risk_v[1])+"_Medium AHT"] = [medium]
                        else:
                            result[str(risk_v[1])+"_Medium AHT"].append(medium)
                        if not result.has_key(str(risk_v[1])+"_Low AHT"):
                            result[str(risk_v[1])+"_Low AHT"] = [low]
                        else:
                            result[str(risk_v[1])+"_Low AHT"].append(low)
                        packet_list.append(risk_v[1])

                if len(packet_list) > 0:
                    for pack in pack_list:
                        if pack not in packet_list:
                            if not result.has_key(str(risk_v[1])+"_High AHT"):
                                result[str(risk_v[1])+"_High AHT"] = [0]
                            else:
                                result[str(risk_v[1])+"_High AHT"].append(0)
                            if not result.has_key(str(risk_v[1])+"_Medium AHT"):
                                result[str(risk_v[1])+"_Medium AHT"] = [0]
                            else:
                                result[str(risk_v[1])+"_Medium AHT"].append(0)
                            if not result.has_key(str(risk_v[1])+"_Low AHT"):
                                result[str(risk_v[1])+"_Low AHT"] = [0]
                            else:
                                result[str(risk_v[1])+"_Low AHT"].append(0)

    return result




def Volume_Comparison(main_dates ,prj_id, center_obj, level_structure_key, dates_list, request, _type):
    result = {}
    filter_params, _term = getting_required_params(level_structure_key, prj_id, center_obj, dates_list)
    if filter_params and _term:
        risk_query = Risk.objects.filter(**filter_params)
        risk_data = risk_query.order_by('date').values_list('date',_term).annotate(high=Sum('high_volume'), medium=Sum('medium_volume'), low=Sum('low_volume'))
        risk_data = filter(lambda v: v[1] != u'', risk_data)
        full_risk_query = Risk.objects.filter(project=prj_id,center=center_obj, date__range=[main_dates[0],main_dates[-1]])
        date_pack = full_risk_query.order_by('date').values_list('date', flat=True).distinct()
        pack_list = full_risk_query.values_list(_term, flat=True).distinct()
        if risk_data:
            for date in date_pack:
                packet_list = []
                for risk_v in risk_data:
                    if date == risk_v[0]:
                        high = float('%.2f' % round(risk_v[2], 2))
                        medium = float('%.2f' % round(risk_v[3], 2))
                        low = float('%.2f' % round(risk_v[4], 2))
                        if not result.has_key(str(risk_v[1])+"_High Volume"):
                            result[str(risk_v[1])+"_High Volume"] = [high]
                        else:
                            result[str(risk_v[1])+"_High Volume"].append(high)
                        if not result.has_key(str(risk_v[1])+"_Medium Volume"):
                            result[str(risk_v[1])+"_Medium Volume"] = [medium]
                        else:
                            result[str(risk_v[1])+"_Medium Volume"].append(medium)
                        if not result.has_key(str(risk_v[1])+"_Low Volume"):
                            result[str(risk_v[1])+"_Low Volume"] = [low]
                        else:
                            result[str(risk_v[1])+"_Low Volume"].append(low)
                        packet_list.append(risk_v[1])

                if len(packet_list) > 0:
                    for pack in pack_list:
                        if pack not in packet_list:
                            if not result.has_key(str(risk_v[1])+"_High Volume"):
                                result[str(risk_v[1])+"_High Volume"] = [0]
                            else:
                                result[str(risk_v[1])+"_High Volume"].append(0)
                            if not result.has_key(str(risk_v[1])+"_Medium Volume"):
                                result[str(risk_v[1])+"_Medium Volume"] = [0]
                            else:
                                result[str(risk_v[1])+"_Medium Volume"].append(0)
                            if not result.has_key(str(risk_v[1])+"_Low Volume"):
                                result[str(risk_v[1])+"_Low Volume"] = [0]
                            else:
                                result[str(risk_v[1])+"_Low Volume"].append(0)
    return result




def Time_Busy_Percentage(main_dates ,prj_id, center_obj, level_structure_key, dates_list, request, _type):
    result = {}
    if _type == 'day':
        filter_params, _term = getting_required_params(level_structure_key, prj_id, center_obj, dates_list)
        if filter_params and _term:
            time_query = Time.objects.filter(**filter_params)
            time_full_query = Time.objects.filter(project=prj_id,center=center_obj,date__range=[main_dates[0], main_dates[-1]])
            date_pack = time_full_query.order_by('date').values_list('date',flat=True).distinct()
            pack_list = time_full_query.values_list(_term,flat=True).distinct()
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
                            if not result.has_key(time_v[1]):
                                result[time_v[1]] = [b_t_per]
                            else:
                                result[time_v[1]].append(b_t_per)
                            packet_list.append(time_v[1])

                    for pack in pack_list:
                        if pack not in packet_list:
                            if not result.has_key(pack):
                                result[pack] = [0]
                            else:
                                result[pack].append(0)

    elif _type in ["week","month"]:
        result = {}
        filter_params, _term = getting_required_params(level_structure_key, prj_id, center_obj, dates_list)
        if filter_params and _term :
            time_query = Time.objects.filter(**filter_params)
            time_busy = time_query.values_list(_term).annotate(grs_one=Sum('busy'), app_vrf=Sum('total'))
            time_busy = filter(lambda v: v[0] != u'', time_busy)
            pack_list = Time.objects.filter(project=prj_id,center=center_obj, date__range=[main_dates[0],main_dates[-1]]).values_list(_term,flat=True).distinct()
            packets = []
            if time_busy:
                for val in time_busy:
                    if val[2] > 0:
                        lid_app = float(val[1]/val[2])*100
                        lid_app = 100 - float(lid_app)
                        lid_app = float('%.2f' % round(lid_app, 2))
                    else:
                        lid_app = 0
                    result[val[0]] = lid_app
                    packets.append(val[0])
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
            time_query = Time.objects.filter(**filter_params)
            time_full_query = Time.objects.filter(project=prj_id,center=center_obj,date__range=[main_dates[0], main_dates[-1]])
            date_pack = time_full_query.order_by('date').values_list('date',flat=True).distinct()
            pack_list = time_full_query.values_list(_term,flat=True).distinct()
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
                            if not result.has_key(time_v[1]):
                                result[time_v[1]] = [a_t_per]
                            else:
                                result[time_v[1]].append(a_t_per)
                            packet_list.append(time_v[1])

                    for pack in pack_list:
                        if pack not in packet_list:
                            if not result.has_key(pack):
                                result[pack] = [0]
                            else:
                                result[pack].append(0)

    elif _type in ["week","month"]:
        result = {}
        filter_params, _term = getting_required_params(level_structure_key, prj_id, center_obj, dates_list)
        if filter_params and _term :
            time_query = Time.objects.filter(**filter_params)
            time_ready = time_query.values_list(_term).annotate(grs_one=Sum('ready'), app_vrf=Sum('total'))
            time_ready = filter(lambda v: v[0] != u'', time_ready)
            pack_list = Time.objects.filter(project=prj_id,center=center_obj, date__range=[main_dates[0],main_dates[-1]]).values_list(_term,flat=True).distinct()
            packets = []
            if time_ready:
                for val in time_ready:
                    if val[2] > 0:
                        lid_app = float(val[1]/val[2])*100
                        lid_app = 100 - float(lid_app)
                        lid_app = float('%.2f' % round(lid_app, 2))
                    else:
                        lid_app = 0
                    result[val[0]] = lid_app
                    packets.append(val[0])
                if len(packets) > 0:
                    for pack in pack_list:
                        if pack not in packets:
                            result[pack] = 0

    return result




def Data_Entry_AHT(date_list,prj_id,center_obj,level_structure_key, main_dates, request,_type):
    result_dict = {}
    filter_params, _term = getting_required_params(level_structure_key, prj_id, center_obj, date_list)
    if filter_params and _term:
        query_values = Risk.objects.filter(**filter_params)
        data_values = query_values.values_list('date',_term).annotate(total=Sum('data_entry_done_aht'))
        data_values = filter(lambda v: v[1] != u'',data_values)
        risk_full_query = Risk.objects.filter(project=prj_id,center=center_obj,date__range=[main_dates[0],main_dates[-1]])
        dates = risk_full_query.order_by('date').values_list('date',flat=True).distinct()
        packets = risk_full_query.values_list(_term,flat=True).distinct()
        if data_values:
            for date in dates:
                _dict_packets = []
                for val in data_values:
                    if str(date) == str(val[0]):
                        if result_dict.has_key(val[1]):
                            result_dict[val[1]].append(round(val[2],2))
                        else:
                            result_dict[val[1]] = [round(val[2],2)]
                        _dict_packets.append(val[1])

                for pack in packets:
                    if pack not in _dict_packets:
                        if result_dict.has_key(pack):
                            result_dict[pack].append(0)
                        else:
                            result_dict[pack]=[0]

    return result_dict




def Pre_Populated_Vol(date_list,prj_id,center_obj,level_structure_key, main_dates, request,_type):
    result_dict = {}
    filter_params, _term = getting_required_params(level_structure_key, prj_id, center_obj, date_list)
    if filter_params and _term:
        query_values = Risk.objects.filter(**filter_params)
        data_values = query_values.values_list('date',_term).annotate(total=Sum('pre_populated_volume'))
        data_values = filter(lambda v: v[1] != u'',data_values)
        risk_full_query = Risk.objects.filter(project=prj_id,center=center_obj,date__range=[main_dates[0],main_dates[-1]])
        dates = risk_full_query.order_by('date').values_list('date',flat=True).distinct()
        packets = risk_full_query.values_list(_term,flat=True).distinct()
        if data_values:
            for date in dates:
                _dict_packets = []
                for val in data_values:
                    if str(date) == str(val[0]):
                        if result_dict.has_key(val[1]):
                            result_dict[val[1]].append(round(val[2],2))
                        else:
                            result_dict[val[1]] = [round(val[2],2)]
                        _dict_packets.append(val[1])

                for pack in packets:
                    if pack not in _dict_packets:
                        if result_dict.has_key(pack):
                            result_dict[pack].append(0)
                        else:
                            result_dict[pack]=[0]

    return result_dict



def Data_Entry_Vol(dates_list,prj_id,center_obj,level_structure_key, main_dates, request,_type):
    result_dict = {}
    filter_params, _term = getting_required_params(level_structure_key, prj_id, center_obj, dates_list)
    if _term and filter_params:
        query_values = Risk.objects.filter(**filter_params)
        pacs = query_values.values_list(_term,flat=True).order_by('date').distinct()
        data_values = query_values.values_list('date',_term,'data_entry_volume')
        data_values = filter(lambda v: v[1] != u'',data_values)
        risk_full_query = Risk.objects.filter(project=prj_id,center=center_obj,date__range=[main_dates[0],main_dates[-1]])
        packets = risk_full_query.values_list(_term,flat=True).distinct()
        dates = risk_full_query.order_by('date').values_list('date',flat=True).distinct()
        if data_values:
            for date in dates:
                _dict_packets = []
                for value in data_values:
                    if str(date) == str(value[0]):
                        if value[1] != "":
                            if result_dict.has_key(value[1]):
                                result_dict[value[1]].append(value[2])
                            else:
                                result_dict[value[1]] = [value[2]]
                            _dict_packets.append(value[1])

                for pack in packets:
                    if pack not in _dict_packets:
                        if result_dict.has_key(pack):
                            result_dict[pack].append(0)
                        else:
                            result_dict[pack] = [0]

    return result_dict




def Pre_Populated_AHT(dates_list,prj_id,center_obj,level_structure_key, main_dates, request, _type):
    result_dict = {}
    filter_params, _term = getting_required_params(level_structure_key, prj_id, center_obj, dates_list)
    if _term and filter_params:
        query_values = Risk.objects.filter(**filter_params)
        pacs = query_values.values_list(_term,flat=True).order_by('date').distinct()
        data_values = query_values.values_list('date',_term,'pre_populated_aht')
        data_values = filter(lambda v: v[1] != u'',data_values)
        risk_full_query = Risk.objects.filter(project=prj_id,center=center_obj,date__range=[main_dates[0],main_dates[-1]])
        packets = risk_full_query.values_list(_term,flat=True).distinct()
        dates = risk_full_query.order_by('date').values_list('date',flat=True).distinct()
        if data_values:
            for date in dates:
                _dict_packets = []
                for value in data_values:
                    if str(date) == str(value[0]):
                        if value[1] != "":
                            if result_dict.has_key(value[1]):
                                result_dict[value[1]].append(round(value[2],2))
                            else:
                                result_dict[value[1]] = [round(value[2],2)]
                            _dict_packets.append(value[1])

                for pack in packets:
                    if pack not in _dict_packets:
                        if result_dict.has_key(pack):
                            result_dict[pack].append(0)
                        else:
                            result_dict[pack] = [0]

    return result_dict
