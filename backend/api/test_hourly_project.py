from common.utils import getHttpResponse as json_HttpResponse
from api.models import *
import datetime
import re
import pytz
from datetime import timedelta
import datetime as dt
from django.db.models import Max
from django.db.models.functions import *
from django.db.models import *
from api.commons import data_dict
from api.graph_settings import graph_data_alignment_color
from api.Error_priority import min_max_num
from api.voice_widgets import date_function
from django.utils import timezone
from api.basics import annotation_check


def getting_required_params(level_structure_key, prj_id, center_obj, date_list):
    
    query_dict = {}
    packet_1 = level_structure_key.get('sub_project', '')
    packet_2 = level_structure_key.get('work_packet', '')
    packet_3  = level_structure_key.get('sub_packet', '')
    field = ''

    if (packet_1 != '' and packet_2 != '' and packet_3 != '') or (packet_1 != ''):
        if (packet_1 == 'All' and packet_2 == 'All' and packet_3 == 'All') or (packet_1 == 'All'):
            query_dict.update({'project': prj_id, 'center': center_obj, 'date__range': [date_list[0], date_list[-1]]})
            field = 'sub_project'
        elif packet_1 != 'All' and packet_2 == 'All' and packet_3 == 'All':
            query_dict.update({'project': prj_id, 'center': center_obj, 'date__range': [date_list[0], date_list[-1]],\
            'sub_project': packet_1})
            field = 'work_packet'
        elif packet_1 != 'All' and packet_2 != 'All' and packet_3 == 'All':
            query_dict.update({'project': prj_id, 'center': center_obj, 'date__range': [date_list[0], date_list[-1]],\
            'sub_project': packet_1,'work_packet': packet_2})
            field = 'sub_packet'
        elif packet_1 != 'All' and packet_2 != 'All' and packet_3 != 'All':
            query_dict.update({'project': prj_id, 'center': center_obj, 'date__range': [date_list[0], date_list[-1]],\
            'sub_project': packet_1,'work_packet': packet_2, 'sub_packet': packet_3})
            field = 'sub_packet'
        
    elif packet_1 == '' and packet_2 != '' and packet_3 != '':
        if packet_2 == 'All' and packet_3 == 'All':
            query_dict.update({'project': prj_id, 'center': center_obj, 'date__range': [date_list[0], date_list[-1]]})
            field = 'work_packet'
        elif packet_2 != 'All' and packet_3 == 'All':
            query_dict.update({'project': prj_id, 'center': center_obj, 'date__range': [date_list[0], date_list[-1]],\
            'work_packet': packet_2})
            field = 'sub_packet'
        elif packet_2 != 'All' and packet_3 != 'All':
            query_dict.update({'project': prj_id, 'center': center_obj, 'date__range': [date_list[0], date_list[-1]],\
            'work_packet': packet_2,'sub_packet': packet_3})
            field = 'sub_packet'

    elif packet_1 == '' and packet_2 != '' and packet_3 == '':
        if packet_2 == 'All':
            query_dict.update({'project': prj_id, 'center': center_obj, 'date__range': [date_list[0], date_list[-1]]})
            field = 'work_packet'
        elif packet_2 != 'All':
            query_dict.update({'project': prj_id, 'center': center_obj, 'date__range': [date_list[0], date_list[-1]],\
            'work_packet': packet_2})
            field = 'work_packet'
    return query_dict, field


def get_level_structure_key(work_packet, sub_project, sub_packet, pro_cen_mapping):
    """It will generate level structure key with existing packet, project, and sub packey types"""

    level_structure_key ={}
    if (work_packet) and (work_packet !='undefined'): level_structure_key['work_packet']= work_packet
    if (sub_project) and (sub_project !='undefined'): level_structure_key['sub_project'] = sub_project
    if (sub_packet) and (sub_packet !='undefined'): level_structure_key['sub_packet'] = sub_packet
    count = 0
    all_count = [count + 1 for key in level_structure_key.values() if key == "All"]
    if len(all_count) >= 2:
        if len(level_structure_key) !=3:
            level_structure_key = {}
        if len(all_count) == 3:
            level_structure_key = {}
    if not level_structure_key:
        sub_pro_level = filter(None,live_transaction_table.objects.filter(project=pro_cen_mapping[0][0], center=pro_cen_mapping[1][0])\
                        .values_list('sub_project',flat=True).distinct())
        if len(sub_pro_level)>= 1:
            level_structure_key['sub_project'] = "All"
        if not level_structure_key:
            work_pac_level = filter(None,live_transaction_table.objects.filter(project=pro_cen_mapping[0][0], center=pro_cen_mapping[1][0])\
                                .values_list('work_packet',flat=True).distinct())
            if len(work_pac_level)>=1:
                level_structure_key['work_packet'] = "All"
        if not level_structure_key:
            sub_pac_level = filter(None,live_transaction_table.objects.filter(project=pro_cen_mapping[0][0], center=pro_cen_mapping[1][0])\
                            .values_list('sub_packet',flat=True).distinct())
            if len(sub_pac_level)>=1:
                level_structure_key['sub_packet'] = "All"
   
    return level_structure_key

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


