
import datetime
import redis
from api.models import *
from api.basics import *
from api.utils import *
from api.commons import data_dict
from django.db.models import Max
from collections import OrderedDict
from itertools import chain
from datetime import timedelta
from api.graph_settings import graph_data_alignment_color
from common.utils import getHttpResponse as json_HttpResponse


def from_to(request):

    internal_name = "internal_accuracy_timeline"
    external_name = "external_accuracy_timeline"
    name = 'line'
    term = ''
    function_name = accuracy_line_graphs
    result = error_line_charts(request, name, function_name, internal_name, external_name, term)

    return json_HttpResponse(result)


def error_line_charts(request, name, function_name, internal_name, external_name, term):
    final_dict = {}
    date_list, data_date, date_arr = [], [], []
    internal_time_line, external_time_line = {}, {}
    week_num = 0
    week_names = []
    main_data_dict = data_dict(request.GET)
    work_packet = main_data_dict['work_packet']
    sub_project = main_data_dict['sub_project']
    sub_packet = main_data_dict['sub_packet']
    project_center = main_data_dict['pro_cen_mapping']
    project = main_data_dict['pro_cen_mapping'][0][0]
    center = main_data_dict['pro_cen_mapping'][1][0]
    if main_data_dict['dwm_dict'].has_key('day') and main_data_dict['type'] == 'day':
        main_dates_list = [ main_data_dict['dwm_dict']['day']]
    elif main_data_dict['dwm_dict'].has_key('week') and main_data_dict['type'] == 'week':
        main_dates_list = main_data_dict['dwm_dict']['week']
    elif main_data_dict['dwm_dict'].has_key('month') and main_data_dict['type'] == 'month':
        main_dates_list = main_data_dict['dwm_dict']['month']['month_dates']    
   
    if main_data_dict['dwm_dict'].has_key('day') and main_data_dict['type'] == 'day':
        for sing_list in main_dates_list:
            level_structure_key = get_level_structure_key(work_packet, sub_project, sub_packet, project_center)
            _internal_data = function_name(sing_list, project, center, level_structure_key, "Internal",term)
            _external_data = function_name(sing_list, project, center, level_structure_key, "External",term)
            if _internal_data:
                date_list = _internal_data['date']
                if len(_internal_data['internal_accuracy_timeline']) > 0:
                    internal_time_line = {}
                    for er_key, er_value in _internal_data['internal_accuracy_timeline'].iteritems():
                        packet_errors = []
                        for err_value in er_value:
                            if err_value == "NA":
                                packet_errors.append(0)
                            else:
                                packet_errors.append(err_value)
                        internal_time_line[er_key] = packet_errors
                if len(_external_data['internal_accuracy_timeline']) > 0:
                    external_time_line = {}
                    for er_key, er_value in _external_data['internal_accuracy_timeline'].iteritems():
                        packet_errors = []
                        for err_value in er_value:
                            if err_value == "NA":
                                packet_errors.append(0)
                            else:
                                packet_errors.append(err_value)
                        external_time_line[er_key] = packet_errors
            final_dict[internal_name] = graph_data_alignment_color(internal_time_line, 'data',level_structure_key, project, center,'internal_accuracy_timeline')
            final_dict[external_name] = graph_data_alignment_color(external_time_line, 'data',level_structure_key, project, center,'external_accuracy_timeline')
            int_error_timeline_min_max = error_timeline_min_max(internal_time_line)
            final_dict['min_internal_time_line'] = int_error_timeline_min_max['min_value']
            final_dict['max_internal_time_line'] = int_error_timeline_min_max['max_value']
            ext_error_timeline_min_max = error_timeline_min_max(external_time_line)
            final_dict['min_external_time_line'] = ext_error_timeline_min_max['min_value']
            final_dict['max_external_time_line'] = ext_error_timeline_min_max['max_value']
            final_dict['date'] = date_list

    elif main_data_dict['dwm_dict'].has_key('week') and main_data_dict['type'] == 'week':
        internal_week_num ,external_week_num, week_num = 0, 0, 0
        combined_list = list(chain.from_iterable(main_dates_list))
        for sing_list in main_dates_list:
            data_date.append(sing_list[0] + ' to ' + sing_list[-1])
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            _internal_data = accuracy_line_week_month(sing_list, project, center, level_structure_key, "Internal",term, combined_list)
            _external_data = accuracy_line_week_month(sing_list, project, center, level_structure_key, "External",term, combined_list)
            if len(_internal_data) > 0:
                internal_week_name = str('week' + str(internal_week_num))
                internal_accuracy_packets = {}
                intr_accuracy_perc = _internal_data
                for in_acc_key,in_acc_value in intr_accuracy_perc.iteritems():
                    if internal_accuracy_packets.has_key(in_acc_key):
                        internal_accuracy_packets[in_acc_key].append(in_acc_value)
                    else:
                        internal_accuracy_packets[in_acc_key] = in_acc_value
                internal_time_line[internal_week_name] = internal_accuracy_packets
                internal_week_num = internal_week_num + 1
            if len(_external_data) > 0:
                external_week_name = str('week' + str(external_week_num))
                external_accuracy_packets = {}
                extr_accuracy_perc = _external_data
                for in_acc_key,in_acc_value in extr_accuracy_perc.iteritems():
                    if external_accuracy_packets.has_key(in_acc_key):
                        external_accuracy_packets[in_acc_key].append(in_acc_value)
                    else:
                        external_accuracy_packets[in_acc_key] = in_acc_value
                external_time_line[external_week_name] = external_accuracy_packets
                external_week_num = external_week_num + 1

        final_internal_accuracy_timeline = errors_week_calcuations(week_names, internal_time_line, {})
        final_external_accuracy_timeline = errors_week_calcuations(week_names, external_time_line, {})
        if final_internal_accuracy_timeline and final_external_accuracy_timeline: 
            final_dict[internal_name] = graph_data_alignment_color(final_internal_accuracy_timeline, 'data',level_structure_key, project, center,'internal_accuracy_timeline')
            final_dict[external_name] = graph_data_alignment_color(final_external_accuracy_timeline, 'data',level_structure_key, project, center,'external_accuracy_timeline')
            int_error_timeline_min_max = error_timeline_min_max(final_internal_accuracy_timeline)
            final_dict['min_internal_time_line'] = int_error_timeline_min_max['min_value']
            final_dict['max_internal_time_line'] = int_error_timeline_min_max['max_value']
            ext_error_timeline_min_max = error_timeline_min_max(final_external_accuracy_timeline)
            final_dict['min_external_time_line'] = ext_error_timeline_min_max['min_value']
            final_dict['max_external_time_line'] = ext_error_timeline_min_max['max_value']
            final_dict['date'] = data_date
    else:
        final_result_dict, final_internal_accuracy_timeline, final_external_accuracy_timeline = {}, {} ,{}
        internal_accuracy_timeline,  external_accuracy_timeline = {},{}
        month_names, data_date = [], []
        main_date_list = main_data_dict['dwm_dict']['month']['month_dates']
        combined_list = list(chain.from_iterable(main_date_list))
        for month_na,month_va in zip(main_data_dict['dwm_dict']['month']['month_names'],main_data_dict['dwm_dict']['month']['month_dates']):
            month_name = month_na
            month_dates = month_va
            data_date.append(month_dates[0] + ' to ' + month_dates[-1])
            month_names.append(month_name)
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            _internal_data = accuracy_line_week_month(month_dates, project, center, level_structure_key, "Internal",term, combined_list)
            _external_data = accuracy_line_week_month(month_dates, project, center, level_structure_key, "External",term, combined_list)
            if len(_internal_data) > 0:
                internal_accuracy_packets = {}
                intr_accuracy_perc = _internal_data
                for in_acc_key,in_acc_value in intr_accuracy_perc.iteritems():
                    if internal_accuracy_packets.has_key(in_acc_key):
                        internal_accuracy_packets[in_acc_key].append(in_acc_value)
                    else:
                        internal_accuracy_packets[in_acc_key] = in_acc_value
                internal_accuracy_timeline[month_name] = internal_accuracy_packets
            if len(_external_data) > 0:
                external_accuracy_packets = {}
                extr_accuracy_perc = _external_data
                for in_acc_key,in_acc_value in extr_accuracy_perc.iteritems():
                    if external_accuracy_packets.has_key(in_acc_key):
                        external_accuracy_packets[in_acc_key].append(in_acc_value)
                    else:
                        external_accuracy_packets[in_acc_key] = in_acc_value
                external_accuracy_timeline[month_name] = external_accuracy_packets
        final_internal_accuracy_timeline = errors_week_calcuations(month_names, internal_accuracy_timeline, {})
        final_external_accuracy_timeline = errors_week_calcuations(month_names, external_accuracy_timeline, {})
        if final_internal_accuracy_timeline and final_external_accuracy_timeline:
            final_dict[internal_name] = graph_data_alignment_color(final_internal_accuracy_timeline, 'data',level_structure_key, project, center,'internal_accuracy_timeline')
            final_dict[external_name] = graph_data_alignment_color(final_external_accuracy_timeline, 'data',level_structure_key, project, center,'external_accuracy_timeline')
            int_error_timeline_min_max = error_timeline_min_max(final_internal_accuracy_timeline)
            final_dict['min_internal_time_line'] = int_error_timeline_min_max['min_value']
            final_dict['max_internal_time_line'] = int_error_timeline_min_max['max_value']
            ext_error_timeline_min_max = error_timeline_min_max(final_external_accuracy_timeline)
            final_dict['min_external_time_line'] = ext_error_timeline_min_max['min_value']
            final_dict['max_external_time_line'] = ext_error_timeline_min_max['max_value']
            final_dict['date'] = data_date
    final_dict['is_annotation'] = annotation_check(request)
    return final_dict


