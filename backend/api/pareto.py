import redis
from api.project import *
from api.query_generations import *
from api.graphs_mod import *
from api.graph_error import *
from api.graph_settings import *


def pareto_data_generation(vol_error_values,internal_time_line):
    result = {}
    volume_error_count = {}
    for key,values in vol_error_values.iteritems():
        new_values = [0 if value=='NA' else value for value in values ]
        volume_error_count[key] = new_values
    volume_error_accuracy = {}
    for key, values in internal_time_line.iteritems():
        error_values = [0 if value=='NA' else value for value in values ]
        volume_error_accuracy[key] = error_values

    result = {}
    result['error_count'] = volume_error_count
    result['error_accuracy'] = volume_error_accuracy
    return result

def agent_pareto_data_generation(request,date_list,prj_id,center_obj,level_structure_key):
    prj_name = Project.objects.filter(id=prj_id).values_list('name', flat=True)
    center_name = Center.objects.filter(id=center_obj).values_list('name', flat=True)
    query_set = query_set_generation(prj_id, center_obj, level_structure_key, date_list)
    extr_volumes_list = Internalerrors.objects.filter(**query_set).values_list('employee_id',flat=True).distinct()
    agent_count = []
    agent_name, error_count = {}, {}
    count = 0
    for agent in extr_volumes_list:
        if level_structure_key.get('work_packet','') == "All" and level_structure_key.get('sub_project','') == "All":
            total_errors = Internalerrors.objects.filter(project=prj_id, center=center_obj, employee_id=agent,
            date__range=[date_list[0], date_list[-1]]).aggregate(Sum('total_errors'))
        elif level_structure_key.get('sub_packet','') == "All" and level_structure_key.get('work_packet','') == "All" and level_structure_key.get('sub_project','') == "All":
            total_errors = Internalerrors.objects.filter(project=prj_id, center=center_obj, employee_id=agent,
            date__range=[date_list[0], date_list[-1]]).aggregate(Sum('total_errors'))
        elif level_structure_key.get('work_packet','') == "All" and len(level_structure_key) == 1:
            total_errors = Internalerrors.objects.filter(project=prj_id, center=center_obj, employee_id=agent,
            date__range=[date_list[0], date_list[-1]]).aggregate(Sum('total_errors'))
        elif level_structure_key.get('sub_project','') == "All":
            total_errors = Internalerrors.objects.filter(project=prj_id, center=center_obj, employee_id=agent,
            date__range=[date_list[0], date_list[-1]]).aggregate(Sum('total_errors'))
        else:
            if level_structure_key.get('sub_project','') != 'All' and level_structure_key.get('work_packet','') == 'All' and level_structure_key.get('sub_packet','') == 'All':
                sub_proj = level_structure_key['sub_project']
                total_errors = Internalerrors.objects.filter(project=prj_id, center=center_obj, employee_id=agent,
                date__range=[date_list[0], date_list[-1]],sub_project = sub_proj).aggregate(Sum('total_errors'))
            elif level_structure_key.get('sub_project','') != 'All' and level_structure_key.get('work_packet','') != 'All' and level_structure_key.get('sub_packet', '') == "All" and len(level_structure_key) == 3:
                sub_proj = level_structure_key['sub_project']
                wk_packet = level_structure_key['work_packet']
                total_errors = Internalerrors.objects.filter(project=prj_id, center=center_obj, employee_id=agent,
                date__range=[date_list[0], date_list[-1]],sub_project = sub_proj, work_packet = wk_packet).aggregate(Sum('total_errors'))
            elif level_structure_key.get('sub_project','') != 'All' and level_structure_key.get('work_packet','') != 'All' and level_structure_key.get('sub_packet','') != "All" and len(level_structure_key) == 3:
                sub_proj = level_structure_key['sub_project']
                wk_packet = level_structure_key['work_packet']
                sb_packet = level_structure_key['sub_packet']
                total_errors = Internalerrors.objects.filter(project=prj_id, center=center_obj, employee_id=agent,
                date__range=[date_list[0], date_list[-1]],sub_project = sub_proj, work_packet = wk_packet, sub_packet = sb_packet).aggregate(Sum('total_errors'))
            elif level_structure_key.get('work_packet','') != "All" and level_structure_key.get('sub_packet','') == "All" and len(level_structure_key) == 2:
                wk_packet = level_structure_key['work_packet']
                total_errors = Internalerrors.objects.filter(project=prj_id, center=center_obj, employee_id=agent,
                date__range=[date_list[0], date_list[-1]],work_packet = wk_packet).aggregate(Sum('total_errors'))
            elif level_structure_key.get('work_packet','') != "All" and level_structure_key.get('sub_packet','') != "All" and len(level_structure_key) == 2:
                wk_packet = level_structure_key['work_packet']
                sb_packet = level_structure_key['sub_packet']
                total_errors = Internalerrors.objects.filter(project=prj_id, center=center_obj, employee_id=agent,
                date__range=[date_list[0], date_list[-1]],work_packet = wk_packet, sub_packet = sb_packet).aggregate(Sum('total_errors'))
            else:
                wk_packet = level_structure_key['work_packet']
                total_errors = Internalerrors.objects.filter(project=prj_id, center=center_obj, employee_id=agent,
                date__range=[date_list[0], date_list[-1]],work_packet = wk_packet).aggregate(Sum('total_errors'))

        if total_errors['total_errors__sum'] > 0:
            for key, value in total_errors.iteritems():
                agent_name[agent] = value
        count = count + 1

    error_count = agent_name
    error_sum = sum(error_count.values())
    new_list, error_count_data, new_emp_list, accuracy_list = [], [], [], []
    new_dict, accuracy_dict, final_pareto_data = {}, {}, {}
    final_pareto_data['Error Count']={}
    final_pareto_data['Error Count']['Error Count'] =[]
    final_pareto_data['Cumulative %'] = {}
    final_pareto_data['Cumulative %']['Cumulative %'] = []
    emp_error_count = 0
    for key,value in sorted(error_count.iteritems(), key=lambda (k, v): (-v, k)):
        data_values = []
        data_values.append(key)
        data_values.append(value)
        error_count_data.append(value)
        new_emp_list.append(data_values)
        data_list = [] 
        emp_error_count = emp_error_count +value
        data_list.append(key)
        data_list.append(emp_error_count)
        new_list.append(data_list)

    final_pareto_data['Error Count']['Error Count'] = error_count_data[:10]
    new_dict.update(new_list)
    for key, value in new_dict.iteritems():
        if error_sum > 0:
            accuracy = (float(float(value)/float(error_sum)))*100
            accuracy_perc = float('%.2f' % round(accuracy, 2))
            accuracy_dict[key] = accuracy_perc
        else:
            accuracy_dict[key] = 0
    error_accuracy, final_emps = [], []
    for key, value in sorted(accuracy_dict.iteritems(), key=lambda (k, v): (v, k)):
        acc_list = []
        final_emps.append(key)
        error_accuracy.append(value)
    final_pareto_data['Cumulative %']['Cumulative %'] = error_accuracy[:10]
    final_data = pareto_graph_data(final_pareto_data)
    result = {}
    result['emp_names'] = final_emps[:10]
    result ['agent_pareto_data'] = final_data
    return result

