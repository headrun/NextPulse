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
from api.monthly_graph import get_target_query_format
from itertools import chain


def customer_data_date_generation(project, center, date_lt, model_name):
    model_class = apps.get_model('api', model_name)
    date_lt = model_class.objects.filter(project=project, center=center, date__range=[date_lt[0], date_lt[-1]]). \
        order_by('date').values_list('date', flat=True).distinct()
    date_lt = map(str, date_lt)
    return date_lt

def customer_data_date_generation_ibm(project, center, date_lt, model_name, level_structure_key):
    model_class = apps.get_model('api', model_name)
    filter_params, _term = getting_required_params(level_structure_key, project, center, date_lt)
    date_lt = model_class.objects.filter(**filter_params).order_by('date').values_list('date', flat=True).distinct()
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
        if prj_id in [30, 112, 160, 129, 159, 117, 180, 181, 182, 123, 113, 162, 114, 126, 119, 115, 118, 130, 127,
                        154, 158, 121, 156, 161, 116, 132] and function_name in [overall_external_accur_trends,overall_internal_accur_trends]:
            date_lst = customer_data_date_generation_ibm(prj_id, center, main_dates, model_name, level_structure_key)
        else:
            date_lst = customer_data_date_generation(prj_id, center, main_dates, model_name)
        data = function_name(main_dates, prj_id, center, level_structure_key, dates_list, request, _type)
        final_dict[result_name] = graph_data_alignment_color(data, 'data', level_structure_key, prj_id, center)
        final_dict['date'] = date_lst
        final_dict['min_max'] = min_max_num(data, result_name)

    elif main_data_dict['dwm_dict'].has_key('week') and main_data_dict['type'] == 'week':
        dates_list = main_data_dict['dwm_dict']['week']
        if function_name in [external_count_cal, overall_external_accur_trends, overall_ext_count,
                             overall_internal_accur_trends, overall_tat_graph, Probe_overall_accuracy]:
            volume_week = week_month_data_acculate(main_dates, prj_id, center, level_structure_key, dates_list, request,
                                                   _type, function_name)
            final_dict[result_name] = graph_data_alignment_color(volume_week, 'data', level_structure_key, \
                                                                 prj_id, center, result_name)
            final_dict['min_max'] = min_max_num(volume_week, result_name)

        elif function_name in []:
            week_data = week_calculations(dates_list, prj_id, center, level_structure_key, function_name, main_dates,
                                          request)
            final_dict[result_name] = graph_data_alignment_color(week_data, 'data', level_structure_key, \
                                                                 prj_id, center, result_name)
            final_dict['min_max'] = min_max_num(week_data, result_name)
        final_dict['date'] = date_function(dates_list, _type)

    elif main_data_dict['dwm_dict'].has_key('month') and main_data_dict['type'] == 'month':
        dates_list = main_data_dict['dwm_dict']['month']
        if function_name in [external_count_cal, overall_external_accur_trends, overall_ext_count,
                             overall_internal_accur_trends, overall_tat_graph, Probe_overall_accuracy]:
            volume_month = week_month_data_acculate(main_dates, prj_id, center, level_structure_key, dates_list,
                                                    request, _type, function_name)
            final_dict[result_name] = graph_data_alignment_color(volume_month, 'data', level_structure_key, \
                                                                 prj_id, center, result_name)
            final_dict['min_max'] = min_max_num(volume_month, result_name)

        elif function_name in []:
            month_data = month_calculations(dates_list, prj_id, center, level_structure_key, function_name, main_dates,
                                            request)
            final_dict[result_name] = graph_data_alignment_color(month_data, 'data', level_structure_key, \
                                                                 prj_id, center, result_name)
            final_dict['min_max'] = min_max_num(month_data, result_name)

        final_dict['date'] = date_function(dates_list, _type)
    final_dict['type'] = main_data_dict['type']
    final_dict['is_annotation'] = annotation_check(request)
    return json_HttpResponse(final_dict)


def week_calculations(dates, project, center, level_structure_key, function_name, main_dates, request):
    _type = 'week'
    week_dict = {}
    week_names = []
    week_num = 0
    for date in dates:
        week_name = str('week' + str(week_num))
        week_names.append(week_name)
        week_num = week_num + 1
        data = function_name(main_dates, project, center, level_structure_key, date, request, _type)
        week_dict[week_name] = data
    if function_name in []:
        result = prod_volume_week_util(project, week_names, week_dict, {}, 'week')
    elif function_name in []:
        result = prod_volume_week_util_headcount(week_names, week_dict, {})
    else:
        result = prod_volume_week(week_names, week_dict, {})
    return result


def month_calculations(dates, project, center, level_structure_key, function_name, main_dates, request):
    _type = 'month'
    month_names = []
    month_dict = {}
    for month_na, month_va in zip(dates['month_names'], dates['month_dates']):
        month_name = month_na
        month_dates = month_va
        month_names.append(month_name)
        data = function_name(main_dates, project, center, level_structure_key, month_dates, request, _type)
        month_dict[month_name] = data
    if function_name in []:
        result = prod_volume_week_util(project, month_names, month_dict, {}, 'month')
    elif function_name in []:
        result = prod_volume_week_util_headcount(month_names, month_dict, {})
    else:
        result = prod_volume_week(month_names, month_dict, {})
    return result


def week_month_data_acculate(main_dates, prj_id, center_obj, level_structure_key, dates_list, request, _type,
                             func_name):
    if _type == 'week':
        week_dict = {}
        week_names = []
        week_num = 0
        for date in dates_list:
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            data = func_name(main_dates, prj_id, center_obj, level_structure_key, date, request, _type)
            week_dict[week_name] = data
        final_result = Customer_week_fn(week_names, week_dict, {}, func_name)
    elif _type == 'month':
        month_dict = {}
        month_names = []
        month_num = 0
        for month_na, month_va in zip(dates_list['month_names'], dates_list['month_dates']):
            month_name = month_na
            month_dates = month_va
            month_names.append(month_name)
            data = func_name(main_dates, prj_id, center_obj, level_structure_key, month_dates, request, _type)
            month_dict[month_name] = data
        final_result = Customer_week_fn(month_names, month_dict, {}, func_name)
    return final_result


def Customer_week_fn(week_names, productivity_list, final_productivity, function_name):
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
                        if function_name in [overall_external_accur_trends, overall_internal_accur_trends,Probe_overall_accuracy]:
                            final_productivity[prod_key].append(100)
                        else:
                            final_productivity[prod_key].append(0)
            else:
                for vol_key, vol_values in final_productivity.iteritems():
                    if function_name in [overall_external_accur_trends, overall_internal_accur_trends,Probe_overall_accuracy ]:
                        final_productivity[vol_key].append(100)
                    else:
                        final_productivity[vol_key].append(0)

    return final_productivity


def min_max_num(int_value_range, result_name):
    min_max_dict = {}
    if len(int_value_range) > 0 and (
        result_name in ["external_error_count", "produc_vs_targ", "external_error_acc", "overall_external_count",
                        "internal_error_acc", "overall_tat", "prb_overall_ext","ext_acc_agent_details","int_acc_agent_details"]):
        values_list = []
        data = int_value_range.values()
        for value in data:
            values_list = values_list + value
        if len(values_list) > 0:
            if (min(values_list) > 2):
                min_value = (min(values_list) - 2)
                max_value = (max(values_list) + 2)
            else:
                min_value = 0
                max_value = (max(values_list) + 2)
        else:
            min_value, max_value = 0, 0
    else:
        min_value, max_value = 0, 0
    min_max_dict['min_value'] = min_value
    min_max_dict['max_value'] = max_value
    return min_max_dict


def Level_Order(level_structure_key):
    if len(level_structure_key) > 2:
        keyorder = ['sub_project', 'work_packet', 'sub_packet']
        level_order = sorted(level_structure_key.items(), key=lambda i: keyorder.index(i[0]))
        for k in level_order:
            if k[1] != 'All':
                level = k[0]

    elif len(level_structure_key) == 2:
        if level_structure_key.has_key('sub_project'):
            keyorder = ['sub_project', 'work_packet']
            level_order = sorted(level_structure_key.items(), key=lambda i: keyorder.index(i[0]))
            for k in level_order:
                if k[1] != "All":
                    level = k[0]

        else:
            keyorder = ['work_packet', 'sub_packet']
            level_order = sorted(level_structure_key.items(), key=lambda i: keyorder.index(i[0]))
            for k in level_order:
                if k[1] != "All":
                    level = k[0]

    else:
        for k, v in level_structure_key.iteritems():
            if v != "All":
                level = k

    return level


