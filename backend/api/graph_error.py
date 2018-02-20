
import datetime
import redis
from api.models import *
from api.commons import data_dict
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
    if name == 'field_bar':
        final_dict[internal_name] = graph_data_alignment_color(_internal_data[internal_name],'y',level_structure_key,project,center,internal_name)
        final_dict[external_name] = graph_data_alignment_color(_external_data[external_name],'y',level_structure_key,project,center,external_name)
    elif name != 'pareto_charts':
        final_dict[internal_name] = graph_data_alignment_color(_internal_data,'y',level_structure_key,project,center,'')
        final_dict[external_name] = graph_data_alignment_color(_external_data,'y',level_structure_key,project,center,'')        
    elif name == 'pareto_charts':
        final_dict[internal_name] = _internal_data
        final_dict[external_name] = _external_data

    final_dict['is_annotation'] = annotation_check(request)
    return final_dict


def err_field_graph(request):

    internal_name = 'internal_field_accuracy_graph'
    external_name = 'external_field_accuracy_graph'
    name = 'field_bar'
    term = ''
    function_name = accuracy_field_bar_graphs

    result = error_charts(request, name, function_name, internal_name, external_name, term)
    return json_HttpResponse(result)


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
    result = error_charts(request, name, function_name, internal_name, external_name, term)
    return json_HttpResponse(result)


def cate_error_sub(request):

    internal_name = 'internal_sub_errors_types'
    external_name = 'external_sub_errors_types'
    name = 'pie_charts'
    term = 'sub_error'
    function_name = internal_extrnal_error_types
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

    elif term == 'sub_error':
        param1 = 'type_error'
        param2 = 'sub_error_count'

    params = get_query_parameters(level_structure_key, prj_id, center_obj, date_list)
    
    error_query = table_name.objects.filter(**params).values(param1, param2)
    if term == '' or term == 'sub_error':
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


