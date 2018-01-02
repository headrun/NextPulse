from django.shortcuts import render
import xlrd
import datetime, time
from django.apps import apps
from voice_service.models import *
from api.models import *
from voice_service.voice_query_insertion import *
from voice_service.constrants import *
from voice_service.voice_widgets import *
from api.voice_widgets import *
from django.db.models import Count as count
from common.utils import getHttpResponse as json_HttpResponse

def location_data(prj_id, center, dates_list, location, skill, disposition):
    final_dict = {}
    if location == 'All' and disposition == 'All' and skill == 'All':
        location_query = InboundDaily.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]])
        location_filters = location_query.values_list('location', flat = True).distinct()
        for date in dates_list:
            date_check = InboundDaily.objects.filter(project = prj_id, center = center, date = date).values('location').count()
            if date_check > 0:
                for loc_name in location_filters:
                    loc_val = InboundDaily.objects.filter(project = prj_id, center = center, date = date, location = loc_name).\
                              aggregate(Sum('total_calls'))
                    value = common_value(loc_val)
                    if final_dict.has_key(loc_name):
                        final_dict[loc_name].append(value)
                    else:
                        final_dict[loc_name] = [value]
    elif location != 'All' and disposition == 'All' and skill == 'All':
        for date in dates_list:
            location_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date)
            date_check = location_query.values('location').count()
            if date_check > 0:
                loc_val = location_query.filter(location = location).aggregate(Sum('total_calls'))
                value = common_value(loc_val)
                if final_dict.has_key(location):
                    final_dict[location].append(value)
                else:
                    final_dict[location] = [value]
    elif location == 'All' and disposition == 'All' and skill != 'All':
        location_names = InboundDaily.objects.filter(\
                         project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], \
                         skill = skill).values_list('location', flat = True).distinct()
        for date in dates_list:
            for name in location_names:
                location_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date)
                date_check = location_query.values('location').count()
                if date_check > 0:
                    loc_val = location_query.filter(location = name, skill = skill).aggregate(Sum('total_calls'))
                    value = common_value(loc_val)
                    if final_dict.has_key(name):
                        final_dict[name].append(value)
                    else:
                        final_dict[name] = [value]
    elif location == 'All' and disposition != 'All' and skill == 'All':
        location_names = InboundHourlyCall.objects.filter(\
                         project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], \
                         disposition = disposition).values_list('location', flat = True).distinct()
        for date in dates_list:
            for name in location_names:
                location_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date)
                date_check = location_query.values('location').count()
                if date_check > 0:
                    loc_val = location_query.filter(location = name, disposition = disposition).aggregate(Sum('total_calls'))
                    value = common_value(loc_val)
                    if final_dict.has_key(name):
                        final_dict[name].append(value)
                    else:
                        final_dict[name] = [value]
    elif location != 'All' and disposition != 'All' and skill == 'All':
        for date in dates_list:
            location_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date)
            date_check = location_query.values('location').count()
            if date_check > 0:
                loc_val = location_query.filter(location = location, disposition = disposition).aggregate(Sum('total_calls'))
                value = common_value(loc_val)
                if final_dict.has_key(location):
                    final_dict[location].append(value)
                else:
                    final_dict[location] = [value]
    elif location != 'All' and disposition == 'All' and skill != 'All':
        for date in dates_list:
            location_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date)
            date_check = location_query.values('location').count()
            if date_check > 0:
                loc_val = location_query.filter(location = location, skill = skill).aggregate(Sum('total_calls'))
                value = common_value(loc_val)
                if final_dict.has_key(location):
                    final_dict[location].append(value)
                else:
                    final_dict[location] = [value]
    elif location == 'All' and disposition != 'All' and skill != 'All':
        location_names = InboundDaily.objects.filter(\
                         project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], \
                         disposition = disposition, skill = skill).values_list('location', flat = True).distinct()
        for date in dates_list:
            for name in location_names:
                location_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date)
                date_check = location_query.values('location').count()
                if date_check > 0:
                    loc_val = location_query.filter(location = name, skill = skill, disposition = disposition).\
                              aggregate(Sum('total_calls'))
                    value = common_value(loc_val)
                    if final_dict.has_key(name):
                        final_dict[name].append(value)
                    else:
                        final_dict[name] = [value]
    else:
        for date in dates_list:
            location_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date)
            date_check = location_query.values('location').count()
            if date_check > 0:
                loc_val = location_query.filter(location = location, skill = skill, disposition = disposition).\
                          aggregate(Sum('total_calls'))
                value = common_value(loc_val)
                if final_dict.has_key(location):
                    final_dict[location].append(value)
                else:
                    final_dict[location] = [value]
    return final_dict

