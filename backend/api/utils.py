
import datetime
from api.models import *
from django.apps import apps
from django.db.models import Sum
from django.db.models import Max
from collections import OrderedDict
from common.utils import getHttpResponse as json_HttpResponse

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


def Packet_Alias_Names(prj_id,center_obj,widget_config_name):
    new_pkt_names = {} 
    productivity_series_list = [] 
    widget_id = Widgets.objects.filter(config_name=widget_config_name).values_list('id',flat=True)
    alias_packet_names = []
    if len(widget_id)>0:
        alias_widget_id = Alias_Widget.objects.filter(widget_name_id=widget_id[0],project=prj_id).values_list('id',flat=True)
        if len(alias_widget_id):
            alias_packet_names = Alias_packets.objects.filter(widget_id=alias_widget_id[0]).values('existed_name','alias_name')
    new_pkt_names = {}
    for packet_name in alias_packet_names:
        new_pkt_names[packet_name['existed_name']] = packet_name['alias_name']
    return new_pkt_names


def graph_data_alignment(volumes_data,name_key):
    color_coding = {}
    productivity_series_list = []
    for vol_name, vol_values in volumes_data.iteritems():
        if isinstance(vol_values, float):
            vol_values = float('%.2f' % round(vol_values, 2))
        prod_dict = {}
        prod_dict['name'] = vol_name.replace('NA_','').replace('_NA','')
        if name_key == 'y':
            prod_dict[name_key] = vol_values
        if name_key == 'data':
            if isinstance(vol_values, list):
                prod_dict[name_key] = vol_values
            else:
                prod_dict[name_key] = [vol_values]
        if vol_name in color_coding.keys():
            prod_dict['color'] = color_coding[vol_name]
        productivity_series_list.append(prod_dict)

    return productivity_series_list


def graph_data_alignment_other(volumes_data, work_packets, name_key):
    productivity_series_list = {}
    for vol_name, vol_values in volumes_data.iteritems():
        prod_main_dict={}
        prod_main_dict['x_axis']=[vol_name]
        prod_inner_dict = {}
        prod_inner_dict['name'] = vol_name
        prod_inner_dict[name_key] =vol_values
        prod_main_dict['y_axis'] = prod_inner_dict
        productivity_series_list[vol_name] = prod_main_dict
    if len(work_packets)<=1:
        return productivity_series_list
    if len((work_packets))>=2:
        if work_packets[0] in productivity_series_list.keys() and work_packets[1] in productivity_series_list.keys():
            prod_main_dict = {}
            prod_main_dict['x_axis'] = [work_packets[0],work_packets[1]]
            prod_inner_dict = {}
            prod_inner_dict[work_packets[0]] = productivity_series_list[work_packets[0]]['y_axis']
            prod_inner_dict[work_packets[1]] = productivity_series_list[work_packets[1]]['y_axis']
            prod_main_dict['y_axis'] = prod_inner_dict
            productivity_series_list[work_packets[0]] = prod_main_dict
        return productivity_series_list



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
            if sum(tat_val_list):
                tat_val_list = tat_val_list
            else:
                tat_val_list = []
    new_dict['tat_graph_details'] = tat_val_list
    return new_dict

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
                #fte_denominator = headcount_data['billable_agents__sum'] + headcount_data['buffer_agents__sum'] + headcount_data['qc_or_qa__sum'] + headcount_data['teamlead__sum']
                fte_denominator = headcount_data['billable_hc__sum'] + headcount_data['buffer_agents__sum'] + headcount_data['qc_or_qa__sum'] + headcount_data['teamlead__sum']
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


def volume_status_week(week_names,productivity_list,final_productivity):
    final_productivity =  OrderedDict()
    for final_key, final_value in productivity_list.iteritems():
        for week_key, week_value in final_value.iteritems():
            if week_key not in final_productivity.keys():
                final_productivity[week_key] = [] 
    for prod_week_num in week_names:
        if len(productivity_list.get(prod_week_num,'')) > 0: 
            for vol_key, vol_values in productivity_list[prod_week_num].iteritems():
                if final_productivity.has_key(vol_key):
                    if vol_key == 'Opening':
                        final_productivity[vol_key].append(vol_values[0])
                    elif vol_key == 'Closing balance':
                        final_productivity[vol_key].append(vol_values[-1])
                    else:
                        if isinstance(vol_values,list):
                            vol_values = sum(vol_values)
                        final_productivity[vol_key].append(vol_values)
                else:
                    if isinstance(vol_values,list):
                        vol_values = sum(vol_values)
                    final_productivity[vol_key] = [vol_values]
            for prod_key, prod_values in final_productivity.iteritems():
                if prod_key not in productivity_list[prod_week_num].keys():
                    final_productivity[prod_key].append(0)
        else:
            for vol_key, vol_values in final_productivity.iteritems():
                final_productivity[vol_key].append(0)
    return final_productivity


