from django.shortcuts import render
import xlrd
import datetime
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
    final_dict, week_final_dict = {}, {}
    if location == 'All' and disposition == 'All' and skill == 'All':
        location_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]]).values('location', 'date').distinct().annotate(total = count('location')).order_by('date')
    elif location != 'All' and disposition == 'All' and skill == 'All':
        location_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], location = location).values('location', 'date').distinct().annotate(total = count('location')).order_by('date')
    elif location == 'All' and disposition != 'All' and skill == 'All':
        location_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], disposition = disposition).values('location', 'date').distinct().annotate(total = count('location')).order_by('date')
    elif location == 'All' and disposition == 'All' and skill != 'All':
        location_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], skill = skill).values('location', 'date').distinct().annotate(total = count('location')).order_by('date')
    elif location != 'All' and disposition != 'All' and skill == 'All':
        location_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], location = location, disposition = disposition).values('location', 'date').distinct().annotate(total = count('location')).order_by('date')
    elif location != 'All' and disposition == 'All' and skill != 'All':
        location_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], location = location, skill = skill).values('location', 'date').distinct().annotate(total = count('location')).order_by('date')
    elif location == 'All' and disposition != 'All' and skill != 'All':
        location_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], disposition = disposition, skill = skill).values('location', 'date').distinct().annotate(total = count('location')).order_by('date')
    elif location != 'All' and disposition != 'All' and skill != 'All':
        location_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], disposition = disposition, skill = skill, location = location).values('location', 'date').distinct().annotate(total = count('location')).order_by('date')
    else:
        return []
    for data in location_query:
       if data['total'] > 0:
           if '->' not in data['location']:
               if final_dict.has_key(data['location']):
                   final_dict[data['location']].append(int(data['total']))
               else:
                   final_dict[data['location']] = [int(data['total'])]
    return final_dict


def skill_data(prj_id, center, dates_list, skill, location, disposition):
    final_dict = {}
    if skill == 'All' and location == 'All' and disposition == 'All':
        skill_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]]).values('skill', 'date').distinct().annotate(total = count('skill')).order_by('date')
    elif skill != 'All' and location == 'All' and disposition == 'All':
        skill_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], skill = skill).values('skill', 'date').distinct().annotate(total = count('skill')).order_by('date')
    elif skill == 'All' and location != 'All' and disposition == 'All':
        skill_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], location = location).values('skill', 'date').distinct().annotate(total = count('skill')).order_by('date')
    elif skill == 'All' and location == 'All' and disposition != 'All':
        skill_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], disposition = disposition).values('skill', 'date').distinct().annotate(total = count('skill')).order_by('date')
    elif skill != 'All' and location != 'All' and disposition == 'All':
        skill_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], location = location, skill = skill).values('skill', 'date').distinct().annotate(total = count('skill')).order_by('date')
    elif skill != 'All' and location == 'All' and disposition != 'All':
        skill_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], disposition = disposition, skill = skill).values('skill', 'date').distinct().annotate(total = count('skill')).order_by('date')
    elif skill == 'All' and location != 'All' and disposition != 'All':
        skill_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], location = location, skill = skill).values('skill', 'date').distinct().annotate(total = count('skill')).order_by('date')
    elif skill != 'All' and location != 'All' and disposition != 'All':
        skill_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], location = location, skill = skill, disposition = disposition).values('skill', 'date').distinct().annotate(total = count('skill')).order_by('date')
    else:
        return []
    for data in skill_query:
        if data['total'] > 0:
            if '->' not in data['skill']:
                if final_dict.has_key(data['skill']):
                    final_dict[data['skill']].append(data['total'])
                else:
                    final_dict[data['skill']] = [data['total']]
    #return [{'name': item, 'data': final_dict[item]} for item in final_dict]
    return final_dict