def skill_data(prj_id, center, dates_list, location, skill, disposition):
    final_dict = {}
    if skill == 'All' and location == 'All' and disposition == 'All':
        skill_query = InboundDaily.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]])
        skill_filters = skill_query.values_list('skill', flat = True).distinct()
        for date in dates_list:
            date_check = InboundDaily.objects.filter(project = prj_id, center = center, date = date).values('skill').count()
            if date_check > 0:
                for skill_name in skill_filters:
                    skill_val = InboundDaily.objects.filter(\
                                project = prj_id, center = center, date = date, skill = skill_name).aggregate(Sum('total_calls'))
                    value = common_value(skill_val)
                    if final_dict.has_key(skill_name):
                        final_dict[skill_name].append(value)
                    else:
                        final_dict[skill_name] = [value]
    elif location == 'All' and disposition == 'All' and skill != 'All':
        for date in dates_list:
            skill_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date)
            date_check = skill_query.values('skill').count()
            if date_check > 0:
                skill_val = skill_query.filter(skill = skill).aggregate(Sum('total_calls'))
                value = common_value(skill_val)
                if final_dict.has_key(skill):
                    final_dict[skill].append(value)
                else:
                    final_dict[skill] = [value]
    elif location != 'All' and disposition == 'All' and skill == 'All':
        skill_names = InboundDaily.objects.filter(\
                      project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], \
                      location = location).values_list('skill', flat = True).distinct()
        for date in dates_list:
            for name in skill_names:
                skill_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date)
                date_check = skill_query.values('skill').count()
                if date_check > 0:
                    skill_val = skill_query.filter(skill = name, location = location).aggregate(Sum('total_calls'))
                    value = common_value(skill_val)
                    if final_dict.has_key(name):
                        final_dict[name].append(value)
                    else:
                        final_dict[name] = [value]
    elif location == 'All' and disposition != 'All' and skill == 'All':
        skill_names = InboundDaily.objects.filter(\
                      project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], \
                      disposition = disposition).values_list('skill', flat = True).distinct()
        for date in dates_list:
            for name in skill_names:
                skill_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date)
                date_check = skill_query.values('skill').count()
                if date_check > 0:
                    skill_val = skill_query.filter(skill = name, disposition = disposition).aggregate(Sum('total_calls'))
                    value = common_value(skill_val)
                    if final_dict.has_key(name):
                        final_dict[name].append(value)
                    else:
                        final_dict[name] = [value]
    elif location == 'All' and disposition != 'All' and skill != 'All':
        for date in dates_list:
            skill_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date)
            date_check = skill_query.values('skill').count()
            if date_check > 0:
                skill_val = skill_query.filter(skill = skill, disposition = disposition).aggregate(Sum('total_calls'))
                value = common_value(skill_val)
                if final_dict.has_key(skill):
                    final_dict[skill].append(value)
                else:
                    final_dict[skill] = [value]
    elif location != 'All' and disposition == 'All' and skill != 'All':
        for date in dates_list:
            skill_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date)
            date_check = skill_query.values('skill').count()
            if date_check > 0:
                skill_val = skill_query.filter(skill = skill, location = location).aggregate(Sum('total_calls'))
                value = common_value(skill_val)
                if final_dict.has_key(skill):
                    final_dict[skill].append(value)
                else:
                    final_dict[skill] = [value]
    elif location != 'All' and disposition != 'All' and skill == 'All':
        skill_names = InboundDaily.objects.filter(\
                        project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], \
                        disposition = disposition, location = location).values_list('skill', flat = True).distinct()
        for date in dates_list:
            for name in skill_names:
                skill_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date)
                date_check = skill_query.values('skill').count()
                if date_check > 0:
                    skill_val = skill_query.filter(skill = name, location = location, disposition = disposition).\
                                aggregate(Sum('total_calls'))
                    value = common_value(skill_val)
                    if final_dict.has_key(name):
                        final_dict[name].append(value)
                    else:
                        final_dict[name] = [value]
    else:
        for date in dates_list:
            skill_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date)
            date_check = skill_query.values('skill').count() 
            if date_check > 0:
                skill_val = skill_query.filter(skill = skill, location = location, disposition = disposition).\
                            aggregate(Sum('total_calls'))
                value = common_value(skill_val)
                if final_dict.has_key(skill):
                    final_dict[skill].append(value)
                else:
                    final_dict[skill] = [value]
    return final_dict

