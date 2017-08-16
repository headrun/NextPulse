
import datetime
from api.basic import *
from api.models import *
from api.graphs_mod import *

def data_dict(variable):
    """It generates common code required for all the widgets"""
    main_data_dict = {}
    from_date = datetime.datetime.strptime(variable['from'],'%Y-%m-%d').date()
    to_date = datetime.datetime.strptime(variable['to'],'%Y-%m-%d').date()
    project_name = variable.get('project','')
    if project_name:
        project_name = project_name.split(' -')[0]
    center_name = variable.get('center','')
    if center_name:
        center_name = center_name.split(' -')[0]
    pro_cen_mapping = []
    pro_cen_mapping.append(Project.objects.filter(name=project_name).values_list('id', 'name')[0])
    pro_cen_mapping.append(Center.objects.filter(name=center_name).values_list('id', 'name')[0])
    main_data_dict['pro_cen_mapping'] = pro_cen_mapping
    main_data_dict['work_packet'] = variable.get('work_packet',[])
    main_data_dict['sub_project'] = variable.get('sub_project','')
    main_data_dict['sub_packet'] = variable.get('sub_packet','')
    dwm_dict= {}
    date_list=num_of_days(to_date,from_date)
    type = variable.get('type','')
    if type == '':
        type = 'day'
    
    is_clicked = variable.get('is_clicked','NA')
    if type == 'day':
        if 'yes' not in is_clicked:
            if len(date_list) > 15:
                type = 'week'
            if len(date_list) > 60:
                type = 'month'
        dwm_dict['day']= date_list
        main_data_dict['dwm_dict'] = dwm_dict

    if type == 'week':
        months_dict = {}
        weeks_data = [] 
        days = (to_date - from_date).days
        days = days+1
        for i in xrange(days):
            date = from_date + datetime.timedelta(i)
            weeks_data.append(str(date))
        weeks = [] 
        weekdays = []   
        fro_mon = datetime.datetime.strptime(weeks_data[0],'%Y-%m-%d').date()
        to_mon = datetime.datetime.strptime(weeks_data[-1],'%Y-%m-%d').date()
        no_of_days = to_mon - fro_mon
        num_days = int(re.findall('\d+', str(no_of_days))[0]) + 1
        week_list=[]
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

    if type == 'week':
        employe_dates = {}
        dwm_dict['week'] = week_list
        for week in week_list:
            if week and  employe_dates.has_key('days'):
                employe_dates['days'] = employe_dates['days']+week

            else:
                employe_dates['days'] = week
        
        main_data_dict['dwm_dict'] = dwm_dict
    
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
    if type == 'month':
        employe_dates = {}
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
        main_data_dict['dwm_dict'] = dwm_dict
    main_data_dict['type'] = type
    return main_data_dict 

