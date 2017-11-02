import datetime
import redis
from api.models import *
from api.commons import data_dict
from django.db.models import Max, Sum 
from collections import OrderedDict
from api.utils import *
from api.basics import *
from api.query_generations import query_set_generation
from api.fte_related import fte_calculation
from api.production import main_productivity_data
from api.weekly_graph import *
from api.graph_settings import *
from voice_service.models import *
from voice_service.widgets import *
from common.utils import getHttpResponse as json_HttpResponse

def location(request):
    result, loc_week_dt = {}, {}
    new_date_list, dates_list, week_names = [], [], []
    month_names = []
    week_num, location_week_num = 0, 0
    curr_loc = request.GET['location']
    dispo_val = request.GET['disposition']
    skill_val = request.GET['skill']
    main_dict = data_dict(request.GET)
    prj_id = main_dict['pro_cen_mapping'][0][0]
    center = main_dict['pro_cen_mapping'][1][0]
    if main_dict['dwm_dict'].has_key('hour') and main_dict['type'] == 'hour':
        hours = main_dict['dwm_dict']['hour'][8:22]
        dates = main_dict['dates']
        for date in dates:
            for hour in hours:
                hr = hour*60*60
                hr1 = (hour + 1)*60*60
                final_hour1 = date + ' ' + time.strftime('%H:%M:%S', time.gmtime(hr1))
                final_hour = date + ' ' + time.strftime('%H:%M:%S', time.gmtime(hr))
                hour_check = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1).values('location').count()
                if hour_check > 0:
                    new_date_list.append(hour)
        hrly_loc_val = hourly_location_data(prj_id, center, dates, hours, curr_loc, dispo_val, skill_val)
        result['location'] = [{'name': item, 'data': hrly_loc_val[item]} for item in hrly_loc_val]
        result['date'] = new_date_list
    elif main_dict['dwm_dict'].has_key('day') and main_dict['type'] == 'day':
        dates = main_dict['dwm_dict']['day']
        date_check = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates[0], dates[-1]]).values('date').annotate(total = count('location')).order_by('date')
        values = OrderedDict(zip(map(lambda p: str(p['date']), date_check), map(lambda p: str(p['total']), date_check)))
        for date_key, date_value in values.iteritems():
            if date_value > 0:
                new_date_list.append(date_key)
                result['date'] = new_date_list
        loca_val = location_data(prj_id, center, dates, curr_loc, dispo_val, skill_val)
        result['location'] = [{'name': item, 'data': loca_val[item]} for item in loca_val]
    elif main_dict['dwm_dict'].has_key('week') and main_dict['type'] == 'week':
        dates = main_dict['dwm_dict']['week']
        for date_values in dates:
            dates_list.append(date_values[0] + ' to ' + date_values[-1])
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            location_details = location_data(prj_id, center, date_values, curr_loc, dispo_val, skill_val)
            location_week_name = str('week' + str(location_week_num))
            loc_week_dt[location_week_name] = location_details
            location_week_num = location_week_num + 1
        final_location_data = prod_volume_week(week_names, loc_week_dt, {})
        result['location'] = [{'name': item, 'data': final_location_data[item]} for item in final_location_data]
        result['date'] = dates_list
    else:
        for month_na,month_va in zip(main_dict['dwm_dict']['month']['month_names'],main_dict['dwm_dict']['month']['month_dates']):
            month_name = month_na
            month_dates = month_va
            dates_list.append(month_dates[0] + ' to ' + month_dates[-1])
            month_names.append(month_name)
            location_details = location_data(prj_id, center, month_dates, curr_loc, dispo_val, skill_val)
            loc_week_dt[month_name] = location_details
        final_location_data = prod_volume_week(month_names, loc_week_dt, {})
        result['location'] = [{'name': item, 'data': final_location_data[item]} for item in final_location_data]
        result['date'] = dates_list
    result['type'] = main_dict['type']
    return json_HttpResponse(result)


