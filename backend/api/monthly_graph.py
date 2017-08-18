
import datetime
import redis
from api.models import *
from api.basics import *
from django.db.models import Max
from api.query_generations import *
from api.graph_settings import graph_data_alignment_color
from common.utils import getHttpResponse as json_HttpResponse

def Monthly_Volume_graph(prj_id,center,date_list, level_structure_key):
    from datetime import datetime
    startTime = datetime.now()
    data_list, final_target, final_done_value, volume_list = [], [], [], [] 
    conn = redis.Redis(host="localhost", port=6379, db=0)
    date_values, date_targets = {}, {} 
    tar_count, done_value = 0, 0 
    prj_name = Project.objects.filter(id=prj_id).values_list('name', flat=True)
    center_name = Center.objects.filter(id=center).values_list('name', flat=True)
    query_set = query_set_generation(prj_id, center, level_structure_key, date_list)
    target_query_set=target_query_set_generation(prj_id, center, level_structure_key, date_list)
    noram_query_set = RawTable.objects.filter(**query_set)
    for_target_query_set = Targets.objects.filter(**target_query_set)
    if level_structure_key.has_key('sub_project'):
        if level_structure_key['sub_project'] == "All":
            sub_packet = filter(None, for_target_query_set.values_list('sub_packet',flat=True).distinct())
            if not sub_packet:
                volume_list = noram_query_set.values('sub_project', 'work_packet').distinct()
            else:
                volume_list = noram_query_set.values('sub_project', 'work_packet','sub_packet').distinct()
        else:
            if level_structure_key.has_key('work_packet'):
                if level_structure_key['work_packet'] == "All":
                    sub_packet = filter(None, for_target_query_set.values_list('sub_packet',flat=True).distinct())
                    if level_structure_key['sub_packet'] == "All":
                        if not sub_packet:
                            volume_list = noram_query_set.values('sub_project','work_packet').distinct()
                        else:
                            volume_list = noram_query_set.values('sub_project', 'work_packet','sub_packet').distinct()

                else:
                    sub_packet = filter(None, for_target_query_set.values_list('sub_packet',flat=True).distinct())
                    if level_structure_key.get('sub_packet','') == "All":
                        if not sub_packet:
                            volume_list = noram_query_set.values('sub_project','work_packet').distinct()
                        else:
                            volume_list = noram_query_set.values('sub_project', 'work_packet','sub_packet').distinct()
                    else:
                        volume_list = []
                        if sub_packet:
                            volume_list = noram_query_set.values('sub_project', 'work_packet','sub_packet').distinct()
    elif level_structure_key.has_key('work_packet') and len(level_structure_key) == 1:
        if level_structure_key['work_packet'] == "All":
            sub_packet = filter(None, for_target_query_set.values_list('sub_packet',flat=True).distinct())
            if level_structure_key.get('sub_packet','') == "All" and sub_packet:
                volume_list = noram_query_set.values('sub_project', 'work_packet','sub_packet').distinct()
            else:
                volume_list = noram_query_set.values('sub_project', 'work_packet').distinct()
        else:
            if level_structure_key.get('sub_packet','') == "All":
                volume_list = noram_query_set.values('sub_project', 'work_packet').distinct()
            else:
                volume_list = noram_query_set.values('sub_project', 'work_packet','sub_packet').distinct()
    elif level_structure_key.has_key('work_packet') and level_structure_key.has_key('sub_packet'):
        sub_packet = filter(None, for_target_query_set.values_list('sub_packet', flat=True).distinct())
        if level_structure_key['sub_packet'] == "All":
            if not sub_packet:
                volume_list = noram_query_set.values('sub_project', 'work_packet').distinct()
        else:
            volume_list = []
            if sub_packet:
                volume_list = noram_query_set.values('sub_project', 'work_packet','sub_packet').distinct()

    else:
        volume_list = []
    new_date_list = []
    volumes_dict, _targets_list, final_values, final_targets = {}, {}, {}, {}
    final_values['total_workdone'], final_targets['total'] = [], []
    final_work_packet = ''
    for date_va in date_list:
        total_done_value = RawTable.objects.filter(project=prj_id, center=center, date=date_va).aggregate(Max('per_day'))
        if total_done_value['per_day__max'] > 0:
            new_date_list.append(str(date_va))
            count = 0
            for vol_type in volume_list:
                if level_structure_key.has_key('sub_project'):
                    local_level_hierarchy_key = vol_type
                else:
                    local_level_hierarchy_key = level_structure_key
                final_work_packet = level_hierarchy_key(local_level_hierarchy_key, vol_type)                
                target_query_set = target_query_generations(prj_id, center, date_va, final_work_packet,level_structure_key)
                targe_master_set = Targets.objects.filter(**target_query_set)
                rawtable_query_set = rawtable_query_generations(prj_id, center, str(date_va), final_work_packet,level_structure_key)
                employee_names = RawTable.objects.filter(**rawtable_query_set).values_list('employee_id')
                employee_count = len(employee_names)
                target_types = Targets.objects.filter(**target_query_set).values('target_type').distinct()
                target_consideration = target_types.filter(target_type = 'Target').values_list('target_value',flat=True).distinct()
                fte_targets_list = target_types.filter(target_type = 'FTE Target').values_list('target_value',flat=True).distinct()
                targets_packets = Targets.objects.filter(project=prj_id, center=center,from_date__lte=date_va,to_date__gte=date_va).values('work_packet','sub_project','sub_packet').distinct()[0]
                if len(target_consideration) > 0 and len(fte_targets_list) > 0:
                    if target_consideration[0] < fte_targets_list[0]:
                        if len(fte_targets_list) > 0:
                            if _targets_list.has_key(final_work_packet):
                                _targets_list[final_work_packet].append(int(fte_targets_list[0]) * employee_count)
                            else:
                                _targets_list[final_work_packet] = [int(fte_targets_list[0]) * employee_count]

                    elif target_consideration[0] >= fte_targets_list[0]:
                        if len(target_consideration) > 0:
                            if _targets_list.has_key(final_work_packet):
                                _targets_list[final_work_packet].append(int(target_consideration[0]))
                            else:
                                _targets_list[final_work_packet] = [int(target_consideration[0])]

                elif len(target_consideration) > 0 and len(fte_targets_list) == 0:
                    if (targets_packets['work_packet'] != '') or (targets_packets['sub_project'] != '') or (targets_packets['sub_packet'] != ''):
                        if _targets_list.has_key(final_work_packet):
                            _targets_list[final_work_packet].append(int(target_consideration[0]))
                        else:
                            _targets_list[final_work_packet] = [int(target_consideration[0])]
                    else:
                        if level_structure_key['work_packet'] == "All":
                            if _targets_list.has_key(prj_name[0]):
                                _targets_list[prj_name[0]].append(int(target_consideration[0]))
                                break
                            else:
                                _targets_list[prj_name[0]] = [int(target_consideration[0])]
                                break

                elif len(target_consideration) == 0 and len(fte_targets_list) > 0:
                    if _targets_list.has_key(final_work_packet):
                         _targets_list[final_work_packet].append(int(fte_targets_list[0]) * employee_count)
                    else:
                        _targets_list[final_work_packet] = [int(fte_targets_list[0]) * employee_count]
                else:
                    if _targets_list.has_key(final_work_packet):
                        _targets_list[final_work_packet].append(0)
                    else:
                        _targets_list[final_work_packet] = [0]

                if not final_work_packet:
                        final_work_packet = level_hierarchy_key(volume_list[count], vol_type)
                count = count + 1

            count = 0
            for vol_type in volume_list:
                if level_structure_key.has_key('sub_project'):
                    local_level_hierarchy_key = vol_type
                else:
                    local_level_hierarchy_key = level_structure_key
                final_work_packet = level_hierarchy_key(local_level_hierarchy_key, vol_type)
                if not final_work_packet:
                        final_work_packet = level_hierarchy_key(volume_list[count], vol_type)
                count = count + 1
                date_pattern = '{0}_{1}_{2}_{3}'.format(prj_name[0], str(center_name[0]), str(final_work_packet),date_va)
                key_list = conn.keys(pattern=date_pattern)
                if not key_list:
                    if date_values.has_key(final_work_packet):
                        date_values[final_work_packet].append(0)
                    else:
                        date_values[final_work_packet] = [0]
                var = [conn.hgetall(cur_key) for cur_key in key_list]
                for one in var:
                    main = one.items()[0]
                    key = main[0]
                    value = main[1]
                    if value == 'None':
                        value = 0
                    if date_values.has_key(key):
                        date_values[key].append(int(value))
                    else:
                        date_values[key] = [int(value)]
    total = 0
    wp_lenght = date_values.keys()
    if len(wp_lenght)>0:
        wp_lenght = date_values[wp_lenght[0]]
    else:
        wp_lenght = ''
    for i in xrange(len(wp_lenght)):
        packet_sum = 0
        for key in date_values.keys():
            try:
                packet_sum += date_values[key][i]
            except:
                packet_sum = packet_sum
        final_values['total_workdone'].append(packet_sum)
        total = total + 1
    volumes_dict = final_values
    new_dict = previous_sum(volumes_dict)
    result = 0
    if len(_targets_list)>0:
        first_key = _targets_list[_targets_list.keys()[0]]
    else:
        first_key = ''
    for i in xrange(len(first_key)):
        packet_sum = 0
        for key in _targets_list.keys():
            try:
                packet_sum += _targets_list[key][i]
            except:
                packet_sum = packet_sum
        final_targets['total'].append(packet_sum)
        result = result + 1
    total_target = previous_sum(final_targets)
    new_total_target = {}
    for tr_key, tr_value in total_target.iteritems():
        new_total_target[tr_key + '_target'] = tr_value
    new_dict.update(new_total_target)
    #print datetime.now() - startTime
    return new_dict

