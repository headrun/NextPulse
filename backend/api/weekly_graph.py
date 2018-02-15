
import datetime
import redis
from api.models import *
from api.basics import *
from api.utils import *
from api.commons import data_dict
from django.db.models import Max
from collections import OrderedDict
from datetime import timedelta
from api.query_generations import query_set_generation
from api.internal_external_common import internal_extrnal_graphs
from api.graph_settings import graph_data_alignment_color
from common.utils import getHttpResponse as json_HttpResponse


def volume_graph_data_week_month(date_list,prj_id,center_obj,level_structure_key):
    conn = redis.Redis(host="localhost", port=6379, db=0)
    result, volumes_dict, date_values = {}, {}, {}
    #prj_name = Project.objects.filter(id=prj_id).values_list('name',flat=True)
    #center_name = Center.objects.filter(id=center_obj).values_list('name', flat=True)
    project = Project.objects.filter(id=prj_id)
    prj_name = project[0].name
    center_name = project[0].center.name
    query_set = query_set_generation(prj_id,center_obj,level_structure_key,date_list)
    volume_list = worktrack_internal_external_workpackets_list(level_structure_key,'Worktrack',query_set)
    total_done_value = RawTable.objects.filter(project=prj_id, center=center_obj, date__range=[date_list[0], date_list[-1]]).values('date').annotate(total=Sum('per_day'))
    values = OrderedDict(zip(map(lambda p: str(p['date']), total_done_value), map(lambda p: str(p['total']), total_done_value)))
    for date_key, total_val in values.iteritems():
    #for date_va in date_list:
        #total_done_value = RawTable.objects.filter(project=prj_id, center=center_obj, date=date_va).aggregate(Max('per_day'))
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
        
        worktrack_volumes = OrderedDict()
        worktrack_volumes['Opening'] = [sum(i) for i in zip(*opening)]
        worktrack_volumes['Received'] = [sum(i) for i in zip(*received)]
        worktrack_volumes['Non Workable Count'] = [sum(i) for i in zip(*nwc)]
        worktrack_volumes['Completed'] = [sum(i) for i in zip(*completed)]
        worktrack_volumes['Closing balance'] = [sum(i) for i in zip(*closing_bal)]
        worktrack_timeline = OrderedDict()
        worktrack_timeline['Completed'] = worktrack_volumes['Completed']
        worktrack_timeline['Received'] = worktrack_volumes['Received']
        worktrack_timeline['Opening'] = worktrack_volumes['Opening']
        final_volume_graph = {}
        final_volume_graph['bar_data']  = worktrack_volumes
        final_volume_graph['line_data'] = worktrack_timeline
        return final_volume_graph
    else:
        final_volume_graph ={}
        final_volume_graph['bar_data'] = {}
        final_volume_graph['line_data'] = {}
        return final_volume_graph        