def received_volume_week(week_names,productivity_list,final_productivity):
    productivity_data = {}
    for final_key, final_value in productivity_list.iteritems():
        for week_key, week_value in final_value.iteritems():
            if week_key not in final_productivity.keys():
                final_productivity[week_key] = []
    for prod_week_num in week_names:
        if len(productivity_list.get(prod_week_num,'')) > 0:
            values = productivity_list[prod_week_num]
            flag = isinstance(values.get('Received',""), list) & isinstance(values.get('Completed',""), list) & isinstance(values.get('Opening',""), list)
            if flag:
                if len(values['Received']) == len(values['Opening']):
                    values['Received'][0] = values['Received'][0] + values['Opening'][0]
                    values['Received'] = sum(values['Received'])
                    values['Completed'] = sum(values['Completed'])
                    productivity_data.update(values)
                    del productivity_data['Opening']
                    for vol_key,vol_values in productivity_data.iteritems():
                        if final_productivity.has_key(vol_key):
                            final_productivity[vol_key].append(vol_values)
                        else:
                            final_productivity[vol_key] = [vol_values]

                for prod_key, prod_values in final_productivity.iteritems():
                    if prod_key not in productivity_list[prod_week_num].keys():
                        final_productivity[prod_key].append(0)
        else:
            for vol_key, vol_values in final_productivity.iteritems():
                final_productivity[vol_key].append(0)
    if final_productivity.has_key('Opening'):
        del final_productivity['Opening']
    else:
        final_productivity = final_productivity
    return final_productivity


def prod_volume_prescan_week_util(week_names,productivity_list,final_productivity):
    for final_key, final_value in productivity_list.iteritems():
        for week_key, week_value in final_value[0].iteritems():
            if week_key not in final_productivity.keys():
                final_productivity[week_key] = []
    for prod_week_num in week_names:
        if len(productivity_list.get(prod_week_num,'')) > 0:
            for vol_key, vol_values in productivity_list[prod_week_num][0].iteritems():
                if final_productivity.has_key(vol_key):
                    if isinstance(vol_values,list):
                        new_values= [k for k in vol_values if k!=0]
                        if len(new_values)>0:
                            vol_values = float(float(sum(vol_values))/len(new_values))
                        else:
                            vol_values = sum(vol_values)
                    vol_values = float('%.2f' % round(vol_values, 2))
                    final_productivity[vol_key].append(vol_values)
                else:
                    if isinstance(vol_values,list):
                        if len(vol_values)>0:
                            vol_values = float(float(sum(vol_values))/len(vol_values))
                        else:
                            vol_values = sum(vol_values)
                    final_productivity[vol_key] = [vol_values]
            for prod_key, prod_values in final_productivity.iteritems():
                if prod_key not in productivity_list[prod_week_num][0].keys():
                    final_productivity[prod_key].append(0)
        else:
            for vol_key, vol_values in final_productivity.iteritems():
                final_productivity[vol_key].append(0)

    return final_productivity


def prod_volume_upload_week_util(week_names,productivity_list,final_productivity):
    for final_key, final_value in productivity_list.iteritems():
        for week_key, week_value in final_value.iteritems():
            if week_key not in final_productivity.keys():
                final_productivity[week_key] = []
    for prod_week_num in week_names:
        if len(productivity_list.get(prod_week_num,'')) > 0:
            for vol_key, vol_values in productivity_list[prod_week_num].iteritems():
                if final_productivity.has_key(vol_key):
                    if isinstance(vol_values,list):
                        new_values= [k for k in vol_values if k!=0]
                        if len(new_values)>0:
                            vol_values = float(float(sum(vol_values))/len(new_values))
                        else:
                            vol_values = sum(vol_values)
                    vol_values = float('%.2f' % round(vol_values, 2))
                    final_productivity[vol_key].append(vol_values)
                else:
                    if isinstance(vol_values,list):
                        if len(vol_values)>0:
                            vol_values = float(float(sum(vol_values))/len(vol_values))
                        else:
                            vol_values = sum(vol_values)
                    final_productivity[vol_key] = [vol_values]
            for prod_key, prod_values in final_productivity.iteritems():
                if prod_key not in productivity_list[prod_week_num].keys():
                    final_productivity[prod_key].append(0)
        else:
            for vol_key, vol_values in final_productivity.iteritems():
                final_productivity[vol_key].append(0)

    return final_productivity


