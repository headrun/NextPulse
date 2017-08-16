import redis
from api.commons import *
from api.pareto import *
from api.query_generations import *
from api.graphs_mod import *
from api.graph_settings import *
from api.graphs_mod import *

def cate_error(request):
    from api.graph_settings import graph_data_alignment_color
    from api.commons import data_dict
    final_dict = {}
    month_names = []
    main_data_dict = data_dict(request.GET)
    if main_data_dict['dwm_dict'].has_key('day'):
        main_dates_list = [ main_data_dict['dwm_dict']['day']]
    elif main_data_dict['dwm_dict'].has_key('week'):
        main_dates_list = main_data_dict['dwm_dict']['week']
    elif main_data_dict['dwm_dict'].has_key('month'):
        main_dates_list = main_data_dict['dwm_dict']['month']['month_dates']
    if main_data_dict['dwm_dict'].has_key('day'):
        for sing_list in main_dates_list:
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            internal_error_types = internal_extrnal_error_types(request, sing_list, main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0], level_structure_key,"Internal")
            external_error_types = internal_extrnal_error_types(request, sing_list, main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0],level_structure_key, "External")
            final_dict['internal_errors_types'] = graph_data_alignment_color(internal_error_types,'y',level_structure_key,main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0],'')
            final_dict['external_errors_types'] = graph_data_alignment_color(external_error_types,'y',level_structure_key,main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0],'')
    elif main_data_dict['dwm_dict'].has_key('week'):
        date_value = []
        for sing_list in main_dates_list:
            date_value = date_value + sing_list
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            internal_error_types = internal_extrnal_error_types(request, date_value, main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0], level_structure_key,"Internal")
            external_error_types = internal_extrnal_error_types(request, date_value, main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0],level_structure_key, "External")
            final_dict['internal_errors_types'] = graph_data_alignment_color(internal_error_types,'y',level_structure_key,main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0],'')
            final_dict['external_errors_types'] = graph_data_alignment_color(external_error_types,'y',level_structure_key,main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0],'')
    else:
        date_value = []
        for sing_list in main_dates_list:
            date_value = date_value + sing_list
        level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
        internal_error_types = internal_extrnal_error_types(request, date_value, main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0], level_structure_key,"Internal")
        external_error_types = internal_extrnal_error_types(request, date_value, main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0],level_structure_key, "External")
        final_dict['internal_errors_types'] = graph_data_alignment_color(internal_error_types,'y',level_structure_key,main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0],'')
        final_dict['external_errors_types'] = graph_data_alignment_color(external_error_types,'y',level_structure_key,main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0],'')
 
    return json_HttpResponse(final_dict)

def pareto_cate_error(request):
    from api.commons import data_dict
    final_dict = {} 
    main_data_dict = data_dict(request.GET)
    if main_data_dict['dwm_dict'].has_key('day'):
        main_dates_list = [ main_data_dict['dwm_dict']['day']]
    elif main_data_dict['dwm_dict'].has_key('week'):
        main_dates_list = main_data_dict['dwm_dict']['week']
    elif main_data_dict['dwm_dict'].has_key('month'):
        main_dates_list = main_data_dict['dwm_dict']['month']['month_dates']
    if main_data_dict['dwm_dict'].has_key('day'):
        for sing_list in main_dates_list:
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            category_error_count = sample_pareto_analysis(request,sing_list, main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0],level_structure_key,"Internal")
            extrnl_category_error_count = sample_pareto_analysis(request,sing_list, main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0], level_structure_key, "External")
            final_dict['Internal_Error_Category'] = category_error_count
            final_dict['External_Error_Category'] = extrnl_category_error_count
    elif main_data_dict['dwm_dict'].has_key('week'):
        date_value = []
        for sing_list in main_dates_list:
            date_value = date_value + sing_list
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            category_error_count = sample_pareto_analysis(request,date_value, main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0],level_structure_key,"Internal")
            extrnl_category_error_count = sample_pareto_analysis(request,date_value, main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0], level_structure_key, "External")
            final_dict['Internal_Error_Category'] = category_error_count
            final_dict['External_Error_Category'] = extrnl_category_error_count
    else:
        date_value = []
        for sing_list in main_dates_list:
            date_value = date_value + sing_list
        level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
        category_error_count = sample_pareto_analysis(request,date_value, main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0],level_structure_key,"Internal")
        extrnl_category_error_count = sample_pareto_analysis(request,date_value, main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0], level_structure_key, "External")
        final_dict['Internal_Error_Category'] = category_error_count
        final_dict['External_Error_Category'] = extrnl_category_error_count
    return json_HttpResponse(final_dict)