def disposition_data(prj_id, center, dates_list, disposition, location, skill):
    final_dict = {}
    if disposition == 'All' and skill == 'All' and location == 'All':
        dispo_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]]).values('disposition', 'date').distinct().annotate(total = count('disposition')).order_by('date')
    elif disposition != 'All' and skill == 'All' and location == 'All':
        dispo_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], disposition = disposition).values('disposition', 'date').distinct().annotate(total = count('disposition')).order_by('date')
    elif disposition == 'All' and skill != 'All' and location == 'All':
        dispo_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], skill = skill).values('disposition', 'date').distinct().annotate(total = count('disposition')).order_by('date')
    elif disposition == 'All' and skill == 'All' and location != 'All':
        dispo_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], location = location).values('disposition', 'date').distinct().annotate(total = count('disposition')).order_by('date')
    elif disposition != 'All' and skill != 'All' and location == 'All':
        dispo_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], skill = skill, disposition = disposition).values('disposition', 'date').distinct().annotate(total = count('disposition')).order_by('date')
    elif disposition == 'All' and skill != 'All' and location != 'All':
        dispo_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], skill = skill, location = location).values('disposition', 'date').distinct().annotate(total = count('disposition')).order_by('date')
    elif disposition != 'All' and skill != 'All' and location == 'All':
        dispo_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], skill = skill, disposition = disposition).values('disposition', 'date').distinct().annotate(total = count('disposition')).order_by('date')
    elif disposition != 'All' and skill != 'All' and location != 'All':
        dispo_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], skill = skill, disposition = disposition, location = location).values('disposition', 'date').distinct().annotate(total = count('disposition')).order_by('date')
    else:
        return []
    for data in dispo_query:
        if data['total'] > 0:
            if '->' not in data['disposition']:
                if final_dict.has_key(data['disposition']):
                    final_dict[data['disposition']].append(data['total'])
                else:
                    final_dict[data['disposition']] = [data['total']]
    #return [{'name': item, 'data': final_dict[item]} for item in final_dict]
    return final_dict

def call_status_data(prj_id, center, dates_list, location, skill, disposition):
    final_dict = {}
    if location == 'All' and skill == 'All' and disposition == 'All':
        status_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]]).values('status', 'date').annotate(total = count('status')).order_by('date')
    elif location != 'All' and skill == 'All' and disposition == 'All':
        status_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], location = location).values('status', 'date').annotate(total = count('status')).order_by('date')
    elif location == 'All' and skill != 'All' and disposition == 'All':
        status_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], skill = skill).values('status', 'date').annotate(total = count('status')).order_by('date')
    elif location == 'All' and skill == 'All' and disposition != 'All':
        status_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], disposition = disposition).values('status', 'date').annotate(total = count('status')).order_by('date')
    elif location != 'All' and skill == 'All' and disposition != 'All':
        status_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], disposition = disposition, location = location).values('status', 'date').annotate(total = count('status')).order_by('date')
    elif location != 'All' and skill != 'All' and disposition == 'All':
        status_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], skill = skill, location = location).values('status', 'date').annotate(total = count('status')).order_by('date')
    elif location == 'All' and skill != 'All' and disposition != 'All':
        status_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], skill = skill, disposition = disposition).values('status', 'date').annotate(total = count('status')).order_by('date')
    elif location != 'All' and skill != 'All' and disposition != 'All':
        status_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], skill = skill, disposition = disposition, location = location).values('status', 'date').annotate(total = count('status')).order_by('date')
    else:
        return []
    for data in status_query:
        if data['total'] > 0:
            if '->' not in data['status']:
                if final_dict.has_key(data['status']):
                    final_dict[data['status']].append(data['total'])
                else:
                    final_dict[data['status']] = [data['total']]
    #return [{'name': item, 'data': final_dict[item]} for item in final_dict]
    return final_dict

def disposition_cate_data(prj_id, center, dates_list, location, skill, disposition):
    final_dict = {} 
    if disposition == 'All' and skill == 'All' and location == 'All':
        dispo_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]]).values('disposition').distinct().annotate(total = count('disposition'))
    elif disposition != 'All' and skill == 'All' and location == 'All':
        dispo_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], disposition = disposition).values('disposition').distinct().annotate(total = count('disposition'))
    elif disposition == 'All' and skill != 'All' and location == 'All':
        dispo_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], skill = skill).values('disposition').distinct().annotate(total = count('disposition'))
    elif disposition == 'All' and skill == 'All' and location != 'All':
        dispo_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], location = location).values('disposition').distinct().annotate(total = count('disposition'))
    elif disposition != 'All' and skill != 'All' and location == 'All':
        dispo_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], skill = skill, disposition = disposition).values('disposition').distinct().annotate(total = count('disposition'))
    elif disposition != 'All' and skill == 'All' and location != 'All':
        dispo_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], location = location, disposition = disposition).values('disposition').distinct().annotate(total = count('disposition'))
    elif disposition == 'All' and skill != 'All' and location != 'All':
        dispo_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], location = location, skill = skill).values('disposition').distinct().annotate(total = count('disposition'))
    elif disposition != 'All' and skill != 'All' and location != 'All':
        dispo_query = InboundHourlyCall.objects.filter(project = prj_id, center = center, date__range = [dates_list[0], dates_list[-1]], location = location, skill = skill, disposition = disposition).values('disposition').distinct().annotate(total = count('disposition'))
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
