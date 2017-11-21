import datetime
#import redis
from api.models import *
from api.commons import data_dict
from django.db.models import Max, Sum 
#from collections import OrderedDict
#from api.utils import *
#from api.basics import *
#from api.query_generations import query_set_generation
#from api.fte_related import fte_calculation
#from api.production import main_productivity_data
from api.weekly_graph import *
#from api.graph_settings import *
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
    prj_type = request.GET['project_type']
    if main_dict['dwm_dict'].has_key('hour') and main_dict['type'] == 'hour':
        hours = main_dict['dwm_dict']['hour'][8:22]
        dates = main_dict['dates']
        location = location_value(curr_loc)
        disposition = dispo_value(dispo_val)
        skill = skill_value(skill_val)
        table_name = project_value(prj_type)
        project = {'project' : [prj_id]}
        dates = {'date' : dates}
        for date in dates:
            for hour in hours:
                hr = hour*60*60
                hr1 = (hour + 1)*60*60
                final_hour1 = date + ' ' + time.strftime('%H:%M:%S', time.gmtime(hr1))
                final_hour = date + ' ' + time.strftime('%H:%M:%S', time.gmtime(hr))
                hour_check = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1).values('location').count()
                if hour_check > 0:
                    new_date_list.append(hour)
        hrly_loc_val = hourly_location_data(project, dates, table_name, location, disposition, skill)
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
        result['location'] = graph_format(loca_val)

    elif main_dict['dwm_dict'].has_key('week') and main_dict['type'] == 'week':
        dates = main_dict['dwm_dict']['week']
        #location_details = location_data(prj_id, center, date_values, curr_loc, dispo_val, skill_val)
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
        #final_week_data = week_calculation(prj_id, center, dates, curr_loc, dispo_val, skill_val)
        result['location'] = graph_format(final_location_data)
        #result['location'] = [{'name': item, 'data': final_week_data[item]} for item in final_week_data]
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
        result['location'] = graph_format(final_location_data)
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
        #result['skill'] = [{'name': item, 'data': hrly_skill_val[item]} for item in hrly_skill_val]
        result['skill'] = graph_format(hrly_skill_val)
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
        result['skill'] = graph_format(skill_val)
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
        result['skill'] = graph_format(final_skill_data)
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
        result['skill'] = graph_format(final_skill_data)
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
        result['disposition'] = graph_format(hrly_dispo_val)
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
        result['disposition'] = graph_format(dispo_val)

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
        result['disposition'] = graph_format(final_dispo_data)
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
        result['disposition'] = graph_format(final_dispo_data)
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
        result['call_status'] = graph_format(hrly_call_val)
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
        result['call_status'] = graph_format(call_val)

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
        result['call_status'] = graph_format(final_call_data)
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
        result['call_status'] = graph_format(final_call_data)
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
        result['outbound_disposition'] = graph_format(hrly_outbnd_dispo_val)
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
        result['outbound_disposition'] = graph_format(outbnd_dispo_val)
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
        result['outbound_disposition'] = graph_format(final_outbnd_dispo_data)
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
        result['outbound_disposition'] = graph_format(final_outbnd_dispo_data)
        result['date'] = dates_list
    result['type'] = main_dict['type']
    return json_HttpResponse(result)


