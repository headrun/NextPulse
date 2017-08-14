
from django.apps import apps
from django.db.models import Max
from django.db.models import Sum
from api.models import *

def internal_extrnal_graphs(date_list,prj_id,center_obj,level_structure_key):
    prj_name = Project.objects.filter(id=prj_id).values_list('name', flat=True)
    center_name = Center.objects.filter(id=center_obj).values_list('name', flat=True)
    final_internal_data = internal_extrnal_graphs_same_formula(date_list, prj_id, center_obj,level_structure_key,err_type='Internal')
    final_external_data = internal_extrnal_graphs_same_formula(date_list, prj_id, center_obj,level_structure_key,err_type='External')
    final_internal_data.update(final_external_data)
    return final_internal_data



def tat_graph(date_list, prj_id, center,level_structure_key):
    new_dict = {}
    final_data,final_notmet_data = [],[]
    data_list, tat_val_list = [],[]
    for date_va in date_list:
        total_done_value = RawTable.objects.filter(project=prj_id, center=center, date=date_va).aggregate(Max('per_day'))
        if total_done_value['per_day__max'] > 0:
            data_list.append(str(date_va))
            count = 0
            tat_da = TatTable.objects.filter(project = prj_id,center= center,date=date_va)
            tat_met_value = tat_da.aggregate(Sum('met_count'))
            tat_not_met_value = tat_da.aggregate(Sum('non_met_count'))
            met_val = tat_met_value['met_count__sum']
            not_met_val = tat_not_met_value['non_met_count__sum']
            if met_val:
                tat_acc = (met_val/(met_val + not_met_val)) * 100
            else:
                tat_acc = 0
            tat_val_list.append(tat_acc)
    new_dict['tat_graph_details'] = tat_val_list
    return new_dict