def accuracy_line_graphs(date_list,prj_id,center_obj,level_structure_key,error_type,_term):

    final_dict , data_dict = {} , {}
    dat_list = []

    if error_type == 'Internal':
        table_name = Internalerrors

    if error_type == 'External':
        table_name = Externalerrors

    filter_params, _term = getting_required_params(level_structure_key, prj_id, center_obj, date_list)
    if filter_params and _term:
        query_values = table_name.objects.filter(**filter_params)
        packet = query_values.values_list(_term, flat=True).distinct()
        packet = list(packet)

        if len(packet) > 0:
            if packet[0] == '':
                if level_structure_key.has_key('work_packet') and level_structure_key.has_key('sub_project'):
                    if level_structure_key['work_packet'] != 'All':
                        packet[0] = str(level_structure_key['work_packet'])
                elif level_structure_key.has_key('work_packet'):
                    if level_structure_key['work_packet'] != 'All':
                        packet[0] = str(level_structure_key['work_packet'])
        packets = map(str, packet)
        error_data = query_values.values_list('date', _term).annotate(total=Sum('total_errors'), audit=Sum('audited_errors'))
        rawtable = RawTable.objects.filter(**filter_params)
        raw_packets = rawtable.values_list('date', _term).annotate(prod=Sum('per_day'))
        date_pack = rawtable.values_list('date', flat=True).distinct()

        for date in date_pack:
            packet_list = []
            dat_list.append(str(date))
            data_list = []
            for data in error_data:
                accuracy = 0
                if str(date) == str(data[0]):
                    if data[2] > 0:
                        value = (float(data[3])/float(data[2])) * 100
                        accuracy = 100 - float('%.2f' % round(value, 2))

                    elif data[2] == 0:
                        for prod_val in raw_packets:
                            if data[0] == prod_val[0] and data[1] == prod_val[1]:
                                value = float((data[3])/float(prod_val[2]))
                                accuracy = 100 - float('%.2f' % round(value,2))
                    else:
                        accuracy = 100
                    if data[1] == '':
                        pack = data[1]
                        if (level_structure_key.has_key('work_packet') and level_structure_key.has_key('sub_project')):
                            if level_structure_key['work_packet'] != 'All':
                                pack = str(level_structure_key['work_packet'])
                        elif level_structure_key.has_key('work_packet'):
                            if level_structure_key['work_packet'] != 'All':
                                pack = str(level_structure_key['work_packet'])
                        elif (level_structure_key.has_key('work_packet') and level_structure_key.has_key('sub_packet')):
                            if (level_structure_key['work_packet'] != 'All' and level_structure_key['sub_packet'] != 'All'):
                                pack = str(level_structure_key['sub_packet'])
                            else:
                                pack = str(level_structure_key['work_packet'])
                    else:
                        pack = data[1]
                    if not data_dict.has_key(pack):
                        data_dict[pack] = [accuracy]
                    else:
                        data_dict[pack].append(accuracy)
                    packet_list.append(pack)
                    data_list.append(accuracy)

            if len(packet_list) > 0:
                packet_list = sorted(list(set(packet_list)))
                packet_list = map(str, packet_list)
                for pack in packets:
                    if str(pack) not in packet_list:
                        if not data_dict.has_key(pack):
                            data_dict[pack] = [0]
                        else:
                            data_dict[pack].append(0)
            if not len(data_list) > 0:
                for pack in packets:
                    if not data_dict.has_key(pack):
                        data_dict[pack] = [0]
                    else:
                        data_dict[pack].append(0)

        final_dict['internal_accuracy_timeline'] = data_dict
        final_dict['date'] = dat_list

    return final_dict


