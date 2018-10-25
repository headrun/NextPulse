import datetime
from api.models import *
from api.commons import data_dict
from django.db.models import Max, Sum 
from api.weekly_graph import *
from voice_service.models import *
from voice_service.widgets import *
from common.utils import getHttpResponse as json_HttpResponse
from voice_service.voice_widgets import *


def get_params(variable):
    location    = variable.GET.get('location', '')
    skill       = variable.GET.get('skill', '')
    disposition = variable.GET.get('disposition', '')
    prj_type    = variable.GET.get('project_type', '')
    return location, skill, disposition, prj_type


def generate_data_common_for_all(request, field_name, function_name):
    "generates the common code for location, skill, disposition, outbound disposition and call status"

    result = {}
    new_date_list = []
    location, skill, disposition, table_type = get_params(request)
    data_values = data_dict(request.GET)
    project_id = data_values['pro_cen_mapping'][0][0]
    center_id = data_values['pro_cen_mapping'][1][0]
    table_name = InboundDaily
    result_name = field_name
    if field_name == 'outbound_disposition':
        table_name = OutboundDaily
        field_name = 'disposition'
        result_name = 'outbound_disposition'
    elif field_name == 'call_status':
        field_name = 'total_calls'
        result_name = 'call_status'
    if data_values['dwm_dict'].has_key('hour') and data_values['type'] == 'hour':
        dates = data_values['dates']
        location, skill, disposition, table_name = hour_parameters(location, skill, disposition, table_type)
        project = {'project': project_id}
        dates = {'date': dates}
        if result_name == 'call_status':
            field_name = 'status'
        result = get_hourly_sum(project, dates, table_name, location, skill, disposition, field_name)
    elif data_values['dwm_dict'].has_key('day') and data_values['type'] == 'day':
        dates = data_values['dwm_dict']['day']
        date_check = table_name.objects.filter(
            project=project_id, 
            center=center_id, 
            date__range=[dates[0], dates[-1]]
            ).values('date').annotate(
                total= count(field_name)
            ).order_by('date')
        values = OrderedDict(zip(map(lambda p: str(p['date']), date_check), map(lambda p: str(p['total']), date_check)))
        for date_key, date_value in values.iteritems():
            if date_value > 0:
                new_date_list.append(date_key)
                result['date'] = new_date_list
        data = function_name(project_id, center_id, dates, location, skill, disposition)        
        result[result_name] = graph_format(data)
    elif data_values['dwm_dict'].has_key('week') and data_values['type'] == 'week':
        dates = data_values['dwm_dict']['week']
        week_data = week_calculation(project_id, center_id, dates, location, skill, disposition, field_name)
        result[result_name] = graph_format(week_data)
        result['date'] = date_function(dates, data_values['type'])
    else:
        dates = data_values['dwm_dict']['month']
        month_data = month_calculation(project_id, center_id, dates, location, skill, disposition, field_name)
        result[result_name] = graph_format(month_data)
        result['date'] = date_function(dates, data_values['type'])
    result['type'] = data_values['type']
    return json_HttpResponse(result)


def location(request):
    name = 'location'
    function_name = location_data
    out_put_data = generate_data_common_for_all(request, name, function_name)
    return out_put_data
    

def skill(request):
    name = 'skill'
    function_name = skill_data
    out_put_data = generate_data_common_for_all(request, name, function_name)
    return out_put_data


def disposition(request):
    name = 'disposition'
    function_name = disposition_data
    out_put_data = generate_data_common_for_all(request, name, function_name)
    return out_put_data


def outbound_disposition(request):
    name = 'outbound_disposition'
    function_name = outbnd_disposition_data
    out_put_data = generate_data_common_for_all(request, name, function_name)
    return out_put_data


def call_status(request):
    name = 'call_status'
    function_name = call_status_data
    out_put_data = generate_data_common_for_all(request, name, function_name)
    return out_put_data


