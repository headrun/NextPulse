from __future__ import division
import datetime, collections
from api.models import *
from api.basics import *
from django.db.models import *
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
        result = aht_team_target_data(date_list,project,center,_term,raw_dates,packets,main_dates,request,filter_params)

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
    

def aht_team_target_data(date_list,project,center,_term,dates,packets,main_dates,request,filter_params):

    result = {}
    target_line = []
    if _term == 'sub_project':
        packet = request.GET.get('sub_project', '')
        main_packets = AHTTeam.objects.filter(project=project,date__range=[main_dates[0], main_dates[-1]],\
                        sub_project=packet).values_list(_term,flat=True).distinct()
    elif _term == 'work_packet':
        packet = request.GET.get('work_packet', '')
        if packet != '' and packet != 'All':
            main_packets = AHTTeam.objects.filter(project=project,date__range=[main_dates[0], main_dates[-1]],work_packet=packet).\
                values_list(_term,flat=True).distinct()
        else:
            main_packets = AHTTeam.objects.filter(project=project,date__range=[main_dates[0], main_dates[-1]]).\
                values_list(_term,flat=True).distinct()
    elif _term == 'sub_packet':
        packet = request.GET.get('sub_packet', '')
        main_packets = AHTTeam.objects.filter(project=project,date__range=[main_dates[0], main_dates[-1]],sub_packet=packet).\
                values_list(_term,flat=True).distinct()
    
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
        if '' not in packets:
            raw_dates = RawTable.objects.filter(project=project, center=center, date__range=[date_list[0],date_list[-1]]).\
                        values_list('date', flat=True).distinct()

            for date in raw_dates:
                packets_list = []
                for data in query_values:
                    if str(date) == str(data[0]):
                        if data[2]:
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
    
def Daywise_Num_of_agents_aht(date_list, prj_id, center, level_structure_key, main_dates, request):
    data_result  = {}
    aht_lt_output = []
    aht_gt_output = []
    target_val = {}  
    
    date_pack = RawTable.objects.filter(project=prj_id,center=center,date__range=[date_list[0],date_list[-1]])\
                                .values_list('date',flat=True).distinct()
    aht_query = AHTIndividual.objects.filter(project=prj_id,center=center,date__range=[date_list[0],date_list[-1]])
    target_aht = Targets.objects.filter(project=prj_id, center=center,target_type="AHT" , sub_project="ID Verification")\
                                .filter(Q(from_date__lte=date_list[0])|Q(from_date__range=[date_list[0],date_list[-1]]))\
                                .filter(Q(to_date__gte=date_list[-1])|Q(to_date__range=[date_list[0],date_list[-1]]))\
                                .values("sub_project").annotate(target=Avg('target_value'))    
    
    if target_aht and aht_query:        
        for aht in target_aht:
            if aht['sub_project'] == 'ID Verification':
                aht_gt_output = aht_query.filter(sub_project='ID Verification', AHT__gt=aht['target'])\
                                            .values("date","sub_project").annotate(agent_c=Count("emp_name"))
                aht_lt_output = aht_query.filter(sub_project='ID Verification', AHT__lt=aht['target'])\
                                            .values("date","sub_project").annotate(agent_c=Count("emp_name"))
                target_val[aht["sub_project"].lower().title()] = int(round(aht["target"]))        
        
        if aht_gt_output or aht_lt_output:
            for date in date_pack:
                content_list = []
                for aht in aht_gt_output:
                    aht["sub_project"] = aht["sub_project"].lower().title()                                            
                    if str(date) == str(aht['date']):                        
                        if not data_result.has_key("Greater than "+str(target_val[aht["sub_project"]])+" sec"):
                            data_result["Greater than "+str(target_val[aht["sub_project"]])+" sec"] = []
                        data_result["Greater than "+str(target_val[aht["sub_project"]])+" sec"].append(aht["agent_c"])
                        content_list.append(aht["agent_c"])

                if not len(content_list) > 0:
                    aht["sub_project"] = aht["sub_project"].lower().title()                        
                    if not data_result.has_key("Greater than "+str(target_val[aht["sub_project"]])+" sec"):
                        data_result["Greater than "+str(target_val[aht["sub_project"]])+" sec"] = []
                    data_result["Greater than "+str(target_val[aht["sub_project"]])+" sec"].append(0)

            for date in date_pack:
                content_list = []
                for aht in aht_lt_output:
                    aht["sub_project"] = aht["sub_project"].lower().title()                        
                    if str(date) == str(aht["date"]):
                        if not data_result.has_key("Lesser than "+str(target_val[aht["sub_project"]])+" sec"):
                            data_result["Lesser than "+str(target_val[aht["sub_project"]])+" sec"] = []
                        data_result["Lesser than "+str(target_val[aht["sub_project"]])+" sec"].append(aht["agent_c"])
                        content_list.append(aht["agent_c"])

                if not len(content_list) > 0:
                    aht["sub_project"] = aht["sub_project"].lower().title()                        
                    if not data_result.has_key("Lesser than "+str(target_val[aht["sub_project"]])+" sec"):
                        data_result["Lesser than "+str(target_val[aht["sub_project"]])+" sec"] = []
                    data_result["Lesser than "+str(target_val[aht["sub_project"]])+" sec"].append(0)

    return data_result