def skill(request):
    result, skill_week_dt = {}, {}
    new_date_list, dates_list, week_names = [], [], []
    month_names = []
    week_num, skill_week_num = 0, 0
    main_dict = data_dict(request.GET)
    skill = request.GET['skill']
    curr_loca = request.GET['location']
    disposition = request.GET['disposition']
    prj_id = main_dict['pro_cen_mapping'][0][0]
    center = main_dict['pro_cen_mapping'][1][0]
    if main_dict['dwm_dict'].has_key('hour') and main_dict['type'] == 'hour':
        hours = main_dict['dwm_dict']['hour'][8:22]
        dates = main_dict['dates']
        for date in dates:
            for hour in hours:
                hr = hour*60*60
                hr1 = (hour + 1)*60*60
                final_hour1 = date + ' ' + time.strftime('%H:%M:%S', time.gmtime(hr1))
                final_hour = date + ' ' + time.strftime('%H:%M:%S', time.gmtime(hr))
                hour_check = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1).values('skill').count()
                if hour_check > 0:
                    new_date_list.append(hour)
        hrly_skill_val = hourly_skill_data(prj_id, center, dates, hours, curr_loca, disposition, skill)
        result['skill'] = [{'name': item, 'data': hrly_skill_val[item]} for item in hrly_skill_val]
        result['date'] = new_date_list
    elif main_dict['dwm_dict'].has_key('day') and main_dict['type'] == 'day':
        dates = main_dict['dwm_dict']['day']
        date_check = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates[0], dates[-1]]).values('date').annotate(total = count('skill')).order_by('date')
        values = OrderedDict(zip(map(lambda p: str(p['date']), date_check), map(lambda p: str(p['total']), date_check)))
        for date_key, date_value in values.iteritems():
            if date_value > 0:
                new_date_list.append(date_key)
                result['date'] = new_date_list
        skill_val = skill_data(prj_id, center, dates, skill, curr_loca, disposition)
        result['skill'] = [{'name': item, 'data': skill_val[item]} for item in skill_val]
    elif main_dict['dwm_dict'].has_key('week') and main_dict['type'] == 'week':
        dates = main_dict['dwm_dict']['week']
        for date_values in dates:
            dates_list.append(date_values[0] + ' to ' + date_values[-1])
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            skill_details = skill_data(prj_id, center, date_values, skill, curr_loca, disposition)
            skill_week_name = str('week' + str(skill_week_num))
            skill_week_dt[skill_week_name] = skill_details
            skill_week_num = skill_week_num + 1
        final_skill_data = prod_volume_week(week_names, skill_week_dt, {})
        result['skill'] = [{'name': item, 'data': final_skill_data[item]} for item in final_skill_data]
        result['date'] = dates_list
    else:
        for month_na,month_va in zip(main_dict['dwm_dict']['month']['month_names'],main_dict['dwm_dict']['month']['month_dates']):
            month_name = month_na
            month_dates = month_va
            dates_list.append(month_dates[0] + ' to ' + month_dates[-1])
            month_names.append(month_name)
            skill_details = skill_data(prj_id, center, month_dates, skill, curr_loca, disposition)
            skill_week_dt[month_name] = skill_details
        final_skill_data = prod_volume_week(month_names, skill_week_dt, {})
        result['skill'] = [{'name': item, 'data': final_skill_data[item]} for item in final_skill_data]
        result['date'] = dates_list
    result['type'] = main_dict['type']
    return json_HttpResponse(result)


def disposition(request):
    result, dispo_week_dt = {}, {} 
    new_date_list, dates_list, week_names = [], [], []
    month_names = []
    week_num, dispo_week_num = 0, 0
    main_dict = data_dict(request.GET)
    disposition = request.GET['disposition']
    curr_loca = request.GET['location']
    skill = request.GET['skill']
    prj_id = main_dict['pro_cen_mapping'][0][0]
    center = main_dict['pro_cen_mapping'][1][0]
    if main_dict['dwm_dict'].has_key('hour') and main_dict['type'] == 'hour':
        hours = main_dict['dwm_dict']['hour'][8:22]
        dates = main_dict['dates']
        for date in dates:
            for hour in hours:
                hr = hour*60*60
                hr1 = (hour + 1)*60*60
                final_hour1 = date + ' ' + time.strftime('%H:%M:%S', time.gmtime(hr1))
                final_hour = date + ' ' + time.strftime('%H:%M:%S', time.gmtime(hr))
                hour_check = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1).values('disposition').count()
                if hour_check > 0:
                    new_date_list.append(hour)
        hrly_dispo_val = hourly_dispo_data(prj_id, center, dates, hours, curr_loca, disposition, skill)
        result['disposition'] = [{'name': item, 'data': hrly_dispo_val[item]} for item in hrly_dispo_val]
        result['date'] = new_date_list
    elif main_dict['dwm_dict'].has_key('day') and main_dict['type'] == 'day':
        dates = main_dict['dwm_dict']['day']
        date_check = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates[0], dates[-1]]).values('date').annotate(total = count('disposition')).order_by('date')
        values = OrderedDict(zip(map(lambda p: str(p['date']), date_check), map(lambda p: str(p['total']), date_check)))
        for date_key, date_value in values.iteritems():
            if date_value > 0:
                new_date_list.append(date_key)
                result['date'] = new_date_list
        dispo_val = disposition_data(prj_id, center, dates, disposition, curr_loca, skill)
        result['disposition'] = [{'name': item, 'data': dispo_val[item]} for item in dispo_val]

    elif main_dict['dwm_dict'].has_key('week') and main_dict['type'] == 'week':
        dates = main_dict['dwm_dict']['week']
        for date_values in dates:
            dates_list.append(date_values[0] + ' to ' + date_values[-1])
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            dispo_details = disposition_data(prj_id, center, date_values, disposition, curr_loca, skill)
            dispo_week_name = str('week' + str(dispo_week_num))
            dispo_week_dt[dispo_week_name] = dispo_details
            dispo_week_num = dispo_week_num + 1
        final_dispo_data = prod_volume_week(week_names, dispo_week_dt, {})
        result['disposition'] = [{'name': item, 'data': final_dispo_data[item]} for item in final_dispo_data]
        result['date'] = dates_list
    else:
        for month_na,month_va in zip(main_dict['dwm_dict']['month']['month_names'],main_dict['dwm_dict']['month']['month_dates']):
            month_name = month_na
            month_dates = month_va
            dates_list.append(month_dates[0] + ' to ' + month_dates[-1])
            month_names.append(month_name)
            dispo_details = disposition_data(prj_id, center, month_dates, disposition, curr_loca, skill)
            dispo_week_dt[month_name] = dispo_details
        final_dispo_data = prod_volume_week(month_names, dispo_week_dt, {})
        result['disposition'] = [{'name': item, 'data': final_dispo_data[item]} for item in final_dispo_data]
        result['date'] = dates_list
    return json_HttpResponse(result)