def get_data_related_to_agent_table(request, function_name, result_name, name):
    "generates the common code for productivity, utilization, occupancy"

    result = {}
    new_date_list = []
    data_values = data_dict(request.GET)
    project_id = data_values['pro_cen_mapping'][0][0]
    center_id = data_values['pro_cen_mapping'][1][0]
    location, skill, disposition, prj_type = get_params(request)
    if data_values['dwm_dict'].has_key('hour') and data_values['type'] == 'hour':
        result = {}
    elif data_values['dwm_dict'].has_key('day') and data_values['type'] == 'day':
        dates = data_values['dwm_dict']['day']
        for date in dates:
            date_check = AgentPerformance.objects.filter(\
                              project=project_id, center=center_id, date=date)\
                              .values('agent').count()
            if date_check > 0:
                new_date_list.append(date)
                result['date'] = new_date_list
        data = function_name(project_id, center_id, dates, location, disposition, skill)
        result[name] = [data]
        final_data = data.update({'name': result_name})
    elif data_values['dwm_dict'].has_key('week') and data_values['type'] == 'week':
        dates = data_values['dwm_dict']['week']
        final_week_data = week_calculation_days(project_id, center_id, dates, location, disposition, skill, name)
        result[name] = [final_week_data]
        final_values = final_week_data.update({'name': result_name})
        result['date'] = date_function(dates, data_values['type'])
    else:
        dates = data_values['dwm_dict']['month']
        final_month_data = month_calculation_days(project_id, center_id, dates, location, disposition, skill, name)
        result[name] = [final_month_data]
        final_values = final_month_data.update({'name': result_name})
        result['date'] = date_function(dates, data_values['type'])
    return json_HttpResponse(result)


def inbnd_occupancy(request):
    name = 'inbnd_occupancy'
    result_name = 'Inbound Occupancy'
    function_name = inbound_occupancy_data
    out_put_data = get_data_related_to_agent_table(request, function_name, result_name, name)
    return out_put_data


def outbnd_occupancy(request):
    name = 'outbnd_occupancy'
    result_name = 'Outbound Occupancy'
    function_name = outbound_occupancy_data
    out_put_data = get_data_related_to_agent_table(request, function_name, result_name, name)
    return out_put_data


def inbnd_utilization(request):
    name = 'inbnd_utilization'
    result_name = 'Inbound Utilization'
    function_name = inbnd_utilization_data
    out_put_data = get_data_related_to_agent_table(request, function_name, result_name, name)
    return out_put_data


def outbnd_utilization(request):
    name = 'outbnd_utilization'
    result_name = 'Outbound Utilization'
    function_name = outbnd_utilization_data
    out_put_data = get_data_related_to_agent_table(request, function_name, result_name, name)
    return out_put_data


def inbound_productivity(request):
    name = 'inbound_productivity'
    result_name = 'Intbound Productivity'
    function_name = inbound_productivity_data
    out_put_data = get_data_related_to_agent_table(request, function_name, result_name, name)
    return out_put_data


def outbound_productivity(request):
    name = 'outbound_productivity'
    result_name = 'Outbound Productivity'
    function_name = outbound_productivity_data
    out_put_data = get_data_related_to_agent_table(request, function_name, result_name, name)
    return out_put_data


def utilization(request):
    name = 'utilization'
    result_name = 'Utiliztion'
    function_name = utilization_data
    out_put_data = get_data_related_to_agent_table(request, function_name, result_name, name)
    return out_put_data


def occupancy(request):
    name = 'occupancy'
    result_name = 'Occupancy'
    function_name = occupancy_data
    out_put_data = get_data_related_to_agent_table(request, function_name, result_name, name)
    return out_put_data


def agent_productivity_data(request):
    name = 'agent_productivity_data'
    result_name = 'Productivity'
    function_name = prod_data
    out_put_data = get_data_related_to_agent_table(request, function_name, result_name, name)
    return out_put_data


