
import datetime
import redis
from api.models import *
from collections import defaultdict, OrderedDict
#from collections import OrderedDict
from django.db.models import Max, Sum
from api.query_generations import query_set_generation
from api.utils import Packet_Alias_Names
from api.basics import level_hierarchy_key
from common.utils import getHttpResponse as json_HttpResponse


def graph_data_alignment_color(volumes_data,name_key,level_structure_key,prj_id,center_obj,widget_config_name=''): 
    packet_color_query = query_set_generation(prj_id,center_obj,level_structure_key,[]) 
    color_query_set = Color_Mapping.objects.filter(**packet_color_query)
    if level_structure_key.has_key('sub_project'):
        if level_structure_key['sub_project'] == "All":
            colors_list = color_query_set.values('sub_project','color_code').distinct()
        else:
            if level_structure_key.has_key('work_packet'):
                if level_structure_key['work_packet'] == "All":
                    sub_packets_list = color_query_set.values_list('sub_packet',flat=True)
                    sub_packets_list = filter(None,sub_packets_list)
                    colors_list = color_query_set.exclude(sub_packet__in=sub_packets_list).values('sub_project','work_packet','color_code').distinct()
                else:
                    colors_list = color_query_set.values('sub_project','work_packet','sub_packet','color_code').distinct()
    elif level_structure_key.has_key('work_packet') and len(level_structure_key) == 1:
        if level_structure_key['work_packet'] == "All":
            colors_list = color_query_set.values('work_packet','sub_packet','color_code').distinct()
            colors_list = [d for d in colors_list if d.get('sub_packet') == '']
        else:
            colors_list = color_query_set.values('sub_project','work_packet','sub_packet','color_code').distinct()
    elif level_structure_key.has_key('work_packet') and level_structure_key.has_key('sub_packet'):
        colors_list = color_query_set.values('sub_project','work_packet','sub_packet','color_code').distinct()
    else:
        colors_list = [] 
    color_mapping = {} 
    for local_wp_color in colors_list :
        wp_color = {} 
        for wp_key,wp_value in local_wp_color.iteritems():
            if wp_value != '':
                wp_color[wp_key] = wp_value

        wp_color_count = len(wp_color)
        if wp_color_count == 4:
            key = '{0}_{1}_{2}'.format(wp_color['sub_project'],wp_color['work_packet'],wp_color['sub_packet'])
            color_mapping[key] = wp_color['color_code']
        elif wp_color_count == 3:
            if wp_color.has_key('sub_project') :
                key = '{0}_{1}'.format(wp_color['sub_project'], wp_color['work_packet'])
                color_mapping[key] = wp_color['color_code']
            else:
                key = '{0}_{1}'.format(wp_color['work_packet'], wp_color['sub_packet'])
                color_mapping[key] = wp_color['color_code']
        elif wp_color_count == 2:
            item = wp_color.pop('color_code')
            key = wp_color.keys()[0]
            color_mapping[wp_color[key]] = item

    productivity_series_list = []
    new_pkt_names = Packet_Alias_Names(prj_id,center_obj,widget_config_name)
    for vol_name, vol_values in volumes_data.iteritems():
        if isinstance(vol_values, float):
            vol_values = float('%.2f' % round(vol_values, 2))
        prod_dict = {}
        prod_dict['name'] = vol_name.replace('NA_','').replace('_NA','')
        if new_pkt_names.has_key(prod_dict['name']):
            prod_dict['name'] = new_pkt_names[prod_dict['name']]
        if vol_name in['total_utilization','total_workdone','total_prodictivity']:
            if vol_name == 'total_utilization':
                prod_dict['name'] = 'Total Utilization'
            elif vol_name == 'total_workdone':
                prod_dict['name'] = 'Total Workdone'
            elif vol_name == 'total_prodictivity':
                prod_dict['name'] = 'Total Productivity'
        if vol_name in ['target_line','total_target']:
            prod_dict['dashStyle'] = 'dash'
            if vol_name == 'target_line':
                prod_dict['name'] = 'Target Line'
            elif vol_name == 'total_target':
                prod_dict['name'] = 'Total Target'

        if name_key == 'y':
            prod_dict[name_key] = vol_values
        if name_key == 'data':
            if isinstance(vol_values, list):
                prod_dict[name_key] = vol_values
            else:
                prod_dict[name_key] = [vol_values]
        if vol_name in color_mapping.keys():
            prod_dict['color'] = color_mapping[vol_name]
        productivity_series_list.append(prod_dict)
    return productivity_series_list


