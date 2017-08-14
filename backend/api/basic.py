
from django.db.models import Max
import calendar
import collections
import datetime
import hashlib
import json
import re
import random
from collections import OrderedDict
from datetime import timedelta
from datetime import date
from dateutil.relativedelta import relativedelta

from django.apps import apps
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.db.models import Sum
from django.db.models import Max
from django.http import HttpResponse
from django.utils.timezone import utc
from django.utils.encoding import smart_str, smart_unicode
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import xlrd
import xlsxwriter
import redis
from xlrd import open_workbook
from xlwt import Workbook, easyxf, XFStyle
from models import *
from common.utils import getHttpResponse as json_HttpResponse


def get_order_of_headers(open_sheet, Default_Headers, mandatory_fileds=[]):
    indexes, sheet_indexes = {}, {}
    sheet_headers = open_sheet.row_values(0)
    lower_sheet_headers = [i.lower() for i in sheet_headers]
    if not mandatory_fileds:
        mandatory_fileds = Default_Headers

    max_index = len(sheet_headers)
    is_mandatory_available = set([i.lower() for i in mandatory_fileds]) - set([j.lower() for j in sheet_headers])
    for ind, val in enumerate(Default_Headers):
        val = val.lower()
        if val in lower_sheet_headers:
            ind_sheet = lower_sheet_headers.index(val)
            sheet_indexes.update({val: ind_sheet})
        else:
            ind_sheet = max_index
            max_index += 1
        #comparing with lower case for case insensitive
        #Change the code as declare *_XL_HEADEERS and *_XL_MAN_HEADERS
        indexes.update({val: ind_sheet})
    return is_mandatory_available, sheet_indexes, indexes


def change_password(request):
    data_to = json.loads(request.POST['json'])
    if "auth_key" in data_to.keys():
        user_id = data_to['user_id']
        auth_key = data_to['auth_key']
        new_pass = data_to['name']
        user_obj = User.objects.filter(id=user_id)[0]
        user_obj.set_password(new_pass)
        user_obj.save()
    else:
        new_pass = json.loads(request.POST['json'])['name']
        user_obj = User.objects.filter(username=request.user.username)[0]
        user_obj.set_password(new_pass)
        user_obj.save()
    return json_HttpResponse('cool')


def get_details(email_id):
    user_obj = User.objects.filter(email=email_id)
    if user_obj:
        user_id = user_obj[0].id
        auth_key = hashlib.sha1(str(random.random())).hexdigest()[:5]
        user_data = Profile()
        user_data.user_id = user_id
        user_data.activation_key = auth_key
        user_data.save()
        return user_id,auth_key
    else:
        return 'Email id not found',0


def forgot_password(request):
    email_id = request.GET['email']
    user_id, auth_key = get_details(email_id)
    var = 'http://nextpulse.nextwealth.in/#!/reset/'+str(user_id)+'/'+str(auth_key)
    if auth_key:
        send_mail('Password Reset', 'click here to reset your password...'+var, 'nextpulse@nextwealth.in', [email_id])
        return json_HttpResponse('Cool')
    else:
        return json_HttpResponse('Email id not found')

def validate_sheet(open_sheet, request, SOH_XL_HEADERS, SOH_XL_MAN_HEADERS):
    sheet_headers = []
    if open_sheet.nrows > 0:
        is_mandatory_available, sheet_headers, all_headers = get_order_of_headers(open_sheet, SOH_XL_HEADERS, SOH_XL_MAN_HEADERS)
        sheet_headers = sorted(sheet_headers.items(), key=lambda x: x[1])
        all_headers = sorted(all_headers.items(), key=lambda x: x[1])
        if is_mandatory_available:
            status = ["Fields are not available: %s" % (", ".join(list(is_mandatory_available)))]
            return "Failed", status
    else:
        status = "Number of Rows: %s" % (str(open_sheet.nrows))
        index_status.update({1: status})
    return sheet_headers

def get_cell_data(open_sheet, row_idx, col_idx):
    try:
        cell_data = open_sheet.cell(row_idx, col_idx).value
        cell_data = smart_str(cell_data)
        cell_data = str(cell_data)
        if isinstance(cell_data, str):
            cell_data = cell_data.strip()
    except IndexError:
        cell_data = ''
    return cell_data


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
        sub_pro_level = filter(None,RawTable.objects.filter(project=pro_cen_mapping[0][0], center=pro_cen_mapping[1][0]).values_list('sub_project',flat=True).distinct())
        if len(sub_pro_level)>= 1:
            level_structure_key['sub_project'] = "All"
        if not level_structure_key:
            work_pac_level = filter(None,RawTable.objects.filter(project=pro_cen_mapping[0][0], center=pro_cen_mapping[1][0]).values_list('work_packet',flat=True).distinct())
            if len(work_pac_level)>=1:
                level_structure_key['work_packet'] = "All"
        if not level_structure_key:
            sub_pac_level = filter(None,RawTable.objects.filter(project=pro_cen_mapping[0][0], center=pro_cen_mapping[1][0]).values_list('sub_packet',flat=True).distinct())
            if len(sub_pac_level)>=1:
                level_structure_key['sub_packet'] = "All"
    return level_structure_key


