
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


"""def internal_external_graphs_common(request,date_list,prj_id,center_obj,level_structure_key,err_type):
    #prj_name = Project.objects.filter(id=prj_id).values_list('name', flat=True)
    #center_name = Center.objects.filter(id=center_obj).values_list('name', flat=True)
    project = Project.objects.filter(id=prj_id)
    prj_name = project[0].name
    center_name = project[0].center.name
    query_set = query_set_generation(prj_id, center_obj, level_structure_key,date_list)
    if err_type =='Internal' :
        extr_volumes_list = worktrack_internal_external_workpackets_list(level_structure_key, 'Internalerrors', query_set)
        err_key_type = 'error'
    if err_type == 'External':
        extr_volumes_list = worktrack_internal_external_workpackets_list(level_structure_key, 'Externalerrors',query_set)
        err_key_type = 'externalerror'
    conn = redis.Redis(host="localhost", port=6379, db=0)
    # below variable for error graphs.
    result, vol_error_values, vol_audit_data = {}, {}, {}
    # below variable for external errors
    extrnl_error_values, extrnl_err_type = {}, {}
    extr_volumes_list_new, all_error_types, sub_error_types = [], [], []
    total_done_value = RawTable.objects.filter(project=prj_id, center=center_obj, date__range=[date_list[0], date_list[-1]]).values('date').annotate(total=Sum('per_day'))
    values = OrderedDict(zip(map(lambda p: str(p['date']), total_done_value), map(lambda p: str(p['total']), total_done_value)))
    #for date_va in date_list:
    for date_key, total_val in values.iteritems():
        count =0
        #total_done_value = RawTable.objects.filter(project=prj_id, center=center_obj, date=date_va).aggregate(Max('per_day'))
        #if total_done_value['per_day__max'] > 0:
        if total_val > 0:
            for vol_type in extr_volumes_list:
                final_work_packet = level_hierarchy_key(level_structure_key, vol_type)
                if not final_work_packet:
                    final_work_packet = level_hierarchy_key(extr_volumes_list[count],vol_type)
                count = count+1
                extr_volumes_list_new.append(final_work_packet)
                if level_structure_key.get('work_packet','') == 'All':
                    #packets_list = RawTable.objects.filter(project=prj_id, center=center_obj, date=date_va,work_packet=final_work_packet).values_list('sub_packet',flat=True).distinct()
                    packets_list = RawTable.objects.filter(project=prj_id, center=center_obj, date=date_key,work_packet=final_work_packet).values_list('sub_packet',flat=True).distinct()
                    for packet in packets_list:
                        if '_' in final_work_packet:
                            packets_values = final_work_packet.split('_')
                            final_work_packet = packets_values[0]
                        else:
                            final_work_packet = final_work_packet
                        if packet:
                            final_work_packet = final_work_packet+'_'+packet
                            #key_pattern = '{0}_{1}_{2}_{3}_{4}'.format(prj_name[0], str(center_name[0]), final_work_packet, date_va,err_key_type)
                            key_pattern = '{0}_{1}_{2}_{3}_{4}'.format(prj_name, center_name, final_work_packet, date_key, err_key_type)
                            audit_key_list = conn.keys(pattern=key_pattern)
                            if not audit_key_list:
                                if vol_error_values.has_key(final_work_packet):
                                    vol_error_values[final_work_packet].append("NA")
                                    vol_audit_data[final_work_packet].append("NA")
                                else:
                                    vol_error_values[final_work_packet] = ["NA"]
                                    vol_audit_data[final_work_packet] = ["NA"]
                            for cur_key in audit_key_list:
                                var = conn.hgetall(cur_key)
                                for key, value in var.iteritems():
                                    if key == 'types_of_errors':
                                        all_error_types.append(value)
                                    elif key == 'sub_error_types':
                                        sub_error_types.append(value)
                                    else:
                                        if value == 'None':
                                            value = "NA"
                                        error_vol_type = final_work_packet
                                        if key == 'total_errors':
                                            if vol_error_values.has_key(error_vol_type):
                                                if value =="NA":
                                                    vol_error_values[error_vol_type].append(value)
                                                else:
                                                    vol_error_values[error_vol_type].append(int(value))
                                            else:
                                                if value =="NA":
                                                    vol_error_values[error_vol_type] = [value]
                                                else:
                                                    vol_error_values[error_vol_type] = [int(value)]
                                        else:
                                            if vol_audit_data.has_key(error_vol_type):
                                                if value=="NA":
                                                    vol_audit_data[error_vol_type].append(value)
                                                else:
                                                    vol_audit_data[error_vol_type].append(int(value))
                                            else:
                                                if value=="NA":
                                                    vol_audit_data[error_vol_type] = [value]
                                                else:
                                                    vol_audit_data[error_vol_type] = [int(value)]
                else:
                    final_work_packet = final_work_packet
                    #key_pattern = '{0}_{1}_{2}_{3}_{4}'.format(prj_name[0], str(center_name[0]), final_work_packet, date_va,err_key_type)
                    key_pattern = '{0}_{1}_{2}_{3}_{4}'.format(prj_name, center_name, final_work_packet, date_key,err_key_type)
                    audit_key_list = conn.keys(pattern=key_pattern)
                    if not audit_key_list:
                        if vol_error_values.has_key(final_work_packet):
                            vol_error_values[final_work_packet].append("NA")
                            vol_audit_data[final_work_packet].append("NA")
                        else:
                            vol_error_values[final_work_packet] = ["NA"]
                            vol_audit_data[final_work_packet] = ["NA"]
                    for cur_key in audit_key_list:
                        var = conn.hgetall(cur_key)
                        for key, value in var.iteritems():
                            if key == 'types_of_errors':
                                all_error_types.append(value)
                            elif key == 'sub_error_types':
                                sub_error_types.append(value)
                            else:
                                if value == 'None':
                                    value = "NA"
                                error_vol_type = final_work_packet
                                if key == 'total_errors':
                                    if vol_error_values.has_key(error_vol_type):
                                        if value =="NA":
                                            vol_error_values[error_vol_type].append(value)
                                        else:
                                            vol_error_values[error_vol_type].append(int(value))
                                    else:
                                        if value =="NA":
                                            vol_error_values[error_vol_type] = [value]
                                        else:
                                            vol_error_values[error_vol_type] = [int(value)]
                                else:
                                    if vol_audit_data.has_key(error_vol_type):
                                        if value=="NA":
                                            vol_audit_data[error_vol_type].append(value)
                                        else:
                                            vol_audit_data[error_vol_type].append(int(value))
                                    else:
                                        if value=="NA":
                                            vol_audit_data[error_vol_type] = [value]
                                        else:
                                            vol_audit_data[error_vol_type] = [int(value)]

    date_values = {}
    #for date_va in date_list:
    for date_key, total_val in values.iteritems():
        #total_done_value = RawTable.objects.filter(project=prj_id, center=center_obj, date=date_va).aggregate(Max('per_day'))
        #if total_done_value['per_day__max'] > 0:
        if total_val > 0:
            volume_list = worktrack_internal_external_workpackets_list(level_structure_key, 'RawTable', query_set)
            count =0
            for vol_type in volume_list:
                final_work_packet = level_hierarchy_key(level_structure_key,vol_type)
                if not final_work_packet:
                    final_work_packet = level_hierarchy_key(volume_list[count],vol_type)
                count = count+1
                extr_volumes_list_new.append(final_work_packet)
                if level_structure_key.get('work_packet','') == 'All':
                    #packets_list = RawTable.objects.filter(project=prj_id, center=center_obj, date=date_va,work_packet=final_work_packet).values_list('sub_packet',flat=True).distinct()
                    packets_list = RawTable.objects.filter(project=prj_id, center=center_obj, date=date_key,work_packet=final_work_packet).values_list('sub_packet',flat=True).distinct()
                    for packet in packets_list:
                        if '_' in final_work_packet:
                            packets_values = final_work_packet.split('_')
                            final_work_packet = packets_values[0]
                        else:
                            final_work_packet = final_work_packet
                        if packet:
                            final_work_packet = final_work_packet+'_'+packet
                            #target_query_set = target_query_generations(prj_id, center_obj, date_va, final_work_packet,level_structure_key)
                            target_query_set = target_query_generations(prj_id, center_obj, date_key, final_work_packet,level_structure_key)
                            target_types = Targets.objects.filter(**target_query_set).values('target_type').distinct()
                            target_consideration = target_types.filter(target_type = 'Fields').aggregate(Sum('target_value'))
                            final_target = target_consideration['target_value__sum']
                            #date_pattern = '{0}_{1}_{2}_{3}'.format(prj_name[0], str(center_name[0]), str(final_work_packet), date_va)
                            date_pattern = '{0}_{1}_{2}_{3}'.format(prj_name, center_name, str(final_work_packet), date_key)
                            key_list = conn.keys(pattern=date_pattern)
                            if not key_list:
                                if date_values.has_key(final_work_packet):
                                    date_values[final_work_packet].append(0)
                                else:
                                    date_values[final_work_packet] = [0]
                            for cur_key in key_list:
                                var = conn.hgetall(cur_key)
                                for key,value in var.iteritems():
                                    if value == 'None':
                                        value = 0
                                    if date_values.has_key(key):
                                        if final_target:
                                            date_values[key].append(int(value)*final_target)
                                        else:
                                            date_values[key].append(int(value))
                                    else:
                                        if final_target:
                                            date_values[key]=[int(value)*final_target]
                                        else:
                                            date_values[key]=[int(value)]

                else:
                    final_work_packet = final_work_packet
                    #target_query_set = target_query_generations(prj_id, center_obj, date_va, final_work_packet,level_structure_key)
                    target_query_set = target_query_generations(prj_id, center_obj, date_key, final_work_packet,level_structure_key)
                    target_types = Targets.objects.filter(**target_query_set).values('target_type').distinct()
                    target_consideration = target_types.filter(target_type = 'Fields').aggregate(Sum('target_value'))
                    final_target = target_consideration['target_value__sum']
                    #date_pattern = '{0}_{1}_{2}_{3}'.format(prj_name[0], str(center_name[0]), str(final_work_packet), date_va)
                    date_pattern = '{0}_{1}_{2}_{3}'.format(prj_name, center_name, str(final_work_packet), date_key)
                    key_list = conn.keys(pattern=date_pattern)
                    if not key_list:
                        if date_values.has_key(final_work_packet):
                            date_values[final_work_packet].append(0)
                        else:
                            date_values[final_work_packet] = [0]
                    for cur_key in key_list:
                        var = conn.hgetall(cur_key)
                        for key,value in var.iteritems():
                            if value == 'None':
                                value = 0
                            if date_values.has_key(key):
                                if final_target:
                                    date_values[key].append(int(value)*final_target)
                                else:
                                    date_values[key].append(int(value))
                            else:
                                if final_target:
                                    date_values[key]=[int(value)*final_target]
                                else:
                                    date_values[key]=[int(value)]
    if level_structure_key.get('work_packet','') == 'All':
        main_dict = {}
        for key, value in date_values.iteritems():
            pa_key = key.split('_')[0]
            if main_dict.has_key(pa_key):
                main_dict[pa_key].append(value)
            else:
                main_dict[pa_key] = [value]
        date_values_sum = {}
        for key, value in main_dict.iteritems():
            production_data = [sum(i) for i in value if i!='NA']
            date_values_sum[key] = sum(production_data)
        #indicidual_error_calc = error_types_sum(all_error_types)
        volume_dict, error_data, vol_err_dict = {}, {}, {}
        error_graph_data = []
        for key, value in vol_error_values.iteritems():
            pa_key = key.split('_')[0]
            if vol_err_dict.has_key(pa_key):
                vol_err_dict[pa_key].append(value)
            else:
                vol_err_dict[pa_key] = [value]
        vol_err_dict_sum = {}
        for key, value in vol_err_dict.iteritems():
            error_filter = [i for i in value if i !='NA']
            packet_dict = []
            for i in error_filter:
                for number in i:
                    if number == 'NA':
                        packet_dict.append(0)
                    else:
                        packet_dict.append(number)
            error_graph = []
            error_data[key] = sum(packet_dict)
            #error_graph.append(key)
            #error_graph.append(sum(packet_dict))
            #error_graph_data.append(error_graph)
        vol_audit_dict = {}
        for key,value in vol_audit_data.iteritems():
            pa_key = key.split('_')[0]
            if vol_audit_dict.has_key(pa_key):
                vol_audit_dict[pa_key].append(value)
            else:
                vol_audit_dict[pa_key] = [value]

        audit_data = {}
        for key, value in vol_audit_dict.iteritems():
            error_filter = [i for i in value if i!='NA']
            packet_dict = []
            for i in error_filter:
                for number in i:
                    if number == 'NA':
                        packet_dict.append(0)
                    else:
                        packet_dict.append(number)
            audit_data[key] = sum(packet_dict)
        error_accuracy = {}
        for key,value in error_data.iteritems():
            if audit_data[key]:
                 percentage = ((float(value)/float(audit_data[key])))*100
                 percentage = 100 - float('%.2f' % round(percentage, 2))
                 error_accuracy[key] = [percentage]
            else:
                if audit_data[key] == 0 and date_values_sum.has_key(key):
                    try:
                        percentage = (float(value) / date_values_sum[key]) * 100
                        percentage = 100 - float('%.2f' % round(percentage, 2))
                        error_accuracy[key] = [percentage]
                    except:
                        error_accuracy[key] = [0]
                else:
                    percentage = 0
                    error_accuracy[key] = [percentage]
        err_acc_name, err_acc_perc = [], []
        for key, value in error_accuracy.iteritems():
            err_acc_name.append(key)
            err_acc_perc.append(value[0])
    else:
        date_values_sum = {}
        for key, value in date_values.iteritems():
            production_data = [i for i in value if i!='NA']
            date_values_sum[key] = sum(production_data)
        #indicidual_error_calc = error_types_sum(all_error_types)
        volume_dict, error_data = {}, {}
        error_graph_data = []
        for key, value in vol_error_values.iteritems():
            error_filter = [i for i in value if i!='NA']
            error_graph = []
            error_data[key] = sum(error_filter)
            #error_graph.append(key)
            #error_graph.append(sum(error_filter))
            #error_graph_data.append(error_graph)
        audit_data, error_accuracy = {}, {}
        for key, value in vol_audit_data.iteritems():
            error_filter = [i for i in value if i!='NA']
            audit_data[key] = sum(error_filter)

        for key,value in error_data.iteritems():
            if audit_data[key]:
                 percentage = ((float(value)/float(audit_data[key])))*100
                 percentage = 100 - float('%.2f' % round(percentage, 2))
                 error_accuracy[key] = [percentage]
            else:
                if audit_data[key] == 0 and date_values_sum.has_key(key):
                    try:
                        percentage = (float(value) / date_values_sum[key]) * 100
                        percentage = 100 - float('%.2f' % round(percentage, 2))
                        error_accuracy[key] = [percentage]
                    except:
                        error_accuracy[key] = [0]
                else:
                    percentage = 0
                    error_accuracy[key] = [percentage]

        err_acc_name, err_acc_perc = [], []
        for key, value in error_accuracy.iteritems():
            err_acc_name.append(key)
            err_acc_perc.append(value[0])
    if err_type == 'Internal':
        result['intr_err_accuracy'] = {}
        result['intr_err_accuracy']['packets_percntage'] = error_accuracy
        result['intr_err_accuracy']['extr_err_name'] = err_acc_name
        result['intr_err_accuracy']['extr_err_perc'] = err_acc_perc
        result['internal_field_accuracy_graph'] = error_accuracy
    if err_type == 'External':
        result['extr_err_accuracy'] = {}
        result['extr_err_accuracy']['packets_percntage'] = error_accuracy
        result['extr_err_accuracy']['extr_err_name'] = err_acc_name
        result['extr_err_accuracy']['extr_err_perc'] = err_acc_perc
        result['external_field_accuracy_graph'] = error_accuracy
    return result"""


