from django.shortcuts import render
import xlrd
import datetime, time
from django.apps import apps
from voice_service.models import *
from api.models import *
from api.redis_operations import redis_insert
from api.basics import *
from api.uploads import *
from api.utils import *
from api.query_generations import *
from voice_service.voice_query_insertion import *
from voice_service.constrants import *
from api.voice_widgets import *
from xlrd import open_workbook
from api.commons import data_dict
from django.db.models import Count as count
from common.utils import getHttpResponse as json_HttpResponse

def location_data(prj_id, center, dates_list, location, disposition, skill):
    final_dict = {}
    if location == 'All' and disposition == 'All' and skill == 'All':
        location_query = InboundDaily.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]])
        location_filters = location_query.values_list('location', flat = True).distinct()
        for date in dates_list:
            date_check = InboundDaily.objects.filter(project = prj_id, center = center, date = date).values('location').count()
            if date_check > 0:
                for loc_name in location_filters:
                    if '->' not in loc_name:
                        loc_val = InboundDaily.objects.filter(project = prj_id, center = center, date = date, location = loc_name).count()
                        if final_dict.has_key(loc_name):
                            final_dict[loc_name].append(loc_val)
                        else:
                            final_dict[loc_name] = [loc_val]
    elif location != 'All' and disposition == 'All' and skill == 'All':
        for date in dates_list:
            loc_val = InboundDaily.objects.filter(project = prj_id, center = center, date = date, location = location).count()
            if loc_val > 0:
                if final_dict.has_key(location):
                    final_dict[location].append(loc_val)
                else:
                    final_dict[location] = [loc_val]
    elif location == 'All' and disposition == 'All' and skill != 'All':
        location_names = InboundDaily.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], skill = skill).values_list('location', flat = True).distinct()
        for date in dates_list:
            for name in location_names:
                if '->' not in name:
                    loc_val = InboundDaily.objects.filter(project = prj_id, center = center, date = date, skill = skill, location = name).count()
                    if loc_val > 0:
                        if final_dict.has_key(name):
                            final_dict[name].append(loc_val)
                        else:
                            final_dict[name] = [loc_val]
    elif location == 'All' and disposition != 'All' and skill == 'All':
        location_names = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], disposition = disposition).values_list('location', flat = True).distinct()
        for date in dates_list:
            for name in location_names:
                if '->' not in name:
                    loc_val = InboundDaily.objects.filter(project = prj_id, center = center, date = date, disposition = disposition, location = name).count()
                    if loc_val > 0:
                        if final_dict.has_key(name):
                            final_dict[name].append(loc_val)
                        else:
                            final_dict[name] = [loc_val]
    elif location != 'All' and disposition != 'All' and skill == 'All':
        for date in dates_list:
            loc_val = InboundDaily.objects.filter(project = prj_id, center = center, date = date, location = location, disposition = disposition).count()
            if loc_val > 0:
                if final_dict.has_key(location):
                    final_dict[location].append(loc_val)
                else:
                    final_dict[location] = [loc_val]
    elif location != 'All' and disposition == 'All' and skill != 'All':
        for date in dates_list:
            loc_val = InboundDaily.objects.filter(project = prj_id, center = center, date = date, location = location, skill = skill).count()
            if loc_val > 0:
                if final_dict.has_key(location):
                    final_dict[location].append(loc_val)
                else:
                    final_dict[location] = [loc_val]
    elif location == 'All' and disposition != 'All' and skill != 'All':
        location_names = InboundDaily.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], disposition = disposition, skill = skill).values_list('location', flat = True).distinct()
        for date in dates_list:
            for name in location_names:
                if '->' not in name:
                    loc_val = InboundDaily.objects.filter(project = prj_id, center = center, date = date, disposition = disposition, skill = skill, location = name).count()
                    if loc_val > 0:
                        if final_dict.has_key(name):
                            final_dict[name].append(loc_val)
                        else:
                            final_dict[name] = [loc_val]
    else:
        for date in dates_list:
            loc_val = InboundDaily.objects.filter(project = prj_id, center = center, date = date, location = location, disposition = disposition, skill = skill).count()
            if loc_val > 0:
                if final_dict.has_key(location):
                    final_dict[location].append(loc_val)
                else:
                    final_dict[location] = [loc_val]
    return final_dict

