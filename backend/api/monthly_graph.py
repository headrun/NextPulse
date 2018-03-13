
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

    for date in dates:
        _dict_packets = []
        for value in data_values:
            if str(date) == str(value[0]):
                if date_values.has_key(value[1]):
                    date_values[value[1]].append(value[3])
                    emp_dict[value[1]].append(value[2])
                else:
                    date_values[value[1]] = [value[3]]
                    emp_dict[value[1]] = [value[2]]
                _dict_packets.append(value[1])

        for pack in packets:
            if pack not in _dict_packets:
                if date_values.has_key(pack):
                    date_values[pack].append(0)
                    emp_dict[pack].append(0)
                else:
                    date_values[pack] = [0]
                    emp_dict[pack] = [0]


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
        query.update({'from_date__lte':date_list[0],'to_date__gte':date_list[-1],'target_type':'FTE Target',\
                        'project':prj_id,'center':center})
        pro_query.update({'from_date__gte':date_list[0],'to_date__lte':date_list[-1],'target_type':'FTE Target',\
                        'project':prj_id,'center':center})
        _type = 'FTE Target'
    else:
        query.update({'from_date__gte':date_list[0],'to_date__lte':date_list[-1],'target_type':'Target',\
                        'project':prj_id,'center':center})
        pro_query.update({'from_date__lte':date_list[0],'to_date__gte':date_list[-1],'target_type':'Target',\
                            'project':prj_id,'center':center})
        _type = 'Target'
    raw_data.update({'project':prj_id,'center':center,'date__range':[date_list[0], date_list[-1]]})
    pro_data.update({'project':prj_id,'center':center,'date__range':[date_list[0],date_list[-1]]})
    sub_packet = level_structure_key.get('sub_packet', '')
    target_query = Targets.objects.filter(**pro_query)
    packet_1 = target_query.values_list('sub_project', flat=True).distinct()
    packet_2 = target_query.values_list('work_packet', flat=True).distinct()
    packet_3 = target_query.values_list('sub_packet', flat=True).distinct()
    if level_structure_key.has_key('sub_project'):
        if level_structure_key['sub_project'] == 'All':
            _term = 'sub_project'
        elif level_structure_key['sub_project'] != 'All' and level_structure_key['work_packet'] == 'All':
            query.update({'sub_project':level_structure_key['sub_project']})
            pro_query.update({'sub_project':level_structure_key['sub_project']})
            raw_data.update({'sub_project':level_structure_key['sub_project']})
            _term = 'sub_project'
        elif level_structure_key['sub_project'] != 'All' and level_structure_key['work_packet'] != 'All' and \
                level_structure_key['sub_packet'] == 'All':
            query.update({'sub_project':level_structure_key['sub_project'],'work_packet':level_structure_key['work_packet']})
            pro_query.update({'sub_project':level_structure_key['sub_project'],'work_packet':level_structure_key['work_packet']})
            raw_data.update({'sub_project':level_structure_key['sub_project'],'work_packet':level_structure_key['work_packet']})
            _term = 'work_packet'
        elif level_structure_key['sub_project'] != 'All' and level_structure_key['work_packet'] != 'All' and\
                level_structure_key['sub_packet'] != 'All':
            query.update({'sub_project':level_structure_key['sub_project'],'work_packet':level_structure_key['work_packet'],\
                        'sub_packet':level_structure_key['sub_packet']})
            pro_query.update({'sub_project':level_structure_key['sub_project'],'work_packet':level_structure_key['work_packet'],\
                        'sub_packet':level_structure_key['sub_packet']})
            raw_data.update({'sub_project':level_structure_key['sub_project'],'work_packet':level_structure_key['work_packet'],\
                            'sub_packet':level_structure_key['sub_packet']})
            _term = 'sub_packet'
    elif level_structure_key.has_key('work_packet'):
        if level_structure_key['work_packet'] == 'All':
            _term = 'work_packet'
        elif level_structure_key['work_packet'] != 'All' and sub_packet == 'All':
            query.update({'work_packet':level_structure_key['work_packet']})
            pro_query.update({'work_packet':level_structure_key['work_packet']})
            raw_data.update({'work_packet':level_structure_key['work_packet']})
            _term = 'work_packet'
        elif level_structure_key['work_packet'] != 'All' and level_structure_key.has_key('sub_packet'):
            if level_structure_key['sub_packet'] != 'All':
                query.update({'work_packet':level_structure_key['work_packet'],'sub_packet':level_structure_key['sub_packet']})
                pro_query.update({'work_packet':level_structure_key['work_packet'],'sub_packet':level_structure_key['sub_packet']})
                raw_data.update({'work_packet':level_structure_key['work_packet'],'sub_packet':level_structure_key['sub_packet']})
                _term = 'sub_packet'
        elif level_structure_key['work_packet'] != 'All':
            query.update({'work_packet':level_structure_key['work_packet']})
            pro_query.update({'work_packet':level_structure_key['work_packet']})
            raw_data.update({'work_packet':level_structure_key['work_packet']})
            _term = 'work_packet'
    
    targets = Targets.objects.filter(**query).values_list('from_date','to_date',_term).\
              annotate(target=Sum('target_value'))
    if targets:
        targets = targets
    else:
        targets = Targets.objects.filter(**pro_query).values_list('from_date','to_date',_term).\
                    annotate(target=Sum('target_value'))
    raw_query = RawTable.objects.filter(**raw_data).values_list('date',_term).annotate(total=Sum('per_day'),count=Count('employee_id'))
   
    return targets, raw_query, _type