def outbnd_dispo_common(request):
    result, dispo_week_dt = {}, {}
    new_date_list, dates_list, week_names = [], [], []
    month_names = []
    week_num, dispo_week_num = 0, 0
    main_dict = data_dict(request.GET)
    disposition = request.GET['disposition']
    prj_id = main_dict['pro_cen_mapping'][0][0]
    center = main_dict['pro_cen_mapping'][1][0]
    if main_dict['dwm_dict'].has_key('day') and main_dict['type'] == 'day':
        dates = main_dict['dwm_dict']['day']
        date_check = OutboundDaily.objects.filter(project = prj_id, center = center, date__range = [dates[0], dates[-1]]).values('date').annotate(total = count('disposition')).order_by('date')
        values = OrderedDict(zip(map(lambda p: str(p['date']), date_check), map(lambda p: str(p['total']), date_check)))
        for date_key, date_value in values.iteritems():
            if date_value > 0:
                new_date_list.append(date_key)
                result['date'] = new_date_list
        outbnd_dispo_common_val = common_outbnd_dispo_data(prj_id, center, dates, disposition)
        result['outbnd_dispo_common'] = [outbnd_dispo_common_val]
        final_values = outbnd_dispo_common_val.update({'name':'Disposition'})
    elif main_dict['dwm_dict'].has_key('week') and main_dict['type'] == 'week':
        dates = main_dict['dwm_dict']['week']
        for date_values in dates:
            dates_list.append(date_values[0] + ' to ' + date_values[-1])
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            dispo_common_details = common_outbnd_dispo_data(prj_id, center, date_values, disposition)
            dispo_week_name = str('week' + str(dispo_week_num))
            dispo_week_dt[dispo_week_name] = dispo_common_details
            dispo_week_num = dispo_week_num + 1
        outbnd_dispo_common_data = prod_volume_week(week_names, dispo_week_dt, {})
        result['outbnd_dispo_common'] = [outbnd_dispo_common_data]
        final_values = outbnd_dispo_common_data.update({'name':'Disposition'})
        result['date'] = dates_list
    else:
        for month_na,month_va in zip(main_dict['dwm_dict']['month']['month_names'],main_dict['dwm_dict']['month']['month_dates']):
            month_name = month_na
            month_dates = month_va
            dates_list.append(month_dates[0] + ' to ' + month_dates[-1])
            month_names.append(month_name)
            dispo_common_details = common_outbnd_dispo_data(prj_id, center, month_dates, disposition)
            dispo_week_dt[month_name] = dispo_common_details
        outbnd_dispo_common_data = prod_volume_week(month_names, dispo_week_dt, {})
        result['outbnd_dispo_common'] = [outbnd_dispo_common_data]
        final_values = outbnd_dispo_common_data.update({'name':'Disposition'})
        result['date'] = dates_list
    result['type'] = main_dict['type']
    return json_HttpResponse(result)

def outbnd_utilization(request):
    result, outbnd_utility_week_dt = {}, {}
    new_date_list, dates_list, week_names = [], [], []
    month_names = []
    week_num, utiliti_week_num = 0, 0
    main_dict = data_dict(request.GET)
    prj_id = main_dict['pro_cen_mapping'][0][0]
    center = main_dict['pro_cen_mapping'][1][0]
    disposition = request.GET['disposition']
    if main_dict['dwm_dict'].has_key('day') and main_dict['type'] == 'day':
        dates = main_dict['dwm_dict']['day']
        for date in dates:
            utility_query = AgentPerformance.objects.filter(project = prj_id, center = center, date = date, call_type = 'Manual').values('agent').count()
            if utility_query > 0:
                new_date_list.append(date)
                result['date'] = new_date_list
        outbnd_utility_data = outbnd_utilization_data(prj_id, center, dates, disposition)
        result['outbnd_utilization'] = [outbnd_utility_data]
        final_values = outbnd_utility_data.update({'name':'Outbound Utilization'})
    elif main_dict['dwm_dict'].has_key('week') and main_dict['type'] == 'week':
        dates = main_dict['dwm_dict']['week']
        for date_values in dates:
            dates_list.append(date_values[0] + ' to ' + date_values[-1])
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            outbnd_utility_data = outbnd_utilization_data(prj_id, center, date_values, disposition)
            utiliti_week_name = str('week' + str(utiliti_week_num))
            outbnd_utility_week_dt[utiliti_week_name] = outbnd_utility_data
            utiliti_week_num = utiliti_week_num + 1
        week_outbnd_utility_data = prod_volume_week_util_headcount(week_names, outbnd_utility_week_dt, {})
        result['outbnd_utilization'] = [week_outbnd_utility_data]
        final_values = week_outbnd_utility_data.update({'name':'Outbound Utilization'})
        result['date'] = dates_list
    else:
        for month_na,month_va in zip(main_dict['dwm_dict']['month']['month_names'],main_dict['dwm_dict']['month']['month_dates']):
            month_name = month_na
            month_dates = month_va
            dates_list.append(month_dates[0] + ' to ' + month_dates[-1])
            month_names.append(month_name)
            outbnd_utility_data = outbnd_utilization_data(prj_id, center, month_dates, disposition)
            outbnd_utility_week_dt[month_name] = outbnd_utility_data
        month_outbnd_utility_data = prod_volume_week_util_headcount(month_names, outbnd_utility_week_dt, {})
        result['outbnd_utilization'] = [month_outbnd_utility_data]
        final_values = month_outbnd_utility_data.update({'name':'Outbound Utilization'})
        result['date'] = dates_list
    return json_HttpResponse(result)