def get_cate_disposition_data(request, result_name):
    "generates the code related to disposition category"

    result = {}
    new_date_list, dates_list, week_names = [], [], []
    month_names = []
    location, skill, disposition, prj_type = get_params(request)
    main_dict = data_dict(request.GET)
    project_id = main_dict['pro_cen_mapping'][0][0]
    center_id = main_dict['pro_cen_mapping'][1][0]
    project = {'project' : project_id}

    location, skill, disposition, table_name = hour_parameters(location, skill, disposition, prj_type)
    if main_dict['dwm_dict'].has_key('hour') and main_dict['type'] == 'hour':
        date = main_dict['dates']
        dates = {'date' : date}
        hourly_data = disposition_cate_data(project, dates, table_name, location, skill, disposition)
        result[result_name] = [{'name': item, 'y': hourly_data[item][0]} for item in hourly_data]
    elif main_dict['dwm_dict'].has_key('day') and main_dict['type'] == 'day':
        dates = main_dict['dwm_dict']['day']
        dates = {'date' : dates}
        daily_data = disposition_cate_data(project, dates, table_name, location, skill, disposition)
        result[result_name] = [{'name': item, 'y': daily_data[item][0]} for item in daily_data]
    elif main_dict['dwm_dict'].has_key('week') and main_dict['type'] == 'week':
        dates = main_dict['dwm_dict']['week']
        week_dates = []
        for date_values in dates:
            week_dates = week_dates + date_values
        date_vals = {'date' : week_dates}
        week_data = disposition_cate_data(project, date_vals, table_name, location, skill, disposition)
        result[result_name] = [{'name': item, 'y': week_data[item][0]} for item in week_data]
    else:
        month_dates = []
        dates = main_dict['dwm_dict']['month']['month_dates']
        for date_values in dates:
            month_dates = month_dates + date_values
        date_vals = {'date' : month_dates}
        month_data = disposition_cate_data(project, date_vals, table_name, location, skill, disposition)
        result[result_name] = [{'name': item, 'y': month_data[item][0]} for item in month_data]
    result['type'] = main_dict['type']
    return json_HttpResponse(result)


def cate_dispo_inbound(request):
    result_name = 'cate_dispo_inbound'
    out_put_data = get_cate_disposition_data(request, result_name)
    return out_put_data


def outbound_dispo_cate(request):
    result_name = 'outbound_dispo_cate'
    out_put_data = get_cate_disposition_data(request, result_name)
    return out_put_data


def outbnd_dispo_common(request):
    result = {}
    new_date_list = []
    main_dict = data_dict(request.GET)
    location, skill, disposition, prj_type = get_params(request)
    prj_id = main_dict['pro_cen_mapping'][0][0]
    center = main_dict['pro_cen_mapping'][1][0]
    name = 'outbnd_dispo_common'
    if main_dict['dwm_dict'].has_key('hour') and main_dict['type'] == 'hour':
        dates = main_dict['dates']
        location, skill, disposition, table_name = hour_parameters(location, skill, disposition, prj_type)
        project = {'project' : [prj_id]}
        dates = {'date' : dates}
        result = get_hourly_sum(project, dates, table_name, location, skill, disposition, name)
    elif main_dict['dwm_dict'].has_key('day') and main_dict['type'] == 'day':
        dates = main_dict['dwm_dict']['day']
        date_check = OutboundDaily.objects.filter(project = prj_id, center = center, date__range = [dates[0], dates[-1]])\
                     .values('date').annotate(total = count('disposition')).order_by('date')
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
        final_week_data = week_calculation(prj_id, center, dates, location, disposition, skill, name)
        result['outbnd_dispo_common'] = [final_week_data]
        final_values = final_week_data.update({'name':'Disposition'})
        result['date'] = date_function(dates, main_dict['type'])
    else:
        dates = main_dict['dwm_dict']['month']
        final_month_data = month_calculation(prj_id, center, dates, location, disposition, skill, name)
        result['outbnd_dispo_common'] = [final_month_data]
        final_values = final_month_data.update({'name':'Disposition'})
        result['date'] = date_function(dates, main_dict['type'])
    result['type'] = main_dict['type']
    return json_HttpResponse(result)


