
import datetime
import redis
from api.models import *
from api.basics import *
from api.utils import *
from collections import OrderedDict
from api.query_generations import *
from django.db.models import Max
from common.utils import getHttpResponse as json_HttpResponse


def accuracy_field_bar_graphs(date_list,prj_id,center_obj,level_structure_key,error_type,term):
    import collections    

    final_dict, result = {}, {}

    if error_type == 'Internal':
        table_name = Internalerrors
        name = 'internal_field_accuracy_graph'
    if error_type == 'External':
        table_name = Externalerrors
        name = 'external_field_accuracy_graph'

    filter_params, _term = getting_required_params(level_structure_key, prj_id, center_obj, date_list)
    query_values = table_name.objects.filter(**filter_params)
    error_data = query_values.values_list(_term).annotate(total=Sum('total_errors'), audit=Sum('audited_errors'))
    rawtable = RawTable.objects.filter(**filter_params)
    raw_data = rawtable.values_list('date',_term).annotate(prod=Sum('per_day'))
    dates = rawtable.values_list('date', flat=True).distinct()
    dates = dates[::-1]
    if level_structure_key.has_key('sub_project'):
        if level_structure_key['sub_project'] == 'All' or level_structure_key['sub_project'] != 'All':
            result[name] = {}
            return result
    if _term == 'work_packet' and level_structure_key['work_packet'] == 'All':
        sub_term = 'sub_packet'
        targets = Targets.objects.filter(project=prj_id,center=center_obj,\
                  from_date__gte=date_list[0],to_date__lte=date_list[-1],target_type='Fields').\
                  values_list('from_date','to_date',_term,sub_term).annotate(total=Sum('target_value'))
        data_values = rawtable.values_list('date',_term,sub_term).annotate(prod=Sum('per_day'))
        packets = [data[1]+'_'+data[2] for data in data_values]
        packets = set(packets)
    elif level_structure_key['work_packet'] != 'All' and level_structure_key.has_key('sub_packet') == 'All':
        sub_term = 'sub_packet'
        targets = Targets.objects.filter(project=prj_id,center=center_obj,\
                  from_date__gte=date_list[0],to_date__lte=date_list[-1],target_type='Fields').\
                  values_list(str('from_date'),str('to_date'),_term,sub_term).annotate(total=Sum('target_value'))
        data_values = rawtable.values_list('date',_term,sub_term).annotate(prod=Sum('per_day'))
        packets = [data[2] for data in data_values]
        packets = set(packets)
    else:
        result[name] = {}
        return result
    targets_dict, result_dict, dct = {}, {}, {}
    for target in targets:
        for date in dates:
            if level_structure_key['work_packet'] == 'All':
                packet = target[2]+'_'+target[3]
            else:
                packet = target[3]
            if packet in packets and (target[0] >= date and target[1] <= date):
                if targets_dict.has_key(packet):
                    targets_dict[packet].append(target[4])
                else:
                    targets_dict[packet] = [target[4]]
  
    for key in packets:
        result_dict.update({key:[]})
    for i, val in enumerate(data_values):
       date,packet,sub_packet,done = val
       if level_structure_key['work_packet'] == 'All': 
           packet = val[1]+'_'+val[2]
       else:
           packet = val[2]  
       if i < len(data_values)-1:
           nxt_date, nxt_packet, sub_packet, nxt_done = data_values[i+1]
           dct.update({packet:done})
           if nxt_date != date:
               for packet in packets:
                   dict_val = result_dict[packet]
                   dict_val.append(dct.setdefault(packet,0))
                   result_dict.update({packet:dict_val})
               dct = {}
       else: 
           p_date, p_packet, p_sub_packet, p_done = data_values[i-1]
           if p_date != date:
               dct = {}
           dct.update({packet:done})
           for packet in packets:
               dict_val = result_dict[packet]
               dict_val.append(dct.setdefault(packet,0))
               result_dict.update({packet:dict_val})  
    target_data = collections.OrderedDict(sorted(targets_dict.items()))
    prod_data = collections.OrderedDict(sorted(result_dict.items()))
    _dict = {}
    for key, value in target_data.iteritems():
        value = zip(target_data[key], prod_data[key])
        _dict[key] = sum([tar*val for tar, val in value])
    data_dict = {}
    for key, value in _dict.iteritems():
        if level_structure_key['work_packet'] == 'All':
            packet = key.split('_')[0]
        else:
            packet = key
        if data_dict.has_key(packet):
            data_dict[packet].append(value)
        else:
            data_dict[packet] = [value]
    for value in error_data:
        if value[1] == 0 and value[0] in data_dict.keys():
            accuracy = (float(value[2])/float(sum(data_dict[value[0]])))*100
            final_value = 100 - float('%.2f' % round(accuracy, 2))
        elif value[1] > 0:
            accuracy = (float(value[2])/float(value[1]))*100
            final_value = 100 - float('%.2f' % round(accuracy, 2))
        else:
            final_value = 100
        final_dict.update({value[0]:final_value})
    result[name] = final_dict
    return result

def accuracy_bar_graphs(date_list,prj_id,center_obj,level_structure_key,error_type,_term):

    _dict = {}

    if error_type == 'Internal':
        table_name = Internalerrors
    if error_type == 'External':
        table_name = Externalerrors

    filter_params, _term = getting_required_params(level_structure_key, prj_id, center_obj, date_list)
    query_values = table_name.objects.filter(**filter_params)
    error_data = query_values.values_list(_term).annotate(total=Sum('total_errors'), audit=Sum('audited_errors'))
    rawtable = RawTable.objects.filter(**filter_params) 
    raw_packets = rawtable.values_list(_term).annotate(prod=Sum('per_day'))
    packets = [data[0] for data in raw_packets]
    packets = set(packets)
    for data in error_data:
        if data[1] > 0:
            value = (float(data[2])/float(data[1])) * 100
            accuracy = 100-float('%.2f' % round(value, 2))
        elif data[1] == 0 and data[0] in packets:
            for prod_val in raw_packets:
                if data[0] == prod_val[0]:
                    value = (float(data[2])/float(prod_val[1])) * 100
                    accuracy = 100-float('%.2f' % round(value, 2))
        else:
            accuracy = 100
        _dict[data[0]] = accuracy
    return _dict