def agent_cate_error(request):
    from api.commons import data_dict
    final_dict = {}
    main_data_dict = data_dict(request.GET)
    if main_data_dict['dwm_dict'].has_key('day'):
        main_dates_list = [ main_data_dict['dwm_dict']['day']]
    elif main_data_dict['dwm_dict'].has_key('week'):
        main_dates_list = main_data_dict['dwm_dict']['week']
    elif main_data_dict['dwm_dict'].has_key('month'):
        main_dates_list = main_data_dict['dwm_dict']['month']['month_dates']
    if main_data_dict['dwm_dict'].has_key('day'):
        for sing_list in main_dates_list:
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            agent_internal_pareto_data = agent_pareto_data_generation(request,sing_list, main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0],level_structure_key)
            extrnl_agent_pareto_data = agent_external_pareto_data_generation(request,sing_list, main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0], level_structure_key)
            final_dict['External_Pareto_data'] = extrnl_agent_pareto_data
            final_dict['Pareto_data'] = agent_internal_pareto_data
    elif main_data_dict['dwm_dict'].has_key('week'):
        date_value = []
        for sing_list in main_dates_list:
            date_value = date_value + sing_list
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            agent_internal_pareto_data = agent_pareto_data_generation(request,date_value, main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0],level_structure_key)
            extrnl_agent_pareto_data = agent_external_pareto_data_generation(request,date_value, main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0], level_structure_key)
            final_dict['External_Pareto_data'] = extrnl_agent_pareto_data
            final_dict['Pareto_data'] = agent_internal_pareto_data
    else:
        date_value = []
        for sing_list in main_dates_list:
            date_value = date_value + sing_list
        level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
        agent_internal_pareto_data = agent_pareto_data_generation(request,date_value, main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0],level_structure_key)
        extrnl_agent_pareto_data = agent_external_pareto_data_generation(request,date_value, main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0], level_structure_key)
        final_dict['External_Pareto_data'] = extrnl_agent_pareto_data
        final_dict['Pareto_data'] = agent_internal_pareto_data
    return json_HttpResponse(final_dict)