def latest_dates(request,prj_id):
    result= {}
    if len(prj_id) == 1:
        latest_date = RawTable.objects.filter(project=prj_id).all().aggregate(Max('date'))
        to_date = latest_date['date__max']
        if to_date:
            from_date = to_date - timedelta(6)
            result['from_date'] = str(from_date)
            result['to_date'] = str(to_date)
        else:
            result['from_date'] = '2017-01-05'
            result['to_date'] = '2017-01-11'
    else:
        result['from_date'] = '2017-01-05'
        result['to_date'] = '2017-01-11'
    return result


def dropdown_data(request):
    final_dict = {}
    final_dict['level'] = [1,2,3]
    return json_HttpResponse(final_dict)

# IBM sub_project functionality
def sub_project_names(request,open_book):
    sub_prj_names = {}
    open_sheet = open_book.sheet_by_index(0)
    prj_names = set(open_sheet.col_values(2)[1:])
    teamleader_obj = TeamLead.objects.filter(name_id=request.user.id).values_list('project_id','center_id')[0]
    prj_obj = Project.objects.filter(id=teamleader_obj[0])[0]
    center = TeamLead.objects.filter(name_id=request.user.id).values_list('center_id',flat=True)[0]
    for project_name in prj_names:
        project_name = prj_obj.name +  " " + project_name
        main_prj_name = Project.objects.filter(name = project_name).values_list('id',flat=True)
        if main_prj_name:
            if sub_prj_names.has_key(project_name):
                sub_prj_names[project_name].append(main_prj_name[0])
            else:
                sub_prj_names[project_name] = main_prj_name[0]
        else:
            proj_name = Project(name = project_name, sub_project_check=0, center_id = center)
            proj_name.save()
            proj_name.id
            if sub_prj_names.has_key(project_name):
                sub_prj_names[project_name].append(proj_name.id)
            else:
                sub_prj_names[project_name] = proj_name.id
    return sub_prj_names

def user_data(request):
    user_group = request.user.groups.values_list('name',flat=True)[0]
    manager_dict = {}
    if 'Center_Manager' in user_group:
        center_objs = Centermanager.objects.filter(name_id=request.user.id)
        if center_objs:
            center_obj = center_objs[0]
            #center_id = Centermanager.objects.filter(name_id=request.user.id).values_list('center_name', flat=True)
            #center_name = Center.objects.filter(id = center_id).values_list('name',flat=True)[0]
            #project = Center.objects.filter(name = str(center_name)).values_list('project_name_id',flat=True)
            project_names = Project.objects.filter(center = center_obj).values_list('name',flat=True)
            manager_dict[center_name]= str(project_names)
    if 'Nextwealth_Manager' in user_group:
        center_id = Nextwealthmanager.objects.filter(id=request.user.id).values_list('center_name', flat=True)
        manager_dict[center_id]= str(center_id)
    return json_HttpResponse(manager_dict)


def num_of_days(to_date,from_date):
    date_list=[]
    no_of_days = to_date - from_date
    no_of_days = int(re.findall('\d+', str(no_of_days))[0])
    for i in xrange(0, no_of_days + 1):
        date_list.append(str(from_date + timedelta(days=i)))
    return date_list

def from_too(request):
    return json_HttpResponse('Cool')