def disposition_data(prj_id, center, dates_list, location, skill, disposition):
    final_dict = {}
    if skill == 'All' and location == 'All' and disposition == 'All':
        dispo_query = InboundDaily.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]])
        dispo_filters = dispo_query.values_list('disposition', flat = True).distinct()
        for date in dates_list:
            date_check = InboundDaily.objects.filter(project = prj_id, center = center, date = date).values('disposition').count()
            if date_check > 0:
                for name in dispo_filters:
                    if name != '':
                        dispo_val = InboundDaily.objects.filter(\
                                    project = prj_id, center = center, date = date, disposition = name).aggregate(Sum('total_calls'))
                        value = common_value(dispo_val)
                        if final_dict.has_key(name):
                            final_dict[name].append(value)
                        else:
                            final_dict[name] = [value]
    elif location == 'All' and disposition != 'All' and skill == 'All':
        for date in dates_list:
            dispo_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date)
            date_check = dispo_query.values('disposition').count()
            if date_check > 0:
                dispo_val = dispo_query.filter(disposition = disposition).aggregate(Sum('total_calls'))
                value = common_value(dispo_val)
                if final_dict.has_key(disposition):
                    final_dict[disposition].append(value)
                else:
                    final_dict[disposition] = [value]
    elif location != 'All' and disposition == 'All' and skill == 'All':
        dispo_names = InboundDaily.objects.filter(\
                      project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], location = location).\
                      values_list('disposition', flat = True).distinct()  
        for date in dates_list:
            dispo_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date)
            date_check = dispo_query.values('disposition').count()
            for name in dispo_names: 
                if name != '':
                    dispo_val = dispo_query.filter(disposition = name, location = location).aggregate(Sum('total_calls'))
                    value = common_value(dispo_val)
                    if date_check > 0:
                        if final_dict.has_key(name):
                            final_dict[name].append(value)
                        else:
                            final_dict[name] = [value]   
    elif location == 'All' and disposition == 'All' and skill != 'All':
        dispo_names = InboundDaily.objects.filter(\
                        project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], \
                        skill = skill).values_list('disposition', flat = True).distinct()
        for date in dates_list:
            dispo_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date)
            date_check = dispo_query.values('disposition').count()
            for name in dispo_names:
                if name != '':
                    dispo_val = dispo_query.filter(disposition = name, skill = skill).aggregate(Sum('total_calls'))
                    value = common_value(dispo_val)
                    if date_check > 0:
                        if final_dict.has_key(name):
                            final_dict[name].append(value)
                        else:
                            final_dict[name] = [value]
    elif location == 'All' and disposition != 'All' and skill != 'All':
        for date in dates_list:
            dispo_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date)
            date_check = dispo_query.values('disposition').count()
            if date_check > 0:
                dispo_val = dispo_query.filter(disposition = disposition, skill = skill).aggregate(Sum('total_calls'))
                value = common_value(dispo_val)
                if final_dict.has_key(disposition):
                    final_dict[disposition].append(value)
                else:
                    final_dict[disposition] = [value]
    elif location != 'All' and disposition != 'All' and skill == 'All':
        for date in dates_list:
            dispo_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date)
            date_check = dispo_query.values('disposition').count()
            if date_check > 0:
                dispo_val = dispo_query.filter(disposition = disposition, location = location).aggregate(Sum('total_calls'))
                value = common_value(dispo_val)
                if final_dict.has_key(disposition):
                    final_dict[disposition].append(value)
                else:
                    final_dict[disposition] = [value]
    elif location != 'All' and disposition == 'All' and skill != 'All':
        dispo_names = InboundDaily.objects.filter(\
                        project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], \
                        skill = skill, location = location).values_list('disposition', flat = True).distinct()
        for date in dates_list:
            dispo_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date)
            date_check = dispo_query.values('disposition').count()
            for name in dispo_names:
                if name != '':
                    if date_check > 0:
                        dispo_val = dispo_query.filter(disposition = name, location = location, skill = skill).\
                                    aggregate(Sum('total_calls'))
                        value = common_value(dispo_val)
                        if final_dict.has_key(name):
                            final_dict[name].append(value)
                        else:
                            final_dict[name] = [value]
    else:
        for date in dates_list:
            dispo_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date)
            date_check = dispo_query.values('disposition').count()
            if date_check > 0:
                dispo_val = dispo_query.filter(disposition = disposition, location = location, skill = skill).\
                            aggregate(Sum('total_calls'))
                value = common_value(dispo_val)
                if final_dict.has_key(disposition):
                    final_dict[disposition].append(value)
                else:
                    final_dict[disposition] = [value]
    return final_dict