def call_status(request):
    result, call_week_dt = {}, {}
    new_date_list, dates_list, week_names = [], [], []
    month_names = []
    week_num, call_week_num = 0, 0
    disposition = request.GET['disposition']
    curr_loca = request.GET['location']
    skill = request.GET['skill']
    main_dict = data_dict(request.GET)
    prj_id = main_dict['pro_cen_mapping'][0][0]
    center = main_dict['pro_cen_mapping'][1][0]
    if main_dict['dwm_dict'].has_key('hour') and main_dict['type'] == 'hour':
        hours = main_dict['dwm_dict']['hour'][8:22]
        dates = main_dict['dates']
        for date in dates:
            for hour in hours:
                hr = hour*60*60
                hr1 = (hour + 1)*60*60
                final_hour1 = date + ' ' + time.strftime('%H:%M:%S', time.gmtime(hr1))
                final_hour = date + ' ' + time.strftime('%H:%M:%S', time.gmtime(hr))
                hour_check = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1).values('status').count()
                if hour_check > 0:
                    new_date_list.append(hour)
        hrly_call_val = hourly_call_data(prj_id, center, dates, hours, curr_loca, disposition, skill)
        result['call_status'] = [{'name': item, 'data': hrly_call_val[item]} for item in hrly_call_val]
        result['date'] = new_date_list

    elif main_dict['dwm_dict'].has_key('day') and main_dict['type'] == 'day':
        dates = main_dict['dwm_dict']['day']
        date_check = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates[0], dates[-1]]).values('date').annotate(total = count('caller_no')).annotate(sta_total = count('status')).order_by('date')
        values = OrderedDict(zip(map(lambda p: str(p['date']), date_check), map(lambda p: str(p['total']), date_check)))
        for date_key, date_value in values.iteritems():
            if date_value > 0:
                new_date_list.append(date_key)
                result['date'] = new_date_list
        call_val = call_status_data(prj_id, center, dates, curr_loca, skill, disposition)
        result['call_status'] = [{'name': item, 'data': call_val[item]} for item in call_val]

    elif main_dict['dwm_dict'].has_key('week') and main_dict['type'] == 'week':
        dates = main_dict['dwm_dict']['week']
        for date_values in dates:
            dates_list.append(date_values[0] + ' to ' + date_values[-1])
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            call_details = call_status_data(prj_id, center, date_values, curr_loca, skill, disposition)
            call_week_name = str('week' + str(call_week_num))
            call_week_dt[call_week_name] = call_details
            call_week_num = call_week_num + 1
        final_call_data = prod_volume_week(week_names, call_week_dt, {})
        result['call_status'] = [{'name': item, 'data': final_call_data[item]} for item in final_call_data]
        result['date'] = dates_list
    else:
        for month_na,month_va in zip(main_dict['dwm_dict']['month']['month_names'],main_dict['dwm_dict']['month']['month_dates']):
            month_name = month_na
            month_dates = month_va
            dates_list.append(month_dates[0] + ' to ' + month_dates[-1])
            month_names.append(month_name)
            call_details = call_status_data(prj_id, center, month_dates, curr_loca, skill, disposition)
            call_week_dt[month_name] = call_details
        final_call_data = prod_volume_week(month_names, call_week_dt, {})
        result['call_status'] = [{'name': item, 'data': final_call_data[item]} for item in final_call_data]
        result['date'] = dates_list
    result['type'] = main_dict['type']
    return json_HttpResponse(result)


