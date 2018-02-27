
import datetime
import redis
from api.models import *
from api.basics import *
from django.db.models import Max, Sum, Count
from api.query_generations import *
from collections import OrderedDict
from api.commons import data_dict
from api.graph_settings import graph_data_alignment_color
from common.utils import getHttpResponse as json_HttpResponse


def volume_cumulative_data(date_list, prj_id, center, level_structure_key):

    date_values, dct = {}, {}
    emp_dict, _dict = {}, {}
    new_date_list = []
    volumes_dict, _targets_list, final_values, final_targets = {}, {}, {}, {}
    final_values['total_workdone'], final_targets['total'] = [], []
    data_list, final_target, final_done_value, volume_list = [], [], [], []
    tar_count, done_value = 0, 0 

    targets, raw_query, _type = get_target_query_format(level_structure_key, prj_id, center, date_list)
    data_values = raw_query
    prod_packets = [value[1] for value in data_values]
    dates = raw_query.values_list('date',flat=True).distinct()
    packets = set(prod_packets)

    for date in dates:
        for target in targets:
            if (target[2] in packets) and (str(target[0]) <= str(date) and str(target[1]) >= str(date)):
                if _targets_list.has_key(target[2]):
                    _targets_list[target[2]].append(target[3])
                else:
                    _targets_list[target[2]] = [target[3]]

    for key in packets:
       date_values.update({key:[]})
       emp_dict.update({key:[]}) 
    for i, val in enumerate(data_values):
        if i:
            date,packet,done,emp_count = val
            if i < len(data_values)-1:
                nxt_date, nxt_packet, nxt_done, nxt_count = data_values[i+1]
                dct.update({packet:emp_count})
                _dict.update({packet:done}) 
                if nxt_date != date:
                    for packet in packets:
                        dict_val = date_values[packet]
                        emp_val = emp_dict[packet]
                        dict_val.append(dct.setdefault(packet,0))
                        emp_val.append(_dict.setdefault(packet,0)) 
                        date_values.update({packet:dict_val})
                        emp_dict.update({packet:emp_val}) 
                    dct = {}
                    _dict = {}
            else:
                p_date, p_packet, p_done, p_count = data_values[i-1]
                if p_date != date:
                    dct = {}
                    _dict = {}
                dct.update({packet:emp_count})
                _dict.update({packet:done}) 
                for packet in packets:
                    dict_val = date_values[packet]
                    emp_val = emp_dict[packet]
                    dict_val.append(dct.setdefault(packet,0))
                    emp_val.append(_dict.setdefault(packet,0))
                    date_values.update({packet:dict_val})
                    emp_dict.update({packet:emp_val})

    import collections
    if _type == 'FTE Target':
        emp_data = collections.OrderedDict(sorted(emp_dict.items()))
        target_data = collections.OrderedDict(sorted(_targets_list.items()))

        target_dict = {}
        for key, value in target_data.iteritems():
            value = zip(target_data[key], emp_data[key])
            target_dict[key] = [tar*val for tar, val in value]
        _targets_list = target_dict
    else:
        _targets_list = _targets_list

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
    return new_dict