def get_packet_details(request):
    """It will generate all the list of packets, projects and sub packets for the project"""
    main_data_dict = data_dict(request.GET)
    dates = [main_data_dict['dwm_dict']['day'][:-1][0], main_data_dict['dwm_dict']['day'][-1:][0]]
    final_dict = {}
    raw_master_set = RawTable.objects.filter(project=main_data_dict['pro_cen_mapping'][0][0], center=main_data_dict['pro_cen_mapping'][1][0], 
                                             date__range=dates)
    sub_pro_level = filter(None, raw_master_set.values_list('sub_project',flat=True).distinct())
    sub_project_level = [i for i in sub_pro_level]
    if len(sub_project_level) >= 1:
        sub_project_level.append('all')
    else:
        sub_project_level = ''
    work_pac_level = filter(None, raw_master_set.values_list('work_packet',flat=True).distinct())
    work_packet_level = [j for j in work_pac_level]
    if len(work_packet_level) >= 1:
        work_packet_level.append('all')
    else:
        work_packet_level = ''
    sub_pac_level = filter(None, raw_master_set.values_list('sub_packet',flat=True).distinct())
    sub_packet_level = [k for k in sub_pac_level]
    if len(sub_packet_level) >= 1:
        sub_packet_level.append('all')
    else:
        sub_packet_level = ''
    final_details = {}
    final_details['sub_project'] = 0
    final_details['work_packet'] = 0
    final_details['sub_packet'] = 0
    if len(sub_pro_level) >= 1:
        final_details['sub_project'] = 1
    if len(work_pac_level) >= 1:
        final_details['work_packet'] = 1
    if len(sub_pac_level) >= 1:
        final_details['sub_packet'] = 1
    prj_id = main_data_dict['pro_cen_mapping'][0][0]
    center = main_data_dict['pro_cen_mapping'][1][0]
    final_dict['sub_project_level'] = sub_project_level
    final_dict['work_packet_level'] = work_packet_level
    final_dict['sub_packet_level'] = sub_packet_level
    big_dict = {}
    if final_details['sub_project']:
        if final_details['work_packet']:
            first = raw_master_set.values_list('sub_project').distinct()
            big_dict = {}
            total = {}
            for i in first:
                list_val = RawTable.objects.filter(project=prj_id, sub_project=i[0], date__range=dates).values_list('work_packet').distinct()
                for j in list_val:
                    total[j[0]] = []
                    sub_pac_data = RawTable.objects.filter(project=prj_id, sub_project=i[0], work_packet=j[0], date__range=dates).values_list('sub_packet').distinct()
                    for l in sub_pac_data:
                        total[j[0]].append(l[0])
                big_dict[i[0]] = total
                total = {}
    elif final_details['work_packet']:
        if final_details['sub_packet']:
            first = raw_master_set.values_list('work_packet').distinct()
            big_dict = {}
            total = {}
            for i in first:
                list_val = RawTable.objects.filter(project=prj_id, work_packet=i[0], date__range=dates).values_list('sub_packet').distinct()
                for j in list_val:
                    total[j[0]] = []
                big_dict[i[0]] = total
                total = {}
        else:
            big_dict = {}
            work_pac_level = raw_master_set.values_list('work_packet').distinct()
            for i in work_pac_level:
                big_dict[i[0]] = {}
    final_dict['level'] = [1, 2]
    final_dict['fin'] = final_details
    final_dict['drop_value'] = big_dict
    return json_HttpResponse(final_dict)


def dropdown_data_types(request):
    project = request.GET['project'].split('-')[0].strip()
    center_id = request.GET['center'].split('-')[0].strip()
    center = Center.objects.filter(name=center_id).values_list('id', flat=True)
    prj_id = Project.objects.filter(name=project).values_list('id', flat=True)
    result = {}
    sub_project = RawTable.objects.filter(project_id=prj_id[0],center_id = center[0]).values_list('sub_project',flat=True).distinct()
    sub_project = filter(None, sub_project)
    work_packet = RawTable.objects.filter(project_id=prj_id[0],center_id = center[0]).values_list('work_packet',flat=True).distinct()
    work_packet = filter(None, work_packet)
    sub_packet = RawTable.objects.filter(project_id=prj_id[0], center_id=center[0]).values_list('sub_packet',flat=True).distinct()
    sub_packet = filter(None, sub_packet)
    result['sub_project'] = 0
    if len(sub_project) > 0:
        result['sub_project'] = 1
    result['work_packet'] = 0
    if len(work_packet) > 0:
        result['work_packet'] = 1
    result['sub_packet'] = 0
    if len(sub_packet) > 0:
        result['sub_packet'] = 1
    return json_HttpResponse(result)


def dates_sorting(timestamps):
    dates = [datetime.datetime.strptime(ts, "%Y-%m-%d") for ts in timestamps]
    dates.sort()
    sorted_values = [datetime.datetime.strftime(ts, "%Y-%m-%d") for ts in dates]
    return sorted_values


def Authoring_mapping(prj_obj,center_obj,model_name):
    table_model = apps.get_model('api', model_name)
    map_query = table_model.objects.filter(project=prj_obj, center=center_obj)
    if len(map_query) > 0:
        map_query = map_query[0].__dict__
    else:
        map_query = {}
    return map_query

def previous_sum(volumes_dict):
    new_dict = {}
    for key, value in volumes_dict.iteritems():
        new_dict[key] = []
        for i in xrange(len(value)):
            if i == 0:
                new_dict[key].append(value[i])
            else:
                new_dict[key].append(new_dict[key][i - 1] + value[i])
    return new_dict