def inbnd_utilization(request):
    result, inbnd_utility_week_dt = {}, {}
    new_date_list, dates_list, week_names = [], [], []
    month_names = []
    week_num, inbnd_utiliti_week_num = 0, 0
    main_dict = data_dict(request.GET)
    prj_id = main_dict['pro_cen_mapping'][0][0]
    center = main_dict['pro_cen_mapping'][1][0]
    location = request.GET['location']
    skill = request.GET['skill']
    disposition = request.GET['disposition']
    if main_dict['dwm_dict'].has_key('day') and main_dict['type'] == 'day':
        dates = main_dict['dwm_dict']['day']
        for date in dates:
            utility_query = AgentPerformance.objects.filter(project = prj_id, center = center, date = date, call_type = 'Inbound').values('agent').count()   
            if utility_query > 0:   
                new_date_list.append(date)
                result['date'] = new_date_list
        inbnd_utility_data = inbnd_utilization_data(prj_id, center, dates, location, skill, disposition)
        result['inbnd_utilization'] = [inbnd_utility_data]
        final_values = inbnd_utility_data.update({'name':'Inbound Utilization'})
    elif main_dict['dwm_dict'].has_key('week') and main_dict['type'] == 'week':
        dates = main_dict['dwm_dict']['week']
        for date_values in dates:
            dates_list.append(date_values[0] + ' to ' + date_values[-1])
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            inbnd_utility_data = inbnd_utilization_data(prj_id, center, date_values, location, skill, disposition)
            inbnd_utiliti_week_name = str('week' + str(inbnd_utiliti_week_num))
            inbnd_utility_week_dt[inbnd_utiliti_week_name] = inbnd_utility_data
            inbnd_utiliti_week_num = inbnd_utiliti_week_num + 1
        week_inbnd_utility_data = prod_volume_week_util_headcount(week_names, inbnd_utility_week_dt, {})
        result['inbnd_utilization'] = [week_inbnd_utility_data]
        final_values = week_inbnd_utility_data.update({'name':'Inbound Utilization'})
        result['date'] = dates_list
    else:
        for month_na,month_va in zip(main_dict['dwm_dict']['month']['month_names'],main_dict['dwm_dict']['month']['month_dates']):
            month_name = month_na 
            month_dates = month_va
            dates_list.append(month_dates[0] + ' to ' + month_dates[-1])
            month_names.append(month_name)
            inbnd_utility_data = inbnd_utilization_data(prj_id, center, month_dates, location, skill, disposition)
            inbnd_utility_week_dt[month_name] = inbnd_utility_data
        month_inbnd_utility_data = prod_volume_week_util_headcount(month_names, inbnd_utility_week_dt, {})
        result['inbnd_utilization'] = [month_inbnd_utility_data]
        final_values = month_inbnd_utility_data.update({'name':'Inbound Utilization'})
        result['date'] = dates_list
    return json_HttpResponse(result)

