#from collections import OrderedDict
import datetime
import redis
from api.models import *
from api.basics import *
#from collections import OrderedDict
import collections
from django.db.models import Max, Sum
from api.query_generations import query_set_generation
from api.graph_settings import graph_data_alignment_color
from common.utils import getHttpResponse as json_HttpResponse

def fte_calculation_sub_project_work_packet(result,level_structure_key):
    final_fte ={}
    count = 0
    if result.has_key('data'):
        new_date_list = result['new_date_list']
        wp_subpackets = result['wp_subpackets']
        for date_va in new_date_list:
            for wp_key_new, wp_name in wp_subpackets.iteritems():
                local_sum = 0
                for sub_packet in wp_name:
                    new_level_structu_key = {}
                    if level_structure_key.has_key('sub_project'):
                        new_level_structu_key['sub_project'] = level_structure_key['sub_project']
                    new_level_structu_key['work_packet'] = wp_key_new
                    new_level_structu_key['sub_packet'] = sub_packet
                    new_level_structu_key['from_date__lte'] = date_va
                    new_level_structu_key['to_date__gte'] = date_va
                    final_work_packet = level_hierarchy_key(level_structure_key, new_level_structu_key)
                    if result['data']['data'].has_key(final_work_packet):
                        if len(result['data']['data'][final_work_packet]) >= count:
                            try:
                                local_sum = local_sum + result['data']['data'][final_work_packet][count]
                            except:
                                local_sum = local_sum
                        else:
                            local_sum = local_sum
                    else:
                        local_sum = local_sum
                if level_structure_key.get('work_packet', '') != 'All':
                    if final_fte.has_key(final_work_packet):
                        final_fte_sum = float('%.2f' % round(local_sum, 2))
                        final_fte[final_work_packet].append(final_fte_sum)
                    else:
                        final_fte_sum = float('%.2f' % round(local_sum, 2))
                        final_fte[final_work_packet] = [final_fte_sum]
                if level_structure_key.get('work_packet', '') == 'All':
                    if level_structure_key.has_key('sub_project'):
                        new_level_structu_key['sub_project'] = level_structure_key['sub_project']
                    new_level_structu_key['work_packet'] = wp_key_new
                    wp_final_work_packet = level_hierarchy_key(level_structure_key, new_level_structu_key)
                    if final_fte.has_key(wp_final_work_packet):
                        final_fte_sum = float('%.2f' % round(local_sum, 2))
                        final_fte[wp_final_work_packet].append(final_fte_sum)
                    else:
                        final_fte_sum = float('%.2f' % round(local_sum, 2))
                        final_fte[wp_final_work_packet] = [final_fte_sum]
            count = count + 1            
        return final_fte