def call_status_data(prj_id, center, dates_list, location, skill, disposition):
    final_dict = {}
    ans_list, unans_list, perc_calls = [], [], []
    if skill == 'All' and location == 'All' and disposition == 'All':
        for date in dates_list:
            date_check = InboundDaily.objects.filter(project = prj_id, center = center, date = date)
            calls = date_check.aggregate(Sum('total_calls'))
            value1 = common_value(calls)
            ans_calls = date_check.aggregate(Sum('calls_answered'))
            value2 = ans_value(ans_calls)
            if calls > 0:
                unans_calls = value1 - value2
                ans_list.append(value2)
                unans_list.append(unans_calls)
                #precen_cal = percentage_calculation(value2, value1)
                #perc_calls.append(precen_cal)
        #final_dict['values'] = perc_calls
        final_dict['Answered'] = ans_list
        final_dict['UnAnswered'] = unans_list
    elif location != 'All' and disposition == 'All' and skill == 'All':
        for date in dates_list:
            inbnd_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date)
            date_check = inbnd_query.values('total_calls').count()
            if date_check > 0:
                call_query = inbnd_query.filter(location = location)
                calls = call_query.aggregate(Sum('total_calls'))
                value1 = common_value(calls)
                ans_calls = call_query.aggregate(Sum('calls_answered'))
                value2 = ans_value(ans_calls)
                unans_calls = value1 - value2
                ans_list.append(value2)
                unans_list.append(unans_calls)
        final_dict['Answered'] = ans_list
        final_dict['UnAnswered'] = unans_list    
    elif location == 'All' and disposition != 'All' and skill == 'All':
        for date in dates_list:
            inbnd_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date)
            date_check = inbnd_query.values('total_calls').count()
            if date_check > 0:
                call_query = inbnd_query.filter(disposition = disposition)
                calls = call_query.aggregate(Sum('total_calls'))
                ans_calls = call_query.aggregate(Sum('calls_answered'))
                value1 = common_value(calls)
                value2 = ans_value(ans_calls)
                unans_calls = value1 - value2
                ans_list.append(value2)
                unans_list.append(unans_calls)
        final_dict['Answered'] = ans_list
        final_dict['UnAnswered'] = unans_list
    elif location == 'All' and disposition == 'All' and skill != 'All':
        for date in dates_list:
            inbnd_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date)
            date_check = inbnd_query.values('total_calls').count()
            if date_check > 0:
                call_query = inbnd_query.filter(skill = skill)
                calls = call_query.aggregate(Sum('total_calls'))
                ans_calls = call_query.aggregate(Sum('calls_answered'))
                value1 = common_value(calls)
                value2 = ans_value(ans_calls)
                unans_calls = value1 - value2
                ans_list.append(value2)
                unans_list.append(unans_calls)
        final_dict['Answered'] = ans_list
        final_dict['UnAnswered'] = unans_list
    elif location != 'All' and disposition == 'All' and skill != 'All':
        for date in dates_list:
            inbnd_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date)
            date_check = inbnd_query.values('total_calls').count()
            if date_check > 0:
                call_query = inbnd_query.filter(skill = skill, location = location)
                calls = call_query.aggregate(Sum('total_calls'))
                ans_calls = call_query.aggregate(Sum('calls_answered'))
                value1 = common_value(calls)
                value2 = ans_value(ans_calls)
                unans_calls = value1 - value2
                ans_list.append(value2)
                unans_list.append(unans_calls)
        final_dict['Answered'] = ans_list
        final_dict['UnAnswered'] = unans_list
    elif location == 'All' and disposition != 'All' and skill != 'All':
        for date in dates_list:
            inbnd_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date)
            date_check = inbnd_query.values('total_calls').count()
            if date_check > 0:
                call_query = inbnd_query.filter(skill = skill, disposition = disposition)
                calls = call_query.aggregate(Sum('total_calls'))
                ans_calls = call_query.aggregate(Sum('calls_answered'))
                value1 = common_value(calls)
                value2 = ans_value(ans_calls)
                unans_calls = value1 - value2
                ans_list.append(value2)
                unans_list.append(unans_calls)
        final_dict['Answered'] = ans_list
        final_dict['UnAnswered'] = unans_list
    elif location != 'All' and disposition != 'All' and skill == 'All':
        for date in dates_list:
            inbnd_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date)
            date_check = inbnd_query.values('total_calls').count()
            if date_check > 0:
                call_query = inbnd_query.filter(location = location, disposition = disposition)
                calls = call_query.aggregate(Sum('total_calls'))
                ans_calls = call_query.aggregate(Sum('calls_answered'))
                value1 = common_value(calls)
                value2 = ans_value(ans_calls)
                unans_calls = value1 - value2
                ans_list.append(value2)   
                unans_list.append(unans_calls)
        final_dict['Answered'] = ans_list
        final_dict['UnAnswered'] = unans_list
    else:
        for date in dates_list:
            inbnd_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date)
            date_check = inbnd_query.values('total_calls').count()
            if date_check > 0:
                call_query = inbnd_query.filter(location = location, disposition = disposition, skill = skill)
                calls = call_query.aggregate(Sum('total_calls'))   
                ans_calls = call_query.aggregate(Sum('calls_answered'))
                calls = call_query.aggregate(Sum('total_calls'))
                ans_calls = call_query.aggregate(Sum('calls_answered'))
                unans_calls = value1 - value2
                ans_list.append(value2)
                unans_list.append(unans_calls)
        final_dict['Answered'] = ans_list
        final_dict['UnAnswered'] = unans_list
    return final_dict

