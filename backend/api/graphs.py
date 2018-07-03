
import datetime
import redis
from api.models import *
from api.commons import data_dict
from django.db.models import *
from collections import OrderedDict
from api.utils import *
from api.basics import *
from api.fte_related import *
from api.weekly_graph import *
from api.graph_settings import *
from datetime import datetime,timedelta, date
from api.voice_widgets import date_function
from common.utils import getHttpResponse as json_HttpResponse


def generate_day_type_formats_multiple(request, result_name, function_name, sub_name1, sub_name2, config_1, config_2):
    final_dict = {}
    final_dict[result_name] = {}
    new_date_list = []
    main_data_dict = data_dict(request.GET)
    prj_id = main_data_dict['pro_cen_mapping'][0][0]
    center = main_data_dict['pro_cen_mapping'][1][0]
    work_packet = main_data_dict['work_packet']
    sub_project = main_data_dict['sub_project']
    sub_packet = main_data_dict['sub_packet']
    pro_center = main_data_dict['pro_cen_mapping']
    _type = main_data_dict['type']

    level_structure_key = get_level_structure_key(work_packet, sub_project, sub_packet, pro_center)
    if main_data_dict['dwm_dict'].has_key('day') and main_data_dict['type'] == 'day':
        date_list = main_data_dict['dates']
        new_date_list = generate_dates(date_list, prj_id, center)
        if function_name == headcount_widgets:
            data = function_name(center, prj_id, date_list, level_structure_key)
            final_dict['utilization_fte_details'] =  graph_data_alignment_color(data['FTE Utilization'],'data',\
                                                     level_structure_key,prj_id,center,'fte_utilization')
            final_dict['utilization_operational_details'] = graph_data_alignment_color(data['Operational Utilization'],'data',\
                                                            level_structure_key,prj_id,center,'operational_utilization')
            final_dict['original_utilization_graph'] = graph_data_alignment_color(data['Overall Utilization'],'data',\
                                                       level_structure_key,prj_id,center,'utilisation_wrt_work_packet')        
        else:
            data = function_name(date_list, prj_id, center, level_structure_key)                                    
            if data:
                sub_result1 = data[sub_name1]
                if (data[sub_name2].has_key('Opening') and data[sub_name2].has_key('Received_week')):
                    del data[sub_name2]['Opening']
                    del data[sub_name2]['Received_week']
                sub_result2 = data[sub_name2]
                final_dict[result_name][sub_name1] = graph_data_alignment_color(sub_result1,'data',level_structure_key,prj_id,center,config_1)
                final_dict[result_name][sub_name2] = graph_data_alignment_color(sub_result2,'data',level_structure_key,prj_id,center,config_2)        
        final_dict['date'] = new_date_list
       
    elif main_data_dict['dwm_dict'].has_key('week') and main_data_dict['type'] == 'week':
        dates_list = main_data_dict['dwm_dict']['week']
        if function_name == headcount_widgets:
            week_data, week_data_1, week_data_2 = week_calculations_multi(dates_list,prj_id,center,level_structure_key,\
                                                  function_name,sub_name1,sub_name2)
            final_dict['utilization_fte_details'] = graph_data_alignment_color(week_data,'data',\
                                                    level_structure_key,prj_id,center,'fte_utilization')
            final_dict['utilization_operational_details'] = graph_data_alignment_color(week_data_1,'data',\
                                                            level_structure_key,prj_id,center,'operational_utilization')
            final_dict['original_utilization_graph'] = graph_data_alignment_color(week_data_2,'data',\
                                                       level_structure_key,prj_id,center,'utilisation_wrt_work_packet')
        else:
            week_data, week_data_1, week_data2 = week_calculations_multi(dates_list,prj_id,center,level_structure_key,\
                                                 function_name,sub_name1,sub_name2)          
            
            if week_data and week_data_1:
                final_dict[result_name][sub_name1] = graph_data_alignment_color(week_data,'data',level_structure_key,prj_id,center,config_1) 
                final_dict[result_name][sub_name2] = graph_data_alignment_color(week_data_1,'data',level_structure_key,prj_id,center,config_2)
        final_dict['date'] = date_function(dates_list, _type)
    
    else:
        dates_list = main_data_dict['dwm_dict']['month']
        if function_name == headcount_widgets:
            month_data, month_data_1, month_data_2 = month_calculations_multi(dates_list,prj_id,center,level_structure_key,\
                                                     function_name,sub_name1,sub_name2)
            final_dict['utilization_fte_details'] = graph_data_alignment_color(month_data,'data',\
                                                    level_structure_key,prj_id,center,'fte_utilization')
            final_dict['utilization_operational_details'] = graph_data_alignment_color(month_data_1,'data',\
                                                            level_structure_key,prj_id,center,'operational_utilization')
            final_dict['original_utilization_graph'] = graph_data_alignment_color(month_data_2,'data',\
                                                       level_structure_key,prj_id,center,'utilisation_wrt_work_packet')
        else:
            month_data, month_data_1, month_data2 = month_calculations_multi(dates_list,prj_id,center,level_structure_key,\
                                                    function_name,sub_name1,sub_name2)
            final_dict[result_name][sub_name1] = graph_data_alignment_color(month_data,'data',level_structure_key,prj_id,center,config_1)
            final_dict[result_name][sub_name2] = graph_data_alignment_color(month_data_1,'data',level_structure_key,prj_id,center,config_2)
        final_dict['date'] = date_function(dates_list, _type)

    final_dict['type'] = main_data_dict['type']
    final_dict['is_annotation'] = annotation_check(request)
    return json_HttpResponse(final_dict)