def skill_data(prj_id, center, dates_list, skill, location, disposition):
    final_dict = {}
    if skill == 'All' and location == 'All' and disposition == 'All':
        skill_query = InboundDaily.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]])
        skill_filters = skill_query.values_list('skill', flat = True).distinct()
        for date in dates_list:
            date_check = InboundDaily.objects.filter(project = prj_id, center = center, date = date).values('skill').count()
            if date_check > 0:
                for skill_name in skill_filters:
                    if '->' not in skill_name:
                        skill_val = InboundDaily.objects.filter(project = prj_id, center = center, date = date, skill = skill_name).count()
                        if final_dict.has_key(skill_name):
                            final_dict[skill_name].append(skill_val)
                        else:
                            final_dict[skill_name] = [skill_val]
    elif location == 'All' and disposition == 'All' and skill != 'All':
        for date in dates_list:
            skill_val = InboundDaily.objects.filter(project = prj_id, center = center, date = date, skill = skill).count()
            if skill_val > 0:
                if final_dict.has_key(skill):
                    final_dict[skill].append(skill_val)
                else:
                    final_dict[skill] = [skill_val]
    elif location != 'All' and disposition == 'All' and skill == 'All':
        skill_names = InboundDaily.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], location = location).values_list('skill', flat = True).distinct()
        for date in dates_list:
            for name in skill_names:
                if '->' not in name:
                    skill_val = InboundDaily.objects.filter(project = prj_id, center = center, date = date, skill = name, location = location).count()
                    if skill_val > 0:
                        if final_dict.has_key(name):
                            final_dict[name].append(skill_val)
                        else:
                            final_dict[name] = [skill_val]
    elif location == 'All' and disposition != 'All' and skill == 'All':
        skill_names = InboundDaily.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], disposition = disposition).values_list('skill', flat = True).distinct()
        for date in dates_list:
            for name in skill_names:
                if '->' not in name:
                    skill_val = InboundDaily.objects.filter(project = prj_id, center = center, date = date, disposition = disposition, skill = name).count()
                    if skill_val > 0:
                        if final_dict.has_key(name):
                            final_dict[name].append(skill_val)
                        else:
                            final_dict[name] = [skill_val]
    elif location == 'All' and disposition != 'All' and skill != 'All':
        for date in dates_list:
            skill_val = InboundDaily.objects.filter(project = prj_id, center = center, date = date, skill = skill, disposition = disposition).count()
            if skill_val > 0:
                if final_dict.has_key(skill):
                    final_dict[skill].append(skill_val)
                else:
                    final_dict[skill] = [skill_val]
    elif location != 'All' and disposition == 'All' and skill != 'All':
        for date in dates_list:
            skill_val = InboundDaily.objects.filter(project = prj_id, center = center, date = date, location = location, skill = skill).count()
            if skill_val > 0:
                if final_dict.has_key(skill):
                    final_dict[skill].append(skill_val)
                else:
                    final_dict[skill] = [skill_val]
    elif location != 'All' and disposition != 'All' and skill == 'All':
        skill_names = InboundDaily.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], disposition = disposition, location = location).values_list('skill', flat = True).distinct()
        for date in dates_list:
            for name in skill_names:
                if '->' not in name:
                    skill_val = InboundDaily.objects.filter(project = prj_id, center = center, date = date, disposition = disposition, skill = name, location = location).count()
                    if skill_val > 0:
                        if final_dict.has_key(name):
                            final_dict[name].append(skill_val)
                        else:
                            final_dict[name] = [skill_val]

    else:
        for date in dates_list:
            skill_val = InboundDaily.objects.filter(project = prj_id, center = center, date = date, location = location, disposition = disposition, skill = skill).count() 
            if skill_val > 0:
                if final_dict.has_key(skill):
                    final_dict[skill].append(skill_val)
                else:
                    final_dict[skill] = [skill_val]
    return final_dict