def error_bar_graph(request):
    from api.commons import data_dict
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
    if main_data_dict['dwm_dict'].has_key('day'):
        for sing_list in main_dates_list:
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            error_graphs_data = internal_extrnal_graphs(sing_list, main_data_dict['pro_cen_mapping'][0][0],
                                                        main_data_dict['pro_cen_mapping'][1][0],level_structure_key)
            if error_graphs_data.has_key('internal_accuracy_graph'):
                final_dict['internal_accuracy_graph'] = graph_data_alignment_color(error_graphs_data['internal_accuracy_graph'], 'y',
               level_structure_key, main_data_dict['pro_cen_mapping'][0][0], main_data_dict['pro_cen_mapping'][1][0],'internal_error_accuracy')
            if error_graphs_data.has_key('intr_err_accuracy'):
                final_intrn_accuracy = {}
                for perc_key,perc_value in error_graphs_data['intr_err_accuracy']['packets_percntage'].iteritems():
                    final_intrn_accuracy[perc_key] = perc_value[0]
                final_dict['internal_accuracy_graph'] = graph_data_alignment_color(final_intrn_accuracy, 'y', level_structure_key,
                    main_data_dict['pro_cen_mapping'][0][0], main_data_dict['pro_cen_mapping'][1][0],'intenal_error_accuracy')
            if error_graphs_data.has_key('external_accuracy_graph'):
                final_dict['external_accuracy_graph'] = graph_data_alignment_color(error_graphs_data['external_accuracy_graph'], 'y',
               level_structure_key, main_data_dict['pro_cen_mapping'][0][0], main_data_dict['pro_cen_mapping'][1][0],'external_error_accuracy')
            if error_graphs_data.has_key('extr_err_accuracy'):
                final_extrn_accuracy = {}
                for perc_key,perc_value in error_graphs_data['extr_err_accuracy']['packets_percntage'].iteritems():
                    final_extrn_accuracy[perc_key] = perc_value[0]
                final_dict['external_accuracy_graph'] = graph_data_alignment_color(final_extrn_accuracy, 'y', level_structure_key,
                     main_data_dict['pro_cen_mapping'][0][0], main_data_dict['pro_cen_mapping'][1][0],'external_error_accuracy')

    elif main_data_dict['dwm_dict'].has_key('week'):
        for sing_list in main_dates_list:
            date_value = date_value + sing_list
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            error_graphs_data = internal_extrnal_graphs(date_value, main_data_dict['pro_cen_mapping'][0][0],
                                                        main_data_dict['pro_cen_mapping'][1][0],level_structure_key)
            if error_graphs_data.has_key('internal_accuracy_graph'):
                final_dict['internal_accuracy_graph'] = graph_data_alignment_color(error_graphs_data['internal_accuracy_graph'], 'y',
               level_structure_key, main_data_dict['pro_cen_mapping'][0][0], main_data_dict['pro_cen_mapping'][1][0],'internal_error_accuracy')
                for perc_key,perc_value in error_graphs_data['intr_err_accuracy']['packets_percntage'].iteritems():
                    final_intrn_accuracy[perc_key] = perc_value[0]
                final_dict['internal_accuracy_graph'] = graph_data_alignment_color(final_intrn_accuracy, 'y', level_structure_key,
                    main_data_dict['pro_cen_mapping'][0][0], main_data_dict['pro_cen_mapping'][1][0],'intenal_error_accuracy')
            if error_graphs_data.has_key('external_accuracy_graph'):
                final_dict['external_accuracy_graph'] = graph_data_alignment_color(error_graphs_data['external_accuracy_graph'], 'y',
               level_structure_key, main_data_dict['pro_cen_mapping'][0][0], main_data_dict['pro_cen_mapping'][1][0],'external_error_accuracy')
            if error_graphs_data.has_key('extr_err_accuracy'):
                final_extrn_accuracy = {}
                for perc_key,perc_value in error_graphs_data['extr_err_accuracy']['packets_percntage'].iteritems():
                    final_extrn_accuracy[perc_key] = perc_value[0]
                final_dict['external_accuracy_graph'] = graph_data_alignment_color(final_extrn_accuracy, 'y', level_structure_key,
                     main_data_dict['pro_cen_mapping'][0][0], main_data_dict['pro_cen_mapping'][1][0],'external_error_accuracy')

    else:
        for sing_list in main_dates_list:
            date_value = date_value + sing_list
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            error_graphs_data = internal_extrnal_graphs(date_value, main_data_dict['pro_cen_mapping'][0][0],
                                                        main_data_dict['pro_cen_mapping'][1][0],level_structure_key)
            if error_graphs_data.has_key('internal_accuracy_graph'):
                final_dict['internal_accuracy_graph'] = graph_data_alignment_color(error_graphs_data['internal_accuracy_graph'], 'y',
               level_structure_key, main_data_dict['pro_cen_mapping'][0][0], main_data_dict['pro_cen_mapping'][1][0],'internal_error_accuracy')
            if error_graphs_data.has_key('intr_err_accuracy'):
                final_intrn_accuracy = {}
                for perc_key,perc_value in error_graphs_data['intr_err_accuracy']['packets_percntage'].iteritems():
                    final_intrn_accuracy[perc_key] = perc_value[0]
                final_dict['internal_accuracy_graph'] = graph_data_alignment_color(final_intrn_accuracy, 'y', level_structure_key,
                    main_data_dict['pro_cen_mapping'][0][0], main_data_dict['pro_cen_mapping'][1][0],'intenal_error_accuracy')
            if error_graphs_data.has_key('external_accuracy_graph'):
                final_dict['external_accuracy_graph'] = graph_data_alignment_color(error_graphs_data['external_accuracy_graph'], 'y',
               level_structure_key, main_data_dict['pro_cen_mapping'][0][0], main_data_dict['pro_cen_mapping'][1][0],'external_error_accuracy')
            if error_graphs_data.has_key('extr_err_accuracy'):
                final_extrn_accuracy = {}
                for perc_key,perc_value in error_graphs_data['extr_err_accuracy']['packets_percntage'].iteritems():
                    final_extrn_accuracy[perc_key] = perc_value[0]
                final_dict['external_accuracy_graph'] = graph_data_alignment_color(final_extrn_accuracy, 'y', level_structure_key,
                     main_data_dict['pro_cen_mapping'][0][0], main_data_dict['pro_cen_mapping'][1][0],'external_error_accuracy')

    int_value_range = error_graphs_data['external_accuracy_graph']
    int_min_max = min_max_value_data(int_value_range)
    final_dict['ext_min_value'] = int_min_max['min_value']
    final_dict['ext_max_value'] = int_min_max['max_value']
    int_value_range = error_graphs_data['internal_accuracy_graph']
    int_min_max = min_max_value_data(int_value_range)
    final_dict['int_min_value'] = int_min_max['min_value']
    final_dict['int_max_value'] = int_min_max['max_value']
    return json_HttpResponse(final_dict)


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
    return json_HttpResponse(final_dict)


