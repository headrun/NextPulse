
import datetime
import redis
from api.models import *
from api.commons import data_dict
#from api.pareto import generate_pareto_calculations
from api.basics import *
from django.db.models import Max
from api.utils import worktrack_internal_external_workpackets_list
from api.query_generations import query_set_generation
from api.graph_settings import graph_data_alignment_color
from api.internal_external_common import *
from common.utils import getHttpResponse as json_HttpResponse


def error_charts(request, name, function_name, internal_name, external_name, term):

    final_dict = {}
    main_data_dict = data_dict(request.GET)
    work_packet = main_data_dict['work_packet']
    sub_project = main_data_dict['sub_project']
    sub_packet = main_data_dict['sub_packet']
    project_center = main_data_dict['pro_cen_mapping']
    project = main_data_dict['pro_cen_mapping'][0][0]
    center = main_data_dict['pro_cen_mapping'][1][0]
    date_list = main_data_dict['dates']

    level_structure_key = get_level_structure_key(work_packet, sub_project, sub_packet, project_center)

    _internal_data = function_name(date_list, project, center, level_structure_key, "Internal",term)
    _external_data = function_name(date_list, project, center, level_structure_key, "External",term)
    if name != 'pareto_charts':
        final_dict[internal_name] = graph_data_alignment_color(_internal_data,'y',level_structure_key,project,center,'')
        final_dict[external_name] = graph_data_alignment_color(_external_data,'y',level_structure_key,project,center,'')
    elif name == 'pareto_charts':
        final_dict[internal_name] = _internal_data
        final_dict[external_name] = _external_data

    final_dict['is_annotation'] = annotation_check(request)
    return final_dict

        
def error_bar_graph(request):

    internal_name = 'internal_accuracy_graph'
    external_name = 'external_accuracy_graph'
    name = 'bar'
    term = ''
    function_name = accuracy_bar_graphs
    
    result = error_charts(request, name, function_name, internal_name, external_name, term)
    return json_HttpResponse(result)


def cate_error(request):
    
    internal_name = 'internal_errors_types'
    external_name = 'external_errors_types'
    name = 'pie_charts'
    term = ''
    function_name = internal_extrnal_error_types
    
    result = error_charts(request, name, function_name, internal_name, external_name, term)
    return json_HttpResponse(result)


def pareto_cate_error(request):

    internal_name = 'internal_error_category'
    external_name = 'external_error_category'
    name = 'pareto_charts'
    term = ''
    function_name = field_pareto_analysis

    result = error_charts(request, name, function_name, internal_name, external_name, term)
    return json_HttpResponse(result)


def agent_cate_error(request):
    
    internal_name = 'pareto_data'
    external_name = 'external_pareto_data'
    name = 'pareto_charts'
    term = 'agent'
    function_name = agent_pareto_analysis
    #import pdb;pdb.set_trace()
    result = error_charts(request, name, function_name, internal_name, external_name, term)
    return json_HttpResponse(result)


def field_pareto_analysis(date_list,project,center,level_structure_key,error_type,_term):

    data = internal_extrnal_error_types(date_list,project,center,level_structure_key,error_type,_term)
    result = generate_pareto_calculations(data)

    return result


def agent_pareto_analysis(date_list,project,center,level_structure_key,error_type,_term):

    data = internal_extrnal_error_types(date_list,project,center,level_structure_key,error_type,_term)
    result = generate_pareto_calculations(data)

    return result