def agent_required(request):
    agent_data = {}
    main_dict = data_dict(request.GET)
    curr_loc, skill_val, dispo_val, prj_type = get_params(request)
    prj_id = main_dict['pro_cen_mapping'][0][0]
    center = main_dict['pro_cen_mapping'][1][0]
    location, skill, disposition, table_name = hour_parameters(curr_loc, skill_val, dispo_val, prj_type)
    project = {'project' : prj_id}
    if main_dict['dwm_dict'].has_key('hour') and main_dict['type'] == 'hour':
        date = main_dict['dates']
    elif main_dict['dwm_dict'].has_key('day') and main_dict['type'] == 'day':
        date = main_dict['dwm_dict']['day']
    elif main_dict['dwm_dict'].has_key('week') and main_dict['type'] == 'week':
        date_vals = main_dict['dwm_dict']['week']
        date = []
        for value in date_vals:
            date = date + value
    else:
        date_vals = main_dict['dwm_dict']['month']['month_dates']
        date = []
        for value in date_vals:
            date = date + value
    dates = {'date' : date}
    agent_data = actual_required_hourly(project, dates, table_name, location, skill, disposition)
    if agent_data:
        agent_data['date'] = agent_data['date']
        agent_data['agent_required'] = agent_graph_data(agent_data)
    return json_HttpResponse(agent_data)
   

def agent_graph_data(agent_data):
    agents_list = []
    for key, value in agent_data.iteritems():
        if key == 'agent_required':
            for value_val in value:
                if value_val['name'] == 'required_login':
                    value_val['type'] = 'spline'
                    value_val['yAxis'] = 2
                    value_val['name'] = 'Required'
                if value_val['name'] == 'actual_login':
                    value_val['type'] = 'spline'
                    value_val['name'] = 'Logged in'
                if value_val['name'] == 'total_calls':
                    value_val['type'] = 'column'
                    value_val['yAxis'] = 1
                    value_val['name'] = 'Calls'
                agents_list.append(value_val)
    return agents_list


def hour_parameters(cur_location, cur_skill, cur_dispo, prj_type):
    location = []
    skill = []
    dispo = []
    table_name = InboundHourlyCall
    if not cur_location == 'All':
        location = cur_location
    if not cur_skill == 'All':
        skill = cur_skill
    if not cur_dispo == 'All':
        dispo = cur_dispo
    if prj_type != 'inbound':
        table_name = OutboundHourlyCall

    return {'location' : location}, {'skill' : skill}, {'disposition' : dispo}, table_name


def week_calculation(prj_id, center, dates, location, skill, disposition, term):
    week_names = []
    data_week_dt = {}
    week_num, data_week_num = 0, 0
    for date in dates:
        week_name = str('week' + str(week_num))
        week_names.append(week_name)
        week_num = week_num + 1
        data_week_name = str('week' + str(data_week_num))
        if term == 'location':
            data_values = location_data(prj_id, center, date, location, skill, disposition)
        elif term == 'skill':
            data_values = skill_data(prj_id, center, date, location, skill, disposition)
        elif term == 'disposition':
            data_values = disposition_data(prj_id, center, date, location, skill, disposition)
        elif term == 'total_calls':
            data_values = call_status_data(prj_id, center, date, location, skill, disposition)
        elif term == 'outbound_disposition':
            data_values = outbnd_disposition_data(prj_id, center, date, location, skill, disposition)
        elif term == 'outbnd_dispo_common':
            data_values = common_outbnd_dispo_data(prj_id, center, date, disposition)
        data_week_dt[data_week_name] = data_values
        data_week_num = data_week_num + 1
    final_data = prod_volume_week(week_names, data_week_dt, {})
    return final_data

def month_calculation(prj_id, center, dates, location, skill, disposition, term):    
    month_names = []
    month_dict = {}
    for month_na,month_va in zip(dates['month_names'],dates['month_dates']):
            month_name = month_na
            month_dates = month_va
            month_names.append(month_name)
            if term == 'location':
                data_values = location_data(prj_id, center, month_dates, location, skill, disposition)
            elif term == 'skill':
                data_values = skill_data(prj_id, center, month_dates, location, skill, disposition)
            elif term == 'disposition':
                data_values = disposition_data(prj_id, center, month_dates, location, skill, disposition)
            elif term == 'total_calls':
                data_values = call_status_data(prj_id, center, month_dates, location, skill, disposition)
            elif term == 'outbound_disposition':
                data_values = outbnd_disposition_data(prj_id, center, month_dates, location, skill, disposition)
            elif term == 'outbnd_dispo_common':
                data_values = common_outbnd_dispo_data(prj_id, center, month_dates, disposition)
            month_dict[month_name] = data_values
    final_data = prod_volume_week(month_names, month_dict, {})
    return final_data 