def different_sub_error_type(total_type_errors):
    all_errors = {}
    new_all_errors = {}
    if len(total_type_errors) > 0:
        for error_dict in total_type_errors:
            error_names= error_dict['type_error'].split('#<>#')
            error_values = error_dict['sub_error_count'].split('#<>#')
            for er_key,er_value in zip(error_names,error_values):
                if all_errors.has_key(er_key):
                    all_errors[er_key].append(int(er_value))
                else:
                    if er_key != '':
                        all_errors[er_key] = [int(er_value)]
        for type_error,sub_error_count in all_errors.iteritems():
            try:
                new_all_errors[str(type_error)] = sum(sub_error_count)
            except:
                type_error = smart_str(type_error)
                new_all_errors[type_error] = sum(sub_error_count)
    return new_all_errors

def different_error_type(total_error_types):
    all_errors = {}
    new_all_errors = {}
    if len(total_error_types) > 0:
        for error_dict in total_error_types:
            error_names= error_dict['error_types'].split('#<>#')
            error_values = error_dict['error_values'].split('#<>#')
            for er_key,er_value in zip(error_names,error_values):
                if all_errors.has_key(er_key):
                    all_errors[er_key].append(int(er_value))
                else:
                    if er_key != '':
                        all_errors[er_key] = [int(er_value)]
        for error_type,error_value in all_errors.iteritems():
            try:
                new_all_errors[str(error_type)] = sum(error_value)
            except:
                error_type = smart_str(error_type)
                new_all_errors[error_type] = sum(error_value)
    return new_all_errors


def error_types_sum(error_list):
    final_error_dict = {}
    new_final_dict = {}
    for error_dict in error_list:
        error_dict = json.loads(error_dict)
        for er_type,er_value in error_dict.iteritems():
            if final_error_dict.has_key(er_type):
                final_error_dict[er_type].append(er_value)
            else:
                final_error_dict[er_type] = [er_value]
    for error_type, error_value in final_error_dict.iteritems():
        final_error_dict[error_type] = sum(error_value)
    if final_error_dict.has_key('no_data'):
        del final_error_dict['no_data']
    for er_key in final_error_dict.keys():
        if final_error_dict[er_key] != 0:
            new_final_dict[er_key] = final_error_dict[er_key]

    return new_final_dict