def level_hierarchy_key(level_structure_key,vol_type):
    final_work_packet = ''
    if level_structure_key.has_key('sub_project'):
        if vol_type['sub_project'] !='':
            final_work_packet = vol_type['sub_project']
    if level_structure_key.has_key('work_packet'):
        if final_work_packet and vol_type['work_packet'] != '':
            final_work_packet = final_work_packet + '_' + vol_type['work_packet']
        else:
            if vol_type['work_packet'] != '':
                final_work_packet = vol_type['work_packet']
    if level_structure_key.has_key('sub_packet'):
        if vol_type.has_key('sub_packet'):
            if final_work_packet and vol_type['sub_packet'] != '':
                final_work_packet = final_work_packet + '_' + vol_type['sub_packet']
            else:
                if vol_type['sub_packet'] != '':
                    final_work_packet = vol_type['sub_packet']
    return  final_work_packet

def day_week_month(request, dwm_dict, prj_id, center, work_packets, level_structure_key):
    from api.graph_error import internal_extrnal_graphs
    from api.graphs_mod import internal_extrnal_graphs
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
                internal_accuracy_timeline[month_name] = error_graphs_data['internal_time_line']['internal_time_line']
                intr_accuracy_perc = error_graphs_data['internal_accuracy_graph']
                for in_acc_key,in_acc_value in intr_accuracy_perc.iteritems():
                    if internal_accuracy_packets.has_key(in_acc_key):
                        internal_accuracy_packets[in_acc_key].append(in_acc_value)
                    else:
                        internal_accuracy_packets[in_acc_key] = in_acc_value
                internal_accuracy_timeline[month_name] = internal_accuracy_packets
            if len(error_graphs_data['external_time_line']) > 0: 
                external_accuracy_packets = {}
                if error_graphs_data.has_key('external_accuracy_graph'):
                    extr_accuracy_perc = error_graphs_data['external_accuracy_graph']
                else:
                    extr_accuracy_perc = error_graphs_data['extr_err_accuracy']['packets_percntage'] 
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

            if error_graphs_data.has_key('extr_err_accuracy'):
                for vol_key, vol_values in error_graphs_data['extr_err_accuracy']['packets_percntage'].iteritems():
                    if all_external_error_accuracy.has_key(vol_key):
                        all_external_error_accuracy[vol_key].append(vol_values[0])
                    else:
                        all_external_error_accuracy[vol_key] = vol_values

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
                external_accuracy_timeline[external_week_name] = error_graphs_data['external_time_line']['external_time_line']
                external_accuracy_packets = {}
                if error_graphs_data.has_key('external_accuracy_graph'):
                    extr_accuracy_perc = error_graphs_data['external_accuracy_graph']
                else:
                    extr_accuracy_perc = error_graphs_data['extr_err_accuracy']['packets_percntage']
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

            if error_graphs_data.has_key('extr_err_accuracy'):
                for vol_key, vol_values in error_graphs_data['extr_err_accuracy']['packets_percntage'].iteritems():
                    if all_external_error_accuracy.has_key(vol_key):
                        all_external_error_accuracy[vol_key].append(vol_values[0])
                    else:
                        all_external_error_accuracy[vol_key] = vol_values

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

def min_max_value_data(int_value_range):
    main_max_dict = {}
    if len(int_value_range) > 0:
        data_value = []
        if (min(int_value_range.values()) > 0):
            for i in int_value_range.values():
                for values in i:
                    data_value.append(values)
            int_min_value = int(round(min(data_value)-2))
            int_max_value = int(round(max(data_value)+2))
        else:
            int_min_value = int(round(min(int_value_range.values())))
            int_max_value = int(round(max(int_value_range.values()) + 2))
    else:
        int_min_value, int_max_value = 0, 0
    main_max_dict ['min_value'] = int_min_value
    main_max_dict ['max_value'] = int_max_value
    return main_max_dict

def min_max_num(int_value_range):
    main_max_dict = {}
    if len(int_value_range) > 0:
        if (min(int_value_range.values()) > 0):
            int_min_value = int(round(min(int_value_range.values()) - 2))
            int_max_value = int(round(max(int_value_range.values()) + 2))
        else:
            int_min_value = int(round(min(int_value_range.values())))
            int_max_value = int(round(max(int_value_range.values()) + 2))
    else:
        int_min_value, int_max_value = 0, 0
    main_max_dict ['min_value'] = int_min_value
    main_max_dict ['max_value'] = int_max_value
    return main_max_dict