def disposition_data(prj_id, center, dates_list, disposition, location, skill):
    final_dict = {}
    if skill == 'All' and location == 'All' and disposition == 'All':
        dispo_query = InboundDaily.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]])
        dispo_filters = dispo_query.values_list('disposition', flat = True).distinct()
        for date in dates_list:
            date_check = InboundDaily.objects.filter(project = prj_id, center = center, date = date).values('disposition').count()
            if date_check > 0:
                for name in dispo_filters:
                    if '->' not in name:
                        dispo_val = InboundDaily.objects.filter(project = prj_id, center = center, date = date, disposition = name).count()
                        if final_dict.has_key(name):
                            final_dict[name].append(dispo_val)
                        else:
                            final_dict[name] = [dispo_val]
    elif location == 'All' and disposition != 'All' and skill == 'All':
        for date in dates_list:
            dispo_val = InboundDaily.objects.filter(project = prj_id, center = center, date = date, disposition = disposition).count()
            if dispo_val > 0:
                if final_dict.has_key(disposition):
                    final_dict[disposition].append(dispo_val)
                else:
                    final_dict[disposition] = [dispo_val]
    elif location != 'All' and disposition == 'All' and skill == 'All':
        dispo_names = InboundDaily.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], location = location).values_list('disposition', flat = True).distinct()  
        for date in dates_list:
            for name in dispo_names: 
                if '->' not in name:
                    dispo_val = InboundDaily.objects.filter(project = prj_id, center = center, date = date, disposition = name, location = location).count()
                    if dispo_val > 0:
                        if final_dict.has_key(name):
                            final_dict[name].append(dispo_val)
                        else:
                            final_dict[name] = [dispo_val]   

    elif location == 'All' and disposition == 'All' and skill != 'All':
        dispo_names = InboundDaily.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], skill = skill).values_list('disposition', flat = True).distinct()
        for date in dates_list:
            for name in dispo_names:
                if '->' not in name:
                    dispo_val = InboundDaily.objects.filter(project = prj_id, center = center, date = date, skill = skill, disposition = name).count()
                    if dispo_val > 0:
                        if final_dict.has_key(name):
                            final_dict[name].append(dispo_val)
                        else:
                            final_dict[name] = [dispo_val]

    elif location == 'All' and disposition != 'All' and skill != 'All':
        for date in dates_list:
            dispo_val = InboundDaily.objects.filter(project = prj_id, center = center, date = date, skill = skill, disposition = disposition).count() 
            if dispo_val > 0:
                if final_dict.has_key(disposition):
                    final_dict[disposition].append(dispo_val)
                else:
                    final_dict[disposition] = [dispo_val]
    elif location != 'All' and disposition != 'All' and skill == 'All':
        for date in dates_list:
            dispo_val = InboundDaily.objects.filter(project = prj_id, center = center, date = date, location = location, disposition = disposition).count()
            if dispo_val > 0:
                if final_dict.has_key(disposition):
                    final_dict[disposition].append(dispo_val)
                else:
                    final_dict[disposition] = [dispo_val]

    elif location != 'All' and disposition == 'All' and skill != 'All':
        dispo_names = InboundDaily.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], skill = skill, location = location).values_list('disposition', flat = True).distinct()
        for date in dates_list:
            for name in dispo_names:
                if '->' not in name:
                    dispo_val = InboundDaily.objects.filter(project = prj_id, center = center, date = date, disposition = name, skill = skill, location = location).count()
                    if dispo_val > 0:
                        if final_dict.has_key(name):
                            final_dict[name].append(dispo_val)
                        else:
                            final_dict[name] = [dispo_val]
    else:
        for date in dates_list:
            dispo_val = InboundDaily.objects.filter(project = prj_id, center = center, date = date, location = location, disposition = disposition, skill = skill).count()
            if dispo_val > 0:
                if final_dict.has_key(disposition):
                    final_dict[disposition].append(dispo_val)
                else:
                    final_dict[disposition] = [dispo_val]
    return final_dict