def day_week_month(request, dwm_dict, prj_id, center, work_packets, level_structure_key):
    if dwm_dict.has_key('day'):
        final_dict = {}
        final_details = {}
        error_graphs_data = internal_extrnal_graphs(dwm_dict['day'], prj_id, center,level_structure_key)
        if len(error_graphs_data['internal_time_line']) > 0:
            internal_time_line = {}
            for er_key, er_value in error_graphs_data['internal_time_line']['internal_time_line'].iteritems():
                packet_errors = []
                for err_value in er_value:
                    if err_value == "NA":
                        packet_errors.append(0)
                    else:
                        packet_errors.append(err_value)
                internal_time_line[er_key] = packet_errors
            final_dict['internal_time_line'] = graph_data_alignment_color(internal_time_line, 'data',level_structure_key, prj_id, center,'internal_accuracy_timeline')
            int_error_timeline_min_max = error_timeline_min_max(internal_time_line)
            final_dict['min_internal_time_line'] = int_error_timeline_min_max['min_value']
            final_dict['max_internal_time_line'] = int_error_timeline_min_max['max_value']
        if len(error_graphs_data['external_time_line']) > 0:
            for er_key, er_value in error_graphs_data['external_time_line']['external_time_line'].iteritems():
                packet_errors = []
                for err_value in er_value:
                    if err_value == "NA":
                        packet_errors.append(0)
                    else:
                        packet_errors.append(err_value)
                error_graphs_data['external_time_line']['external_time_line'][er_key] = packet_errors
            final_dict['external_time_line'] = graph_data_alignment_color(error_graphs_data['external_time_line']['external_time_line'], 'data', level_structure_key, prj_id,center,'external_accuracy_timeline')
            ext_error_timeline_min_max = error_timeline_min_max(
                error_graphs_data['external_time_line']['external_time_line'])
            final_dict['min_external_time_line'] = ext_error_timeline_min_max['min_value']
            final_dict['max_external_time_line'] = ext_error_timeline_min_max['max_value']
        all_external_error_accuracy = {}
        all_internal_error_accuracy = {}

        dates = [dwm_dict['day'][0], dwm_dict['day'][-1:][0]]

        ext_min_value, ext_max_value = 0, 0
        if error_graphs_data.has_key('extr_err_accuracy'):
            ext_value_range = error_graphs_data['extr_err_accuracy']['extr_err_perc']
            if len(ext_value_range) > 0:
                if ext_value_range != '' and min(ext_value_range) > 0:
                    ext_min_value = int(round(min(ext_value_range) - 2))
                    ext_max_value = int(round(max(ext_value_range) + 2))
                else:
                    ext_min_value = int(round(min(ext_value_range)))
                    ext_max_value = int(round(max(ext_value_range) + 2))
            final_dict['ext_min_value'] = ext_min_value
            final_dict['ext_max_value'] = ext_max_value
        new_date_list = []
        for date_va in dwm_dict['day']:
            total_done_value = RawTable.objects.filter(project=prj_id,center=center,date=date_va).aggregate(Max('per_day'))
            if total_done_value['per_day__max'] > 0:
                new_date_list.append(date_va)
        final_dict['date'] = new_date_list
        return final_dict

    if dwm_dict.has_key('month'):
        result_dict, final_result_dict, final_internal_accuracy_timeline = {}, {}, {}
        internal_accuracy_timeline, final_external_accuracy_timeline, external_accuracy_timeline = {}, {}, {}
        month_names, data_date = [], []
        all_internal_error_accuracy, all_external_error_accuracy = {}, {}
        for month_na,month_va in zip(dwm_dict['month']['month_names'],dwm_dict['month']['month_dates']):
            month_name = month_na
            month_dates = month_va
            data_date.append(month_dates[0] + ' to ' + month_dates[-1])
            month_names.append(month_name)
            error_graphs_data = internal_extrnal_graphs(month_dates, prj_id, center,level_structure_key)
            if len(error_graphs_data['internal_time_line']) > 0:
                internal_accuracy_packets = {}
                #internal_accuracy_timeline[month_name] = error_graphs_data['internal_time_line']['internal_time_line']
                intr_accuracy_perc = error_graphs_data['internal_accuracy_graph']
                for in_acc_key,in_acc_value in intr_accuracy_perc.iteritems():
                    if internal_accuracy_packets.has_key(in_acc_key):
                        internal_accuracy_packets[in_acc_key].append(in_acc_value)
                    else:
                        internal_accuracy_packets[in_acc_key] = in_acc_value
                internal_accuracy_timeline[month_name] = internal_accuracy_packets
            if len(error_graphs_data['external_time_line']) > 0: 
                external_accuracy_packets = {}

                """if error_graphs_data.has_key('external_accuracy_graph'):
                    extr_accuracy_perc = error_graphs_data['external_accuracy_graph']
                else:
                    extr_accuracy_perc = error_graphs_data['extr_err_accuracy']['packets_percntage'] """

                extr_accuracy_perc = error_graphs_data['external_accuracy_graph']
                for ex_acc_key,ex_acc_value in extr_accuracy_perc.iteritems():
                    if external_accuracy_packets.has_key(ex_acc_key):
                        if isinstance(ex_acc_value,list):
                            external_accuracy_packets[ex_acc_key].append(ex_acc_value[0])
                        else:
                            external_accuracy_packets[ex_acc_key].append(ex_acc_value)
                    else:
                        if isinstance(ex_acc_value,list):
                            external_accuracy_packets[ex_acc_key] = ex_acc_value
                        else:
                            external_accuracy_packets[ex_acc_key] = [ex_acc_value]
                external_accuracy_timeline[month_name] = external_accuracy_packets

            """if error_graphs_data.has_key('extr_err_accuracy'):
                for vol_key, vol_values in error_graphs_data['extr_err_accuracy']['packets_percntage'].iteritems():
                    if all_external_error_accuracy.has_key(vol_key):
                        all_external_error_accuracy[vol_key].append(vol_values[0])
                    else:
                        all_external_error_accuracy[vol_key] = vol_values"""

        dates = [dwm_dict['month']['month_dates'][0][0], dwm_dict['month']['month_dates'][-1:][0][-1:][0]]

        final_internal_accuracy_timeline = errors_week_calcuations(month_names, internal_accuracy_timeline,final_internal_accuracy_timeline)
        final_external_accuracy_timeline = errors_week_calcuations(month_names, external_accuracy_timeline,final_external_accuracy_timeline)
        result_dict['internal_time_line'] = graph_data_alignment_color(final_internal_accuracy_timeline, 'data',level_structure_key, prj_id, center,'internal_accuracy_timeline')        
        int_error_timeline_min_max = error_timeline_min_max(final_internal_accuracy_timeline)
        result_dict['min_internal_time_line'] = int_error_timeline_min_max['min_value']
        result_dict['max_internal_time_line'] = int_error_timeline_min_max['max_value']
        result_dict['external_time_line'] = graph_data_alignment_color(final_external_accuracy_timeline, 'data',level_structure_key, prj_id, center,'external_accuracy_timeline')

        ext_error_timeline_min_max = error_timeline_min_max(final_external_accuracy_timeline)
        result_dict['min_external_time_line'] = ext_error_timeline_min_max['min_value']
        result_dict['max_external_time_line'] = ext_error_timeline_min_max['max_value']
        result_dict['date'] = data_date
        return result_dict

    if dwm_dict.has_key('week'):
        final_result_dict, result_dict, final_internal_accuracy_timeline = {}, {}, {}
        internal_accuracy_timeline, final_external_accuracy_timeline, external_accuracy_timeline = {}, {}, {}
        all_internal_error_accuracy, all_external_error_accuracy = {}, {}
        data_date, week_names = [], []
        internal_week_num, external_week_num, week_num = 0, 0, 0
        for week in dwm_dict['week']:
            data_date.append(week[0] + ' to ' + week[-1])
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            error_graphs_data = internal_extrnal_graphs(week, prj_id, center,level_structure_key)
            if len(error_graphs_data['internal_time_line']) > 0:
                internal_week_name = str('week' + str(internal_week_num))
                internal_accuracy_packets = {}
                intr_accuracy_perc = error_graphs_data['internal_accuracy_graph']
                for in_acc_key,in_acc_value in intr_accuracy_perc.iteritems():
                    if internal_accuracy_packets.has_key(in_acc_key):
                        internal_accuracy_packets[in_acc_key].append(in_acc_value)
                    else:
                        internal_accuracy_packets[in_acc_key] = in_acc_value
                internal_accuracy_timeline[internal_week_name] = internal_accuracy_packets
                internal_week_num = internal_week_num + 1

            if len(error_graphs_data['external_time_line']) > 0:
                external_week_name = str('week' + str(external_week_num))
                #external_accuracy_timeline[external_week_name] = error_graphs_data['external_time_line']['external_time_line']
                external_accuracy_packets = {}

                """if error_graphs_data.has_key('external_accuracy_graph'):
                    extr_accuracy_perc = error_graphs_data['external_accuracy_graph']
                else:
                    extr_accuracy_perc = error_graphs_data['extr_err_accuracy']['packets_percntage']"""
                
                extr_accuracy_perc = error_graphs_data['external_accuracy_graph']
                for ex_acc_key,ex_acc_value in extr_accuracy_perc.iteritems():
                    if external_accuracy_packets.has_key(ex_acc_key):
                        if isinstance(ex_acc_value,list):
                            external_accuracy_packets[ex_acc_key].append(ex_acc_value[0])
                        else:
                            external_accuracy_packets[ex_acc_key].append(ex_acc_value)
                    else:
                        if isinstance(ex_acc_value,list):
                            external_accuracy_packets[ex_acc_key] = ex_acc_value
                        else:
                            external_accuracy_packets[ex_acc_key] = [ex_acc_value]
                external_accuracy_timeline[external_week_name] = external_accuracy_packets
                external_week_num = external_week_num + 1

            """if error_graphs_data.has_key('extr_err_accuracy'):
                for vol_key, vol_values in error_graphs_data['extr_err_accuracy']['packets_percntage'].iteritems():
                    if all_external_error_accuracy.has_key(vol_key):
                        all_external_error_accuracy[vol_key].append(vol_values[0])
                    else:
                        all_external_error_accuracy[vol_key] = vol_values"""

        dates = [dwm_dict['week'][0][0], dwm_dict['week'][-1:][0][-1:][0]]    
        final_internal_accuracy_timeline = errors_week_calcuations(week_names, internal_accuracy_timeline,final_internal_accuracy_timeline)
        final_external_accuracy_timeline = errors_week_calcuations(week_names, external_accuracy_timeline,final_external_accuracy_timeline)
        result_dict['internal_time_line'] = graph_data_alignment_color(final_internal_accuracy_timeline, 'data',level_structure_key, prj_id, center,'internal_accuracy_timeline')
        int_error_timeline_min_max = error_timeline_min_max(final_internal_accuracy_timeline)
        result_dict['min_internal_time_line'] = int_error_timeline_min_max['min_value']
        result_dict['max_internal_time_line'] = int_error_timeline_min_max['max_value']
        result_dict['external_time_line'] = graph_data_alignment_color(final_external_accuracy_timeline, 'data',
                                                                       level_structure_key, prj_id, center,'external_accuracy_timeline')
        ext_error_timeline_min_max = error_timeline_min_max(final_external_accuracy_timeline)
        result_dict['min_external_time_line'] = ext_error_timeline_min_max['min_value']
        result_dict['max_external_time_line'] = ext_error_timeline_min_max['max_value']
        result_dict['date'] = data_date
        return result_dict