def prod_volume_week(week_names,productivity_list,final_productivity):
    for final_key, final_value in productivity_list.iteritems():
        for week_key, week_value in final_value.iteritems():
            if week_key not in final_productivity.keys():
                final_productivity[week_key] = []
    for prod_week_num in week_names:
        if len(productivity_list.get(prod_week_num,'')) > 0:
            for vol_key, vol_values in productivity_list[prod_week_num].iteritems():
                if final_productivity.has_key(vol_key):
                    if isinstance(vol_values,list):
                        vol_values = sum(vol_values)
                    final_productivity[vol_key].append(vol_values)
                else:
                    if isinstance(vol_values,list):
                        vol_values = sum(vol_values)
                    final_productivity[vol_key] = [vol_values]
            for prod_key, prod_values in final_productivity.iteritems():
                if prod_key not in productivity_list[prod_week_num].keys():
                    final_productivity[prod_key].append(0)
        else:
            for vol_key, vol_values in final_productivity.iteritems():
                final_productivity[vol_key].append(0)
    return final_productivity


def prod_volume_week_util_headcount(week_names,productivity_list,final_productivity):
    for final_key, final_value in productivity_list.iteritems():
        for week_key, week_value in final_value.iteritems():
            if week_key not in final_productivity.keys():
                final_productivity[week_key] = []
    for prod_week_num in week_names:
        if len(productivity_list.get(prod_week_num,'')) > 0:
            for vol_key, vol_values in productivity_list[prod_week_num].iteritems():
                if final_productivity.has_key(vol_key):
                    if isinstance(vol_values,list):
                        new_values= [k for k in vol_values if k!=0] 
                        if len(new_values)>0:
                            vol_values = float(float(sum(vol_values))/len(new_values))
                        else: 
                            vol_values = sum(vol_values)
                    vol_values = float('%.2f' % round(vol_values, 2))
                    final_productivity[vol_key].append(vol_values)
                else: 
                    if isinstance(vol_values,list):
                        if len(vol_values)>0:
                            vol_values = float(float(sum(vol_values))/len(vol_values))
                        else: 
                            vol_values = sum(vol_values)
                    final_productivity[vol_key] = [vol_values]
            for prod_key, prod_values in final_productivity.iteritems():
                if prod_key not in productivity_list[prod_week_num].keys():
                    final_productivity[prod_key].append(0)
        else: 
            for vol_key, vol_values in final_productivity.iteritems():
                final_productivity[vol_key].append(0)
    return final_productivity


def prod_volume_week_util(prj_id,week_names,productivity_list,final_productivity,week_or_month):
    var = Project.objects.filter(id=prj_id).values('days_week','days_month')[0]
    for final_key, final_value in productivity_list.iteritems():
        for week_key, week_value in final_value.iteritems():
            if week_key not in final_productivity.keys():
                final_productivity[week_key] = []
    
    for prod_week_num in week_names:
        if len(productivity_list.get(prod_week_num,'')) > 0:
            for vol_key, vol_values in productivity_list[prod_week_num].iteritems():
                if final_productivity.has_key(vol_key):
                    if isinstance(vol_values,list):
                        new_values= [k for k in vol_values if k!=0]
                        for key,value in var.iteritems():
                            if key == 'days_week' and week_or_month == 'week':
                                if len(new_values)> 5:
                                    vol_values = float(float(sum(vol_values))/value)
                                    vol_values = float('%.2f' % round(vol_values, 2))
                                elif len(new_values) <= 5 and len(new_values) != 0:
                                    vol_values = float(float(sum(vol_values))/len(new_values))
                                    vol_values = float('%.2f' % round(vol_values, 2))
                                else:
                                    vol_values = sum(vol_values)
                            elif key == 'days_month' and week_or_month == 'month':
                                if len(new_values)> 21:
                                    vol_values = float(float(sum(vol_values))/value)
                                    vol_values = float('%.2f' % round(vol_values, 2))
                                elif len(new_values) <= 21 and len(new_values) != 0:
                                    vol_values = float(float(sum(vol_values))/len(new_values))
                                    vol_values = float('%.2f' % round(vol_values, 2))
                                else:
                                    vol_values = sum(vol_values)
                        final_productivity[vol_key].append(vol_values)
                else:
                    if isinstance(vol_values,list):
                        if len(vol_values)>0:
                            vol_values = float(float(sum(vol_values))/len(vol_values))
                    else:
                            vol_values = sum(vol_values)
                    final_productivity[vol_key] = [vol_values]
            for prod_key, prod_values in final_productivity.iteritems():
                if prod_key not in productivity_list[prod_week_num].keys():
                    final_productivity[prod_key].append(0)
        else:
            for vol_key, vol_values in final_productivity.iteritems():
                final_productivity[vol_key].append(0)
    
    return final_productivity