def productivity_day(date_list, prj_id, center_obj, level_structure_key):

    packet_names = Headcount.objects.filter(project=prj_id, center=center_obj, date__range=[date_list[0],date_list[-1]]).values('sub_project', 'work_packet', 'sub_packet').distinct()
    count  = 0;
    for i in packet_names:
        if all(value == '' for value in i.values()):
            count = count + 1;
    filter_params, _term = getting_required_params(level_structure_key, prj_id, center_obj, date_list)
    data_dict = {};
    status = 0

    if level_structure_key.get('sub_project','') == 'All':
        status = 1

    elif level_structure_key.get('sub_project','') == '' and level_structure_key.get('work_packet','') == 'All':
        status = 1

    if status and count:
        query_values = RawTable.objects.filter(**filter_params)
        data_values = query_values.values_list('date').annotate(total=Sum('per_day'))
        headcount = Headcount.objects.filter(**filter_params).values_list('date').annotate(head_c=Sum('billable_agents'))
        value_lst = []

        for data_v in data_values:
            for head_v in headcount:
                if data_v[0] == head_v[0]:
                    if head_v[1] > 0:
                        val = float('%.2f' % round(float(data_v[1])/float(head_v[1]),2))
                    else:
                        val = 0
                    value_lst.append(val)
                else:
                    pass
        data_dict['Total Productivity'] = value_lst
    else:
        if packet_names:
            dates_pack = RawTable.objects.filter(project=prj_id, center=center_obj,date__range=[date_list[0],date_list[-1]]).values_list('date', flat=True).distinct()
            raw_query = RawTable.objects.filter(**filter_params)
            raw_value = raw_query.values('date','sub_project','work_packet','sub_packet').annotate(total=Sum('per_day'))
            headcount = Headcount.objects.filter(**filter_params).values('date','sub_project','work_packet','sub_packet').annotate(head_c=Sum('billable_agents'))
            if _term == 'sub_project':
                packet_details = raw_query.values_list(_term, flat=True).distinct()
            elif _term == 'work_packet':
                packet_details = raw_query.values_list(_term, flat=True).distinct()
            elif _term == 'sub_packet':
                packet_details = raw_query.values_list(_term, flat=True).distinct()
            else:
                packet_details = raw_query.values_list('sub_packet', flat=True).distinct()

            prod_trend = []
            for data_v in raw_value:
                for head_v in headcount:
                    if (data_v['date'] == head_v['date']):
                        if (head_v['sub_project'] == '' and  head_v['work_packet'] != '' and head_v['sub_packet'] == ''):
                            if (data_v['work_packet'].lower() == head_v['work_packet'].lower()):
                                pack = data_v['work_packet'].lower()
                                pack = pack.title()
                                if head_v['head_c'] > 0:
                                    prod_trend.append({'date': data_v['date'] , 'work_packet': pack, 'result': float(data_v['total']/head_v['head_c']) })
                                else:
                                    prod_trend.append({'date': data_v['date'] , 'work_packet': pack, 'result': 0 })
                        elif (head_v['sub_project'] != '' and head_v['work_packet'] == '' and head_v['sub_packet'] == ''):
                            if (data_v['sub_project'].lower() == head_v['sub_project'].lower()):
                                pack = data_v['sub_project'].lower()
                                pack = pack.title()
                                if head_v['head_c'] > 0:
                                    prod_trend.append({'date': data_v['date'], 'sub_project': pack, 'result': float(data_v['total']/head_v['head_c']) })
                                else:
                                    prod_trend.append({'date': data_v['date'] , 'work_packet': pack, 'result': 0 })

                        elif (head_v['sub_project'] != '' and head_v['work_packet'] != '' and head_v['sub_packet'] == ''):
                            if (data_v['sub_project'].lower() == head_v['sub_project'].lower() and data_v['work_packet'].lower() == head_v['work_packet'].lower()):
                                pack = data_v['sub_project'].lower()
                                pack = pack.title()
                                pack_1 = data_v['work_packet'].lower()
                                pack_1 = pack_1.title()
                                if head_v['head_c'] > 0:
                                    prod_trend.append({'date': data_v['date'], 'sub_project':pack, 'work_packet': pack_1 , 'result': float(data_v['total']/head_v['head_c'])})
                                else:
                                    prod_trend.append({'date': data_v['date'], 'sub_project':pack, 'work_packet': pack_1 , 'result': 0 })

                        elif (head_v['sub_project'] != '' and head_v['work_packet'] != '' and head_v['sub_packet'] != ''):
                            if (data_v['sub_project'].lower() == head_v['sub_project'].lower() and data_v['work_packet'].lower() == head_v['work_packet'].lower() and data_v['sub_packet'].lower() == head_v['sub_packet'].lower()):
                                pack = data_v['sub_project'].lower()
                                pack = pack.title()
                                pack_1 = data_v['work_packet'].lower()
                                pack_1 = pack_1.title()
                                pack_2 = data_v['sub_packet'].lower()
                                pack_2 = pack_2.title()
                                if head_v['head_c'] > 0:
                                    prod_trend.append({'date': data_v['date'], 'sub_project':pack, 'work_packet': pack_1 , 'sub_packet':  pack_2, 'result': float(data_v['total']/head_v['head_c']) })
                                else:
                                    prod_trend.append({'date': data_v['date'], 'sub_project':pack, 'work_packet': pack_1 , 'sub_packet': pack_2, 'result': 0 })
                        elif (head_v['sub_project'] =='' and head_v['work_packet'] != '' and head_v['sub_packet'] != ''):
                            if (data_v['work_packet'].lower() == head_v['work_packet'].lower() and  data_v['sub_packet'].lower() == head_v['sub_packet'].lower()):
                                pack = data_v['work_packet'].lower()
                                pack = pack.title()
                                pack_1 = data_v['sub_packet'].lower()
                                pack_1 = pack_1.title()
                                if head_v['head_c'] > 0:
                                    prod_trend.append({ 'date': data_v['date'], 'work_packet': pack, 'sub_packet': pack_1, 'result': float(data_v['total']/head_v['head_c']) })
                                else:
                                    prod_trend.append({ 'date': data_v['date'], 'work_packet': pack, 'sub_packet': pack_1, 'result': 0 })

            for check_date in dates_pack:
                packet_list = []
                content_list = []
                for index in prod_trend:
                    if str(check_date) == str(index['date']):
                        if (packet_names[0]['sub_project'] == '' and packet_names[0]['work_packet'] != '' and packet_names[0]['sub_packet'] == ''):
                            if ( _term != 'sub_project' and  _term != 'sub_packet'):
                                packet_list.append(index[_term])
                                content_list.append(index['result'])

                        elif(packet_names[0]['sub_project'] != '' and packet_names[0]['work_packet'] == '' and packet_names[0]['sub_packet'] == ''):
                            if ( _term != 'work_packet' and  _term != 'sub_packet'):
                                packet_list.append(index[_term])
                                content_list.append(index['result'])

                        elif(packet_names[0]['sub_project'] != '' and packet_names[0]['work_packet'] != '' and packet_names[0]['sub_packet'] ==''):
                            if _term != 'sub_packet':
                                packet_list.append(index[_term])
                                content_list.append(index['result'])

                        elif (packet_names[0]['sub_project'] == '' and packet_names[0]['work_packet'] != '' and packet_names[0]['sub_packet'] != ''):
                            if _term != 'sub_project':
                                packet_list.append(index[_term])
                                content_list.append(index['result'])
                        else:
                            packet_list.append(index[_term])
                            content_list.append(index['result'])

                if len(packet_list) > 0:
                    packet_list = sorted(list(set(packet_list)))
                    packet_list = map(str, packet_list)
                    for pack in packet_details:
                        pack = str(pack)
                        pack = pack.lower()
                        pack = pack.title()
                        if pack not in packet_list:
                            if (packet_names[0]['sub_project'] == '' and packet_names[0]['work_packet'] != '' and packet_names[0]['sub_packet'] == ''):
                                if _term == 'work_packet':
                                    prod_trend.append({"date": check_date, _term:pack, "result":0})
                            elif(packet_names[0]['sub_project'] != '' and packet_names[0]['work_packet'] == '' and packet_names[0]['sub_packet'] == ''):
                                if _term == 'sub_project':
                                    prod_trend.append({"date": check_date, _term:pack, "result":0})
                            elif(packet_names[0]['sub_project'] != '' and packet_names[0]['work_packet'] != '' and packet_names[0]['sub_packet'] ==''):
                                if _term == 'sub_project':
                                    prod_trend.append({"date": check_date, _term:pack,'work_packet':'' , "result":0})
                                elif _term == 'work_packet':
                                    prod_trend.append({"date": check_date,"sub_project":filter_params['sub_project'], _term:pack, "result":0})
                            elif (packet_names[0]['sub_project'] == '' and packet_names[0]['work_packet'] != '' and packet_names[0]['sub_packet'] != ''):
                                if _term == 'work_packet':
                                    prod_trend.append({"date": check_date,"work_packet": pack, 'sub_packet':'', "result":0})
                                elif _term == 'sub_packet':
                                    prod_trend.append({ "date": check_date, 'work_packet': filter_params['work_packet'], 'sub_packet': pack , "result": 0})
                            elif (packet_names[0]['sub_project'] != '' and packet_names[0]['work_packet'] != '' and packet_names[0]['sub_packet'] != ''):
                                if _term == 'sub_project':
                                    prod_trend.append({"date": check_date, _term:pack,'work_packet':'' ,'sub_packet': '', "result":0})
                                elif _term == 'work_packet':
                                    prod_trend.append({"date": check_date,"sub_project":filter_params['sub_project'], _term:pack, 'sub_packet': '', "result":0})
                                elif _term == 'sub_packet':
                                    prod_trend.append({"date": check_date,"sub_project":filter_params['sub_project'], _term:pack, 'work_packet': filter_params['work_packet'], "result":0})

                if not len(content_list) > 0:
                    for pack in packet_details:
                        pack = str(pack)
                        pack = pack.lower()
                        pack = pack.title()
                        if (packet_names[0]['sub_project'] == '' and packet_names[0]['work_packet'] != '' and packet_names[0]['sub_packet'] == ''):
                            if _term == 'work_packet':
                                prod_trend.append({"date": check_date, _term:pack, "result":0})
                        elif(packet_names[0]['sub_project'] != '' and packet_names[0]['work_packet'] == '' and packet_names[0]['sub_packet'] == ''):
                            if _term == 'sub_project':
                                prod_trend.append({"date": check_date, _term:pack, "result":0})

                        elif(packet_names[0]['sub_project'] != '' and packet_names[0]['work_packet'] != '' and packet_names[0]['sub_packet'] ==''):
                            if _term == 'sub_project':
                                prod_trend.append({"date": check_date, _term:pack,'work_packet':'' , "result":0})
                            elif _term == 'work_packet':
                                prod_trend.append({"date": check_date,"sub_project":filter_params['sub_project'], _term:pack, "result":0})

                        elif (packet_names[0]['sub_project'] == '' and packet_names[0]['work_packet'] != '' and packet_names[0]['sub_packet'] != ''):
                            if _term == 'work_packet':
                                prod_trend.append({"date": check_date,"work_packet": pack, 'sub_packet':'', "result":0})
                            elif _term == 'sub_packet':
                                prod_trend.append({ "date": check_date, 'work_packet': filter_params['work_packet'], 'sub_packet': pack , "result": 0})
                        elif (packet_names[0]['sub_project'] != '' and packet_names[0]['work_packet'] != '' and packet_names[0]['sub_packet'] != ''):
                            if _term == 'sub_project':
                                prod_trend.append({"date": check_date, _term:pack,'work_packet':'' ,'sub_packet': '', "result":0})
                            elif _term == 'work_packet':
                                prod_trend.append({"date": check_date,"sub_project":filter_params['sub_project'], _term:pack, 'sub_packet': '', "result":0})
                            elif _term == 'sub_packet':
                                prod_trend.append({"date": check_date,"sub_project":filter_params['sub_project'], _term:pack, 'work_packet': filter_params['work_packet'], "result":0})

            if (packet_names[0]['sub_project'] == '' and packet_names[0]['work_packet'] != '' and packet_names[0]['sub_packet'] == ''):
                if _term == 'work_packet':
                    tmp_obj = _term_function(_term, prod_trend, 1)
                    fte_trend_data, data_dict = tmp_obj_handling(tmp_obj, "sub-project")

            elif(packet_names[0]['sub_project'] != '' and packet_names[0]['work_packet'] == '' and packet_names[0]['sub_packet'] == ''):
                if _term == 'sub_project':
                    tmp_obj = _term_function(_term, prod_trend, 1)
                    fte_trend_data, data_dict = tmp_obj_handling(tmp_obj, "sub-project")
                if _term == 'work_packet':
                    tmp_obj = _term_function('sub_project', prod_trend, 1)
                    fte_trend_data, data_dict = tmp_obj_handling(tmp_obj, "sub-project")

            elif(packet_names[0]['sub_project'] != '' and packet_names[0]['work_packet'] != '' and packet_names[0]['sub_packet'] ==''):
                if _term == 'sub_project':
                    tmp_obj = _term_function(_term, prod_trend, 1)
                    fte_trend_data, data_dict = tmp_obj_handling(tmp_obj, "sub-project")
                elif _term == 'work_packet':
                    tmp_obj = _term_function(_term, prod_trend, 2)
                    fte_trend_data, data_dict = tmp_obj_handling(tmp_obj, "sub-packet__work-packet")

            elif(packet_names[0]['sub_project'] != '' and packet_names[0]['work_packet'] != '' and packet_names[0]['sub_packet'] != '' ):
                if _term == 'sub_project':
                    tmp_obj = _term_function(_term, prod_trend, 1)
                    fte_trend_data, data_dict = tmp_obj_handling(tmp_obj, "sub-project")
                elif _term == 'work_packet':
                    tmp_obj = _term_function(_term, prod_trend, 2)
                    fte_trend_data, data_dict = tmp_obj_handling(tmp_obj, "sub-packet__work-packet")
                else:
                    tmp_obj = {}
                    for tmp in prod_trend:
                        if tmp_obj.has_key(str(tmp['date'])):
                            if tmp_obj[str(tmp['date'])].has_key(tmp['sub_project']+"__"+tmp['work_packet']+"__"+tmp['sub_packet']):
                                tmp_obj[str(tmp['date'])][tmp['sub_project']+"__"+tmp['work_packet']+"__"+tmp['sub_packet'] ]= tmp_obj[str(tmp['date'])][tmp['sub_project']+"__"+tmp['work_packet']+"__"+tmp['sub_packet']] + tmp['result']
                            else:
                                tmp_obj[str(tmp['date'])].update({tmp['sub_project']+"__"+tmp['work_packet']+"__"+tmp['sub_packet'] : tmp['result']})
                        else:
                            tmp_obj[str(tmp['date'])] = {tmp['sub_project']+"__"+tmp['work_packet']+"__"+tmp['sub_packet'] : tmp['result']}

                    fte_trend_data, data_dict = tmp_obj_handling(tmp_obj, "sub-project__work-packet__sub-packet")

            elif (packet_names[0]['sub_project'] == '' and packet_names[0]['work_packet'] != '' and packet_names[0]['sub_packet'] != ''):
                if _term == 'work_packet':
                    tmp_obj = _term_function(_term, prod_trend, 1)
                    fte_trend_data, data_dict = tmp_obj_handling(tmp_obj, "sub-project")
                elif _term == 'sub_packet':
                    tmp_obj = {}
                    for tmp in prod_trend:
                        if tmp_obj.has_key(str(tmp['date'])):
                            if tmp_obj[str(tmp['date'])].has_key(tmp['work_packet']+'__'+tmp['sub_packet']):
                                tmp_obj[str(tmp['date'])][tmp['work_packet']+'__'+tmp['sub_packet']] = tmp_obj[str(tmp['date'])][tmp['work_packet']+'__'+tmp['sub_packet']] + tmp['result']
                            else:
                                tmp_obj[str(tmp['date'])].update({tmp['work_packet']+'__'+tmp['sub_packet'] : tmp['result']})
                        else:
                            tmp_obj[str(tmp['date'])] = {tmp['work_packet']+'__'+tmp['sub_packet'] : tmp['result']}

                    fte_trend_data, data_dict = tmp_obj_handling(tmp_obj, "sub-packet__work-packet")
        else:
            data_dict = {}
    final_dict = data_dict
    return final_dict