def fte_calculation_sub_project_sub_packet(prj_id,center_obj,work_packet_query,level_structure_key,date_list):
    packets_target, wp_subpackets = {}, {}
    new_date_list = []
    conn = redis.Redis(host="localhost", port=6379, db=0)
    project = Project.objects.filter(id=prj_id)
    prj_name = project[0].name
    center_name = project[0].center.name
    distinct_wp = Targets.objects.filter(**work_packet_query).values_list('work_packet', flat=True).distinct()
    new_work_packet_query = work_packet_query
    for wrk_pkt in distinct_wp:
        work_packet_query['work_packet'] = wrk_pkt
        work_packet_query['target_type'] = 'FTE Target'
        distinct_sub_pkt = Targets.objects.filter(**work_packet_query).values_list('sub_packet', flat=True).distinct()
        wp_subpackets[wrk_pkt] = distinct_sub_pkt
    raw_query_set = {}
    raw_query_set['project'] = prj_id
    raw_query_set['center'] = center_obj
    date_values, volumes_dict, result = {}, {}, {}
    total_done_value = RawTable.objects.filter(project=prj_id, center=center_obj, date__range=[date_list[0], date_list[-1]])\
                       .values('date').annotate(total=Sum('per_day'))
    values = OrderedDict(zip(map(lambda p: str(p['date']), total_done_value), map(lambda p: str(p['total']), total_done_value)))
    for date_key, total_val in values.iteritems():
        new_work_packet_query['from_date__lte'] = date_key
        new_work_packet_query['to_date__gte'] = date_key
        if new_work_packet_query.has_key('work_packet'):
            del new_work_packet_query['work_packet']
        work_packets = Targets.objects.filter(**new_work_packet_query)\
                        .values('sub_project', 'work_packet', 'sub_packet','target_value').distinct()
        for wp_dict in work_packets:
            packets_target[wp_dict['sub_packet']] = int(wp_dict['target_value'])
        if total_val > 0:
            new_date_list.append(date_key)
            for wp_key, wp_name in wp_subpackets.iteritems():
                for sub_packet in wp_name:
                    new_level_structu_key = {}
                    if level_structure_key.has_key('sub_project'):
                        new_level_structu_key['sub_project'] = level_structure_key['sub_project']
                    new_level_structu_key['work_packet'] = wp_key
                    new_level_structu_key['sub_packet'] = sub_packet
                    new_level_structu_key['from_date__lte'] = date_key
                    new_level_structu_key['to_date__gte'] = date_key
                    final_work_packet = level_hierarchy_key(level_structure_key, new_level_structu_key)
                    date_pattern = '{0}_{1}_{2}_{3}'.format(prj_name, center_name, str(final_work_packet), date_key)
                    key_list = conn.keys(pattern=date_pattern)
                    packets_values = Targets.objects.filter(**new_level_structu_key)\
                                     .values('sub_project', 'work_packet', 'sub_packet','target_value').distinct()
                    if not key_list:
                        if date_values.has_key(final_work_packet):
                            date_values[final_work_packet].append(0)
                        else:
                            date_values[final_work_packet] = [0]
                    for cur_key in key_list:
                        var = conn.hgetall(cur_key)
                        for key, value in var.iteritems():
                            if value == 'None':
                                value = 0
                            if date_values.has_key(key):
                                if packets_values:
                                    try:
                                        fte_sum = float(value) / packets_target[sub_packet]
                                    except:
                                        fte_sum = 0
                                else:
                                    fte_sum = 0
                                date_values[key].append(fte_sum)
                            else:
                                if packets_target.has_key(sub_packet)>0:
                                    if packets_target[sub_packet]>0:
                                        fte_sum = float(value) / packets_target[sub_packet]
                                        date_values[key] = [fte_sum]
                        volumes_dict['data'] = date_values
                        volumes_dict['date'] = date_list
                        result['data'] = volumes_dict
    result['wp_subpackets'] = wp_subpackets
    result['new_date_list'] = new_date_list
    return result