def product_total_graph(date_list,prj_id,center_obj,level_structure_key):
    ratings = defaultdict(list)
    conn = redis.Redis(host="localhost", port=6379, db=0)
    result, volumes_dict, date_values = {}, {}, {}
    #prj_name = Project.objects.filter(id=prj_id).values_list('name',flat=True)
    #center_name = Center.objects.filter(id=center_obj).values_list('name', flat=True)
    project = Project.objects.filter(id=prj_id)
    prj_name = project[0].name
    center_name = project[0].center.name
    query_set = query_set_generation(prj_id,center_obj,level_structure_key,date_list)
    main_set = RawTable.objects.filter(**query_set)
    new_date_list = []
    total_done_value = RawTable.objects.filter(project=prj_id, center=center_obj, date__range=[date_list[0], date_list[-1]]).values('date').annotate(total=Sum('per_day'))
    values = OrderedDict(zip(map(lambda p: str(p['date']), total_done_value), map(lambda p: str(p['total']), total_done_value)))
    for date_key, total_val in values.iteritems():
    #for date_va in date_list:
        #total_done_value = RawTable.objects.filter(project=prj_id,center=center_obj,date=date_va).aggregate(Max('per_day'))
        #if total_done_value['per_day__max'] > 0:
        if total_val > 0:
            #new_date_list.append(date_va)
            new_date_list.append(date_key)
            if level_structure_key.has_key('sub_project'):
                if level_structure_key['sub_project'] == "All":
                    volume_list = main_set.values('sub_project').distinct()
                else:
                    if level_structure_key.has_key('work_packet'):
                        if level_structure_key['work_packet'] == "All":
                            volume_list = main_set.values('sub_project','work_packet').distinct()
                        else:
                            volume_list = main_set.values('sub_project','work_packet','sub_packet').distinct()
            elif level_structure_key.has_key('work_packet') and len(level_structure_key) ==1:
                if level_structure_key['work_packet'] == "All":
                    volume_list = main_set.values('sub_project','work_packet').distinct()
                else:
                    volume_list = main_set.values('sub_project', 'work_packet','sub_packet').distinct()
            elif level_structure_key.has_key('work_packet') and level_structure_key.has_key('sub_packet'):
                volume_list = main_set.values('sub_project','work_packet','sub_packet').distinct()
            else:
                volume_list = []

            count =0
            for vol_type in volume_list:
                final_work_packet = level_hierarchy_key(level_structure_key,vol_type)
                if not final_work_packet:
                    final_work_packet = level_hierarchy_key(volume_list[count],vol_type)
                count = count+1
                #date_pattern = '{0}_{1}_{2}_{3}'.format(prj_name[0], str(center_name[0]), str(final_work_packet), str(date_va))
                date_pattern = '{0}_{1}_{2}_{3}'.format(prj_name, center_name, str(final_work_packet), date_key)
                key_list = conn.keys(pattern=date_pattern)
                if not key_list:
                    if date_values.has_key(final_work_packet):
                        date_values[final_work_packet].append(0)
                    else:
                        date_values[final_work_packet] = [0]
                var = [conn.hgetall(cur_key) for cur_key in key_list]
                for one in var:
                    main = one.items()[0]
                    key = main[0]
                    value = main[1]
                    if value == 'None':
                        value = 0
                    if date_values.has_key(key):
                        date_values[key].append(int(value))
                    else:
                        date_values[key] = [int(value)]
                    volumes_dict['data'] = date_values
                    volumes_dict['date'] = new_date_list
                    result['data'] = volumes_dict

    try:
        volumes_data = result['data']['data']
    except:
        result['data']={}
        result['data']['data'] = {}
        volumes_data = result['data']['data']
        volumes_data = {}
    if None in volumes_data.keys():
        del volumes_data[None]
    result['prod_days_data'] = volumes_data
    query_set = query_set_generation(prj_id,center_obj,level_structure_key, [])
    main_target_set = Targets.objects.filter(**query_set)

    if 'All' not in level_structure_key.values():
        packet_target = Targets.objects.filter(**query_set).values('sub_project', 'work_packet', 'sub_packet', 'target_type').distinct()
        final_packet_target = packet_target.filter(target_type='Production').values('target_value')
        target_line = []
        if final_packet_target:
            for date_va in new_date_list:
                target_line.append(int(final_packet_target[0]['target_value']))
            if len(result['prod_days_data']) == 1:
                result['prod_days_data']['target_line'] = target_line
                                
    volume_bar_data, volume_keys_data = {}, {}
    volume_bar_data['volume_type']= volumes_data.keys()
    for key,value in volumes_data.iteritems():
        volume_keys_data[key]= sum(value)
    volume_list_data=[]
    volume_dict = {}
    for key,value in volume_keys_data.iteritems() :
        new_list=[]
        try:
            if 'DetailFinancial' not in key:
                if volume_dict.has_key(key):
                    new_list.append(volume_dict[key])
                else:
                    new_list.append(key)
                new_list.append(value)
                volume_list_data.append(new_list)
        except:
            pass
    volume_bar_data['volume_new_data']=volume_list_data
    volume_bar_data['volume_values'] = volume_keys_data
    result['volumes_data'] = volume_bar_data
    return result