def monthly_volume(request):
    final_dict = {}
    data_date, new_date_list = [], []
    week_names = []
    week_num = 0
    month_names = []
    monthly_vol_data = {}
    monthly_vol_data['total_workdone'] = []
    monthly_vol_data['total_target'] = []
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
            for date_va in sing_list:
                total_done_value = RawTable.objects.filter(project=prj_id,center=center,date=date_va).aggregate(Max('per_day'))
                if total_done_value['per_day__max'] > 0:
                    new_date_list.append(date_va)
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            monthly_volume_graph_details = Monthly_Volume_graph(main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0],sing_list,level_structure_key)
            final_dict['monthly_volume_graph_details'] = graph_data_alignment_color(monthly_volume_graph_details, 'data',level_structure_key,main_data_dict['pro_cen_mapping'][0][0], main_data_dict['pro_cen_mapping'][1][0],'monthly_volume') 
            final_dict['date'] = new_date_list
    elif main_data_dict['dwm_dict'].has_key('week') and main_data_dict['type'] == 'week':
        for sing_list in main_dates_list:
            data_date.append(sing_list[0] + ' to ' + sing_list[-1])
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            monthly_volume_graph_details = Monthly_Volume_graph(main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0],sing_list,level_structure_key)
            for vol_cumulative_key,vol_cumulative_value in monthly_volume_graph_details.iteritems():
                if len(vol_cumulative_value) > 0:
                    monthly_vol_data[vol_cumulative_key].append(vol_cumulative_value[-1])
                else:
                    monthly_vol_data[vol_cumulative_key].append(0)
        monthly_work_done = monthly_vol_data['total_workdone'].count(0)
        monthly_total_target = monthly_vol_data['total_target'].count(0)
        if monthly_work_done == len(monthly_vol_data['total_workdone']) and monthly_total_target == len(monthly_vol_data['total_target']) :
            monthly_vol_data = {}
        final_montly_vol_data = previous_sum(monthly_vol_data)
        final_dict['monthly_volume_graph_details'] = graph_data_alignment_color(final_montly_vol_data, 'data', level_structure_key,prj_id, center)
        final_dict['monthly_volume_graph_details'] = graph_data_alignment_color(final_montly_vol_data, 'data', level_structure_key,prj_id, center,'monthly_volume')
        final_dict['date'] = data_date
    else:
        for month_na,month_va in zip(main_data_dict['dwm_dict']['month']['month_names'],main_data_dict['dwm_dict']['month']['month_dates']):
            month_name = month_na
            month_dates = month_va
            data_date.append(month_dates[0] + ' to ' + month_dates[-1])
            month_names.append(month_name)
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            monthly_volume_graph_details = Monthly_Volume_graph(prj_id, center, month_dates,level_structure_key)
            for vol_cumulative_key, vol_cumulative_value in monthly_volume_graph_details.iteritems():
                if len(vol_cumulative_value) > 0:
                    monthly_vol_data[vol_cumulative_key].append(vol_cumulative_value[-1])
                else:
                    monthly_vol_data[vol_cumulative_key].append(0)
        monthly_work_done = monthly_vol_data['total_workdone'].count(0)
        monthly_total_target = monthly_vol_data['total_target'].count(0)
        if monthly_work_done == len(monthly_vol_data['total_workdone']) and monthly_total_target == len(monthly_vol_data['total_target']):
            monthly_vol_data = {}
        final_montly_vol_data = previous_sum(monthly_vol_data)
        final_dict['monthly_volume_graph_details'] = graph_data_alignment_color(final_montly_vol_data, 'data',level_structure_key, prj_id, center)
        final_dict['monthly_volume_graph_details'] = graph_data_alignment_color(final_montly_vol_data, 'data',level_structure_key, prj_id, center,'monthly_volume')    
        final_dict['date'] = data_date
    final_dict['type'] = main_data_dict['type']
    return json_HttpResponse(final_dict)