def week_calculations(dates, project, center, level_structure_key, function_name, main_dates,request):
    
    week_dict = {}
    week_names = []
    week_num = 0
    for date in dates:
        week_name = str('week' + str(week_num))
        week_names.append(week_name)
        week_num = week_num + 1
        data = function_name(date, project, center, level_structure_key,main_dates,request, 'week')
        week_dict[week_name] = data
    if function_name in []:
        result = prod_volume_week_util(project, week_names, week_dict, {}, 'week')
    elif function_name in [hourly_production, hourly_error, Accuracy_Hourly]:
        result = prod_volume_week_util_headcount(week_names, week_dict, {})    
    else:
       result = prod_volume_week(week_names, week_dict, {}) 
    return result  


def month_calculations(dates, project, center, level_structure_key, function_name, main_dates,request):

    month_names = []
    month_dict = {}
    for month_na,month_va in zip(dates['month_names'],dates['month_dates']):
        month_name = month_na
        month_dates = month_va
        month_names.append(month_name)
        data = function_name(month_dates, project, center, level_structure_key, main_dates, request, 'month')
        month_dict[month_name] = data
    if function_name in []:
        result = prod_volume_week_util(project, month_names, month_dict, {}, 'month')
    elif function_name in [hourly_production, hourly_error, Accuracy_Hourly]:
        result = prod_volume_week_util_headcount(month_names, month_dict, {})    
    else:
        result = prod_volume_week(month_names, month_dict, {})
    return result

def num_of_days(to_date,from_date):
    date_list=[]
    no_of_days = to_date - from_date
    no_of_days = int(re.findall('\d+', str(no_of_days))[0])
    for i in xrange(0, no_of_days + 1):
        date_list.append(str(from_date + timedelta(days=i)))
    return date_list


def generate_day_week_month_format(request, function_name, result_name):
    final_dict = {}
    main_data_dict = data_dict(request.GET)
   
    main_dates = main_data_dict['dates']
    prj_id = main_data_dict['pro_cen_mapping'][0][0]
    center = main_data_dict['pro_cen_mapping'][1][0]
    work_packet = main_data_dict['work_packet']
    sub_project = main_data_dict['sub_project']
    sub_packet = main_data_dict['sub_packet']
    pro_center = main_data_dict['pro_cen_mapping']
    _type = main_data_dict['type']

    level_structure_key = get_level_structure_key(work_packet, sub_project, sub_packet, pro_center)
   
    if main_data_dict['dwm_dict'].has_key('hour') and main_data_dict['type'] == 'hour' and len(main_dates)==1:
        dates_list = main_data_dict['dwm_dict']['hour']
        data = function_name(main_dates, prj_id, center, level_structure_key, dates_list, request, _type)
        final_dict[result_name] = graph_data_alignment_color(data['value'], 'data', level_structure_key, \
                                        prj_id, center, result_name)        
        final_dict['date'] = data['hour']
        

    elif main_data_dict['dwm_dict'].has_key('hour') and main_data_dict['type'] == 'hour' and len(main_dates)!=1:
        dates_list = main_data_dict['dwm_dict']['hour']
        data = function_name(main_dates, prj_id, center, level_structure_key, dates_list, request, _type)
        final_dict[result_name] = graph_data_alignment_color(data['value'], 'data', level_structure_key, \
                                        prj_id, center, result_name)        
        final_dict['date'] = data['hour']
        final_dict['dates'] = [main_dates[0],main_dates[0]]

    elif main_data_dict['dwm_dict'].has_key('day') and main_data_dict['type'] == 'day' and len(main_dates)!=1:
        dates_list = main_data_dict['dwm_dict']['day']
        data = function_name(main_dates, prj_id, center, level_structure_key, dates_list, request, _type)
        final_dict[result_name] = graph_data_alignment_color(data, 'data', level_structure_key, prj_id, center)
        final_dict['date'] = dates_list
        final_dict['min_max'] = min_max_num(data, result_name)

    elif main_data_dict['dwm_dict'].has_key('week') and main_data_dict['type'] == 'week' and len(main_dates)!=1:
        dates_list = main_data_dict['dwm_dict']['week']        
        week_data = week_calculations(dates_list, prj_id, center, level_structure_key, function_name, main_dates,request)        
        final_dict[result_name] = graph_data_alignment_color(week_data, 'data', level_structure_key, prj_id, center)
        final_dict['min_max'] = min_max_num(week_data,result_name)
        final_dict['date'] = date_function(dates_list, _type)
    
    elif main_data_dict['dwm_dict'].has_key('month') and main_data_dict['type'] == 'month' and len(main_dates)!=1:
        dates_list = main_data_dict['dwm_dict']['month']        
        week_data = month_calculations(dates_list, prj_id, center, level_structure_key, function_name, main_dates,request)        
        final_dict[result_name] = graph_data_alignment_color(week_data, 'data', level_structure_key, prj_id, center)
        final_dict['min_max'] = min_max_num(week_data,result_name)
        final_dict['date'] = date_function(dates_list, _type)
        
    final_dict['type'] = main_data_dict['type']
    
    
   
    return json_HttpResponse(final_dict)



def Test_project_hourly(request):

    result_name = "hourly_prod"
    function_name = hourly_production
    result = generate_day_week_month_format(request, function_name, result_name)

    return result