def accuracy_line_week_month(date_list,prj_id,center_obj,level_structure_key,error_type,_term, combined_list):

    _dict = {}
    if error_type == 'Internal':
        table_name = Internalerrors
    if error_type == 'External':
        table_name = Externalerrors

    filter_params, _term = getting_required_params(level_structure_key, prj_id, center_obj, date_list)
    if _term and filter_params:
        query_values = table_name.objects.filter(**filter_params)
        packets = query_values.values_list(_term, flat=True).distinct()
        error_data = query_values.values_list(_term).annotate(total=Sum('total_errors'), audit=Sum('audited_errors'))
        rawtable = RawTable.objects.filter(**filter_params)
        raw_packets = rawtable.values_list(_term).annotate(prod=Sum('per_day'))
        complete_pack = table_name.objects.filter(project=prj_id, center=center_obj, date__range=[combined_list[0],combined_list[-1]]).values_list(_term, flat=True).distinct()
        if error_data:
            for data in error_data:
                accuracy = 0
                if data[1] > 0:
                    value = (float(data[2])/float(data[1])) * 100
                    accuracy = 100-float('%.2f' % round(value, 2))
                elif data[1] == 0:
                    for prod_val in raw_packets:
                        if data[0] == prod_val[0]:
                            value = (float(data[2])/float(prod_val[1])) * 100
                            accuracy = 100-float('%.2f' % round(value, 2))
                else:
                    accuracy = 100
                if data[0] == '':
                    pack = data[0]
                    if (level_structure_key.has_key('work_packet') and level_structure_key.has_key('sub_project')):
                        if level_structure_key['work_packet'] != 'All':
                            pack = str(level_structure_key['work_packet'])
                    elif level_structure_key.has_key('work_packet'):
                        if level_structure_key['work_packet'] != 'All':
                            pack = str(level_structure_key['work_packet'])
                    elif (level_structure_key.has_key('work_packet') and level_structure_key.has_key('sub_packet')):
                        if (level_structure_key['work_packet'] != 'All' and level_structure_key['sub_packet'] != 'All'):
                            pack = str(level_structure_key['sub_packet'])
                        else:
                            pack = str(level_structure_key['work_packet'])
                else:
                    pack = data[0]
                _dict[pack] = accuracy
        else:
            for packets in complete_pack:
                _dict[packets] = 0
    return _dict