def External_Error_proj(request):
    result_name = 'external_error_count'
    function_name = external_count_cal
    model_name = 'Externalerrors'
    result = generate_day_week_month_format(request, result_name, function_name, model_name)
    return result


def Production_vs_Target(request):
    final_dict = {}
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
    result_name = 'produc_vs_targ'
    result = Production_target(main_dates, prj_id, center, level_structure_key, main_dates, request, _type)
    final_dict[result_name] = graph_data_alignment_color(result['data'], 'data', level_structure_key, prj_id, center)
    final_dict['date'] = result['date']
    final_dict['min_max'] = min_max_num(result['data'], result_name)
    final_dict['type'] = main_data_dict['type']
    final_dict['is_annotation'] = annotation_check(request)
    return json_HttpResponse(final_dict)


def Overall_external_accur(request):
    result_name = 'external_error_acc'
    function_name = overall_external_accur_trends
    model_name = 'RawTable'
    result = generate_day_week_month_format(request, result_name, function_name, model_name)
    return result


def Probe_overall_external_accur(request):
    result_name = 'prb_overall_ext'
    function_name = Probe_overall_accuracy
    model_name = 'Externalerrors'
    result = generate_day_week_month_format(request, result_name, function_name, model_name)
    return result


def Overall_External_Error(request):
    result_name = 'overall_external_count'
    function_name = overall_ext_count
    model_name = 'Externalerrors'
    result = generate_day_week_month_format(request, result_name, function_name, model_name)
    return result


def Overall_internal_accur(request):
    result_name = 'internal_error_acc'
    function_name = overall_internal_accur_trends
    model_name = 'RawTable'
    result = generate_day_week_month_format(request, result_name, function_name, model_name)
    return result


def Overall_TAT(request):
    result_name = 'overall_tat'
    function_name = overall_tat_graph
    model_name = 'TatTable'
    result = generate_day_week_month_format(request, result_name, function_name, model_name)
    return result


def Agent_wise_production(request):
    final_dict = {}
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
    result_name = 'agent_wise_production'
    result = agentwise_production(main_dates, prj_id, center, level_structure_key, request, _type)
    final_dict[result_name] = graph_data_alignment_color(result['data'], 'data', level_structure_key, prj_id, center)
    final_dict['date'] = result['date'] 
    final_dict['min_max'] = min_max_num(result['data'],result_name)
    final_dict['type'] = main_data_dict['type']
    final_dict['is_annotation'] = annotation_check(request)
    return json_HttpResponse(final_dict)



def hash_remover(x):
    if "#<>#" in x:
        r = x.split("#<>#")
    else:
        r = [x]
    return r


def Internal_Acc_Agents(request):
    final_dict = {}
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
    result_name = 'int_acc_agent_details'
    result = agent_int_acc(main_dates, prj_id, center, level_structure_key, request, _type)
    final_dict[result_name] = graph_data_alignment_color(result['data'], 'data', level_structure_key, prj_id, center)
    final_dict['date'] = result['date']    
    final_dict['min_max'] = min_max_num(result['data'],result_name)
    final_dict['type'] = main_data_dict['type']
    final_dict['is_annotation'] = annotation_check(request)
    return json_HttpResponse(final_dict)


def External_Acc_Agents(request):
    final_dict = {}
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
    result_name = 'ext_acc_agent_details'
    result = agent_ext_acc(main_dates, prj_id, center, level_structure_key, request, _type)
    final_dict[result_name] = graph_data_alignment_color(result['data'], 'data', level_structure_key, prj_id, center)
    final_dict['date'] = result['date']    
    final_dict['min_max'] = min_max_num(result['data'],result_name)
    final_dict['type'] = main_data_dict['type']
    final_dict['is_annotation'] = annotation_check(request)
    return json_HttpResponse(final_dict)



def external_count_cal(main_dates, prj_id, center, level_structure_key, dates_list, request, _type):
    result = {}
    filter_params, _term = getting_required_params(level_structure_key, prj_id, center, dates_list)
    if _type == "day":
        if filter_params and _term:
            ext_full_query = Externalerrors.objects.filter(project=prj_id, center=center,
                                                           date__range=[main_dates[0], main_dates[-1]])
            ext_query = Externalerrors.objects.filter(**filter_params)
            date_pack = ext_full_query.order_by('date').values_list('date', flat=True).distinct()
            pack_list = ext_query.values_list('error_types', flat=True).distinct()
            pack_list = map(hash_remover, pack_list)
            pack_list = (list(chain.from_iterable(pack_list)))

            def lower(x):
                return x.lower().title()

            pack_list = map(lower, pack_list)
            pack_list = set(pack_list)

            exter_data = ext_query.order_by('date').values('date', 'error_types', 'error_values')

            result_ = OrderedDict()
            packet = []
            for date in date_pack:
                reslt = {}
                for x in exter_data:
                    if date == x['date']:
                        if "#<>#" in x["error_types"]:
                            err_k = x['error_types'].split('#<>#')
                            err_v = x['error_values'].split('#<>#')
                            for k, v in zip(err_k, err_v):
                                K = k.lower().title()
                                if not reslt.has_key(K):
                                    reslt[K] = int(v)
                                else:
                                    reslt[K] = int(reslt[K]) + int(v)
                        else:
                            K = x['error_types'].lower().title()
                            if not reslt.has_key(K):
                                reslt[K] = int(x['error_values'])
                            else:
                                reslt[K] = int(reslt[K]) + int(x['error_values'])

                result_[date] = reslt
            out = {}
            for date in date_pack:
                packet_list = []
                content_list = []
                for val in result_.iteritems():
                    if date == val[0]:
                        for k, v in val[1].iteritems():
                            if not out.has_key(k):
                                out[k] = [v]
                            else:
                                out[k].append(v)
                            packet_list.append(k)
                            content_list.append(v)

                if len(packet_list) > 0:
                    for pack in pack_list:
                        if pack not in packet_list:
                            if not out.has_key(pack):
                                out[pack] = [0]
                            else:
                                out[pack].append(0)

                if len(content_list) == 0:
                    for pack in pack_list:
                        if not out.has_key(pack):
                            out[pack] = [0]
                        else:
                            out[pack].append(0)

            return out

    elif _type in ["week", "month"]:
        ext_full_query = Externalerrors.objects.filter(project=prj_id, center=center,
                                                       date__range=[main_dates[0], main_dates[-1]])
        ext_query = Externalerrors.objects.filter(**filter_params)

        ex_qy = ext_query.values('error_types', 'error_values')
        pack_lst = ext_full_query.values_list('error_types', flat=True).distinct()
        pack_list = map(hash_remover, pack_lst)
        pack_list = (list(chain.from_iterable(pack_list)))

        def lower(x):
            return x.lower().title()

        pack_list = map(lower, pack_list)
        pack_list = set(pack_list)
        out = {}
        for ext in ex_qy:
            if '#<>#' in ext['error_types']:
                err_k = ext['error_types'].split('#<>#')
                err_v = ext['error_values'].split('#<>#')
                for k, v in zip(err_k, err_v):
                    K = k.lower().title()
                    if not out.has_key(K):
                        out[K] = int(v)
                    else:
                        out[K] = int(out[K]) + int(v)
            else:
                K = ext['error_types'].lower().title()
                if not out.has_key(K):
                    out[K] = int(ext['error_values'])
                else:
                    out[K] = int(out[K]) + int(ext['error_values'])

        res = {}
        packet_list = []
        for k, v in out.iteritems():
            if not res.has_key(k):
                res[k] = v
            else:
                res[k].append(v)
            packet_list.append(k)
        if len(packet_list) > 0:
            for pack in pack_list:
                if pack not in packet_list:
                    res[pack] = 0

        return res