def generate_pareto_calculations(data):

    "common function for calculating agent and field pareto data"
    
    accuracy_dict, final_pareto_data = {}, {}
    accuracy_list, error_list, data_values = [], [], []
    final_pareto_data['Error Count'] = {}
    final_pareto_data['Error Count']['Error Count'] = []
    final_pareto_data['Cumulative %'] = {}
    final_pareto_data['Cumulative %']['Cumulative %'] = []
    error_sum = sum(data.values())
    count = 0
    new_dict, result = {}, {}
    for key, value in sorted(data.iteritems(), key=lambda (k, v): (-v, k)):
        err_list = []
        count = count + value
        err_list.append(key)
        err_list.append(count)
        data_values.append(value)
        error_list.append(err_list)
    new_dict.update(error_list)
    final_pareto_data['Error Count']['Error Count'] = data_values[:10]

    accuracy_dict = {}
    for key, value in new_dict.iteritems():
        if error_sum > 0:
            accuracy = (float(float(value) / float(error_sum))) * 100
            accuracy_perc = float('%.2f' % round(accuracy, 2))
            accuracy_dict[key] = accuracy_perc
        else:
            accuracy_dict[key] = 100

    error_accuracy, final_list, type_accuracy = [], [], []
    for key, value in sorted(accuracy_dict.iteritems(), key=lambda (k, v): (v, k)):
        final_list.append(key)
        type_accuracy.append(value)
    final_pareto_data['Cumulative %']['Cumulative %'] = type_accuracy[:10]
    final_data = pareto_graph_data(final_pareto_data)

    result['category_name'] = final_list[:10]
    result['category_pareto'] = final_data
    return result


def pareto_graph_data(pareto_dict):
    final_list = []
    for key,value in pareto_dict.iteritems():
        alignment_data = graph_data_alignment(value, 'data')
        for single_dict in alignment_data:
            if key == 'Error Count':
                single_dict['type'] = 'column'
            if key == 'Cumulative %':
                single_dict['type']='spline'
                single_dict['yAxis'] = 1
            final_list.append(single_dict)
    return final_list


def err_field_graph(request):
    final_dict = {}
    data_date = []
    main_data_dict = data_dict(request.GET)
    if main_data_dict['dwm_dict'].has_key('day'):
        main_dates_list = [ main_data_dict['dwm_dict']['day']]
    elif main_data_dict['dwm_dict'].has_key('week'):
        main_dates_list = main_data_dict['dwm_dict']['week']
    elif main_data_dict['dwm_dict'].has_key('month'):
        main_dates_list = main_data_dict['dwm_dict']['month']['month_dates']
    date_value = []
    prj_id = main_data_dict['pro_cen_mapping'][0][0]
    center = main_data_dict['pro_cen_mapping'][1][0]
    if ((main_data_dict['dwm_dict'].has_key('day')) or (main_data_dict['dwm_dict'].has_key('week')) or (main_data_dict['dwm_dict'].has_key('month'))):
        for sing_list in main_dates_list:
            date_value = date_value + sing_list
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            if main_data_dict['dwm_dict'].has_key('day'):
                field_internal_error_graph_data = internal_external_graphs_common(request, sing_list,prj_id,center,level_structure_key,'Internal')
                field_external_error_graph_data = internal_external_graphs_common(request, sing_list,prj_id,center,level_structure_key,'External')
            else:
                field_internal_error_graph_data = internal_external_graphs_common(request, date_value,prj_id,center,level_structure_key,'Internal')
                field_external_error_graph_data = internal_external_graphs_common(request, date_value,prj_id,center,level_structure_key,'External')
            if field_internal_error_graph_data.has_key('internal_field_accuracy_graph'):
                final_dict['internal_field_accuracy_graph'] = graph_data_alignment_color(field_internal_error_graph_data['internal_field_accuracy_graph'], 'y', level_structure_key, prj_id, center,'internal_field_accuracy_graph')

            if field_external_error_graph_data.has_key('external_field_accuracy_graph'):
                final_dict['external_field_accuracy_graph'] = graph_data_alignment_color(field_external_error_graph_data['external_field_accuracy_graph'], 'y', level_structure_key, prj_id, center,'external_field_accuracy_graph')

            if field_external_error_graph_data.has_key('extr_err_accuracy'):
                final_field_extrn_accuracy = {}
                for perc_key,perc_value in field_external_error_graph_data['extr_err_accuracy']['packets_percntage'].iteritems():
                    final_field_extrn_accuracy[perc_key] = perc_value[0]
                final_dict['external_field_accuracy_graph'] = graph_data_alignment_color(final_field_extrn_accuracy, 'y', level_structure_key, prj_id, center,'')
            if field_internal_error_graph_data.has_key('intr_err_accuracy'):
                final_field_intrn_accuracy = {}
                for perc_key,perc_value in field_internal_error_graph_data['intr_err_accuracy']['packets_percntage'].iteritems():
                    final_field_intrn_accuracy[perc_key] = perc_value[0]
                final_dict['internal_field_accuracy_graph'] = graph_data_alignment_color(final_field_intrn_accuracy, 'y', level_structure_key, prj_id, center,'')
                int_value_range = field_internal_error_graph_data['internal_field_accuracy_graph']
                int_min_max = min_max_value_data(int_value_range)
                final_dict['inter_min_value'] = int_min_max['min_value']
                final_dict['inter_max_value'] = int_min_max['max_value']
                int_value_range = field_external_error_graph_data['external_field_accuracy_graph']
                int_min_max = min_max_value_data(int_value_range)
                final_dict['exter_min_value'] = int_min_max['min_value']
                final_dict['exter_max_value'] = int_min_max['max_value']
    final_dict['is_annotation'] = annotation_check(request)
    return json_HttpResponse(final_dict)