def agent_external_pareto_data_generation(request,date_list,prj_id,center_obj,level_structure_key):
    prj_name = Project.objects.filter(id=prj_id).values_list('name', flat=True)
    center_name = Center.objects.filter(id=center_obj).values_list('name', flat=True)
    query_set = query_set_generation(prj_id, center_obj, level_structure_key, date_list)
    extrnal_volumes_list = Externalerrors.objects.filter(**query_set).values_list('employee_id',flat=True).distinct()
    agent_count = []
    extrnl_agent_name, extrnl_error_count = {}, {}
    count = 0
    for agent in extrnal_volumes_list:
        if level_structure_key.get('work_packet','') == "All" and level_structure_key.get('sub_project','') == "All" and len(level_structure_key) == 2:
            total_errors = Externalerrors.objects.filter(project=prj_id, center=center_obj, employee_id=agent,
            date__range=[date_list[0], date_list[-1]]).aggregate(Sum('total_errors'))
        elif level_structure_key.get('sub_packet','') == "All" and level_structure_key.get('work_packet','') == "All" and level_structure_key.get('sub_project','') == "All":
            total_errors = Externalerrors.objects.filter(project=prj_id, center=center_obj, employee_id=agent,
            date__range=[date_list[0], date_list[-1]]).aggregate(Sum('total_errors'))
        elif level_structure_key.get('work_packet','') == "All" and len(level_structure_key) == 1:
            total_errors = Externalerrors.objects.filter(project=prj_id, center=center_obj, employee_id=agent,
            date__range=[date_list[0], date_list[-1]]).aggregate(Sum('total_errors'))
        elif level_structure_key.get('sub_project','') == "All":
            total_errors = Externalerrors.objects.filter(project=prj_id, center=center_obj, employee_id=agent,
            date__range=[date_list[0], date_list[-1]]).aggregate(Sum('total_errors'))
        else:
            if level_structure_key.get('sub_project','') != 'All' and level_structure_key.get('work_packet','') == 'All' and level_structure_key.get('sub_packet','') == 'All':
                sub_proj = level_structure_key['sub_project']
                total_errors = Externalerrors.objects.filter(project=prj_id, center=center_obj, employee_id=agent,
                date__range=[date_list[0], date_list[-1]],sub_project = sub_proj).aggregate(Sum('total_errors'))
            elif level_structure_key.get('sub_project','') != 'All' and level_structure_key.get('work_packet','') != 'All' and level_structure_key.get('sub_packet', '') == "All" and len(level_structure_key) == 3:
                sub_proj = level_structure_key['sub_project']
                wk_packet = level_structure_key['work_packet']
                total_errors = Externalerrors.objects.filter(project=prj_id, center=center_obj, employee_id=agent,
                date__range=[date_list[0], date_list[-1]],sub_project = sub_proj, work_packet = wk_packet).aggregate(Sum('total_errors'))
            elif level_structure_key.get('sub_project','') != 'All' and level_structure_key.get('work_packet','') != 'All' and level_structure_key.get('sub_packet','') != "All" and len(level_structure_key) == 3:
                sub_proj = level_structure_key['sub_project']
                wk_packet = level_structure_key['work_packet']
                sb_packet = level_structure_key['sub_packet']
                total_errors = Externalerrors.objects.filter(project=prj_id, center=center_obj, employee_id=agent,
                sub_project = sub_proj, work_packet = wk_packet, sub_packet = sb_packet, date__range=[date_list[0], date_list[-1]]).aggregate(Sum('total_errors'))
            elif level_structure_key.get('work_packet','') != "All" and level_structure_key.get('sub_packet','') == "All" and len(level_structure_key) == 2:   
                wk_packet = level_structure_key['work_packet']
                total_errors = Externalerrors.objects.filter(project=prj_id, center=center_obj, employee_id=agent,
                date__range=[date_list[0], date_list[-1]],work_packet = wk_packet).aggregate(Sum('total_errors'))
            elif level_structure_key.get('work_packet','') != "All" and level_structure_key.get('sub_packet','') != "All" and len(level_structure_key) == 2:
                wk_packet = level_structure_key['work_packet']
                sb_packet = level_structure_key['sub_packet']
                total_errors = Externalerrors.objects.filter(project=prj_id, center=center_obj, employee_id=agent,
                date__range=[date_list[0], date_list[-1]],work_packet = wk_packet, sub_packet = sb_packet).aggregate(Sum('total_errors'))
            else:
                wk_packet = level_structure_key['work_packet']
                total_errors = Externalerrors.objects.filter(project=prj_id, center=center_obj, employee_id=agent,
                date__range=[date_list[0], date_list[-1]],work_packet = wk_packet).aggregate(Sum('total_errors'))

        if total_errors['total_errors__sum'] > 0:
            for key, value in total_errors.iteritems():
                extrnl_agent_name[agent] = value
        count = count + 1

    extrnl_error_count = extrnl_agent_name
    extrnl_error_sum = sum(extrnl_error_count.values())
    new_list = []
    new_extrnl_dict, extrnl_accuracy_dict, final_pareto_data = {}, {}, {}
    final_pareto_data['Error Count']={}
    final_pareto_data['Error Count']['Error Count'] =[]
    final_pareto_data['Cumulative %'] = {}
    final_pareto_data['Cumulative %']['Cumulative %'] = []
    extrnl_error_count_data = []

    emp_error_count = 0
    for key, value in sorted(extrnl_error_count.iteritems(), key=lambda (k, v): (-v, k)):
        extrnl_error_count_data.append(value)
        data_list = []
        emp_error_count = emp_error_count +value
        data_list.append(key)
        data_list.append(emp_error_count)
        new_list.append(data_list)
    new_extrnl_dict.update(new_list)
    final_pareto_data['Error Count']['Error Count'] = extrnl_error_count_data[:10]

    for key, value in new_extrnl_dict.iteritems():
        if extrnl_error_sum > 0:
            accuracy = (float(float(value)/float(extrnl_error_sum)))*100
            accuracy_perc = float('%.2f' % round(accuracy, 2))
            extrnl_accuracy_dict[key] = accuracy_perc
        else: 
            extrnl_accuracy_dict[key] = 0
    
    extrnl_error_accuracy,final_emps = [], []
    for key, value in sorted(extrnl_accuracy_dict.iteritems(), key=lambda (k, v): (v, k)):
        final_emps.append(key)
        extrnl_error_accuracy.append(value)
    final_pareto_data['Cumulative %']['Cumulative %'] = extrnl_error_accuracy[:10]
    final_data = pareto_graph_data(final_pareto_data)
    result_dict = {}
    result_dict['emp_names'] = final_emps[:10]
    result_dict ['agent_pareto_data'] = final_data
    return result_dict