def _term_function(_term, prod_trend, packet_level):

    if packet_level == 1:
        tmp_obj = {}
        for tmp in prod_trend:
            if tmp_obj.has_key(str(tmp['date'])):
                if tmp_obj[str(tmp['date'])].has_key(tmp[_term]):
                    tmp_obj[str(tmp['date'])][tmp[_term]] = tmp_obj[str(tmp['date'])][tmp[_term]] + tmp['result']
                else:
                    tmp_obj[str(tmp['date'])].update({tmp[_term] : tmp['result']})
            else:
                tmp_obj[str(tmp['date'])] = {tmp[_term] : tmp['result']}

    elif packet_level == 2:
        tmp_obj = {}
        for tmp in prod_trend:
            if tmp_obj.has_key(str(tmp['date'])):
                if tmp_obj[str(tmp['date'])].has_key(tmp['sub_project']+'__'+tmp['work_packet']):
                    tmp_obj[str(tmp['date'])][tmp['sub_project']+'__'+tmp['work_packet']] = tmp_obj[str(tmp['date'])][tmp['sub_project']+'__'+tmp['work_packet']] + tmp['result']
                else:
                    tmp_obj[str(tmp['date'])].update({tmp['sub_project']+'__'+tmp['work_packet'] : tmp['result']})
            else:
                tmp_obj[str(tmp['date'])] = {tmp['sub_project']+'__'+tmp['work_packet'] : tmp['result']}

    return tmp_obj