def inbnd_occupancy(request):
    result, inbnd_occupa_week_dt = {}, {}
    new_date_list, dates_list, week_names = [], [], []
    month_names = []
    week_num, inbnd_occupa_week_num = 0, 0
    main_dict = data_dict(request.GET)
    prj_id = main_dict['pro_cen_mapping'][0][0]
    center = main_dict['pro_cen_mapping'][1][0]
    location = request.GET['location']
    skill = request.GET['skill']
    disposition = request.GET['disposition']
    if main_dict['dwm_dict'].has_key('day') and main_dict['type'] == 'day':
        dates = main_dict['dwm_dict']['day']
        for date in dates:
            occupancy_query = AgentPerformance.objects.filter(project = prj_id, center = center, date = date, call_type = 'Inbound').values('agent').count()  
            if occupancy_query > 0:
                new_date_list.append(date)
                result['date'] = new_date_list
        inbnd_occupancy = inbound_occupancy_data(prj_id, center, dates, location, skill, disposition)
        result['inbnd_occupancy'] = [inbnd_occupancy]
        final_values = inbnd_occupancy.update({'name':'Inbound Occupancy'})
    elif main_dict['dwm_dict'].has_key('week') and main_dict['type'] == 'week':
        dates = main_dict['dwm_dict']['week']
        for date_values in dates:
            dates_list.append(date_values[0] + ' to ' + date_values[-1])
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            inbnd_occupancy = inbound_occupancy_data(prj_id, center, date_values, location, skill, disposition)
            inbnd_occupa_week_name = str('week' + str(inbnd_occupa_week_num))
            inbnd_occupa_week_dt[inbnd_occupa_week_name] = inbnd_occupancy
            inbnd_occupa_week_num = inbnd_occupa_week_num + 1
        week_inbnd_occupancy_data = prod_volume_week_util_headcount(week_names, inbnd_occupa_week_dt, {})
        result['inbnd_occupancy'] = [week_inbnd_occupancy_data]
        final_values = week_inbnd_occupancy_data.update({'name':'Inbound Occupancy'})
        result['date'] = dates_list
    else:
        for month_na,month_va in zip(main_dict['dwm_dict']['month']['month_names'],main_dict['dwm_dict']['month']['month_dates']):
            month_name = month_na
            month_dates = month_va
            dates_list.append(month_dates[0] + ' to ' + month_dates[-1])
            month_names.append(month_name)
            inbnd_occupancy = inbound_occupancy_data(prj_id, center, month_dates, location, skill, disposition)
            inbnd_occupa_week_dt[month_name] = inbnd_occupancy
        month_inbnd_occupa_data = prod_volume_week_util_headcount(month_names, inbnd_occupa_week_dt, {})
        result['inbnd_occupancy'] = [month_inbnd_occupa_data]
        final_values = month_inbnd_occupa_data.update({'name':'Inbound Occupancy'})
        result['date'] = dates_list
    return json_HttpResponse(result)


def outbnd_occupancy(request):
    result, outbnd_occupa_week_dt = {}, {}
    new_date_list, dates_list, week_names = [], [], []
    month_names = []
    week_num, outbnd_occupa_week_num = 0, 0
    main_dict = data_dict(request.GET) 
    prj_id = main_dict['pro_cen_mapping'][0][0]
    center = main_dict['pro_cen_mapping'][1][0]
    disposition = request.GET['disposition']
    if main_dict['dwm_dict'].has_key('day') and main_dict['type'] == 'day':
        dates = main_dict['dwm_dict']['day']
        for date in dates:
            occupancy_query = AgentPerformance.objects.filter(project = prj_id, center = center, date = date, call_type = 'Manual').values('agent').count()
            if occupancy_query > 0:
                new_date_list.append(date)
                result['date'] = new_date_list
        otbnd_occupancy = outbound_occupancy_data(prj_id, center, dates, disposition)
        result['outbnd_occupancy'] = [otbnd_occupancy]
        final_values = otbnd_occupancy.update({'name':'Outbound Occupancy'})
    elif main_dict['dwm_dict'].has_key('week') and main_dict['type'] == 'week':
        dates = main_dict['dwm_dict']['week']
        for date_values in dates:
            dates_list.append(date_values[0] + ' to ' + date_values[-1])
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            otbnd_occupancy = outbound_occupancy_data(prj_id, center, date_values, disposition)
            outbnd_occupa_week_name = str('week' + str(outbnd_occupa_week_num))
            outbnd_occupa_week_dt[outbnd_occupa_week_name] = otbnd_occupancy
            outbnd_occupa_week_num = outbnd_occupa_week_num + 1
        week_outbnd_occupancy_data = prod_volume_week_util_headcount(week_names, outbnd_occupa_week_dt, {})
        result['outbnd_occupancy'] = [week_outbnd_occupancy_data]
        final_values = week_outbnd_occupancy_data.update({'name':'Outbound Occupancy'})
        result['date'] = dates_list
    else:
        for month_na,month_va in zip(main_dict['dwm_dict']['month']['month_names'],main_dict['dwm_dict']['month']['month_dates']):
            month_name = month_na
            month_dates = month_va
            dates_list.append(month_dates[0] + ' to ' + month_dates[-1])
            month_names.append(month_name)
            otbnd_occupancy = outbound_occupancy_data(prj_id, center, month_dates, disposition)
            outbnd_occupa_week_dt[month_name] = otbnd_occupancy
        month_outbnd_occupa_data = prod_volume_week_util_headcount(month_names, outbnd_occupa_week_dt, {})
        result['outbnd_occupancy'] = [month_outbnd_occupa_data]
        final_values = month_outbnd_occupa_data.update({'name':'Outbound Occupancy'})
        result['date'] = dates_list 
    return json_HttpResponse(result)