def internal_bar_data(pro_id, cen_id, from_, to_, main_work_packet, chart_type,project):
    if (project == "Probe" and chart_type == 'External Accuracy') or (project == 'Ujjivan' and chart_type in ['External Accuracy','Internal Accuracy']) or (project == "IBM" and chart_type == 'External Accuracy'):
        date_range = num_of_days(to_, from_)
        final_internal_bar_drilldown = {} 
        final_internal_bar_drilldown['type'] = chart_type
        final_internal_bar_drilldown['project'] = project
        list_data, table_headers = [], []
        for date in date_range:
            accuracy_query_set = accuracy_query_generations(pro_id,cen_id,date,main_work_packet)
            if chart_type == 'External Accuracy':
                list_of = Externalerrors.objects.filter(**accuracy_query_set).values_list('employee_id','date','work_packet','total_errors','sub_packet')
            elif project == 'Ujjivan' and chart_type == 'Internal Accuracy':
                list_of = Internalerrors.objects.filter(**accuracy_query_set).values_list('employee_id', 'date','work_packet','total_errors','sub_packet')
            for i in list_of:
                per_day_value = RawTable.objects.filter(employee_id=i[0],date=i[1],work_packet=i[2]).values_list('per_day')
                try: 
                    per_day_value = per_day_value[0][0]
                except:
                    per_day_value = 0
                if per_day_value > 0:
                    list_data.append({'date':str(i[1]), 'total_errors':i[3], 'productivity': per_day_value})
                    Productivity_value = 0
                    Error_count = 0
                for ans in list_data:
                    if ans['productivity']:
                        Productivity_value = Productivity_value + ans['productivity']
                    if ans['total_errors']:
                        Error_count = Error_count + ans['total_errors']
                    if ans['productivity'] > 0:
                        accuracy = 100 - ((float(ans['total_errors']) / float(ans['productivity']))) * 100
                        accuracy_agg = float('%.2f' % round(accuracy, 2))
                        ans['accuracy'] = accuracy_agg
            if len(list_data)>0:
                table_headers = ['date','productivity','total_errors']
        final_internal_bar_drilldown['data'] = list_data
        final_internal_bar_drilldown['table_headers'] = table_headers
        final_internal_bar_drilldown['Productivity_value'] = Productivity_value
        final_internal_bar_drilldown['Error_count'] = Error_count
        return final_internal_bar_drilldown

    date_range = num_of_days(to_,from_)
    final_internal_bar_drilldown = {} 
    final_internal_bar_drilldown['type'] = chart_type
    final_internal_bar_drilldown['project'] = project
    internal_bar_list, table_headers, list_of = [], [], []
    for date in date_range:
        if chart_type == 'Internal Accuracy' or chart_type == 'Internal_Bar_Pie':
            packets_list = main_work_packet.split('_')
            packets_list_type = ''
            if len(packets_list) == 2:
                sub_project_statuts = Internalerrors.objects.filter(project=pro_id, center=cen_id, date=date).values_list('sub_project',flat=True)
                sub_project_statuts = filter(None, sub_project_statuts)
                if len(sub_project_statuts) > 0:
                    sub_project, work_packet = main_work_packet.split('_')
                    list_of = Internalerrors.objects.filter(project=pro_id, center=cen_id, date=date,sub_project=sub_project,work_packet=work_packet).values_list('employee_id', 'date', 'work_packet', 'audited_errors', 'total_errors')
                work_packet_statuts = Internalerrors.objects.filter(center=cen_id, project=pro_id,date=date).values_list('work_packet', flat=True)
                work_packet_statuts = filter(None, work_packet_statuts)
                if len(sub_project_statuts) == 0 and len(work_packet_statuts)>0:
                    work_packet, sub_packet = main_work_packet.split('_')
                    is_work_pac_exist = Internalerrors.objects.filter(project=pro_id, center=cen_id, date=date).values_list('work_packet', 'sub_packet').distinct()
                    if len(is_work_pac_exist) > 1:
                        list_of = Internalerrors.objects.filter(project=pro_id, center=cen_id, date=date,work_packet=work_packet).values_list('employee_id', 'date', 'work_packet', 'audited_errors', 'total_errors')
                    else:
                        list_of = Internalerrors.objects.filter(project=pro_id, center=cen_id, date=date,work_packet=work_packet).values_list('employee_id', 'date', 'work_packet', 'audited_errors', 'total_errors')
            elif len(packets_list) == 3:
                if '_' in work_packet:
                    sub_project, work_packet, sub_packet = main_work_packet.split('_')
                    list_of = Internalerrors.objects.filter(project=pro_id, center=cen_id, date=date,work_packet=work_packet,sub_packet=sub_packet).values_list('employee_id', 'date', 'work_packet', 'audited_errors', 'total_errors')
                else:
                    is_work_pac_exist = Internalerrors.objects.filter(project=pro_id, center=cen_id, date=date).values_list('work_packet', 'sub_packet').distinct()
                    if len(is_work_pac_exist) > 1:
                        list_of = Internalerrors.objects.filter(project=pro_id, center=cen_id, date=date,work_packet=work_packet).values_list('employee_id', 'date', 'work_packet', 'audited_errors', 'total_errors')
                    else:
                        list_of = Internalerrors.objects.filter(project=pro_id, center=cen_id, date=date,work_packet=work_packet).values_list('employee_id', 'date', 'work_packet', 'audited_errors', 'total_errors')
            else:
                sub_project_statuts = Internalerrors.objects.filter(project=pro_id,center=cen_id, date=date).values_list('sub_project',flat=True)
                sub_project_statuts = filter(None, sub_project_statuts)
                if len(sub_project_statuts) > 0:
                    packets_list_type = 'sub_project'
                    is_work_pac_exist = Internalerrors.objects.filter(project=pro_id,center=cen_id,date=date).values_list('sub_project', 'work_packet', 'sub_packet').distinct()
                    if len(is_work_pac_exist) > 1:
                        list_of = Internalerrors.objects.filter(project=pro_id,center=cen_id, date=date,sub_project=packets_list[0]).values_list('employee_id', 'date', 'work_packet', 'audited_errors', 'total_errors')
                    else:
                        list_of = Internalerrors.objects.filter(project=pro_id,center=cen_id, date=date,sub_project=packets_list[0]).values_list('employee_id', 'date', 'work_packet', 'audited_errors', 'total_errors')
                else:
                    packets_list_type = 'work_packet'
                    is_work_pac_exist = Internalerrors.objects.filter(project=pro_id,center=cen_id, date=date).values_list('work_packet', 'sub_packet').distinct()
                    if len(is_work_pac_exist) > 1:
                        list_of = Internalerrors.objects.filter(project=pro_id,center=cen_id, date=date,work_packet=packets_list[0]).values_list('employee_id', 'date', 'work_packet', 'audited_errors', 'total_errors')
                    else:
                        list_of = Internalerrors.objects.filter(project=pro_id,center=cen_id, date=date,work_packet=packets_list[0]).values_list('employee_id', 'date', 'work_packet', 'audited_errors', 'total_errors')
                        
        else:
            packets_list = main_work_packet.split('_')
            packets_list_type = ''
            list_of =[]
            if len(packets_list) == 2:
                sub_project_statuts = Externalerrors.objects.filter(project=pro_id,center=cen_id,date=date).values_list('sub_project', flat=True)
                sub_project_statuts = filter(None, sub_project_statuts)
                sub_project, work_packet = main_work_packet.split('_')
                if len(sub_project_statuts) > 0:
                    list_of = Externalerrors.objects.filter(project=pro_id, center=cen_id, date=date,sub_project=sub_project,work_packet=work_packet).values_list('employee_id', 'date','work_packet','audited_errors','total_errors')
                work_packet_statuts = Externalerrors.objects.filter(center=cen_id, project=pro_id,date=date).values_list('work_packet', flat=True)
                work_packet_statuts = filter(None, work_packet_statuts)
                if len(sub_project_statuts) == 0 and len(work_packet_statuts) > 0:
                    work_packet, sub_packet = main_work_packet.split('_')
                    is_work_pac_exist = Externalerrors.objects.filter(project=pro_id,center=cen_id,date=date).values_list('work_packet','sub_packet').distinct()
                    if len(is_work_pac_exist) > 1:
                        list_of = Externalerrors.objects.filter(project=pro_id,center=cen_id,work_packet=work_packet,date=date).values_list('employee_id','date','sub_packet','audited_errors','total_errors')

            elif len(packets_list) == 3:
                if '_' in work_packet:
                    sub_project, work_packet, sub_packet = main_work_packet.split('_')
                    list_of = Externalerrors.objects.filter(center=cen_id, project=pro_id, date=date,work_packet=work_packet, sub_packet=sub_packet).values_list('employee_id', 'date', 'work_packet', 'audited_errors', 'total_errors')
                else:
                    is_work_pac_exist = Externalerrors.objects.filter(project=pro_id, center=cen_id, date=date).values_list('work_packet','sub_packet').distinct()
                    if len(is_work_pac_exist) > 1:
                        list_of = Externalerrors.objects.filter(project=pro_id,center=cen_id,work_packet=work_packet, data=date).values_list('employee_id','date','work_packet','audited_errors','total_errors')
                    else:
                        list_of = Externalerrors.objects.filter(project=pro_id,center=cen_id,work_packet=work_packet, data=date).values_list('employee_id','date','work_packet','audited_errors','total_errors')
            else:
                sub_project_statuts = Externalerrors.objects.filter(project=pro_id, center=cen_id, date=date).values_list('sub_project', flat=True)
                sub_project_statuts = filter(None, sub_project_statuts)

                if len(sub_project_statuts) > 0:
                    packets_list_type = 'sub_project'
                    is_work_pac_exist = Externalerrors.objects.filter(project=pro_id,center=cen_id, date=date).values_list('sub_project','work_packet','sub_packet').distinct()
                    if len(is_work_pac_exist) > 1:
                        list_of = Externalerrors.objects.filter(project=pro_id, center=cen_id, sub_project=packets_list[0], date=date).values_list('employee_id','date','work_packet','audited_errors','total_errors')
                    else:
                        list_of = Externalerrors.objects.filter(project=pro_id, center=cen_id, sub_project=packets_list[0], date=date).values_list('employee_id','date','work_packet','audited_errors','total_errors')
                else:
                    packets_list_type = 'work_packet'
                    is_work_pac_exist = Externalerrors.objects.filter(project=pro_id,center=cen_id, date=date).values_list('work_packet','sub_packet').distinct()
                    if len(is_work_pac_exist) > 1:
                        list_of = Externalerrors.objects.filter(project=pro_id, center=cen_id, work_packet=packets_list[0],date=date).values_list('employee_id','date','work_packet','audited_errors','total_errors')
                    else:
                        list_of = Externalerrors.objects.filter(project=pro_id, center=cen_id, work_packet=packets_list[0],date=date).values_list('employee_id','date','work_packet','audited_errors','total_errors')
        for i in list_of:
            internal_bar_list.append({'date':str(i[1]), 'audited_count':i[3], 'total_errors':i[4]})
            audited_value = 0
            Error_count = 0
            for ans in internal_bar_list:
                if ans['audited_count']:
                    audited_value = audited_value + ans['audited_count']
                if ans['total_errors']:
                    Error_count = Error_count + ans['total_errors']
                if ans['total_errors'] >0 and ans['audited_count']>0:
                    accuracy = 100 - ((float(ans['total_errors']) / float(ans['audited_count']))) * 100
                    accuracy_agg = float('%.2f' % round(accuracy, 2))
                    ans['accuracy'] = accuracy_agg
                elif ans['total_errors']==0 and ans['audited_count']==0:
                    ans['accuracy'] = 0
                else:
                    ans['accuracy'] = 100
    if len(internal_bar_list) > 0:
        table_headers = ['date','audited_count', 'total_errors']
    final_internal_bar_drilldown['data'] = internal_bar_list
    final_internal_bar_drilldown['project'] = project
    final_internal_bar_drilldown['table_headers'] = table_headers
    final_internal_bar_drilldown['audited_value'] = audited_value
    final_internal_bar_drilldown['Error_count'] = Error_count
    return final_internal_bar_drilldown