def sample_pareto_analysis(request,date_list,prj_id,center_obj,level_structure_key,err_type):
    from api.graph_error import error_types_sum
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
    result, vol_error_values, vol_audit_data, extrnl_error_values, extrnl_err_type = {}, {}, {}, {}, {}
    extr_volumes_list_new, all_error_types, sub_error_types = [], [], []
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
                var = [conn.hgetall(cur_key) for cur_key in audit_key_list]
                if var:
                    var = var[0]
                else:
                    var = {}
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

    accuracy_cate_dict, final_external_pareto_data = {}, {}
    accuracy_cate_list = []
    final_external_pareto_data['Error Count'] = {}
    final_external_pareto_data['Error Count']['Error Count'] = []
    final_external_pareto_data['Cumulative %'] = {}
    final_external_pareto_data['Cumulative %']['Cumulative %'] = []
    indicidual_error_calc = error_types_sum(all_error_types)
    error_cate_sum = sum(indicidual_error_calc.values())
    error_list, cate_data_values = [], []
    cate_count = 0
    new_cate_dict = {}
    for key, value in sorted(indicidual_error_calc.iteritems(), key=lambda (k, v): (-v, k)):
        err_list = []
        cate_count = cate_count + value
        err_list.append(key)
        err_list.append(cate_count)
        cate_data_values.append(value)
        error_list.append(err_list)
    new_cate_dict.update(error_list)

    final_external_pareto_data['Error Count']['Error Count'] = cate_data_values[:10]
    cate_accuracy_list, final_cate_list = [], []
    cate_accuracy_dict = {}
    for key, value in new_cate_dict.iteritems():
        if error_cate_sum > 0:
            accuracy = (float(float(value) / float(error_cate_sum))) * 100
            accuracy_perc = float('%.2f' % round(accuracy, 2))
            cate_accuracy_dict[key] = accuracy_perc
        else:
            cate_accuracy_dict[key] = 100

    error_accuracy, final_cate_list = [], []
    for key, value in sorted(cate_accuracy_dict.iteritems(), key=lambda (k, v): (v, k)):
        acc_list = []
        final_cate_list.append(key)
        cate_accuracy_list.append(value)
    final_external_pareto_data['Cumulative %']['Cumulative %'] = cate_accuracy_list[:10]
    final_external_data = pareto_graph_data(final_external_pareto_data)
    result = {}
    result['category_name'] = final_cate_list[:10]
    result['category_pareto'] = final_external_data
    return result


def pareto_graph_data(pareto_dict):
    from api.graph_settings import graph_data_alignment
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