def call_status_data(prj_id, center, dates_list, location, skill, disposition):
    final_dict = {}
    if skill == 'All' and location == 'All' and disposition == 'All':
        call_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]])
        call_filters = call_query.values_list('status', flat = True).distinct()
        for date in dates_list:
            date_check = InboundHourlyCall.objects.filter(project = prj_id, center = center, date = date).values('status').count()
            if date_check > 0:
                for name in call_filters:
                    if '->' not in name:
                        call_val = InboundHourlyCall.objects.filter(project = prj_id, center = center, date = date, status = name).count()
                        if final_dict.has_key(name):
                            final_dict[name].append(call_val)
                        else:
                            final_dict[name] = [call_val]
    elif location != 'All' and disposition == 'All' and skill == 'All':
        call_status = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], location = location).values_list('status', flat = True).distinct()
        for date in dates_list:
            for name in call_status: 
                if '->' not in name:
                    status_val = InboundHourlyCall.objects.filter(project = prj_id, center = center, date = date, status = name, location = location).count()  
                    if status_val > 0:
                        if final_dict.has_key(name):
                            final_dict[name].append(status_val)
                        else:
                            final_dict[name] = [status_val]
    
    elif location == 'All' and disposition != 'All' and skill == 'All':
        call_status = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], disposition = disposition).values_list('status', flat = True).distinct()
        for date in dates_list:
            for name in call_status:
                if '->' not in name:
                   status_val = InboundHourlyCall.objects.filter(project = prj_id, center = center, date = date, disposition = disposition, status = name).count()  
                   if status_val > 0:
                       if final_dict.has_key(name):
                           final_dict[name].append(status_val)
                       else:
                           final_dict[name] = [status_val]

    elif location == 'All' and disposition == 'All' and skill != 'All':
        call_status = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], skill = skill).values_list('status', flat = True).distinct()
        for date in dates_list:
            for name in call_status:
                if '->' not in name:
                    status_val = InboundHourlyCall.objects.filter(project = prj_id, center = center, date = date, skill = skill, status = name).count()
                    if status_val > 0:
                        if final_dict.has_key(name):
                            final_dict[name].append(status_val)
                        else:
                            final_dict[name] = [status_val]

    elif location != 'All' and disposition == 'All' and skill != 'All':
        call_status = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], skill = skill, location = location).values_list('status', flat = True).distinct()
        for date in dates_list:
            for name in call_status:
                if '->' not in name:
                    status_val = InboundHourlyCall.objects.filter(project = prj_id, center = center, date = date, status = name, skill = skill, location = location).count()
                    if status_val > 0:
                        if final_dict.has_key(name):
                            final_dict[name].append(status_val)
                        else:
                            final_dict[name] = [status_val]

    elif location == 'All' and disposition != 'All' and skill != 'All':
        call_status = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], disposition = disposition, skill = skill).values_list('status', flat = True).distinct()
        for date in dates_list:
            for name in call_status:
                if '->' not in name:
                    status_val = InboundHourlyCall.objects.filter(project = prj_id, center = center, date = date, disposition = disposition, skill = skill, status = name).count()
                    if status_val > 0:
                        if final_dict.has_key(name):
                            final_dict[name].append(status_val)
                        else:
                            final_dict[name] = [status_val]

    elif location != 'All' and disposition != 'All' and skill == 'All':
        call_status = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], disposition = disposition, location = location).values_list('status', flat = True).distinct()
        for date in dates_list:
            for name in call_status:
                if '->' not in name:
                    status_val = InboundHourlyCall.objects.filter(project = prj_id, center = center, date = date, disposition = disposition, status = name, location = location).count()
                    if status_val > 0:
                        if final_dict.has_key(name):
                            final_dict[name].append(status_val)
                        else:
                            final_dict[name] = [status_val] 
    else:
        call_status = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], disposition = disposition, location = location, skill = skill).values_list('status', flat = True).distinct()
        for date in dates_list:
            for name in call_status:
                if '->' not in name:
                    status_val = InboundHourlyCall.objects.filter(project = prj_id, center = center, date = date, location = location, disposition = disposition, skill = skill, status = name).count()
                    if status_val > 0:
                        if final_dict.has_key(name):
                            final_dict[name].append(status_val)
                        else:
                            final_dict[name] = [status_val]
    return final_dict

def disposition_cate_data(prj_id, center, dates_list, disposition, location, skill):
    final_dict = {}
    if location == 'All' and skill == 'All' and disposition == 'All':
        dispo_query = InboundDaily.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]]).values('disposition').distinct().annotate(total = count('disposition'))
    elif disposition != 'All' and skill == 'All' and location == 'All':
        dispo_query = InboundDaily.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], disposition = disposition).values('disposition').distinct().annotate(total = count('disposition'))
    elif disposition == 'All' and skill != 'All' and location == 'All':
        dispo_query = InboundDaily.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], skill = skill).values('disposition').distinct().annotate(total = count('disposition'))
    elif disposition == 'All' and skill == 'All' and location != 'All':
        dispo_query = InboundDaily.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], location = location).values('disposition').distinct().annotate(total = count('disposition'))
    elif disposition != 'All' and skill != 'All' and location == 'All':
        dispo_query = InboundDaily.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], skill = skill, disposition = disposition).values('disposition').distinct().annotate(total = count('disposition'))
    elif disposition == 'All' and skill != 'All' and location != 'All':
        dispo_query = InboundDaily.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], skill = skill, location = location).values('disposition').distinct().annotate(total = count('disposition'))
    elif disposition != 'All' and skill != 'All' and location == 'All':
        dispo_query  = InboundDaily.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], skill = skill, disposition = disposition).values('disposition').distinct().annotate(total = count('disposition'))
    elif disposition != 'All' and skill != 'All' and location != 'All':
        dispo_query = InboundDaily.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], skill = skill, disposition = disposition, location = location).values('disposition').distinct().annotate(total = count('disposition')) 
    else:
        return []
    for data in dispo_query:
        if data['total'] > 0:
            if '->' not in data['disposition']:
                if final_dict.has_key(data['disposition']):
                    final_dict[data['disposition']].append(data['total'])
                else:
                    final_dict[data['disposition']] = [data['total']]
    return final_dict