def Test_hourly_login(request):
    
    result,final_dict = {}, {}    
    result_dict, dct = {}, {}   
    dates_list = []    
    result_dict['hour'] = []
    result_name = "hourly_login"   
    main_data_dict = data_dict(request.GET)
    main_dates = main_data_dict['dates']
    prj_id = main_data_dict['pro_cen_mapping'][0][0]
    center = main_data_dict['pro_cen_mapping'][1][0]
    work_packet = main_data_dict['work_packet']
    sub_project = main_data_dict['sub_project']
    sub_packet = main_data_dict['sub_packet']
    pro_center = main_data_dict['pro_cen_mapping']
    level_structure_key = get_level_structure_key(work_packet, sub_project, sub_packet, pro_center)    
    data_exist = live_agent_login_table.objects.filter(date__in=main_dates)
   
    if len(data_exist) > 0:
        data = [(i, datetime.time(i).strftime('%I %p')) for i in range(24)]
        for i in data:
            dates_list.append(i[0])
        if len(main_dates) == 1:
            hourly_dct = {}
            if main_dates[0] == str(datetime.datetime.today().date()):
                ref = live_agent_login_table.objects.all()
                data_outt = ref.filter(date=main_dates[0],logout_time__isnull=False).annotate(hour_out = Trunc('logout_time','hour',output_field=TimeField()),hour_in = Trunc('login_time','hour',output_field=TimeField())).values_list('hour_out','hour_in')
                
                data_inn = ref.filter(date=main_dates[0], logout_time__isnull=True).annotate(hour_in = Trunc('login_time','hour',output_field=TimeField())).values_list('hour_in')
                
                resume = live_break_time.objects.filter(date=main_dates[0],to_time__isnull=True).annotate(from_out=Trunc('from_time','hour',output_field=TimeField())).values_list('from_out')

                val_dict = {}
                val_dict_out = {}

                br_tm = {}
                
                for val in resume:
                    if br_tm.has_key(val[0]):
                        br_tm[str(val[0])].append(1)
                    else:
                        br_tm[str(val[0])] = [1]

                for logout in data_outt:
                    
                    if val_dict_out.has_key(str(logout[1])):
                        val_dict_out[str(logout[1])].append(1)
                        temp = str(datetime.datetime.strptime(str(logout[1]),"%H:%M:%S")+datetime.timedelta(hours=1)).split(" ")[1]
                        while True:
                            if str(logout[0])<temp:
                                break
                            else:
                                if val_dict_out.has_key(temp):
                                    val_dict_out[temp].append(1)
                                else:
                                    val_dict_out[temp] = [1]
                                temp = str(datetime.datetime.strptime(temp,"%H:%M:%S")+datetime.timedelta(hours=1)).split(" ")[1]
                    else:
                        val_dict_out[str(logout[1])] = [1]
                        temp = str(datetime.datetime.strptime(str(logout[1]),"%H:%M:%S")+datetime.timedelta(hours=1)).split(" ")[1]
                        while True:
                            if str(logout[0])<temp:
                                break
                            else:
                                if val_dict_out.has_key(temp):
                                    val_dict_out[temp].append(1)
                                else:
                                    val_dict_out[temp] = [1]
                                temp = str(datetime.datetime.strptime(temp,"%H:%M:%S")+datetime.timedelta(hours=1)).split(" ")[1]    
                    
                
                stt = str(pytz.timezone("Asia/Kolkata").localize(datetime.datetime.now(),is_dst=None)).split('+')
                curr = str(datetime.datetime.strptime(stt[0].split(" ")[1].split('.')[0],"%H:%M:%S")+datetime.timedelta(hours=int(stt[1].split(':')[0]),minutes=int(stt[1].split(':')[1]))).split(' ')[1]
                cur_time = str(datetime.datetime.now()).split(" ")[1].split(".")[0]
                
                for login in data_inn:

                    if val_dict.has_key(str(login[0])):                    
                        val_dict[str(login[0])].append(1)
                        temp = str(datetime.datetime.strptime(str(login[0]),"%H:%M:%S")+datetime.timedelta(hours=1)).split(" ")[1]
                        while True:
                            if temp>curr:
                                break
                            else:
                                if val_dict.has_key(temp):
                                    val_dict[temp].append(1)
                                else:
                                    val_dict[temp]=[1]
                                temp = str(datetime.datetime.strptime(temp,"%H:%M:%S")+datetime.timedelta(hours=1)).split(" ")[1]
                    else:
                        val_dict[str(login[0])] = [1]
                        temp = str(datetime.datetime.strptime(str(login[0]),"%H:%M:%S")+datetime.timedelta(hours=1)).split(" ")[1]
                        while True:
                            if temp>curr:
                                break
                            else:
                                if val_dict.has_key(temp):
                                    val_dict[temp].append(1)
                                else:
                                    val_dict[temp]=[1]
                                temp = str(datetime.datetime.strptime(temp,"%H:%M:%S")+datetime.timedelta(hours=1)).split(" ")[1]
            else:
                ref = live_agent_login_table.objects.all()
                data_outt = ref.filter(date=main_dates[0],logout_time__isnull=False).annotate(hour_out = Trunc('logout_time','hour',output_field=TimeField()),hour_in = Trunc('login_time','hour',output_field=TimeField())).values_list('hour_out','hour_in')
                
                data_inn = ref.filter(date=main_dates[0], logout_time__isnull=True).annotate(hour_in = Trunc('login_time','hour',output_field=TimeField())).values_list('hour_in')
                
                resume = live_break_time.objects.filter(date=main_dates[0],to_time__isnull=True).annotate(from_out=Trunc('from_time','hour',output_field=TimeField())).values_list('from_out')

                val_dict = {}
                val_dict_out = {}

                br_tm = {}
                
                for val in resume:
                    if br_tm.has_key(val[0]):
                        br_tm[str(val[0])].append(1)
                    else:
                        br_tm[str(val[0])] = [1]

                for logout in data_outt: 
                    if val_dict_out.has_key(str(logout[1])):
                        
                        val_dict_out[str(logout[1])].append(1)
                        temp = str(datetime.datetime.strptime(str(logout[1]),"%H:%M:%S")+datetime.timedelta(hours=1)).split(" ")[1]
                        while True:
                            if str(logout[0])<temp:
                                break
                            else:
                                if val_dict_out.has_key(temp):
                                    val_dict_out[temp].append(1)
                                else:
                                    val_dict_out[temp] = [1]
                                temp = str(datetime.datetime.strptime(temp,"%H:%M:%S")+datetime.timedelta(hours=1)).split(" ")[1]
                    else:
                        
                        val_dict_out[str(logout[1])] = [1]
                        temp = str(datetime.datetime.strptime(str(logout[1]),"%H:%M:%S")+datetime.timedelta(hours=1)).split(" ")[1]
                        while True:
                            if str(logout[0])<temp:
                                break
                            else:
                                if val_dict_out.has_key(temp):
                                    val_dict_out[temp].append(1)
                                else:
                                    val_dict_out[temp] = [1]
                                temp = str(datetime.datetime.strptime(temp,"%H:%M:%S")+datetime.timedelta(hours=1)).split(" ")[1]
            
            res = {}
            for key,val in val_dict.iteritems():
                res[key] = val
            for key,val in val_dict_out.iteritems():
                if res.has_key(key):
                    res[key] = res[key] + val
                else:
                    res[key] = val

            pau_tm = {}

            for key,val in br_tm.iteritems():
                temp = sum(br_tm[key])
                key = int(key.split(':')[0],10)
                pau_tm[key] = temp

            for key,val in res.iteritems():
                temp = sum(res[key])
                key = int(key.split(':')[0],10)
                if pau_tm.has_key(key):
                    dct[key] = temp - pau_tm[key]
                else:
                    dct[key] = temp
            
            hourly_val = []
            for i in dates_list:
                if dct.has_key(i):
                    if dct[i] != 0:
                        result_dict['hour'].append(i)
                        hourly_val.append(dct[i])
                else:
                    result_dict['hour'].append(i)
                    hourly_val.append(0)            
            hourly_dct["Hourly Logins"] = hourly_val
            result_dict['value'] = hourly_dct

        else:
            hourly_dct = {}
            val_dic = {}
            val_dict = {}
            reff = live_agent_login_table.objects.filter(date__in = main_dates).exclude(logout_time__isnull=True)
            for dt in main_dates:
                ref = reff.filter(date = dt)
                if ref:
                    data_inn = ref.annotate(hour_in = Trunc('login_time','hour',output_field=TimeField()),hour_out = Trunc('logout_time','hour',output_field=TimeField())).values_list('hour_in','hour_out')
                    for val in data_inn:
                        if str(val[0])<=str(val[1]):
                            if val_dic.has_key(str(val[0])):
                                val_dic[str(val[0])].append(1)
                                temp = str(datetime.datetime.strptime(str(val[0]),"%H:%M:%S")+datetime.timedelta(hours=1)).split(" ")[1]
                                while True:
                                    if str(val[1])<temp:
                                        break
                                    else:
                                        if val_dic.has_key(temp):
                                            val_dic[temp].append(1)
                                        else:
                                            val_dic[temp] = [1]
                                    temp = str(datetime.datetime.strptime(temp,"%H:%M:%S")+datetime.timedelta(hours=1)).split(" ")[1]
                            else:
                                val_dic[str(val[0])] = [1]
                                temp = str(datetime.datetime.strptime(str(val[0]),"%H:%M:%S")+datetime.timedelta(hours=1)).split(" ")[1]
                                while True:
                                    if str(val[1])<temp:
                                        break
                                    else:
                                        val_dic[temp] = [1]
                                    temp = str(datetime.datetime.strptime(temp,"%H:%M:%S")+datetime.timedelta(hours=1)).split(" ")[1]
                    
                if str(datetime.datetime.today().date()) == dt:
                    data_cur = live_agent_login_table.objects.filter(date = dt, logout_time__isnull = True).annotate(hour_in = Trunc('login_time','hour',output_field=TimeField())).values_list('hour_in')
                    stt = str(pytz.timezone("Asia/Kolkata").localize(datetime.datetime.now(),is_dst=None)).split('+')
                    curr = str(datetime.datetime.strptime(stt[0].split(" ")[1].split('.')[0],"%H:%M:%S")+datetime.timedelta(hours=int(stt[1].split(':')[0]),minutes=int(stt[1].split(':')[1]))).split(' ')[1]
                    for dat in data_cur:
                        if val_dic.has_key(str(dat[0])):
                            val_dic[str(dat[0])].append(1)
                            temp = str(datetime.datetime.strptime(str(dat[0]),"%H:%M:%S")+datetime.timedelta(hours=1)).split(" ")[1]
                            while True:
                                if temp>curr:
                                    break
                                else:
                                    if val_dic.has_key(temp):
                                        val_dic[temp].append(1)
                                    else:
                                        val_dic[temp] = [1]
                                    temp = str(datetime.datetime.strptime(temp,"%H:%M:%S")+datetime.timedelta(hours=1)).split(" ")[1]
                        else:
                            val_dic[str(dat[0])] = [1]
                            temp = str(datetime.datetime.strptime(str(dat[0]),"%H:%M:%S")+datetime.timedelta(hours=1)).split(" ")[1]
                            while True:
                                if temp>curr:
                                    break
                                else:
                                    if val_dic.has_key(temp):
                                        val_dic[temp].append(1)
                                    else:
                                        val_dic[temp] = [1]
                                    temp = str(datetime.datetime.strptime(temp,"%H:%M:%S")+datetime.timedelta(hours=1)).split(" ")[1]                            
                
                    
            for key,val in val_dic.iteritems():
                temp = sum(val_dic[key])
                key = int(key.split(':')[0],10)
                dct[key] = temp            
            
            hourly_val = []
            for i in dates_list:
                if dct.has_key(i):
                    if dct[i] != 0:
                        result_dict['hour'].append(i)
                        hourly_val.append(dct[i])
                else:
                    result_dict['hour'].append(i)
                    hourly_val.append(0)
            
        hourly_dct["Hourly Logins"] = hourly_val
        result_dict['value'] = hourly_dct
    
        final_dict[result_name] = graph_data_alignment_color(result_dict['value'], 'data', level_structure_key, \
                                        prj_id, center, result_name)      
                                          
    final_dict['date'] = result_dict['hour']
    final_dict['type'] = main_data_dict['type']  
    final_dict['is_annotation'] = annotation_check(request)  
    return json_HttpResponse(final_dict)