def Production_target(main_dates, prj_id, center, level_structure_key, dates_list, request, _type):
    result, prod_dict, targ_dict = OrderedDict(), OrderedDict(), OrderedDict()
    prod_val, packets, targ_val = [], [], []
    filter_params, _term = getting_required_params(level_structure_key, prj_id, center, dates_list)
    targets, targ_query, raw_query, raw_data, _type, targ_term = get_target_query_format(level_structure_key, prj_id,
                                                                                         center, dates_list)
    if ((filter_params and targ_query) and (targ_term and _term)):
        prod_full_query = RawTable.objects.filter(project=prj_id, center=center,
                                                  date__range=[main_dates[0], main_dates[-1]])
        prod_query = RawTable.objects.filter(**filter_params)
        dates = prod_full_query.values_list('date', flat=True).distinct()
        prod_packet = prod_query.values_list(_term, flat=True).distinct()
        prod_values = prod_query.order_by(_term).values_list(_term).annotate(Work_done=Sum('per_day'))
        prod_values = filter(lambda x: x[0] != '', prod_values)
        tar_pack = targ_query.order_by(_term).values_list(_term, flat=True).distinct()
        tar_pack = filter(lambda x: x != '', tar_pack)

        def lower(x):
            return x.lower().title()

        tar_pack = map(lower, tar_pack)
        prod_packet = map(lower, prod_packet)
        full_packet = prod_packet + tar_pack
        if prod_values:
            for val in prod_values:
                pack = val[0].lower().title()
                if prod_dict.has_key(pack):
                    prod_dict[pack].append(val[1])
                else:
                    prod_dict[pack] = [val[1]]

            for pack in full_packet:
                if pack not in prod_dict.keys():
                    prod_dict[pack] = [0]

            prod_dict = collections.OrderedDict(sorted(prod_dict.items()))
            for key, val in prod_dict.iteritems():
                packets.append(key)
                val = sum(val)
                prod_val.append(val)

        if targ_query:
            targ_values = targ_query.values_list(targ_term).annotate(target=Sum('target_value'))
            targ_values = filter(lambda x: x[0] != '', targ_values)
            headc_query = Headcount.objects.filter(**filter_params).values_list(_term).annotate(
                head_c=Sum('billable_agents'))
            if _type == "FTE Target":
                for head_c in headc_query:
                    for tal in targ_values:
                        pack = tal[0].lower().title()
                        pack1 = head_c[0].lower().title()
                        if pack == pack1:
                            tar_val = tal[1] * head_c[1]
                            tar_val = float("%.2f" % round(tar_val))
                            if targ_dict.has_key(pack):
                                targ_dict[pack].append(tar_val)
                            else:
                                targ_dict[pack] = [tar_val]

            else:
                for tal in targ_values:
                    pack = tal[0].lower().title()
                    targ_val = float("%.2f" % round(tal[1]))
                    if targ_dict.has_key(pack):
                        targ_dict[pack].append(tar_val)
                    else:
                        targ_dict[pack] = [tar_val]

            for pack in full_packet:
                if pack not in targ_dict.keys():
                    targ_dict[pack] = [0]

            targ_dict = collections.OrderedDict(sorted(targ_dict.items()))
            for key, val in targ_dict.iteritems():
                packets.append(key)
                val = sum(val)
                targ_val.append(val)

    result_temp = {}
    result_temp['Production'] = prod_val
    result_temp['Target'] = targ_val
    result['data'] = result_temp
    result['date'] = list(set(packets))
    return result