def internal_extrnal_sub_error_types(request,date_list,prj_id,center_obj,level_structure_key,err_type):
    project = Project.objects.filter(id=prj_id)
    prj_name = project[0].name
    center_name = project[0].center.name
    query_set = query_set_generation(prj_id, center_obj, level_structure_key,date_list)
    if err_type =='Internal' :
        extr_volumes_list = worktrack_internal_external_workpackets_list(level_structure_key, 'Internalerrors',query_set)
        err_key_type = 'error'
    if err_type == 'External':
        extr_volumes_list = worktrack_internal_external_workpackets_list(level_structure_key, 'Externalerrors',query_set)
        err_key_type = 'externalerror'
    conn = redis.Redis(host="localhost", port=6379, db=0)
    result = {}
    vol_error_values = {}
    vol_audit_data = {}
    extrnl_error_values = {}
    extrnl_err_type = {}
    extr_volumes_list_new=[]
    all_error_types = []
    sub_error_types = []
    total_done_value = RawTable.objects.filter(project=prj_id, center=center_obj, date__range=[date_list[0], date_list[-1]]).values('date').annotate(total=Sum('per_day'))
    values = OrderedDict(zip(map(lambda p: str(p['date']), total_done_value), map(lambda p: str(p['total']), total_done_value)))
    for date_key, total_val in values.iteritems():
        count =0
        if total_val > 0:
            for vol_type in extr_volumes_list:
                final_work_packet = level_hierarchy_key(level_structure_key, vol_type)
                if not final_work_packet:
                    final_work_packet = level_hierarchy_key(extr_volumes_list[count],vol_type)
                count = count+1
                extr_volumes_list_new.append(final_work_packet)
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
                            if key == 'error_values':
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
    sub_error_category_calculations = error_types_sum(sub_error_types)
    return sub_error_category_calculations


def internal_extrnal_error_types(date_list,prj_id,center_obj,level_structure_key,error_type,term): 

    final_dict = {}

    param1 = 'employee_id'
    param2 = 'total_errors'

    if error_type == 'Internal':
        table_name = Internalerrors
    if error_type == 'External':
        table_name = Externalerrors

    if term == '':
        param1 = 'error_types'
        param2 = 'error_values'
    params = get_query_parameters(level_structure_key, prj_id, center_obj, date_list)
    
    error_query = table_name.objects.filter(**params).values(param1, param2)
    if term == '':
        values = different_error_type(error_query)
    elif term == 'agent':
        values = agent_errors(error_query)
    for key, value in values.iteritems():
        if key != 'no_data':
            if final_dict.has_key(key):
                final_dict[key].append(value)
            else:
                final_dict[key] = value
    return final_dict


def agent_errors(total_error_types):
    all_errors = {}
    new_all_errors = {}
    if len(total_error_types) > 0:
        for error_dict in total_error_types:
            emp_names= error_dict['employee_id']
            error_values = error_dict['total_errors']
            for key,value in zip([emp_names],[error_values]):
                if all_errors.has_key(key):
                    all_errors[key].append(int(value))
                else:
                    if key != '': 
                        all_errors[key] = [int(value)]
        for error_type,error_value in all_errors.iteritems():
            try:
                new_all_errors[str(error_type)] = sum(error_value)
            except:
                error_type = smart_str(error_type)
                new_all_errors[error_type] = sum(error_value)
    return new_all_errors