def Test_hourly_error(request):
    
    result_name = "hourly_error"
    function_name = hourly_error
    result = generate_day_week_month_format(request, function_name, result_name)

    return result

def Hourly_Accuracy(request):
    result = {}
    result_name = "hour_acc"
    function_name = Accuracy_Hourly
    result = generate_day_week_month_format(request, function_name, result_name)

    return result

def Total_Login(request):

    result = {}
    if request.GET['to'] == request.GET['from']:
        dt = request.GET['from']
        tot_log = live_agent_login_table.objects.exclude(logout_time__isnull = False)
        data_out = tot_log.filter(date=dt).aggregate(count = Count('agent_id'))
        
        date = [dt]
        data = [data_out['count']]
        result['date'] = date
        result['total_login'] = [{'data':data,'name':'Logins'}]
    
    return json_HttpResponse(result)

def total_hourly_production(request):
    result = {}       
    final_dict = {}
    main_data_dict = data_dict(request.GET)
    prj_id = main_data_dict['pro_cen_mapping'][0][0]
    center = main_data_dict['pro_cen_mapping'][1][0]
    work_packet = main_data_dict['work_packet']
    sub_project = main_data_dict['sub_project']
    sub_packet = main_data_dict['sub_packet']
    pro_center = main_data_dict['pro_cen_mapping']
    
    level_structure_key = get_level_structure_key(work_packet, sub_project, sub_packet, pro_center)
    
    if request.GET['to'] == request.GET['from']:
        filter_params, _term = getting_required_params(level_structure_key, prj_id, center, [request.GET['to']])
        ref = live_transaction_table.objects.filter(**filter_params)
        reff = ref.aggregate(total=Count('id'))
        final_dict['name'] = 'Total Production'
        final_dict["data"] = [reff['total']]        
        result['total'] = [final_dict]
        result['date'] = [request.GET['to']]
    return json_HttpResponse(result)