def overall_external_accur_trends(main_dates, prj_id, center, level_structure_key, dates_list, request, _type):
    result_dict, produc_lst = {}, []
    filter_params, _term = getting_required_params(level_structure_key, prj_id, center, dates_list)
    if _term and filter_params:
        if _type == "day":
            exter_acc_query = Externalerrors.objects.filter(project=prj_id, center=center,
                                                            date__range=[main_dates[0], main_dates[-1]])
            dates = exter_acc_query.values_list('date', flat=True).distinct()
            query_values = Externalerrors.objects.filter(**filter_params)
            if all('All' in x for x in level_structure_key.values()):
                data_values = query_values.order_by('date').values_list('date').annotate(
                    total=Sum('total_errors'), audit=Sum('audited_errors'))
                data_values = filter(lambda e: e[1] != u'', data_values)
                rawtable = RawTable.objects.filter(**filter_params)
                raw_packets = rawtable.order_by('date').values_list('date').annotate(prod=Sum('per_day'))
                raw_packets = filter(lambda e: e[1] != u'', raw_packets)
                f_pack = rawtable.values_list(_term, flat=True).distinct()
                e_pack = query_values.values_list(_term,flat=True).distinct()
                filter_pack = filter(lambda r: r not in e_pack, f_pack)
                q_v = query_values.order_by('date').filter(audited_errors=0).values('date',_term).distinct()
                if _term=='sub_project':
                    res = {}
                    for dat in dates:
                        val = []
                        for q in q_v:
                            if dat == q['date']:
                                val.append(q['sub_project'])
                        out = rawtable.filter(date=dat,sub_project__in=val).aggregate(prod=Sum('per_day'))
                        res[dat] = out['prod']
                    raw_val = rawtable.filter(sub_project__in=filter_pack).distinct()

                elif _term=='work_packet':
                    res = {}
                    for dat in dates:
                        val = []
                        for q in q_v:
                            if dat == q['date']:
                                val.append(q['work_packet'])
                        out = rawtable.filter(date=dat,work_packet__in=val).aggregate(prod=Sum('per_day'))
                        res[dat] = out['prod']
                    raw_val = rawtable.filter(work_packet__in=filter_pack).distinct()
                raw_dates = rawtable.order_by('date').values_list('date',flat=True).distinct()
                if prj_id in [30, 112, 160, 129, 159, 117, 180, 181, 182, 123, 113, 162, 114, 126, 119, 115, 118, 130, 127,
                                154, 158, 121, 156, 161, 116, 132]:
                    if raw_packets:
                        for date in raw_dates:
                            if date in dates:
                                for data in data_values:
                                    if date == data[0]:
                                        if data[1] > 0:
                                            out = raw_val.filter(date=str(data[0])).aggregate(prod=Sum('per_day'))
                                            val = res[data[0]]
                                            if out['prod'] == None:
                                                out['prod'] = 0
                                            if val == None:
                                                val = 0
                                            out_1 = data[1] + out['prod'] + val
                                            value = (float(data[2]) / float(out_1)) * 100
                                            accuracy = 100 - value
                                            accuracy = float('%.2f' % round(accuracy, 2))
                                        elif data[1] == 0:
                                            for prod_val in raw_packets:
                                                if date == prod_val[0]:
                                                    value = (float(data[2]) / float(prod_val[1])) * 100
                                                    accuracy = 100 - value
                                                    accuracy = float('%.2f' % round(accuracy, 2))
                                        else:
                                            accuracy = 100
                            else:
                                accuracy = 100
                            produc_lst.append(accuracy)
                        result_dict['Internal Accuracy'] = produc_lst
                else:
                    if data_values and raw_packets:
                        for date in dates:
                            for data in data_values:
                                    if date == data[0]:
                                        if data[1] > 0:
                                            out = raw_val.filter(date=str(data[0])).aggregate(prod=Sum('per_day'))
                                            val = res[data[0]]
                                            if out['prod'] == None:
                                                out['prod'] = 0
                                            if val == None:
                                                val = 0
                                            out_1 = data[1] + out['prod'] + val
                                            value = (float(data[2]) / float(out_1)) * 100
                                            accuracy = 100 - value
                                            accuracy = float('%.2f' % round(accuracy, 2))
                                        elif data[1] == 0:
                                            for prod_val in raw_packets:
                                                if date == prod_val[0]:
                                                    value = (float(data[2]) / float(prod_val[1])) * 100
                                                    accuracy = 100 - value
                                                    accuracy = float('%.2f' % round(accuracy, 2))
                                        else:
                                            accuracy = 100
                            produc_lst.append(accuracy)
                        result_dict['External Accuracy'] = produc_lst
            else:
                level = Level_Order(level_structure_key)
                data_values = query_values.values_list('date', level).annotate(total=Sum('total_errors'),
                                                                               audit=Sum('audited_errors'))
                data_values = filter(lambda e: e[1] != u'', data_values)
                rawtable = RawTable.objects.filter(**filter_params)
                raw_packets = rawtable.values_list('date', level).annotate(prod=Sum('per_day'))
                raw_packets = filter(lambda e: e[1] != u'', raw_packets)
                packets = query_values.values_list(level, flat=True).distinct()
                r_packets = rawtable.values_list(level, flat=True).distinct()
                def low(x):  return x.lower().title()
                r_packets = map(low, r_packets)
                r_dates = rawtable.values_list('date', flat=True).distinct()
                if prj_id in [30, 112, 160, 129, 159, 117, 180, 181, 182, 123, 113, 162, 114, 126, 119, 115, 118, 130, 127,
                                154, 158, 121, 156, 161, 116, 132]:
                    if raw_packets:
                        for date in r_dates:
                            data_list = []
                            for data in data_values:
                                if date == data[0]:
                                    pack = data[1].lower().title()
                                    if data[2] > 0:
                                        value = (float(data[3]) / float(data[2])) * 100
                                        accuracy = 100 - value
                                        accuracy = float('%.2f' % round(accuracy, 2))
                                    elif data[2] == 0:
                                        if (pack in r_packets) and (data[0] in r_dates):
                                            for prod_val in raw_packets:
                                                if date == prod_val[0] and pack == prod_val[1].lower().title():
                                                    value = (float(data[3]) / float(prod_val[2])) * 100
                                                    accuracy = 100 - value
                                                    accuracy = float('%.2f' % round(accuracy, 2))
                                    else:
                                        accuracy = 100
                                    if not result_dict.has_key(pack):
                                        result_dict[pack] = [accuracy]
                                    else:
                                        result_dict[pack].append(accuracy)
                                    data_list.append(accuracy)
                            if len(data_list) == 0:
                                for pack in r_packets:
                                    pack = pack.lower().title()
                                    if not result_dict.has_key(pack):
                                        result_dict[pack] = [100]
                                    else:
                                        result_dict[pack].append(100)
                else:
                    if data_values and raw_packets:
                        for date in dates:
                            data_list = []
                            for data in data_values:
                                if date == data[0]:
                                    pack = data[1].lower().title()
                                    if data[2] > 0:
                                        value = (float(data[3]) / float(data[2])) * 100
                                        accuracy = 100 - value
                                        accuracy = float('%.2f' % round(accuracy, 2))
                                    elif data[2] == 0:
                                        if (pack in r_packets) and (data[0] in r_dates):
                                            for prod_val in raw_packets:
                                                if date == prod_val[0] and pack == prod_val[1].lower().title():
                                                    value = (float(data[3]) / float(prod_val[2])) * 100
                                                    accuracy = 100 - value
                                                    accuracy = float('%.2f' % round(accuracy, 2))
                                        else:
                                            accuracy = 100
                                    else:
                                        accuracy = 100

                                    if not result_dict.has_key(pack):
                                        result_dict[pack] = [accuracy]
                                    else:
                                        result_dict[pack].append(accuracy)
                                    data_list.append(accuracy)

                            if len(data_list) == 0:
                                for pack in packets:
                                    pack = pack.lower().title()
                                    if not result_dict.has_key(pack):
                                        result_dict[pack] = [100]
                                    else:
                                        result_dict[pack].append(100)


        elif _type in ["week", "month"]:
            ext_full_query = Externalerrors.objects.filter(project=prj_id, center=center,
                                                           date__range=[main_dates[0], main_dates[-1]])
            ext_query = Externalerrors.objects.filter(**filter_params)
            rawtable = RawTable.objects.filter(**filter_params)
            if all('All' in x for x in level_structure_key.values()):
                exter_qy = ext_query.aggregate(audited_errors=Sum('audited_errors'),
                                               total_errors=Sum('total_errors'))
                if exter_qy.values()[0] == None and  exter_qy.values()[1] == None:
                    exter_qy = {}                
                
                f_pack = rawtable.values_list(_term, flat=True).distinct()
                e_pack = ext_query.values_list(_term,flat=True).distinct()
                filter_pack = filter(lambda r: r not in e_pack, f_pack)
                q_v = ext_query.filter(audited_errors=0).values_list(_term,flat=True).distinct()
                fil = list(q_v)+filter_pack
                if _term == 'sub_project':
                    raw_val = rawtable.filter(sub_project__in=fil).aggregate(prod=Sum('per_day'))
                elif _term == 'work_packet':
                    raw_val = rawtable.filter(work_packet__in=fil).aggregate(prod=Sum('per_day'))
                raw_pack = rawtable.aggregate(prod=Sum('per_day'))
                if prj_id in [30, 112, 160, 129, 159, 117, 180, 181, 182, 123, 113, 162, 114, 126, 119, 115, 118, 130, 127,
                                154, 158, 121, 156, 161, 116, 132]:
                    if raw_pack:
                        if exter_qy:
                            if exter_qy['audited_errors'] > 0:
                                if raw_val['prod'] == None:
                                    raw_val['prod'] = 0
                                value = (float(exter_qy['total_errors'])/float(exter_qy['audited_errors']+raw_val['prod'])) * 100
                                accuracy = 100 - value
                                accuracy = float('%.2f' % round(accuracy, 2))
                            elif exter_qy['audited_errors'] == 0:
                                value = (float(exter_qy['total_errors'])/float(raw_pack['prod'])) * 100
                                accuracy = 100 - value
                                accuracy = float('%.2f' % round(accuracy, 2))
                            else:
                                accuracy = 100
                        else:
                            accuracy = 100
                        result_dict['External Accuracy'] = accuracy
                else:
                    if exter_qy and raw_pack:
                        if exter_qy['audited_errors'] > 0:
                            if raw_val['prod'] == None:
                                raw_val['prod'] = 0
                            value = (float(exter_qy['total_errors'])/float(exter_qy['audited_errors']+raw_val['prod'])) * 100
                            accuracy = 100 - value
                            accuracy = float('%.2f' % round(accuracy, 2))
                        elif exter_qy['audited_errors'] == 0:
                            value = (float(exter_qy['total_errors'])/float(raw_pack['prod'])) * 100
                            accuracy = 100 - value
                            accuracy = float('%.2f' % round(accuracy, 2))
                        else:
                            accuracy = 100
                        result_dict['External Accuracy'] = accuracy

            else:
                level = Level_Order(level_structure_key)
                raw_packets = rawtable.values_list(level).annotate(prod=Sum('per_day'))                
                ext_qy = ext_query.values_list(level).annotate(audited_errors=Sum('audited_errors'),
                                                               total_errors=Sum('total_errors'))
                pack_lst = ext_full_query.values_list(level, flat=True).distinct()
                ext_qy = filter(lambda t: t[1] != u'', ext_qy)
                raw_packets = filter(lambda e: e[1] != u'', raw_packets)
                raw_list = rawtable.values_list(level, flat=True).distinct()
                def case(x): return x.lower().title()
                raw_list = map(case, raw_list)
                if prj_id in [30, 112, 160, 129, 159, 117, 180, 181, 182, 123, 113, 162, 114, 126, 119, 115, 118, 130, 127,
                                154, 158, 121, 156, 161, 116, 132]:
                    if raw_packets:
                        if ext_qy:
                            for data in ext_qy:
                                pack = data[0].lower().title()
                                accuracy = 100
                                if data[2] > 0:
                                    value = (float(data[1]) / float(data[2])) * 100
                                    accuracy = 100 - value
                                    accuracy = float('%.2f' % round(accuracy, 2))
                                elif data[2] == 0:
                                    if pack in raw_list:
                                        for prod_val in raw_packets:
                                            if pack == prod_val[0].lower().title():
                                                value = (float(data[1]) / float(prod_val[1])) * 100
                                                accuracy = 100 - value
                                                accuracy = float('%.2f' % round(accuracy, 2))
                                    else:
                                        accuracy = 100
                                else:
                                    accuracy = 100

                            result_dict[pack] = accuracy
                        else:
                            for r_pack in raw_packets:
                                pac_k = r_pack[0].lower().title()
                                if not result_dict.has_key(pac_k):
                                    result_dict[pac_k] = 100
                else:
                    if ext_qy and raw_packets:
                        for data in ext_qy:
                            pack = data[0].lower().title()
                            accuracy = 100
                            if data[2] > 0:
                                value = (float(data[1]) / float(data[2])) * 100
                                accuracy = 100 - value
                                accuracy = float('%.2f' % round(accuracy, 2))
                            elif data[2] == 0:
                                if pack in raw_list:
                                    for prod_val in raw_packets:
                                        if pack == prod_val[0].lower().title():
                                            value = (float(data[1]) / float(prod_val[1])) * 100
                                            accuracy = 100 - value
                                            accuracy = float('%.2f' % round(accuracy, 2))
                                else:
                                    accuracy = 100
                            else:
                                accuracy = 100

                            result_dict[pack] = accuracy

        return result_dict