def dispo_outbound_cate_data(prj_id, center, dates_list, disposition):
    final_dict = {}
    if disposition == 'All':
        outbnd_dispo_cate_query = OutboundDaily.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]]).values('disposition').distinct().annotate(total = count('disposition'))
    elif disposition != 'All':
        outbnd_dispo_cate_query = OutboundDaily.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]],disposition = disposition).values('disposition').distinct().annotate(total = count('disposition'))
    else:
        return []
    for value in outbnd_dispo_cate_query:
        if value['total'] > 0:
            if ('->' not in value['disposition']) and (value['disposition'] != ''):
                if final_dict.has_key(value['disposition']):
                    final_dict[value['disposition']].append(value['total'])
                else:
                    final_dict[value['disposition']] = [value['total']]
    return final_dict


def hourly_location_data(prj_id, center, dates, hours, location, disposition, skill):
    final_dict = {}
    for date in dates:
        for hour in hours:
            hr = hour*60*60 
            hr1 = (hour + 1)*60*60
            final_hour1 = date + ' ' + time.strftime('%H:%M:%S', time.gmtime(hr1))       
            final_hour = date + ' ' + time.strftime('%H:%M:%S', time.gmtime(hr))
            if location == 'All' and disposition == 'All' and skill == 'All':
                location_hr_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1).values('location').distinct().annotate(total = count('location'))
            elif location != 'All' and disposition == 'All' and skill == 'All':
                location_hr_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1, location = location).values('location').distinct().annotate(total = count('location'))
            elif location == 'All' and disposition != 'All' and skill == 'All':
                location_hr_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1, disposition = disposition).values('location').distinct().annotate(total = count('location'))
            elif location == 'All' and disposition == 'All' and skill != 'All':
                location_hr_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1, skill = skill).values('location').distinct().annotate(total = count('location'))
            elif location != 'All' and disposition != 'All' and skill == 'All':
                location_hr_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1, location = location, disposition = disposition).values('location').distinct().annotate(total = count('location'))
            elif location == 'All' and disposition != 'All' and skill != 'All':
                location_hr_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1, disposition = disposition, skill = skill).values('location').distinct().annotate(total = count('location'))
            elif location != 'All' and disposition == 'All' and skill != 'All':
                location_hr_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1, location = location, skill = skill).values('location').distinct().annotate(total = count('location'))
            elif location != 'All' and disposition != 'All' and skill != 'All':
                location_hr_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1, location = location, skill = skill, disposition = disposition).values('location').distinct().annotate(total = count('location'))
            else:
                return []
            for value in location_hr_query:
                if value['total'] > 0:
                   if '->' not in value['location']:
                       if final_dict.has_key(value['location']):
                            final_dict[value['location']].append(value['total'])
                       else:
                           final_dict[value['location']] = [value['total']]
    return final_dict