def adding_min_max(high_chart_key,values_dict):
    result = {}
    min_max_values = error_timeline_min_max(values_dict)
    result['min_'+high_chart_key] = min_max_values['min_value']
    result['max_' + high_chart_key] = min_max_values['max_value']
    return result


def from_to(request):
    from_date = datetime.datetime.strptime(request.GET['from'],'%Y-%m-%d').date()
    to_date = datetime.datetime.strptime(request.GET['to'],'%Y-%m-%d').date()
    type = request.GET['type']
    #type='day'
    try:
        work_packet = request.GET.get('work_packet')
        if ' and ' in work_packet:
            work_packet = work_packet.replace(' and ', ' & ')
    except:
        work_packet = []
    try:
        sub_project = request.GET.get('sub_project')
    except:
        sub_project = ''
    try:
        sub_packet = request.GET.get('sub_packet')
    except:
        sub_packet = ''
    
    try:
        is_clicked = request.GET.get('is_clicked','NA')
    except:
        is_clicked = 'NA'
    project = request.GET['project'].split('-')[0].strip()
    center_id = request.GET['center'].split('-')[0].strip()
    center = Center.objects.filter(name=center_id).values_list('id', flat=True)
    prj_id = Project.objects.filter(name=project).values_list('id', flat=True)
    date_list, month_list, month_names_list = [], [], []
    if type == 'day':
        date_list=num_of_days(to_date,from_date)
        if 'yes' not in is_clicked:
            if len(date_list) > 15:
                type = 'week'
            if len(date_list) > 60:
                type = 'month'
    if type == 'month':
        months_dict = {}
        month_list = [[]]
        month_names_list = []
        month_count = 0
        days = (to_date - from_date).days
        days = days+1
        for i in xrange(0, days):
            date = from_date + datetime.timedelta(i)
            month = date.strftime("%B")
            if month not in month_names_list:
                month_names_list.append(month)
            if month in months_dict:
                months_dict[month].append(str(date))
                month_list[month_count].append(str(date))
            else:
                months_dict[month] = [str(date)]
                month_count = month_count + 1
                month_list.append([str(date)])
        if month_list[0] == []:
            del month_list[0]

    if type == 'week':
        months_dict = {}
        weeks_data = []
        days = (to_date - from_date).days
        days = days+1
        for i in xrange(0, days):
            date = from_date + datetime.timedelta(i)
            weeks_data.append(str(date))
        weeks, weekdays, week_list = [], [], []
        fro_mon = datetime.datetime.strptime(weeks_data[0],'%Y-%m-%d').date()
        to_mon = datetime.datetime.strptime(weeks_data[-1],'%Y-%m-%d').date()
        no_of_days = to_mon - fro_mon
        num_days = int(re.findall('\d+', str(no_of_days))[0]) + 1
        start = 1
        end = 7 - fro_mon.weekday()
        while start <= num_days:
            weeks.append({'start': start, 'end': end})
            sdate = fro_mon + datetime.timedelta(start - 1) 
            edate = fro_mon + datetime.timedelta(end - 1) 
            weekdays.append({'start': sdate, 'end': edate})
            start = end + 1
            end = end + 7
            if end > num_days:
                end = num_days
        if weekdays[-1]['end'] > to_mon :
            weekdays[-1]['end'] = to_mon
        for w_days in weekdays:
            date_list = num_of_days(w_days['end'],w_days['start'])
            week_list.append(date_list)
    dwm_dict= {}
    employe_dates = {}
    if type == 'day':
        dwm_dict['day']= date_list
        employe_dates['days'] = date_list
    if type == 'month':
        new_month_dict = {}
        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July','August', 'September', 'October', 'November', 'December']
        k = OrderedDict(sorted(months_dict.items(), key=lambda x: months.index(x[0])))
        for month_na in tuple(k):
            new_month_dict[month_na] = {}
            if employe_dates.has_key('days'):
                employe_dates['days'] = employe_dates['days']+months_dict[month_na]
            else:
                employe_dates['days']=months_dict[month_na]
        dwm_dict['month'] = {'month_names':month_names_list, 'month_dates':month_list}

    if type == 'week':
        dwm_dict['week'] = week_list
        for week in week_list:
            if week and  employe_dates.has_key('days'):
                employe_dates['days'] = employe_dates['days']+week
            else:
                employe_dates['days'] = week


    resul_data = {}
    main_data_dict = data_dict(request.GET)
    level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'], main_data_dict['pro_cen_mapping'])
    final_result_dict = day_week_month(request,dwm_dict,prj_id,center,work_packet,level_structure_key)
    ###volumes_graphs_details = volumes_graphs_data(date_list,prj_id,center,level_structure_key)
    #volumes_graphs_details = volumes_graphs_data_table(employe_dates['days'],prj_id,center,level_structure_key)

    final_dict = {}      
    #final_result_dict['volumes_graphs_details'] = volumes_graphs_details
    #internal_sub_error_types = internal_extrnal_sub_error_types(request, employe_dates['days'], prj_id, center, level_structure_key,"Internal")
    #external_sub_error_types = internal_extrnal_sub_error_types(request, employe_dates['days'], prj_id, center,level_structure_key, "External")
    #final_result_dict['internal_sub_error_types'] = graph_data_alignment_color(internal_sub_error_types,'y',level_structure_key,prj_id,center,'')
    #final_result_dict['external_sub_error_types'] = graph_data_alignment_color(external_sub_error_types,'y',level_structure_key,prj_id,center,'')
    final_result_dict['days_type'] = type
    final_result_dict['is_annotation'] = annotation_check(request)
    return json_HttpResponse(final_result_dict)