def overall_ext_count(main_dates, prj_id, center, level_structure_key, dates_list, request, _type):
    result = {}
    filter_params, _term = getting_required_params(level_structure_key, prj_id, center, dates_list)
    if filter_params and _term:
        if _type == "day":
            ext_full_query = Externalerrors.objects.filter(project=prj_id, center=center,
                                                           date__range=[main_dates[0], main_dates[-1]])
            ext_query = Externalerrors.objects.filter(**filter_params)
            date_pack = ext_full_query.order_by('date').values_list('date', flat=True).distinct()
            ext_data = ext_query.order_by('date').filter(error_values__gt=0).values_list('date').annotate(
                total_errors=Sum('total_errors'))
            data = []
            ext_data = filter(lambda t: t[1] != u'', ext_data)
            if ext_data:
                for date in date_pack:
                    content_list = []
                    for ext_v in ext_data:
                        if date == ext_v[0]:
                            if ext_v[1] != 'None':
                                if not result.has_key('Error Count'):
                                    result['Error Count'] = [ext_v[1]]
                                else:
                                    result['Error Count'].append(ext_v[1])
                                content_list.append(ext_v[1])

                    if len(content_list) == 0:
                        if not result.has_key('Error Count'):
                            result['Error Count'] = [0]
                        else:
                            result['Error Count'].append(0)

        elif _type in ["week", "month"]:
            ext_full_query = Externalerrors.objects.filter(project=prj_id, center=center,
                                                           date__range=[main_dates[0], main_dates[-1]])
            ext_query = Externalerrors.objects.filter(**filter_params)
            ext_qy = ext_query.aggregate(total_errors=Sum('total_errors'))
            result = {}
            if ext_qy['total_errors'] != None:
                result['Error Count'] = ext_qy['total_errors']
            else:
                result['Error Count'] = 0

    return result