def hourly_skill_data(prj_id, center, dates, hours, location, disposition, skill):
    final_dict = {}
    for date in dates:
        for hour in hours:
            hr = hour*60*60
            hr1 = (hour + 1)*60*60
            final_hour1 = date + ' ' + time.strftime('%H:%M:%S', time.gmtime(hr1))       
            final_hour = date + ' ' + time.strftime('%H:%M:%S', time.gmtime(hr))
            if location == 'All' and disposition == 'All' and skill == 'All':
                skill_hr_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1).values('skill').distinct().annotate(total = count('skill'))
            elif location != 'All' and disposition == 'All' and skill == 'All':
                skill_hr_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1, location = location).values('skill').distinct().annotate(total = count('skill'))
            elif location == 'All' and disposition != 'All' and skill == 'All':
                skill_hr_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1, disposition = disposition).values('skill').distinct().annotate(total = count('skill'))
            elif location == 'All' and disposition == 'All' and skill != 'All':
                skill_hr_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1, skill = skill).values('skill').distinct().annotate(total = count('skill'))
            elif location != 'All' and disposition != 'All' and skill == 'All':
                skill_hr_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1, location = location, disposition = disposition).values('skill').distinct().annotate(total = count('skill'))
            elif location == 'All' and disposition != 'All' and skill != 'All':
                skill_hr_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1, disposition = disposition, skill = skill).values('skill').distinct().annotate(total = count('skill'))
            elif location != 'All' and disposition == 'All' and skill != 'All':
                skill_hr_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1, location = location, skill = skill).values('skill').distinct().annotate(total = count('skill'))
            elif location != 'All' and disposition != 'All' and skill != 'All':
                skill_hr_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1, location = location, skill = skill, disposition = disposition).values('skill').distinct().annotate(total = count('skill'))
            else:
                return []
            for value in skill_hr_query:
                if value['total'] > 0:
                   if '->' not in value['skill']:
                       if final_dict.has_key(value['skill']):
                            final_dict[value['skill']].append(value['total'])
                       else:
                           final_dict[value['skill']] = [value['total']]
    return final_dict

def hourly_dispo_data(prj_id, center, dates, hours, location, disposition, skill):
    final_dict = {}
    for date in dates:
        for hour in hours:
            hr = hour*60*60
            hr1 = (hour + 1)*60*60
            final_hour1 = date + ' ' + time.strftime('%H:%M:%S', time.gmtime(hr1))
            final_hour = date + ' ' + time.strftime('%H:%M:%S', time.gmtime(hr))
            if location == 'All' and disposition == 'All' and skill == 'All':
                dispo_hr_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1).values('disposition').distinct().annotate(total = count('disposition'))
            elif location != 'All' and disposition == 'All' and skill == 'All':
                dispo_hr_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1, location = location).values('disposition').distinct().annotate(total = count('disposition'))
            elif location == 'All' and disposition != 'All' and skill == 'All':
                dispo_hr_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1, disposition = disposition).values('disposition').distinct().annotate(total = count('disposition'))
            elif location == 'All' and disposition == 'All' and skill != 'All':
                dispo_hr_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1, skill = skill).values('disposition').distinct().annotate(total = count('disposition'))
            elif location != 'All' and disposition != 'All' and skill == 'All':
                dispo_hr_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1, location = location, disposition = disposition).values('disposition').distinct().annotate(total = count('disposition'))
            elif location == 'All' and disposition != 'All' and skill != 'All': 
                dispo_hr_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1, disposition = disposition, skill = skill).values('disposition').distinct().annotate(total = count('disposition'))
            elif location != 'All' and disposition == 'All' and skill != 'All':
                dispo_hr_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1, location = location, skill = skill).values('disposition').distinct().annotate(total = count('disposition'))
            elif location != 'All' and disposition != 'All' and skill != 'All':
                dispo_hr_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1, location = location, skill = skill, disposition = disposition).values('disposition').distinct().annotate(total = count('disposition'))
            else:
                return []
            for value in dispo_hr_query:
                if value['total'] > 0:
                   if '->' not in value['disposition']:
                       if final_dict.has_key(value['disposition']):
                            final_dict[value['disposition']].append(value['total'])
                       else:
                           final_dict[value['disposition']] = [value['total']]
    return final_dict


def hourly_call_data(prj_id, center, dates, hours, location, disposition, skill):
    final_dict = {}  
    for date in dates:
        for hour in hours:
            hr = hour*60*60
            hr1 = (hour + 1)*60*60
            final_hour1 = date + ' ' + time.strftime('%H:%M:%S', time.gmtime(hr1))
            final_hour = date + ' ' + time.strftime('%H:%M:%S', time.gmtime(hr))
            if location == 'All' and disposition == 'All' and skill == 'All':
                call_hr_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1).values('status').distinct().annotate(total = count('status'))
            elif location != 'All' and disposition == 'All' and skill == 'All':
                call_hr_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1, location = location).values('status').distinct().annotate(total = count('status'))
            elif location == 'All' and disposition != 'All' and skill == 'All':
                call_hr_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1, disposition = disposition).values('status').distinct().annotate(total = count('status'))
            elif location == 'All' and disposition == 'All' and skill != 'All':
                call_hr_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1, skill = skill).values('status').distinct().annotate(total = count('status'))
            elif location != 'All' and disposition != 'All' and skill == 'All':
                call_hr_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1, location = location, disposition = disposition).values('status').distinct().annotate(total = count('status'))
            elif location == 'All' and disposition != 'All' and skill != 'All':
                call_hr_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1, disposition = disposition, skill = skill).values('status').distinct().annotate(total = count('status'))
            elif location != 'All' and disposition == 'All' and skill != 'All':
                call_hr_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1, location = location, skill = skill).values('status').distinct().annotate(total = count('status'))
            elif location != 'All' and disposition != 'All' and skill != 'All':
                call_hr_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1, location = location, skill = skill, disposition = disposition).values('status').distinct().annotate(total = count('status'))
            else:
                return []
            for value in call_hr_query:
                if value['total'] > 0:
                   if '->' not in value['status']:
                       if final_dict.has_key(value['status']):
                            final_dict[value['status']].append(value['total'])
                       else:
                           final_dict[value['status']] = [value['total']]
    return final_dict