def workpackets_list(level_structure_key,table_model_name,query_set):
    table_model = apps.get_model('api', 'Headcount')
    if level_structure_key.has_key('sub_project'):
        if level_structure_key['sub_project'] == "All":
            volume_list = table_model.objects.filter(**query_set).values('sub_project').distinct()
        else:
            if level_structure_key.has_key('work_packet'):
                if level_structure_key['work_packet'] == "All":
                    volume_list = table_model.objects.filter(**query_set).values('sub_project', 'work_packet').distinct()
                else:
                    volume_list = table_model.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()
    elif level_structure_key.has_key('work_packet') and len(level_structure_key) == 1:
        if level_structure_key['work_packet'] == "All":
            volume_list = table_model.objects.filter(**query_set).values('work_packet').distinct()
        else:
            volume_list = table_model.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()
    elif level_structure_key.has_key('work_packet') and level_structure_key.has_key('sub_packet'):
        volume_list = table_model.objects.filter(**query_set).values('sub_project', 'work_packet', 'sub_packet').distinct()
    else:
        volume_list = []
    return volume_list

def workpackets_list_utilization(level_structure_key,table_model_name,query_set):
    table_model = apps.get_model('api', 'Headcount')
    if level_structure_key.has_key('sub_project'):
        if level_structure_key['sub_project'] == "All":
            volume_list = table_model.objects.filter(**query_set).values('sub_project','work_packet').distinct()
        else:
            if level_structure_key.has_key('work_packet'):
                if level_structure_key['work_packet'] == "All":
                    volume_list = table_model.objects.filter(**query_set).values('sub_project', 'work_packet').distinct()
                else:
                    volume_list = table_model.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()
    elif level_structure_key.has_key('work_packet') and len(level_structure_key) == 1:
        if level_structure_key['work_packet'] == "All":
            volume_list = table_model.objects.filter(**query_set).values('work_packet').distinct()
        else:
            volume_list = table_model.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()
    elif level_structure_key.has_key('work_packet') and level_structure_key.has_key('sub_packet'):
        volume_list = table_model.objects.filter(**query_set).values('sub_project', 'work_packet', 'sub_packet').distinct()
    else:
        volume_list = []
    return volume_list