def overall_internal_accur_trends(main_dates, prj_id, center, level_structure_key, dates_list, request, _type):
    result_dict, produc_lst = {}, []
    filter_params, _term = getting_required_params(level_structure_key, prj_id, center, dates_list)
    if _term and filter_params:
        if _type == "day":
            exter_acc_query = Internalerrors.objects.filter(project=prj_id, center=center,
                                                            date__range=[main_dates[0], main_dates[-1]])
            dates = exter_acc_query.values_list('date', flat=True).distinct()
            query_values = Internalerrors.objects.filter(**filter_params)
            if all('All' in x for x in level_structure_key.values()):
                data_values = query_values.order_by('date').values_list('date').annotate(
                    total=Sum('total_errors'), audit=Sum('audited_errors'))
                data_values = filter(lambda e: e[1] != u'', data_values)
                rawtable = RawTable.objects.filter(**filter_params)
                raw_packets = rawtable.order_by('date').values_list('date').annotate(prod=Sum('per_day'))
                raw_packets = filter(lambda e: e[1] != u'', raw_packets)
                f_pack = rawtable.values_list(_term, flat=True).distinct()
                e_pack = query_values.values_list(_term, flat=True).distinct()
                filter_pack = filter(lambda r: r not in e_pack, f_pack)
                q_v = query_values.order_by('date').filter(audited_errors=0).values('date', _term).distinct()
                if _term == 'sub_project':
                    res = {}
                    for dat in dates:
                        val = []
                        for q in q_v:
                            if dat == q['date']:
                                val.append(q['sub_project'])
                        out = rawtable.filter(date=dat, sub_project__in=val).aggregate(prod=Sum('per_day'))
                        res[dat] = out['prod']
                    raw_val = rawtable.filter(sub_project__in=filter_pack).distinct()
                elif _term == 'work_packet':
                    res = {}
                    for dat in dates:
                        val = []
                        for q in q_v:
                            if dat == q['date']:
                                val.append(q['work_packet'])
                        out = rawtable.filter(date=dat, work_packet__in=val).aggregate(prod=Sum('per_day'))
                        res[dat] = out['prod']
                    raw_val = rawtable.filter(work_packet__in=filter_pack).distinct()
                raw_dates = rawtable.order_by('date').values_list('date',flat=True).distinct()
                if prj_id in [30, 112, 160, 129, 159, 117, 180, 181, 182, 123, 113, 162, 114, 126, 119, 115, 118, 130, 127,
                                154, 158, 121, 156, 161, 116, 132]:
                    if raw_packets:
                        for date in raw_dates:
                            if date in dates:
                                for data in data_values:
                                    if date == data[0]:
                                        if data[1] > 0:
                                            out = raw_val.filter(date=str(data[0])).aggregate(prod=Sum('per_day'))
                                            val = res[data[0]]
                                            if out['prod'] == None:
                                                out['prod'] = 0
                                            if val == None:
                                                val = 0
                                            out_1 = data[1] + out['prod'] + val
                                            value = (float(data[2]) / float(out_1)) * 100
                                            accuracy = 100 - value
                                            accuracy = float('%.2f' % round(accuracy, 2))
                                        elif data[1] == 0:
                                            for prod_val in raw_packets:
                                                if date == prod_val[0]:
                                                    value = (float(data[2]) / float(prod_val[1])) * 100
                                                    accuracy = 100 - value
                                                    accuracy = float('%.2f' % round(accuracy, 2))
                                        else:
                                            accuracy = 100
                            else:
                                accuracy = 100
                            produc_lst.append(accuracy)
                        result_dict['Internal Accuracy'] = produc_lst
                else:
                    if data_values and raw_packets:
                        for date in dates:
                            for data in data_values:
                                    if date == data[0]:
                                        if data[1] > 0:
                                            out = raw_val.filter(date=str(data[0])).aggregate(prod=Sum('per_day'))
                                            val = res[data[0]]
                                            if out['prod'] == None:
                                                out['prod'] = 0
                                            if val == None:
                                                val = 0
                                            out_1 = data[1] + out['prod'] + val
                                            value = (float(data[2]) / float(out_1)) * 100
                                            accuracy = 100 - value
                                            accuracy = float('%.2f' % round(accuracy, 2))
                                        elif data[1] == 0:
                                            for prod_val in raw_packets:
                                                if date == prod_val[0]:
                                                    value = (float(data[2]) / float(prod_val[1])) * 100
                                                    accuracy = 100 - value
                                                    accuracy = float('%.2f' % round(accuracy, 2))
                                        else:
                                            accuracy = 100
                            produc_lst.append(accuracy)
                        result_dict['Internal Accuracy'] = produc_lst

            else:
                level = Level_Order(level_structure_key)
                data_values = query_values.values_list('date', level).annotate(total=Sum('total_errors'),
                                                                               audit=Sum('audited_errors'))
                data_values = filter(lambda e: e[1] != u'', data_values)
                rawtable = RawTable.objects.filter(**filter_params)
                raw_packets = rawtable.values_list('date', level).annotate(prod=Sum('per_day'))
                raw_packets = filter(lambda e: e[1] != u'', raw_packets)
                packets = query_values.values_list(level, flat=True).distinct()
                r_dates = rawtable.values_list('date', flat=True).distinct()
                r_packets = rawtable.values_list(level, flat=True).distinct()
                def low(x): return x.lower().title()
                r_packets = map(low, r_packets)
                r_dates = rawtable.values_list('date', flat=True).distinct()
                if prj_id in [30, 112, 160, 129, 159, 117, 180, 181, 182, 123, 113, 162, 114, 126, 119, 115, 118, 130, 127,
                                154, 158, 121, 156, 161, 116, 132]:
                    if raw_packets:
                        for date in r_dates:
                            data_list = []
                            for data in data_values:
                                if date == data[0]:
                                    pack = data[1].lower().title()
                                    if data[2] > 0:
                                        value = (float(data[3]) / float(data[2])) * 100
                                        accuracy = 100 - value
                                        accuracy = float('%.2f' % round(accuracy, 2))
                                    elif data[2] == 0:
                                        if (pack in r_packets) and (data[0] in r_dates):
                                            for prod_val in raw_packets:
                                                if date == prod_val[0] and pack == prod_val[1].lower().title():
                                                    value = (float(data[3]) / float(prod_val[2])) * 100
                                                    accuracy = 100 - value
                                                    accuracy = float('%.2f' % round(accuracy, 2))
                                    else:
                                        accuracy = 100

                                    if not result_dict.has_key(pack):
                                        result_dict[pack] = [accuracy]
                                    else:
                                        result_dict[pack].append(accuracy)
                                    data_list.append(accuracy)

                            if len(data_list) == 0:
                                for pack in r_packets:
                                    pack = pack.lower().title()
                                    if not result_dict.has_key(pack):
                                        result_dict[pack] = [100]
                                    else:
                                        result_dict[pack].append(100)
                else:
                    if data_values and raw_packets:
                        for date in dates:
                            data_list = []
                            for data in data_values:
                                if date == data[0]:
                                    pack = data[1].lower().title()
                                    if data[2] > 0:
                                        value = (float(data[3]) / float(data[2])) * 100
                                        accuracy = 100 - value
                                        accuracy = float('%.2f' % round(accuracy, 2))
                                    elif data[2] == 0:
                                        if (pack in r_packets) and (data[0] in r_dates):
                                            for prod_val in raw_packets:
                                                if date == prod_val[0] and pack == prod_val[1].lower().title():
                                                    value = (float(data[3]) / float(prod_val[2])) * 100
                                                    accuracy = 100 - value
                                                    accuracy = float('%.2f' % round(accuracy, 2))
                                        else:
                                            accuracy = 100
                                    else:
                                        accuracy = 100

                                    if not result_dict.has_key(pack):
                                        result_dict[pack] = [accuracy]
                                    else:
                                        result_dict[pack].append(accuracy)
                                    data_list.append(accuracy)

                            if len(data_list) == 0:
                                for pack in packets:
                                    pack = pack.lower().title()
                                    if not result_dict.has_key(pack):
                                        result_dict[pack] = [100]
                                    else:
                                        result_dict[pack].append(100)



        elif _type in ["week", "month"]:
            ext_full_query = Internalerrors.objects.filter(project=prj_id, center=center,
                                                           date__range=[main_dates[0], main_dates[-1]])
            ext_query = Internalerrors.objects.filter(**filter_params)
            rawtable = RawTable.objects.filter(**filter_params)
            if all('All' in x for x in level_structure_key.values()):
                ext_qy = ext_query.aggregate(audited_errors=Sum('audited_errors'),
                                             total_errors=Sum('total_errors'))
                if ext_qy.values()[0] == None and ext_qy.values()[1] == None:
                    ext_qy = {}               
                
                f_pack = rawtable.values_list(_term, flat=True).distinct()
                e_pack = ext_query.values_list(_term, flat=True).distinct()
                filter_pack = filter(lambda r: r not in e_pack, f_pack)
                q_v = ext_query.filter(audited_errors=0).values_list(_term, flat=True).distinct()
                fil = list(q_v) + filter_pack
                if _term == 'sub_project':
                    raw_val = rawtable.filter(sub_project__in=fil).aggregate(prod=Sum('per_day'))
                elif _term == 'work_packet':
                    raw_val = rawtable.filter(work_packet__in=fil).aggregate(prod=Sum('per_day'))
                raw_packets = rawtable.aggregate(prod=Sum('per_day'))
                if prj_id in [30, 112, 160, 129, 159, 117, 180, 181, 182, 123, 113, 162, 114, 126, 119, 115, 118, 130, 127,
                                154, 158, 121, 156, 161, 116, 132]:
                    if raw_packets:
                        if ext_qy:
                            if ext_qy['audited_errors'] > 0:
                                if raw_val['prod'] == None:
                                    raw_val['prod'] = 0
                                value = (float(ext_qy['total_errors']) / float(ext_qy['audited_errors'] + raw_val['prod'])) * 100
                                accuracy = 100 - value
                                accuracy = float('%.2f' % round(accuracy, 2))
                            elif ext_qy['audited_errors'] == 0:
                                value = (float(ext_qy['total_errors']) / float(raw_packets['prod'])) * 100
                                accuracy = 100 - value
                                accuracy = float('%.2f' % round(accuracy, 2))
                            else:
                                accuracy = 100
                        else:
                            accuracy = 100

                        result_dict['Internal Accuracy'] = accuracy
                else:
                    if ext_qy and raw_packets:
                        if ext_qy['audited_errors'] > 0:
                            if raw_val['prod'] == None:
                                raw_val['prod'] = 0
                            value = (float(ext_qy['total_errors']) / float(ext_qy['audited_errors'] + raw_val['prod'])) * 100
                            accuracy = 100 - value
                            accuracy = float('%.2f' % round(accuracy, 2))
                        elif ext_qy['audited_errors'] == 0:
                            value = (float(ext_qy['total_errors']) / float(raw_packets['prod'])) * 100
                            accuracy = 100 - value
                            accuracy = float('%.2f' % round(accuracy, 2))
                        else:
                            accuracy = 100
                        result_dict['Internal Accuracy'] = accuracy

            else:
                level = Level_Order(level_structure_key)
                raw_packets = rawtable.values_list(level).annotate(prod=Sum('per_day'))
                ext_qy = ext_query.values_list(level).annotate(audited_errors=Sum('audited_errors'),
                                                               total_errors=Sum('total_errors'))
                pack_lst = ext_full_query.values_list(level, flat=True).distinct()
                ext_qy = filter(lambda t: t[1] != u'', ext_qy)
                raw_packets = filter(lambda e: e[1] != u'', raw_packets)
                raw_list = rawtable.values_list(level, flat=True).distinct()
                def case(x):  return x.lower().title()
                raw_list = map(case, raw_list)
                if prj_id in [30, 112, 160, 129, 159, 117, 180, 181, 182, 123, 113, 162, 114, 126, 119, 115, 118, 130, 127,
                                154, 158, 121, 156, 161, 116, 132]:
                    if raw_packets:
                        if ext_qy:
                            for data in ext_qy:
                                pack = data[0].lower().title()
                                if data[2] > 0:
                                    value = (float(data[1]) / float(data[2])) * 100
                                    accuracy = 100 - value
                                    accuracy = float('%.2f' % round(accuracy, 2))
                                elif data[2] == 0:
                                    if pack in raw_list:
                                        for prod_val in raw_packets:
                                            if pack == prod_val[0].lower().title():
                                                value = (float(data[1]) / float(prod_val[1])) * 100
                                                accuracy = 100 - value
                                                accuracy = float('%.2f' % round(accuracy, 2))
                                    else:
                                        accuracy = 100
                                else:
                                    accuracy = 100
                                result_dict[pack] = accuracy
                        else:
                            for r_pack in raw_packets:
                                pac_k = r_pack[0].lower().title()
                                if not result_dict.has_key(pac_k):
                                    result_dict[pac_k] = 100
                else:
                    if ext_qy and raw_packets:
                        for data in ext_qy:
                            pack = data[0].lower().title()
                            if data[2] > 0:
                                value = (float(data[1]) / float(data[2])) * 100
                                accuracy = 100 - value
                                accuracy = float('%.2f' % round(accuracy, 2))
                            elif data[2] == 0:
                                if pack in raw_list:
                                    for prod_val in raw_packets:
                                        if pack == prod_val[0].lower().title():
                                            value = (float(data[1]) / float(prod_val[1])) * 100
                                            accuracy = 100 - value
                                            accuracy = float('%.2f' % round(accuracy, 2))
                                else:
                                    accuracy = 100
                            else:
                                accuracy = 100
                            result_dict[pack] = accuracy

        return result_dict



def overall_tat_graph(main_dates, prj_id, center, level_structure_key, dates_list, request, _type):
    result = {}
    filter_params, _term = getting_required_params(level_structure_key, prj_id, center, dates_list)
    if _term and filter_params:
        query_data = TatTable.objects.filter(**filter_params)
        if _type == "day":
            query_values = query_data.values_list('date').annotate(Met=Sum('met_count'), Not_met=Sum('non_met_count'))
            if query_values:
                raw_dates = TatTable.objects.filter(project=prj_id, center=center,
                                                    date__range=[main_dates[0], main_dates[-1]]). \
                    values_list('date', flat=True).distinct()
                for date in raw_dates:
                    for data in query_values:
                        if date == data[0]:
                            if data[1] + data[2] > 0:
                                value = (float(data[1]) / float(data[2] + data[1])) * 100
                                if result.has_key('TAT Value'):
                                    result['TAT Value'].append(round(value, 2))
                                else:
                                    result['TAT Value'] = [round(value, 2)]
                            else:
                                if result.has_key('TAT Value'):
                                    result['TAT Value'].append(0)
                                else:
                                    result['TAT Value'] = [0]

        elif _type in ["week", "month"]:
            query_values = query_data.aggregate(Met=Sum('met_count'), Not_met=Sum('non_met_count'))
            if query_values['Met'] != None:
                met_count = query_values['Met']
            else:
                met_count = 0
            if query_values['Not_met'] != None:
                not_met_count = query_values['Not_met']
            else:
                not_met_count = 0
            total_count = met_count + not_met_count
            if total_count > 0:
                tat_per_val = (met_count / total_count) * 100
                tat_per_val = float('%.2f' % round(tat_per_val, 2))
            else:
                tat_per_val = 0
            result['TAT Value'] = tat_per_val

    return result