def Total_Error(request):

    result = {}
    main_data_dict = data_dict(request.GET)
    prj_id = main_data_dict['pro_cen_mapping'][0][0]
    center = main_data_dict['pro_cen_mapping'][1][0]
    work_packet = main_data_dict['work_packet']
    sub_project = main_data_dict['sub_project']
    sub_packet = main_data_dict['sub_packet']
    pro_center = main_data_dict['pro_cen_mapping']
    
    level_structure_key = get_level_structure_key(work_packet, sub_project, sub_packet, pro_center)
    if request.GET['to'] == request.GET['from']:
        
        filter_params, _term = getting_required_params(level_structure_key, prj_id, center, [request.GET['to']])
        ref = live_error_table.objects.filter(**filter_params)
        data_out = ref.aggregate(count = Count('transaction_id'))
        date = [request.GET['from']]
        data = [data_out['count']]
        result['date'] = date
        result['total_err'] = [{'data':data,'name':'Error'}]
    
    return json_HttpResponse(result)

def hourly_production(main_dates, prj_id, center, level_structure_key, dates_list, request, _type):
    result_dict, dct = {}, {}
    filter_params, _term = getting_required_params(level_structure_key, prj_id, center, dates_list)

    if _type == 'hour': 
        if len(main_dates) == 1:
            filter_params.pop('date__range')
            dat = datetime.datetime.strptime(main_dates[0],"%Y-%m-%d").date()
            hourly_dct = {}
            filter_params['date__in'] = main_dates
            ref_obj = live_transaction_table.objects.filter(**filter_params)
            if ref_obj:
                ref = ref_obj.annotate(s_date=Trunc('end_time','date',output_field=DateField())).exclude(s_date__isnull = True)
                data_value = ref.filter(s_date=dat).annotate(hour = Trunc('end_time','hour',output_field=TimeField())).values_list('transaction_id','hour')
                val_dic = {}
                for val in data_value:
                    if val_dic.has_key(str(val[1])):
                        val_dic[str(val[1])].append(int(val[0]))
                    else:
                        val_dic[str(val[1])] = [int(val[0])]
                
                for key,val in val_dic.iteritems():
                    temp = len(val_dic[key])
                    key = int(key.split(':')[0],10)
                    dct[key] = temp
                result_dict['hour'] = []
                hourly_val = []

                for i in dates_list:
                    if dct.has_key(i):
                        if dct[i] != 0:
                            result_dict['hour'].append(i)
                            hourly_val.append(dct[i])
                    else:
                        result_dict['hour'].append(i)
                        hourly_val.append(0)
                
                hourly_dct["Hourly Production"] = hourly_val
                
                result_dict['value'] = hourly_dct
            else:
                result_dict['value'] = {}
                result_dict['hour'] = []
        else:
            filter_params.pop('date__range')
            dat = map(lambda x : datetime.datetime.strptime(x,"%Y-%m-%d").date(), main_dates)
            hourly_dct = {}
            val_dic = {}
            filter_params['date__in'] = main_dates
            
            ref_obj = live_transaction_table.objects.filter(**filter_params)
            if ref_obj:
                for dt in dat:            
                    
                    ref = ref_obj.annotate(s_date=Trunc('end_time','date',output_field=DateField())).exclude(s_date__isnull = True)
                    data_value = ref.filter(s_date=dt).annotate(hour = Trunc('end_time','hour',output_field=TimeField())).values_list('transaction_id','hour')
                    for val in data_value:
                        if val_dic.has_key(str(val[1])):
                            val_dic[str(val[1])].append(int(val[0]))
                        else:
                            val_dic[str(val[1])] = [int(val[0])]
                
                for key,val in val_dic.iteritems():
                    temp = len(val_dic[key])
                    key = int(key.split(':')[0],10)
                    dct[key] = temp
                
                result_dict['hour'] = []
                hourly_val = []
                
                
                for i in dates_list:
                    if dct.has_key(i):
                        result_dict['hour'].append(i)
                        hourly_val.append(dct[i])
                    else:
                        result_dict['hour'].append(i)
                        hourly_val.append(0)
                
                hourly_dct["Hourly Production"] = hourly_val
                
                result_dict['value'] = hourly_dct
            else:
                result_dict['value'] = {}
                result_dict['hour'] = []
    
    else:
        ref_obj = RawTable.objects.filter(**filter_params)
        
        if ref_obj:
            if _type == 'day':
                
                ref = ref_obj.values('date').annotate(sum = Sum('per_day'))
                day_dct, daily_dct = {}, {}
                for val in ref:
                    if not day_dct.has_key(str(val['date'])):
                        day_dct[str(val['date'])] = int(val['sum'])

                daily_val = []
                for i in dates_list:
                    if day_dct.has_key(i):
                        daily_val.append(day_dct[i])
                    else:
                        daily_val.append(0)
                
                result_dict["Production"] = daily_val

            elif _type == 'week':

                week_val = []
                ref = ref_obj.filter(date__in=main_dates).aggregate(sum = Sum('per_day'))
               
                if ref['sum'] != None:
                    week_val.append(ref['sum'])
                else:
                    week_val.append(0)

                result_dict["Production"] = week_val

            elif _type == 'month':
                
                month_val = []
                ref = ref_obj.filter(date__in = main_dates).aggregate(sum = Sum('per_day'))
                if ref['sum'] != None:
                    month_val.append(ref['sum'])
                else:
                    month_val.append(0)

                result_dict["Production"] = month_val
    
    return result_dict