def fte_graphs(request):

    function_name = fte_trend_scope
    result_name = "fte_calc_data"
    sub_name1 = 'fte_scope'
    sub_name2 = 'fte_trend'
    config_name = 'sum_total_fte'
    config_name_1 = 'total_fte'
    result = generate_day_type_formats_multiple(request,result_name,function_name,sub_name1,sub_name2,config_name,config_name_1)

    return result


def week_calculations_multi(dates,project,center,level_structure_key,function_name,sub_name1,sub_name2):

    week_dict, week_dict_1, week_dict_2 = {}, {}, {}
    final_dict, final_dict_1 = {}, {}
    week_names = []
    week_num = 0
    week_or_month = 'week'
    for date in dates:
        week_name = str('week' + str(week_num))
        week_names.append(week_name)
        week_num = week_num + 1
        if function_name == headcount_widgets:
            data = function_name(center,project,date,level_structure_key)
            if data:
                week_dict[week_name] = data['FTE Utilization']
                week_dict_1[week_name] = data['Operational Utilization']
                week_dict_2[week_name] = data['Overall Utilization']
                result = prod_volume_week_util_headcount(week_names, week_dict, {})
                result_1 = prod_volume_week_util_headcount(week_names, week_dict_1, {})
                result_2 = prod_volume_week_util_headcount(week_names, week_dict_2, {})
        else:
            data = function_name(date, project, center, level_structure_key)
            if data:
                week_dict[week_name] = data[sub_name1]
                week_dict_1[week_name] = data[sub_name2]
                if function_name == fte_trend_scope:
                    result = prod_volume_week_util(project, week_names, week_dict, {}, week_or_month)
                    result_1 = prod_volume_week_util(project ,week_names ,week_dict_1, {}, week_or_month)
                    result_2 = ''
                else:
                    result = volume_status_week(week_names, week_dict, final_dict)
                    result_1 = received_volume_week(week_names, week_dict_1, final_dict_1)
                    result_2 = ''
            else:
                result, result_1, result_2 = {}, {}, {}
    return result, result_1, result_2


def month_calculations_multi(dates,project,center,level_structure_key,function_name,sub_name1,sub_name2):            
           
    month_names = []
    month_dict, month_dict_1, month_dict_2 = {}, {}, {}
    final_dict, final_dict_1 = {}, {}
    week_or_month = 'month'
    for month_na,month_va in zip(dates['month_names'],dates['month_dates']):
        month_name = month_na
        month_dates = month_va
        month_names.append(month_name)
        if function_name == headcount_widgets:
            data = function_name(center, project, month_dates, level_structure_key)
            if data:
                month_dict[month_name] = data['FTE Utilization']
                month_dict_1[month_name] = data['Operational Utilization']
                month_dict_2[month_name] = data['Overall Utilization']
                result = prod_volume_week_util_headcount(month_names, month_dict, {})
                result_1 = prod_volume_week_util_headcount(month_names, month_dict_1, {})
                result_2 = prod_volume_week_util_headcount(month_names, month_dict_2, {})
        else:
            data = function_name(month_dates, project, center, level_structure_key)
            if data:
                month_dict[month_name] = data[sub_name1]
                month_dict_1[month_name] = data[sub_name2]
                if function_name == fte_trend_scope:
                    result = prod_volume_week_util(project, month_names, month_dict, {}, week_or_month)
                    result_1 = prod_volume_week_util(project, month_names, month_dict_1, {}, week_or_month)
                    result_2 = ''
                else:
                    result = volume_status_week(month_names, month_dict, final_dict)
                    result_1 = received_volume_week(month_names, month_dict_1, final_dict_1)
                    result_2 = ''
            else:
                result, result_1, result_2 = {}, {}, {}
    return result, result_1, result_2