def week_calculation_days(prj_id, center, dates, location, disposition, skill, term):
    week_names = []
    data_week_dt = {}
    week_num, data_week_num = 0, 0
    for date in dates:
        week_name = str('week' + str(week_num))
        week_names.append(week_name)
        week_num = week_num + 1
        data_week_name = str('week' + str(data_week_num))
        if term == 'inbnd_utilization':
            data_values = inbnd_utilization_data(prj_id, center, date, location, skill, disposition)
        elif term == 'inbnd_occupancy':
            data_values = inbound_occupancy_data(prj_id, center, date, location, skill, disposition)
        elif term == 'inbound_productivity':
            data_values = inbound_productivity_data(prj_id, center, date, location, skill, disposition)
        elif term == 'utilization':
            data_values = utilization_data(prj_id, center, date, location, skill, disposition)
        elif term == 'occupancy':
            data_values = occupancy_data(prj_id, center, date, location, skill, disposition)
        elif term == 'agent_productivity_data':
            data_values = prod_data(prj_id, center, date, location, skill, disposition)
        elif term == 'outbnd_utilization':
            data_values = outbnd_utilization_data(prj_id, center, date, location, skill, disposition)
        elif term == 'outbnd_occupancy':
            data_values = outbound_occupancy_data(prj_id, center, date, location, skill, disposition)
        elif term == 'outbound_productivity':
            data_values = outbound_productivity_data(prj_id, center, date, location, skill, disposition)
        data_week_dt[data_week_name] = data_values
        data_week_num = data_week_num + 1
    final_data = prod_volume_week_util_headcount(week_names, data_week_dt, {})
    return final_data

def month_calculation_days(prj_id, center, dates, location, disposition, skill, term):
    month_names = []
    month_dict = {}
    for month_na,month_va in zip(dates['month_names'],dates['month_dates']):
        month_name = month_na
        month_dates = month_va
        month_names.append(month_name)
        if term == 'inbnd_utilization':
            data_values = inbnd_utilization_data(prj_id, center, month_dates, location, skill, disposition)
        elif term == 'inbnd_occupancy':
            data_values = inbound_occupancy_data(prj_id, center, month_dates, location, skill, disposition)
        elif term == 'inbound_productivity':
            data_values = inbound_productivity_data(prj_id, center, month_dates, location, skill, disposition)
        elif term == 'utilization':
            data_values = utilization_data(prj_id, center, month_dates, location, skill, disposition)
        elif term == 'occupancy':
            data_values = occupancy_data(prj_id, center, month_dates, location, skill, disposition)
        elif term == 'agent_productivity_data':
            data_values = prod_data(prj_id, center, month_dates, location, skill, disposition)
        elif term == 'outbnd_utilization':
            data_values = outbnd_utilization_data(prj_id, center, month_dates, location, skill, disposition)
        elif term == 'outbnd_occupancy':
            data_values = outbound_occupancy_data(prj_id, center, month_dates, location, skill, disposition)
        elif term == 'outbound_productivity':
            data_values = outbound_productivity_data(prj_id, center, month_dates, location, skill, disposition)
        month_dict[month_name] = data_values
    final_data = prod_volume_week_util_headcount(month_names, month_dict, {})
    return final_data


def date_function(dates, date_type):
    dates_list = []
    if date_type == 'week':
        for date in dates:
            dates_list.append(date[0] + ' to ' + date[-1])
    else:
        for month_na,month_va in zip(dates['month_names'],dates['month_dates']):
            month_dates = month_va
            dates_list.append(month_dates[0] + ' to ' + month_dates[-1])
    return dates_list


def graph_format(week_data):
    return [{'name': item, 'data': week_data[item]} for item in week_data]