def fte_calculation(request,prj_id,center_obj,date_list,level_structure_key):
    query_set = {}
    query_set['project'] = prj_id
    query_set['center'] = center_obj
    project = Project.objects.filter(id=prj_id)
    prj_name = project[0].name
    center_name = project[0].center.name
    work_packet_query =  query_set_generation(prj_id,center_obj,level_structure_key,[])
    work_packet_query['target_type'] = 'FTE Target'
    work_packets = Targets.objects.filter(**work_packet_query).values('sub_project','work_packet','sub_packet','target_value').distinct()
    sub_packet_query = query_set_generation(prj_id,center_obj,level_structure_key,[])
    sub_packet_query['target_type'] = 'FTE Target'
    sub_packets = filter(None,Targets.objects.filter(**sub_packet_query).values_list('sub_packet',flat=True).distinct())
    conn = redis.Redis(host="localhost", port=6379, db=0)
    new_date_list = []
    status = 0
    if len(sub_packets) == 0:
        work_packets = Targets.objects.filter(**work_packet_query)\
                       .values('sub_project', 'work_packet', 'sub_packet','target_value').distinct()
        date_values, volumes_dict, result = {}, {}, {}
        total_done_value = RawTable.objects.filter(project=prj_id, center=center_obj, date__range=[date_list[0], date_list[-1]])\
                             .values('date').annotate(total=Sum('per_day'))
        values = OrderedDict(zip(map(lambda p: str(p['date']), total_done_value), map(lambda p: str(p['total']), total_done_value)))
        for date_key, total_val in values.iteritems():
            if total_val > 0:
                new_date_list.append(date_key)
                for wp_packet in work_packets:
                    final_work_packet = level_hierarchy_key(level_structure_key, wp_packet)
                    date_pattern = '{0}_{1}_{2}_{3}'.format(prj_name, center_name, str(final_work_packet), date_key)
                    key_list = conn.keys(pattern=date_pattern)
                    if wp_packet['target_value'] >0:
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
                                fte_sum = float(value) / int(wp_packet['target_value'])
                                date_values[key].append(fte_sum)
                            else:
                                fte_sum = float(value) / int(wp_packet['target_value'])
                                date_values[key] = [fte_sum]
                        volumes_dict['data'] = date_values
                        volumes_dict['date'] = date_list
                        result['data'] = volumes_dict
    else:
        if level_structure_key.get('sub_project','')=='All':
            sub_projects = filter(None, Targets.objects.filter(**sub_packet_query).values_list('sub_project',flat=True).distinct())
            final_fte = {}
            for sub_project in sub_projects:
                sub_project_query = {}
                sub_project_query['project'] = prj_id
                sub_project_query['center'] = center_obj
                sub_project_query['sub_project'] = sub_project
                sub_project_query['target_type'] = 'FTE Target'
                new_level_structu_key = {}
                new_level_structu_key['sub_project'] = sub_project
                new_level_structu_key['work_packet'] = 'All'
                new_level_structu_key['sub_packet'] = 'All'
                result = fte_calculation_sub_project_sub_packet(prj_id, center_obj, sub_project_query, new_level_structu_key,date_list)
                sub_packet_data = fte_calculation_sub_project_work_packet(result, new_level_structu_key)
                if sub_packet_data :
                    wp_total_data = fte_wp_total(sub_packet_data)
                    if len(wp_total_data['wp_fte']) > 0:
                        final_fte[sub_project] = wp_total_data['wp_fte']
        else:
            result = fte_calculation_sub_project_sub_packet(prj_id,center_obj,work_packet_query,level_structure_key,date_list)

    count = 0
    if (len(sub_packets) == 0) :
        final_fte = {}
        if result.has_key('data'):
            final_fte= result['data']['data']
            for wp_key, wp_value in final_fte.iteritems():
                final_fte[wp_key] = [float('%.2f' % round(wp_values, 2)) for wp_values in wp_value]
    else :
        type = request.GET['type']
        if level_structure_key.get('sub_project', '') != 'All':
            final_fte = {}
            if result.has_key('data'):
                new_date_list = result['new_date_list']
                wp_subpackets = result['wp_subpackets']
                for date_va in new_date_list:
                    for wp_key_new, wp_name in wp_subpackets.iteritems():
                        local_sum = 0
                        for sub_packet in wp_name:
                            if level_structure_key.has_key('sub_project'):
                                if (level_structure_key.get('sub_project','All')!= 'All') and \
                                    (level_structure_key.get('work_packet','All')!='All') and \
                                    (level_structure_key.get('sub_packet','All')=='All'):
                                    local_sum = 0
                            new_level_structu_key = {}
                            if level_structure_key.has_key('sub_project'):
                                new_level_structu_key['sub_project']=level_structure_key['sub_project']
                            new_level_structu_key['work_packet'] = wp_key_new
                            new_level_structu_key['sub_packet'] = sub_packet
                            final_work_packet = level_hierarchy_key(level_structure_key, new_level_structu_key)
                            if type == 'day':
                                if result['data']['data'].has_key(final_work_packet):
                                    try:
                                        local_sum = local_sum + result['data']['data'][final_work_packet][count]
                                    except:
                                        local_sum = 0
                                else:
                                    local_sum = local_sum
                            if type == 'week' or type == 'month':
                                if result['data']['data'].has_key(final_work_packet):
                                    if 0.0 in result['data']['data'][final_work_packet]:
                                       values = collections.Counter(result['data']['data'][final_work_packet])
                                       count_value = values[0.0]
                                    else:
                                        count_value = 0
                                    count_num = len(result['data']['data'][final_work_packet]) - count_value
                                    try:
                                        local_sum = local_sum + sum(result['data']['data'][final_work_packet])/count_num
                                    except:
                                        local_sum = local_sum + 0
                                else:
                                    local_sum = local_sum
                            if level_structure_key.get('work_packet','') != 'All' :
                                if final_fte.has_key(final_work_packet):
                                    final_fte_sum = float('%.2f' % round(local_sum, 2))
                                    final_fte[final_work_packet].append(final_fte_sum)
                                else:
                                    final_fte_sum = float('%.2f' % round(local_sum, 2))
                                    final_fte[final_work_packet] = [final_fte_sum]
                        if level_structure_key.get('work_packet','') == 'All' :
                            new_wp_level_structu_key = {}
                            if level_structure_key.has_key('sub_project'):
                                new_wp_level_structu_key['sub_project']=level_structure_key['sub_project']
                            new_wp_level_structu_key['work_packet'] = wp_key_new
                            wp_final_work_packet = level_hierarchy_key(level_structure_key, new_wp_level_structu_key)
                            if final_fte.has_key(wp_final_work_packet):
                                final_fte_sum = float('%.2f' % round(local_sum, 2))
                                final_fte[wp_final_work_packet].append(final_fte_sum)
                            else:
                                final_fte_sum = float('%.2f' % round(local_sum, 2))
                                final_fte[wp_final_work_packet] = [final_fte_sum]
                    count =count+1
    type = request.GET['type']
    if request.GET['project'].split(' - ')[0] == 'NTT DATA Services TP':
        if type == "day":
            work_packet_fte = {}
            work_packet_fte['total_fte'] = {}
            work_packet_fte['total_fte'] = [sum(i) for i in zip(*final_fte.values())]
            work_packet_fte['total_fte'] = [round(wp_values, 2) for wp_values in work_packet_fte['total_fte']]
            fte_high_charts = {}
            fte_high_charts['total_fte'] = work_packet_fte
            fte_high_charts['work_packet_fte'] = graph_data_alignment_color(final_fte, 'data', level_structure_key, prj_id, center_obj,'')
            fte_high_charts['work_packet_fte'] = final_fte
            fte_high_charts['date'] = new_date_list
        if type == "week" or type == "month":
            work_packet_fte = {}
            packet_fte = {}
            for key,value in final_fte.iteritems():
                count = 0
                if final_fte.has_key(key):
                    if 0.0 in value:
                        count = collections.Counter(value)
                        count_value = count[0.0]
                    else:
                        count_value = 0
                count_num = len(value) - count_value
                if count_num == 0:
                    fte_sum = 0
                else:
                    fte_sum = sum(value)/count_num
                packet_fte[key] = float('%.2f' % round(fte_sum, 2))
            fte_high_charts = {}
            fte_high_charts['total_fte'] = {}
            fte_high_charts['work_packet_fte'] = {}
            packet_fte_values = float('%.2f' % round(sum(packet_fte.values()), 2))
            final_fte_values = sum(packet_fte.values())
            fte_high_charts['total_fte']['total_fte'] = [float('%.2f' % round(final_fte_values, 2))]
            fte_high_charts['work_packet_fte'] = graph_data_alignment_color(final_fte, 'data', level_structure_key, prj_id, center_obj,'')
            fte_high_charts['work_packet_fte'] = final_fte
            fte_high_charts['date'] = new_date_list
        return fte_high_charts
    else:
        work_packet_fte = {}
        work_packet_fte['total_fte'] = {}
        work_packet_fte['total_fte'] = [sum(i) for i in zip(*final_fte.values())]
        work_packet_fte['total_fte'] = [round(wp_values, 2) for wp_values in work_packet_fte['total_fte']]
        fte_high_charts = {}
        fte_high_charts['total_fte'] = work_packet_fte
        fte_high_charts['work_packet_fte'] = graph_data_alignment_color(final_fte, 'data', level_structure_key, prj_id, center_obj,'')
        fte_high_charts['work_packet_fte'] = final_fte
        fte_high_charts['date'] = new_date_list
        return fte_high_charts