def internal_extrnal_sub_error_types(request,date_list,prj_id,center_obj,level_structure_key,err_type):
    prj_name = Project.objects.filter(id=prj_id).values_list('name', flat=True)
    center_name = Center.objects.filter(id=center_obj).values_list('name', flat=True)
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
    for date_va in date_list:
        count =0
        total_done_value = RawTable.objects.filter(project=prj_id, center=center_obj, date=date_va).aggregate(Max('per_day'))
        if total_done_value['per_day__max'] > 0:
            for vol_type in extr_volumes_list:
                final_work_packet = level_hierarchy_key(level_structure_key, vol_type)
                if not final_work_packet:
                    final_work_packet = level_hierarchy_key(extr_volumes_list[count],vol_type)
                count = count+1
                extr_volumes_list_new.append(final_work_packet)
                key_pattern = '{0}_{1}_{2}_{3}_{4}'.format(prj_name[0], str(center_name[0]), final_work_packet, date_va,err_key_type)
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

def internal_extrnal_error_types(request,date_list,prj_id,center_obj,level_structure_key,err_type):
    from api.graphs_mod import worktrack_internal_external_workpackets_list
    prj_name = Project.objects.filter(id=prj_id).values_list('name', flat=True)
    center_name = Center.objects.filter(id=center_obj).values_list('name', flat=True)
    query_set = query_set_generation(prj_id, center_obj, level_structure_key,date_list)
    if err_type =='Internal' :
        extr_volumes_list = worktrack_internal_external_workpackets_list(level_structure_key, 'Internalerrors',query_set)
        err_key_type = 'error'
    if err_type == 'External':
        extr_volumes_list = worktrack_internal_external_workpackets_list(level_structure_key, 'Externalerrors',query_set)
        err_key_type = 'externalerror'
    conn = redis.Redis(host="localhost", port=6379, db=0)
    # below variable for error graphs.
    result = {}
    vol_error_values = {}
    vol_audit_data = {}
    # below variable for external errors
    extrnl_error_values = {}
    extrnl_err_type = {}
    extr_volumes_list_new=[]
    all_error_types = []
    sub_error_types = []
    for date_va in date_list:
        count =0
        total_done_value = RawTable.objects.filter(project=prj_id, center=center_obj, date=date_va).aggregate(Max('per_day'))
        if total_done_value['per_day__max'] > 0:
            for vol_type in extr_volumes_list:
                final_work_packet = level_hierarchy_key(level_structure_key, vol_type)
                if not final_work_packet:
                    final_work_packet = level_hierarchy_key(extr_volumes_list[count],vol_type)
                count = count+1
                extr_volumes_list_new.append(final_work_packet)
                key_pattern = '{0}_{1}_{2}_{3}_{4}'.format(prj_name[0], str(center_name[0]), final_work_packet, date_va,err_key_type)
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
    indicidual_error_calc = error_types_sum(all_error_types)
    return indicidual_error_calc