def cate_dispo_inbound(request):
    result = {}
    new_date_list, dates_list, week_names = [], [], []
    month_names = []
    curr_loca = request.GET['location']
    disposition = request.GET['disposition']
    skill = request.GET['skill']
    main_dict = data_dict(request.GET)
    prj_id = main_dict['pro_cen_mapping'][0][0]
    center = main_dict['pro_cen_mapping'][1][0]
    if main_dict['dwm_dict'].has_key('hour') and main_dict['type'] == 'hour':
        date = main_dict['dates'][0]
        hour_check = InboundHourlyCall.objects.filter(project = prj_id, center = center, date = date).values('disposition').count()
        if hour_check > 0:
            hrly_dispo_cate = hrly_disposition_cate_data(prj_id, center, date, disposition, curr_loca, skill)
        result['cate_dispo_inbound'] = [{'name': item, 'y': hrly_dispo_cate[item][0]} for item in hrly_dispo_cate]
    elif main_dict['dwm_dict'].has_key('day') and main_dict['type'] == 'day':
        dates = main_dict['dwm_dict']['day']
        date_check = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates[0], dates[-1]]).values('date').annotate(total = count('disposition')).order_by('date')
        values = OrderedDict(zip(map(lambda p: str(p['date']), date_check), map(lambda p: str(p['total']), date_check)))
        for date_key, date_value in values.iteritems():
            if date_value > 0:
                new_date_list.append(date_key)
        dispo_cate_val = disposition_cate_data(prj_id, center, dates, disposition, curr_loca, skill)  
        result['cate_dispo_inbound'] = [{'name': item, 'y': dispo_cate_val[item][0]} for item in dispo_cate_val]
    elif main_dict['dwm_dict'].has_key('week') and main_dict['type'] == 'week':
        dates = main_dict['dwm_dict']['week']
        week_dates = []
        for date_values in dates:
            week_dates = week_dates + date_values
        dispo_cate_val = disposition_cate_data(prj_id, center, week_dates, disposition, curr_loca, skill)
        result['cate_dispo_inbound'] = [{'name': item, 'y': dispo_cate_val[item][0]} for item in dispo_cate_val]
    else:
        month_dates = []
        dates = main_dict['dwm_dict']['month']['month_dates']
        for date_values in dates:
            month_dates = month_dates + date_values
        dispo_cate_val = disposition_cate_data(prj_id, center, month_dates, disposition, curr_loca, skill)
        result['cate_dispo_inbound'] = [{'name': item, 'y': dispo_cate_val[item][0]} for item in dispo_cate_val]
    result['type'] = main_dict['type']
    return json_HttpResponse(result)

def outbound_dispo_cate(request):
    result = {}
    new_date_list = []
    disposition = request.GET['disposition']
    main_dict = data_dict(request.GET)
    prj_id = main_dict['pro_cen_mapping'][0][0]
    center = main_dict['pro_cen_mapping'][1][0]
    if main_dict['dwm_dict'].has_key('hour') and main_dict['type'] == 'hour':
        date = main_dict['dates'][0]
        hour_check = OutboundHourlyCall.objects.filter(project = prj_id, center = center, date = date).values('disposition').count()
        if hour_check > 0:
            hrly_dispo_outbnd_cate = hrly_dispo_outbound_cate_data(prj_id, center, date, disposition)
        result['outbound_dispo_cate'] = [{'name': item, 'y': hrly_dispo_outbnd_cate[item][0]} for item in hrly_dispo_outbnd_cate]
    elif main_dict['dwm_dict'].has_key('day') and main_dict['type'] == 'day':
        dates = main_dict['dwm_dict']['day']
        date_check = OutboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates[0], dates[-1]]).values('date').annotate(total = count('disposition')).order_by('date')
        values = OrderedDict(zip(map(lambda p: str(p['date']), date_check), map(lambda p: str(p['total']), date_check)))
        for date_key, date_value in values.iteritems():
            if date_value > 0:
                new_date_list.append(date_key)
        dispo_out_cate_val = dispo_outbound_cate_data(prj_id, center, dates, disposition)
        result['outbound_dispo_cate'] = [{'name': item, 'y': dispo_out_cate_val[item][0]} for item in dispo_out_cate_val]
    elif main_dict['dwm_dict'].has_key('week') and main_dict['type'] == 'week':
        dates = main_dict['dwm_dict']['week']
        week_dates = []
        for date_values in dates:
            week_dates = week_dates + date_values
        dispo_out_cate_val = dispo_outbound_cate_data(prj_id, center, week_dates, disposition)
        result['outbound_dispo_cate'] = [{'name': item, 'y': dispo_out_cate_val[item][0]} for item in dispo_out_cate_val]
    else:
        month_dates = []
        dates = main_dict['dwm_dict']['month']['month_dates']
        for date_values in dates:
            month_dates = month_dates + date_values
        dispo_out_cate_val = dispo_outbound_cate_data(prj_id, center, month_dates, disposition)
        result['outbound_dispo_cate'] = [{'name': item, 'y': dispo_out_cate_val[item][0]} for item in dispo_out_cate_val]
    result['type'] = main_dict['type']
    return json_HttpResponse(result)