def internal_extrnal_graphs_same_formula(date_list,prj_id,center_obj,level_structure_key,err_type):
    #from api.graphs_mod import worktrack_internal_external_workpackets_list
    #prj_name = Project.objects.filter(id=prj_id).values_list('name', flat=True)
    project = Project.objects.filter(id=prj_id)
    prj_name = project[0].name
    center_name = project[0].center.name
    #center_name = Center.objects.filter(id=center_obj).values_list('name', flat=True)
    query_set = query_set_generation(prj_id, center_obj, level_structure_key,date_list)
    if err_type =='Internal' :
        extr_volumes_list = worktrack_internal_external_workpackets_list(level_structure_key, 'Internalerrors', query_set)
        err_key_type = 'error'
    if err_type == 'External':
        extr_volumes_list = worktrack_internal_external_workpackets_list(level_structure_key, 'Externalerrors',query_set)
        err_key_type = 'externalerror'
    conn = redis.Redis(host="localhost", port=6379, db=0)
    # below variable for error graphs.
    result, vol_error_values, vol_audit_data = {}, {}, {}
    # below variable for external errors
    extrnl_error_values, extrnl_err_type, date_values = {}, {}, {}
    extr_volumes_list_new, all_error_types, sub_error_types = [], [], []
    volume_list = worktrack_internal_external_workpackets_list(level_structure_key, 'RawTable', query_set)
    total_done_value = RawTable.objects.filter(project=prj_id, center=center_obj, date__range=[date_list[0], date_list[-1]]).values('date').annotate(total=Sum('per_day'))
    values = OrderedDict(zip(map(lambda p: str(p['date']), total_done_value), map(lambda p: str(p['total']), total_done_value)))
    #for date_va in date_list:
    for date_key, total_val in values.iteritems():
        count =0
        #total_done_value = RawTable.objects.filter(project=prj_id, center=center_obj, date=date_va).aggregate(Max('per_day'))
        #if total_done_value['per_day__max'] > 0:
        if total_val > 0:
            for vol_type in volume_list:
                final_work_packet = level_hierarchy_key(level_structure_key,vol_type)
                if not final_work_packet:
                    final_work_packet = level_hierarchy_key(volume_list[count],vol_type)
                count = count+1
                #date_pattern = '{0}_{1}_{2}_{3}'.format(prj_name[0], str(center_name[0]), str(final_work_packet), date_va)
                date_pattern = '{0}_{1}_{2}_{3}'.format(prj_name, center_name, str(final_work_packet), date_key)
                key_list = conn.keys(pattern=date_pattern)
                if not key_list:
                    if date_values.has_key(final_work_packet):
                        date_values[final_work_packet].append(0)
                    else:
                        date_values[final_work_packet] = [0]
                var = [conn.hgetall(cur_key) for cur_key in key_list]
                if var:
                    var = var[0]
                else:
                    var = {}
                for key,value in var.iteritems():
                    if value == 'None':
                        value = 0
                    if date_values.has_key(key):
                        date_values[key].append(int(value))
                    else:
                        date_values[key]=[int(value)]
            for vol_type in extr_volumes_list:
                final_work_packet = level_hierarchy_key(level_structure_key, vol_type)
                if not final_work_packet:
                    final_work_packet = level_hierarchy_key(extr_volumes_list[count],vol_type)
                count = count+1
                extr_volumes_list_new.append(final_work_packet)
                #key_pattern = '{0}_{1}_{2}_{3}_{4}'.format(prj_name[0], str(center_name[0]), final_work_packet, date_va,err_key_type)
                key_pattern = '{0}_{1}_{2}_{3}_{4}'.format(prj_name, center_name, final_work_packet, date_key,err_key_type)
                audit_key_list = conn.keys(pattern=key_pattern)
                if not audit_key_list:
                    if vol_error_values.has_key(final_work_packet):
                        vol_error_values[final_work_packet].append("NA")
                        vol_audit_data[final_work_packet].append("NA")
                    else:
                        vol_error_values[final_work_packet] = ["NA"]
                        vol_audit_data[final_work_packet] = ["NA"]
                var2 = [conn.hgetall(cur_key) for cur_key in audit_key_list]
                if var2:
                    var2 = var2[0]
                else:
                    var2 = {}
                for key, value in var2.iteritems():
                    if key == 'types_of_errors':
                        all_error_types.append(value)
                    elif key == 'sub_error_types':
                        sub_error_types.append(value)
                    else:
                        if value == 'None':
                            value = "NA"
                        error_vol_type = final_work_packet
                        if key == 'total_errors':
                            if vol_error_values.has_key(error_vol_type):
                                if value =="NA":
                                    vol_error_values[error_vol_type].append(value)
                                else:
                                    vol_error_values[error_vol_type].append(int(value))
                            else:
                                if value =="NA":
                                    vol_error_values[error_vol_type] = [value]
                                else:
                                    vol_error_values[error_vol_type] = [int(value)]
                        else:
                            if vol_audit_data.has_key(error_vol_type):
                                if value=="NA":
                                    vol_audit_data[error_vol_type].append(value)
                                else:
                                    vol_audit_data[error_vol_type].append(int(value))
                            else:
                                if value=="NA":
                                    vol_audit_data[error_vol_type] = [value]
                                else:
                                    vol_audit_data[error_vol_type] = [int(value)]

    date_values_sum, volume_dict, error_volume_data = {}, {}, {}
    for key, value in date_values.iteritems():
        production_data = [i for i in value if i!='NA']
        date_values_sum[key] = sum(production_data)
    #indicidual_error_calc = error_types_sum(all_error_types)

    error_graph_data = []
    for key, value in vol_error_values.iteritems():
        error_filter = [i for i in value if i!='NA']
        error_graph = []
        error_volume_data[key] = sum(error_filter)
        #error_graph.append(key)
        #error_graph.append(sum(error_filter))
        #error_graph_data.append(error_graph)
    error_audit_data, error_accuracy = {}, {}
    for key, value in vol_audit_data.iteritems():
        error_filter = [i for i in value if i!='NA']
        error_audit_data[key] = sum(error_filter)
    for key,value in error_volume_data.iteritems():
        if error_audit_data[key]:
             percentage = ((float(value)/float(error_audit_data[key])))*100
             percentage = 100 - float('%.2f' % round(percentage, 2))
             error_accuracy[key] = [percentage]
        else:
            if error_audit_data[key] == 0 and date_values_sum.has_key(key):
                try:
                    percentage = (float(value) / date_values_sum[key]) * 100
                    percentage = 100 - float('%.2f' % round(percentage, 2))
                    error_accuracy[key] = [percentage]
                except:
                    error_accuracy[key] = [0]
            else:
                percentage = 0
                error_accuracy[key] = [percentage]

    err_acc_name, err_acc_perc = [], []
    for key, value in error_accuracy.iteritems():
        err_acc_name.append(key)
        err_acc_perc.append(value[0])

    total_graph_data, internal_time_line = {}, {}
    for key,value in vol_audit_data.iteritems():
        count = 0
        for vol_error_value in value:
            if vol_error_value > 0 and vol_error_values[key][count] !="NA":
                if vol_error_value != "NA":
                    percentage = (float(vol_error_values[key][count]) / vol_error_value) * 100
                    percentage = 100-float('%.2f' % round(percentage, 2))
            else:
                if vol_error_value == 0 and date_values_sum.has_key(key):
                    try:
                        percentage = (float(vol_error_values[key][count]) / date_values_sum[key]) * 100
                        percentage = 100-float('%.2f' % round(percentage, 2))
                    except:
                        percentage = 0
                else:
                    percentage = 0
            if internal_time_line.has_key(key):
                internal_time_line[key].append(percentage)
            else:
                internal_time_line[key] = [percentage]
            count= count+1

    range_internal_time_line = {}
    if err_type == 'Internal':
        range_internal_time_line['internal_time_line'] = internal_time_line
        range_internal_time_line['date'] = date_list
        result['intr_err_accuracy'] = {}
        result['intr_err_accuracy']['packets_percntage'] = error_accuracy
        result['intr_err_accuracy']['extr_err_name'] = err_acc_name
        result['intr_err_accuracy']['extr_err_perc'] = err_acc_perc
        result['internal_error_count'] = error_volume_data
        result['internal_accuracy_graph'] = error_accuracy
        result['internal_time_line'] = range_internal_time_line
        result['internal_time_line_date'] = date_list
        #result['internal_pareto_data'] = pareto_data_generation(vol_error_values, internal_time_line)

    if err_type == 'External':
        range_internal_time_line['external_time_line'] = internal_time_line
        range_internal_time_line['date'] = date_list
        result['extr_err_accuracy'] = {}
        result['extr_err_accuracy']['packets_percntage'] = error_accuracy
        result['extr_err_accuracy']['extr_err_name'] = err_acc_name
        result['extr_err_accuracy']['extr_err_perc'] = err_acc_perc
        result['external_error_count'] = error_volume_data
        result['external_accuracy_graph'] = error_accuracy
        result['external_time_line'] = range_internal_time_line
        result['external_time_line_date'] = date_list
        #result['external_pareto_data'] = pareto_data_generation(vol_error_values, internal_time_line)
    return result