def outbound_productivity(request):
    result, outbnd_prod_week_dt = {}, {}
    new_date_list, dates_list, week_names = [], [], []
    month_names = []
    week_num, outbnd_prod_week_num = 0, 0
    main_dict = data_dict(request.GET)
    prj_id = main_dict['pro_cen_mapping'][0][0]
    center = main_dict['pro_cen_mapping'][1][0]
    disposition = request.GET['disposition']
    if main_dict['dwm_dict'].has_key('day') and main_dict['type'] == 'day':
        dates = main_dict['dwm_dict']['day']
        for date in dates:
            prod_query = AgentPerformance.objects.filter(project = prj_id, center = center, date = date, call_type = 'Manual').values('agent').count()
            if prod_query > 0:
                new_date_list.append(date)
                result['date'] = new_date_list
        outbnd_prod = outbound_productivity_data(prj_id, center, dates, disposition)
        result['outbound_productivity'] = [outbnd_prod]
        final_values = outbnd_prod.update({'name':'Outbound Productivity'})
    elif main_dict['dwm_dict'].has_key('week') and main_dict['type'] == 'week':
        dates = main_dict['dwm_dict']['week']
        for date_values in dates:
            dates_list.append(date_values[0] + ' to ' + date_values[-1])
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            outbnd_prod = outbound_productivity_data(prj_id, center, date_values, disposition)
            outbnd_prod_week_name = str('week' + str(outbnd_prod_week_num))
            outbnd_prod_week_dt[outbnd_prod_week_name] = outbnd_prod
            outbnd_prod_week_num = outbnd_prod_week_num + 1
        week_outbnd_prod_data = prod_volume_week_util_headcount(week_names, outbnd_prod_week_dt, {})
        result['outbound_productivity'] = [week_outbnd_prod_data]
        final_values = week_outbnd_prod_data.update({'name':'Outbound Productivity'})
        result['date'] = dates_list
    else:
        for month_na,month_va in zip(main_dict['dwm_dict']['month']['month_names'],main_dict['dwm_dict']['month']['month_dates']):
            month_name = month_na 
            month_dates = month_va
            dates_list.append(month_dates[0] + ' to ' + month_dates[-1])
            month_names.append(month_name)
            outbnd_prod = outbound_productivity_data(prj_id, center, month_dates, disposition)
            outbnd_prod_week_dt[month_name] = outbnd_prod
        month_outbnd_prod_data = prod_volume_week_util_headcount(month_names, outbnd_prod_week_dt, {})
        result['outbound_productivity'] = [month_outbnd_prod_data]
        final_values = month_outbnd_prod_data.update({'name':'Outbound Productivity'})
        result['date'] = dates_list  
    return json_HttpResponse(result)