def get_target_query_format(level_structure_key, prj_id, center, date_list):
    
    query, raw_data = {}, {}
    pro_query, pro_data = {}, {}
    _term = ''
    _type = Targets.objects.filter(project=prj_id, center=center).values_list('target_type',flat=True).distinct()
    if 'FTE Target' in _type:
        query['from_date__lte'] = date_list[0]
        query['to_date__gte'] = date_list[-1]
        query['target_type'] = 'FTE Target'
        pro_query['from_date__lte'] = date_list[0]
        pro_query['to_date__gte'] = date_list[-1]
        pro_query['target_type'] = 'FTE Target'
        _type = 'FTE Target'
    else:
        query['from_date__gte'] = date_list[0]
        query['to_date__lte'] = date_list[-1]
        query['target_type'] = 'Target'
        pro_query['from_date__gte'] = date_list[0]
        pro_query['to_date__lte'] = date_list[-1]
        pro_query['target_type'] = 'Target'
        _type = 'Target'
    query['project'] = prj_id
    query['center'] = center
    pro_query['project'] = prj_id
    pro_query['center'] = center
    raw_data['project'] = prj_id
    raw_data['center'] = center
    raw_data['date__range'] = [date_list[0], date_list[-1]]
    pro_data['project'] = prj_id
    pro_data['center'] = center
    pro_data['date__range'] = [date_list[0], date_list[-1]]
    sub_packet = level_structure_key.get('sub_packet', '')

    target_query = Targets.objects.filter(**pro_query)
    packet_1 = target_query.values_list('sub_project', flat=True).distinct()
    packet_2 = target_query.values_list('work_packet', flat=True).distinct()
    packet_3 = target_query.values_list('sub_packet', flat=True).distinct()

    if level_structure_key.has_key('sub_project'):
        if level_structure_key['sub_project'] == 'All':
            _term = 'sub_project'
        elif level_structure_key['sub_project'] != 'All' and level_structure_key['work_packet'] == 'All':
            query['sub_project'] = level_structure_key['sub_project']
            raw_data['sub_project'] = level_structure_key['sub_project']
            _term = 'sub_project'
        elif level_structure_key['sub_project'] != 'All' and level_structure_key['work_packet'] != 'All' and \
                level_structure_key['sub_packet'] == 'All':
            query['sub_project'] = level_structure_key['sub_project']
            query['work_packet'] = level_structure_key['work_packet']
            raw_data['sub_project'] = level_structure_key['sub_project']
            raw_data['work_packet'] = level_structure_key['work_packet']
            _term = 'work_packet'
        elif level_structure_key['sub_project'] != 'All' and level_structure_key['work_packet'] != 'All' and\
                level_structure_key['sub_packet'] != 'All':
            query['sub_project'] = level_structure_key['sub_project']
            query['work_packet'] = level_structure_key['work_packet']
            query['sub_packet'] = level_structure_key['sub_packet']
            raw_data['sub_project'] = level_structure_key['sub_project']
            raw_data['work_packet'] = level_structure_key['work_packet']
            raw_data['sub_packet'] = level_structure_key['sub_packet']
            _term = 'sub_packet'
    elif level_structure_key.has_key('work_packet'):
        if level_structure_key['work_packet'] == 'All':
            _term = 'work_packet'
        elif level_structure_key['work_packet'] != 'All' and sub_packet == 'All':
            query['work_packet'] = level_structure_key['work_packet']
            raw_data['work_packet'] = level_structure_key['work_packet']
            _term = 'work_packet'
        elif level_structure_key['work_packet'] != 'All' and level_structure_key.has_key('sub_packet'):
            if level_structure_key['sub_packet'] != 'All':
                query['work_packet'] = level_structure_key['work_packet']
                query['sub_packet'] = level_structure_key['sub_packet']
                raw_data['work_packet'] = level_structure_key['work_packet']
                raw_data['sub_packet'] = level_structure_key['sub_packet']
                _term = 'sub_packet'
        elif level_structure_key['work_packet'] != 'All':
            query['work_packet'] = level_structure_key['work_packet']
            raw_data['work_packet'] = level_structure_key['work_packet']
            _term = 'work_packet'

    targets = Targets.objects.filter(**query).values_list('from_date','to_date',_term).\
              annotate(target=Sum('target_value'))
    raw_query = RawTable.objects.filter(**raw_data).values_list('date',_term).annotate(total=Sum('per_day'),count=Count('employee_id'))
   
    return targets, raw_query, _type


"""def Monthly_Volume_graph(prj_id,center,date_list, level_structure_key):
    from datetime import datetime
    startTime = datetime.now()
    data_list, final_target, final_done_value, volume_list = [], [], [], [] 
    conn = redis.Redis(host="localhost", port=6379, db=0)
    date_values, date_targets = {}, {} 
    tar_count, done_value = 0, 0 
    #prj_name = Project.objects.filter(id=prj_id).values_list('name', flat=True)
    #center_name = Center.objects.filter(id=center).values_list('name', flat=True)
    project = Project.objects.filter(id=prj_id)
    prj_name = project[0].name
    center_name = project[0].center.name
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
    total_done_value = RawTable.objects.filter(project=prj_id, center=center, date__range=[date_list[0], date_list[-1]]).values('date').annotate(total=Sum('per_day'))
    values = OrderedDict(zip(map(lambda p: str(p['date']), total_done_value), map(lambda p: str(p['total']), total_done_value)))
    for date_va, total_val in values.iteritems():
    #for date_va in date_list:
        #total_done_value = RawTable.objects.filter(project=prj_id, center=center, date=date_va).aggregate(Max('per_day'))
        #if total_done_value['per_day__max'] > 0:
        if total_val > 0:
            #new_date_list.append(str(date_va))
            new_date_list.append(date_va)
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
                        if fte_targets_list:
                            if _targets_list.has_key(final_work_packet):
                                _targets_list[final_work_packet].append(int(fte_targets_list[0]) * employee_count)
                            else:
                                _targets_list[final_work_packet] = [int(fte_targets_list[0]) * employee_count]

                    elif target_consideration[0] >= fte_targets_list[0]:
                        if target_consideration:
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
                date_pattern = '{0}_{1}_{2}_{3}'.format(prj_name, center_name, str(final_work_packet),date_va)
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
    #new_total_target['date'] = new_date_list
    new_dict.update(new_total_target)
    #print datetime.now() - startTime
    #new_dict['date'] = new_date_list
    return new_dict"""


