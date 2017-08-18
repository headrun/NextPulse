
import redis
from api.models import *
from api.commons import data_dict
from api.pareto import *
from api.basics import *
from django.db.models import Max
from api.utils import worktrack_internal_external_workpackets_list
from api.query_generations import query_set_generation
from api.internal_external_common import *
from common.utils import getHttpResponse as json_HttpResponse

def cate_error(request):
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