def alloc_and_compl(request):

    function_name = work_track_data
    result_name = 'volume_graphs'
    sub_name1 = 'bar_data'
    sub_name2 = 'line_data'
    config_name = 'volume_bar_graph'
    config_name_1 = 'volume_productivity_graph'

    result = generate_day_type_formats_multiple(request,result_name,function_name,sub_name1,sub_name2,config_name,config_name_1)
    return result


def utilisation_all(request):

    function_name = headcount_widgets
    result_name = ''
    sub_name1 = ''
    sub_name2 = ''
    config_name = ''
    config_name_1 = ''

    result = generate_day_type_formats_multiple(request,result_name,function_name,sub_name1,sub_name2,config_name,config_name_1)
    return result
    

def adding_min_max(high_chart_key,final_dict):
    result = {}
    min_max_values = error_timeline_min_max(final_dict)
    result['min_'+high_chart_key] = min_max_values['min_value']
    result['max_' + high_chart_key] = min_max_values['max_value']
    return result


def work_track_data(date_list,prj_id,center_obj,level_structure_key):
    
    _dict = OrderedDict()
    line_dict = OrderedDict()
    volume_graph_data = {}
    filter_params = get_query_parameters(level_structure_key, prj_id, center_obj, date_list)
    if filter_params:
        track_query = Worktrack.objects.filter(**filter_params)
        query_data = track_query.values_list('date').annotate(open_val=Sum('opening'), \
                     receive=Sum('received'), hold=Sum('non_workable_count'), done=Sum('completed'), \
                     balance=Sum('closing_balance'))        
        
        for value in query_data:
            if _dict.has_key('Opening'):
                _dict['Opening'].append(value[4])
                _dict['Received'].append(value[1])
                _dict['Non Workable Count'].append(value[3])
                _dict['Completed'].append(value[2])
                _dict['Closing balance'].append(value[5])
                line_dict['Received'].append(value[4]+value[1])
                line_dict['Received_week'].append(value[1])
                line_dict['Completed'].append(value[2])
                line_dict['Opening'].append(value[4])
            else:
                _dict['Opening'] = [value[4]]
                _dict['Received'] = [value[1]]
                _dict['Non Workable Count'] = [value[3]]
                _dict['Completed'] = [value[2]]
                _dict['Closing balance'] = [value[5]]
                line_dict['Received'] = [value[4]+value[1]]
                line_dict['Received_week'] = [value[1]]
                line_dict['Completed'] = [value[2]]
                line_dict['Opening'] = [value[4]]
        volume_graph_data['bar_data'] = _dict
        volume_graph_data['line_data'] = line_dict
    return volume_graph_data



def headcount_widgets(center_obj,prj_id,date_list,level_structure_key):

    final_utilization_result = {}
    final_utilization_result['FTE Utilization'] = {}
    final_utilization_result['FTE Utilization']['FTE Utilization'] = []
    final_utilization_result['Operational Utilization'] = {}
    final_utilization_result['Operational Utilization']['Operational Utilization'] = []
    final_utilization_result['Overall Utilization'] = {}
    final_utilization_result['Overall Utilization']['Overall Utilization'] = []

    filter_params = get_query_parameters(level_structure_key, prj_id, center_obj, date_list)
    if filter_params:
        query_values = Headcount.objects.filter(**filter_params).values_list('date').\
                       annotate(bill_hc=Sum('billable_hc'),bill_age=Sum('billable_agents'),\
                       buff_age=Sum('buffer_agents'),qc=Sum('qc_or_qa'),tl=Sum('teamlead'),\
                       trainees=Sum('trainees_and_trainers'),manager=Sum('managers'),mis=Sum('mis'))
        for value in query_values:
            util_numerator = value[7]
            fte_denominator = value[7] + value[8] + value[4] + value[5]
            operational_denominator = fte_denominator + value[3]
            overall_util_denominator = operational_denominator + value[1] + value[6]
            if fte_denominator > 0: 
                fte_value = (float(float(util_numerator) / float(fte_denominator))) * 100
                fte_value = float('%.2f' % round(fte_value, 2))
            else:
                fte_value = 0
            if operational_denominator > 0:
                operational_value = (float(float(util_numerator) / float(operational_denominator))) * 100
                operational_value = float('%.2f' % round(operational_value, 2))
            else:
                operational_value = 0
            if overall_util_denominator > 0:
                overall_util_value = (float(float(util_numerator) / float(overall_util_denominator))) * 100
                overall_util_value = float('%.2f' % round(overall_util_value, 2))
            else:
                overall_util_value = 0
            final_utilization_result['FTE Utilization']['FTE Utilization'].append(fte_value)
            final_utilization_result['Operational Utilization']['Operational Utilization'].append(operational_value)
            final_utilization_result['Overall Utilization']['Overall Utilization'].append(overall_util_value)

    return final_utilization_result