def errors_week_calcuations(week_names,internal_accuracy_timeline,final_internal_accuracy_timeline):
    for prodct_key, prodct_value in internal_accuracy_timeline.iteritems():
        for vol_key, vol_values in prodct_value.iteritems():
            error_pers = []
            if vol_values != 'NA':
                error_pers.append(vol_values)
            else:
                error_pers.append(0)

            if len(error_pers) > 0:
                int_errors = float(sum(error_pers)) / len(error_pers)
                int_errors = float('%.2f' % round(int_errors, 2))
            else:
                int_errors = 0
            internal_accuracy_timeline[prodct_key][vol_key] = int_errors

    for final_key, final_value in internal_accuracy_timeline.iteritems():
        for week_key, week_value in final_value.iteritems():
            if week_key not in final_internal_accuracy_timeline.keys():
                final_internal_accuracy_timeline[week_key] = []

    for prod_week_num in week_names:
        if internal_accuracy_timeline.has_key(prod_week_num):
            if len(internal_accuracy_timeline[prod_week_num]) > 0:
                for vol_key, vol_values in internal_accuracy_timeline[prod_week_num].iteritems():
                    if final_internal_accuracy_timeline.has_key(vol_key):
                        final_internal_accuracy_timeline[vol_key].append(vol_values)
                    else:
                        final_internal_accuracy_timeline[vol_key] = [vol_values]

                for prod_key, prod_values in final_internal_accuracy_timeline.iteritems():
                    if prod_key not in internal_accuracy_timeline[prod_week_num].keys():
                        final_internal_accuracy_timeline[prod_key].append(0)
            else:
                for vol_key, vol_values in final_internal_accuracy_timeline.iteritems():
                    final_internal_accuracy_timeline[vol_key].append(0)

    return final_internal_accuracy_timeline


def adding_min_max(high_chart_key,values_dict):
    result = {}
    min_max_values = error_timeline_min_max(values_dict)
    result['min_'+high_chart_key] = min_max_values['min_value']
    result['max_' + high_chart_key] = min_max_values['max_value']
    return result