def inbound_productivity(request):
    result, inbnd_prod_week_dt = {}, {}
    new_date_list, dates_list, week_names = [], [], []
    month_names = []
    week_num, inbnd_prod_week_num = 0, 0
    main_dict = data_dict(request.GET)
    prj_id = main_dict['pro_cen_mapping'][0][0]
    center = main_dict['pro_cen_mapping'][1][0]
    location = request.GET['location']
    skill = request.GET['skill']
    disposition = request.GET['disposition']
    if main_dict['dwm_dict'].has_key('day') and main_dict['type'] == 'day':
        dates = main_dict['dwm_dict']['day']
        for date in dates:
            prod_query = AgentPerformance.objects.filter(project = prj_id, center = center, date = date, call_type = 'Inbound').values('agent').count()
            if prod_query > 0:
                new_date_list.append(date)
                result['date'] = new_date_list
        inbnd_prod = inbound_productivity_data(prj_id, center, dates, location, skill, disposition)
        result['inbound_productivity'] = [inbnd_prod]
        final_values = inbnd_prod.update({'name':'Inbound Productivity'})
    elif main_dict['dwm_dict'].has_key('week') and main_dict['type'] == 'week':
        dates = main_dict['dwm_dict']['week']
        for date_values in dates:
            dates_list.append(date_values[0] + ' to ' + date_values[-1])
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            inbnd_prod = inbound_productivity_data(prj_id, center, date_values, location, skill, disposition)
            inbnd_prod_week_name = str('week' + str(inbnd_prod_week_num))
            inbnd_prod_week_dt[inbnd_prod_week_name] = inbnd_prod
            inbnd_prod_week_num = inbnd_prod_week_num + 1
        week_inbnd_prod_data = prod_volume_week_util_headcount(week_names, inbnd_prod_week_dt, {})
        result['inbound_productivity'] = [week_inbnd_prod_data]
        final_values = week_inbnd_prod_data.update({'name':'Inbound Productivity'})
        result['date'] = dates_list
    else:
        for month_na,month_va in zip(main_dict['dwm_dict']['month']['month_names'],main_dict['dwm_dict']['month']['month_dates']):
            month_name = month_na
            month_dates = month_va
            dates_list.append(month_dates[0] + ' to ' + month_dates[-1])
            month_names.append(month_name)
            inbnd_prod = inbound_productivity_data(prj_id, center, month_dates, location, skill, disposition)
            inbnd_prod_week_dt[month_name] = inbnd_prod
        month_inbnd_prod_data = prod_volume_week_util_headcount(month_names, inbnd_prod_week_dt, {})
        result['inbound_productivity'] = [month_inbnd_prod_data]
        final_values = month_inbnd_prod_data.update({'name':'Inbound Productivity'})
        result['date'] = dates_list
    return json_HttpResponse(result)

def utilization(request):
    result, utility_week_dt = {}, {}
    new_date_list, dates_list, week_names = [], [], []
    month_names = []
    week_num, utiliti_week_num = 0, 0
    main_dict = data_dict(request.GET)
    prj_id = main_dict['pro_cen_mapping'][0][0]
    center = main_dict['pro_cen_mapping'][1][0]
    location = request.GET['location']
    skill = request.GET['skill']
    disposition = request.GET['disposition']
    if main_dict['dwm_dict'].has_key('day') and main_dict['type'] == 'day':
        dates = main_dict['dwm_dict']['day']
        for date in dates:
            common_utility_query = AgentPerformance.objects.filter(project = prj_id, center = center, date = date).values('agent').count()
            if common_utility_query > 0:
                new_date_list.append(date)
                result['date'] = new_date_list
        utility_data = utilization_data(prj_id, center, dates, location, skill, disposition)
        result['utilization'] = [utility_data]
        final_values = utility_data.update({'name':'Utilization'})
    elif main_dict['dwm_dict'].has_key('week') and main_dict['type'] == 'week':
        dates = main_dict['dwm_dict']['week']
        for date_values in dates:
            dates_list.append(date_values[0] + ' to ' + date_values[-1])
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            utility_data = utilization_data(prj_id, center, date_values, location, skill, disposition)
            utiliti_week_name = str('week' + str(utiliti_week_num))
            utility_week_dt[utiliti_week_name] = utility_data
            utiliti_week_num = utiliti_week_num + 1
        week_utility_data = prod_volume_week_util_headcount(week_names, utility_week_dt, {})
        result['utilization'] = [week_utility_data]
        final_values = week_utility_data.update({'name':'Utilization'})
        result['date'] = dates_list
    else:
        for month_na,month_va in zip(main_dict['dwm_dict']['month']['month_names'],main_dict['dwm_dict']['month']['month_dates']):
            month_name = month_na
            month_dates = month_va
            dates_list.append(month_dates[0] + ' to ' + month_dates[-1])
            month_names.append(month_name)
            utility_data = utilization_data(prj_id, center, month_dates, location, skill, disposition)
            utility_week_dt[month_name] = utility_data
        month_utility_data = prod_volume_week_util_headcount(month_names, utility_week_dt, {})
        result['utilization'] = [month_utility_data]
        final_values = month_utility_data.update({'name':'Utilization'})
        result['date'] = dates_list
    return json_HttpResponse(result)