def Percentage_of_agents_aht(date_list, prj_id, center, level_structure_key, main_dates, request):
    data_result, data_dict  = {}, {}
    ext_output =  []
    data_list = []
    sample_out = {}
    filter_params, _term = getting_required_params(level_structure_key, prj_id, center, date_list)    
    aht_query = AHTIndividual.objects.filter(**filter_params)
    target_aht = Targets.objects.filter(project=prj_id , center=center ,target_type="AHT" ,sub_project__icontains="ID Verification")\
                                .filter(Q(from_date__lte=date_list[0])|Q(from_date__range=[date_list[0],date_list[-1]]))\
                                .filter(Q(to_date__gte=date_list[-1])|Q(to_date__range=[date_list[0],date_list[-1]]))                    
    
    
    if target_aht and aht_query:
        target_aht = target_aht.aggregate(target=Sum('target_value'))
        accuracy_obj = Externalerrors.objects.filter(**filter_params).values_list("date","employee_id",_term)\
                                        .annotate(error_c=Sum("total_errors"),audited_c=Sum("audited_errors"))       
        
        j = 0
        for in_acc in accuracy_obj:
            if in_acc[3] > 0:
                accuracy = 100 - ((float(in_acc[4]/in_acc[3]))*100)
            else:
                accuracy = 0
            if accuracy > 99.00:                
                ext_output.append({})
                ext_output[j]["date"] = str(in_acc[0])
                ext_output[j]["emp_name"] = str(in_acc[1])
                ext_output[j][_term] = str(in_acc[2])
                ext_output[j]["accuracy"] = accuracy
                j += 1        
        
        AHT_obj = aht_query.filter(AHT__lt=target_aht['target']).values("date","emp_name",_term)        
        logins = aht_query.values("date",_term).annotate(No_of_logins=Count('emp_name'))
        
        for acc in ext_output:
            for aht in AHT_obj:
                if (str(acc['date']) == str(aht['date']) and acc['emp_name'] == aht['emp_name'] and acc[_term] == aht[_term]):                    
                    if not data_dict.has_key(str(acc['date'])+"__"+acc[_term]):                        
                        data_dict[str(acc['date'])+"__"+acc[_term]]= 1
                    else:                        
                        data_dict[str(acc['date'])+"__"+acc[_term]] = data_dict[str(acc['date'])+"__"+acc[_term]] + 1         
        
        i = 0
        for k, v in data_dict.iteritems():
            data_list.append({})
            key = k.split("__")
            data_list[i]['date'] = key[0]
            data_list[i][_term] = key[1]
            data_list[i]['Met_count'] = v
            i += 1        
        
        data_list = sorted(data_list, key=lambda k: k['date'])        
        logins = sorted(logins, key=lambda k: k['date'])
        
        if data_list and logins:
            data_result['Percentage Of People <67 and >99%'] = []
            for data in data_list:
                for log in logins:
                    if (str(data['date']) == str(log['date']) and data[_term] == log[_term]):
                        no_of_log = float(data["Met_count"]/log["No_of_logins"])*100
                        no_of_log = float("%.2f"%round(no_of_log,2))
                        if not sample_out.has_key(str(data['date'])):
                            sample_out[str(data['date'])] = [no_of_log]
                        else:
                            sample_out[str(data['date'])].append(no_of_log)

            sample_out = collections.OrderedDict(sorted(sample_out.items()))
            for key, value in sample_out.iteritems():
                per_val = float(sum(value)/len(value))
                per_value = float("%.2f"%round(per_val,2))
                data_result['Percentage Of People <67 and >99%'].append(per_value)
    
    return data_result