def disposition_cate_data(prj_id, dates_list, table_name, location = {}, skill = {}, disposition = {}):
    final_dict = {}
    term = 'disposition'
    filter_parameters = create_filters([location, skill, disposition, prj_id, dates_list])
    if table_name == OutboundHourlyCall:
        table_name = OutboundDaily
    else:
        table_name = InboundDaily
    dispo_query = table_name.objects.filter(**filter_parameters).values(term).distinct().annotate(total = Sum('total_calls'))
    for data in dispo_query:
        if data['total'] > 0:
            if final_dict.has_key(data[term]):
                final_dict[data[term]].append(data['total'])
            else:
                final_dict[data[term]] = [data['total']]
    return final_dict


def outbnd_disposition_data(prj_id, center, dates, location, skill, disposition):
    final_dict = {}
    if disposition == 'All':
        outbnd_dispo_query = OutboundDaily.objects.filter(project = prj_id, center = center, date__range = [dates[0], dates[-1]])
        dispo_filters = outbnd_dispo_query.values_list('disposition', flat = True).distinct()
        for date in dates:
            date_check = OutboundDaily.objects.filter(project = prj_id, center = center, date = date).values('disposition').count()
            if date_check > 0:
                for name in dispo_filters:
                    if name != '':
                        outbnd_dispo_val = OutboundDaily.objects.filter(\
                                           project = prj_id, center = center, date = date, disposition = name).\
                                           aggregate(Sum('total_calls'))
                        value = common_value(outbnd_dispo_val)
                        if final_dict.has_key(name):
                            final_dict[name].append(value)
                        else:
                            final_dict[name] = [value]
    elif disposition != 'All':
        for date in dates:
            outbnd_dispo = OutboundDaily.objects.filter(project = prj_id, center = center, date = date)
            date_check = outbnd_dispo.values('disposition').count()
            if date_check > 0:
                outbnd_dispo_val = outbnd_dispo.filter(disposition = disposition).aggregate(Sum('total_calls'))
                value = common_value(outbnd_dispo_val)                
                if final_dict.has_key(disposition):
                    final_dict[disposition].append(value)
                else:
                    final_dict[disposition] = [value]
    else:
        return {}
    return final_dict

def agents_required_inbound(prj_id, center, dates, location, skill, disposition):
    final_dict = {}
    inbnd_calls_query = InboundDaily.objects.filter(project = prj_id, center = center, date__range = [dates[0], dates[-1]])
    inbnd_agents = inbnd_calls_query.values_list('agent').distinct()
    inbnd_skills = inbnd_calls_query.values_list('skill', flat = True).distinct()
    for date in dates:
        for skill in inbnd_skills:
            skill_agent_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date, skill = skill)
            total_calls = skill_agent_query.values('total_calls').count()
            inbnd_agents = skill_agent_query.values_list('agent', flat = True).distinct()
            for agent in inbnd_agents:
                login_hrs = AgentPerformance.objects.filter(project = prj_id, center = center, date = date, name = agent).\
                            values_list('login_duration', flat=True)                
    return final_dict