def occupancy(request):
    result, occupa_week_dt = {}, {}
    new_date_list, dates_list, week_names = [], [], []
    month_names = []
    week_num, occupa_week_num = 0, 0
    main_dict = data_dict(request.GET)
    prj_id = main_dict['pro_cen_mapping'][0][0]
    center = main_dict['pro_cen_mapping'][1][0]
    location = request.GET['location']
    skill = request.GET['skill']
    disposition = request.GET['disposition']
    if main_dict['dwm_dict'].has_key('day') and main_dict['type'] == 'day':
        dates = main_dict['dwm_dict']['day']
        for date in dates:
            common_occupancy_query = AgentPerformance.objects.filter(project = prj_id, center = center, date = date).values('agent').count()
            if common_occupancy_query > 0:
                new_date_list.append(date)
                result['date'] = new_date_list
        occup_data = occupancy_data(prj_id, center, dates, location, skill, disposition)
        result['occupancy'] = [occup_data]
        final_values = occup_data.update({'name':'Occupancy'})
    elif main_dict['dwm_dict'].has_key('week') and main_dict['type'] == 'week':
        dates = main_dict['dwm_dict']['week']
        for date_values in dates:
            dates_list.append(date_values[0] + ' to ' + date_values[-1])
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            occup_data = occupancy_data(prj_id, center, date_values, location, skill, disposition)
            occupa_week_name = str('week' + str(occupa_week_num))
            occupa_week_dt[occupa_week_name] = occup_data
            occupa_week_num = occupa_week_num + 1
        week_occupancy_data = prod_volume_week_util_headcount(week_names, occupa_week_dt, {})
        result['occupancy'] = [week_occupancy_data]
        final_values = week_occupancy_data.update({'name':'Occupancy'})
        result['date'] = dates_list
    else:
        for month_na,month_va in zip(main_dict['dwm_dict']['month']['month_names'],main_dict['dwm_dict']['month']['month_dates']):
            month_name = month_na
            month_dates = month_va
            dates_list.append(month_dates[0] + ' to ' + month_dates[-1])
            month_names.append(month_name)
            occup_data = occupancy_data(prj_id, center, month_dates, location, skill, disposition)
            occupa_week_dt[month_name] = occup_data
        month_occupa_data = prod_volume_week_util_headcount(month_names, occupa_week_dt, {})
        result['occupancy'] = [month_occupa_data]
        final_values = month_occupa_data.update({'name':'Occupancy'})
        result['date'] = dates_list
    return json_HttpResponse(result)


def agent_productivity_data(request):
    result, prod_week_dt = {}, {}
    new_date_list, dates_list, week_names = [], [], []
    month_names = []
    week_num, prod_week_num = 0, 0
    main_dict = data_dict(request.GET)
    prj_id = main_dict['pro_cen_mapping'][0][0]
    center = main_dict['pro_cen_mapping'][1][0]
    location = request.GET['location']
    skill = request.GET['skill']
    disposition = request.GET['disposition']
    if main_dict['dwm_dict'].has_key('day') and main_dict['type'] == 'day':
        dates = main_dict['dwm_dict']['day']
        for date in dates:
            common_prod_query = AgentPerformance.objects.filter(project = prj_id, center = center, date = date).values('agent').count()
            if common_prod_query > 0:
                new_date_list.append(date)
                result['date'] = new_date_list
        productivity_val = prod_data(prj_id, center, dates, location, skill, disposition)
        result['agent_productivity_data'] = [productivity_val]
        final_values = productivity_val.update({'name':'Productivity'})
    elif main_dict['dwm_dict'].has_key('week') and main_dict['type'] == 'week':
        dates = main_dict['dwm_dict']['week']
        for date_values in dates:
            dates_list.append(date_values[0] + ' to ' + date_values[-1])
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            productivity_val = prod_data(prj_id, center, date_values, location, skill, disposition)
            prod_week_name = str('week' + str(prod_week_num))
            prod_week_dt[prod_week_name] = productivity_val
            prod_week_num = prod_week_num + 1
        week_prod_data = prod_volume_week_util_headcount(week_names, prod_week_dt, {})
        result['agent_productivity_data'] = [week_prod_data]
        final_values = week_prod_data.update({'name':'Productivity'})
        result['date'] = dates_list
    else:
        for month_na,month_va in zip(main_dict['dwm_dict']['month']['month_names'],main_dict['dwm_dict']['month']['month_dates']):
            month_name = month_na
            month_dates = month_va
            dates_list.append(month_dates[0] + ' to ' + month_dates[-1])
            month_names.append(month_name)
            productivity_val = prod_data(prj_id, center, month_dates, location, skill, disposition)
            prod_week_dt[month_name] = productivity_val
        month_prod_data = prod_volume_week_util_headcount(month_names, prod_week_dt, {})
        result['agent_productivity_data'] = [month_prod_data]
        final_values = month_prod_data.update({'name':'Productivity'})
        result['date'] = dates_list
    return json_HttpResponse(result)