def timework(date_list,date_key):
    if date_key:
        from_da = datetime.strptime(date_list[0], "%Y-%m-%d")
        to_da = datetime.strptime(date_list[len(date_list)-1], "%Y-%m-%d")
    else:
        from_da = datetime.strptime(date_list[0], "%Y-%b-%d")
        to_da = datetime.strptime(date_list[len(date_list)-1], "%Y-%b-%d")

    def daterange(date1, date2):
        for n in range(int ((date2 - date1).days)+1):
            yield date1 + timedelta(n)

    date_arr = [];    
    da_arr = [];
    for t_del in daterange(from_da,to_da):
        da_arr.append(t_del);
        if (t_del.isocalendar()[2] == 7) | (t_del == to_da):
            date_arr.append(da_arr)
            da_arr = [];

    for i in reversed(date_arr):        
        if i[0].isocalendar()[2] != 7 and i[0].isocalendar()[2] != 1: 
            current_date1 =  i[0] - timedelta(days=(7-i[0].isocalendar()[2]))
            current_date2 =  i[0] + timedelta(days=(7-i[0].isocalendar()[2]))
        else:
            current_date1 =  i[0]
            current_date2 =  i[0] + timedelta(days=(6))        

        da_arr1 = [];
        for t_del in daterange(current_date1,current_date2):
            da_arr1.append(t_del.strftime("%Y-%m-%d"));

        pre_date1 =  current_date1 - timedelta(days=7)
        pre_date2 =  current_date1 - timedelta(days=1)

        da_arr2 = [];
        for t_del in daterange(pre_date1,pre_date2):
            da_arr2.append(t_del.strftime("%Y-%m-%d"));

        return {"current":da_arr1,"previous":da_arr2};