def hourly_error(main_dates, prj_id, center, level_structure_key, dates_list, request, _type):

    result_dict, dct = {}, {}
    filter_params, _term = getting_required_params(level_structure_key, prj_id, center, dates_list)
    
    if _type == 'hour': 
        if len(main_dates) == 1:
            filter_params.pop('date__range')
            filter_params['date__in'] = main_dates
            dat = datetime.datetime.strptime(main_dates[0],"%Y-%m-%d").date()
            hourly_dct = {}
            ref_obj = live_error_table.objects.filter(**filter_params)
            
            if ref_obj:
                ref = ref_obj.annotate(s_date=Trunc('prod_end_time','date',output_field=DateField())).exclude(s_date__isnull = True)
                data_value = ref.filter(s_date=dat).annotate(hour = Trunc('prod_end_time','hour',output_field=TimeField())).values_list('transaction_id','hour')
                val_dic = {}
                for val in data_value:
                    if val_dic.has_key(str(val[1])):
                        val_dic[str(val[1])].append(int(val[0]))
                    else:
                        val_dic[str(val[1])] = [int(val[0])]
                
                for key,val in val_dic.iteritems():
                    temp = len(val_dic[key])
                    key = int(key.split(':')[0],10)
                    dct[key] = temp
                result_dict['hour'] = []
                hourly_val = []

                for i in dates_list:
                    if dct.has_key(i):
                        if dct[i] != 0:
                            result_dict['hour'].append(i)
                            hourly_val.append(dct[i])
                    else:
                        result_dict['hour'].append(i)
                        hourly_val.append(0)
                
                hourly_dct["Hourly Error"] = hourly_val
                
                result_dict['value'] = hourly_dct
            else:
                result_dict['value'] = {}
                result_dict['hour'] = []
        
        else:
            filter_params.pop('date__range')
            dat = map(lambda x : datetime.datetime.strptime(x,"%Y-%m-%d").date(), main_dates)
            hourly_dct = {}
            val_dic = {}
            filter_params['date__in'] = main_dates
            ref_obj = live_error_table.objects.filter(**filter_params)
            if ref_obj:
                for dt in dat:
                    ref = ref_obj.annotate(s_date=Trunc('prod_end_time','date',output_field=DateField())).exclude(s_date__isnull = True)
                    data_value = ref.filter(s_date=dt).annotate(hour = Trunc('prod_end_time','hour',output_field=TimeField())).values_list('transaction_id','hour')
                    for val in data_value:
                        if val_dic.has_key(str(val[1])):
                            val_dic[str(val[1])].append(int(val[0]))
                        else:
                            val_dic[str(val[1])] = [int(val[0])]
                
                for key,val in val_dic.iteritems():
                    temp = len(val_dic[key])
                    key = int(key.split(':')[0],10)
                    dct[key] = temp
                
                result_dict['hour'] = []
                hourly_val = []
                
                
                for i in dates_list:
                    if dct.has_key(i):
                        result_dict['hour'].append(i)
                        hourly_val.append(dct[i])
                    else:
                        result_dict['hour'].append(i)
                        hourly_val.append(0)
                
                hourly_dct["Hourly Error"] = hourly_val
                
                result_dict['value'] = hourly_dct
            else:
                result_dict['value'] = {}
                result_dict['hour'] = []
    else:
        ref_obj = Internalerrors.objects.filter(**filter_params)
        
        if ref_obj:
            
            if _type == 'day':
                ref = ref_obj.values('date').annotate(sum = Sum('total_errors'))
                day_dct, daily_dct = {}, {}
                for val in ref:
                    if not day_dct.has_key(str(val['date'])):
                        day_dct[str(val['date'])] = int(val['sum'])

                daily_val = []
                for i in dates_list:
                    if day_dct.has_key(i):
                        daily_val.append(day_dct[i])
                    else:
                        daily_val.append(0)
                
                result_dict["Error"] = daily_val
            elif _type == 'week':
                ref = ref_obj.filter(date__in=main_dates).aggregate(sum = Sum('total_errors'))

                week_val = []
                if ref['sum'] != None:
                    week_val.append(ref['sum'])
                else:
                    week_val.append(0)
                result_dict['Error'] = week_val
            elif _type == 'month':
                ref = ref_obj.filter(date__in=main_dates).aggregate(sum = Sum('total_errors'))
                month_val = []
                if ref:
                    month_val.append(ref['sum'])
                else:
                    month_val.append(0)
                result_dict['Error'] = month_val

    return result_dict