def common_outbnd_dispo_data(project, center, dates, disposition):
    final_dict = {} 
    dispo_list = []
    if disposition == 'All':
        outbnd_dispo_query = OutboundDaily.objects.filter(\
                                project = project, center = center, date__range = [dates[0], dates[-1]]).\
                                values_list('disposition', flat = True).distinct()
        for date in dates:
            values_list = []
            date_check = OutboundDaily.objects.filter(project = project, center = center, date = date).values('disposition').count()
            if date_check > 0:
                for dispo_name in outbnd_dispo_query:
                    if dispo_name != '':
                        outbnd_val = OutboundDaily.objects.filter(\
                                     project = project, center = center, date = date, disposition = dispo_name).\
                                     aggregate(Sum('total_calls'))
                        value = common_value(outbnd_val)
                        values_list.append(value)
                final_values = sum(values_list)
                dispo_list.append(final_values)
        final_dict['data'] = dispo_list
    else:
        final_dict = {}
    return final_dict

def outbnd_utilization_data(project, center, dates, location, disposition, skill):
    final_dict = {}
    utiliti_list = []
    if disposition == 'All':
        for date in dates:
            agent_values = AgentPerformance.objects.filter(project = project, center = center, date = date, call_type = 'Manual')
            agents_count = agent_values.values('agent').count()
            if agents_count > 0:
                login_time = agent_values.values_list('login_duration', flat = True)
                hold_time = agent_values.values_list('pause_time', flat = True)
                talk_time = agent_values.values_list('talk_time', flat = True)
                wrapup_time = get_avg_wrapup_time(project, center, date, call_type = 'Manual')
                if sum(login_time) > 0:
                    utili_val = (float(sum(hold_time) + sum(talk_time) + wrapup_time)/float(sum(login_time)))*100
                    utili_val = float('%.2f' % round(utili_val, 2))
                else:
                    utili_val = 0
                utiliti_list.append(utili_val)
            final_dict['data'] = utiliti_list
    else:
        final_dict = {}
    return final_dict

def inbnd_utilization_data(project, center, dates, location, disposition, skill):
    final_dict = {}
    utiliti_list = []
    if location == 'All' and skill == 'All' and disposition == 'All':
        for date in dates:
            agent_values = AgentPerformance.objects.filter(project = project, center = center, date = date, call_type = 'Inbound')
            agents_count = agent_values.values('agent').count()
            if agents_count > 0:
                login_time = agent_values.values_list('login_duration', flat = True)
                hold_time = agent_values.values_list('pause_time', flat = True)
                talk_time = agent_values.values_list('talk_time', flat = True)
                wrapup_time = get_avg_wrapup_time(project, center, date, call_type = 'Inbound')
                if sum(login_time) > 0:
                    utili_val = (float(sum(hold_time) + sum(talk_time) + wrapup_time)/float(sum(login_time)))*100
                    utili_val = float('%.2f' % round(utili_val, 2))
                else:
                    utili_val = 0
                utiliti_list.append(utili_val)
            final_dict['data'] = utiliti_list
    else:
        final_dict = {}
    return final_dict

def utilization_data(project, center, dates, location, skill, disposition):
    final_dict = {}  
    utiliti_list = []
    if location == 'All' and skill == 'All' and disposition == 'All':
        for date in dates:
            agent_values = AgentPerformance.objects.filter(project = project, center = center, date = date)
            agents_count = agent_values.values('agent').count()
            if agents_count > 0:
                login_time = agent_values.values_list('login_duration', flat = True)
                hold_time = agent_values.values_list('pause_time', flat = True)
                talk_time = agent_values.values_list('talk_time', flat = True)
                wrapup_time = get_avg_wrapup_time(project, center, date, call_type = '')
                if sum(login_time) > 0:
                    utili_val = (float(sum(hold_time) + sum(talk_time) + wrapup_time)/float(sum(login_time)))*100
                    utili_val = float('%.2f' % round(utili_val, 2))
                else:
                    utili_val = 0  
                utiliti_list.append(utili_val)
            final_dict['data'] = utiliti_list
    else:
        final_dict = {}
    return final_dict

