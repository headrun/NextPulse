import datetime
from api.models import *
from api.basics import *
from django.db.models import Max, Sum, Count
from api.query_generations import *
from collections import OrderedDict
from api.commons import data_dict
from api.graph_settings import graph_data_alignment_color
from common.utils import getHttpResponse as json_HttpResponse


def aht_team_calculations(date_list, project, center, level_structure_key, main_dates, request):
    
    result = {}
    
    filter_params, _term = getting_required_params(level_structure_key, project, center, date_list)
    if _term  and filter_params:
        query_data = AHTTeam.objects.filter(**filter_params)
        aht_values = query_data.values_list('date',_term,'AHT')
        packets = query_data.values_list(_term,flat=True).distinct() 
        raw_dates = RawTable.objects.filter(project=project, center=center, date__range=[date_list[0],date_list[-1]]).\
                    values_list('date', flat=True).distinct()
        result = aht_team_target_data(date_list,project,center,_term,raw_dates,packets,main_dates,request)

        for date in raw_dates:
            packets_list = []
            for data in aht_values:
                if str(date) == str(data[0]):
                    if result.has_key(data[1]):
                        result[data[1]].append(round(data[2], 2))
                    else:
                        result[data[1]] = [round(data[2], 2)]
                    packets_list.append(data[1])
            
            for packet in packets:
                if packet not in packets_list:
                    if result.has_key(packet):
                        result[packet].append(0)
                    else:
                        result[packet] = [0]

    return result
    

def aht_team_target_data(date_list,project,center,_term,dates,packets,main_dates,request):

    result = {}
    target_line = []
    #import pdb;pdb.set_trace()
    if _term == 'work_packet':
        packet = request.GET.get('work_packet', '')
        if packet:
            main_packets = AHTTeam.objects.filter(project=project,date__range=[main_dates[0], main_dates[-1]],work_packet=packet).\
                values_list(_term,flat=True).distinct()
        else:
            main_packets = AHTTeam.objects.filter(project=project,date__range=[main_dates[0], main_dates[-1]]).\
                values_list(_term,flat=True).distinct()
    elif _term == 'sub_packet':
        packet = request.GET.get('sub_packet')
        main_packets = AHTTeam.objects.filter(project=project,date__range=[main_dates[0], main_dates[-1]],sub_packet=packet).\
                values_list(_term,flat=True).distinct()
    #import pdb;pdb.set_trace()
    if len(main_packets) == 1:
        target_query = Targets.objects.filter(project=project,center=center,from_date__lte=date_list[0],\
                       to_date__gte=date_list[-1],target_type='AHT').\
                        values_list('from_date','to_date','target_value',_term)
        if target_query:
            target_query = target_query
        else:
            target_query = Targets.objects.filter(project=project,center=center,from_date__gte=date_list[0],\
                       to_date__lte=date_list[-1],target_type='AHT').\
                        values_list('from_date','to_date','target_value',_term)
        for date in dates:
            for target in target_query:
                if (target[3] in packets) and (str(target[0]) <= str(date)) and (str(target[1]) >= str(date)):
                    target_line.append(target[2])
        result['target_line'] = target_line
    return result


def tat_graph(date_list, project, center, level_structure_key, main_dates, request):

    result = {}
    
    filter_params, _term = getting_required_params(level_structure_key, project, center, date_list)
    if _term and filter_params:
        query_data = TatTable.objects.filter(**filter_params)
        query_values = query_data.values_list('date',_term,'met_count','non_met_count')
        packets = query_data.values_list(_term,flat=True).distinct()
        raw_dates = RawTable.objects.filter(project=project, center=center, date__range=[date_list[0],date_list[-1]]).\
                    values_list('date', flat=True).distinct()

        for date in raw_dates:
            packets_list = []
            for data in query_values:
                if str(date) == str(data[0]):
                    value = (float(data[2])/float(data[3]+data[2]))*100
                    if result.has_key(data[1]):
                        result[data[1]].append(round(value, 2)) 
                    else:
                        result[data[1]] = [round(value, 2)] 
                    packets_list.append(data[1])
        
            for packet in packets:
                if packet not in packets_list:
                    if result.has_key(packet):
                        result[packet].append(0)
                    else:
                        result[packet] = [0] 
    return result
    