def internal_extrnal_graphs(date_list,prj_id,center_obj,level_structure_key):
    #prj_name = Project.objects.filter(id=prj_id).values_list('name', flat=True)
    #center_name = Center.objects.filter(id=center_obj).values_list('name', flat=True)
    final_internal_data = internal_extrnal_graphs_same_formula(date_list, prj_id, center_obj,level_structure_key,err_type='Internal')
    final_external_data = internal_extrnal_graphs_same_formula(date_list, prj_id, center_obj,level_structure_key,err_type='External')
    final_internal_data.update(final_external_data)
    return final_internal_data


def accuracy_bar_graphs(date_list,prj_id,center_obj,level_structure_key,error_type,_term):

    _dict = {}

    if error_type == 'Internal':
        table_name = Internalerrors
    if error_type == 'External':
        table_name = Externalerrors

    filter_params, _term = getting_required_params(level_structure_key, prj_id, center_obj, date_list)
    query_values = table_name.objects.filter(**filter_params)
    packets = query_values.values_list(_term, flat=True).distinct()
    error_data = query_values.values_list(_term).annotate(total=Sum('total_errors'), audit=Sum('audited_errors'))
    rawtable = RawTable.objects.filter(**filter_params) 
    raw_packets = rawtable.values_list(_term).annotate(prod=Sum('per_day'))

    for data in error_data:
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
        _dict[data[0]] = accuracy
    return _dict