def get_avg_wrapup_time(project, center, date, call_type):
    agents_list = []
    if call_type != '':
        agent_data = AgentPerformance.objects.filter(project = project, center = center, date = date, call_type = call_type)
    else:
        agent_data = AgentPerformance.objects.filter(project = project, center = center, date = date)
    agents_vals = agent_data.values('agent').count()
    agent_names = agent_data.values_list('agent', flat = True).distinct()
    if agents_vals > 0:
        wrap_time = agent_data.values_list('wrapup_time', flat = True)
        no_of_calls = agent_data.values_list('total_calls', flat = True)
        if sum(no_of_calls) > 0:
            time_per_agent = float(sum(wrap_time))/float(sum(no_of_calls))
        else:
            time_per_agent = 0
    return time_per_agent

def inbound_occupancy_data(project, center, dates, location, skill, disposition):
    final_dict = {}
    occupancy_list = []
    if location == 'All' and skill == 'All' and disposition == 'All':
        for date in dates:
            agent_values = AgentPerformance.objects.filter(project = project, center = center, date = date, call_type = 'Inbound')
            agents_count = agent_values.values('agent').count()
            if agents_count > 0:
                login_time = agent_values.values_list('login_duration', flat = True)
                hold_time = agent_values.values_list('pause_time', flat = True)
                talk_time = agent_values.values_list('talk_time', flat = True)
                idle_time = agent_values.values_list('idle_time', flat = True)
                wrapup_time = get_avg_wrapup_time(project, center, date, call_type = 'Inbound')
                if sum(login_time):
                    occupancy_val = (float(sum(hold_time) + sum(talk_time) + sum(idle_time) + wrapup_time)/float(sum(login_time)))*100
                    occupancy_val = float('%.2f' % round(occupancy_val, 2))
                else:
                    occupancy_val = 0
                occupancy_list.append(occupancy_val)
            final_dict['data'] = occupancy_list
    else:
        final_dict = {}
    return final_dict

def outbound_occupancy_data(project, center, dates, location, disposition, skill):
    final_dict = {}
    occupancy_list = []
    if disposition == 'All':
        for date in dates:
            agent_values = AgentPerformance.objects.filter(project = project, center = center, date = date, call_type = 'Manual')
            agents_count = agent_values.values('agent').count()
            if agents_count > 0:
                login_time = agent_values.values_list('login_duration', flat = True)
                hold_time = agent_values.values_list('pause_time', flat = True)
                talk_time = agent_values.values_list('talk_time', flat = True)
                idle_time = agent_values.values_list('idle_time', flat = True)
                wrapup_time = get_avg_wrapup_time(project, center, date, call_type = 'Manual')
                if sum(login_time) > 0:
                    occupancy_val = (float(sum(hold_time) + sum(talk_time) + sum(idle_time) + wrapup_time)/float(sum(login_time)))*100
                    occupancy_val = float('%.2f' % round(occupancy_val, 2))
                else:
                    occupancy_val = 0
                occupancy_list.append(occupancy_val)
            final_dict['data'] = occupancy_list
    else:
        final_dict = {}
    return final_dict

def occupancy_data(project, center, dates, location, skill, disposition):
    final_dict = {}
    occupancy_list = []
    if location == 'All' and skill == 'All' and disposition == 'All':
        for date in dates:
            agent_values = AgentPerformance.objects.filter(project = project, center = center, date = date)
            agents_count = agent_values.values('agent').count()
            if agents_count > 0:
                login_time = agent_values.values_list('login_duration', flat = True)
                hold_time = agent_values.values_list('pause_time', flat = True)
                talk_time = agent_values.values_list('talk_time', flat = True)
                idle_time = agent_values.values_list('idle_time', flat = True)
                wrapup_time = get_avg_wrapup_time(project, center, date, call_type = '')
                if sum(login_time):
                    occupancy_val = (float(sum(hold_time) + sum(talk_time) + sum(idle_time) + wrapup_time)/float(sum(login_time)))*100
                    occupancy_val = float('%.2f' % round(occupancy_val, 2))
                else:
                    occupancy_val = 0
                occupancy_list.append(occupancy_val)
            final_dict['data'] = occupancy_list
    else:
        final_dict = {}
    return final_dict

def outbound_productivity_data(project, center, dates, location, disposition, skill):
    final_dict = {}
    prod_list = []
    if disposition == 'All':
        for date in dates:
            agent_values = AgentPerformance.objects.filter(project = project, center = center, date = date, call_type = 'Manual')
            agents_count = agent_values.values('agent').count()
            if agents_count > 0:
                prod_val = get_prod_per_agent(project, center, date, call_type = 'Manual')
                prod_list.append(prod_val)
            final_dict['data'] = prod_list
    else:
        final_dict = {}
    return final_dict