def agent_required(request):
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
    if main_dict['dwm_dict'].has_key('day') and main_dict['type'] == 'day':
        dates = main_dict['dwm_dict']['day']
        date_check = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates[0], dates[-1]]).values('date').annotate(total = count('skill')).order_by('date')
        values = OrderedDict(zip(map(lambda p: str(p['date']), date_check), map(lambda p: str(p['total']), date_check)))
        for date_key, date_value in values.iteritems():
            if date_value > 0:
                new_date_list.append(date_key)
                result['date'] = new_date_list
        skill_val = agent_deployed_call_data(prj_id, center, dates, skill, curr_loca, disposition)
        final_values = graph_format(skill_val)
        agents_data  = agent_graph_data(final_values)
        result['agent_required'] = agents_data
    elif main_dict['dwm_dict'].has_key('week') and main_dict['type'] == 'week':
        dates = main_dict['dwm_dict']['week']
        for date_values in dates:
            dates_list.append(date_values[0] + ' to ' + date_values[-1])
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            skill_details = agent_deployed_call_data(prj_id, center, date_values, skill, curr_loca, disposition)
            skill_week_name = str('week' + str(skill_week_num))
            skill_week_dt[skill_week_name] = skill_details
            skill_week_num = skill_week_num + 1
        final_skill_data = prod_volume_week(week_names, skill_week_dt, {})
        final_values = graph_format(final_skill_data)
        agents_data  = agent_graph_data(final_values)
        result['agent_required'] = agents_data
        result['date'] = dates_list
    else:
        for month_na,month_va in zip(main_dict['dwm_dict']['month']['month_names'],main_dict['dwm_dict']['month']['month_dates']):
            month_name = month_na
            month_dates = month_va
            dates_list.append(month_dates[0] + ' to ' + month_dates[-1])
            month_names.append(month_name)
            skill_details = agent_deployed_call_data(prj_id, center, month_dates, skill, curr_loca, disposition)
            skill_week_dt[month_name] = skill_details
        final_skill_data = prod_volume_week(month_names, skill_week_dt, {})
        final_values = graph_format(final_skill_data)
        agents_data  = agent_graph_data(final_values)
        result['agent_required'] = agents_data
        result['date'] = dates_list
    result['type'] = main_dict['type']
    return json_HttpResponse(result)
    

def agent_graph_data(agent_data):
    agent_list = []
    for type_val in agent_data:
        if type_val['name'] == 'Calls':
            type_val['type'] = 'column'
        if type_val['name'] == 'Logged in':
            type_val['type'] = 'spline'
            type_val['yAxis'] = 1
        if type_val['name'] == 'Required':
            type_val['type'] = 'spline'
            type_val['yAxis'] = 2
        agent_list.append(type_val)
    return agent_list


def location_value(location):
    if location == 'All':
        location = []
    else:
        location = [location]
    return {'location' : location}

def dispo_value(disposition):
    if disposition == 'All':
        disposition = []
    else:
        disposition = [disposition]
    return {'disposition' : disposition}

def skill_value(skill):
    if skill == 'All':
        skill = []
    else:
        skill = [skill]
    return {'skill' : skill}


def project_value(prj_type):
    if prj_type == 'inbound':
        table_name = 'InboundHourlyCall'
    else:
        table_name = 'OutboundHourlyCall'
    return table_name

def week_calculation(prj_id, center, dates, curr_loc, dispo_val, skill_val):
    date_list, week_names = [], []
    data_week_dt = {}
    week_num, data_week_num = 0, 0
    for date in dates:
        date_list.append(date[0] + ' to ' + date[-1])
        week_name = str('week' + str(week_num))
        week_names.append(week_name)
        week_num = week_num + 1
        data_week_name = str('week' + str(data_week_num))
        data_values = location_data(prj_id, center, date, curr_loc, dispo_val, skill_val)
        data_week_dt[data_week_name] = data_values
        data_week_num = data_week_num + 1
    final_data = prod_volume_week(week_names, data_week_dt, {})
    return final_data

def graph_format(week_data):
    return [{'name': item, 'data': week_data[item]} for item in week_data]
