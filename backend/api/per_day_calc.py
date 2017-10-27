
import datetime
import redis
from api.models import *
from api.basics import *
from api.utils import *
from api.commons import *
from django.db.models import Max, Sum
from collections import OrderedDict
from api.query_generations import query_set_generation
from api.graph_settings import graph_data_alignment_color
from common.utils import getHttpResponse as json_HttpResponse

def prod_avg_perday(request):
    final_dict = {}
    data_date, new_date_list = [], []
    week_names = []
    week_num = 0
    prod_avg_dt = {}
    month_names = []
    main_data_dict = data_dict(request.GET)
    if main_data_dict['dwm_dict'].has_key('day') and main_data_dict['type'] == 'day':
        main_dates_list = [ main_data_dict['dwm_dict']['day']]
    elif main_data_dict['dwm_dict'].has_key('week') and main_data_dict['type'] == 'week':
        main_dates_list = main_data_dict['dwm_dict']['week']
    elif main_data_dict['dwm_dict'].has_key('month') and main_data_dict['type'] == 'month':
        main_dates_list = main_data_dict['dwm_dict']['month']['month_dates']
    prj_id = main_data_dict['pro_cen_mapping'][0][0]
    center = main_data_dict['pro_cen_mapping'][1][0]
    if main_data_dict['dwm_dict'].has_key('day') and main_data_dict['type'] == 'day':
        for sing_list in main_dates_list:
            total_done_value = RawTable.objects.filter(project=prj_id, center=center, date__range=[sing_list[0], sing_list[-1]]).values('date').annotate(total=Sum('per_day'))
            values = OrderedDict(zip(map(lambda p: str(p['date']), total_done_value), map(lambda p: str(p['total']), total_done_value)))
            for date_va, total_val in values.iteritems():
            #for date_va in sing_list:
                #total_done_value = RawTable.objects.filter(project=prj_id,center=center,date=date_va).aggregate(Max('per_day'))
                #if total_done_value['per_day__max'] > 0:
                if total_val > 0:
                    new_date_list.append(date_va)
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            production_avg_details = production_avg_perday(sing_list, main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0], level_structure_key)
            final_dict['production_avg_details'] = graph_data_alignment_color(production_avg_details,'data', level_structure_key,main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0])
            final_dict['date'] = new_date_list
    elif main_data_dict['dwm_dict'].has_key('week') and main_data_dict['type'] == 'week':
        for sing_list in main_dates_list:
            data_date.append(sing_list[0] + ' to ' + sing_list[-1])
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            production_avg_details = production_avg_perday(sing_list, main_data_dict['pro_cen_mapping'][0][0],main_data_dict['pro_cen_mapping'][1][0], level_structure_key)
            prod_avg_dt[week_name] = production_avg_details
        final_prod_avg_details = prod_volume_week_util(prj_id,week_names, prod_avg_dt, {},'week')
        final_dict['production_avg_details'] = graph_data_alignment_color(final_prod_avg_details, 'data',level_structure_key, prj_id, center)
        final_dict['date'] = data_date
    else:
        for month_na,month_va in zip(main_data_dict['dwm_dict']['month']['month_names'],main_data_dict['dwm_dict']['month']['month_dates']):
            month_name = month_na
            month_dates = month_va
            data_date.append(month_dates[0] + ' to ' + month_dates[-1])
            month_names.append(month_name)
            level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'],main_data_dict['pro_cen_mapping'])
            production_avg_details = production_avg_perday(month_dates,prj_id,center,level_structure_key)
            prod_avg_dt[month_name] = production_avg_details
        final_prod_avg_details = prod_volume_week_util(prj_id,month_names, prod_avg_dt, {},'month')
        final_dict['production_avg_details'] = graph_data_alignment_color(final_prod_avg_details,'data',level_structure_key, prj_id, center)
        final_dict['date'] = data_date
    final_dict['type'] = main_data_dict['type']    
    return json_HttpResponse(final_dict)

def production_avg_perday(date_list,prj_id,center_obj,level_structure_key):
    conn = redis.Redis(host="localhost", port=6379, db=0)
    result, volumes_dict, date_values = {}, {}, {}
    #prj_name = Project.objects.filter(id=prj_id).values_list('name', flat=True)
    #center_name = Center.objects.filter(id=center_obj).values_list('name', flat=True)
    project = Project.objects.filter(id=prj_id)
    prj_name = project[0].name
    center_name = project[0].center.name
    query_set = query_set_generation(prj_id, center_obj, level_structure_key, date_list)
    new_date_list = []
    total_done_value = RawTable.objects.filter(project=prj_id, center=center_obj, date__range=[date_list[0], date_list[-1]]).values('date').annotate(total=Sum('per_day'))
    values = OrderedDict(zip(map(lambda p: str(p['date']), total_done_value), map(lambda p: str(p['total']), total_done_value)))
    for date_key, total_val in values.iteritems():
    #for date_va in date_list:
        #total_done_value = RawTable.objects.filter(project=prj_id, center=center_obj, date=date_va).aggregate(Max('per_day'))
        #if total_done_value['per_day__max'] > 0:
        if total_val > 0:
            #new_date_list.append(date_va)
            new_date_list.append(date_key)
            if level_structure_key.has_key('sub_project'):
                if level_structure_key['sub_project'] == "All":
                    volume_list = RawTable.objects.filter(**query_set).values('sub_project').distinct()
                else:
                    if level_structure_key.has_key('work_packet'):
                        if level_structure_key['work_packet'] == "All":
                            volume_list = RawTable.objects.filter(**query_set).values('sub_project','work_packet').distinct()
                        else:
                            volume_list = RawTable.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()
            elif level_structure_key.has_key('work_packet') and len(level_structure_key) == 1:
                if level_structure_key['work_packet'] == "All":
                    volume_list = RawTable.objects.filter(**query_set).values('sub_project', 'work_packet').distinct()
                else:
                    volume_list = RawTable.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()
            elif level_structure_key.has_key('work_packet') and level_structure_key.has_key('sub_packet'):
                volume_list = RawTable.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()
            else:
                volume_list = [] 
            count = 0
            for vol_type in volume_list:
                final_work_packet = level_hierarchy_key(level_structure_key, vol_type)
                if not final_work_packet:
                    final_work_packet = level_hierarchy_key(volume_list[count], vol_type)
                count = count + 1
                #date_pattern = '{0}_{1}_{2}_{3}'.format(prj_name[0], str(center_name[0]), str(final_work_packet),date_va)
                date_pattern = '{0}_{1}_{2}_{3}'.format(prj_name, center_name, str(final_work_packet), date_key)
                key_list = conn.keys(pattern=date_pattern)
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
                            date_values[key].append(int(value))
                        else:
                            date_values[key] = [int(value)]
    return date_values
