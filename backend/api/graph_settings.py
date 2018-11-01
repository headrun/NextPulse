
import datetime
import redis
from api.models import *
from collections import defaultdict, OrderedDict
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
	if str(vol_name).find('Busy %') > 0:
            prod_dict['stack'] = str(vol_name).split(' Busy %')[0]
        if str(vol_name).find('Ready %') > 0:
            prod_dict['stack'] = str(vol_name).split(' Ready %')[0]
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