def Probe_overall_accuracy(main_dates, prj_id, center, level_structure_key, dates_list, request, _type):
    result = OrderedDict()
    result_dict, product_lst = {}, []
    filter_params, _term = getting_required_params(level_structure_key, prj_id, center, dates_list)
    if _term and filter_params:
        if _type == "day":
            exter_acc_query = Externalerrors.objects.filter(project=prj_id, center=center,
                                                            date__range=[main_dates[0], main_dates[-1]])
            dates = exter_acc_query.values_list('date', flat=True).distinct()
            query_values = Externalerrors.objects.filter(**filter_params)            
            rawtable = RawTable.objects.filter(**filter_params)
            if all('All' in x for x in level_structure_key.values()):
                data_values = query_values.exclude(
                    work_packet__in=["BIFR", "CompanyCoordinates", "CreditRating", "Defaulter", "RPES", "Legal and CDR",
                                     "Auditor", "Financials", "PAN","Manupatra","Compliance"]) \
                    .order_by('date').values_list('date').annotate(total=Sum('total_errors') \
                                                                   , audit=Sum('audited_errors'))
                
                if query_values:
                    group_val1 = query_values.filter(
                        work_packet__in=["BIFR", "CompanyCoordinates", "CreditRating", "Defaulter", "RPES",
                                         "Legal and CDR","Manupatra","Compliance"]). \
                        order_by('date').values_list('date'). \
                        annotate(total=Sum('total_errors'), audit=Avg('audited_errors'))
                    
                    group_val2 = query_values.filter(work_packet__in=["Auditor", "Financials", "PAN"]). \
                        order_by('date').values_list('date'). \
                        annotate(total=Sum('total_errors'), audit=Avg('audited_errors'))
                    
                    r = query_values.values_list(_term, flat=True).distinct()
                    pac_dict = {}
                    if len(group_val1) > 0:
                        for e_val in data_values:
                            for grp1_v in group_val1:
                                if e_val[0] == grp1_v[0]:
                                    if not result.has_key(e_val[0]):
                                        result[e_val[0]] = {"total": e_val[2] + grp1_v[2],
                                                            "audited": e_val[1] + grp1_v[1]}
                                    else:
                                        pass
                    if len(group_val2) > 0:
                        for e_val in data_values:
                            for grp2_v in group_val2:
                                if e_val[0] == grp2_v[0]:
                                    if result.has_key(e_val[0]):
                                        result[e_val[0]] = {"total": result[e_val[0]]["total"] + grp2_v[2],
                                                            "audited": result[e_val[0]]["audited"] + grp2_v[1]}
                                    else:
                                        result[e_val[0]] = {"total": e_val[2] + grp2_v[2],
                                                            "audited": e_val[1] + grp2_v[1]}
                    if len(group_val1) == 0 and len(group_val2) == 0:
                        for e_val in data_values:
                            result[e_val[0]] = {"total": e_val[2], "audited": e_val[1]}

                    if len(data_values) == 0:
                        if len(group_val1) > 0:                                                    
                            for grp1_v in group_val1:                                
                                if not result.has_key(grp1_v[0]):
                                    result[grp1_v[0]] = {"total":  grp1_v[2],"audited":  grp1_v[1]}

                        if len(group_val2) > 0:                    
                            for grp2_v in group_val2:                            
                                if result.has_key(grp2_v[0]):
                                    result[grp2_v[0]] = {"total": result[grp2_v[0]]["total"] + grp2_v[2],
                                                        "audited": result[grp2_v[0]]["audited"] + grp2_v[1]}
                                else:
                                    result[grp2_v[0]] = {"total": grp2_v[2], "audited": grp2_v[1]}
                            


                    for date, values in result.iteritems():
                        if values['audited'] > 0:
                            acc_v = float(values['total'] / values['audited']) * 100
                            acc_v = 100 - acc_v
                            accuracy = float("%.2f" % round(acc_v, 2))
                        else:
                            accuracy = 100
                        product_lst.append(accuracy)

                result_dict['External Accuracy'] = product_lst
            else:
                level = Level_Order(level_structure_key)
                data_values = query_values.values_list('date', level).annotate(total=Sum('total_errors'),
                                                                               audit=Sum('audited_errors'))
                data_values = filter(lambda e: e[1] != u'', data_values)
                rawtable = RawTable.objects.filter(**filter_params)
                raw_packets = rawtable.values_list('date', level).annotate(prod=Sum('per_day'))
                raw_packets = filter(lambda e: e[1] != u'', raw_packets)
                packets = query_values.values_list(level, flat=True).distinct()
                r_packets = rawtable.values_list(level, flat=True).distinct()
                def low(x): return x.lower().title()
                r_packets = map(low, r_packets)
                r_dates = rawtable.values_list('date', flat=True).distinct()
                if data_values and raw_packets:
                    for date in dates:
                        data_list = []
                        for data in data_values:
                            if date == data[0]:
                                pack = data[1].lower().title()
                                if data[2] > 0:
                                    value = (float(data[3]) / float(data[2])) * 100
                                    accuracy = 100 - value
                                    accuracy = float('%.2f' % round(accuracy, 2))
                                elif data[2] == 0:
                                    if (pack in r_packets) and (data[0] in r_dates):
                                        for prod_val in raw_packets:
                                            if date == prod_val[0] and pack == prod_val[1].lower().title():
                                                value = (float(data[3]) / float(prod_val[2])) * 100
                                                accuracy = 100 - value
                                                accuracy = float('%.2f' % round(accuracy, 2))
                                    else:
                                        accuracy = 100
                                else:
                                    accuracy = 100

                                if not result_dict.has_key(pack):
                                    result_dict[pack] = [accuracy]
                                else:
                                    result_dict[pack].append(accuracy)
                                data_list.append(accuracy)

                        if len(data_list) == 0:
                            for pack in packets:
                                pack = pack.lower().title()
                                if not result_dict.has_key(pack):
                                    result_dict[pack] = [100]
                                else:
                                    result_dict[pack].append(100)


        elif _type in ["week", "month"]:
            exter_acc_query = Externalerrors.objects.filter(project=prj_id, center=center,
                                                            date__range=[main_dates[0], main_dates[-1]])
            dates = exter_acc_query.values_list('date', flat=True).distinct()
            query_values = Externalerrors.objects.filter(**filter_params)
            rawtable = RawTable.objects.filter(**filter_params)
            if all('All' in x for x in level_structure_key.values()):
                data_values = query_values.exclude(
                    work_packet__in=["BIFR", "CompanyCoordinates", "CreditRating", "Defaulter", "RPES", "Legal and CDR",
                                     "Auditor", "Financials", "PAN","Manupatra","Compliance"]) \
                    .order_by('date').values_list('date').annotate(total=Sum('total_errors') \
                                                                   , audit=Sum('audited_errors'))

                if query_values:
                    group_val1 = query_values.filter(
                        work_packet__in=["BIFR", "CompanyCoordinates", "CreditRating", "Defaulter", "RPES",
                                         "Legal and CDR","Manupatra","Compliance"]). \
                        order_by('date').values_list('date'). \
                        annotate(total=Sum('total_errors'), audit=Avg('audited_errors'))

                    group_val2 = query_values.filter(work_packet__in=["Auditor", "Financials", "PAN"]). \
                        order_by('date').values_list('date'). \
                        annotate(total=Sum('total_errors'), audit=Avg('audited_errors'))

                    r = query_values.values_list(_term, flat=True).distinct()
                    pac_dict = {}
                    if len(group_val1) > 0:
                        for e_val in data_values:
                            for grp1_v in group_val1:
                                if e_val[0] == grp1_v[0]:
                                    if not result.has_key(e_val[0]):
                                        result[e_val[0]] = {"total": e_val[2] + grp1_v[2],
                                                            "audited": e_val[1] + grp1_v[1]}
                                    else:
                                        pass
                    if len(group_val2) > 0:
                        for e_val in data_values:
                            for grp2_v in group_val2:
                                if e_val[0] == grp2_v[0]:
                                    if result.has_key(e_val[0]):
                                        result[e_val[0]] = {"total": result[e_val[0]]["total"] + grp2_v[2],
                                                            "audited": result[e_val[0]]["audited"] + grp2_v[1]}
                                    else:
                                        result[e_val[0]] = {"total": e_val[2] + grp2_v[2],
                                                        "audited": e_val[1] + grp2_v[1]}

                    if len(group_val1) == 0 and len(group_val2) == 0:
                        for e_val in data_values:
                            result[e_val[0]] = {"total": e_val[2], "audited": e_val[1]}
                    
                    if len(data_values) == 0:
                        if len(group_val1) > 0:                                                    
                            for grp1_v in group_val1:                                
                                if not result.has_key(grp1_v[0]):
                                    result[grp1_v[0]] = {"total":  grp1_v[2],"audited":  grp1_v[1]}

                        if len(group_val2) > 0:                    
                            for grp2_v in group_val2:                            
                                if result.has_key(grp2_v[0]):
                                    result[grp2_v[0]] = {"total": result[grp2_v[0]]["total"] + grp2_v[2],
                                                        "audited": result[grp2_v[0]]["audited"] + grp2_v[1]}
                                else:
                                    result[grp2_v[0]] = {"total": grp2_v[2], "audited": grp2_v[1]}

                    pac_week = {}
                    pac_week['total'], pac_week['audit'] = [], []
                    for date, values in result.iteritems():
                        pac_week['total'].append(values['total'])
                        pac_week['audit'].append(values['audited'])

                    result = {}
                    result['total'] = sum(pac_week['total'])
                    result['audit'] = sum(pac_week['audit'])

                    if result['audit'] > 0:
                        acc_v = float(result['total'] / result['audit']) * 100
                        acc_v = 100 - acc_v
                        accuracy = float("%.2f" % round(acc_v, 2))
                    else:
                        accuracy = 100

                    result_dict['External Accuracy'] = accuracy

            else:
                level = Level_Order(level_structure_key)
                raw_packets = rawtable.values_list(level).annotate(prod=Sum('per_day'))
                ext_qy = query_values.values_list(level).annotate(audited_errors=Sum('audited_errors'),
                                                                  total_errors=Sum('total_errors'))
                pack_lst = exter_acc_query.values_list(level, flat=True).distinct()
                ext_qy = filter(lambda t: t[1] != u'', ext_qy)
                raw_packets = filter(lambda e: e[1] != u'', raw_packets)
                raw_list = rawtable.values_list(_term, flat=True).distinct()

                def case(x):
                    return x.lower().title()

                raw_list = map(case, raw_list)
                if ext_qy and raw_packets:
                    for data in ext_qy:
                        pack = data[0].lower().title()
                        accuracy = 100
                        if data[2] > 0:
                            value = (float(data[1]) / float(data[2])) * 100
                            accuracy = 100 - value
                            accuracy = float('%.2f' % round(accuracy, 2))
                        elif data[2] == 0:
                            if pack in raw_list:
                                for prod_val in raw_packets:
                                    if pack == prod_val[0].lower().title():
                                        value = (float(data[1]) / float(prod_val[1])) * 100
                                        accuracy = 100 - value
                                        accuracy = float('%.2f' % round(accuracy, 2))
                            else:
                                accuracy = 100
                        else:
                            accuracy = 100

                        result_dict[pack] = accuracy

    return result_dict




