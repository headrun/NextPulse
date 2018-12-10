
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


def volume_cumulative_data(date_list, prj_id, center, level_structure_key,main_dates,request):

    date_values, dct = {}, {}
    emp_dict, _dict = {}, {}
    new_date_list = []
    volumes_dict, _targets_list, final_values, final_targets = {}, {}, {}, {}
    final_values['total_workdone'], final_targets['total'] = [], []
    data_list, final_target, final_done_value, volume_list = [], [], [], []
    tar_count, done_value = 0, 0 

    targets, targ_query, raw_query, raw_data,  _type, _term = get_target_query_format(level_structure_key, prj_id, center, date_list)
    data_values = raw_query
	
    g = {}
    for i in raw_data:
        if g.has_key(i['date']):
            if g.get(i["date"], {}).has_key(i['employee_id']):
                g[i["date"]][i["employee_id"]][i[_term]]=i["count"]
            else:
                g[i["date"]][i["employee_id"]]={}
                g[i["date"]][i["employee_id"]][i[_term]]=i["count"]
        else:
            g[i["date"]]={}
            g[i["date"]][i["employee_id"]]={i[_term]:i["count"]}        
    
    count3 = {} 
    for k,v in g.iteritems():
        for k1,v1 in v.iteritems():
            for k2,v2 in v1.iteritems():
                if count3.has_key(k):
                    if count3[k].has_key(k2):
                        if len(v1)>1:
                            count3[k][k2].append(float(1/len(v1)))
                        else:
                            count3[k][k2].append(1)
                    else:
                        count3[k][k2]=[1]
                else:
                    count3[k] = {k2:[1]}                 
    
    sum_count = {}
    for k,v in count3.iteritems():
        for k1,v1 in v.iteritems():                  
            if sum_count.has_key(k):                
                sum_count[k][k1] = sum(v1)                           
            else:
                sum_count[k] = {}  
                sum_count[k][k1] = sum(v1)      

    if raw_query:
        prod_packets = [value[1] for value in data_values]        
        dates = raw_query.values_list('date',flat=True).distinct()
        packets = set(prod_packets)    
    else:
        dates = []

    for date in dates:
        _dict_packet = []
        for target in targets:                                            
            if (target[2] in packets) and (str(target[0]) <= str(date) and str(target[1]) >= str(date)):                                
                target_val = float('%.2f' % round(target[3]))
                if _targets_list.has_key(target[2]):
                    _targets_list[target[2]].append(target_val)                    
                else:
                    _targets_list[target[2]] = [target_val]   
                _dict_packet.append(target[2])
                
        for pact in packets:            
            if pact not in _dict_packet:               
                if _targets_list.has_key(pact):
                    _targets_list[pact].append(0)                    
                else:
                    _targets_list[pact] = [0]

    for date in dates:
        _dict_packets = []
        for value in data_values:
            if str(date) == str(value[0]):
                if date_values.has_key(value[1]):
                    date_values[value[1]].append(value[3])                    
                else:
                    date_values[value[1]] = [value[3]]                   
                _dict_packets.append(value[1])
        
        for pack in packets:
            if pack not in _dict_packets:
                if date_values.has_key(pack):
                    date_values[pack].append(0)                    
                else:
                    date_values[pack] = [0]                       
    
    emp_data1 = {}
    for k,v in sum_count.iteritems():
        _dict_pack = []
        for k1,v1 in v.iteritems():
            if emp_data1.has_key(k1):
                emp_data1[k1].append(v1)
            else:
                emp_data1[k1] = [v1] 
            _dict_pack.append(k1)    
        
        for pac in packets:            
            if pac not in _dict_pack:               
                if emp_data1.has_key(pac):                    
                    emp_data1[pac].append(0)
                else:                    
                    emp_data1[pac] = [0]       
    
    import collections
    if _type == 'FTE Target':              
        target_data = collections.OrderedDict(sorted(_targets_list.items()))
        target_dict = {}
        for key, value in target_data.iteritems():                               
            value = zip(target_data[key], emp_data1[key])            
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
        key_max = max(_targets_list, key= lambda x: len((_targets_list[x])))         
        first_key =  _targets_list[key_max]                  
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
    if _term != "":        
        targets = Targets.objects.filter(**pro_query).values_list('from_date','to_date',_term).\
                  annotate(target=Sum('target_value'))
        targ_query = Targets.objects.filter(**pro_query)
        if targets:
            targets = targets
        else:        
            targets = Targets.objects.filter(**query).values_list('from_date','to_date',_term).\
                        annotate(target=Sum('target_value'))
            targ_query = Targets.objects.filter(**query)
        raw_query = RawTable.objects.filter(**raw_data).values_list('date',_term).annotate(total=Sum('per_day'),count=Count('employee_id'))        
        E_data = RawTable.objects.filter(**raw_data).values(_term,'employee_id','date').annotate(count=Count('employee_id'))                                     
    else:
        targets, raw_query, _type = {}, {}, {}
    
    return targets, targ_query, raw_query, E_data, _type, _term



def productivity_day(date_list, prj_id, center_obj, level_structure_key, main_dates,request):

    packet_names = Headcount.objects.filter(project=prj_id, center=center_obj, date__range=[date_list[0],date_list[-1]]).values('sub_project', 'work_packet', 'sub_packet').distinct()
    count  = 0;

    for i in packet_names:
        if all(value == '' for value in i.values()):
            count = count + 1;
    filter_params, _term = getting_required_params(level_structure_key, prj_id, center_obj, date_list)
    data_dict = {};
    if _term and filter_params:
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