def from_to(request):
    from_date = datetime.datetime.strptime(request.GET['from'],'%Y-%m-%d').date()
    to_date = datetime.datetime.strptime(request.GET['to'],'%Y-%m-%d').date()
    type = request.GET['type']
    #type='day'
    try:
        work_packet = request.GET.get('work_packet')
        if ' and ' in work_packet:
            work_packet = work_packet.replace(' and ', ' & ')
    except:
        work_packet = []
    try:
        sub_project = request.GET.get('sub_project')
    except:
        sub_project = ''
    try:
        sub_packet = request.GET.get('sub_packet')
    except:
        sub_packet = ''
    
    try:
        is_clicked = request.GET.get('is_clicked','NA')
    except:
        is_clicked = 'NA'
    project = request.GET['project'].split('-')[0].strip()
    center_id = request.GET['center'].split('-')[0].strip()
    center = Center.objects.filter(name=center_id).values_list('id', flat=True)
    prj_id = Project.objects.filter(name=project).values_list('id', flat=True)
    date_list, month_list, month_names_list = [], [], []
    if type == 'day':
        date_list=num_of_days(to_date,from_date)
        if 'yes' not in is_clicked:
            if len(date_list) > 15:
                type = 'week'
            if len(date_list) > 60:
                type = 'month'
    if type == 'month':
        months_dict = {}
        month_list = [[]]
        month_names_list = []
        month_count = 0
        days = (to_date - from_date).days
        days = days+1
        for i in xrange(0, days):
            date = from_date + datetime.timedelta(i)
            month = date.strftime("%B")
            if month not in month_names_list:
                month_names_list.append(month)
            if month in months_dict:
                months_dict[month].append(str(date))
                month_list[month_count].append(str(date))
            else:
                months_dict[month] = [str(date)]
                month_count = month_count + 1
                month_list.append([str(date)])
        if month_list[0] == []:
            del month_list[0]

    if type == 'week':
        months_dict = {}
        weeks_data = []
        days = (to_date - from_date).days
        days = days+1
        for i in xrange(0, days):
            date = from_date + datetime.timedelta(i)
            weeks_data.append(str(date))
        weeks, weekdays, week_list = [], [], []
        fro_mon = datetime.datetime.strptime(weeks_data[0],'%Y-%m-%d').date()
        to_mon = datetime.datetime.strptime(weeks_data[-1],'%Y-%m-%d').date()
        no_of_days = to_mon - fro_mon
        num_days = int(re.findall('\d+', str(no_of_days))[0]) + 1
        start = 1
        end = 7 - fro_mon.weekday()
        while start <= num_days:
            weeks.append({'start': start, 'end': end})
            sdate = fro_mon + datetime.timedelta(start - 1) 
            edate = fro_mon + datetime.timedelta(end - 1) 
            weekdays.append({'start': sdate, 'end': edate})
            start = end + 1
            end = end + 7
            if end > num_days:
                end = num_days
        if weekdays[-1]['end'] > to_mon :
            weekdays[-1]['end'] = to_mon
        for w_days in weekdays:
            date_list = num_of_days(w_days['end'],w_days['start'])
            week_list.append(date_list)
    dwm_dict= {}
    employe_dates = {}
    if type == 'day':
        dwm_dict['day']= date_list
        employe_dates['days'] = date_list
    if type == 'month':
        new_month_dict = {}
        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July','August', 'September', 'October', 'November', 'December']
        k = OrderedDict(sorted(months_dict.items(), key=lambda x: months.index(x[0])))
        for month_na in tuple(k):
            new_month_dict[month_na] = {}
            if employe_dates.has_key('days'):
                employe_dates['days'] = employe_dates['days']+months_dict[month_na]
            else:
                employe_dates['days']=months_dict[month_na]
        dwm_dict['month'] = {'month_names':month_names_list, 'month_dates':month_list}

    if type == 'week':
        dwm_dict['week'] = week_list
        for week in week_list:
            if week and  employe_dates.has_key('days'):
                employe_dates['days'] = employe_dates['days']+week
            else:
                employe_dates['days'] = week


    resul_data = {}
    main_data_dict = data_dict(request.GET)
    level_structure_key = get_level_structure_key(main_data_dict['work_packet'], main_data_dict['sub_project'], main_data_dict['sub_packet'], main_data_dict['pro_cen_mapping'])
    final_result_dict = day_week_month(request,dwm_dict,prj_id,center,work_packet,level_structure_key)
    ###volumes_graphs_details = volumes_graphs_data(date_list,prj_id,center,level_structure_key)
    #volumes_graphs_details = volumes_graphs_data_table(employe_dates['days'],prj_id,center,level_structure_key)

    final_dict = {}      
    #final_result_dict['volumes_graphs_details'] = volumes_graphs_details
    #internal_sub_error_types = internal_extrnal_sub_error_types(request, employe_dates['days'], prj_id, center, level_structure_key,"Internal")
    #external_sub_error_types = internal_extrnal_sub_error_types(request, employe_dates['days'], prj_id, center,level_structure_key, "External")
    #final_result_dict['internal_sub_error_types'] = graph_data_alignment_color(internal_sub_error_types,'y',level_structure_key,prj_id,center,'')
    #final_result_dict['external_sub_error_types'] = graph_data_alignment_color(external_sub_error_types,'y',level_structure_key,prj_id,center,'')
    final_result_dict['days_type'] = type
    return json_HttpResponse(final_result_dict)


def upload_target_data(date_list, prj_id, center):
    result_data = []
    final_result = {}
    final_data = []
    for date in date_list:
        total_done_value = RawTable.objects.filter(project=prj_id, center=center, date=date).aggregate(Max('per_day'))
        if total_done_value['per_day__max'] > 0:
            target = UploadDataTable.objects.filter(project=prj_id,center=center,date=date).aggregate(Sum('target'))
            upload = UploadDataTable.objects.filter(project=prj_id,center=center,date=date).aggregate(Sum('upload'))
            if target['target__sum'] > 0 and upload['upload__sum'] > 0:
                percentage = (float(upload['upload__sum'])/float(target['target__sum'])) * 100
                final_percentage = (float('%.2f' % round(percentage, 2)))
            else:
                final_percentage = 0
            final_data.append(final_percentage)
    final_result['data'] = final_data
    return final_result