def agent_int_acc(main_dates, prj_id, center, level_structure_key, request, _type):
    result_temp, result = {}, {}
    filter_params, _term = getting_required_params(level_structure_key, prj_id, center, main_dates)    
    if filter_params and _term:
        int_acc_full_query = Internalerrors.objects.filter(project=prj_id, center=center,
                                                        date__range=[main_dates[0], main_dates[-1]])
        dates = int_acc_full_query.values_list('date', flat=True).distinct()
        query_values = Internalerrors.objects.filter(**filter_params)
        rawtable = RawTable.objects.filter(**filter_params)
        data_values = query_values.order_by('employee_id').values_list('employee_id').annotate(
                    total=Sum('total_errors'), audit=Sum('audited_errors'))
        data_value = query_values.order_by('employee_id').values('employee_id').annotate(
                    total=Sum('total_errors'), audit=Sum('audited_errors'))
        table_values = rawtable.order_by('employee_id').values_list('employee_id').annotate(prod=Sum('per_day'))
        prod_values = filter(lambda x:x[0] != '', table_values)
        r_agents = rawtable.values_list('employee_id', flat=True).distinct()
        def case(x): return x.lower().title()
        raw_list = map(case, r_agents)
        acc = []
        acc_val = []
        for pack in data_values:
            key = pack[0].lower().title()
            if pack[1]>0:
                value = (float(pack[2]) / float(pack[1])) * 100
                accuracy = 100 - value
                accuracy = float('%.2f' % round(accuracy, 2))
            elif pack[1] == 0:
                if key in r_agents:
                    for val in table_values:                    
                            if key == val[0].lower().title():
                                value = (float(pack[2]) / float(val[1]))
                                accuracy = 100 - value
                                accuracy = float('%.2f' % round(accuracy, 2))
                else:
                    accuracy = 100
            else:
                accuracy = 100
            acc.append(accuracy)
            acc_val.append(key)                   

        result_out = {}
        result_out['Internal Accuracy'] = acc
        result['data'] = result_out
        result['date'] = acc_val

    return result


def agent_ext_acc(main_dates, prj_id, center, level_structure_key, request, _type):
    result_temp, result = {}, {}
    filter_params, _term = getting_required_params(level_structure_key, prj_id, center, main_dates)    
    if filter_params and _term:
        int_acc_full_query = Externalerrors.objects.filter(project=prj_id, center=center,
                                                        date__range=[main_dates[0], main_dates[-1]])
        dates = int_acc_full_query.values_list('date', flat=True).distinct()
        query_values = Externalerrors.objects.filter(**filter_params)
        rawtable = RawTable.objects.filter(**filter_params)
        data_values = query_values.order_by('employee_id').values_list('employee_id').annotate(
                    total=Sum('total_errors'), audit=Sum('audited_errors'))
        data_value = query_values.order_by('employee_id').values('employee_id').annotate(
                    total=Sum('total_errors'), audit=Sum('audited_errors'))
        table_values = rawtable.order_by('employee_id').values_list('employee_id').annotate(prod=Sum('per_day'))
        prod_values = filter(lambda x:x[0] != '', table_values)
        r_agents = rawtable.values_list('employee_id', flat = True).distinct()
        def lower(x): return x.lower().title()
        r_agents = map(lower, r_agents)
        acc = []
        acc_val = []
        for pack in data_values:
            key = pack[0].lower().title()
            if pack[1]>0:
                value = (float(pack[2]) / float(pack[1])) * 100
                accuracy = 100 - value
                accuracy = float('%.2f' % round(accuracy, 2))
            elif pack[1] == 0:
                if key in r_agents:
                    for val in table_values:
                        if key == val[0].lower().title():
                            value = (float(pack[2]) / float(val[1]))
                            accuracy = 100 - value
                            accuracy = float('%.2f' % round(accuracy, 2))
                else:
                    accuracy = 100
            else:
                accuracy = 100
            acc.append(accuracy)
            acc_val.append(key)                    

        result_out = {}
        result_out['External Accuracy'] = acc
        result['data'] = result_out
        result['date'] = acc_val

    return result



def agentwise_production(date_list, prj_id, center_obj, level_structure_key, main_dates, request):
    result = OrderedDict()
    content_list,prod_list = [],[]
    filter_params, _term = getting_required_params(level_structure_key, prj_id, center_obj, date_list)
    if filter_params and _term:                        
        query_values = RawTable.objects.filter(**filter_params)
        data_values = query_values.order_by('employee_id').values_list('employee_id').annotate(total=Sum('per_day'))                                
        for i in data_values:                                    
            content_list.append(i[0])  
            prod_list.append(i[1])                  
    
    result_temp = {}  
    result_temp['Production']  =  prod_list
    result['data'] = result_temp    
    result['date'] = content_list 
    
    return result       