def worktrack_internal_external_workpackets_list(level_structure_key,table_model_name,query_set):
    table_model = apps.get_model('api', table_model_name)
    volume_list = []
    table_master_set = table_model.objects.filter(**query_set)
    if level_structure_key.has_key('sub_project'):
        if level_structure_key['sub_project'] == "All":
            volume_list = table_master_set.values('sub_project').distinct()
        else:
            if level_structure_key.has_key('work_packet'):
                if level_structure_key['work_packet'] == "All":
                    volume_list = table_master_set.values('sub_project', 'work_packet').distinct()
                else:
                    sub_packet = filter(None, Worktrack.objects.filter(**query_set).values('sub_packet').distinct())
                    volume_list = table_master_set.values('sub_project', 'work_packet','sub_packet').distinct()
                    if sub_packet:
                        volume_list = table_master_set.values('sub_project','work_packet').distinct()
    elif level_structure_key.has_key('work_packet') and len(level_structure_key) == 1:
        if level_structure_key['work_packet'] == "All":
            volume_list = table_master_set.values('sub_project', 'work_packet').distinct()
        else:
            sub_packet = filter(None, table_master_set.values('sub_packet').distinct())
            volume_list = table_master_set.values('sub_project', 'work_packet','sub_packet').distinct()
            if sub_packet:
                volume_list = table_master_set.values('sub_project', 'work_packet').distinct()
    elif level_structure_key.has_key('work_packet') and level_structure_key.has_key('sub_packet'):
        volume_list = table_master_set.values('sub_project', 'work_packet','sub_packet').distinct()
    else:
        volume_list = []
    return volume_list