def hrly_disposition_cate_data(prj_id, center, date, disposition, location, skill):
    final_dict = {}
    if location == 'All' and skill == 'All' and disposition == 'All':
        cate_dispo_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date).values('disposition').distinct().annotate(total = count('disposition'))
    elif disposition != 'All' and skill == 'All' and location == 'All':
        cate_dispo_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date, disposition = disposition).values('disposition').distinct().annotate(total = count('disposition'))
    elif disposition == 'All' and skill != 'All' and location == 'All':
        cate_dispo_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date, skill = skill).values('disposition').distinct().annotate(total = count('disposition'))
    elif disposition == 'All' and skill == 'All' and location != 'All':
        cate_dispo_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date, location = location).values('disposition').distinct().annotate(total = count('disposition'))
    elif disposition != 'All' and skill != 'All' and location == 'All':
        cate_dispo_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date, skill = skill, disposition = disposition).values('disposition').distinct().annotate(total = count('disposition'))
    elif disposition == 'All' and skill != 'All' and location != 'All':
        cate_dispo_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date, skill = skill, location = location).values('disposition').distinct().annotate(total = count('disposition'))
    elif disposition != 'All' and skill != 'All' and location == 'All':
        cate_dispo_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date, skill = skill, disposition = disposition).values('disposition').distinct().annotate(total = count('disposition'))
    elif disposition != 'All' and skill != 'All' and location != 'All':
        cate_dispo_query = InboundDaily.objects.filter(project = prj_id, center = center, date = date, skill = skill, disposition = disposition, location = location).values('disposition').distinct().annotate(total = count('disposition'))
    else:
        return []
    for data in cate_dispo_query:
        if data['total'] > 0:
            if '->' not in data['disposition']:
                if final_dict.has_key(data['disposition']):
                    final_dict[data['disposition']].append(data['total'])
                else:
                    final_dict[data['disposition']] = [data['total']]
    return final_dict

def hrly_dispo_outbound_cate_data(prj_id, center, date, disposition):
    final_dict = {}
    if disposition == 'All':
        outbnd_dispo_query = OutboundDaily.objects.filter(project = prj_id, center = center, date = date).values('disposition').distinct().annotate(total = count('disposition'))
    elif disposition != 'All':
        outbnd_dispo_query = OutboundDaily.objects.filter(project = prj_id, center = center, date = date, disposition = disposition).values('disposition').distinct().annotate(total = count('disposition'))
    else:
        return []
    for value in outbnd_dispo_query:
        if value['total'] > 0:
            if ('->' not in value['disposition']) and (value['disposition'] != ''):
                if final_dict.has_key(value['disposition']):
                    final_dict[value['disposition']].append(value['total'])
                else:
                    final_dict[value['disposition']] = [value['total']]
    return final_dict


def outbnd_disposition_data(prj_id, center, dates, disposition):
    final_dict = {}
    if disposition == 'All':
        outbnd_dispo_query = OutboundDaily.objects.filter(project = prj_id, center = center, date__range = [dates[0], dates[-1]])
        dispo_filters = outbnd_dispo_query.values_list('disposition', flat = True).distinct()
        for date in dates:
            date_check = OutboundDaily.objects.filter(project = prj_id, center = center, date = date).values('disposition').count()
            if date_check > 0:
                for name in dispo_filters:
                    if ('->' not in name) and (name != ''):
                        outbnd_dispo_val = OutboundDaily.objects.filter(project = prj_id, center = center, date = date, disposition = name).count()
                        if final_dict.has_key(name):
                            final_dict[name].append(outbnd_dispo_val)
                        else:
                            final_dict[name] = [outbnd_dispo_val]
    elif disposition != 'All':
        for date in dates:
            outbnd_dispo_val = OutboundDaily.objects.filter(project = prj_id, center = center, date = date, disposition = disposition).count()
            if dispo_val > 0:
                if final_dict.has_key(disposition):
                    final_dict[disposition].append(outbnd_dispo_val)
                else:
                    final_dict[disposition] = [outbnd_dispo_val]
    else:
        return {}
    return final_dict