def Accuracy_Hourly(main_dates, prj_id, center, level_structure_key, dates_list, request, _type):

    result_dict, dct = {}, {}
    filter_params, _term = getting_required_params(level_structure_key, prj_id, center, dates_list)

    if _type == 'hour': 
        if len(main_dates) == 1:
            filter_params.pop('date__range')
            dat = datetime.datetime.strptime(main_dates[0],"%Y-%m-%d").date()
            hourly_dct = {}
            
            filter_params['date__in'] = main_dates
            ref_obj = live_error_table.objects.filter(**filter_params)
            ref_val = live_transaction_table.objects.filter(**filter_params)
            if ref_val:
                val_dic = {}
                out = {}
                if ref_obj:
                    ref = ref_obj.annotate(s_date=Trunc('prod_end_time','date',output_field=DateField())).exclude(s_date__isnull = True)
                    data_value = ref.filter(s_date=dat).annotate(hour = Trunc('prod_end_time','hour',output_field=TimeField())).values_list('transaction_id','hour')
                    
                    for val in data_value:
                        if val_dic.has_key(str(val[1])):
                            val_dic[str(val[1])].append(int(val[0]))
                        else:
                            val_dic[str(val[1])] = [int(val[0])]
                    
                    for key,val in val_dic.iteritems():
                        temp = len(val_dic[key])
                        key = int(key.split(':')[0],10)
                        out[key] = temp
                
                reff = ref_val.annotate(s_date=Trunc('end_time','date',output_field=DateField())).exclude(s_date__isnull = True)
                data_out = reff.filter(s_date=dat).annotate(hour = Trunc('end_time','hour',output_field=TimeField())).values_list('transaction_id','hour')
                
                out_dic = {}

                for val in data_out:
                    if out_dic.has_key(str(val[1])):
                        out_dic[str(val[1])].append(int(val[0]))
                    else:
                        out_dic[str(val[1])] = [int(val[0])]
                
                res = {}
                
                
                for key,val in out_dic.iteritems():
                    temp = len(out_dic[key])
                    key = int(key.split(':')[0],10)
                    res[key] = temp
                result_dict['hour'] = []
                hourly_val = []
                
                for i in dates_list:
                    if res.has_key(i):
                        if out.has_key(i):
                            if res[i] != 0:
                                result_dict['hour'].append(i)
                                val = (float(out[i])/float(res[i]))*100
                                
                                acc = 100 - float('%.2f'%round(val,2))
                                hourly_val.append(acc)
                        else:
                            result_dict['hour'].append(i)
                            hourly_val.append(100)
                    else:
                        result_dict['hour'].append(i)
                        hourly_val.append(0)
                
                hourly_dct["Hourly Accuracy"] = hourly_val
                
                result_dict['value'] = hourly_dct
            else:
                result_dict['value'] = {}
                result_dict['hour'] = []
        else:
            filter_params.pop('date__range')
            dat = map(lambda x : datetime.datetime.strptime(x,"%Y-%m-%d").date(), main_dates)
            hourly_dct = {}
            val_dic = {}
            val_out = {}
            
            filter_params['date__in'] = main_dates
            ref_obj = live_transaction_table.objects.filter(**filter_params)
            ref_val = live_error_table.objects.filter(**filter_params)
            if ref_obj:
                for dt in dat:
                    if ref_val:
                        reff = ref_val.annotate(s_date=Trunc('prod_end_time','date',output_field=DateField())).exclude(s_date__isnull = True)
                        data_out = reff.filter(s_date=dt).annotate(hour = Trunc('prod_end_time','hour',output_field=TimeField())).values_list('transaction_id','hour')
                        for val in data_out:
                            if val_out.has_key(str(val[1])):
                                val_out[str(val[1])].append(int(val[0]))
                            else:
                                val_out[str(val[1])] = [int(val[0])]
                    
                    ref = ref_obj.annotate(s_date=Trunc('end_time','date',output_field=DateField())).exclude(s_date__isnull = True)
                    data_value = ref.filter(s_date=dt).annotate(hour = Trunc('end_time','hour',output_field=TimeField())).values_list('transaction_id','hour')                
                    
                    
                    for val in data_value:
                        if val_dic.has_key(str(val[1])):
                            val_dic[str(val[1])].append(int(val[0]))
                        else:
                            val_dic[str(val[1])] = [int(val[0])]
                    
                out = {}
                res = {}
                for key,val in val_dic.iteritems():
                    temp = len(val_dic[key])
                    key = int(key.split(':')[0],10)
                    out[key] = temp
                if val_out:
                    for key,val in val_out.iteritems():
                        temp = len(val_out[key])
                        key = int(key.split(':')[0],10)
                        res[key] = temp

                result_dict['hour'] = []
                hourly_val = []

                for i in dates_list:
                    if out.has_key(i):
                        if res.has_key(i):
                            result_dict['hour'].append(i)
                            val = (float(res[i])/float(out[i]))*100
                            acc = 100 - float('%.2f'%round(val,2))
                            hourly_val.append(acc)
                        else:
                            result_dict['hour'].append(i)
                            hourly_val.append(100)
                    else:
                        result_dict['hour'].append(i)
                        hourly_val.append(0)

                hourly_dct["Hourly Accuracy"] = hourly_val
                
                result_dict['value'] = hourly_dct
            else:
                result_dict['value'] = {}
                result_dict['hour'] = []
    else:
        ref_obj=Internalerrors.objects.filter(**filter_params)
        
        val_obj = RawTable.objects.filter(**filter_params)
        if ref_obj and val_obj:
            if _type =="day":
                data_value = ref_obj.values('date').annotate(error = Sum('total_errors'))
                data_out = val_obj.values('date').annotate(prod=Sum('per_day'))

                day_dct = {}
                for val in data_value:
                    for val_ue in data_out:
                        if val['date']== val_ue['date']:
                            if not day_dct.has_key(str(val['date'])):
                                if val_ue['prod']!=0:
                                    val_ac=(float(val['error'])/float(val_ue['prod']))*100
                                    accur=100-float('%.2f'%round(val_ac,2))
                                    day_dct[str(val['date'])] = accur
                                

                daily_val = []
                for i in dates_list:
                    
                    if day_dct.has_key(i):
                        daily_val.append(day_dct[i])
                    else:
                        daily_val.append(0)
                        
                result_dict["Total Accuracy"] = daily_val
            
            elif _type =="week":    
                data_value = ref_obj.filter(date__in=main_dates).aggregate(error = Sum('total_errors'))
                data_out = val_obj.filter(date__in=main_dates).aggregate(prod=Sum('per_day'))
                    
                if data_value['error']!=None and data_out['prod']!=None:
                    
                    val_ac= (float(data_value['error'])/float(data_out['prod']))*100
                    accur=100-float('%.2f'%round(val_ac,2))

                    week_val=[]
                    if accur!=None:
                        week_val.append(accur)
                    
                    else:
                        week_val.append(0)   
                            
                    result_dict["Total Accuracy"] = week_val


            elif _type== "month":
                
                data_value = ref_obj.filter(date__in=dates_list).aggregate(error = Sum('total_errors'))
                data_out = val_obj.filter(date__in=dates_list).aggregate(prod=Sum('per_day'))
                
                if data_value['error']!=None and data_out['prod']!=None:
                    
                    val_ac= (float(data_value['error'])/float(data_out['prod']))*100
                    accur=100-float('%.2f'%round(val_ac,2))
                    
                    month_val=[]
                    if accur!=None:
                        month_val.append(accur)
                    else:
                        month_val.append(0)
                    result_dict["Total Accuracy"]=month_val

    return result_dict

def live_date(request):
    date = datetime.datetime.now()
    dt = (str(date)).split(' ')[0]
    date_now = {}
    date_now['result'] = dt
    return json_HttpResponse(date_now)