def modified_utilization_calculations(center,prj_id,date_list,level_structure_key):
    final_utilization_result = {}
    final_utilization_result['fte_utilization'] = {}
    final_utilization_result['fte_utilization']['fte_utilization'] = []
    final_utilization_result['operational_utilization'] = {}
    final_utilization_result['operational_utilization']['operational_utilization'] = []
    final_utilization_result['overall_utilization'] = {}
    final_utilization_result['overall_utilization']['overall_utilization'] = []
    new_date_list = []
    status = 0
    if level_structure_key.get('sub_project','') == 'All':
        status = 1
    elif level_structure_key.get('work_packet','') == 'All':
        status = 1
    if status:
        final_prodictivity, product_date_values, utilization_date_values = {}, {}, {}
        product_date_values['total_prodictivity'], utilization_date_values['total_utilization'] = [] , [] 
        for date_va in date_list:
            total_done_value = RawTable.objects.filter(project=prj_id, center=center, date=date_va).aggregate(Max('per_day'))
            new_date_list.append(date_va)
            if total_done_value['per_day__max'] > 0: 
                headcount_details = Headcount.objects.filter(project=prj_id, center=center, date=date_va).aggregate(Sum('billable_hc'),
                                    Sum('billable_agents'),Sum('buffer_agents'),Sum('qc_or_qa'),Sum('teamlead'),
                                    Sum('trainees_and_trainers'),Sum('managers'),Sum('mis'))
                headcount_data = {}
                for hc_key,hc_value in headcount_details.iteritems():
                    headcount_data[hc_key] = hc_value
                    if hc_value == None:
                        headcount_data[hc_key] = 0
                util_numerator = headcount_data['billable_hc__sum']
                fte_denominator = headcount_data['billable_agents__sum'] + headcount_data['buffer_agents__sum'] + headcount_data['qc_or_qa__sum'] + headcount_data['teamlead__sum']
                operational_denominator  = fte_denominator + headcount_data['trainees_and_trainers__sum']
                overall_util_denominator = operational_denominator + headcount_data['managers__sum'] + headcount_data['mis__sum']
                if fte_denominator > 0:
                    fte_value = (float(float(util_numerator) / float(fte_denominator))) * 100
                    fte_value = float('%.2f' % round(fte_value, 2))
                else:
                    fte_value = 0
                final_utilization_result['fte_utilization']['fte_utilization'].append(fte_value)
                if operational_denominator > 0:
                    operational_value = (float(float(util_numerator) / float(operational_denominator))) * 100
                    operational_value = float('%.2f' % round(operational_value, 2))
                else:
                    operational_value = 0
                final_utilization_result['operational_utilization']['operational_utilization'].append(operational_value)
                if overall_util_denominator > 0:
                    overall_util_value = (float(float(util_numerator) / float(overall_util_denominator))) * 100
                    overall_util_value = float('%.2f' % round(overall_util_value, 2))
                else:
                    overall_util_value = 0
                final_utilization_result['overall_utilization']['overall_utilization'].append(overall_util_value)
    return final_utilization_result 