def tmp_obj_handling(tmp_obj, packet_level):

    import collections
    data_dict = {}
    if packet_level == "sub-project":
        ordi = collections.OrderedDict(tmp_obj)
        tmp_obj = sorted(ordi.items(), key=lambda x: x)
        fte_trend_data = []
        for tk in tmp_obj:
            val = 0
            for k, v in tk[1].iteritems():
                v = float('%.2f' % round(v, 2))
                if not data_dict.has_key(k):
                    data_dict[k] = [v]
                else:
                    data_dict[k].append(v)
                val += v
            val = float('%.2f' % round(val, 2))
            fte_trend_data.append(val)

    elif packet_level == "work-packet__sub-packet":
        ordi = collections.OrderedDict(tmp_obj)
        tmp_obj = sorted(ordi.items(), key=lambda x: x)
        for tk in tmp_obj:
            val = 0
            for k, v in tk[1].iteritems():
                v = float('%.2f' % round(v, 2))
                key = k.split("__")
                if not data_dict.has_key(key[0]):
                    data_dict[key[0]] = [v]
                else:
                    data_dict[key[0]].append(v)
                val += v
            val = float('%.2f' % round(val, 2))
            fte_trend_data.append(val)

    elif packet_level == "sub-packet__work-packet":
        ordi = collections.OrderedDict(tmp_obj)
        tmp_obj = sorted(ordi.items(), key=lambda x: x)
        fte_trend_data = []
        for tk in tmp_obj:
            val = 0
            for k, v in tk[1].iteritems():
                key = k.split('__')
                v = float('%.2f' % round(v, 2))
                if not data_dict.has_key(key[1]):
                    data_dict[key[1]] = [v]
                else:
                    data_dict[key[1]].append(v)

                val += v
            val = float('%.2f' % round(val, 2))
            fte_trend_data.append(val)

    elif packet_level == "sub-project__work-packet__sub-packet":
        ordi = collections.OrderedDict(tmp_obj)
        tmp_obj = sorted(ordi.items(), key=lambda x: x)
        fte_trend_data = []
        for tk in tmp_obj:
            val = 0
            for k, v in tk[1].iteritems():
                key = k.split('__')
                v = float('%.2f' % round(v, 2))
                if not data_dict.has_key(key[2]):
                    data_dict[key[2]] = [v]
                else:
                    data_dict[key[2]].append(v)
                val += v
            val = float('%.2f' % round(val, 2))
            fte_trend_data.append(val)

    return fte_trend_data, data_dict



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


