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
    if main_dict['dwm_dict'].has_key('day') and main_dict['type'] == 'day':
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
        for date_vaulues in dates:
            dates_list.append(date_vaulues[0] + ' to ' + date_vaulues[-1])
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            location_details = location_data(prj_id, center, date_vaulues, curr_loc, dispo_val, skill_val)
            location_week_name = str('week' + str(location_week_num))
            loc_week_dt[location_week_name] = location_details
            location_week_num = location_week_num + 1
        final_location_data = prod_volume_week_util(prj_id, week_names, loc_week_dt, {}, 'week')
        result['location'] = final_location_data
        result['date'] = dates_list
    else:
        for month_na,month_va in zip(main_dict['dwm_dict']['month']['month_names'],main_dict['dwm_dict']['month']['month_dates']):
            month_name = month_na
            month_dates = month_va
            dates_list.append(month_dates[0] + ' to ' + month_dates[-1])
            month_names.append(month_name)
            location_details = location_data(prj_id, center, month_dates, curr_loc, dispo_val, skill_val)
            loc_week_dt[month_name] = location_details
        final_location_data = prod_volume_week_util(prj_id, month_names, loc_week_dt, {}, 'month')
        result['location'] = final_location_data
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
    if main_dict['dwm_dict'].has_key('day') and main_dict['type'] == 'day':
        dates = main_dict['dwm_dict']['day']
        date_check = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates[0], dates[-1]]).values('date').annotate(total = count('skill')).order_by('date')
        values = OrderedDict(zip(map(lambda p: str(p['date']), date_check), map(lambda p: str(p['total']), date_check)))
        for date_key, date_value in values.iteritems():
            if date_value > 0:
                new_date_list.append(date_key)
                result['date'] = new_date_list
        #result['skill'] = skill_data(prj_id, center, dates, skill, curr_loca, disposition)
        skill_val = skill_data(prj_id, center, dates, skill, curr_loca, disposition)
        result['skill'] = [{'name': item, 'data': skill_val[item]} for item in skill_val]
    elif main_dict['dwm_dict'].has_key('week') and main_dict['type'] == 'week':
        dates = main_dict['dwm_dict']['week']
        for date_vaulues in dates:
            dates_list.append(date_vaulues[0] + ' to ' + date_vaulues[-1])
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            skill_details = skill_data(prj_id, center, dates, skill, curr_loca, disposition)
            skill_week_name = str('week' + str(skill_week_num))
            skill_week_dt[skill_week_name] = skill_details
            skill_week_num = skill_week_num + 1
        final_skill_data = prod_volume_week_util(prj_id, week_names, skill_week_dt, {}, 'week')
        result['skill'] = final_skill_data
        result['date'] = dates_list
    else:
        for month_na,month_va in zip(main_dict['dwm_dict']['month']['month_names'],main_dict['dwm_dict']['month']['month_dates']):
            month_name = month_na
            month_dates = month_va
            dates_list.append(month_dates[0] + ' to ' + month_dates[-1])
            month_names.append(month_name)
            skill_details = skill_data(prj_id, center, dates, skill, curr_loca, disposition)
            skill_week_dt[month_name] = skill_details
        final_skill_data = prod_volume_week_util(prj_id, month_names, skill_week_dt, {}, 'month')
        result['skill'] = final_skill_data
        result['date'] = dates_list
    result['type'] = main_dict['type']
    return json_HttpResponse(result)


def disposition(request):
    result = {} 
    new_date_list = []
    main_dict = data_dict(request.GET)
    disposition = request.GET['disposition']
    curr_loca = request.GET['location']
    skill = request.GET['skill']
    prj_id = main_dict['pro_cen_mapping'][0][0]
    center = main_dict['pro_cen_mapping'][1][0]
    dates = main_dict['dwm_dict']['day']
    date_check = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates[0], dates[-1]]).values('date').annotate(total = count('disposition')).order_by('date')
    values = OrderedDict(zip(map(lambda p: str(p['date']), date_check), map(lambda p: str(p['total']), date_check)))
    for date_key, date_value in values.iteritems():
        if date_value > 0:
            new_date_list.append(date_key)
            result['date'] = new_date_list
    result['disposition'] = disposition_data(prj_id, center, dates, disposition, curr_loca, skill)
    return json_HttpResponse(result)


def call_status(request):
    result = {}
    new_date_list = []
    disposition = request.GET['disposition']
    curr_loca = request.GET['location']
    skill = request.GET['skill']
    main_dict = data_dict(request.GET)
    prj_id = main_dict['pro_cen_mapping'][0][0]
    center = main_dict['pro_cen_mapping'][1][0]
    dates = main_dict['dwm_dict']['day']
    date_check = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates[0], dates[-1]]).values('date').annotate(total = count('caller_no')).annotate(sta_total = count('status')).order_by('date')
    values = OrderedDict(zip(map(lambda p: str(p['date']), date_check), map(lambda p: str(p['total']), date_check)))
    for date_key, date_value in values.iteritems():
        if date_value > 0:
            new_date_list.append(date_key)
            result['date'] = new_date_list
    result['call_status'] = call_status_data(prj_id, center, dates, curr_loca, skill, disposition)
    return json_HttpResponse(result)


def cate_dispo_inbound(request):
    result = {}
    new_date_list = []
    curr_loca = request.GET['location']
    disposition = request.GET['disposition']
    skill = request.GET['skill']
    main_dict = data_dict(request.GET)
    prj_id = main_dict['pro_cen_mapping'][0][0]
    center = main_dict['pro_cen_mapping'][1][0]
    dates = main_dict['dwm_dict']['day']
    date_check = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates[0], dates[-1]]).values('date').annotate(total = count('disposition')).order_by('date')
    values = OrderedDict(zip(map(lambda p: str(p['date']), date_check), map(lambda p: str(p['total']), date_check)))
    for date_key, date_value in values.iteritems():
        if date_value > 0:
            new_date_list.append(date_key)
    result['cate_dispo_inbound'] = disposition_cate_data(prj_id, center, dates, disposition, curr_loca, skill)
    return json_HttpResponse(result)