def hourly_outbnd_dispo_data(prj_id, center, dates, hours, disposition):
    final_dict = {}
    for date in dates:
        for hour in hours:
            hr = hour*60*60
            hr1 = (hour + 1)*60*60
            final_hour1 = date + ' ' + time.strftime('%H:%M:%S', time.gmtime(hr1))
            final_hour = date + ' ' + time.strftime('%H:%M:%S', time.gmtime(hr))
            if disposition == 'All':
                outbnd_dispo_hr_query = OutboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1).values('disposition').distinct().annotate(total = count('disposition'))
            elif disposition != 'All':
                outbnd_dispo_hr_query = OutboundHourlyCall.objects.filter(project = prj_id, center = center, start_time__gte = final_hour, end_time__lte = final_hour1, disposition = disposition).values('disposition').distinct().annotate(total = count('disposition'))
            else:
                return []
            for value in outbnd_dispo_hr_query:
                if value['total'] > 0:
                    if ('->' not in value['disposition']) and (value['disposition'] != ''):
                        if final_dict.has_key(value['disposition']):
                            final_dict[value['disposition']].append(value['total'])
                        else:
                            final_dict[value['disposition']] = [value['total']]
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
                login_hrs = AgentPerformance.objects.filter(project = prj_id, center = center, date = date, name = agent).values_list('login_duration', flat=True)                
    return final_dict


def common_outbnd_dispo_data(project, center, dates, disposition):
    final_dict = {} 
    dispo_list = []
    if disposition == 'All':
        outbnd_dispo_query = OutboundDaily.objects.filter(project = project, center = center, date__range = [dates[0], dates[-1]]).values_list('disposition', flat = True).distinct()
        for date in dates:
            values_list = []
            for dispo_name in outbnd_dispo_query:
                if dispo_name != '':
                    outbnd_val = OutboundDaily.objects.filter(project = project, center = center, date = date, disposition = dispo_name).count()
                    values_list.append(outbnd_val)
            final_values = sum(values_list)
            if final_values > 0:
                oubnd_dispo_val = final_values
                dispo_list.append(oubnd_dispo_val)
        final_dict['data'] = dispo_list
    else:
        final_dict = {}
    return final_dict

def outbnd_utilization_data(project, center, dates, disposition):
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


def inbnd_utilization_data(project, center, dates, location, skill, disposition):
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
        for agent in agent_names:
            if call_type != '':
                agent_query = AgentPerformance.objects.filter(project = project, center = center, date = date, call_type = call_type, agent = agent)
            else:
                agent_query = AgentPerformance.objects.filter(project = project, center = center, date = date, agent = agent)
            wrap_time = agent_query.values_list('wrapup_time', flat = True)
            no_of_calls = agent_query.values_list('total_calls', flat = True)
            if sum(no_of_calls) > 0:
                time_per_agent = float(sum(wrap_time))/float(sum(no_of_calls))
            else:
                time_per_agent = 0
            agents_list.append(time_per_agent)
    day_agent_val = float(sum(agents_list))/float(len(agents_list))
    return day_agent_val

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


def outbound_occupancy_data(project, center, dates, disposition):
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

def outbound_productivity_data(project, center, dates, disposition):
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

def inbound_productivity_data(project, center, dates, location, skill, disposition):
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
                agent_query = AgentPerformance.objects.filter(project = project, center = center, date = date, call_type = call_type, agent = agent)
            else:
                agent_query = AgentPerformance.objects.filter(project = project, center = center, date = date, agent = agent)
            login_time = agent_query.values_list('login_duration', flat = True)
            productivity_val = float(sum(login_time))/float(28800)
            agent_prod.append(productivity_val)    
    final_prod_agent = (float(sum(agent_prod))/float(len(agent_prod)))*100
    final_prod_agent = float('%.2f' % round(final_prod_agent, 2))
    return final_prod_agent