def performance_summary(request):
    main_data_dict = data_dict(request.GET)
    prj_id = main_data_dict['pro_cen_mapping'][0][0]
    center = main_data_dict['pro_cen_mapping'][1][0]
    work_packet = main_data_dict['work_packet']
    sub_project = main_data_dict['sub_project']
    sub_packet = main_data_dict['sub_packet']
    pro_center = main_data_dict['pro_cen_mapping']
    _type = main_data_dict['type']    

    if request.GET.get('key_from_date','undefined') != 'undefined' and request.GET.get('key_to_date','undefined') != 'undefined' :
        date_list = [request.GET['key_from_date'],request.GET['key_to_date']]
        date_obj = timework(date_list,0)
    else:
        date_list = main_data_dict['dates']
        date_obj = timework(date_list,1)    

    level_structure_key = get_level_structure_key(work_packet, sub_project, sub_packet, pro_center)
    
    current_date =  date_obj['current']
    previous_date =  date_obj['previous']

    filter_params_current,_termCur = getting_required_params(level_structure_key, prj_id, center, current_date)
    filter_params_previous,_termPre = getting_required_params(level_structure_key, prj_id, center, previous_date)
    
    data_production =RawTable.objects.filter(**filter_params_current).values("date").annotate(cCount=Sum("per_day")).distinct()
    data_audit =Externalerrors.objects.filter(**filter_params_current).values("date").annotate(aCount=Sum("audited_errors"),eCount=Sum("total_errors")).distinct()

    data_accuracy = {};
    for index,data in enumerate(data_audit):
        if data["aCount"] != 0:
            data_accuracy.update({str(data["date"].strftime("%Y-%b-%d")):float('%.2f' % round((float(data["aCount"]-data["eCount"])/data["aCount"])*100,2))})
        else:
            data_accuracy.update({str(data["date"].strftime("%Y-%b-%d")):0})
            
    
    data_AHT =AHTTeam.objects.filter(**filter_params_current).values("date").annotate(avg=Avg("AHT")).distinct()
    data_AHT_login =AHTIndividual.objects.filter(**filter_params_current).values("date").annotate(count=Count("emp_name")).distinct()
    
    pre_main_result = {}
    
    production_obj = {};
    for prod in data_production:
        production_obj[str(prod['date'].strftime("%Y-%b-%d"))] = prod['cCount']
    
    audit_obj = {};
    error_obj = {};
    for audit in data_audit:
        audit_obj[str(audit['date'].strftime("%Y-%b-%d"))] = audit['aCount']
        error_obj[str(audit['date'].strftime("%Y-%b-%d"))] = audit['eCount']

    aht_avg_obj = {};
    aht_count_obj = {};
    for aht in data_AHT:
        aht_avg_obj[str(aht['date'].strftime("%Y-%b-%d"))] = float('%.2f' % round(aht['avg'],2))
    
    for aht_login in data_AHT_login:
        aht_count_obj[str(aht_login['date'].strftime("%Y-%b-%d"))] = aht_login['count']    
    
    
    pre_data_production =RawTable.objects.filter(**filter_params_previous).aggregate(Pre_Production_Count=Sum("per_day"))
    pre_data_audit =Externalerrors.objects.filter(**filter_params_previous).aggregate(Pre_Audit_Count=Sum("audited_errors"),Pre_Error_Count=Sum("total_errors"))
    pre_data_AHT =AHTTeam.objects.filter(**filter_params_previous).aggregate(Pre_Aht_Avg=Avg("AHT"))
    pre_data_AHT_login = AHTIndividual.objects.filter(**filter_params_previous).values("date").annotate(Pre_count=Count("emp_name")).aggregate(Pre_login_count=Avg("Pre_count"))
    

    if (pre_data_audit["Pre_Audit_Count"]) is not None and (pre_data_audit["Pre_Error_Count"] is not None):
        pre_data_accuracy = str('%.2f' % round((float(pre_data_audit["Pre_Audit_Count"]-pre_data_audit["Pre_Error_Count"])/pre_data_audit["Pre_Audit_Count"])*100,2))+'%'
    else:
        pre_data_accuracy = "NA"
    

    if pre_data_production['Pre_Production_Count'] == None:
        pre_data_production['Pre_Production_Count'] = " NA "

    pre_main_result.update(pre_data_production)

    if pre_data_audit["Pre_Audit_Count"] is not None:
        pre_main_result.update(pre_data_audit)
    else:
        pre_main_result.update({"Pre_Audit_Count":"NA"})
    
    if pre_data_audit["Pre_Error_Count"] is not None:
        pre_main_result.update({"Pre_Error_Count":pre_data_audit["Pre_Error_Count"]})
    else:
        pre_main_result.update({"Pre_Error_Count":"NA"})

    if pre_data_AHT_login["Pre_login_count"] > -1:
        pre_data_AHT_login["Pre_login_count"] = float('%.2f' % round(float(pre_data_AHT_login["Pre_login_count"]),0))
        pre_main_result.update(pre_data_AHT_login)
    else:
        pre_main_result.update({"Pre_login_count":"NA"})

    if pre_data_AHT["Pre_Aht_Avg"] is not None:
        pre_main_result.update({"Pre_Aht_Avg":float('%.2f' % round(pre_data_AHT["Pre_Aht_Avg"],2))})
    else:
        pre_main_result.update({"Pre_Aht_Avg":"NA"})

    pre_main_result.update({"Pre_Accuracy":pre_data_accuracy})

    for index,cdate in enumerate(current_date):
        current_date[index] = datetime.strptime(cdate,'%Y-%m-%d').strftime("%Y-%b-%d")
    
    for index,pdate in enumerate(previous_date):
        previous_date[index] = datetime.strptime(pdate,'%Y-%m-%d').strftime("%Y-%b-%d")
    
    main_result = {"accuracy":data_accuracy,"production":production_obj,"audit_count":audit_obj,"audit_errors":error_obj,"AHT_avg":aht_avg_obj,"AHT_count":aht_count_obj,"pre_main_result":pre_main_result,"current_date":current_date,"previous_date":previous_date,"pre_api_date":[previous_date[0],previous_date[len(previous_date)-1]]}

    return json_HttpResponse(main_result)