def Error_checking(employee_data,error_match=False):
    employee_data['status'] = 'mis_match'
    if employee_data.has_key('individual_errors') or employee_data.has_key('sub_errors'):
        if employee_data['individual_errors'].has_key('no_data'):
           employee_data['status'] = 'matched'
        try:
            total_errors = int(float(employee_data['total_errors']))
        except:
            total_errors = 0

        if employee_data['sub_errors'].has_key('no_data'):
            employee_data['status'] = 'matched'
        try:
            total_errors = int(float(employee_data['total_errors']))
        except:
            total_errors = 0

        all_error_values = []
        sub_error_values = []

        for er_value in employee_data['individual_errors'].values():
            try:
                er_value = int(float(er_value))
            except:
                er_value = 0
            all_error_values.append(er_value)

        for er_value in employee_data['sub_errors'].values():
            try:
                er_value = int(float(er_value))
            except:
                er_value = 0
            sub_error_values.append(er_value)
        if error_match == True:
            if total_errors == sum(sub_error_values):
                sub_error_values = [str(value) for value in sub_error_values]
                employee_data['status'] = 'matched'
                type_error = '#<>#'.join(employee_data['sub_errors'].keys())
                sub_error_count = '#<>#'.join(sub_error_values)
            else:
                employee_data['type_error'] = None
                employee_data['sub_error_count'] = 0

            if total_errors == sum(all_error_values):
                all_error_values = [str(value) for value in all_error_values ]
                employee_data['status'] = 'matched'
                error_types='#<>#'.join(employee_data['individual_errors'].keys())
                error_values = '#<>#'.join(all_error_values)
                employee_data['error_types'] = error_types
                employee_data['error_values'] = error_values
            else:
                employee_data['error_types'] = None
                employee_data['error_values'] = 0
        else:
            all_error_values = [str(value) for value in all_error_values]
            sub_error_values = [str(value) for value in sub_error_values]
            error_types = '#<>#'.join(employee_data['individual_errors'].keys())
            type_error = '#<>#'.join(employee_data['sub_errors'].keys())
            error_values = '#<>#'.join(all_error_values)
            sub_error_count = '#<>#'.join(sub_error_values)
            employee_data['error_types'] = error_types
            employee_data['type_error'] = type_error
            employee_data['sub_error_count'] = sub_error_count
            employee_data['error_values'] = error_values
    return employee_data

def error_timeline_min_max(min_max_dict):
    int_timeline_min_max = []
    for wp_key, wp_value in min_max_dict.iteritems():
        int_timeline_min_max = int_timeline_min_max + wp_value
    final_min_max={}
    if len(int_timeline_min_max)>0:
        min_value = int(round(min(int_timeline_min_max) - 2))
        max_value = int(round(max(int_timeline_min_max) + 2))
        final_min_max['min_value'] = 0
        if min_value > 0:
            final_min_max['min_value'] = min_value
        final_min_max['max_value'] = max_value
    else:
        final_min_max['min_value'] = 0
        final_min_max['max_value'] = 0
    return final_min_max

def errors_week_calcuations(week_names,internal_accuracy_timeline,final_internal_accuracy_timeline):
    for prodct_key, prodct_value in internal_accuracy_timeline.iteritems():
        for vol_key, vol_values in prodct_value.iteritems():
            error_pers = [i for i in vol_values if i != 'NA']
            if len(error_pers) > 0:
                int_errors = float(sum(error_pers)) / len(error_pers)
                int_errors = float('%.2f' % round(int_errors, 2))
            else:
                int_errors = 0
            internal_accuracy_timeline[prodct_key][vol_key] = int_errors

    for final_key, final_value in internal_accuracy_timeline.iteritems():
        for week_key, week_value in final_value.iteritems():
            if week_key not in final_internal_accuracy_timeline.keys():
                final_internal_accuracy_timeline[week_key] = []
    for prod_week_num in week_names:
        if internal_accuracy_timeline.has_key(prod_week_num):
            if len(internal_accuracy_timeline[prod_week_num]) > 0:
                for vol_key, vol_values in internal_accuracy_timeline[prod_week_num].iteritems():
                    if final_internal_accuracy_timeline.has_key(vol_key):
                        final_internal_accuracy_timeline[vol_key].append(vol_values)
                    else:
                        final_internal_accuracy_timeline[vol_key] = [vol_values]
                for prod_key, prod_values in final_internal_accuracy_timeline.iteritems():
                    if prod_key not in internal_accuracy_timeline[prod_week_num].keys():
                        final_internal_accuracy_timeline[prod_key].append(0)
            else:
                for vol_key, vol_values in final_internal_accuracy_timeline.iteritems():
                    final_internal_accuracy_timeline[vol_key].append(0)
    return final_internal_accuracy_timeline