def inbound_productivity_data(project, center, dates, location, disposition, skill):
    final_dict = {}
    prod_list = []
    if location == 'All' and skill == 'All' and disposition == 'All':
        for date in dates:
            agent_values = AgentPerformance.objects.filter(project = project, center = center, date = date, call_type = 'Inbound')
            agents_count = agent_values.values('agent').count()
            if agents_count > 0:
                prod_val = get_prod_per_agent(project, center, date, call_type = 'Inbound')
                prod_list.append(prod_val)
            final_dict['data'] = prod_list
    else:
        final_dict = {}
    return final_dict

def prod_data(project, center, dates, location, skill, disposition):
    final_dict = {}
    prod_list = []
    if location == 'All' and skill == 'All' and disposition == 'All':
        for date in dates:
            agent_values = AgentPerformance.objects.filter(project = project, center = center, date = date)
            agents_count = agent_values.values('agent').count()
            if agents_count > 0:
                prod_val = get_prod_per_agent(project, center, date, call_type = '')
                prod_list.append(prod_val)
            final_dict['data'] = prod_list
    else:
        final_dict = {}
    return final_dict

def get_prod_per_agent(project, center, date, call_type):
    agent_prod = []
    if call_type != '':
        agent_data = AgentPerformance.objects.filter(project = project, center = center, date = date, call_type = call_type)
    else:
        agent_data = AgentPerformance.objects.filter(project = project, center = center, date = date)
    agents_vals = agent_data.values('agent').count()
    agent_names = agent_data.values_list('agent', flat = True).distinct()
    if agents_vals > 0:
        for agent in agent_names:
            if call_type != '':
                agent_query = AgentPerformance.objects.filter(\
                              project = project, center = center, date = date, call_type = call_type, agent = agent)
            else:
                agent_query = AgentPerformance.objects.filter(project = project, center = center, date = date, agent = agent)
            login_time = agent_query.values_list('login_duration', flat = True)
            productivity_val = float(sum(login_time))/float(28800)
            agent_prod.append(productivity_val)    
    final_prod_agent = (float(sum(agent_prod))/float(len(agent_prod)))*100
    final_prod_agent = float('%.2f' % round(final_prod_agent, 2))
    return final_prod_agent

def agent_deployed_call_data(project, center, dates, skill, location, disposition):
    final_dict = {}
    calls_list, agents_list, req_list = [], [], [] 
    if skill == 'All' and location == 'All' and disposition == 'All':
        for date in dates:
            skill_data = InboundDaily.objects.filter(project = project, center = center, date = date)
            skill_calls = skill_data.aggregate(Sum('total_calls'))
            if skill_calls['total_calls__sum'] > 0:
                agent_count = skill_data.values('agent').count()
                agents_req = float(skill_calls['total_calls__sum'])/float(agent_count)
                fin_agents_val = float('%.2f' % round(agents_req, 2))
                calls_list.append(skill_calls['total_calls__sum'])
                agents_list.append(agent_count)
                req_list.append(fin_agents_val)
    elif skill != 'All' and location == 'All' and disposition == 'All':
        for date in dates:
            normal_query = InboundDaily.objects.filter(project = project, center = center, date = date)
            skill_data = InboundDaily.objects.filter(project = project, center = center, date = date, skill = skill)
            date_check = normal_query.values('skill').count()
            if date_check > 0:
                skill_calls = skill_data.aggregate(Sum('total_calls'))
                agent_count = skill_data.values('agent').count()
                if agent_count:
                    agents_req = float(skill_calls['total_calls__sum'])/float(agent_count)
                else:
                    agents_req = 0
                fin_agents_val = float('%.2f' % round(agents_req, 2))
                calls_list.append(skill_calls['total_calls__sum'])
                agents_list.append(agent_count)
                req_list.append(fin_agents_val)
    else:
        final_dict = {}
    final_dict['Calls'] = calls_list
    final_dict['Logged in'] = agents_list
    final_dict['Required'] = req_list
    return final_dict

def common_value(data):
    if data['total_calls__sum'] != None:
        value = data['total_calls__sum']
    else:
        value = 0
    return value

def ans_value(values):
    if values['calls_answered__sum'] != None:
        value = values['calls_answered__sum']
    else:
        value = 0
    return value

def percentage_calculation(ans_calls, total_calls):
    value = (float(ans_calls )/ total_calls) * 100
    final_value = float('%.2f' % round(value, 2))
    print ans_calls, total_calls, final_value
    return final_value