def outbound_disposition(request):
    result, dispo_week_dt = {}, {}
    new_date_list, dates_list, week_names = [], [], []
    month_names = []
    week_num, dispo_week_num = 0, 0
    main_dict = data_dict(request.GET)
    disposition = request.GET['disposition']
    prj_id = main_dict['pro_cen_mapping'][0][0]
    center = main_dict['pro_cen_mapping'][1][0]
    if main_dict['dwm_dict'].has_key('hour') and main_dict['type'] == 'hour':
        hours = main_dict['dwm_dict']['hour'][8:22]
        dates = main_dict['dates']
        for date in dates:
            for hour in hours:
                hr = hour*60*60
                hr1 = (hour + 1)*60*60
                final_hour1 = date + ' ' + time.strftime('%H:%M:%S', time.gmtime(hr1))
                final_hour = date + ' ' + time.strftime('%H:%M:%S', time.gmtime(hr))
                hour_check = OutboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1).values('disposition').count()
                if hour_check > 0:
                    new_date_list.append(hour)
        hrly_outbnd_dispo_val = hourly_outbnd_dispo_data(prj_id, center, dates, hours, disposition)
        result['outbound_disposition'] = [{'name': item, 'data': hrly_outbnd_dispo_val[item]} for item in hrly_outbnd_dispo_val]
        result['date'] = new_date_list
    elif main_dict['dwm_dict'].has_key('day') and main_dict['type'] == 'day':
        dates = main_dict['dwm_dict']['day']
        date_check = OutboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates[0], dates[-1]]).values('date').annotate(total = count('disposition')).order_by('date')
        values = OrderedDict(zip(map(lambda p: str(p['date']), date_check), map(lambda p: str(p['total']), date_check)))
        for date_key, date_value in values.iteritems():
            if date_value > 0:
                new_date_list.append(date_key)
                result['date'] = new_date_list
        outbnd_dispo_val = outbnd_disposition_data(prj_id, center, dates, disposition)
        result['outbound_disposition'] = [{'name': item, 'data': outbnd_dispo_val[item]} for item in outbnd_dispo_val]
    elif main_dict['dwm_dict'].has_key('week') and main_dict['type'] == 'week':
        dates = main_dict['dwm_dict']['week']
        for date_values in dates:
            dates_list.append(date_values[0] + ' to ' + date_values[-1])
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            dispo_details = outbnd_disposition_data(prj_id, center, date_values, disposition)
            dispo_week_name = str('week' + str(dispo_week_num))
            dispo_week_dt[dispo_week_name] = dispo_details
            dispo_week_num = dispo_week_num + 1
        final_outbnd_dispo_data = prod_volume_week(week_names, dispo_week_dt, {})
        result['outbound_disposition'] = [{'name': item, 'data': final_outbnd_dispo_data[item]} for item in final_outbnd_dispo_data]
        result['date'] = dates_list
    else:
        for month_na,month_va in zip(main_dict['dwm_dict']['month']['month_names'],main_dict['dwm_dict']['month']['month_dates']):
            month_name = month_na
            month_dates = month_va
            dates_list.append(month_dates[0] + ' to ' + month_dates[-1])
            month_names.append(month_name)
            dispo_details = outbnd_disposition_data(prj_id, center, month_dates, disposition)
            dispo_week_dt[month_name] = dispo_details
        final_outbnd_dispo_data = prod_volume_week(month_names, dispo_week_dt, {})
        result['outbound_disposition'] = [{'name': item, 'data': final_outbnd_dispo_data[item]} for item in final_outbnd_dispo_data]
        result['date'] = dates_list
    return json_HttpResponse(result)


