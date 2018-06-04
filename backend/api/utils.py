
import datetime
from api.models import *
from django.apps import apps
from django.db.models import Sum
from django.db.models import Max
from collections import OrderedDict
from api.basics import *
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
    final_productivity =  OrderedDict()
    productivity_data = {} 
    for prod_week_num in week_names:
        if len(productivity_list.get(prod_week_num,'')) > 0:
            values = productivity_list[prod_week_num]
            flag = isinstance(values.get('Received',""), list) & isinstance(values.get('Completed',""), list) & isinstance(values.get('Opening',""), list)
            if flag:
                if len(values['Received']) == len(values['Opening']) and len(values['Opening']) >= 1:                    
                    productivity_data['Received'] = values['Opening'][0] + sum(values['Received_week'])
                    productivity_data['Completed'] = sum(values['Completed'])
                    
                    for prod_key, prod_values in productivity_data.iteritems():
                        if final_productivity.has_key(prod_key):
                            final_productivity[prod_key].append(prod_values)
                        else:
                            final_productivity[prod_key] = [prod_values]

                    for prod_key, prod_values in final_productivity.iteritems():
                        if prod_key not in productivity_list[prod_week_num].keys():
                            final_productivity[prod_key].append(0)
                else:
                    final_productivity['Completed'] = [0]
                    final_productivity['Received'] = [0]
                        
            else:
                for vol_key in productivity_list[prod_week_num].keys():
                    if vol_key != 'Opening':
                        final_productivity[vol_key].append(0)              
        else:
            final_productivity['Completed'] = [0]
            final_productivity['Received'] = [0]    
    
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


