import datetime
import traceback
from django.shortcuts import render
from common.utils import getHttpResponse as HttpResponse
from models import *
from django.views.decorators.csrf import csrf_exempt
from auth.decorators import loginRequired
from xlrd import open_workbook
import xlrd
from xlrd import open_workbook
from xlwt import Workbook, easyxf, XFStyle
import xlsxwriter
from src import *
from forms import *
from django.db.models import Sum
from django.db.models import Max
import redis
from datetime import timedelta
from datetime import date
from dateutil.relativedelta import relativedelta
import re
import json
from django.apps import apps
from collections import OrderedDict
from django.utils.timezone import utc
from django.utils.encoding import smart_str, smart_unicode
from collections import OrderedDict
from django.core.mail import send_mail
import collections
import hashlib
import random


def error_insert(request):
    pass

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
    return HttpResponse('cool')

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
        return HttpResponse('Cool')
    else:
        return HttpResponse('Email id not found')

def validate_sheet(open_sheet, request, SOH_XL_HEADERS, SOH_XL_MAN_HEADERS):
    sheet_headers = []
    if open_sheet.nrows > 0:
        is_mandatory_available, sheet_headers, all_headers = get_order_of_headers(open_sheet, SOH_XL_HEADERS, SOH_XL_MAN_HEADERS)
        sheet_headers = sorted(sheet_headers.items(), key=lambda x: x[1])
        all_headers = sorted(all_headers.items(), key=lambda x: x[1])
        if is_mandatory_available:
            status = ["Fields are not available: %s" % (", ".join(list(is_mandatory_available)))]
            #index_status.update({1: status})
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

#@loginRequired

def project(request):
    try:
        #manager_prj =  request.GET.get('name','')
        #manager_prj = manager_prj.strip(' -')
        multi_center, multi_project = request.GET.get('name').split(' - ')
    except: 
        #manager_prj = ''
        multi_center, multi_project = '',''
    user_group = request.user.groups.values_list('name', flat=True)[0]
    user_group_id = Group.objects.filter(name=user_group).values_list('id', flat=True)
    dict = {}
    list_wid = []
    layout_list = []
    final_dict = {}
    
    if 'team_lead' in user_group:
        center = TeamLead.objects.filter(name_id=request.user.id).values_list('center')
        prj_id = TeamLead.objects.filter(name_id=request.user.id).values_list('project')

    if 'customer' in user_group:
        select_list = [] 
        details = {} 
        center_list = Customer.objects.filter(name_id=request.user.id).values_list('center')
        project_list = Customer.objects.filter(name_id=request.user.id).values_list('project')
        if (len(center_list) & len(project_list)) == 1:
            select_list.append('none')
        if len(center_list) < 2: 
            center_name = str(Center.objects.filter(id=center_list[0][0])[0])
            for project in project_list:
                project_name = str(Project.objects.filter(id=project[0])[0])
                vari = center_name + ' - ' + project_name
                select_list.append(vari)
        elif len(center_list) >= 2:
            for center in center_list:
                center_name = str(Center.objects.filter(id=center[0])[0])
                for project in project_list:
                    project_name = str(Project.objects.filter(id=project[0])[0])
                    select_list.append(center_name + ' - ' + project_name) 
        details['list'] = select_list
    
        if len(select_list) > 1: 
              if multi_project:
                 prj_id = Project.objects.filter(name=multi_project).values_list('id','center_id')
              else:
                 prj_name = select_list[1].split(' - ')[1]
                 prj_id = Project.objects.filter(name=prj_name).values_list('id','center_id') 

    if 'nextwealth_manager' in user_group:
        select_list = []  
        #layout_list = []
        center_list = Nextwealthmanager.objects.filter(name_id=request.user.id).values_list('center')
        if len(center_list) < 2: 
            center_name = str(Center.objects.filter(id=center_list[0][0])[0])
            center_id = Center.objects.filter(name = center_name)[0].id
            project_list = Project.objects.filter(center_id=center_id)
            for project in project_list:
                project_name = str(project)
                #select_list.append(center_name + ' - ' + project_name)
                select_list.append(project_name)

        elif len(center_list) >= 2:
            for center in center_list:
                center_name = str(Center.objects.filter(id=center[0])[0])
                center_id = Center.objects.filter(id=center[0])[0].id
                project_list = Project.objects.filter(center_id=center_id)
                for project in project_list:
                    project_name = str(project)
                    select_list.append(project_name)    

        if len(select_list) > 1:
            if multi_project:
                prj_id = Project.objects.filter(name=multi_project).values_list('id','center_id')
            else:
                prj_name = select_list[1]
                #prj_name = select_list[1]
                prj_id = Project.objects.filter(name=prj_name).values_list('id','center_id')

    if 'center_manager' in user_group:
        select_list = []
        center_list = Centermanager.objects.filter(name_id=request.user.id).values_list('center')
        if len(center_list) < 2:
            center_name = str(Center.objects.filter(id=center_list[0][0])[0])
            center_id = Center.objects.filter(name = center_name)[0].id
            project_list = Project.objects.filter(center_id=center_id)
            for project in project_list:
                project_name = str(project)
                select_list.append(project_name)

        elif len(center_list) >= 2:
            for center in center_list:
                center_name = str(Center.objects.filter(id=center[0])[0])
                center_id = Center.objects.filter(id=center[0])[0].id
                project_list = Project.objects.filter(center_id=center_id)
                for project in project_list:
                    project_name = str(project)
                    select_list.append(project_name)
          
        if len(select_list) > 1:
            if multi_project:
                prj_id = Project.objects.filter(name=multi_project).values_list('id','center_id')
            else:
                prj_name = select_list[1]
                prj_id = Project.objects.filter(name=prj_name).values_list('id','center_id')    

        else:
            if multi_project:
                prj_id = Project.objects.filter(name=multi_project).values_list('id','center_id')
            else:
                prj_name = select_list[0]
                prj_id = Project.objects.filter(name=prj_name).values_list('id','center_id') 

    
    """if user_group in ['nextwealth_manager','center_manager','customer']:
        widgets_id = Widgets_group.objects.filter(User_Group_id=user_group_id, project=prj_id[0][0],center=prj_id[0][1]).values('widget_priority', 'is_drilldown','is_display', 'widget_name')
    else:
        widgets_id = Widgets_group.objects.filter(User_Group_id=user_group_id, project=prj_id,center=center).values('widget_priority', 'is_drilldown','is_display', 'widget_name')

    for data in widgets_id:
        if data['is_display'] == True:
            widgets_data = Widgets.objects.filter(id=data['widget_name']).values('config_name', 'name', 'id_num', 'col','opt', 'day_type_widget', 'api')
            wid_dict = widgets_data[0]
            wid_dict['widget_priority'] = data['widget_priority']
            wid_dict['is_drilldown'] = data['is_drilldown']
            list_wid.append(wid_dict)
    sorted_dict = sorted(list_wid, key=lambda k: k['widget_priority'])
    lay_out_order = []
    #import pdb;pdb.set_trace()
    for i in sorted_dict:
        config_name = i.pop('config_name')
        lay_out_order.append(config_name)
        final_dict[config_name] = i
    layout_list.append(final_dict)
    layout_list.append({'layout': lay_out_order})"""

    if user_group in ['nextwealth_manager','center_manager','customer']:
        widgets_id = Widgets_group.objects.filter(User_Group_id=user_group_id, project=prj_id[0][0],center=prj_id[0][1]).values('widget_priority', 'is_drilldown','is_display', 'widget_name')
    else:
        widgets_id = Widgets_group.objects.filter(User_Group_id=user_group_id, project=prj_id,center=center).values('widget_priority', 'is_drilldown','is_display', 'widget_name')

    for data in widgets_id:
        if data['is_display'] == True:
            widgets_data = Widgets.objects.filter(id=data['widget_name']).values('config_name', 'name', 'id_num', 'col','opt', 'day_type_widget', 'api')
            if user_group in ['nextwealth_manager','center_manager','customer']:
                alias_name = Alias_Widget.objects.filter(project=prj_id[0][0],widget_name_id=data['widget_name']).values('alias_widget_name')
            else:
                alias_name = Alias_Widget.objects.filter(project=prj_id,widget_name_id=data['widget_name']).values('alias_widget_name')
            new_dict ={}
            if len(alias_name) > 0:
                if alias_name[0]['alias_widget_name']:
                    #new_dict['name'] = str(alias_name[0]['alias_widget_name'])
                    for wd_key,wd_value in widgets_data[0].iteritems():
                        if wd_key == 'name': 
                            new_dict[wd_key] = str(alias_name[0]['alias_widget_name'])
                        else:
                            new_dict[wd_key] = wd_value 
                    widgets_data[0].update(new_dict)
                    #widgets_data[0]['name'] = str(alias_name[0]['alias_widget_name'])
            if new_dict: 
                wid_dict = new_dict
            else:
                wid_dict = widgets_data[0]
            wid_dict['widget_priority'] = data['widget_priority']
            wid_dict['is_drilldown'] = data['is_drilldown']
            list_wid.append(wid_dict)
    sorted_dict = sorted(list_wid, key=lambda k: k['widget_priority'])
    lay_out_order = [] 
    for i in sorted_dict:
        config_name = i.pop('config_name')
        lay_out_order.append(config_name)
        final_dict[config_name] = i
    layout_list.append(final_dict)
    layout_list.append({'layout': lay_out_order}) 



    if 'team_lead' in user_group:
        final_details = {}
        details = {}
        select_list = []
        #layout_list = []
        center_list = TeamLead.objects.filter(name_id=request.user.id).values_list('center')
        project_list = TeamLead.objects.filter(name_id=request.user.id).values_list('project')
        if (len(center_list) & len(project_list)) == 1:
            select_list.append('none')
        if len(center_list) < 2:
            center_name = str(Center.objects.filter(id=center_list[0][0])[0])
            for project in project_list:
                project_name = str(Project.objects.filter(id=project[0])[0])
                #lay_list = json.loads(str(Project.objects.filter(id=project[0]).values_list('layout')[0][0]))
                vari = center_name + ' - ' + project_name
                #layout_list.append({vari:lay_list})
                select_list.append(vari)
        elif len(center_list) >= 2:
            for center in center_list:
                center_name = str(Center.objects.filter(id=center[0])[0])
                for project in project_list:
                    project_name = str(Project.objects.filter(id=project[0])[0])
                    select_list.append(center_name + ' - ' + project_name)
        details['list'] = select_list
        details['role'] = 'team_lead'
        details['lay'] = layout_list
        details['final'] = final_details
        new_dates = latest_dates(request, project_list)
        details['dates'] = new_dates
        return HttpResponse(details)

    if 'center_manager' in user_group:
        final_details = {}
        details = {}
        select_list = []
        #layout_list = []
        center = Centermanager.objects.filter(name_id=request.user.id).values_list('center', flat=True)[0]
        center_name = Center.objects.filter(id=center).values_list('name', flat=True)[0]
        project_names = Project.objects.filter(center_id=center).values_list('name', flat=True)
        for project in project_names:
            #lay_list = json.loads(str(Project.objects.filter(name=project).values_list('layout')[0][0]))
            vari = center_name + ' - ' + project
            #layout_list.append({vari:lay_list})
            select_list.append(center_name + ' - ' + project)
        details['list'] = select_list
        details['role'] = 'center_manager'
        details['lay'] = layout_list
        details['final'] = final_details
        if len(project_names) > 1: 
            if multi_project:
                prj_id = Project.objects.filter(name=multi_project).values_list('id',flat=True)
            else:
                prj_id = Project.objects.filter(name=project_names[1]).values_list('id',flat=True)
            new_dates = latest_dates(request, prj_id)
        else:
            new_dates = latest_dates(request, project_names)
        details['dates'] = new_dates
        return HttpResponse(details)

    if 'nextwealth_manager' in user_group:
        final_details = {}
        details = {}
        select_list = []
        #layout_list = []
        center_list = Nextwealthmanager.objects.filter(name_id=request.user.id).values_list('center')
        if len(center_list) < 2:
            center_name = str(Center.objects.filter(id=center_list[0][0])[0])
            center_id = Center.objects.filter(name = center_name)[0].id
            project_list = Project.objects.filter(center_id=center_id)
            for project in project_list:
                project_name = str(project)
                try:
                    lay_list = json.loads(str(Project.objects.filter(name=project_name).values_list('layout')[0][0]))
                except:
                    lay_list = ''
                vari = center_name + ' - ' + project_name
                #vari = project_name
                #layout_list.append({vari:lay_list})
                select_list.append(center_name + ' - ' + project_name)
                #select_list.append(project_name)

        elif len(center_list) >= 2:
            for center in center_list:
                center_name = str(Center.objects.filter(id=center[0])[0])
                center_id = Center.objects.filter(id=center[0])[0].id
                project_list = Project.objects.filter(center_id=center_id)
                for project in project_list:
                    project_name = str(project)
                    try:
                        lay_list = json.loads(str(Project.objects.filter(name=project_name).values_list('layout')[0][0]))
                    except:
                        lay_list = ''
                    vari = center_name + ' - ' + project_name
                    #vari = project_name
                    layout_list.append({vari:lay_list})
                    select_list.append(center_name + ' - ' + project_name)
                    #select_list.append(project_name)

        details['list'] = select_list
        details['role'] = 'nextwealth_manager'
        details['lay'] = layout_list
        details['final'] = final_details
        if len(select_list) > 1:
            if multi_project:
                prj_id = Project.objects.filter(name=multi_project).values_list('id',flat=True)
            else:
                prj_name = select_list[1].split('- ')[1].strip()
                #prj_name = select_list[1]
                prj_id = Project.objects.filter(name=prj_name).values_list('id',flat=True)
            new_dates = latest_dates(request, prj_id)
        else:
            new_dates = latest_dates(request, project_list)
        details['dates'] = new_dates
        return HttpResponse(details)

    if 'customer' in user_group:
        final_details = {}
        details = {}
        select_list = []
        #layout_list = []
        #lay_list = json.loads(str(Customer.objects.filter(name_id=request.user.id).values_list('layout')[0][0]))
        #layout_list.append({'layout': lay_list})

        center_list = Customer.objects.filter(name_id=request.user.id).values_list('center')
        project_list = Customer.objects.filter(name_id=request.user.id).values_list('project')
        #customer_id = Customer.objects.filter(name_id=request.user.id).values_list('id', flat=True)

        if (len(center_list) & len(project_list)) == 1:
            select_list.append('none')
        if len(center_list) < 2:
            center_name = str(Center.objects.filter(id=center_list[0][0])[0])
            for project in project_list:
                project_name = str(Project.objects.filter(id=project[0])[0])
                #lay_list = json.loads(str(Project.objects.filter(id=project[0]).values_list('layout')[0][0]))
                vari = center_name + ' - ' + project_name
                #layout_list.append({vari:lay_list})
                select_list.append(vari)
        elif len(center_list) >= 2:
            for center in center_list:
                center_name = str(Center.objects.filter(id=center[0])[0])
                for project in project_list:
                    project_name = str(Project.objects.filter(id=project[0])[0])
                    select_list.append(center_name + ' - ' + project_name)
        details['list'] = select_list
        details['role'] = 'customer'
        details['lay'] = layout_list
        details['final'] = final_details
        project_names = project_list
        if len(project_names) > 1: 
            if multi_project:
                prj_id = Project.objects.filter(name=multi_project).values_list('id',flat=True)
            else:
                prj_id = Project.objects.filter(name=project_names[1]).values_list('id',flat=True)
            new_dates = latest_dates(request, prj_id)
        else:
            new_dates = latest_dates(request, project_names)
        details['dates'] = new_dates

        details['dates'] = new_dates
        return HttpResponse(details)

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


def different_error_type(total_error_types):
    all_errors = {}
    new_all_errors = {}
    if len(total_error_types) > 0:
        for error_dict in total_error_types:
            error_names= error_dict['error_types'].split('#<>#')
            error_values = error_dict['error_values'].split('#<>#')
            for er_key,er_value in zip(error_names,error_values):
                if all_errors.has_key(er_key):
                    all_errors[er_key].append(int(er_value))
                else:
                    if er_key != '':
                        all_errors[er_key] = [int(er_value)]
        for error_type,error_value in all_errors.iteritems():
            try:
                new_all_errors[str(error_type)] = sum(error_value)
            except:
                error_type = smart_str(error_type)
                new_all_errors[error_type] = sum(error_value)
    return new_all_errors


def error_types_sum(error_list):
    final_error_dict = {}
    new_final_dict = {}
    for error_dict in error_list:
        error_dict = json.loads(error_dict)
        for er_type,er_value in error_dict.iteritems():
            if final_error_dict.has_key(er_type):
                final_error_dict[er_type].append(er_value)
            else:
                final_error_dict[er_type] = [er_value]
    for error_type, error_value in final_error_dict.iteritems():
        final_error_dict[error_type] = sum(error_value)
    if final_error_dict.has_key('no_data'):
        del final_error_dict['no_data']
    for er_key in final_error_dict.keys():
        if final_error_dict[er_key] != 0:
            new_final_dict[er_key] = final_error_dict[er_key]

    #return final_error_dict
    return new_final_dict



def internal_extrnal_error_types(request,date_list,prj_id,center_obj,level_structure_key,err_type):
    prj_name = Project.objects.filter(id=prj_id).values_list('name', flat=True)
    center_name = Center.objects.filter(id=center_obj).values_list('name', flat=True)
    query_set = query_set_generation(prj_id, center_obj, level_structure_key,date_list)
    if err_type =='Internal' :
        #extr_volumes_list = Internalerrors.objects.filter(**query_set).values('sub_project','work_packet','sub_packet').distinct()
        extr_volumes_list = worktrack_internal_external_workpackets_list(level_structure_key, 'Internalerrors',query_set)
        err_key_type = 'error'
    if err_type == 'External':
        #extr_volumes_list = Externalerrors.objects.filter(**query_set).values('sub_project','work_packet','sub_packet').distinct()
        extr_volumes_list = worktrack_internal_external_workpackets_list(level_structure_key, 'Externalerrors',query_set)
        err_key_type = 'externalerror'
    conn = redis.Redis(host="localhost", port=6379, db=0)
    # below variable for error graphs.
    result = {}
    vol_error_values = {}
    vol_audit_data = {}
    # below variable for external errors
    extrnl_error_values = {}
    extrnl_err_type = {}
    extr_volumes_list_new=[]
    all_error_types = []
    for date_va in date_list:
        count =0
        total_done_value = RawTable.objects.filter(project=prj_id, center=center_obj, date=date_va).aggregate(Max('per_day'))
        if total_done_value['per_day__max'] > 0:
            for vol_type in extr_volumes_list:
                """for vol_keys, vol_values in vol_type.iteritems():
                    if vol_values == '':
                        vol_type[vol_keys] = 'NA'
                work_packets = vol_type['sub_project'] + '_' + vol_type['work_packet'] + '_' + vol_type['sub_packet']"""
                #work_packets = vol_type['work_packet']
                final_work_packet = level_hierarchy_key(level_structure_key, vol_type)
                if not final_work_packet:
                    final_work_packet = level_hierarchy_key(extr_volumes_list[count],vol_type)
                count = count+1
                extr_volumes_list_new.append(final_work_packet)
                key_pattern = '{0}_{1}_{2}_{3}_{4}'.format(prj_name[0], str(center_name[0]), final_work_packet, date_va,err_key_type)
                audit_key_list = conn.keys(pattern=key_pattern)
                if not audit_key_list:
                    if vol_error_values.has_key(final_work_packet):
                        vol_error_values[final_work_packet].append("NA")
                        vol_audit_data[final_work_packet].append("NA")
                    else:
                        vol_error_values[final_work_packet] = ["NA"]
                        vol_audit_data[final_work_packet] = ["NA"]
                for cur_key in audit_key_list:
                    var = conn.hgetall(cur_key)
                    for key, value in var.iteritems():
                        if key == 'types_of_errors':
                            all_error_types.append(value)
                        else:
                            if value == 'None':
                                value = "NA"
                            error_vol_type = final_work_packet
                            #if key == 'total_errors':
                            if key == 'error_values':
                                if vol_error_values.has_key(error_vol_type):
                                    if value =="NA":
                                        vol_error_values[error_vol_type].append(value)
                                    else:
                                        vol_error_values[error_vol_type].append(int(value))
                                else:
                                    if value =="NA":
                                        vol_error_values[error_vol_type] = [value]
                                    else:
                                        vol_error_values[error_vol_type] = [int(value)]
                            else:
                                if vol_audit_data.has_key(error_vol_type):
                                    if value=="NA":
                                        vol_audit_data[error_vol_type].append(value)
                                    else:
                                        vol_audit_data[error_vol_type].append(int(value))
                                else:
                                    if value=="NA":
                                        vol_audit_data[error_vol_type] = [value]
                                    else:
                                        vol_audit_data[error_vol_type] = [int(value)]
    indicidual_error_calc = error_types_sum(all_error_types)
    return indicidual_error_calc

def redis_insertion_final(prj_obj,center_obj,dates_list,key_type,level_structure):
    data_dict = {}
    prj_name = prj_obj.name
    center_name = center_obj.name
    all_dates = []
    if key_type == 'Production':
        volumes_list = RawTable.objects.filter(project=prj_obj, center=center_obj).values('sub_project', 'work_packet', 'sub_packet').distinct()
    if key_type == 'Internal':
        volumes_list = Internalerrors.objects.filter(project=prj_obj, center=center_obj).values('sub_project', 'work_packet', 'sub_packet').distinct()
    if key_type == 'External':
        volumes_list = Externalerrors.objects.filter(project=prj_obj, center=center_obj).values('sub_project', 'work_packet', 'sub_packet').distinct()
    if key_type == 'WorkTrack':
        volumes_list = Worktrack.objects.filter(project=prj_obj, center=center_obj).values('sub_project', 'work_packet', 'sub_packet').distinct()
    for date in dates_list:
        date_is = datetime.datetime.strptime(date,'%Y-%m-%d').date()
        for row_record_dict in volumes_list:
            final_work_packet = ''
            single_row_dict = {}
            query_set = {}
            query_set['date'] = date
            query_set['project'] = prj_obj
            query_set['center'] = center_obj
            #for vol_key, vol_value in row_record_dict.iteritems():
            if 'sub_project' in level_structure:
                final_work_packet = row_record_dict['sub_project']
                query_set['sub_project'] = row_record_dict['sub_project']
            if 'work_packet' in level_structure:
                query_set['work_packet'] = row_record_dict['work_packet']
                if final_work_packet:
                    final_work_packet = final_work_packet + '_' + row_record_dict['work_packet']
                else:
                    final_work_packet = row_record_dict['work_packet']
            if 'sub_packet' in level_structure:
                query_set['sub_packet'] = row_record_dict['sub_packet']
                if final_work_packet:
                    final_work_packet = final_work_packet + '_' + row_record_dict['sub_packet']
                else:
                    final_work_packet = row_record_dict['sub_packet']
            value_dict = {}
            if key_type == 'Production':
                redis_key = '{0}_{1}_{2}_{3}'.format(prj_name,center_name,final_work_packet,str(date_is))
                total = RawTable.objects.filter(**query_set).values_list('per_day').aggregate(Sum('per_day'))
                value_dict[str(final_work_packet)] = str(total['per_day__sum'])
                data_dict[redis_key] = value_dict
            if key_type == 'Internal':
                redis_key = '{0}_{1}_{2}_{3}_error'.format(prj_name,center_name,final_work_packet,str(date_is))
                total_audit = Internalerrors.objects.filter(**query_set).values_list('audited_errors').aggregate(Sum('audited_errors'))
                total_errors = Internalerrors.objects.filter(**query_set).values_list('total_errors').aggregate(Sum('total_errors'))
                error_types = Internalerrors.objects.filter(**query_set).values('error_types','error_values')
                total_error_types = different_error_type(error_types)
                value_dict['total_audit'] = str(total_audit['audited_errors__sum'])
                value_dict['total_errors'] = str(total_errors['total_errors__sum'])
                value_dict['types_of_errors'] = json.dumps(total_error_types)
                data_dict[redis_key] = value_dict
            if key_type == 'External':
                redis_key = '{0}_{1}_{2}_{3}_externalerror'.format(prj_name,center_name,final_work_packet,str(date_is))
                total_audit = Externalerrors.objects.filter(**query_set).values_list('audited_errors').aggregate(Sum('audited_errors'))
                total_errors = Externalerrors.objects.filter(**query_set).values_list('total_errors').aggregate(Sum('total_errors'))
                error_types = Externalerrors.objects.filter(**query_set).values('error_types', 'error_values')
                total_error_types = different_error_type(error_types)
                value_dict['total_audit'] = str(total_audit['audited_errors__sum'])
                value_dict['total_errors'] = str(total_errors['total_errors__sum'])
                value_dict['types_of_errors'] = json.dumps(total_error_types)
                data_dict[redis_key] = value_dict
            if key_type == 'WorkTrack':
                redis_key = '{0}_{1}_{2}_{3}_worktrack'.format(prj_name, center_name, final_work_packet,str(date_is))
                #closing_balance = Worktrack.objects.filter(**query_set).values_list('closing_balance')
                closing_balance = Worktrack.objects.filter(**query_set).values_list('closing_balance').aggregate(Sum('closing_balance'))
                #received = Worktrack.objects.filter(**query_set).values_list('received')
                received = Worktrack.objects.filter(**query_set).values_list('received').aggregate(Sum('received'))
                #completed = Worktrack.objects.filter(**query_set).values_list('completed')
                completed = Worktrack.objects.filter(**query_set).values_list('completed').aggregate(Sum('completed'))
                #opening = Worktrack.objects.filter(**query_set).values_list('opening')
                opening = Worktrack.objects.filter(**query_set).values_list('opening').aggregate(Sum('opening'))
                #non_workable_count = Worktrack.objects.filter(**query_set).values_list('non_workable_count')
                non_workable_count = Worktrack.objects.filter(**query_set).values_list('non_workable_count').aggregate(Sum('non_workable_count'))
                try:
                    #value_dict['closing_balance'] = str(closing_balance[0][0])
                    value_dict['closing_balance'] = str(closing_balance['closing_balance__sum'])
                except:
                    value_dict['closing_balance'] = ''
                try:
                    #value_dict['completed'] = str(completed[0][0])
                    value_dict['completed'] = str(completed['completed__sum'])
                except:
                    value_dict['completed'] = ''
                try:
                    #value_dict['opening'] = str(opening[0][0])
                    value_dict['opening'] = str(opening['opening__sum'])
                except:
                    value_dict['opening'] = ''
                try:
                    #value_dict['non_workable_count'] = str(non_workable_count[0][0])
                    value_dict['non_workable_count'] = str(non_workable_count['non_workable_count__sum'])
                except:
                    value_dict['non_workable_count'] = ''
                try:
                    #value_dict['received'] = int(received[0][0])
                    value_dict['received'] = int(received['received__sum'])
                except:
                    value_dict['received'] = ''
                data_dict[redis_key] = value_dict

    conn = redis.Redis(host="localhost", port=6379, db=0)
    current_keys = []
    for key, value in data_dict.iteritems():
        current_keys.append(key)
        conn.hmset(key, value)
    return "hai"


def redis_insert(prj_obj,center_obj,dates_list,key_type):
    wp_count,sub_pct_count,sub_prj_count = 0,0,0
    level_herarchy = []
    wk_packet , wk_packet , sub_prj = [],[],[]
    if key_type == 'Production':
        level_herarchy_packets = RawTable.objects.filter(project=prj_obj, center=center_obj,date__range=[dates_list[0], dates_list[-1]]).values('sub_project','work_packet','sub_packet').distinct()
        wk_packet = [wp_count+1 for key in level_herarchy_packets if len(key['work_packet'])]
        sub_packet = [sub_pct_count+1 for key in level_herarchy_packets if len(key['sub_packet'])]
        sub_prj = [sub_prj_count+1 for key in level_herarchy_packets if len(key['sub_project'])]
    if key_type == 'Internal':
        level_herarchy_packets = Internalerrors.objects.filter(project=prj_obj, center=center_obj,date__range=[dates_list[0], dates_list[-1]]).values('sub_project', 'work_packet', 'sub_packet').distinct()
        wk_packet = [wp_count + 1 for key in level_herarchy_packets if len(key['work_packet'])]
        sub_packet = [sub_pct_count + 1 for key in level_herarchy_packets if len(key['sub_packet'])]
        sub_prj = [sub_prj_count + 1 for key in level_herarchy_packets if len(key['sub_project'])]
    if key_type == 'External':
        level_herarchy_packets = Externalerrors.objects.filter(project=prj_obj, center=center_obj,date__range=[dates_list[0], dates_list[-1]]).values('sub_project', 'work_packet', 'sub_packet').distinct()
        wk_packet = [wp_count + 1 for key in level_herarchy_packets if len(key['work_packet'])]
        sub_packet = [sub_pct_count + 1 for key in level_herarchy_packets if len(key['sub_packet'])]
        sub_prj = [sub_prj_count + 1 for key in level_herarchy_packets if len(key['sub_project'])]
    if key_type == 'WorkTrack':
        level_herarchy_packets = Worktrack.objects.filter(project=prj_obj, center=center_obj,date__range=[dates_list[0], dates_list[-1]]).values('sub_project','work_packet','sub_packet').distinct()
        wk_packet = [wp_count + 1 for key in level_herarchy_packets if len(key['work_packet'])]
        sub_packet = [sub_pct_count + 1 for key in level_herarchy_packets if len(key['sub_packet'])]
        sub_prj = [sub_prj_count + 1 for key in level_herarchy_packets if len(key['sub_project'])]
    if len(wk_packet) > 0 : level_herarchy.append('work_packet')
    if len(sub_packet) > 0: level_herarchy.append('sub_packet')
    if len(sub_prj) > 0: level_herarchy.append('sub_project')

    level_dict ={}
    if len(level_herarchy)  == 3:
        level_dict['level3'] = ['sub_project','work_packet','sub_packet']
        level_dict['level2'] = ['sub_project','work_packet']
        level_dict['level1'] = ['sub_project']
    if len(level_herarchy)  == 2:
        if 'sub_project' in level_herarchy:
            level_dict['level2'] = ['sub_project','work_packet']
            level_dict['level1'] = ['sub_project']
        else :
            level_dict['level2'] = ['work_packet','sub_packet']
            level_dict['level1'] = ['work_packet']
    if len(level_herarchy) == 1:
        if 'sub_project' in level_herarchy:
            level_dict['level1'] = level_dict['level1'] = level_herarchy
        else:
            level_dict['level1'] = level_dict['level1'] = ['work_packet']
    for level_key in level_dict:
        final_inserting = redis_insertion_final(prj_obj, center_obj, dates_list, key_type, level_dict[level_key])
    return "completed"

def redis_insert_old(prj_obj,center_obj,dates_list,key_type):
    prj_name = prj_obj.name
    center_name = center_obj.name
    data_dict = {}
    #dates_list = RawTable.objects.filter(project=prj_obj,center=center_obj).values_list('date').distinct()
    all_dates = []
    for date in dates_list:
        #part_date = str(date[0].date())
        part_date = str(date)
        all_dates.append(part_date)
        #volumes_list = RawTable.objects.filter(date=date[0],project=prj_obj,center=center_obj ).values_list('volume_type').distinct()

        if key_type == 'Production':
            volumes_list = RawTable.objects.filter(project=prj_obj,center=center_obj,date=date ).values('sub_project','work_packet','sub_packet','date').distinct()
        if key_type == 'Internal':
            volumes_list = Internalerrors.objects.filter(project=prj_obj,center=center_obj, date=date).values('sub_project','work_packet','sub_packet', 'date').distinct()
        if key_type == 'External':
            volumes_list = Externalerrors.objects.filter(project=prj_obj, center=center_obj, date=date).values('sub_project', 'work_packet', 'sub_packet', 'date').distinct()
        for row_record_dict in volumes_list:
            single_row_dict={}
            for vol_key,vol_value in row_record_dict.iteritems():
                if vol_value=='':
                    single_row_dict[vol_key]='NA'
                else:
                    single_row_dict[vol_key] =vol_value
            value_dict = {}
            if key_type=='Production':
                redis_key = '{0}_{1}_{2}_{3}_{4}_{5}'.format(prj_name,center_name,single_row_dict['sub_project'],single_row_dict['work_packet'],single_row_dict['sub_packet'],str(single_row_dict['date']))
                total = RawTable.objects.filter(sub_project=row_record_dict['sub_project'],work_packet=row_record_dict['work_packet'],
                                                sub_packet=row_record_dict['sub_packet'],date=date).values_list('per_day').aggregate(Sum('per_day'))
                value_dict[str(single_row_dict['sub_project']+'_'+single_row_dict['work_packet']+'_'+single_row_dict['sub_packet'])] = str(total['per_day__sum'])
                data_dict[redis_key] = value_dict
            if key_type == 'Internal':
                redis_key = '{0}_{1}_{2}_{3}_{4}_{5}_error'.format(prj_name, center_name, single_row_dict['sub_project'],single_row_dict['work_packet'],single_row_dict['sub_packet'], str(single_row_dict['date']))
                total_audit = Internalerrors.objects.filter(sub_project=row_record_dict['sub_project'],
                                                work_packet=row_record_dict['work_packet'],
                                                sub_packet=row_record_dict['sub_packet'], date=date).values_list('audited_errors').aggregate(Sum('audited_errors'))
                total_errors = Internalerrors.objects.filter(sub_project=row_record_dict['sub_project'],
                                                             work_packet=row_record_dict['work_packet'],
                                                             sub_packet=row_record_dict['sub_packet'],
                                                             date=date).values_list('total_errors').aggregate(Sum('total_errors'))
                value_dict['total_audit'] = str(total_audit['audited_errors__sum'])
                value_dict['total_errors'] = str(total_errors['total_errors__sum'])
                data_dict[redis_key] = value_dict
            if key_type == 'External':
                redis_key = '{0}_{1}_{2}_{3}_{4}_{5}_externalerror'.format(prj_name, center_name,single_row_dict['sub_project'],single_row_dict['work_packet'],single_row_dict['sub_packet'], str(single_row_dict['date']))
                total_audit = Externalerrors.objects.filter(sub_project=row_record_dict['sub_project'],
                                                            work_packet=row_record_dict['work_packet'],
                                                            sub_packet=row_record_dict['sub_packet'],
                                                            date=date).values_list('audited_errors').aggregate(Sum('audited_errors'))
                total_errors = Externalerrors.objects.filter(sub_project=row_record_dict['sub_project'],
                                                             work_packet=row_record_dict['work_packet'],
                                                             sub_packet=row_record_dict['sub_packet'],
                                                             date=date).values_list('total_errors').aggregate(Sum('total_errors'))
                value_dict['total_audit'] = str(total_audit['audited_errors__sum'])
                value_dict['total_errors'] = str(total_errors['total_errors__sum'])
                data_dict[redis_key] = value_dict

    conn = redis.Redis(host="localhost", port=6379, db=0)
    current_keys = []
    for key,value in data_dict.iteritems():
        current_keys.append(key)
        conn.hmset(key,value)
    return "hai"



def dropdown_data(request):
    final_dict = {}
    final_dict['level'] = [1,2,3]
    return HttpResponse(final_dict)


def raw_table_query_insertion(customer_data,prj_obj,center_obj,teamleader_obj_name,per_day_value,db_check):
    prod_date_list = customer_data['date']
    new_can = 0
    check_query = RawTable.objects.filter(project=prj_obj, sub_project=customer_data.get('sub_project', ''),
                                          work_packet=customer_data['work_packet'],
                                          sub_packet=customer_data.get('sub_packet', ''),
                                          employee_id=customer_data.get('employee_id', ''), date=customer_data['date'],
                                          center=center_obj).values('per_day','id')
    if len(check_query) == 0:
        new_can = RawTable(project=prj_obj, sub_project=customer_data.get('sub_project', ''),
                           work_packet=customer_data['work_packet'],
                           sub_packet=customer_data.get('sub_packet', ''),
                           employee_id=customer_data.get('employee_id', ''),
                           per_hour=0,
                           per_day=per_day_value, date=customer_data['date'],
                           norm=int(float(customer_data.get('target',0))),
                           team_lead=teamleader_obj_name, center=center_obj)
        if new_can:
            try:
                print customer_data
                new_can.save()
            except:
                print "error in raw_table_query"
    if len(check_query) > 0:
        if db_check == 'aggregate':
            per_day_value = per_day_value + int(check_query[0]['per_day'])
            new_can_agr = RawTable.objects.filter(id=int(check_query[0]['id'])).update(per_day=per_day_value)
        elif db_check == 'update':
            new_can_upd = RawTable.objects.filter(id=int(check_query[0]['id'])).update(per_day=per_day_value)

    return prod_date_list


def internalerror_query_insertion(customer_data, prj_obj, center_obj,teamleader_obj_name, db_check):
    internal_date_list = customer_data['date']
    check_query = Internalerrors.objects.filter(project=prj_obj, sub_project=customer_data.get('sub_project', ''),
                                          work_packet=customer_data['work_packet'],
                                          sub_packet=customer_data.get('sub_packet', ''),
                                          employee_id=customer_data.get('employee_id', ''),date=customer_data['date'],
                                          center=center_obj).values('audited_errors','total_errors', 'id')

    try:
        total_errors = int(float(customer_data['total_errors']))
    except:
        total_errors = 0
    try:
        if customer_data.get('audited_errors', ''):
            audited_count = int(float(customer_data.get('audited_errors', '')))
        else:
            audited_count = 0
    except:
        audited_count = 0

    if len(check_query) == 0:
        new_can = Internalerrors(employee_id=customer_data.get('employee_id', ''),
                                 sub_project=customer_data.get('sub_project', ''),
                                 work_packet=customer_data['work_packet'],
                                 sub_packet=customer_data.get('sub_packet', ''), date=customer_data['date'],
                                 audited_errors=int(float(audited_count)),
                                 total_errors=total_errors,
                                 error_types = customer_data.get('error_types', ''),
                                 error_values = customer_data.get('error_values', ''),
                                 project=prj_obj, center=center_obj)
        if new_can:
            try:
                print customer_data
                new_can.save()
            except:
                print "error in internal_table_query"

    if len(check_query) > 0:
        if db_check == 'aggregate':
            audited_count = audited_count + int(check_query[0]['audited_errors'])
            total_errors = total_errors + int(check_query[0]['total_errors'])
            new_can_agr = Internalerrors.objects.filter(id=int(check_query[0]['id'])).update(audited_errors=audited_count,total_errors=total_errors)
        elif db_check == 'update':
            new_can_upd = Internalerrors.objects.filter(id=int(check_query[0]['id'])).update(audited_errors=audited_count,total_errors=total_errors)
    return internal_date_list



def externalerror_query_insertion(customer_data, prj_obj, center_obj,teamleader_obj_name, db_check):
    external_date_list = customer_data['date']
    new_can = 0
    check_query = Externalerrors.objects.filter(project=prj_obj, sub_project=customer_data.get('sub_project', ''),
                                          work_packet=customer_data['work_packet'],
                                          sub_packet=customer_data.get('sub_packet', ''),
                                          employee_id=customer_data.get('employee_id', ''),date=customer_data['date'],
                                          center=center_obj).values('audited_errors','total_errors', 'id')
    try:
        total_errors = int(float(customer_data['total_errors']))
    except:
        total_errors = 0
    try:
        if customer_data.get('audited_errors', ''):
            audited_count = int(float(customer_data.get('audited_errors', '')))
        else:
            audited_count = 0
    except:
        audited_count = 0
    if len(check_query) == 0:
        new_can = Externalerrors(employee_id=customer_data.get('employee_id', ''),
                                 sub_project=customer_data.get('sub_project', ''),
                                 work_packet=customer_data['work_packet'],
                                 sub_packet=customer_data.get('sub_packet', ''), date=customer_data['date'],
                                 audited_errors=int(float(audited_count)),
                                 total_errors=total_errors,
                                 error_types=customer_data.get('error_types', ''),
                                 error_values=customer_data.get('error_values', ''),
                                 project=prj_obj, center=center_obj)
        if new_can:
            try:
                new_can.save()
            except:
                print "error in external_table_query"
    if len(check_query) > 0:
        if db_check == 'aggregate':
            audited_count = audited_count + int(check_query[0]['audited_errors'])
            total_errors = total_errors + int(check_query[0]['total_errors'])
            new_can_agr = Externalerrors.objects.filter(id=int(check_query[0]['id'])).update(audited_errors=audited_count,total_errors=total_errors)
        elif db_check == 'update':
            new_can_update = Externalerrors.objects.filter(id=int(check_query[0]['id'])).update(audited_errors=audited_count,total_errors=total_errors)

    return external_date_list


def target_table_query_insertion(customer_data,prj_obj,center_obj,teamleader_obj_name,db_check):
    prod_date_list = customer_data['from_date']
    new_can = 0
    check_query = Targets.objects.filter(project=prj_obj, sub_project=customer_data.get('sub_project', ''),
                                          work_packet=customer_data['work_packet'],
                                          sub_packet=customer_data.get('sub_packet', ''),
                                          from_date=customer_data['from_date'],
                                         to_date=customer_data['to_date'],
                                         center=center_obj).values('target','fte_target')

    try:
        target = int(float(customer_data['target']))
    except:
        target = 0
    try:
        fte_target = int(float(customer_data['fte_target']))
    except:
        fte_target = 0

    if len(check_query) == 0:
        new_can = Targets(project=prj_obj, sub_project=customer_data.get('sub_project', ''),
                           work_packet=customer_data['work_packet'],
                           sub_packet=customer_data.get('sub_packet', ''),
                           from_date=customer_data['from_date'],
                           to_date=customer_data['to_date'],
                           target=target,fte_target=fte_target,center=center_obj)
        if new_can:
            try:
                new_can.save()
            except:
                print "error in target_table_query"
    if len(check_query) > 0:
        if db_check == 'aggregate':
            target = target + int(check_query[0]['target'])
            fte_target = fte_target + int(check_query[0]['fte_target'])
            new_can_agr = Targets.objects.filter(id=int(check_query[0]['id'])).update(targer=target,fte_target=fte_target)
        elif db_check == 'update':
            new_can_upd = Targets.objects.filter(id=int(check_query[0]['id'])).update(targer=target,fte_target=fte_target)

    return prod_date_list


def upload(request):
    teamleader_obj_name = TeamLead.objects.filter(name_id=request.user.id)[0]
    teamleader_obj = TeamLead.objects.filter(name_id=request.user.id).values_list('project_id','center_id')[0]
    prj_obj = Project.objects.filter(id=teamleader_obj[0])[0]
    prj_name= prj_obj.name
    center_obj = Center.objects.filter(id=teamleader_obj[1])[0]
    fname = request.FILES['myfile']
    var = fname.name.split('.')[-1].lower()
    if var not in ['xls', 'xlsx', 'xlsb']:
        return HttpResponse("Invalid File")
    else:
        try:
            open_book = open_workbook(filename=None, file_contents=fname.read())
            #open_sheet = open_book.sheet_by_index(0)
        except:
            return HttpResponse("Invalid File")
        excel_sheet_names = open_book.sheet_names()
        file_sheet_names = Authoringtable.objects.filter(project=prj_obj,center=center_obj).values_list('sheet_name',flat=True).distinct()
        #file_sheet_names = [x.encode('UTF8') for x in file_sheet_name]
        sheet_index_dict = {}
        for sh_name in file_sheet_names:
            if sh_name in excel_sheet_names:
                sheet_index_dict[sh_name] = open_book.sheet_names().index(sh_name)
        """
        project_type = Project.objects.filter(name=prj_obj.name,center=center_obj).values_list('project_type',flat=True)
        if len(project_type)>0:
            project_type = str(project_type[0])
        """

        db_check = str(Project.objects.filter(name=prj_obj.name,center=center_obj).values_list('project_db_handling',flat=True)[0])
        sheet_count = Authoringtable.objects.filter(project=prj_obj, center=center_obj).values_list('sheet_name',flat=True).distinct()
        for key,value in sheet_index_dict.iteritems():
            one_sheet_data = {}
            prod_date_list,internal_date_list,external_date_list=[],[],[]
            open_sheet = open_book.sheet_by_index(value)
            SOH_XL_HEADERS = open_sheet.row_values(0)
            main_headers = Authoringtable.objects.filter(sheet_name=key,project=prj_obj,center=center_obj).values_list('sheet_field',flat=True)
            sheet_main_headers = main_headers
            table_schema = Authoringtable.objects.filter(sheet_name=key,project=prj_obj,center=center_obj).values_list('table_schema',flat=True)
            table_name = Authoringtable.objects.filter(sheet_name=key,project=prj_obj,center=center_obj).values_list('table_type',flat=True).distinct()
            if len(table_name) > 0 :
                table_name = str(table_name[0])
            mapping_table = {}
            for sh_filed,t_field in zip(sheet_main_headers,table_schema):
                mapping_table[sh_filed] = t_field
            SOH_XL_MAN_HEADERS = [x.title() for x in main_headers]
            sheet_headers = validate_sheet(open_sheet,request,SOH_XL_HEADERS,SOH_XL_MAN_HEADERS)
            for row_idx in range(1, open_sheet.nrows):
                error_type = {}
                raw_sheet_data = {}
                customer_data = {}
                for column, col_idx in sheet_headers:
                    cell_data = get_cell_data(open_sheet, row_idx, col_idx)
                    column_name = mapping_table.get(column, '')
                    if column in ["date", "from date","to date","audited date"]:
                        cell_data = xlrd.xldate_as_tuple(int(cell_data.split('.')[0]), 0)
                        cell_data = '%s-%s-%s' % (cell_data[0], cell_data[1], cell_data[2])
                        customer_data[column_name] = ''.join(cell_data)
                        raw_sheet_data[column_name] = ''.join(cell_data)
                    elif column !="date," and column in mapping_table.keys():
                        customer_data[column_name] = ''.join(cell_data)
                        raw_sheet_data[column_name] = ''.join(cell_data)

                if prj_name in ['Dellcoding']:
                    if raw_sheet_data['date'] not in one_sheet_data.keys():
                        one_sheet_data[raw_sheet_data['date']]=[raw_sheet_data]
                    else:
                        one_sheet_data[raw_sheet_data['date']].append(raw_sheet_data)
                    if row_idx == (open_sheet.nrows-1):
                        one_sheet = sheet_upload_one(prj_obj, center_obj, teamleader_obj_name, key, one_sheet_data)

                if len(sheet_count) >= 3 :
                    if table_name == 'raw_table':
                        if customer_data.has_key('target') == False:
                            customer_data['target'] = 0
                        try:
                            per_day_value = int(float(customer_data.get('work_done', '')))
                        except:
                            per_day_value = 0
                        raw_table_insert = raw_table_query_insertion(customer_data,prj_obj,center_obj,teamleader_obj_name,per_day_value,db_check)
                        prod_date_list.append(customer_data['date'])
                    if table_name == 'internal_error':
                        try:
                            total_errors = int(float(customer_data['total_errors']))
                        except:
                            total_errors = 0
                        if customer_data.has_key('audited_count') == False:
                            audited_count = 0
                        if customer_data.get('audited_count', '') :
                            audited_count = customer_data.get('audited_count', '')
                        internalerror_insert = internalerror_query_insertion(customer_data, prj_obj, center_obj,teamleader_obj_name, audited_count,total_errors, db_check)
                        internal_date_list.append(customer_data['date'])
                    if table_name == 'external_error':
                        try:
                            total_errors = int(float(customer_data['total_errors']))
                        except:
                            total_errors = 0
                        if customer_data.has_key('audited_count') == False:
                            audited_count = 0
                        if customer_data.get('audited_count', '') :
                            audited_count = customer_data.get('audited_count', '')
                        externalerror_insert = externalerror_query_insertion(customer_data, prj_obj, center_obj,teamleader_obj_name, audited_count,total_errors, db_check)
                        external_date_list.append(customer_data['date'])

                if len(sheet_count) == 2 :
                    if table_name == 'raw_table':
                        if customer_data.has_key('target') == False:
                            customer_data['target'] = 0
                        try:
                            per_day_value = int(float(customer_data.get('work_done', '')))
                        except:
                            per_day_value = 0
                        raw_table_insert = raw_table_query_insertion(customer_data,prj_obj,center_obj,teamleader_obj_name,per_day_value,db_check)
                        prod_date_list.append(customer_data['date'])
                    if table_name == 'internal_external' and customer_data.get('error_type','')== 'Internal':
                        if customer_data.get('audited_count','') :
                            audited_count = customer_data.get('audited_count','')
                        else:
                            try:
                                audited_count = int(float(customer_data['qced_count']))
                            except:
                                audited_count = 0
                        try:
                            total_errors = int(float(customer_data['total_errors']))
                        except:
                            total_errors = 0
                        internalerror_insert = internalerror_query_insertion(customer_data, prj_obj, center_obj,teamleader_obj_name, audited_count,total_errors, db_check)
                        internal_date_list.append(customer_data['date'])
                    if table_name == 'internal_external' and customer_data.get('error_type','')== 'External':
                        if customer_data.get('audited_count','') :
                            audited_count = customer_data.get('audited_count','')
                        else:
                            try:
                                    audited_count = int(float(customer_data['daily_audit']))
                            except:
                                audited_count = 0
                        try:
                            total_errors = int(float(customer_data['total_errors']))
                        except:
                            total_errors = 0
                        externalerror_insert = externalerror_query_insertion(customer_data, prj_obj, center_obj,teamleader_obj_name, audited_count,total_errors, db_check)
                        external_date_list.append(customer_data['date'])


            if len(sheet_count) >= 3:
                if table_name == 'raw_table':
                    prod_date_list =list(set(prod_date_list))
                    insert = redis_insert(prj_obj, center_obj, prod_date_list, key_type='Production')
                if table_name == 'internal_error':
                    internal_date_list = list(set(internal_date_list))
                    insert = redis_insert(prj_obj, center_obj, internal_date_list, key_type='Internal')
                if table_name == 'external_error':
                    external_date_list = list(set(external_date_list))
                    insert = redis_insert(prj_obj, center_obj, external_date_list, key_type='External', )

            if len(sheet_count) == 2:
                prod_date_list = list(set(prod_date_list))
                if table_name == 'raw_table':
                    insert = redis_insert(prj_obj, center_obj, prod_date_list, key_type='Production')
                if table_name == 'internal_external':
                    external_date_list = list(set(external_date_list))
                    internal_date_list = list(set(internal_date_list))
                    insert = redis_insert(prj_obj, center_obj, external_date_list, key_type='External')
                    insert = redis_insert(prj_obj, center_obj, internal_date_list, key_type='Internal')

            var ='hello'
        return HttpResponse(var)

def sheet_upload_one(prj_obj,center_obj,teamleader_obj,key,one_sheet_data):
    customer_data={}
    work_packets = ['CAMC - XRAYS','CAMC']
    new_can = 0
    print one_sheet_data
    for data_key,data_value in one_sheet_data.iteritems():
        internal_errors = {}
        external_errors = {}
        #print data_value
        for data_dict in data_value:
            if data_dict['work_packet'] in work_packets :
                volume_type = '{0}_{1}'.format(data_dict['project'], data_dict['work_packet']).replace(' ','')
                try:
                    per_day_value = int(float(data_dict['count']))
                except:
                    per_day_value = 0
                norm = 833
                new_can = RawTable(project=prj_obj, employee=data_dict.get('emp_id', ''),
                                   volume_type=volume_type, per_hour=0, per_day=per_day_value,
                                   date=data_dict['date'], norm=norm,
                                   team_lead=teamleader_obj, center=center_obj)
                new_can.save()
            if ('Internal' in data_dict['work_packet']):
                internal_errors[data_dict['work_packet']] = data_dict['count']
                internal_errors['volume_type'] = data_dict['project']
            if 'External' in data_dict['work_packet'] :
                external_errors[data_dict['work_packet']] = data_dict['count']
                external_errors['volume_type'] = data_dict['project']
        if internal_errors:
            new_can = Error(employee_id=internal_errors.get('emp_id', ''),
                            volume_type=internal_errors['volume_type'].replace(' ',''),
                            date=data_key, audited_errors=int(float(internal_errors['Internal Audited'])),
                            error_value=int(float(internal_errors['Internal Error'])), project=prj_obj,
                            center=center_obj, error_type=internal_errors.get('error_name',''))
            new_can.save()
        if external_errors :
            new_can = Externalerrors(employee_id=external_errors.get('emp_id', ''),
                                     volume_type=external_errors['volume_type'].replace(' ',''),
                                     date=data_key, audited_errors=int(float(external_errors['External Audited'])),
                                     error_value=int(float(external_errors['External Error'])), project=prj_obj,
                                     center=center_obj, error_type=external_errors.get('error_name',''))
            new_can.save()

def data_pre_processing(customer_data,table_mapping,final_data_set,db_check,ignorable_fields,other_fields,date_name):
    local_dataset = {}
    for raw_key, raw_value in table_mapping.iteritems():
        if '#<>#' in raw_value:
            checking_values = raw_value.split('#<>#')
            if customer_data.has_key(checking_values[0].lower()):
                if customer_data[checking_values[0].lower()] not in ignorable_fields:
                    if (checking_values[1] == '') and (customer_data[checking_values[0]] not in other_fields):
                        local_dataset[raw_key] = customer_data[checking_values[2].lower()]
                    elif customer_data[checking_values[0].lower()] == checking_values[1]:
                        local_dataset[raw_key] = customer_data[checking_values[2].lower()]
                    else:
                        local_dataset[raw_key] = 'not_applicable'

    emp_key = '{0}_{1}_{2}_{3}'.format(local_dataset.get('sub_project', 'NA'),
                                       local_dataset.get('work_packet', 'NA'),
                                       local_dataset.get('sub_packet', 'NA'),
                                       local_dataset.get('employee_id', 'NA'))
    #if 'not_applicable' not in local_dataset.values():
    if final_data_set.has_key(str(customer_data[date_name])):
        if final_data_set[str(customer_data[date_name])].has_key(emp_key):
            for intr_key, intr_value in local_dataset.iteritems():
                if intr_key not in final_data_set[str(customer_data[date_name])][emp_key].keys():
                    final_data_set[str(customer_data[date_name])][emp_key][intr_key] = intr_value
                else:
                    if (intr_key == 'total_errors') or (intr_key == 'audited_errors'):
                        try:
                            intr_value = int(float(intr_value))
                        except:
                            intr_value = 0
                        try:
                            dataset_value = int(float(final_data_set[str(customer_data[date_name])][emp_key][intr_key]))
                        except:
                            dataset_value = 0
                        if db_check == 'aggregate':
                            final_data_set[str(customer_data[date_name])][emp_key][intr_key] = intr_value + dataset_value
                        elif db_check == 'update':
                            final_data_set[str(customer_data[date_name])][emp_key][intr_key] = intr_value
        else:
            final_data_set[str(customer_data[date_name])][emp_key] = local_dataset


def Authoring_mapping(prj_obj,center_obj,model_name):
    table_model = apps.get_model('api', model_name)
    map_query = table_model.objects.filter(project=prj_obj, center=center_obj)
    if len(map_query) > 0:
        map_query = map_query[0].__dict__
    else:
        map_query = {}
    return map_query

def upload_new(request):
    teamleader_obj_name = TeamLead.objects.filter(name_id=request.user.id)[0]
    teamleader_obj = TeamLead.objects.filter(name_id=request.user.id).values_list('project_id','center_id')[0]
    prj_obj = Project.objects.filter(id=teamleader_obj[0])[0]
    prj_name= prj_obj.name
    center_obj = Center.objects.filter(id=teamleader_obj[1])[0]
    fname = request.FILES['myfile']
    var = fname.name.split('.')[-1].lower()
    if var not in ['xls', 'xlsx', 'xlsb']:
        return HttpResponse("Invalid File")
    else:
        try:
            open_book = open_workbook(filename=None, file_contents=fname.read())
            #open_sheet = open_book.sheet_by_index(0)
        except:
            return HttpResponse("Invalid File")

        excel_sheet_names = open_book.sheet_names()
        file_sheet_names = Authoringtable.objects.filter(project=prj_obj,center=center_obj).values_list('sheet_name',flat=True).distinct()
        sheet_names = {}
        raw_table_mapping = {}
        internal_error_mapping = {}
        external_error_mapping = {}
        worktrack_mapping = {}
        headcount_mapping = {}
        target_mapping = {}
        tat_mapping = {}
        ignorablable_fields = []
        other_fileds = []
        authoring_dates = {}
        mapping_ignores = ['project_id','center_id','_state','sheet_name','id','total_errors_require']
        raw_table_map_query = Authoring_mapping(prj_obj,center_obj,'RawtableAuthoring')
        for map_key,map_value in raw_table_map_query.iteritems():
            if map_key == 'sheet_name':
                sheet_names['raw_table_sheet'] = map_value
            if map_value != '' and map_key not in mapping_ignores:
                if map_key == 'ignorable_fileds':
                    ignorablable_fields = map_value.split('#<>#')
                else:
                    raw_table_mapping[map_key]= map_value.lower()
                    if '#<>#' in map_value:
                        required_filed = map_value.split('#<>#')
                        if len(required_filed) >= 2 and required_filed != '':
                            other_fileds.append(required_filed[1])
                if map_key == 'date':
                    authoring_dates['raw_table_date'] = map_value.lower()

        internal_error_map_query  = Authoring_mapping(prj_obj,center_obj,'InternalerrorsAuthoring')
        for map_key,map_value in internal_error_map_query.iteritems():
            if map_key == 'sheet_name':
                sheet_names['internal_error_sheet'] = map_value
            if map_key == 'total_errors_require':
                intrnl_error_check = map_value 
            if map_value != '' and map_key not in mapping_ignores:
                internal_error_mapping[map_key]= map_value.lower()
                if '#<>#' in map_value:
                    required_filed = map_value.split('#<>#')
                    if len(required_filed) >= 2 and required_filed != '':
                        other_fileds.append(required_filed[1])
                if map_key == 'date':
                    authoring_dates['intr_error_date'] = map_value.lower()
        
        external_error_map_query = Authoring_mapping(prj_obj,center_obj,'ExternalerrorsAuthoring')
        for map_key,map_value in external_error_map_query.iteritems():
            if map_key == 'sheet_name':
                sheet_names['external_error_sheet'] = map_value
            if map_key == 'total_errors_require':
                extrnl_error_check = map_value
            if map_value != '' and map_key not in mapping_ignores:
                external_error_mapping[map_key]= map_value.lower()
                if '#<>#' in map_value:
                    required_filed = map_value.split('#<>#')
                    if len(required_filed) >= 2 and required_filed != '':
                        other_fileds.append(required_filed[1])
                if map_key == 'date':
                    authoring_dates['extr_error_date'] = map_value.lower()
        worktrack_map_query = Authoring_mapping(prj_obj,center_obj,'WorktrackAuthoring')
        for map_key,map_value in worktrack_map_query.iteritems():
            if map_key == 'sheet_name':
                sheet_names['worktrack_sheet'] = map_value
            if map_value != '' and map_key not in mapping_ignores:
                worktrack_mapping[map_key]= map_value.lower()
                if '#<>#' in map_value:
                    required_filed = map_value.split('#<>#')
                    other_fileds.append(required_filed[1])
                if map_key == 'date':
                    authoring_dates['worktrack_date'] = map_value.lower()
        headcount_map_query = Authoring_mapping(prj_obj,center_obj,'HeadcountAuthoring')
        for map_key, map_value in headcount_map_query.iteritems():
            if map_key == 'sheet_name':
                sheet_names['headcount_sheet'] = map_value
            if map_value != '' and map_key not in mapping_ignores:
                headcount_mapping[map_key] = map_value.lower()
                if '#<>#' in map_value:
                    required_filed = map_value.split('#<>#')
                    other_fileds.append(required_filed[1])
                if map_key == 'date':
                    authoring_dates['headcount_date'] = map_value.lower()

        target_map_query = Authoring_mapping(prj_obj, center_obj, 'TargetsAuthoring')
        for map_key, map_value in target_map_query.iteritems():
            if map_key == 'sheet_name':
                sheet_names['target_sheet'] = map_value
            if map_value != '' and map_key not in mapping_ignores:
                target_mapping[map_key] = map_value.lower()
                if '#<>#' in map_value:
                    required_filed = map_value.split('#<>#')
                    other_fileds.append(required_filed[1])
                if map_key in ['from_date','to_date']:
                    if map_key == 'from_date':
                        authoring_dates['target_from_date'] = map_value.lower()
                    else:
                        authoring_dates['target_to_date'] = map_value.lower()

        tat_map_query = Authoring_mapping(prj_obj, center_obj, 'TatAuthoring')
        for map_key, map_value in tat_map_query.iteritems():
            if map_key == 'sheet_name':
                sheet_names['tat_sheet'] = map_value
            if map_value != '' and map_key not in mapping_ignores:
                tat_mapping[map_key] = map_value.lower()
                if '#<>#' in map_value:
                    required_filed = map_value.split('#<>#')
                    other_fileds.append(required_filed[1])
                if map_key == 'received_date':
                    authoring_dates['tat_date'] = map_value.lower()
         

        other_fileds = filter(None, other_fileds)
        file_sheet_names = sheet_names.values()
        sheet_index_dict = {}
        for sh_name in file_sheet_names:
            if sh_name in excel_sheet_names:
                sheet_index_dict[sh_name] = open_book.sheet_names().index(sh_name)

        db_check = str(Project.objects.filter(name=prj_obj.name,center=center_obj).values_list('project_db_handling',flat=True)[0])
        raw_table_dataset, internal_error_dataset, external_error_dataset, work_track_dataset,headcount_dataset = {}, {}, {}, {},{}
        target_dataset = {}
        tats_table_dataset = {}
        for key,value in sheet_index_dict.iteritems():
            one_sheet_data = {}
            prod_date_list,internal_date_list,external_date_list=[],[],[]
            open_sheet = open_book.sheet_by_index(value)
            SOH_XL_HEADERS = open_sheet.row_values(0)
            main_headers = []
            mapping_table ={}
            SOH_XL_MAN_HEADERS = [x.title() for x in main_headers]
            sheet_headers = validate_sheet(open_sheet,request,SOH_XL_HEADERS,SOH_XL_MAN_HEADERS)
            for row_idx in range(1, open_sheet.nrows):
                customer_data = {}
                for column, col_idx in sheet_headers:
                    cell_data = get_cell_data(open_sheet, row_idx, col_idx)
                    if column in authoring_dates.values():
                        cell_data = xlrd.xldate_as_tuple(int(cell_data.split('.')[0]), 0)
                        cell_data = '%s-%s-%s' % (cell_data[0], cell_data[1], cell_data[2])
                        customer_data[column] = ''.join(cell_data)
                    elif column != "date" :
                        customer_data[column] = ''.join(cell_data)

                if key == sheet_names['raw_table_sheet']:
                    date_name = authoring_dates['raw_table_date']
                    if not raw_table_dataset.has_key(customer_data[date_name]):
                        raw_table_dataset[str(customer_data[date_name])]={}
                    local_raw_data = {}
                    for raw_key,raw_value in raw_table_mapping.iteritems():
                        if '#<>#' in raw_value:
                            checking_values=raw_value.split('#<>#')
                            if customer_data.has_key(checking_values[0].lower()):
                                if customer_data[checking_values[0].lower()] in ignorablable_fields:
                                    local_raw_data[raw_key] = 'not_applicable'
                                else:
                                    if (checking_values[1] == '') and (customer_data[checking_values[0]] not in other_fileds):
                                        local_raw_data[raw_key] = customer_data[checking_values[2].lower()]
                                    elif customer_data[checking_values[0].lower()] == checking_values[1]:
                                        local_raw_data[raw_key] = customer_data[checking_values[2].lower()]
                                    else:
                                        local_raw_data[raw_key] = 'not_applicable'
                        elif ('#<>#' not in raw_value) and (raw_value in customer_data.keys()):
                            local_raw_data[raw_key] = customer_data[raw_value]

                    emp_key = '{0}_{1}_{2}_{3}'.format(local_raw_data.get('sub_project', 'NA'),
                                                       local_raw_data.get('work_packet', 'NA'),
                                                       local_raw_data.get('sub_packet', 'NA'),
                                                       local_raw_data.get('employee_id', 'NA'))

                    if 'not_applicable' not in local_raw_data.values():
                        if raw_table_dataset.has_key(str(customer_data[date_name])):
                            if raw_table_dataset[str(customer_data[date_name])].has_key(emp_key):
                                for pdct_key,pdct_value in local_raw_data.iteritems():
                                    if pdct_key not in raw_table_dataset[str(customer_data[date_name])][emp_key].keys():
                                        raw_table_dataset[str(customer_data[date_name])][emp_key][pdct_key] = pdct_value
                                    else:
                                        if (pdct_key == 'per_day') :
                                            try:
                                                pdct_value = int(float(pdct_value))
                                            except:
                                                pdct_value = 0
                                            try:
                                                dataset_value = int(float(raw_table_dataset[str(customer_data[date_name])][emp_key][pdct_key]))
                                            except:
                                                dataset_value =0
                                            if db_check == 'aggregate':
                                                raw_table_dataset[str(customer_data[date_name])][emp_key][pdct_key] = pdct_value + dataset_value
                                            elif db_check == 'update':
                                                raw_table_dataset[str(customer_data[date_name])][emp_key][pdct_key] = pdct_value
                            else:
                                raw_table_dataset[str(customer_data[date_name])][emp_key] = local_raw_data


                if key == sheet_names.get('internal_error_sheet',''):
                    date_name = authoring_dates['intr_error_date']
                    if not internal_error_dataset.has_key(customer_data[date_name]):
                        internal_error_dataset[str(customer_data[date_name])] = {}
                    local_internalerror_data= {}
                    intr_error_types = {}
                    for raw_key,raw_value in internal_error_mapping.iteritems():
                        if '#<>#' in raw_value:
                            checking_values = raw_value.split('#<>#')
                            if customer_data.has_key(checking_values[0].lower()):
                                if customer_data[checking_values[0].lower()].lower() == checking_values[1].lower():
                                    local_internalerror_data[raw_key] = customer_data[checking_values[2].lower()]
                                else:
                                    local_internalerror_data[raw_key] = 'not_applicable'

                        elif ('#<>#' not in raw_value) and (raw_value in customer_data.keys()):
                            if (raw_key== 'error_category') or (raw_key== 'error_count'):
                                if customer_data.get(internal_error_mapping['error_category']) != '' :
                                    error_count = customer_data[internal_error_mapping['error_count']]
                                    if error_count == '':
                                        error_count = 0
                                    local_internalerror_data['individual_errors']={}
                                    local_internalerror_data['individual_errors'][customer_data[raw_value]] = error_count
                                else:
                                    local_internalerror_data['individual_errors']={}
                                    local_internalerror_data['individual_errors']['no_data']='no_data'
                            else:
                                local_internalerror_data[raw_key] = customer_data[raw_value]

                    emp_key ='{0}_{1}_{2}_{3}'.format(local_internalerror_data.get('sub_project', 'NA') , local_internalerror_data.get('work_packet','NA') , local_internalerror_data.get('sub_packet', 'NA') , local_internalerror_data.get('employee_id', 'NA'))
                    if 'not_applicable' not in local_internalerror_data.values():
                        if internal_error_dataset.has_key(str(customer_data[date_name])):
                            if internal_error_dataset[str(customer_data[date_name])].has_key(emp_key):
                                if local_internalerror_data.has_key('individual_errors') and internal_error_dataset[str(customer_data[date_name])][emp_key].has_key('individual_errors'):
                                    individual_errors = local_internalerror_data['individual_errors']
                                    individual_errors.update(internal_error_dataset[str(customer_data[date_name])][emp_key]['individual_errors'])
                                    internal_error_dataset[str(customer_data[date_name])][emp_key]['individual_errors'] = local_internalerror_data['individual_errors']
                            else:
                                internal_error_dataset[str(customer_data[date_name])][emp_key]=local_internalerror_data
                    else:
                        na_key = [key_value for key_value in local_internalerror_data.values() if key_value=='not_applicable']
                        if (len(na_key) == 1) and (sheet_names.get('external_error_sheet','')== sheet_names.get('internal_error_sheet','')) and (sheet_names.get('external_error_sheet','')== sheet_names.get('raw_table_sheet','')):
                            if internal_error_dataset[str(customer_data[date_name])].has_key(emp_key):
                                for intr_key,intr_value in local_internalerror_data.iteritems():
                                    if intr_key not in internal_error_dataset[str(customer_data[date_name])][emp_key].keys():
                                        internal_error_dataset[str(customer_data[date_name])][emp_key][intr_key] = intr_value
                            else:
                                for intr_key, intr_value in local_internalerror_data.iteritems():
                                    if intr_value == 'not_applicable':
                                        delete_key = intr_key
                                del local_internalerror_data[delete_key]
                                if 'not_applicable' not in local_internalerror_data.values():
                                    internal_error_dataset[str(customer_data[date_name])][emp_key] = local_internalerror_data

            
                if key == sheet_names.get('external_error_sheet',''):
                    date_name = authoring_dates['extr_error_date']
                    if not external_error_dataset.has_key(customer_data[date_name]):
                        external_error_dataset[str(customer_data[date_name])] = {}
                    local_externalerror_data= {}
                    extr_error_types = {}
                    for raw_key,raw_value in external_error_mapping.iteritems():
                        if '#<>#' in raw_value:
                            checking_values = raw_value.split('#<>#')
                            if customer_data.has_key(checking_values[0].lower()):
                                if customer_data[checking_values[0].lower()].lower() == checking_values[1].lower():
                                    local_externalerror_data[raw_key] = customer_data[checking_values[2].lower()]
                                else:
                                    local_externalerror_data[raw_key] = 'not_applicable'

                        elif ('#<>#' not in raw_value) and (raw_value in customer_data.keys()):
                            if (raw_key== 'error_category') or (raw_key== 'error_count'):
                                if customer_data.get(external_error_mapping['error_category']) != '' :
                                    error_count = customer_data[external_error_mapping['error_count']]
                                    if error_count == '':
                                        error_count = 0
                                    local_externalerror_data['individual_errors']={}
                                    local_externalerror_data['individual_errors'][customer_data[raw_value]] = error_count
                                else:
                                    local_externalerror_data['individual_errors']={}
                                    local_externalerror_data['individual_errors']['no_data']='no_data'
                            else:
                                local_externalerror_data[raw_key] = customer_data[raw_value]

                    emp_key ='{0}_{1}_{2}_{3}'.format(local_externalerror_data.get('sub_project', 'NA') , local_externalerror_data.get('work_packet','NA') , local_externalerror_data.get('sub_packet', 'NA') , local_externalerror_data.get('employee_id', 'NA'))
                    if 'not_applicable' not in local_externalerror_data.values():
                        if external_error_dataset.has_key(str(customer_data[date_name])):
                            if external_error_dataset[str(customer_data[date_name])].has_key(emp_key):
                                if local_externalerror_data.has_key('individual_errors') and external_error_dataset[str(customer_data[date_name])][emp_key].has_key('individual_errors'):
                                    individual_errors = local_externalerror_data['individual_errors']
                                    individual_errors.update(external_error_dataset[str(customer_data[date_name])][emp_key]['individual_errors'])
                                    external_error_dataset[str(customer_data[date_name])][emp_key]['individual_errors'] = local_externalerror_data['individual_errors']
                            else:
                                external_error_dataset[str(customer_data[date_name])][emp_key]=local_externalerror_data
                    else:
                        na_key = [key_value for key_value in local_externalerror_data.values() if key_value=='not_applicable']
                        if (len(na_key) == 1) and (sheet_names.get('external_error_sheet','')== sheet_names.get('internal_error_sheet','')) and (sheet_names.get('external_error_sheet','')== sheet_names.get('raw_table_sheet','')):
                            if external_error_dataset[str(customer_data[date_name])].has_key(emp_key):
                                for extr_key, extr_value in local_externalerror_data.iteritems():
                                    if extr_key not in external_error_dataset[str(customer_data[date_name])][emp_key].keys():
                                        external_error_dataset[str(customer_data[date_name])][emp_key][extr_key] = extr_value
                            else:
                                for intr_key, intr_value in local_externalerror_data.iteritems():
                                    if intr_value == 'not_applicable':
                                        delete_key = intr_key
                                del local_externalerror_data[delete_key]
                                if 'not_applicable' not in local_externalerror_data.values():
                                    external_error_dataset[str(customer_data[date_name])][emp_key] = local_externalerror_data

                if key == sheet_names.get('worktrack_sheet', ''):
                    date_name = authoring_dates['worktrack_date']
                    if not work_track_dataset.has_key(customer_data[date_name]):
                        work_track_dataset[str(customer_data[date_name])] = {}
                    local_worktrack_data = {}
                    for raw_key, raw_value in worktrack_mapping.iteritems():
                        if '#<>#' in raw_value:
                            checking_values = raw_value.split('#<>#')
                            if customer_data.has_key(checking_values[0].lower()):
                                if customer_data[checking_values[0].lower()].lower() == checking_values[1].lower():
                                    local_worktrack_data[raw_key] = customer_data[checking_values[2].lower()]
                                else:
                                    local_worktrack_data[raw_key] = 'not_applicable'

                        elif ('#<>#' not in raw_value) and (raw_value in customer_data.keys()):
                            local_worktrack_data[raw_key] = customer_data[raw_value]

                    emp_key = '{0}_{1}_{2}_{3}'.format(local_worktrack_data.get('sub_project', 'NA'),
                                                       local_worktrack_data.get('work_packet', 'NA'),
                                                       local_worktrack_data.get('sub_packet', 'NA'),
                                                       local_worktrack_data.get('employee_id', 'NA'))
                    if 'not_applicable' not in local_worktrack_data.values():
                        if work_track_dataset.has_key(str(customer_data[date_name])):
                            if work_track_dataset[str(customer_data[date_name])].has_key(emp_key):
                                for extr_key, extr_value in local_worktrack_data.iteritems():
                                    if extr_key not in work_track_dataset[str(customer_data[date_name])][emp_key].keys():
                                        work_track_dataset[str(customer_data[date_name])][emp_key][extr_key] = extr_value
                                    else:
                                        if (extr_key == 'total_errors') or (extr_key == 'audited_errors'):
                                            try:
                                                extr_value = int(float(extr_value))
                                            except:
                                                extr_value = 0
                                            try:
                                                dataset_value = int(float(
                                                    work_track_dataset[str(customer_data[date_name])][emp_key][extr_key]))
                                            except:
                                                dataset_value = 0
                                            if db_check == 'aggregate':
                                                work_track_dataset[str(customer_data[date_name])][emp_key][extr_key] = extr_value + dataset_value
                                            elif db_check == 'update':
                                                work_track_dataset[str(customer_data[date_name])][emp_key][extr_key] = extr_value
                            else:
                                work_track_dataset[str(customer_data[date_name])][emp_key] = local_worktrack_data
                    else:
                        na_key = [key_value for key_value in local_worktrack_data.values() if key_value == 'not_applicable']
                        if (len(na_key) == 1) and (sheet_names.get('external_error_sheet', '') == sheet_names.get('internal_error_sheet','')) and(sheet_names.get('external_error_sheet', '') == sheet_names.get('raw_table_sheet', '')):
                            if external_error_dataset[str(customer_data[date_name])].has_key(emp_key):
                                for extr_key, extr_value in local_worktrack_data.iteritems():
                                    if extr_key not in work_track_dataset[str(customer_data[date_name])][emp_key].keys():
                                        work_track_dataset[str(customer_data[date_name])][emp_key][extr_key] = extr_value
                            else:
                                for intr_key, intr_value in local_worktrack_data.iteritems():
                                    if intr_value == 'not_applicable':
                                        delete_key = intr_key
                                del local_worktrack_data[delete_key]
                                if 'not_applicable' not in local_worktrack_data.values():
                                    work_track_dataset[str(customer_data[date_name])][emp_key] = local_worktrack_data
                    print local_worktrack_data

                if key == sheet_names.get('headcount_sheet', ''):
                    date_name = authoring_dates['headcount_date']
                    if not headcount_dataset.has_key(customer_data[date_name]):
                        headcount_dataset[str(customer_data[date_name])] = {}
                    local_headcount_data = {}
                    for raw_key, raw_value in headcount_mapping.iteritems():
                        if '#<>#' in raw_value:
                            checking_values = raw_value.split('#<>#')
                            if customer_data.has_key(checking_values[0].lower()):
                                if customer_data[checking_values[0].lower()].lower() == checking_values[1].lower():
                                    local_headcount_data[raw_key] = customer_data[checking_values[2].lower()]
                                else:
                                    local_headcount_data[raw_key] = 'not_applicable'

                        elif ('#<>#' not in raw_value) and (raw_value in customer_data.keys()):
                            local_headcount_data[raw_key] = customer_data[raw_value]

                    emp_key = '{0}_{1}_{2}_{3}'.format(local_headcount_data.get('sub_project', 'NA'),
                                                       local_headcount_data.get('work_packet', 'NA'),
                                                       local_headcount_data.get('sub_packet', 'NA'),
                                                       local_headcount_data.get('employee_id', 'NA'))
                    if 'not_applicable' not in local_headcount_data.values():
                        if headcount_dataset.has_key(str(customer_data[date_name])):
                            if headcount_dataset[str(customer_data[date_name])].has_key(emp_key):
                                for extr_key, extr_value in local_headcount_data.iteritems():
                                    if extr_key not in headcount_dataset[str(customer_data[date_name])][emp_key].keys():
                                        headcount_dataset[str(customer_data[date_name])][emp_key][extr_key] = extr_value
                                    else:
                                        if (extr_key == 'total_errors') or (extr_key == 'audited_errors'):
                                            try:
                                                extr_value = int(float(extr_value))
                                            except:
                                                extr_value = 0
                                            try:
                                                dataset_value = int(float(headcount_dataset[str(customer_data[date_name])][emp_key][extr_key]))
                                            except:
                                                dataset_value = 0
                                            if db_check == 'aggregate':
                                                headcount_dataset[str(customer_data[date_name])][emp_key][extr_key] = extr_value + dataset_value
                                            elif db_check == 'update':
                                                headcount_dataset[str(customer_data[date_name])][emp_key][extr_key] = extr_value
                            else:
                                headcount_dataset[str(customer_data[date_name])][emp_key] = local_headcount_data

                if key == sheet_names.get('target_sheet', ''):
                    date_name = authoring_dates['target_from_date']
                    if not target_dataset.has_key(customer_data[date_name]):
                        target_dataset[str(customer_data[date_name])] = {}
                    local_target_data = {}
                    for raw_key, raw_value in target_mapping.iteritems():
                        if '#<>#' in raw_value:
                            checking_values = raw_value.split('#<>#')
                            if customer_data.has_key(checking_values[0].lower()):
                                if customer_data[checking_values[0].lower()].lower() == checking_values[1].lower():
                                    local_target_data[raw_key] = customer_data[checking_values[2].lower()]
                                else:
                                    local_target_data[raw_key] = 'not_applicable'

                        elif ('#<>#' not in raw_value) and (raw_value in customer_data.keys()):
                            local_target_data[raw_key] = customer_data[raw_value]

                    emp_key = '{0}_{1}_{2}_{3}'.format(local_target_data.get('sub_project', 'NA'),
                                                       local_target_data.get('work_packet', 'NA'),
                                                       local_target_data.get('sub_packet', 'NA'),
                                                       local_target_data.get('employee_id', 'NA'))
                    if 'not_applicable' not in local_target_data.values():
                        if target_dataset.has_key(str(customer_data[date_name])):
                            if target_dataset[str(customer_data[date_name])].has_key(emp_key):
                                for extr_key, extr_value in local_target_data.iteritems():
                                    if extr_key not in target_dataset[str(customer_data[date_name])][emp_key].keys():
                                        target_dataset[str(customer_data[date_name])][emp_key][extr_key] = extr_value
                                    else:
                                        if (extr_key == 'total_errors') or (extr_key == 'audited_errors'):
                                            try:
                                                extr_value = int(float(extr_value))
                                            except:
                                                extr_value = 0
                                            try:
                                                dataset_value = int(float(target_dataset[str(customer_data[date_name])][emp_key][extr_key]))
                                            except:
                                                dataset_value = 0
                                            if db_check == 'aggregate':
                                                target_dataset[str(customer_data[date_name])][emp_key][extr_key] = extr_value + dataset_value
                                            elif db_check == 'update':
                                                target_dataset[str(customer_data[date_name])][emp_key][extr_key] = extr_value
                            else:
                                target_dataset[str(customer_data[date_name])][emp_key] = local_target_data

                if key == sheet_names.get('tat_sheet', ''):
                    date_name = authoring_dates['tat_date']
                    if not tats_table_dataset.has_key(customer_data[date_name]):
                        tats_table_dataset[str(customer_data[date_name])] = {}
                    local_tat_data = {}
                    for raw_key, raw_value in tat_mapping.iteritems():
                        if '#<>#' in raw_value:
                            checking_values = raw_value.split('#<>#')
                            if customer_data.has_key(checking_values[0].lower()):
                                if customer_data[checking_values[0].lower()].lower() == checking_values[1].lower():
                                    local_tat_data[raw_key] = customer_data[checking_values[2].lower()]
                                else:
                                    local_tat_data[raw_key] = 'not_applicable'

                        elif ('#<>#' not in raw_value) and (raw_value in customer_data.keys()):
                            local_tat_data[raw_key] = customer_data[raw_value]

                    emp_key = '{0}_{1}_{2}_{3}'.format(local_tat_data.get('sub_project', 'NA'),
                                                       local_tat_data.get('work_packet', 'NA'),
                                                       local_tat_data.get('sub_packet', 'NA'),
                                                       local_tat_data.get('employee_id', 'NA'))
                    if 'not_applicable' not in local_tat_data.values():
                        if tats_table_dataset.has_key(str(customer_data[date_name])):
                            if tats_table_dataset[str(customer_data[date_name])].has_key(emp_key):
                                for extr_key, extr_value in local_tat_data.iteritems():
                                    if extr_key not in tats_table_dataset[str(customer_data[date_name])][emp_key].keys():
                                        tats_table_dataset[str(customer_data[date_name])][emp_key][extr_key] = extr_value
                                    else:
                                        if (extr_key == 'total_errors') or (extr_key == 'audited_errors'):
                                            try:
                                                extr_value = float(extr_value)
                                            except:
                                                extr_value = 0
                                            try:
                                                dataset_value = float(tats_table_dataset[str(customer_data[date_name])][emp_key][extr_key])
                                            except:
                                                dataset_value = 0
                                            if db_check == 'aggregate':
                                                tats_table_dataset[str(customer_data[date_name])][emp_key][extr_key] = extr_value + dataset_value
                                            elif db_check == 'update':
                                                tats_table_dataset[str(customer_data[date_name])][emp_key][extr_key] = extr_value
                            else:
                                tats_table_dataset[str(customer_data[date_name])][emp_key] = local_tat_data
        
        for date_key,date_value in internal_error_dataset.iteritems():
            for emp_key,emp_value in date_value.iteritems():
                emp_data = Error_checking(emp_value,intrnl_error_check)
                #if emp_data['status'] == 'matched':
                internalerror_insert = internalerror_query_insertion(emp_data, prj_obj, center_obj,teamleader_obj_name,db_check)
        for date_key,date_value in external_error_dataset.iteritems():
            for emp_key,emp_value in date_value.iteritems():
                emp_data = Error_checking(emp_value,extrnl_error_check)
                #if emp_data['status'] == 'matched':
                externalerror_insert = externalerror_query_insertion(emp_value, prj_obj, center_obj,teamleader_obj_name,db_check)
        for date_key,date_value in work_track_dataset.iteritems():
            for emp_key,emp_value in date_value.iteritems():
                externalerror_insert = worktrack_query_insertion(emp_value, prj_obj, center_obj,teamleader_obj_name,db_check)
        for date_key, date_value in headcount_dataset.iteritems():
            for emp_key, emp_value in date_value.iteritems():
                headcount_insert = headcount_query_insertion(emp_value, prj_obj, center_obj, teamleader_obj_name,db_check)
        for date_key, date_value in target_dataset.iteritems():
            for emp_key, emp_value in date_value.iteritems():
                externalerror_insert = target_table_query_insertion(emp_value, prj_obj, center_obj, teamleader_obj_name,db_check)

        for date_key, date_value in tats_table_dataset.iteritems():
            for emp_key, emp_value in date_value.iteritems():
                externalerror_insert = tat_query_insertion(emp_value, prj_obj, center_obj, teamleader_obj_name,db_check)  


        for date_key,date_value in raw_table_dataset.iteritems():
            for emp_key,emp_value in date_value.iteritems():
                try:
                    per_day_value = int(float(emp_value.get('per_day', '')))
                except:
                    per_day_value = 0
                raw_table_insert = raw_table_query_insertion(emp_value, prj_obj, center_obj, teamleader_obj_name,per_day_value, db_check)

        if len(raw_table_dataset)>0:
            sorted_dates = dates_sorting(raw_table_dataset)
            insert = redis_insert(prj_obj, center_obj,sorted_dates , key_type='Production')
        if len(internal_error_dataset) > 0:
            sorted_dates = dates_sorting(internal_error_dataset)
            insert = redis_insert(prj_obj, center_obj, sorted_dates, key_type='Internal')
        if len(external_error_dataset):
            sorted_dates = dates_sorting(external_error_dataset)
            insert = redis_insert(prj_obj, center_obj, sorted_dates, key_type='External')
        if len(work_track_dataset) > 0:
            sorted_dates = dates_sorting(work_track_dataset)
            insert = redis_insert(prj_obj, center_obj, sorted_dates, key_type='WorkTrack')
        var ='hello'
        return HttpResponse(var)

def dates_sorting(timestamps):
    dates = [datetime.datetime.strptime(ts, "%Y-%m-%d") for ts in timestamps]
    dates.sort()
    sorted_values = [datetime.datetime.strftime(ts, "%Y-%m-%d") for ts in dates]
    return sorted_values

def Error_checking(employee_data,error_match=False):
    employee_data['status'] = 'mis_match'
    if employee_data.has_key('individual_errors'):
        if employee_data['individual_errors'].has_key('no_data'):
           employee_data['status'] = 'matched' 
        try:
            total_errors = int(float(employee_data['total_errors']))
        except:
            total_errors = 0
        all_error_values = []
        for er_value in employee_data['individual_errors'].values():
            try:
                er_value = int(float(er_value))
            except:
                er_value = 0
            all_error_values.append(er_value)

        if error_match ==True:
            if total_errors == sum(all_error_values):
                all_error_values = [str(value) for value in all_error_values ]
                employee_data['status'] = 'matched'
                error_types='#<>#'.join(employee_data['individual_errors'].keys())
                error_values = '#<>#'.join(all_error_values)
                employee_data['error_types'] = error_types
                employee_data['error_values'] = error_values
            else:
                employee_data['error_types'] = None
                employee_data['error_values'] = 0
        else:
            all_error_values = [str(value) for value in all_error_values]
            error_types = '#<>#'.join(employee_data['individual_errors'].keys())
            error_values = '#<>#'.join(all_error_values)
            employee_data['error_types'] = error_types
            employee_data['error_values'] = error_values 

    return employee_data

def worktrack_query_insertion(customer_data, prj_obj, center_obj,teamleader_obj_name, db_check):
    worktrac_date_list = customer_data['date']
    check_query = Worktrack.objects.filter(project=prj_obj, sub_project=customer_data.get('sub_project', ''),
                                          work_packet=customer_data['work_packet'],
                                          sub_packet=customer_data.get('sub_packet', ''),
                                          date=customer_data['date'],
                                          center=center_obj).values('opening','received', 'non_workable_count','completed','closing_balance')

    try:
        opening = int(float(customer_data['opening']))
    except:
        opening = 0
    try:
        received = int(float(customer_data['received']))
    except:
        received = 0
    try:
        non_workable_count = int(float(customer_data['non_workable_count']))
    except:
        non_workable_count = 0
    try:
        completed = int(float(customer_data['completed']))
    except:
        completed = 0
    try:
        closing_balance = int(float(customer_data['closing_balance']))
    except:
        closing_balance = 0

    if len(check_query) == 0:
        new_can = Worktrack(sub_project=customer_data.get('sub_project', ''),
                            work_packet=customer_data['work_packet'],
                            sub_packet=customer_data.get('sub_packet', ''), date=customer_data['date'],
                            opening=opening,
                            received = received,
                            non_workable_count = non_workable_count,
                            completed = completed,
                            closing_balance = closing_balance,
                            project=prj_obj, center=center_obj)
        if new_can:
            try:
                print customer_data
                new_can.save()
            except:
                print "error in internal_table_query"

    if len(check_query) > 0:
        if db_check == 'aggregate':
            opening = opening + int(check_query[0]['opening'])
            received = received + int(check_query[0]['received'])
            non_workable_count = non_workable_count + int(check_query[0]['non_workable_count'])
            completed = completed + int(check_query[0]['completed'])
            closing_balance = closing_balance + int(check_query[0]['closing_balance'])
            new_can_agr = Worktrack.objects.filter(id=int(check_query[0]['id'])).update(opening=opening,
                            received = received,
                            non_workable_count = non_workable_count,
                            completed = completed,
                            closing_balance = closing_balance,)
        elif db_check == 'update':
            new_can_upd = Internalerrors.objects.filter(id=int(check_query[0]['id'])).update(opening=opening,
                            received = received,
                            non_workable_count = non_workable_count,
                            completed = completed,
                            closing_balance = closing_balance,)
    return worktrac_date_list

def headcount_query_insertion(customer_data, prj_obj, center_obj,teamleader_obj_name, db_check):
    head_date_list = customer_data['date']
    check_query = Headcount.objects.filter(project=prj_obj, sub_project=customer_data.get('sub_project', ''),
                                          work_packet=customer_data.get('work_packet',''),
                                          sub_packet=customer_data.get('sub_packet', ''),
                                          date=customer_data['date'],
                                          center=center_obj).values('billable_hc','billable_agents','buffer_agents','qc_or_qa','teamlead','trainees_and_trainers','managers','mis')

    try:
        billable_hc = float(customer_data['billable_hc'])
    except:
        billable_hc = 0
    try:
        billable_agents = float(customer_data['billable_agents'])
    except:
        billable_agents = 0
    try:
        buffer_agents = float(customer_data['buffer_agents'])
    except:
        buffer_agents = 0
    try:
        qc_or_qa = float(customer_data['qc_or_qa'])
    except:
        qc_or_qa = 0
    try:
        teamlead = float(customer_data['teamlead'])
    except:
        teamlead = 0
    try:
        trainees_and_trainers = float(customer_data['trainees_and_trainers'])
    except:
        trainees_and_trainers = 0
    try:
        managers = float(customer_data['managers'])
    except:
        managers = 0
    try:
        mis = float(customer_data['mis'])
    except:
        mis = 0


    if len(check_query) == 0:
        new_can = Headcount(sub_project=customer_data.get('sub_project', ''),
                            work_packet=customer_data.get('work_packet',''),
                            sub_packet=customer_data.get('sub_packet', ''), date=customer_data['date'],
                            billable_hc = billable_hc,billable_agents = billable_agents,
                            buffer_agents = buffer_agents, qc_or_qa = qc_or_qa,teamlead = teamlead,
                            trainees_and_trainers = trainees_and_trainers, managers = managers,mis = mis,
                            project=prj_obj, center=center_obj)
        if new_can:
            try:
                print customer_data
                new_can.save()
            except:
                print "error in internal_table_query"

    if len(check_query) > 0:
        if db_check == 'aggregate':
            billable_hc = billable_hc + float(check_query[0]['billable_hc'])
            billable_agents = billable_agents + float(check_query[0]['billable_agents'])
            buffer_agents = buffer_agents + float(check_query[0]['buffer_agents'])
            qc_or_qa = qc_or_qa +float(check_query[0]['qc_or_qa'])
            teamlead = teamlead +float(check_query[0]['teamlead'])
            trainees_and_trainers = trainees_and_trainers+float(check_query[0]['trainees_and_trainers'])
            managers = managers+float(check_query[0]['managers'])
            mis = mis + float(check_query[0]['mis'])

            new_can_agr = Headcount.objects.filter(id=int(check_query[0]['id'])).update(billable_hc = billable_hc,
                            billable_agents = billable_agents,buffer_agents = buffer_agents, qc_or_qa = qc_or_qa,teamlead = teamlead,
                            trainees_and_trainers = trainees_and_trainers, managers = managers,mis = mis)

        elif db_check == 'update':
            new_can_agr = Headcount.objects.filter(id=int(check_query[0]['id'])).update(billable_hc = billable_hc,
                            billable_agents = billable_agents,buffer_agents = buffer_agents, qc_or_qa = qc_or_qa,teamlead = teamlead,
                            trainees_and_trainers = trainees_and_trainers, managers = managers,mis = mis)
    return head_date_list


def tat_query_insertion(customer_data, prj_obj, center_obj,teamleader_obj_name, db_check):
    tat_date_list = customer_data['received_date']
    check_query = TatTable.objects.filter(project=prj_obj, sub_project=customer_data.get('sub_project', ''),
                                          work_packet=customer_data['work_packet'],
                                          sub_packet=customer_data.get('sub_packet', ''),
                                          date=customer_data['received_date'],
                                          center=center_obj).values('total_received','met_count','non_met_count','tat_status')

    try:
        total_received = int(float(customer_data['total_received']))
    except:
        total_received = 0
    try:
        met_count = int(float(customer_data['met_count']))
    except:
        met_count = 0
    try:
        non_met_count = int(float(customer_data['non_met_count']))
    except:
        non_met_count = 0
    try:
        tat_status = customer_data['tat_status']
    except:
        tat_status = ''

    if len(check_query) == 0:
        new_can = TatTable(sub_project=customer_data.get('sub_project', ''),
                            work_packet=customer_data['work_packet'],
                            sub_packet=customer_data.get('sub_packet', ''), date=customer_data['received_date'],
                            total_received=total_received,
                            met_count = met_count,
                            non_met_count = non_met_count,
                            tat_status = tat_status,
                            project=prj_obj, center=center_obj)

        if new_can:
            new_can.save()

    if len(check_query) > 0:
        if db_check == 'aggregate':
            total_received = total_received + int(check_query[0]['total_received'])
            met_count = met_count + int(check_query[0]['met_count'])
            non_met_count = non_met_count + int(check_query[0]['non_met_count'])
            new_can_agr = TatTable.objects.filter(id=int(check_query[0]['id'])).update(total_received=total_received,
                                                                                       met_count = met_count,
                                                                                       non_met_count = non_met_count,
                                                                                       tat_status = tat_status,)
        elif db_check == 'update':
            new_can_upd = TatTable.objects.filter(id=int(check_query[0]['id'])).update(total_received=total_received,
                                                                                       met_count = met_count,
                                                                                       non_met_count = non_met_count,)
    return tat_date_list


def user_data(request):
    user_group = request.user.groups.values_list('name',flat=True)[0]
    manager_dict = {}
    if 'Center_Manager' in user_group:
        center_id = Centermanager.objects.filter(name_id=request.user.id).values_list('center_name', flat=True)
        center_name = Center.objects.filter(id = center_id).values_list('name',flat=True)[0]
        project = Center.objects.filter(name = str(center_name)).values_list('project_name_id',flat=True)
        project_names = Project.objects.filter(id__in = project).values_list('name',flat=True)
        manager_dict[center_name]= str(project_names)
    if 'Nextwealth_Manager' in user_group:
        center_id = Nextwealthmanager.objects.filter(id=request.user.id).values_list('center_name')
    return HttpResponse(manager_dict)


def Packet_Alias_Names(prj_id,center_obj,widget_config_name):
    new_pkt_names = {} 
    productivity_series_list = [] 
    widget_id = Widgets.objects.filter(config_name=widget_config_name).values_list('id',flat=True)
    alias_packet_names = []
    if len(widget_id)>0:
        alias_widget_id = Alias_Widget.objects.filter(widget_name_id=widget_id[0],project=prj_id[0]).values_list('id',flat=True)
        if len(alias_widget_id):
            alias_packet_names = Alias_packets.objects.filter(widget_id=alias_widget_id[0]).values('existed_name','alias_name')
    new_pkt_names = {}
    for packet_name in alias_packet_names:
        new_pkt_names[packet_name['existed_name']] = packet_name['alias_name']
    return new_pkt_names


def graph_data_alignment_color(volumes_data,name_key,level_structure_key,prj_id,center_obj,widget_config_name=''):
    packet_color_query = query_set_generation(prj_id[0],center_obj[0],level_structure_key,[]) 
    if level_structure_key.has_key('sub_project'):
        if level_structure_key['sub_project'] == "All":
            colors_list = Color_Mapping.objects.filter(**packet_color_query).values('sub_project','color_code').distinct()
        else:
            if level_structure_key.has_key('work_packet'):
                if level_structure_key['work_packet'] == "All":
                    sub_packets_list = Color_Mapping.objects.filter(**packet_color_query).values_list('sub_packet',flat=True)
                    sub_packets_list = filter(None,sub_packets_list)
                    colors_list = Color_Mapping.objects.filter(**packet_color_query).exclude(sub_packet__in=sub_packets_list).values('sub_project','work_packet','color_code').distinct()
                else:
                    colors_list = Color_Mapping.objects.filter(**packet_color_query).values('sub_project','work_packet','sub_packet','color_code').distinct()
    elif level_structure_key.has_key('work_packet') and len(level_structure_key) == 1:
        if level_structure_key['work_packet'] == "All":
            colors_list = Color_Mapping.objects.filter(**packet_color_query).values('work_packet','sub_packet','color_code').distinct()
            colors_list = [d for d in colors_list if d.get('sub_packet') == '']
        else:
            colors_list = Color_Mapping.objects.filter(**packet_color_query).values('sub_project','work_packet','sub_packet','color_code').distinct()
    elif level_structure_key.has_key('work_packet') and level_structure_key.has_key('sub_packet'):
        colors_list = Color_Mapping.objects.filter(**packet_color_query).values('sub_project','work_packet','sub_packet','color_code').distinct()
    else:
        colors_list = [] 
    color_mapping = {} 
    for local_wp_color in colors_list :
        wp_color = {} 
        for wp_key,wp_value in local_wp_color.iteritems():
            if wp_value != '':
                wp_color[wp_key] = wp_value
        if len(wp_color) == 4:
            key = '{0}_{1}_{2}'.format(wp_color['sub_project'],wp_color['work_packet'],wp_color['sub_packet'])
            color_mapping[key] = wp_color['color_code']
        elif len(wp_color) == 3:
            if wp_color.has_key('sub_project') :
                key = '{0}_{1}'.format(wp_color['sub_project'], wp_color['work_packet'])
                color_mapping[key] = wp_color['color_code']
            else:
                key = '{0}_{1}'.format(wp_color['work_packet'], wp_color['sub_packet'])
                color_mapping[key] = wp_color['color_code']
        elif len(wp_color) == 2:
            item = wp_color.pop('color_code')
            key = wp_color.keys()[0]
            color_mapping[wp_color[key]] = item

    productivity_series_list = []
    new_pkt_names = Packet_Alias_Names(prj_id,center_obj,widget_config_name)

    for vol_name, vol_values in volumes_data.iteritems():
        if isinstance(vol_values, float):
            vol_values = float('%.2f' % round(vol_values, 2))
        prod_dict = {}
        prod_dict['name'] = vol_name.replace('NA_','').replace('_NA','')
        if new_pkt_names.has_key(prod_dict['name']):
            prod_dict['name'] = new_pkt_names[prod_dict['name']]
        """if vol_name in['total_utilization','total_workdone']:
            if vol_name == 'total_utilization':
                prod_dict['name'] = 'Total Utilization'
            elif vol_name == 'total_workdone':
                prod_dict['name'] = 'Total Workdone'"""
        if vol_name in['total_utilization','total_workdone','total_prodictivity']:
            if vol_name == 'total_utilization':
                prod_dict['name'] = 'Total Utilization'
            elif vol_name == 'total_workdone':
                prod_dict['name'] = 'Total Workdone'
            elif vol_name == 'total_prodictivity':
                prod_dict['name'] = 'Total Productivity'
        if vol_name in ['target_line','total_target']:
            prod_dict['dashStyle'] = 'dash'
            if vol_name == 'target_line':
                prod_dict['name'] = 'Target Line'
            elif vol_name == 'total_target':
                prod_dict['name'] = 'Total Target'

        if name_key == 'y':
            prod_dict[name_key] = vol_values
        if name_key == 'data':
            if isinstance(vol_values, list):
                prod_dict[name_key] = vol_values
            else:
                prod_dict[name_key] = [vol_values]
        if vol_name in color_mapping.keys():
            prod_dict['color'] = color_mapping[vol_name]

        productivity_series_list.append(prod_dict)

    return productivity_series_list


def graph_data_alignment(volumes_data,name_key):
    #new_pkt_names = Packet_Alias_Names(prj_id,center_obj,widget_config_name)
    color_coding = {}
    productivity_series_list = []
    for vol_name, vol_values in volumes_data.iteritems():
        if isinstance(vol_values, float):
            vol_values = float('%.2f' % round(vol_values, 2))
        prod_dict = {}
        prod_dict['name'] = vol_name.replace('NA_','').replace('_NA','')
        if name_key == 'y':
            prod_dict[name_key] = vol_values
        if name_key == 'data':
            if isinstance(vol_values, list):
                prod_dict[name_key] = vol_values
            else:
                prod_dict[name_key] = [vol_values]
        if vol_name in color_coding.keys():
            prod_dict['color'] = color_coding[vol_name]
        productivity_series_list.append(prod_dict)

    return productivity_series_list



def graph_data_alignment_other(volumes_data, work_packets, name_key):
    productivity_series_list = {}
    for vol_name, vol_values in volumes_data.iteritems():
        prod_main_dict={}
        prod_main_dict['x_axis']=[vol_name]
        prod_inner_dict = {}
        prod_inner_dict['name'] = vol_name
        prod_inner_dict[name_key] =vol_values
        prod_main_dict['y_axis'] = prod_inner_dict
        # productivity_series_list.append(prod_dict)
        productivity_series_list[vol_name] = prod_main_dict
    if len(work_packets)<=1:
        return productivity_series_list
    if len((work_packets))>=2:
        if work_packets[0] in productivity_series_list.keys() and work_packets[1] in productivity_series_list.keys():
            prod_main_dict = {}
            prod_main_dict['x_axis'] = [work_packets[0],work_packets[1]]
            prod_inner_dict = {}
            prod_inner_dict[work_packets[0]] = productivity_series_list[work_packets[0]]['y_axis']
            prod_inner_dict[work_packets[1]] = productivity_series_list[work_packets[1]]['y_axis']
            prod_main_dict['y_axis'] = prod_inner_dict
            productivity_series_list[work_packets[0]] = prod_main_dict
        return productivity_series_list

def level_hierarchy_key(level_structure_key,vol_type):
    final_work_packet = ''

    if level_structure_key.has_key('sub_project'):
        if vol_type['sub_project'] !='':
            final_work_packet = vol_type['sub_project']
    if level_structure_key.has_key('work_packet'):
        if final_work_packet and vol_type['work_packet'] != '':
            final_work_packet = final_work_packet + '_' + vol_type['work_packet']
        else:
            if vol_type['work_packet'] != '':
                final_work_packet = vol_type['work_packet']
    if level_structure_key.has_key('sub_packet'):
        if vol_type.has_key('sub_packet'):
            if final_work_packet and vol_type['sub_packet'] != '':
                final_work_packet = final_work_packet + '_' + vol_type['sub_packet']
            else:
                if vol_type['sub_packet'] != '':
                    final_work_packet = vol_type['sub_packet']
    return  final_work_packet

def query_set_generation(prj_id,center_obj,level_structure_key,date_list):
    query_set = {}
    query_set['project'] = prj_id
    query_set['center'] = center_obj
    if date_list:
        query_set['date__range'] = [date_list[0], date_list[-1]]
    if level_structure_key.has_key('sub_project'):
        if level_structure_key['sub_project'] != "All":
            query_set['sub_project'] = level_structure_key['sub_project']
    if level_structure_key.has_key('work_packet'):
        if level_structure_key['work_packet'] != "All":
            query_set['work_packet'] = level_structure_key['work_packet']
    if level_structure_key.has_key('sub_packet'):
        if level_structure_key['sub_packet'] != "All":
            query_set['sub_packet'] = level_structure_key['sub_packet']
    return query_set


def target_query_set_generation(prj_id,center_obj,level_structure_key,date_list):
    query_set = {}
    query_set['project'] = prj_id
    query_set['center'] = center_obj
    if date_list:
        #query_set['date__range'] = [date_list[0], date_list[-1]]
        query_set['from_date__lte'] = date_list[0]
        query_set['to_date__gte'] = date_list[-1]
    if level_structure_key.has_key('sub_project'):
        if level_structure_key['sub_project'] != "All":
            query_set['sub_project'] = level_structure_key['sub_project']
    if level_structure_key.has_key('work_packet'):
        if level_structure_key['work_packet'] != "All":
            query_set['work_packet'] = level_structure_key['work_packet']
    if level_structure_key.has_key('sub_packet'):
        if level_structure_key['sub_packet'] != "All":
            query_set['sub_packet'] = level_structure_key['sub_packet']
    return query_set


def production_avg_perday(date_list,prj_id,center_obj,work_packets,level_structure_key):
    work = work_packets
    conn = redis.Redis(host="localhost", port=6379, db=0)
    result = {}
    volumes_dict = {}
    date_values = {}
    prj_name = Project.objects.filter(id=prj_id).values_list('name', flat=True)
    center_name = Center.objects.filter(id=center_obj).values_list('name', flat=True)
    query_set = query_set_generation(prj_id, center_obj, level_structure_key, date_list)
    new_date_list = []
    for date_va in date_list:
        total_done_value = RawTable.objects.filter(project=prj_id, center=center_obj, date=date_va).aggregate(Max('per_day'))
        if total_done_value['per_day__max'] > 0:
            new_date_list.append(date_va)
            if level_structure_key.has_key('sub_project'):
                if level_structure_key['sub_project'] == "All":
                    volume_list = RawTable.objects.filter(**query_set).values('sub_project').distinct()
                else:
                    if level_structure_key.has_key('work_packet'):
                        if level_structure_key['work_packet'] == "All":
                            volume_list = RawTable.objects.filter(**query_set).values('sub_project','work_packet').distinct()
                        else:
                            volume_list = RawTable.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()
            elif level_structure_key.has_key('work_packet') and len(level_structure_key) == 1:
                if level_structure_key['work_packet'] == "All":
                    volume_list = RawTable.objects.filter(**query_set).values('sub_project', 'work_packet').distinct()
                else:
                    volume_list = RawTable.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()
            elif level_structure_key.has_key('work_packet') and level_structure_key.has_key('sub_packet'):
                volume_list = RawTable.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()
            else:
                volume_list = []

            count = 0
            for vol_type in volume_list:
                final_work_packet = level_hierarchy_key(level_structure_key, vol_type)
                if not final_work_packet:
                    final_work_packet = level_hierarchy_key(volume_list[count], vol_type)
                count = count + 1
                date_pattern = '{0}_{1}_{2}_{3}'.format(prj_name[0], str(center_name[0]), str(final_work_packet),date_va)
                key_list = conn.keys(pattern=date_pattern)
                if not key_list:
                    if date_values.has_key(final_work_packet):
                        date_values[final_work_packet].append(0)
                    else:
                        date_values[final_work_packet] = [0]
                for cur_key in key_list:
                    var = conn.hgetall(cur_key)
                    for key, value in var.iteritems():
                        if value == 'None':
                            value = 0
                        if date_values.has_key(key):
                            date_values[key].append(int(value))
                        else:
                            date_values[key] = [int(value)]
    return date_values


def product_total_graph(date_list,prj_id,center_obj,work_packets,level_structure_key):
    work = work_packets
    conn = redis.Redis(host="localhost", port=6379, db=0)
    result = {}
    volumes_dict = {}
    date_values = {}
    #volume_list = RawTable.objects.filter(project=prj_id,center=center_obj).values_list('volume_type', flat=True).distinct()
    prj_name = Project.objects.filter(id=prj_id).values_list('name',flat=True)
    center_name = Center.objects.filter(id=center_obj).values_list('name', flat=True)
    query_set = query_set_generation(prj_id,center_obj,level_structure_key,date_list)
    new_date_list = []
    for date_va in date_list:
        #below code for product,wpf graph
        total_done_value = RawTable.objects.filter(project=prj_id,center=center_obj,date=date_va).aggregate(Max('per_day'))
        if total_done_value['per_day__max'] > 0 :
            new_date_list.append(date_va)
            if level_structure_key.has_key('sub_project'):
                if level_structure_key['sub_project'] == "All":
                    volume_list = RawTable.objects.filter(**query_set).values('sub_project').distinct()
                else:
                    if level_structure_key.has_key('work_packet'):
                        if level_structure_key['work_packet'] == "All":
                            volume_list = RawTable.objects.filter(**query_set).values('sub_project','work_packet').distinct()
                        else:
                            volume_list = RawTable.objects.filter(**query_set).values('sub_project','work_packet','sub_packet').distinct()
            elif level_structure_key.has_key('work_packet') and len(level_structure_key) ==1:
                if level_structure_key['work_packet'] == "All":
                    volume_list = RawTable.objects.filter(**query_set).values('sub_project','work_packet').distinct()
                else:
                    volume_list = RawTable.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()
            elif level_structure_key.has_key('work_packet') and level_structure_key.has_key('sub_packet'):
                volume_list = RawTable.objects.filter(**query_set).values('sub_project','work_packet','sub_packet').distinct()
            else:
                volume_list = []
            """elif level_structure_key.has_key('sub_project') and len(level_structure_key) ==1:
                if level_structure_key['sub_project'] == "All":
                    volume_list = RawTable.objects.filter(**query_set).values('sub_project').distinct()
                else:
                    volume_list = RawTable.objects.filter(**query_set).values('sub_project','work_packet').distinct()"""

            count =0
            for vol_type in volume_list:
                final_work_packet = level_hierarchy_key(level_structure_key,vol_type)
                if not final_work_packet:
                    final_work_packet = level_hierarchy_key(volume_list[count],vol_type)
                count = count+1
                date_pattern = '{0}_{1}_{2}_{3}'.format(prj_name[0], str(center_name[0]), str(final_work_packet), date_va)
                key_list = conn.keys(pattern=date_pattern)
                if not key_list:
                    if date_values.has_key(final_work_packet):
                        date_values[final_work_packet].append(0)
                    else:
                        date_values[final_work_packet] = [0]
                for cur_key in key_list:
                    var = conn.hgetall(cur_key)
                    for key,value in var.iteritems():
                        if value == 'None':
                            value = 0
                        if date_values.has_key(key):
                            date_values[key].append(int(value))
                        else:
                            date_values[key]=[int(value)]

                    volumes_dict['data'] = date_values
                    volumes_dict['date'] = new_date_list
                    result['data'] = volumes_dict

    #below code is to generate productivity chcart format
    try:
        volumes_data = result['data']['data']
    except:
        result['data']={}
        result['data']['data'] = {}
        volumes_data = result['data']['data']
    if None in volumes_data.keys():
        del volumes_data[None]
    #productivity_series_list = graph_data_alignment_other(volumes_data,work,name_key='data')
    #productivity_series_list = graph_data_alignment(volumes_data,name_key='data')
    result['prod_days_data'] = volumes_data
    if 'All' not in level_structure_key.values():
        query_set = query_set_generation(prj_id, center_obj, level_structure_key, [])
        packet_target = Targets.objects.filter(**query_set).values('sub_project', 'work_packet', 'sub_packet', 'target').distinct()
        target_line = []
        if packet_target:
            for date_va in new_date_list:
                target_line.append(int(packet_target[0]['target']))
            if len(result['prod_days_data']) == 1:
                result['prod_days_data']['target_line'] = target_line

    if 'All' not in level_structure_key.values():
        query_set = query_set_generation(prj_id, center_obj, level_structure_key, [])
        packet_targets = Targets.objects.filter(**query_set).values('sub_project', 'work_packet', 'sub_packet', 'target','from_date','to_date').distinct()
        target_line = []
        for target_dates in packet_targets:
            date_range = num_of_days(target_dates['to_date'],target_dates['from_date'])
            target_dates['date_range'] = date_range
        if packet_targets:
            for date_va in new_date_list:
                for target_data in packet_targets:
                    if date_va in target_data['date_range']:
                        target_line.append(int(target_data['target']))
            if len(result['prod_days_data']) == 1:
                result['prod_days_data']['target_line'] = target_line 

    volume_bar_data = {}
    volume_bar_data['volume_type']= volumes_data.keys()
    volume_keys_data ={}
    for key,value in volumes_data.iteritems():
        volume_keys_data[key]= sum(value)
    volume_list_data=[]
    volume_dict = {}

    for key,value in volume_keys_data.iteritems() :
        new_list=[]
        try:
            if 'DetailFinancial' not in key:
                if volume_dict.has_key(key):
                    new_list.append(volume_dict[key])
                else:
                    new_list.append(key)
                new_list.append(value)
                volume_list_data.append(new_list)
        except:
            pass
    volume_bar_data['volume_new_data']=volume_list_data
    volume_bar_data['volume_values'] = volume_keys_data
    result['volumes_data'] = volume_bar_data
    return result

def internal_extrnal_graphs_same_formula(request,date_list,prj_id,center_obj,level_structure_key,err_type):
    prj_name = Project.objects.filter(id=prj_id).values_list('name', flat=True)
    center_name = Center.objects.filter(id=center_obj).values_list('name', flat=True)
    query_set = query_set_generation(prj_id, center_obj, level_structure_key,date_list)
    if err_type =='Internal' :
        extr_volumes_list = worktrack_internal_external_workpackets_list(level_structure_key, 'Internalerrors', query_set)
        err_key_type = 'error'
    if err_type == 'External':
        extr_volumes_list = worktrack_internal_external_workpackets_list(level_structure_key, 'Externalerrors',query_set)
        err_key_type = 'externalerror'
    conn = redis.Redis(host="localhost", port=6379, db=0)
    # below variable for error graphs.
    result = {}
    vol_error_values = {}
    vol_audit_data = {}
    # below variable for external errors
    extrnl_error_values = {}
    extrnl_err_type = {}
    extr_volumes_list_new=[]
    all_error_types = []
    for date_va in date_list:
        count =0
        total_done_value = RawTable.objects.filter(project=prj_id, center=center_obj, date=date_va).aggregate(Max('per_day'))
        #total_done_value= worktrack_internal_external_workpackets_list(level_structure_key, 'RawTable', query_set).aggregate(Max('per_day'))
        if total_done_value['per_day__max'] > 0:
            for vol_type in extr_volumes_list:
                #work_packets = vol_type['work_packet']
                final_work_packet = level_hierarchy_key(level_structure_key, vol_type)
                if not final_work_packet:
                    final_work_packet = level_hierarchy_key(extr_volumes_list[count],vol_type)
                count = count+1
                extr_volumes_list_new.append(final_work_packet)
                key_pattern = '{0}_{1}_{2}_{3}_{4}'.format(prj_name[0], str(center_name[0]), final_work_packet, date_va,err_key_type)
                audit_key_list = conn.keys(pattern=key_pattern)
                if not audit_key_list:
                    if vol_error_values.has_key(final_work_packet):
                        vol_error_values[final_work_packet].append("NA")
                        vol_audit_data[final_work_packet].append("NA")
                    else:
                        vol_error_values[final_work_packet] = ["NA"]
                        vol_audit_data[final_work_packet] = ["NA"]
                for cur_key in audit_key_list:
                    var = conn.hgetall(cur_key)
                    for key, value in var.iteritems():
                        if key == 'types_of_errors':
                            all_error_types.append(value)
                        else:
                            if value == 'None':
                                value = "NA"
                            error_vol_type = final_work_packet
                            if key == 'total_errors':
                                if vol_error_values.has_key(error_vol_type):
                                    if value =="NA":
                                        vol_error_values[error_vol_type].append(value)
                                    else:
                                        vol_error_values[error_vol_type].append(int(value))
                                else:
                                    if value =="NA":
                                        vol_error_values[error_vol_type] = [value]
                                    else:
                                        vol_error_values[error_vol_type] = [int(value)]
                            else:
                                if vol_audit_data.has_key(error_vol_type):
                                    if value=="NA":
                                        vol_audit_data[error_vol_type].append(value)
                                    else:
                                        vol_audit_data[error_vol_type].append(int(value))
                                else:
                                    if value=="NA":
                                        vol_audit_data[error_vol_type] = [value]
                                    else:
                                        vol_audit_data[error_vol_type] = [int(value)]

    indicidual_error_calc = error_types_sum(all_error_types)

    volume_dict = {}
    # error_dist_vol = Error.objects.values_list('volume_type', flat=True).distinct()
    #error_dist_vol = Externalerrors.objects.filter(project=prj_id, center=center_obj).values_list('volume_type',flat=True).distinct()
    error_volume_data = {}
    error_graph_data = []
    for key, value in vol_error_values.iteritems():
        error_filter = [i for i in value if i!='NA']
        error_graph = []
        error_volume_data[key] = sum(error_filter)
        error_graph.append(key)
        error_graph.append(sum(error_filter))
        error_graph_data.append(error_graph)
    error_audit_data = {}
    for key, value in vol_audit_data.iteritems():
        error_filter = [i for i in value if i!='NA']
        error_audit_data[key] = sum(error_filter)
    error_accuracy = {}
    for volume in extr_volumes_list_new:
        if (volume in error_volume_data.keys()) and (volume in error_audit_data.keys()) :
            if error_audit_data[volume] != 0:
                percentage = (float(error_volume_data[volume]) / error_audit_data[volume]) * 100
                percentage = 100 -float('%.2f' % round(percentage, 2))
                error_accuracy[volume] = percentage
            else:
                error_accuracy[volume] = 0
    total_graph_data = {}
    internal_time_line = {}
    for key,value in vol_audit_data.iteritems():
        count =0
        for vol_error_value in value:
            if vol_error_value > 0 and vol_error_values[key][count] !="NA":
                if vol_error_value != "NA":
                    percentage = (float(vol_error_values[key][count]) / vol_error_value) * 100
                    percentage = 100-float('%.2f' % round(percentage, 2))
                else:
                    percentage = 0
            else:
                percentage = "NA"
            if internal_time_line.has_key(key):
                internal_time_line[key].append(percentage)
            else:
                internal_time_line[key] = [percentage]
                internal_time_line[key] = [percentage]
            count= count+1


    range_internal_time_line = {}
    if err_type == 'Internal':
        range_internal_time_line['internal_time_line'] = internal_time_line
        range_internal_time_line['date'] = date_list
        result['internal_error_count'] = error_volume_data
        result['internal_accuracy_graph'] = error_accuracy
        result['internal_time_line'] = range_internal_time_line
        result['internal_time_line_date'] = date_list
        result['internal_pareto_data'] = pareto_data_generation(vol_error_values, internal_time_line)


    if err_type == 'External':
        range_internal_time_line['external_time_line'] = internal_time_line
        range_internal_time_line['date'] = date_list
        result['external_error_count'] = error_volume_data
        result['external_accuracy_graph'] = error_accuracy
        result['external_time_line'] = range_internal_time_line
        result['external_time_line_date'] = date_list
        result['external_pareto_data'] = pareto_data_generation(vol_error_values, internal_time_line)

    return result

    # below code for external graphs

def pareto_data_generation(vol_error_values,internal_time_line):
    result = {}
    volume_error_count = {}
    for key,values in vol_error_values.iteritems():
        new_values = [0 if value=='NA' else value for value in values ]
        volume_error_count[key] = new_values
    volume_error_accuracy = {}
    for key, values in internal_time_line.iteritems():
        error_values = [0 if value=='NA' else value for value in values ]
        volume_error_accuracy[key] = error_values

    result = {}
    result['error_count'] = volume_error_count
    result['error_accuracy'] = volume_error_accuracy
    return result

def externalerror_graph(request,date_list,prj_id,center_obj,packet_sum_data,level_structure_key):
    prj_name = Project.objects.filter(id=prj_id).values_list('name', flat=True)
    center_name = Center.objects.filter(id=center_obj).values_list('name', flat=True)
    query_set = query_set_generation(prj_id, center_obj, level_structure_key,date_list)
    #extr_volumes_list = Externalerrors.objects.filter(**query_set).values('sub_project','work_packet','sub_packet').distinct()
    extr_volumes_list = worktrack_internal_external_workpackets_list(level_structure_key, 'Externalerrors', query_set)
    extr_volumes_list_new = []
    conn = redis.Redis(host="localhost", port=6379, db=0)
    # below variable for error graphs.
    result = {}
    vol_error_values = {}
    vol_audit_data = {}
    # below variable for external errors
    extrnl_error_values = {}
    extrnl_err_type = {}
    all_error_types = []

    for date_va in date_list:
        # below code for internal error
        total_done_value = RawTable.objects.filter(project=prj_id, center=center_obj, date=date_va).aggregate(Max('per_day'))
        if total_done_value['per_day__max'] > 0:
            count =0
            for vol_type in extr_volumes_list:
                final_work_packet = level_hierarchy_key(level_structure_key, vol_type)
                if not final_work_packet:
                    final_work_packet = level_hierarchy_key(extr_volumes_list[count], vol_type)
                count = count + 1

                extr_volumes_list_new.append(final_work_packet)
                extr_key_pattern =  '{0}_{1}_{2}_{3}_externalerror'.format(prj_name[0], str(center_name[0]), final_work_packet, date_va)
                extr_key_list = conn.keys(pattern=extr_key_pattern)
                if not extr_key_list:
                    if extrnl_error_values.has_key(final_work_packet):
                        extrnl_error_values[final_work_packet].append("NA")
                        extrnl_err_type[final_work_packet].append("NA")
                    else:
                        extrnl_error_values[final_work_packet] = ["NA"]
                        extrnl_err_type[final_work_packet] = ["NA"]
                for cur_key in extr_key_list:
                    var = conn.hgetall(cur_key)
                    for key, value in var.iteritems():
                        if key == 'types_of_errors':
                            all_error_types.append(value)
                        else:
                            if value == 'None':
                                value = "NA"
                            error_vol_type = final_work_packet
                            if key == 'total_errors':
                                if extrnl_error_values.has_key(error_vol_type):
                                    if value=="NA":
                                        extrnl_error_values[error_vol_type].append(value)
                                    else:
                                        extrnl_error_values[error_vol_type].append(int(value))
                                else:
                                    if value=="NA":
                                        extrnl_error_values[error_vol_type] = [value]
                                    else:
                                        extrnl_error_values[error_vol_type] = [int(value)]
                            else:
                                if extrnl_err_type.has_key(error_vol_type):
                                    if value=="NA":
                                        extrnl_err_type[error_vol_type].append(value)
                                    else:
                                        extrnl_err_type[error_vol_type].append(int(value))
                                else:
                                    if value=="NA":
                                        extrnl_err_type[error_vol_type] = [value]
                                    else:
                                        extrnl_err_type[error_vol_type] = [int(value)]
    volume_dict = {}
    extrnl_error_sum = {}
    for key, value in extrnl_error_values.iteritems():
        error_filter = [i for i in value if i!='NA']
        extrnl_error_sum[key] = sum(error_filter)

    date_values = {}
    for date_va in date_list:
        #below code for product,wpf graphs
        total_done_value = RawTable.objects.filter(project=prj_id, center=center_obj, date=date_va).aggregate(Max('per_day'))
        if total_done_value['per_day__max'] > 0:
            #volume_list = RawTable.objects.filter(**query_set).values('sub_project','work_packet','sub_packet').distinct()
            volume_list = worktrack_internal_external_workpackets_list(level_structure_key, 'RawTable', query_set)
            count =0
            for vol_type in volume_list:
                final_work_packet = level_hierarchy_key(level_structure_key,vol_type)
                if not final_work_packet:
                    final_work_packet = level_hierarchy_key(volume_list[count],vol_type)
                count = count+1
                date_pattern = '{0}_{1}_{2}_{3}'.format(prj_name[0], str(center_name[0]), str(final_work_packet), date_va)
                key_list = conn.keys(pattern=date_pattern)
                if not key_list:
                    if date_values.has_key(final_work_packet):
                        date_values[final_work_packet].append(0)
                    else:
                        date_values[final_work_packet] = [0]
                for cur_key in key_list:
                    var = conn.hgetall(cur_key)
                    for key,value in var.iteritems():
                        if value == 'None':
                            value = 0
                        if date_values.has_key(key):
                            date_values[key].append(int(value))
                        else:
                            date_values[key]=[int(value)]
    # beow code for external erro accuracy
    #packet_sum_data = packet_sum_data
    date_values_sum = {}
    for key, value in date_values.iteritems():
        production_data = [i for i in value if i!='NA']
        date_values_sum[key] = sum(production_data) 
    extr_err_accuracy = {}
    for er_key, er_value in extrnl_error_sum.iteritems():
        if date_values_sum.has_key(er_key):
            if date_values_sum[er_key] != 0:
                #if packet_sum_data.has_key(er_key):
                #if packet_sum_data[er_key] != 0:
                #percentage = (float(er_value) / packet_sum_data[er_key]) * 100
                percentage = (float(er_value) / date_values_sum[er_key]) * 100
                percentage = 100 - float('%.2f' % round(percentage, 2))
                extr_err_accuracy[er_key] = [percentage]
            else:
                extr_err_accuracy[er_key] = [0]
    #volume_list = RawTable.objects.values_list('volume_type', flat=True).distinct()
    extr_err_acc_name = []
    extr_err_acc_perc = []
    for key, value in extr_err_accuracy.iteritems():
        extr_err_acc_name.append(key)
        extr_err_acc_perc.append(value[0])
    err_type_keys = []
    err_type_avod = []
    err_type_concept = []
    external_time_line = {}
    product_data={}
    for key,value in extrnl_err_type.iteritems():
        count =0
        for vol_error_value in value:
            if date_values.has_key(key):
                if (date_values[key][count] > 0) and (extrnl_error_values[key][count] != 'NA'):
                    percentage = (float(extrnl_error_values[key][count]) / date_values[key][count]) * 100
                    percentage = 100-float('%.2f' % round(percentage, 2))
                else:
                    percentage = "NA"
                if external_time_line.has_key(key):
                    external_time_line[key].append(percentage)
                else:
                    external_time_line[key] = [percentage]
                    external_time_line[key] = [percentage]
            count= count+1
    range_internal_time_line = {}
    range_internal_time_line['external_time_line'] = external_time_line
    range_internal_time_line['date'] = date_list

    result['extr_err_accuracy'] = {}
    #result['extr_err_accuracy']['packets_percntage'] = graph_data_alignment(extr_err_accuracy, name_key='data')
    result['extr_err_accuracy']['packets_percntage'] = extr_err_accuracy
    result['extr_err_accuracy']['extr_err_name'] = extr_err_acc_name
    result['extr_err_accuracy']['extr_err_perc'] = extr_err_acc_perc
    result['external_time_line'] = range_internal_time_line
    result['external_pareto_data'] = pareto_data_generation(extrnl_error_values,external_time_line)

    if 'DFES' in extrnl_error_sum:
        del extrnl_error_sum['DFES']
    result['extrn_error_count'] = graph_data_alignment(extrnl_error_sum, name_key='y')
    # print result
    return result


def agent_pareto_data_generation(request,date_list,prj_id,center_obj,level_structure_key):
    prj_name = Project.objects.filter(id=prj_id).values_list('name', flat=True)
    center_name = Center.objects.filter(id=center_obj).values_list('name', flat=True)
    query_set = query_set_generation(prj_id, center_obj, level_structure_key, date_list)
    extr_volumes_list = Internalerrors.objects.filter(**query_set).values_list('employee_id',flat=True).distinct()
    agent_count = []
    agent_name = {}
    error_count = {}
    count = 0
    for agent in extr_volumes_list:
        #total_errors = Internalerrors.objects.filter(project=prj_id, center=center_obj, employee_id=agent,date__range=[date_list[0], date_list[-1]]).aggregate(Sum('total_errors'))
        total_errors = Internalerrors.objects.filter(project=prj_id, center=center_obj, employee_id=agent,date__range=[date_list[0], date_list[-1]]).aggregate(Sum('total_errors'))
        if total_errors['total_errors__sum'] > 0:
            for key, value in total_errors.iteritems():
                agent_name[agent] = value
        count = count + 1

    error_count = agent_name
    error_sum = sum(error_count.values())
    new_list = []
    new_dict = {}
    accuracy_dict = {}
    accuracy_list = []
    new_emp_list = []
    final_pareto_data = {}
    final_pareto_data['Error Count']={}
    final_pareto_data['Error Count']['Error Count'] =[]
    final_pareto_data['Cumulative %'] = {}
    final_pareto_data['Cumulative %']['Cumulative %'] = []
    error_count_data = []
    for key,value in sorted(error_count.iteritems(), key=lambda (k, v): (-v, k)):
        data_values = []
        data_values.append(key)
        data_values.append(value)
        error_count_data.append(value)
        new_emp_list.append(data_values)

    final_pareto_data['Error Count']['Error Count'] = error_count_data[:10]

    emp_error_count = 0
    for key, value in sorted(error_count.iteritems(), key=lambda (k, v): (-v, k)):
        data_list = []
        emp_error_count = emp_error_count +value
        data_list.append(key)
        data_list.append(emp_error_count)
        new_list.append(data_list)
    new_dict.update(new_list)
    for key, value in new_dict.iteritems():
        if error_sum > 0:
            accuracy = (float(float(value)/float(error_sum)))*100
            accuracy_perc = float('%.2f' % round(accuracy, 2))
            accuracy_dict[key] = accuracy_perc
        else:
            accuracy_dict[key] = 0
    error_accuracy = []
    final_emps = []
    for key, value in sorted(accuracy_dict.iteritems(), key=lambda (k, v): (v, k)):
        acc_list = []
        #acc_list.append(key)
        final_emps.append(key)
        #acc_list.append(value)
        error_accuracy.append(value)
        #accuracy_list.append(acc_list)
    final_pareto_data['Cumulative %']['Cumulative %'] = error_accuracy[:10]

    final_data = pareto_graph_data(final_pareto_data)
    result = {}
    result['emp_names'] = final_emps[:10]
    result ['agent_pareto_data'] = final_data

    return result


def agent_external_pareto_data_generation(request,date_list,prj_id,center_obj,level_structure_key):
    prj_name = Project.objects.filter(id=prj_id).values_list('name', flat=True)
    center_name = Center.objects.filter(id=center_obj).values_list('name', flat=True)
    query_set = query_set_generation(prj_id, center_obj, level_structure_key, date_list)
    extrnal_volumes_list = Externalerrors.objects.filter(**query_set).values_list('employee_id',flat=True).distinct()
    agent_count = []
    extrnl_agent_name = {}
    extrnl_error_count = {}
    count = 0
    for agent in extrnal_volumes_list:
        #total_errors = Externalerrors.objects.filter(project=prj_id, center=center_obj, employee_id=agent,date__range=[date_list[0], date_list[-1]]).aggregate(Sum('total_errors'))
        total_errors = Externalerrors.objects.filter(project=prj_id, center=center_obj, employee_id=agent,date__range=[date_list[0], date_list[-1]]).aggregate(Sum('total_errors'))
        if total_errors['total_errors__sum'] > 0:
            for key, value in total_errors.iteritems():
                extrnl_agent_name[agent] = value
        count = count + 1

    extrnl_error_count = extrnl_agent_name
    extrnl_error_sum = sum(extrnl_error_count.values())
    new_list = []
    new_extrnl_dict = {}
    extrnl_accuracy_dict = {}
    final_pareto_data = {}
    final_pareto_data['Error Count']={}
    final_pareto_data['Error Count']['Error Count'] =[]
    final_pareto_data['Cumulative %'] = {}
    final_pareto_data['Cumulative %']['Cumulative %'] = []
    extrnl_error_count_data = []
    for key,value in sorted(extrnl_error_count.iteritems(), key=lambda (k, v): (-v, k)):
        extrnl_error_count_data.append(value)

    final_pareto_data['Error Count']['Error Count'] = extrnl_error_count_data[:10]

    emp_error_count = 0
    for key, value in sorted(extrnl_error_count.iteritems(), key=lambda (k, v): (-v, k)):
        data_list = []
        emp_error_count = emp_error_count +value
        data_list.append(key)
        data_list.append(emp_error_count)
        new_list.append(data_list)
    new_extrnl_dict.update(new_list)

    #import pdb;pdb.set_trace()
    for key, value in new_extrnl_dict.iteritems():
        if extrnl_error_sum > 0:
            accuracy = (float(float(value)/float(extrnl_error_sum)))*100
            accuracy_perc = float('%.2f' % round(accuracy, 2))
            extrnl_accuracy_dict[key] = accuracy_perc
        else: 
            extrnl_accuracy_dict[key] = 0
    
    extrnl_error_accuracy = []
    final_emps = []
    for key, value in sorted(extrnl_accuracy_dict.iteritems(), key=lambda (k, v): (v, k)):
        final_emps.append(key)
        extrnl_error_accuracy.append(value)

    final_pareto_data['Cumulative %']['Cumulative %'] = extrnl_error_accuracy[:10]
    final_data = pareto_graph_data(final_pareto_data)
    result_dict = {}
    result_dict['emp_names'] = final_emps[:10]
    result_dict ['agent_pareto_data'] = final_data
    return result_dict


def sample_pareto_analysis(request,date_list,prj_id,center_obj,level_structure_key,err_type):
    prj_name = Project.objects.filter(id=prj_id).values_list('name', flat=True)
    center_name = Center.objects.filter(id=center_obj).values_list('name', flat=True)
    query_set = query_set_generation(prj_id, center_obj, level_structure_key,date_list)
    if err_type =='Internal' :
        #extr_volumes_list = Internalerrors.objects.filter(**query_set).values('sub_project','work_packet','sub_packet').distinct()
        extr_volumes_list = worktrack_internal_external_workpackets_list(level_structure_key, 'Internalerrors',query_set)
        err_key_type = 'error'
    if err_type == 'External':
        #extr_volumes_list = Externalerrors.objects.filter(**query_set).values('sub_project','work_packet','sub_packet').distinct()
        extr_volumes_list = worktrack_internal_external_workpackets_list(level_structure_key, 'Externalerrors',query_set)
        err_key_type = 'externalerror'
    conn = redis.Redis(host="localhost", port=6379, db=0)
    result = {}
    vol_error_values = {}
    vol_audit_data = {}
    extrnl_error_values = {}
    extrnl_err_type = {}
    extr_volumes_list_new=[]
    all_error_types = []
    for date_va in date_list:
        count =0
        total_done_value = RawTable.objects.filter(project=prj_id, center=center_obj, date=date_va).aggregate(Max('per_day'))
        if total_done_value['per_day__max'] > 0:
            for vol_type in extr_volumes_list:
                final_work_packet = level_hierarchy_key(level_structure_key, vol_type)
                if not final_work_packet:
                    final_work_packet = level_hierarchy_key(extr_volumes_list[count],vol_type)
                count = count+1
                extr_volumes_list_new.append(final_work_packet)
                key_pattern = '{0}_{1}_{2}_{3}_{4}'.format(prj_name[0], str(center_name[0]), final_work_packet, date_va,err_key_type)
                audit_key_list = conn.keys(pattern=key_pattern)
                if not audit_key_list:
                    if vol_error_values.has_key(final_work_packet):
                        vol_error_values[final_work_packet].append("NA")
                        vol_audit_data[final_work_packet].append("NA")
                    else:
                        vol_error_values[final_work_packet] = ["NA"]
                        vol_audit_data[final_work_packet] = ["NA"]
                for cur_key in audit_key_list:
                    var = conn.hgetall(cur_key)
                    for key, value in var.iteritems():
                        if key == 'types_of_errors':
                            all_error_types.append(value)
                        else:
                            if value == 'None':
                                value = "NA"
                            error_vol_type = final_work_packet
                            #if key == 'total_errors':
                            if key == 'error_values':
                                if vol_error_values.has_key(error_vol_type):
                                    if value =="NA":
                                        vol_error_values[error_vol_type].append(value)
                                    else:
                                        vol_error_values[error_vol_type].append(int(value))
                                else:
                                    if value =="NA":
                                        vol_error_values[error_vol_type] = [value]
                                    else:
                                        vol_error_values[error_vol_type] = [int(value)]
                            else:
                                if vol_audit_data.has_key(error_vol_type):
                                    if value=="NA":
                                        vol_audit_data[error_vol_type].append(value)
                                    else:
                                        vol_audit_data[error_vol_type].append(int(value))
                                else:
                                    if value=="NA":
                                        vol_audit_data[error_vol_type] = [value]
                                    else:
                                        vol_audit_data[error_vol_type] = [int(value)]

    accuracy_cate_dict = {}
    accuracy_cate_list = []
    final_external_pareto_data = {}
    final_external_pareto_data['Error Count'] = {}
    final_external_pareto_data['Error Count']['Error Count'] = []
    final_external_pareto_data['Cumulative %'] = {}
    final_external_pareto_data['Cumulative %']['Cumulative %'] = []

    indicidual_error_calc = error_types_sum(all_error_types)
    error_cate_sum = sum(indicidual_error_calc.values())
    error_list = []
    cate_count = 0
    new_cate_dict = {}
    cate_data_values = []
    for key, value in sorted(indicidual_error_calc.iteritems(), key=lambda (k, v): (-v, k)):
        err_list = []
        cate_count = cate_count + value
        err_list.append(key)
        err_list.append(cate_count)
        cate_data_values.append(value)
        error_list.append(err_list)
    new_cate_dict.update(error_list)

    final_external_pareto_data['Error Count']['Error Count'] = cate_data_values[:10]

    cate_accuracy_list = []
    final_cate_list = []
    cate_accuracy_dict = {}
    for key, value in new_cate_dict.iteritems():
        if error_cate_sum > 0:
            accuracy = (float(float(value) / float(error_cate_sum))) * 100
            accuracy_perc = float('%.2f' % round(accuracy, 2))
            cate_accuracy_dict[key] = accuracy_perc
        else:
            cate_accuracy_dict[key] = 100

    error_accuracy = []
    final_cate_list = []
    for key, value in sorted(cate_accuracy_dict.iteritems(), key=lambda (k, v): (v, k)):
        acc_list = []
        final_cate_list.append(key)
        cate_accuracy_list.append(value)
    final_external_pareto_data['Cumulative %']['Cumulative %'] = cate_accuracy_list[:10]
    final_external_data = pareto_graph_data(final_external_pareto_data)
    result = {}
    result['category_name'] = final_cate_list[:10]
    result['category_pareto'] = final_external_data
    return result



def external_internal_without_audit_graph(request,date_list,prj_id,center_obj,packet_sum_data,level_structure_key,err_type):
    prj_name = Project.objects.filter(id=prj_id).values_list('name', flat=True)
    center_name = Center.objects.filter(id=center_obj).values_list('name', flat=True)
    query_set = query_set_generation(prj_id, center_obj, level_structure_key,date_list)
    if err_type == 'Internal':
        #extr_volumes_list = Internalerrors.objects.filter(**query_set).values('sub_project','work_packet','sub_packet').distinct()
        extr_volumes_list = worktrack_internal_external_workpackets_list(level_structure_key, 'Internalerrors', query_set)
        err_key_type = 'error'
    if err_type == 'External':
        #extr_volumes_list = Externalerrors.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()
        extr_volumes_list = worktrack_internal_external_workpackets_list(level_structure_key, 'Externalerrors', query_set)
        err_key_type = 'externalerror'
    extr_volumes_list_new = []
    conn = redis.Redis(host="localhost", port=6379, db=0)
    # below variable for error graphs.
    result = {}
    vol_error_values = {}
    vol_audit_data = {}
    # below variable for external errors
    extrnl_error_values = {}
    extrnl_err_type = {}
    all_error_types = []
    for date_va in date_list:
        # below code for internal error
        total_done_value = RawTable.objects.filter(project=prj_id, center=center_obj, date=date_va).aggregate(Max('per_day'))
        #total_done_value = worktrack_internal_external_workpackets_list(level_structure_key, 'RawTable',query_set).aggregate(Max('per_day'))
        if total_done_value['per_day__max'] > 0:
            count =0
            for vol_type in extr_volumes_list:
                final_work_packet = level_hierarchy_key(level_structure_key, vol_type)
                if not final_work_packet:
                    final_work_packet = level_hierarchy_key(extr_volumes_list[count], vol_type)
                count = count + 1

                extr_volumes_list_new.append(final_work_packet)
                extr_key_pattern =  '{0}_{1}_{2}_{3}_{4}'.format(prj_name[0], str(center_name[0]), final_work_packet, date_va,err_key_type)
                extr_key_list = conn.keys(pattern=extr_key_pattern)
                if not extr_key_list:
                    if extrnl_error_values.has_key(final_work_packet):
                        extrnl_error_values[final_work_packet].append("NA")
                        extrnl_err_type[final_work_packet].append("NA")
                    else:
                        extrnl_error_values[final_work_packet] = ["NA"]
                        extrnl_err_type[final_work_packet] = ["NA"]
                for cur_key in extr_key_list:
                    var = conn.hgetall(cur_key)
                    for key, value in var.iteritems():
                        if key == 'types_of_errors':
                            all_error_types.append(value)
                        else:
                            if value == 'None':
                                value = "NA"
                            error_vol_type = final_work_packet
                            if key == 'total_errors':
                                if extrnl_error_values.has_key(error_vol_type):
                                    if value=="NA":
                                        extrnl_error_values[error_vol_type].append(value)
                                    else:
                                        extrnl_error_values[error_vol_type].append(int(value))
                                else:
                                    if value=="NA":
                                        extrnl_error_values[error_vol_type] = [value]
                                    else:
                                        extrnl_error_values[error_vol_type] = [int(value)]
                            else:
                                if extrnl_err_type.has_key(error_vol_type):
                                    if value=="NA":
                                        extrnl_err_type[error_vol_type].append(value)
                                    else:
                                        extrnl_err_type[error_vol_type].append(int(value))
                                else:
                                    if value=="NA":
                                        extrnl_err_type[error_vol_type] = [value]
                                    else:
                                        extrnl_err_type[error_vol_type] = [int(value)]
    volume_dict = {}
    extrnl_error_sum = {}
    for key, value in extrnl_error_values.iteritems():
        error_filter = [i for i in value if i!='NA']
        extrnl_error_sum[key] = sum(error_filter)

    date_values = {}
    for date_va in date_list:
        #below code for product,wpf graphs
        total_done_value = RawTable.objects.filter(project=prj_id, center=center_obj, date=date_va).aggregate(Max('per_day'))
        if total_done_value['per_day__max'] > 0:
            volume_list = RawTable.objects.filter(**query_set).values('sub_project','work_packet','sub_packet').distinct()
            count =0
            for vol_type in extr_volumes_list:
                final_work_packet = level_hierarchy_key(level_structure_key,vol_type)
                if not final_work_packet:
                    final_work_packet = level_hierarchy_key(volume_list[count],vol_type)
                count = count+1
                date_pattern = '{0}_{1}_{2}_{3}'.format(prj_name[0], str(center_name[0]), str(final_work_packet), date_va)
                key_list = conn.keys(pattern=date_pattern)
                if not key_list:
                    if date_values.has_key(final_work_packet):
                        date_values[final_work_packet].append(0)
                    else:
                        date_values[final_work_packet] = [0]
                for cur_key in key_list:
                    var = conn.hgetall(cur_key)
                    for key,value in var.iteritems():
                        if value == 'None':
                            value = 0
                        if date_values.has_key(key):
                            date_values[key].append(int(value))
                        else:
                            date_values[key]=[int(value)]
    # beow code for external erro accuracy
    packet_sum_data = packet_sum_data
    extr_err_accuracy = {}
    for er_key, er_value in extrnl_error_sum.iteritems():
        if packet_sum_data.has_key(er_key):
            if packet_sum_data[er_key] != 0:
                percentage = (float(er_value) / packet_sum_data[er_key]) * 100
                percentage = 100 - float('%.2f' % round(percentage, 2))
                extr_err_accuracy[er_key] = percentage
            else:
                extr_err_accuracy[er_key] = 0
    #volume_list = RawTable.objects.values_list('volume_type', flat=True).distinct()
    extr_err_acc_name = []
    extr_err_acc_perc = []
    """for key, value in extr_err_accuracy.iteritems():
        extr_err_acc_name.append(key)
        extr_err_acc_perc.append(value[0])"""
    err_type_keys = []
    err_type_avod = []
    err_type_concept = []
    external_time_line = {}
    product_data={}
    for key,value in extrnl_err_type.iteritems():
        count =0
        for vol_error_value in value:
            if date_values.has_key(key):
                if (date_values[key][count] > 0) and (extrnl_error_values[key][count] != 'NA'):
                    percentage = (float(extrnl_error_values[key][count]) / date_values[key][count]) * 100
                    percentage = 100-float('%.2f' % round(percentage, 2))
                else:
                    percentage = "NA"
                if external_time_line.has_key(key):
                    external_time_line[key].append(percentage)
                else:
                    external_time_line[key] = [percentage]
                    external_time_line[key] = [percentage]
            count= count+1
    range_internal_time_line = {}
    if err_type == 'Internal':
        range_internal_time_line['internal_time_line'] = external_time_line
        range_internal_time_line['date'] = date_list
        result['intr_err_accuracy'] = {}
        #result['intr_err_accuracy']['packets_percntage'] = extr_err_accuracy
        result['internal_accuracy_graph'] = extr_err_accuracy
        #result['intr_err_accuracy']['extr_err_name'] = extr_err_acc_name
        #result['intr_err_accuracy']['extr_err_perc'] = extr_err_acc_perc
        result['internal_time_line'] = range_internal_time_line
        result['internal_pareto_data'] = pareto_data_generation(extrnl_error_values,external_time_line)

    if err_type == 'External':
        range_internal_time_line['external_time_line'] = external_time_line
        range_internal_time_line['date'] = date_list
        result['extr_err_accuracy'] = {}
        result['extr_err_accuracy']['packets_percntage'] = extr_err_accuracy
        result['extr_err_accuracy']['extr_err_name'] = extr_err_acc_name
        result['extr_err_accuracy']['extr_err_perc'] = extr_err_acc_perc
        result['external_time_line'] = range_internal_time_line
        result['external_pareto_data'] = pareto_data_generation(extrnl_error_values,external_time_line)

    if 'DFES' in extrnl_error_sum:
        del extrnl_error_sum['DFES']
    result['extrn_error_count'] = graph_data_alignment(extrnl_error_sum, name_key='y')
    # print result
    return result



def internal_extrnal_graphs(request,date_list,prj_id,center_obj,packet_sum_data,level_structure_key):
    prj_name = Project.objects.filter(id=prj_id).values_list('name', flat=True)
    center_name = Center.objects.filter(id=center_obj).values_list('name', flat=True)
    if prj_name[0] in ['']:
        final_internal_data = external_internal_without_audit_graph(request, date_list, prj_id, center_obj, packet_sum_data,level_structure_key,err_type='Internal')
    else:
        final_internal_data = internal_extrnal_graphs_same_formula(request, date_list, prj_id, center_obj,level_structure_key,err_type='Internal')
    if prj_name[0] in ['NTT DATA Services TP','NTT DATA Services Coding','Mobius','Gooru','3iKYC','Bigbasket','Sulekha','Tally','Nextwealth','Wipro','Federal Bank','E4U','indix','Walmart Chittor','Walmart']:
        final_external_data = internal_extrnal_graphs_same_formula(request, date_list, prj_id, center_obj,level_structure_key,err_type='External')
        final_internal_data.update(final_external_data)
        return final_internal_data

    elif prj_name[0] in ['Probe','Ujjivan','IBM','IBM Africa','IBM SEA','IBM Quality Control','IBM Pakistan','IBM NA and EU','IBM Latin America','IBM India and Srilanka','IBM DCIW']:
        #final_internal_data = internal_extrnal_graphs_same_formula(request, date_list, prj_id, center_obj,level_structure_key, err_type='Internal')
        final_external_data = externalerror_graph(request, date_list, prj_id, center_obj,packet_sum_data,level_structure_key)
        final_internal_data.update(final_external_data)
        return final_internal_data
    else:
        final_external_data = internal_extrnal_graphs_same_formula(request, date_list, prj_id, center_obj,level_structure_key,err_type='External')
        final_internal_data.update(final_external_data)
        return final_internal_data


    """if prj_name[0] in ['Ujjivan']:
        final_external_data = internalerror_graph(request, date_list, prj_id, center_obj, packet_sum_data,level_structure_key)
        #final_external_data = internalerror_graph(request, date_list, prj_id, center_obj, packet_sum_data,level_structure_key, err_type='External')
        #final_internal_data.update(final_external_data)
        #return final_internal_data
        return final_external_data"""
    #return result


def errors_week_calcuations(week_names,internal_accuracy_timeline,final_internal_accuracy_timeline):
    for prodct_key, prodct_value in internal_accuracy_timeline.iteritems():
        for vol_key, vol_values in prodct_value.iteritems():
            error_pers = [i for i in vol_values if i != 'NA']
            if len(error_pers) > 0:
                int_errors = float(sum(error_pers)) / len(error_pers)
                int_errors = float('%.2f' % round(int_errors, 2))
            else:
                int_errors = 0
            internal_accuracy_timeline[prodct_key][vol_key] = int_errors

    for final_key, final_value in internal_accuracy_timeline.iteritems():
        for week_key, week_value in final_value.iteritems():
            if week_key not in final_internal_accuracy_timeline.keys():
                final_internal_accuracy_timeline[week_key] = []
    for prod_week_num in week_names:
        if len(internal_accuracy_timeline[prod_week_num]) > 0:
            for vol_key, vol_values in internal_accuracy_timeline[prod_week_num].iteritems():
                if final_internal_accuracy_timeline.has_key(vol_key):
                    final_internal_accuracy_timeline[vol_key].append(vol_values)
                else:
                    final_internal_accuracy_timeline[vol_key] = [vol_values]
            for prod_key, prod_values in final_internal_accuracy_timeline.iteritems():
                if prod_key not in internal_accuracy_timeline[prod_week_num].keys():
                    final_internal_accuracy_timeline[prod_key].append(0)
        else:
            for vol_key, vol_values in final_internal_accuracy_timeline.iteritems():
                final_internal_accuracy_timeline[vol_key].append(0)
    return final_internal_accuracy_timeline



def errors_week_calcuations(week_names,internal_accuracy_timeline,final_internal_accuracy_timeline):
    for prodct_key, prodct_value in internal_accuracy_timeline.iteritems():
        for vol_key, vol_values in prodct_value.iteritems():
            error_pers = [i for i in vol_values if i != 'NA']
            if len(error_pers) > 0:
                int_errors = float(sum(error_pers)) / len(error_pers)
                int_errors = float('%.2f' % round(int_errors, 2))
            else:
                int_errors = 0
            internal_accuracy_timeline[prodct_key][vol_key] = int_errors

    for final_key, final_value in internal_accuracy_timeline.iteritems():
        for week_key, week_value in final_value.iteritems():
            if week_key not in final_internal_accuracy_timeline.keys():
                final_internal_accuracy_timeline[week_key] = []
    for prod_week_num in week_names:
        if internal_accuracy_timeline.has_key(prod_week_num):
            if len(internal_accuracy_timeline[prod_week_num]) > 0:
                for vol_key, vol_values in internal_accuracy_timeline[prod_week_num].iteritems():
                    if final_internal_accuracy_timeline.has_key(vol_key):
                        final_internal_accuracy_timeline[vol_key].append(vol_values)
                    else:
                        final_internal_accuracy_timeline[vol_key] = [vol_values]
                for prod_key, prod_values in final_internal_accuracy_timeline.iteritems():
                    if prod_key not in internal_accuracy_timeline[prod_week_num].keys():
                        final_internal_accuracy_timeline[prod_key].append(0)
            else:
                for vol_key, vol_values in final_internal_accuracy_timeline.iteritems():
                    final_internal_accuracy_timeline[vol_key].append(0)
    return final_internal_accuracy_timeline


def min_max_num(int_value_range):
    main_max_dict = {}
    if len(int_value_range) > 0:
        if (min(int_value_range.values()) > 0):
            int_min_value = int(round(min(int_value_range.values()) - 2))
            int_max_value = int(round(max(int_value_range.values()) + 2))
        else:
            int_min_value = int(round(min(int_value_range.values())))
            int_max_value = int(round(max(int_value_range.values()) + 2))
    else:
        int_min_value, int_max_value = 0, 0
    main_max_dict ['min_value'] = int_min_value
    main_max_dict ['max_value'] = int_max_value
    return main_max_dict

def volume_status_week(week_names,productivity_list,final_productivity):
    final_productivity =  OrderedDict()
    for final_key, final_value in productivity_list.iteritems():
        for week_key, week_value in final_value.iteritems():
            if week_key not in final_productivity.keys():
                final_productivity[week_key] = [] 
    for prod_week_num in week_names:
        if len(productivity_list.get(prod_week_num,'')) > 0: 
            for vol_key, vol_values in productivity_list[prod_week_num].iteritems():
                if final_productivity.has_key(vol_key):
                    if vol_key == 'Opening':
                        final_productivity[vol_key].append(vol_values[0])
                    elif vol_key == 'Closing balance':
                        final_productivity[vol_key].append(vol_values[-1])
                    else:
                        if isinstance(vol_values,list):
                            vol_values = sum(vol_values)
                        final_productivity[vol_key].append(vol_values)
                else:
                    if isinstance(vol_values,list):
                        vol_values = sum(vol_values)
                    final_productivity[vol_key] = [vol_values]
            for prod_key, prod_values in final_productivity.iteritems():
                if prod_key not in productivity_list[prod_week_num].keys():
                    final_productivity[prod_key].append(0)
        else:
            for vol_key, vol_values in final_productivity.iteritems():
                final_productivity[vol_key].append(0)
    return final_productivity


def received_volume_week(week_names,productivity_list,final_productivity):
    productivity_data = {} 
    for final_key, final_value in productivity_list.iteritems():
        for week_key, week_value in final_value.iteritems():
            if week_key not in final_productivity.keys():
                final_productivity[week_key] = [] 
    for prod_week_num in week_names:
        if len(productivity_list.get(prod_week_num,'')) > 0: 
            values = productivity_list[prod_week_num]
            if len(values['Received']) == len(values['Opening']):
                values['Received'][0] = values['Received'][0] + values['Opening'][0]
                values['Received'] = sum(values['Received'])
                values['Completed'] = sum(values['Completed'])
                values['Opening'] = sum(values['Opening'])
                productivity_data.update(values)
                del productivity_data['Opening']
                for vol_key,vol_values in productivity_data.iteritems():
                    if final_productivity.has_key(vol_key):
                        final_productivity[vol_key].append(vol_values)
                    else:
                        final_productivity[vol_key] = [vol_values]

            for prod_key, prod_values in final_productivity.iteritems():
                if prod_key not in productivity_list[prod_week_num].keys():
                    final_productivity[prod_key].append(0)
        else:
            for vol_key, vol_values in final_productivity.iteritems():
                final_productivity[vol_key].append(0)
    return final_productivity

def prod_volume_week(week_names,productivity_list,final_productivity):
    for final_key, final_value in productivity_list.iteritems():
        for week_key, week_value in final_value.iteritems():
            if week_key not in final_productivity.keys():
                final_productivity[week_key] = []
    for prod_week_num in week_names:
        if len(productivity_list.get(prod_week_num,'')) > 0:
            for vol_key, vol_values in productivity_list[prod_week_num].iteritems():
                if final_productivity.has_key(vol_key):
                    if isinstance(vol_values,list):
                        vol_values = sum(vol_values)
                    final_productivity[vol_key].append(vol_values)
                else:
                    if isinstance(vol_values,list):
                        vol_values = sum(vol_values)
                    final_productivity[vol_key] = [vol_values]
            for prod_key, prod_values in final_productivity.iteritems():
                if prod_key not in productivity_list[prod_week_num].keys():
                    final_productivity[prod_key].append(0)
        else:
            for vol_key, vol_values in final_productivity.iteritems():
                final_productivity[vol_key].append(0)
    return final_productivity


def prod_volume_week_util(week_names,productivity_list,final_productivity):
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

def prod_volume_week_util_dell_coding(week_names,productivity_list,final_productivity,week_or_month):
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
                            if week_or_month =='week':
                                if len(new_values)<5:
                                    vol_values = sum(vol_values)/len(new_values)
                                elif len(new_values) >= 5:
                                    vol_values = sum(vol_values)/5
                            else:
                                vol_values = sum(vol_values)/21
                        else:
                            vol_values = sum(vol_values)
                    vol_values = float('%.2f' % round(vol_values, 2))
                    final_productivity[vol_key].append(vol_values)
                else:
                    if isinstance(vol_values,list):
                        if len(vol_values)>0:
                            vol_values = sum(vol_values)/len(vol_values)
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

def error_timeline_min_max(min_max_dict):
    int_timeline_min_max = []
    for wp_key, wp_value in min_max_dict.iteritems():
        int_timeline_min_max = int_timeline_min_max + wp_value
    final_min_max={}
    if len(int_timeline_min_max)>0:
        min_value = int(round(min(int_timeline_min_max) - 5))
        max_value = int(round(max(int_timeline_min_max) + 5))
        final_min_max['min_value'] = 0
        if min_value > 0:
            final_min_max['min_value'] = min_value
        final_min_max['max_value'] = max_value
    else:
        final_min_max['min_value'] = 0
        final_min_max['max_value'] = 0
    return final_min_max


def pareto_graph_data(pareto_dict):
    final_list = []
    for key,value in pareto_dict.iteritems():
        alignment_data = graph_data_alignment(value, 'data')
        for single_dict in alignment_data:
            """if key == 'Cumulative %':
                single_dict['type']='spline'
            if key == 'Error Count':
                single_dict['type'] = 'column'
                single_dict['yAxis'] = 1"""
            if key == 'Error Count':
                single_dict['type'] = 'column'
                #single_dict['yAxis'] = 1
            if key == 'Cumulative %':
                single_dict['type']='spline'
                single_dict['yAxis'] = 1
            final_list.append(single_dict)
    return final_list


def week_month_pareto_calc(week_names,pareto_error_count,accuracy_timeline):
    final_pareto_error_count = prod_volume_week(week_names, pareto_error_count, {})
    pareto_dict = {}
    pareto_dict['Error Count'] = final_pareto_error_count
    pareto_dict['Cumulative %'] = accuracy_timeline
    pareto_chart = pareto_graph_data(pareto_dict)

    return pareto_chart

def adding_min_max(high_chart_key,values_dict):
    result = {}
    min_max_values = error_timeline_min_max(values_dict)
    result['min_'+high_chart_key] = min_max_values['min_value']
    result['max_' + high_chart_key] = min_max_values['max_value']
    return result

"""def tat_graph(date_list, prj_id, center, level_structure_key):
    data_list = []
    conn = redis.Redis(host="localhost", port=6379, db=0)
    date_values = {}
    prj_name = Project.objects.filter(id=prj_id).values_list('name', flat=True)
    center_name = Center.objects.filter(id=center).values_list('name', flat=True)
    query_set = query_set_generation(prj_id, center, level_structure_key, date_list)
    new_date_list = []
    new_dict = {}

    if level_structure_key.has_key('sub_project'):
        if level_structure_key['sub_project'] == "All":
            volume_list = TatTable.objects.filter(**query_set).values('sub_project').distinct()
        else:
            if level_structure_key.has_key('work_packet'):
                if level_structure_key['work_packet'] == "All":
                    volume_list = TatTable.objects.filter(**query_set).values('sub_project', 'work_packet').distinct()
                else:
                    volume_list = TatTable.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()
    elif level_structure_key.has_key('work_packet') and len(level_structure_key) == 1:
        if level_structure_key['work_packet'] == "All":
            volume_list = TatTable.objects.filter(**query_set).values('sub_project', 'work_packet').distinct()
        else:
            volume_list = TatTable.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()
    elif level_structure_key.has_key('work_packet') and level_structure_key.has_key('sub_packet'):
        volume_list = TatTable.objects.filter(**query_set).values('sub_project', 'work_packet', 'sub_packet').distinct()
    else:
        volume_list = []

    for date in date_list:
        total_done_value = RawTable.objects.filter(project=prj_id, center=center, date=date).aggregate(Max('per_day'))
        if total_done_value['per_day__max'] > 0:
            data_list.append(date)
            count = 0
            final_data = []
            final_notmet_data = []
            if level_structure_key.get('work_packet','') == "All":
                tat_status = TatTable.objects.filter(project = prj_id,center= center,date=date).values_list('tat_status',flat=True)
                for i in tat_status:
                    if i == 'Met':
                        tat_value = 100
                        final_data.append(tat_value)
                    else:
                        tat_value = 0
                        final_notmet_data.append(tat_value)

            elif level_structure_key.get('sub_project', '') == "All":
                tat_status = TatTable.objects.filter(project=prj_id, center=center, date=date).values_list(
                    'tat_status', flat=True)
                for i in tat_status:
                    if i == 'Met':
                        tat_value = 100
                        final_data.append(tat_value)
                    else:
                        tat_value = 0
                        final_notmet_data.append(tat_value)

                tat_count = len(final_data)
                tat_not_count = len(final_notmet_data)
                if tat_count != 0:
                    tat_accuracy = float((float(tat_not_count)/float(tat_count+tat_not_count))*100)
                    tat_accuracy = 100 - (float('%.2f' % round(tat_accuracy, 2)))
                    new_date_list.append(tat_accuracy)
            else:
                for vol_type in volume_list:
                    if level_structure_key.has_key('sub_project'):
                        local_level_hierarchy_key = vol_type
                    else:
                        local_level_hierarchy_key = level_structure_key
                    final_work_packet = level_hierarchy_key(local_level_hierarchy_key, vol_type)
                    tat_table_query_set = tat_table_query_generations(prj_id, center, date, final_work_packet,level_structure_key)

                    if not final_work_packet:
                        final_work_packet = level_hierarchy_key(volume_list[count], vol_type)
                    count = count + 1
                    tat_status_value = TatTable.objects.filter(**tat_table_query_set).values_list('tat_status',flat=True)
                    for i in tat_status_value:
                        if  i == 'Met':
                            tat_value = 100
                        else:
                            tat_value = 0
                        new_date_list.append(tat_value)
        new_dict['Tat Met Status'] = new_date_list
    return new_dict """


def tat_graph(date_list, prj_id, center, level_structure_key):
    data_list = []
    conn = redis.Redis(host="localhost", port=6379, db=0)
    date_values = {}
    prj_name = Project.objects.filter(id=prj_id).values_list('name', flat=True)
    center_name = Center.objects.filter(id=center).values_list('name', flat=True)
    query_set = query_set_generation(prj_id, center, level_structure_key, date_list)
    new_date_list = []
    new_dict = {}
    if level_structure_key.has_key('sub_project'):
        if level_structure_key['sub_project'] == "All":
            volume_list = TatTable.objects.filter(**query_set).values('sub_project').distinct()
        else:
            if level_structure_key.has_key('work_packet'):
                if level_structure_key['work_packet'] == "All":
                    volume_list = TatTable.objects.filter(**query_set).values('sub_project', 'work_packet').distinct()
                else:
                    volume_list = TatTable.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()
    elif level_structure_key.has_key('work_packet') and len(level_structure_key) == 1:
        if level_structure_key['work_packet'] == "All":
            volume_list = TatTable.objects.filter(**query_set).values('sub_project', 'work_packet').distinct()
        else:
            volume_list = TatTable.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()
    elif level_structure_key.has_key('work_packet') and level_structure_key.has_key('sub_packet'):
        volume_list = TatTable.objects.filter(**query_set).values('sub_project', 'work_packet', 'sub_packet').distinct()
    else:
        volume_list = []

    for date in date_list:
        total_done_value = RawTable.objects.filter(project=prj_id, center=center, date=date).aggregate(Max('per_day'))
        if total_done_value['per_day__max'] > 0:
            data_list.append(date)
            count = 0
            final_data = []
            final_notmet_data = []
            if level_structure_key.get('work_packet','') == "All":
                tat_status = TatTable.objects.filter(project = prj_id,center= center,date=date).values_list('tat_status',flat=True)
                for i in tat_status:
                    if i == 'Met':
                        tat_value = 100
                        final_data.append(tat_value)
                    else:
                        tat_value = 0
                        final_notmet_data.append(tat_value)

                tat_count = len(final_data)
                tat_not_count = len(final_notmet_data)
                if tat_count != 0:
                    tat_accuracy = float((float(tat_not_count) / float(tat_count + tat_not_count)) * 100)
                    tat_accuracy = 100 - (float('%.2f' % round(tat_accuracy, 2)))
                    new_date_list.append(tat_accuracy)

            elif level_structure_key.get('sub_project', '') == "All":
                tat_status = TatTable.objects.filter(project=prj_id, center=center, date=date).values_list(
                    'tat_status', flat=True)
                for i in tat_status:
                    if i == 'Met':
                        tat_value = 100
                        final_data.append(tat_value)
                    else:
                        tat_value = 0
                        final_notmet_data.append(tat_value)

                tat_count = len(final_data)
                tat_not_count = len(final_notmet_data)
                if tat_count != 0:
                    tat_accuracy = float((float(tat_not_count)/float(tat_count+tat_not_count))*100)
                    tat_accuracy = 100 - (float('%.2f' % round(tat_accuracy, 2)))
                    new_date_list.append(tat_accuracy)
            else:
                for vol_type in volume_list:
                    if level_structure_key.has_key('sub_project'):
                        local_level_hierarchy_key = vol_type
                    else:
                        local_level_hierarchy_key = level_structure_key
                    final_work_packet = level_hierarchy_key(local_level_hierarchy_key, vol_type)
                    tat_table_query_set = tat_table_query_generations(prj_id, center, date, final_work_packet,level_structure_key)

                    if not final_work_packet:
                        final_work_packet = level_hierarchy_key(volume_list[count], vol_type)
                    count = count + 1
                    tat_status_value = TatTable.objects.filter(**tat_table_query_set).values_list('tat_status',flat=True)
                    for i in tat_status_value:
                        if  i == 'Met':
                            tat_value = 100
                        else:
                            tat_value = 0
                        new_date_list.append(tat_value)
        new_dict['tat_graph_details'] = new_date_list
    return new_dict


def day_week_month(request, dwm_dict, prj_id, center, work_packets, level_structure_key):
    if dwm_dict.has_key('day'):
        final_dict = {}
        final_details = {}
        result_dict =  product_total_graph(dwm_dict['day'], prj_id, center, work_packets, level_structure_key)
        tat_graph_details = tat_graph(dwm_dict['day'], prj_id, center,level_structure_key)
        production_avg_details = production_avg_perday(dwm_dict['day'], prj_id, center, work_packets, level_structure_key)
        result_dict['production_avg_details'] = graph_data_alignment_color(production_avg_details, 'data', level_structure_key,prj_id, center)
        volume_graph = volume_graph_data(dwm_dict['day'], prj_id, center, level_structure_key)
        result_dict['volume_graphs'] = {}
        result_dict['volume_graphs']['bar_data'] = graph_data_alignment_color(volume_graph['bar_data'],'data', level_structure_key,prj_id,center,'volume_bar_graph') 
        result_dict['volume_graphs']['line_data'] = graph_data_alignment_color(volume_graph['line_data'],'data', level_structure_key,prj_id,center,'volume_productivity_graph')

        monthly_volume_graph_details = Monthly_Volume_graph(dwm_dict['day'], prj_id, center, level_structure_key)
        #import pdb;pdb.set_trace()
        result_dict['monthly_volume_graph_details'] = graph_data_alignment_color(monthly_volume_graph_details,'data', level_structure_key,prj_id, center,'monthly_volume')

        result_dict['tat_graph_details'] = graph_data_alignment_color(tat_graph_details, 'data', level_structure_key, prj_id,center,'TAT Graph')
        tat_min_max = adding_min_max('tat_graph_details',tat_graph_details)
        result_dict.update(tat_min_max)
        utilization_details = modified_utilization_calculations(center, prj_id, dwm_dict['day'], level_structure_key)

        productivity_utilization_data = main_productivity_data(center, prj_id, dwm_dict['day'], level_structure_key)
        #utilization_fte_details = utilization_work_packet_data(center, prj_id, dwm_dict['day'], level_structure_key)
        #utilization_operational_details = utilization_operational_data(center, prj_id, dwm_dict['day'], level_structure_key)
        result_dict['utilization_fte_details'] = graph_data_alignment_color(utilization_details['fte_utilization'], 'data',level_structure_key, prj_id, center,'fte_utilization')
        result_dict['utilization_operational_details'] = graph_data_alignment_color(utilization_details['operational_utilization'], 'data',level_structure_key, prj_id, center,'operational_utilization')
        result_dict['original_productivity_graph'] = graph_data_alignment_color(productivity_utilization_data['productivity'], 'data', level_structure_key, prj_id, center,'productivity_trends')
        result_dict['original_utilization_graph'] = graph_data_alignment_color(utilization_details['overall_utilization'], 'data', level_structure_key, prj_id, center,'utilisation_wrt_work_packet')
        #result_dict['utilization_fte_graph'] = graph_data_alignment_color(productivity_utilization_data, 'data', level_structure_key, prj_id, center,'')
        #productivity_min_max = adding_min_max('original_productivity_graph',productivity_utilization_data['productivity'])
        #utilization_min_max = adding_min_max('original_utilization_graph', productivity_utilization_data['utilization'])
        #result_dict.update(productivity_min_max)
        #result_dict.update(utilization_min_max)
        #fte_graph_data = fte_calculation(request,prj_id, center, dwm_dict['day'], level_structure_key)
        fte_graph_data = fte_calculation(request,prj_id, center, dwm_dict['day'], level_structure_key)
        result_dict['fte_calc_data'] = {}
        result_dict['fte_calc_data']['total_fte'] = graph_data_alignment_color(fte_graph_data['total_fte'], 'data',level_structure_key, prj_id, center,'sum_total_fte')
        result_dict['fte_calc_data']['work_packet_fte'] = graph_data_alignment_color(fte_graph_data['work_packet_fte'],'data', level_structure_key,prj_id, center)
        if len(result_dict['prod_days_data']) > 0:
            # result_dict['productivity_data'] = graph_data_alignment(result_dict['prod_days_data'],name_key='data')
            result_dict['productivity_data'] = graph_data_alignment_color(result_dict['prod_days_data'], 'data',level_structure_key, prj_id, center)
        else:
            result_dict['productivity_data'] = []
        packet_sum_data = result_dict['volumes_data']['volume_values']
        error_graphs_data = internal_extrnal_graphs(request, dwm_dict['day'], prj_id, center, packet_sum_data,level_structure_key)
        external_pareto_graph = pareto_graph_data(error_graphs_data['external_pareto_data'])
        final_dict['internal_pareto_graph_data'] = pareto_graph_data(error_graphs_data['internal_pareto_data'])
        final_dict['external_pareto_graph_data'] = external_pareto_graph
        # final_dict['internal_time_line'] = error_graphs_data['internal_time_line']
        if len(error_graphs_data['internal_time_line']) > 0:
            internal_time_line = {}
            for er_key, er_value in error_graphs_data['internal_time_line']['internal_time_line'].iteritems():
                packet_errors = []
                for err_value in er_value:
                    if err_value == "NA":
                        packet_errors.append(0)
                    else:
                        packet_errors.append(err_value)
                internal_time_line[er_key] = packet_errors
            # final_dict['internal_time_line'] = graph_data_alignment(internal_time_line,name_key='data')
            final_dict['internal_time_line'] = graph_data_alignment_color(internal_time_line, 'data',level_structure_key, prj_id, center,'internal_accuracy_timeline')
            int_error_timeline_min_max = error_timeline_min_max(internal_time_line)
            final_dict['min_internal_time_line'] = int_error_timeline_min_max['min_value']
            final_dict['max_internal_time_line'] = int_error_timeline_min_max['max_value']
        if len(error_graphs_data['external_time_line']) > 0:
            for er_key, er_value in error_graphs_data['external_time_line']['external_time_line'].iteritems():
                packet_errors = []
                for err_value in er_value:
                    if err_value == "NA":
                        packet_errors.append(0)
                    else:
                        packet_errors.append(err_value)
                error_graphs_data['external_time_line']['external_time_line'][er_key] = packet_errors
            # final_dict['external_time_line'] = graph_data_alignment(error_graphs_data['external_time_line']['external_time_line'],name_key='data')
            final_dict['external_time_line'] = graph_data_alignment_color(error_graphs_data['external_time_line']['external_time_line'], 'data', level_structure_key, prj_id,center,'external_accuracy_timeline')
            ext_error_timeline_min_max = error_timeline_min_max(
                error_graphs_data['external_time_line']['external_time_line'])
            final_dict['min_external_time_line'] = ext_error_timeline_min_max['min_value']
            final_dict['max_external_time_line'] = ext_error_timeline_min_max['max_value']
        """int_value_range = error_graphs_data['internal_accuracy_graph']
        int_min_max = min_max_num(int_value_range)
        final_dict['int_min_value'] = int_min_max['min_value']
        final_dict['int_max_value'] = int_min_max['max_value']"""
        all_external_error_accuracy = {}
        all_internal_error_accuracy = {}

        '''if error_graphs_data.has_key('intr_err_accuracy'):
            for vol_key, vol_values in error_graphs_data['intr_err_accuracy']['packets_percntage'].iteritems():
                all_internal_error_accuracy[vol_key] = vol_values[0]
                final_dict['internal_accuracy_graph'] = graph_data_alignment_color(all_internal_error_accuracy, 'y',level_structure_key, prj_id, center)'''
        if error_graphs_data.has_key('internal_accuracy_graph'):
            # final_dict['internal_accuracy_graph'] = graph_data_alignment(error_graphs_data['internal_accuracy_graph'], name_key='y')
            final_dict['internal_accuracy_graph'] = graph_data_alignment_color(error_graphs_data['internal_accuracy_graph'], 'y', level_structure_key, prj_id, center,'internal_error_accuracy')
        if error_graphs_data.has_key('extr_err_accuracy'):
            for vol_key, vol_values in error_graphs_data['extr_err_accuracy']['packets_percntage'].iteritems():
                all_external_error_accuracy[vol_key] = vol_values[0]
            # final_dict['external_accuracy_graph'] = graph_data_alignment(all_external_error_accuracy,name_key='y')
            """final_dict['external_accuracy_graph'] = graph_data_alignment_color(all_external_error_accuracy, 'y',level_structure_key, prj_id, center,'external_error_accuracy')
        if error_graphs_data.has_key('external_accuracy_graph'):
            # final_dict['external_accuracy_graph'] = graph_data_alignment(error_graphs_data['external_accuracy_graph'], name_key='y')
            final_dict['external_accuracy_graph'] = graph_data_alignment_color(
                error_graphs_data['external_accuracy_graph'], 'y', level_structure_key, prj_id, center,'external_error_accuracy')"""
        final_dict.update(result_dict)
        sub_pro_level = filter(None, RawTable.objects.filter(project=prj_id, center=center).values_list('sub_project',flat=True).distinct())
        sub_project_level = [i for i in sub_pro_level]
        if len(sub_project_level) >= 1:
            sub_project_level.append('all')
        else:
            sub_project_level = ''
        work_pac_level = filter(None, RawTable.objects.filter(project=prj_id, center=center).values_list('work_packet',flat=True).distinct())
        work_packet_level = [j for j in work_pac_level]
        if len(work_packet_level) >= 1:
            work_packet_level.append('all')
        else:
            work_packet_level = ''
        sub_pac_level = filter(None, RawTable.objects.filter(project=prj_id, center=center).values_list('sub_packet',flat=True).distinct())
        sub_packet_level = [k for k in sub_pac_level]
        if len(sub_packet_level) >= 1:
            sub_packet_level.append('all')
        else:
            sub_packet_level = ''
        # sub_pro_level = filter(RawTable.objects.filter(project=prj_id, center=center).values_list('sub_project').distinct()
        # work_pac_level = RawTable.objects.filter(project=prj_id, center=center).values_list('work_packet').distinct()
        # sub_pac_level = RawTable.objects.filter(project=prj_id, center=center).values_list('sub_packet').distinct()
        final_details['sub_project'] = 0
        final_details['work_packet'] = 0
        final_details['sub_packet'] = 0
        if len(sub_pro_level) >= 1:
            final_details['sub_project'] = 1
        if len(work_pac_level) >= 1:
            final_details['work_packet'] = 1
        if len(sub_pac_level) >= 1:
            final_details['sub_packet'] = 1

        final_dict['sub_project_level'] = sub_project_level
        final_dict['work_packet_level'] = work_packet_level
        final_dict['sub_packet_level'] = sub_packet_level
        big_dict = {}
        if final_details['sub_project']:
            if final_details['work_packet']:
                first = RawTable.objects.filter(project=prj_id).values_list('sub_project').distinct()
                big_dict = {}
                total = {}
                for i in first:
                    list_val = RawTable.objects.filter(project=prj_id, sub_project=i[0]).values_list('work_packet').distinct()
                    for j in list_val:
                        total[j[0]] = []
                        sub_pac_data = RawTable.objects.filter(project=prj_id, sub_project=i[0], work_packet=j[0]).values_list('sub_packet').distinct()
                        for l in sub_pac_data:
                            total[j[0]].append(l[0])
                    big_dict[i[0]] = total
                    total = {}
        elif final_details['work_packet']:
            if final_details['sub_packet']:
                first = RawTable.objects.filter(project=prj_id).values_list('work_packet').distinct()
                big_dict = {}
                total = {}
                for i in first:
                    list_val = RawTable.objects.filter(project=prj_id, work_packet=i[0]).values_list('sub_packet').distinct()
                    for j in list_val:
                        total[j[0]] = []
                    big_dict[i[0]] = total
                    total = {}
            else:
                big_dict = {}
                work_pac_level = RawTable.objects.filter(project=prj_id, center=center).values_list('work_packet').distinct()
                for i in work_pac_level:
                    big_dict[i[0]] = {}
        # final_dict['drop_value'] = {u'Charge': {u'Copay': [], u'Charge': [], u'DemoCheck': [], u'Demo': []}, u'Payment': {u'Payment': []}}
        final_dict['level'] = [1, 2]
        final_dict['fin'] = final_details
        final_dict['drop_value'] = big_dict
        ext_min_value, ext_max_value = 0, 0
        if error_graphs_data.has_key('extr_err_accuracy'):
            ext_value_range = error_graphs_data['extr_err_accuracy']['extr_err_perc']
            if len(ext_value_range) > 0:
                if ext_value_range != '' and min(ext_value_range) > 0:
                    ext_min_value = int(round(min(ext_value_range) - 2))
                    ext_max_value = int(round(max(ext_value_range) + 2))
                else:
                    ext_min_value = int(round(min(ext_value_range)))
                    ext_max_value = int(round(max(ext_value_range) + 2))
            final_dict['ext_min_value'] = ext_min_value
            final_dict['ext_max_value'] = ext_max_value
        # final_dict.update(error_graphs_data)
        return final_dict

    if dwm_dict.has_key('month'):
        final_result_dict = {}
        final_internal_accuracy_timeline = {}
        internal_accuracy_timeline = {}
        final_external_accuracy_timeline = {}
        external_accuracy_timeline = {}
        main_productivity_timeline = {}
        utilization_timeline = {}
        # final_external_accuracy_timeline = {}
        month_names = []
        final_vol_graph_line_data, vol_graph_line_data = {}, {}
        final_vol_graph_bar_data, vol_graph_bar_data = {}, {}
        final_productivity = {}
        productivity_list = {}
        total_fte_list = {}
        wp_fte_list = {}
        internal_pareto_error_count = {}
        externl_pareto_error_count = {}
        all_internal_error_accuracy = {}
        all_external_error_accuracy = {}
        utilization_operational_dt = {}
        utilization_fte_dt = {}
        monthly_vol_data = {}
        tat_graph_dt = {}
        prod_avg_dt = {}
        monthly_vol_data['total_workdone'] = []
        monthly_vol_data['total_target'] = []
        data_date = []
        #month_lst = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October','November', 'December']
        #month_order = OrderedDict(sorted(dwm_dict['month'].items(), key=lambda x: month_lst.index(x[0])))
        #for month_na in tuple(month_order):
        for month_na,month_va in zip(dwm_dict['month']['month_names'],dwm_dict['month']['month_dates']):
            month_name = month_na
            #month_dates = dwm_dict['month'][month_na]
            month_dates = month_va
            data_date.append(month_dates[0] + ' to ' + month_dates[-1])
            result_dict = product_total_graph(month_dates, prj_id, center, work_packets, level_structure_key)
            if len(result_dict['prod_days_data']) > 0:
                productivity_list[month_name] = result_dict['volumes_data']['volume_values']
                month_names.append(month_name)
            else:
                productivity_list[month_name] = {}
                month_names.append(month_name)
            packet_sum_data = result_dict['volumes_data']['volume_values']

            #volume_graph = volume_graph_data(month_dates, prj_id, center, level_structure_key)
            volume_graph = volume_graph_data_week_month(month_dates, prj_id, center, level_structure_key)
            vol_graph_line_data[month_name] = volume_graph['line_data']
            vol_graph_bar_data[month_name] = volume_graph['bar_data']
            production_avg_details = production_avg_perday(month_dates, prj_id, center, work_packets,level_structure_key)
            prod_avg_dt[month_name] = production_avg_details
            tat_graph_details = tat_graph(month_dates,prj_id,center,level_structure_key)
            tat_graph_dt[month_name] = tat_graph_details
            utilization_details = modified_utilization_calculations(center, prj_id, month_dates, level_structure_key)
            #utilization_operational_details = utilization_operational_data(center, prj_id, month_dates, level_structure_key)
            utilization_operational_dt[month_name] = utilization_details['operational_utilization']
            #utilization_fte_details = utilization_work_packet_data(center, prj_id, month_dates, level_structure_key)
            #utilization_fte_dt[month_name] = utilization_fte_details['utilization']
            utilization_fte_dt[month_name] = utilization_details['fte_utilization']
            monthly_volume_graph_details = Monthly_Volume_graph(month_dates, prj_id, center, level_structure_key)
            for vol_cumulative_key, vol_cumulative_value in monthly_volume_graph_details.iteritems():
                if len(vol_cumulative_value) > 0:
                    monthly_vol_data[vol_cumulative_key].append(vol_cumulative_value[-1])
                else:
                    monthly_vol_data[vol_cumulative_key].append(0)
            #monthly_vol_data[month_name] = monthly_volume_graph_details

            error_graphs_data = internal_extrnal_graphs(request, month_dates, prj_id, center, packet_sum_data,level_structure_key)
            internal_pareto_error_count[month_name] = error_graphs_data['internal_pareto_data']['error_count']
            externl_pareto_error_count[month_name] = error_graphs_data['external_pareto_data']['error_count']
            productivity_utilization_data = main_productivity_data(center, prj_id, month_dates, level_structure_key)
            #utlization_operational_details = utilization_operational_data(center, prj_id, month_dates, level_structure_key)
            main_productivity_timeline[month_name] = productivity_utilization_data['productivity']
            #main_productivity_timeline[month_name] = utilization_details[]
            #utilization_timeline[month_name] = productivity_utilization_data['utilization']
            #utilization_timeline[month_name] = utilization_details['fte_utilization']
            utilization_timeline[month_name] = utilization_details['overall_utilization']
            #utilization_operational_timeline[month_name] = utlization_operational_details
            fte_graph_data = fte_calculation(request, prj_id, center, month_dates, level_structure_key)
            total_fte_list[month_name] = fte_graph_data['total_fte']
            wp_fte_list[month_name] = fte_graph_data['work_packet_fte']

            """if len(error_graphs_data['internal_time_line']) > 0:
                internal_accuracy_timeline[month_name] = error_graphs_data['internal_time_line']['internal_time_line']
            if len(error_graphs_data['external_time_line']) > 0:
                external_accuracy_timeline[month_name] = error_graphs_data['external_time_line']['external_time_line']"""

            if len(error_graphs_data['internal_time_line']) > 0: 
                internal_accuracy_packets = {}
                internal_accuracy_timeline[month_name] = error_graphs_data['internal_time_line']['internal_time_line']
                intr_accuracy_perc = error_graphs_data['internal_accuracy_graph']
                for in_acc_key,in_acc_value in intr_accuracy_perc.iteritems():
                    if internal_accuracy_packets.has_key(in_acc_key):
                        internal_accuracy_packets[in_acc_key].append(in_acc_value)
                    else:
                        internal_accuracy_packets[in_acc_key] = [in_acc_value]
                internal_accuracy_timeline[month_name] = internal_accuracy_packets
            if len(error_graphs_data['external_time_line']) > 0: 
                #external_accuracy_timeline[month_name] = error_graphs_data['external_time_line']['external_time_line']
                external_accuracy_packets = {}
                if error_graphs_data.has_key('external_accuracy_graph'):
                    extr_accuracy_perc = error_graphs_data['external_accuracy_graph']
                else:
                    extr_accuracy_perc = error_graphs_data['extr_err_accuracy']['packets_percntage'] 
                for ex_acc_key,ex_acc_value in extr_accuracy_perc.iteritems():
                    if external_accuracy_packets.has_key(ex_acc_key):
                        if isinstance(ex_acc_value,list):
                            external_accuracy_packets[ex_acc_key].append(ex_acc_value[0])
                        else:
                            external_accuracy_packets[ex_acc_key].append(ex_acc_value)
                    else:
                        if isinstance(ex_acc_value,list):
                            external_accuracy_packets[ex_acc_key] = ex_acc_value
                        else:
                            external_accuracy_packets[ex_acc_key] = [ex_acc_value]
                external_accuracy_timeline[month_name] = external_accuracy_packets



            """for vol_key, vol_values in error_graphs_data['internal_accuracy_graph'].iteritems():
                if all_internal_error_accuracy.has_key(vol_key):
                    all_internal_error_accuracy[vol_key].append(vol_values)
                else:
                    all_internal_error_accuracy[vol_key] = [vol_values]
            if error_graphs_data.has_key('external_accuracy_graph'):
                for vol_key, vol_values in error_graphs_data['external_accuracy_graph'].iteritems():
                    if all_external_error_accuracy.has_key(vol_key):
                        all_external_error_accuracy[vol_key].append(vol_values)
                    else:
                        all_external_error_accuracy[vol_key] = [vol_values]"""
            if error_graphs_data.has_key('extr_err_accuracy'):
                for vol_key, vol_values in error_graphs_data['extr_err_accuracy']['packets_percntage'].iteritems():
                    if all_external_error_accuracy.has_key(vol_key):
                        all_external_error_accuracy[vol_key].append(vol_values[0])
                    else:
                        all_external_error_accuracy[vol_key] = vol_values

        # below for productivity,packet wise performance
        final_prod_avg_details = prod_volume_week_util(month_names, prod_avg_dt, {})
        result_dict['production_avg_details'] = graph_data_alignment_color(final_prod_avg_details,'data',level_structure_key, prj_id, center) 
        final_productivity = prod_volume_week(month_names, productivity_list, final_productivity)
        final_vol_graph_bar_data = volume_status_week(month_names, vol_graph_bar_data, final_vol_graph_bar_data)
        #final_vol_graph_bar_data = prod_volume_week(month_names, vol_graph_bar_data, final_vol_graph_bar_data)
        #final_vol_graph_line_data = prod_volume_week(month_names, vol_graph_line_data, final_vol_graph_line_data)
        final_vol_graph_line_data = received_volume_week(month_names, vol_graph_line_data, final_vol_graph_line_data)
        final_internal_accuracy_timeline = errors_week_calcuations(month_names, internal_accuracy_timeline,final_internal_accuracy_timeline)
        final_external_accuracy_timeline = errors_week_calcuations(month_names, external_accuracy_timeline,final_external_accuracy_timeline)
        # result_dict['internal_time_line'] = graph_data_alignment(final_internal_accuracy_timeline, name_key='data')
        result_dict['internal_time_line'] = graph_data_alignment_color(final_internal_accuracy_timeline, 'data',level_structure_key, prj_id, center,'internal_accuracy_timeline')
        final_tat_details = prod_volume_week_util(month_names, tat_graph_dt, {})
        result_dict['tat_graph_details'] = graph_data_alignment_color(final_tat_details, 'data',level_structure_key, prj_id, center,'TAT Graph')
        final_utlil_operational = prod_volume_week_util(month_names, utilization_operational_dt, {})
        result_dict['utilization_operational_details'] = graph_data_alignment_color(final_utlil_operational, 'data',level_structure_key, prj_id, center,'operational_utilization')
        final_util_fte = prod_volume_week_util(month_names, utilization_fte_dt, {})
        result_dict['utilization_fte_details'] = graph_data_alignment_color(final_util_fte, 'data', level_structure_key,prj_id, center,'fte_utilization')
        monthly_work_done = monthly_vol_data['total_workdone'].count(0)
        monthly_total_target = monthly_vol_data['total_target'].count(0)
        if monthly_work_done == len(monthly_vol_data['total_workdone']) and monthly_total_target == len(monthly_vol_data['total_target']):
            monthly_vol_data = {}
        final_montly_vol_data = previous_sum(monthly_vol_data)
        result_dict['monthly_volume_graph_details'] = graph_data_alignment_color(final_montly_vol_data, 'data',level_structure_key, prj_id, center)
        result_dict['monthly_volume_graph_details'] = graph_data_alignment_color(final_montly_vol_data, 'data',level_structure_key, prj_id, center,'monthly_volume')

        internal_pareto_anlysis_data = week_month_pareto_calc(month_names, internal_pareto_error_count,final_internal_accuracy_timeline)
        result_dict['internal_pareto_graph_data'] = internal_pareto_anlysis_data
        external_pareto_anlysis_data = week_month_pareto_calc(month_names, externl_pareto_error_count,final_external_accuracy_timeline)
        result_dict['external_pareto_graph_data'] = external_pareto_anlysis_data

        int_error_timeline_min_max = error_timeline_min_max(final_internal_accuracy_timeline)
        result_dict['min_internal_time_line'] = int_error_timeline_min_max['min_value']
        result_dict['max_internal_time_line'] = int_error_timeline_min_max['max_value']
        # result_dict['external_time_line'] = graph_data_alignment(final_external_accuracy_timeline, name_key='data')
        result_dict['external_time_line'] = graph_data_alignment_color(final_external_accuracy_timeline, 'data',level_structure_key, prj_id, center,'external_accuracy_timeline')
        # below code productivity and utilization

        final_main_productivity_timeline = errors_week_calcuations(month_names, main_productivity_timeline, {})
        final_utilization_timeline = errors_week_calcuations(month_names, utilization_timeline, {})
        result_dict['original_productivity_graph'] = graph_data_alignment_color(final_main_productivity_timeline,'data', level_structure_key, prj_id,center,'productivity_trends')
        result_dict['original_utilization_graph'] = graph_data_alignment_color(final_utilization_timeline, 'data',level_structure_key, prj_id, center,'utilisation_wrt_work_packet')
        productivity_min_max = adding_min_max('original_productivity_graph', final_main_productivity_timeline)
        utilization_min_max = adding_min_max('original_utilization_graph', final_utilization_timeline)
        #result_dict.update(productivity_min_max)
        result_dict.update(utilization_min_max)
        ext_error_timeline_min_max = error_timeline_min_max(final_external_accuracy_timeline)
        result_dict['min_external_time_line'] = ext_error_timeline_min_max['min_value']
        result_dict['max_external_time_line'] = ext_error_timeline_min_max['max_value']
        tat_min_max = adding_min_max('tat_graph_details', final_tat_details)
        result_dict.update(tat_min_max) 
        result_dict['volume_graphs'] = {}
        result_dict['volume_graphs']['bar_data'] = graph_data_alignment_color(final_vol_graph_bar_data,'data', level_structure_key,prj_id,center,'volume_bar_graph')
        result_dict['volume_graphs']['line_data'] = graph_data_alignment_color(final_vol_graph_line_data,'data', level_structure_key,prj_id,center,'volume_productivity_graph')
        result_dict['fte_calc_data'] = {}
        #final_total_fte_calc = prod_volume_week(month_names, total_fte_list, {})
        #final_total_fte_calc = prod_volume_week_util(month_names, total_fte_list, {})
        prj_name = Project.objects.get(id=prj_id[0]).name
        if prj_name == 'NTT DATA Services Coding':
            final_total_fte_calc = prod_volume_week_util_dell_coding(month_names, total_fte_list, {},'month')
            final_total_wp_fte_calc = prod_volume_week_util_dell_coding(month_names, wp_fte_list, {},'month')
        else:
            final_total_fte_calc = prod_volume_week_util(month_names, total_fte_list, {})
            final_total_wp_fte_calc = prod_volume_week_util(month_names, wp_fte_list, {})

        result_dict['fte_calc_data']['total_fte'] = graph_data_alignment_color(final_total_fte_calc, 'data',level_structure_key, prj_id, center,'sum_total_fte')
        #final_total_wp_fte_calc = prod_volume_week(month_names, wp_fte_list, {})
        #final_total_wp_fte_calc = prod_volume_week_util(month_names, wp_fte_list, {})
        #final_total_wp_fte_calc = prod_volume_week_util_dell_coding(month_names, wp_fte_list, {})
        result_dict['fte_calc_data']['work_packet_fte'] = graph_data_alignment_color(final_total_wp_fte_calc, 'data',level_structure_key, prj_id,center,'total_fte')

        error_volume_data = {}
        volume_new_data = []
        for key, value in final_productivity.iteritems():
            error_graph = []
            error_volume_data[key] = sum(value)
            error_graph.append(key.replace('NA_', '').replace('_NA', ''))
            error_graph.append(sum(value))
            volume_new_data.append(error_graph)

        # result_dict['productivity_data']= graph_data_alignment(final_productivity,name_key='data')
        result_dict['productivity_data'] = graph_data_alignment_color(final_productivity, 'data', level_structure_key,
                                                                      prj_id, center,'Production Chart')
        result_dict['volumes_data'] = {}
        result_dict['volumes_data']['volume_new_data'] = volume_new_data
        for error_key, error_value in all_internal_error_accuracy.iteritems():
            all_internal_error_accuracy[error_key] = sum(error_value) / len(error_value)
        for error_key, error_value in all_external_error_accuracy.iteritems():
            all_external_error_accuracy[error_key] = sum(error_value) / len(error_value)
        # result_dict['internal_accuracy_graph'] = graph_data_alignment(all_internal_error_accuracy, name_key='y')
        """result_dict['internal_accuracy_graph'] = graph_data_alignment_color(all_internal_error_accuracy, 'y',level_structure_key, prj_id, center,'internal_error_accuracy')
        int_min_max = min_max_num(all_internal_error_accuracy)
        result_dict['int_min_value'] = int_min_max['min_value']
        result_dict['int_max_value'] = int_min_max['max_value']
        # result_dict['external_accuracy_graph'] = graph_data_alignment(all_external_error_accuracy, name_key='y')
        result_dict['external_accuracy_graph'] = graph_data_alignment_color(all_external_error_accuracy, 'y',level_structure_key, prj_id, center,'external_error_accuracy')
        ext_min_max = min_max_num(all_external_error_accuracy)
        result_dict['ext_min_value'] = ext_min_max['min_value']
        result_dict['ext_max_value'] = ext_min_max['max_value']"""
        result_dict['data']['date'] = data_date
        return result_dict



    if dwm_dict.has_key('week'):
        final_result_dict = {}
        final_internal_accuracy_timeline = {}
        internal_accuracy_timeline = {}
        final_external_accuracy_timeline = {}
        external_accuracy_timeline = {}
        # final_external_accuracy_timeline = {}
        # external_accuracy_timeline = {}
        # final_external_accuracy_timeline = {}
        final_vol_graph_line_data, vol_graph_line_data = {}, {}
        final_vol_graph_bar_data, vol_graph_bar_data = {}, {}
        final_productivity = {}
        productivity_list = {}
        total_fte_list = {}
        wp_fte_list = {}
        util_fte_list = {}
        internal_pareto_error_count = {}
        externl_pareto_error_count = {}
        all_internal_error_accuracy = {}
        all_external_error_accuracy = {}
        utilization_operational_dt = {}
        utilization_fte_dt = {}
        monthly_vol_data = {}
        tat_graph_dt = {}
        prod_avg_dt = {}
        monthly_vol_data['total_workdone'] = []
        monthly_vol_data['total_target'] = [] 
        data_date = []
        week_num = 0
        week_names = []
        internal_week_num = 0
        external_week_num = 0
        productivity_week_num = 0
        tat_details_week_num = 0
        utilization_operational_week_num = 0
        pareto_week_num, fte_week_num = 0, 0
        main_productivity_timeline = {}
        utilization_timeline = {}
        for week_key, week_dates in dwm_dict.iteritems():
            for week in week_dates:
                data_date.append(week[0] + ' to ' + week[-1])
                result_dict = product_total_graph(week, prj_id, center, work_packets, level_structure_key)
                if len(result_dict['prod_days_data']) > 0:
                    week_name = str('week' + str(week_num))
                    week_names.append(week_name)
                    productivity_list[week_name] = result_dict['volumes_data']['volume_values']
                    week_num = week_num + 1
                else:
                    week_name = str('week' + str(week_num))
                    week_names.append(week_name)
                    productivity_list[week_name] = {}
                    week_num = week_num + 1

                utilization_details = modified_utilization_calculations(center, prj_id, week, level_structure_key)
                #utilization_operational_details = utilization_operational_data(center, prj_id, week,level_structure_key)
                #utilization_operational_dt[week_name] = utilization_operational_details['utilization']
                utilization_operational_dt[week_name] = utilization_details['operational_utilization']
                tat_graph_details = tat_graph(week, prj_id, center, level_structure_key)
                tat_graph_dt[week_name] = tat_graph_details 
                #utilization_fte_details = utilization_work_packet_data(center, prj_id, week,level_structure_key)
                #utilization_fte_dt[week_name] = utilization_fte_details['utilization']
                utilization_fte_dt[week_name] = utilization_details['fte_utilization']
                production_avg_details = production_avg_perday(week, prj_id, center, work_packets,level_structure_key)
                prod_avg_dt[week_name] = production_avg_details
                monthly_volume_graph_details = Monthly_Volume_graph(week, prj_id, center,level_structure_key)
                for vol_cumulative_key,vol_cumulative_value in monthly_volume_graph_details.iteritems():
                    if len(vol_cumulative_value) > 0:
                        monthly_vol_data[vol_cumulative_key].append(vol_cumulative_value[-1])
                    else:
                        monthly_vol_data[vol_cumulative_key].append(0)
                #monthly_vol_data[week_name] = monthly_volume_graph_details
                #volume_graph = volume_graph_data(week, prj_id, center, level_structure_key)
                volume_graph = volume_graph_data_week_month(week, prj_id, center, level_structure_key)
                vol_graph_line_data[week_name] = volume_graph['line_data']
                vol_graph_bar_data[week_name] = volume_graph['bar_data']
                packet_sum_data = result_dict['volumes_data']['volume_values']
                fte_graph_data = fte_calculation(request, prj_id, center, week, level_structure_key)
                fte_week_name = str('week' + str(fte_week_num))
                total_fte_list[fte_week_name] = fte_graph_data['total_fte']
                wp_fte_list[fte_week_name] = fte_graph_data['work_packet_fte']
                fte_week_num = fte_week_num + 1
                error_graphs_data = internal_extrnal_graphs(request, week, prj_id, center, packet_sum_data,level_structure_key)
                pareto_week_name = str('week' + str(pareto_week_num))
                internal_pareto_error_count[pareto_week_name] = error_graphs_data['internal_pareto_data']['error_count']
                externl_pareto_error_count[pareto_week_name] = error_graphs_data['external_pareto_data']['error_count']
                pareto_week_num = pareto_week_num + 1
                productivity_utilization_data = main_productivity_data(center, prj_id, week, level_structure_key)
                productivity_week_name = str('week' + str(productivity_week_num))
                #utilization_operational_week_num = str('week' + str(utilization_operational_week_num))
                #utlization_operational_details = utilization_operational_data(center, prj_id, week, level_structure_key)
                main_productivity_timeline[productivity_week_name] = productivity_utilization_data['productivity']
                #utilization_timeline[productivity_week_name] = productivity_utilization_data['utilization']
                utilization_timeline[productivity_week_name] = utilization_details['overall_utilization']

                #utilization_operational_timeline[utilization_operational_week_num] = utlization_operational_details
                productivity_week_num = productivity_week_num + 1
                #utilization_operational_week_num = utilization_operational_week_num + 1

                if len(error_graphs_data['internal_time_line']) > 0:
                    internal_week_name = str('week' + str(internal_week_num))
                    #internal_accuracy_timeline[internal_week_name] = error_graphs_data['internal_time_line']['internal_time_line']
                    #internal_week_num = internal_week_num + 1
                    internal_accuracy_packets = {}
                    intr_accuracy_perc = error_graphs_data['internal_accuracy_graph']
                    for in_acc_key,in_acc_value in intr_accuracy_perc.iteritems():
                        if internal_accuracy_packets.has_key(in_acc_key):
                            internal_accuracy_packets[in_acc_key].append(in_acc_value)
                        else:
                            internal_accuracy_packets[in_acc_key] = [in_acc_value]
                    #internal_accuracy_timeline[month_name] = internal_accuracy_packets
                    internal_accuracy_timeline[internal_week_name] = internal_accuracy_packets
                    internal_week_num = internal_week_num + 1

                if len(error_graphs_data['external_time_line']) > 0:
                    external_week_name = str('week' + str(external_week_num))
                    external_accuracy_timeline[external_week_name] = error_graphs_data['external_time_line']['external_time_line']
                    external_accuracy_packets = {}
                    if error_graphs_data.has_key('external_accuracy_graph'):
                        extr_accuracy_perc = error_graphs_data['external_accuracy_graph']
                    else:
                        extr_accuracy_perc = error_graphs_data['extr_err_accuracy']['packets_percntage']
                    for ex_acc_key,ex_acc_value in extr_accuracy_perc.iteritems():
                        if external_accuracy_packets.has_key(ex_acc_key):
                            if isinstance(ex_acc_value,list):
                                external_accuracy_packets[ex_acc_key].append(ex_acc_value[0])
                            else:
                                external_accuracy_packets[ex_acc_key].append(ex_acc_value)
                        else:
                            if isinstance(ex_acc_value,list):
                                external_accuracy_packets[ex_acc_key] = ex_acc_value
                            else:
                                external_accuracy_packets[ex_acc_key] = [ex_acc_value]
                    #external_accuracy_timeline[month_name] = external_accuracy_packets
                    external_accuracy_timeline[external_week_name] = external_accuracy_packets
                    external_week_num = external_week_num + 1




                """if len(error_graphs_data['external_time_line']) > 0:
                    external_week_name = str('week' + str(external_week_num))
                    external_accuracy_timeline[external_week_name] = error_graphs_data['external_time_line']['external_time_line']
                    external_week_num = external_week_num + 1
                for vol_key, vol_values in error_graphs_data['internal_accuracy_graph'].iteritems():
                    if all_internal_error_accuracy.has_key(vol_key):
                        all_internal_error_accuracy[vol_key].append(vol_values)
                    else:
                        all_internal_error_accuracy[vol_key] = [vol_values]
                if error_graphs_data.has_key('external_accuracy_graph'):
                    for vol_key, vol_values in error_graphs_data['external_accuracy_graph'].iteritems():
                        if all_external_error_accuracy.has_key(vol_key):
                            all_external_error_accuracy[vol_key].append(vol_values)
                        else:
                            all_external_error_accuracy[vol_key] = [vol_values]"""
                if error_graphs_data.has_key('extr_err_accuracy'):
                    for vol_key, vol_values in error_graphs_data['extr_err_accuracy']['packets_percntage'].iteritems():
                        if all_external_error_accuracy.has_key(vol_key):
                            all_external_error_accuracy[vol_key].append(vol_values[0])
                        else:
                            all_external_error_accuracy[vol_key] = vol_values
        # below for productivity,packet wise performance
        result_dict['fte_calc_data'] = {}
        prj_name = Project.objects.get(id=prj_id[0]).name
        if prj_name == 'NTT DATA Services Coding':
            final_total_fte_calc =prod_volume_week_util_dell_coding(week_names, total_fte_list, {},'week')
            final_total_wp_fte_calc = prod_volume_week_util_dell_coding(week_names, wp_fte_list, {},'week')
        else:
            final_total_fte_calc = prod_volume_week_util(week_names, total_fte_list, {})
            final_total_wp_fte_calc = prod_volume_week_util(week_names, wp_fte_list, {})


        #final_total_fte_calc = prod_volume_week(week_names, total_fte_list, {})
        #final_total_fte_calc = prod_volume_week_util(week_names, total_fte_list, {})
        result_dict['fte_calc_data']['total_fte'] = graph_data_alignment_color(final_total_fte_calc, 'data',level_structure_key, prj_id, center,'sum_total_fte')
        final_prod_avg_details = prod_volume_week_util(week_names, prod_avg_dt, {})
        result_dict['production_avg_details'] = graph_data_alignment_color(final_prod_avg_details, 'data',level_structure_key, prj_id, center) 
        #final_total_wp_fte_calc = prod_volume_week(week_names, wp_fte_list, {})
        #final_total_wp_fte_calc = prod_volume_week_util(week_names, wp_fte_list, {})
        result_dict['fte_calc_data']['work_packet_fte'] = graph_data_alignment_color(final_total_wp_fte_calc, 'data',level_structure_key, prj_id,center,'total_fte')
        final_tat_details = prod_volume_week_util(week_names, tat_graph_dt, {})
        result_dict['tat_graph_details'] = graph_data_alignment_color(final_tat_details,'data', level_structure_key, prj_id, center,'Tat Graph')
        tat_min_max = adding_min_max('tat_graph_details', final_tat_details) 
        final_utlil_operational = prod_volume_week_util(week_names, utilization_operational_dt, {})
        result_dict['utilization_operational_details'] = graph_data_alignment_color(final_utlil_operational,'data', level_structure_key, prj_id,center,'operational_utilization')
        final_util_fte = prod_volume_week_util(week_names, utilization_fte_dt, {})
        result_dict['utilization_fte_details'] = graph_data_alignment_color(final_util_fte, 'data',level_structure_key, prj_id, center,'fte_utilization')
        #final_montly_vol_data = prod_volume_week(week_names, monthly_vol_data, {})
        monthly_work_done = monthly_vol_data['total_workdone'].count(0)
        monthly_total_target = monthly_vol_data['total_target'].count(0)
        if monthly_work_done == len(monthly_vol_data['total_workdone']) and monthly_total_target == len(monthly_vol_data['total_target']) :
            monthly_vol_data = {}
        final_montly_vol_data = previous_sum(monthly_vol_data)
        result_dict['monthly_volume_graph_details'] = graph_data_alignment_color(final_montly_vol_data, 'data', level_structure_key,prj_id, center) 
        result_dict['monthly_volume_graph_details'] = graph_data_alignment_color(final_montly_vol_data, 'data', level_structure_key,prj_id, center,'monthly_volume')

        final_productivity = prod_volume_week(week_names, productivity_list, final_productivity)
        #final_vol_graph_bar_data = prod_volume_week(week_names, vol_graph_bar_data, final_vol_graph_bar_data)
        final_vol_graph_bar_data = volume_status_week(week_names, vol_graph_bar_data, final_vol_graph_bar_data)
        #final_vol_graph_line_data = prod_volume_week(week_names, vol_graph_line_data, final_vol_graph_line_data)
        final_vol_graph_line_data = received_volume_week(week_names, vol_graph_line_data, final_vol_graph_line_data)
        result_dict['volume_graphs'] = {}
        result_dict['volume_graphs']['bar_data'] = graph_data_alignment_color(final_vol_graph_bar_data,'data', level_structure_key,prj_id,center,'volume_bar_graph') 
        result_dict['volume_graphs']['line_data'] = graph_data_alignment_color(final_vol_graph_line_data,'data', level_structure_key,prj_id,center,'volume_productivity_graph') 

        final_internal_accuracy_timeline = errors_week_calcuations(week_names, internal_accuracy_timeline,final_internal_accuracy_timeline)
        final_external_accuracy_timeline = errors_week_calcuations(week_names, external_accuracy_timeline,final_external_accuracy_timeline)
        final_main_productivity_timeline = errors_week_calcuations(week_names, main_productivity_timeline, {})
        final_utilization_timeline = errors_week_calcuations(week_names, utilization_timeline, {})
        result_dict['original_productivity_graph'] = graph_data_alignment_color(final_main_productivity_timeline,'data', level_structure_key, prj_id,center,'productivity_trends')
        result_dict['original_utilization_graph'] = graph_data_alignment_color(final_utilization_timeline, 'data',level_structure_key, prj_id, center,'utilisation_wrt_work_packet')
        productivity_min_max = adding_min_max('original_productivity_graph', final_main_productivity_timeline)
        utilization_min_max = adding_min_max('original_utilization_graph', final_utilization_timeline)
        result_dict.update(productivity_min_max)
        result_dict.update(utilization_min_max)
        # result_dict['internal_time_line'] = graph_data_alignment(final_internal_accuracy_timeline,name_key='data')
        result_dict['internal_time_line'] = graph_data_alignment_color(final_internal_accuracy_timeline, 'data',level_structure_key, prj_id, center,'internal_accuracy_timeline')

        internal_pareto_anlysis_data = week_month_pareto_calc(week_names, internal_pareto_error_count,final_internal_accuracy_timeline)
        result_dict['internal_pareto_graph_data'] = internal_pareto_anlysis_data
        external_pareto_anlysis_data = week_month_pareto_calc(week_names,externl_pareto_error_count,final_external_accuracy_timeline)
        result_dict['external_pareto_graph_data'] = external_pareto_anlysis_data

        int_error_timeline_min_max = error_timeline_min_max(final_internal_accuracy_timeline)
        result_dict['min_internal_time_line'] = int_error_timeline_min_max['min_value']
        result_dict['max_internal_time_line'] = int_error_timeline_min_max['max_value']
        # result_dict['external_time_line'] = graph_data_alignment(final_external_accuracy_timeline,name_key='data')
        result_dict['external_time_line'] = graph_data_alignment_color(final_external_accuracy_timeline, 'data',
                                                                       level_structure_key, prj_id, center,'external_accuracy_timeline')
        ext_error_timeline_min_max = error_timeline_min_max(final_external_accuracy_timeline)
        result_dict['min_external_time_line'] = ext_error_timeline_min_max['min_value']
        result_dict['max_external_time_line'] = ext_error_timeline_min_max['max_value']
        error_volume_data = {}
        volume_new_data = []
        for key, value in final_productivity.iteritems():
            error_graph = []
            error_volume_data[key] = sum(value)
            error_graph.append(key.replace('NA_', '').replace('_NA', ''))
            error_graph.append(sum(value))
            volume_new_data.append(error_graph)
        # result_dict['productivity_data'] = graph_data_alignment(final_productivity, name_key='data')
        result_dict['productivity_data'] = graph_data_alignment_color(final_productivity, 'data', level_structure_key,prj_id, center)
        result_dict['volumes_data'] = {}
        result_dict['volumes_data']['volume_new_data'] = volume_new_data

        """for error_key, error_value in all_internal_error_accuracy.iteritems():
            all_internal_error_accuracy[error_key] = sum(error_value) / len(error_value)
        for error_key, error_value in all_external_error_accuracy.iteritems():
            all_external_error_accuracy[error_key] = sum(error_value) / len(error_value)
        # result_dict['internal_accuracy_graph'] = graph_data_alignment(all_internal_error_accuracy, name_key='y')
        result_dict['internal_accuracy_graph'] = graph_data_alignment_color(all_internal_error_accuracy, 'y',level_structure_key, prj_id,center,'internal_error_accuracy')
        int_min_max = min_max_num(all_internal_error_accuracy)
        result_dict['int_min_value'] = int_min_max['min_value']
        result_dict['int_max_value'] = int_min_max['max_value']
        # result_dict['external_accuracy_graph'] = graph_data_alignment(all_external_error_accuracy, name_key='y')
        result_dict['external_accuracy_graph'] = graph_data_alignment_color(all_external_error_accuracy, 'y',level_structure_key, prj_id, center,'external_error_accuracy')
        ext_min_max = min_max_num(all_external_error_accuracy)
        result_dict['ext_min_value'] = ext_min_max['min_value']
        result_dict['ext_max_value'] = ext_min_max['max_value']"""
        result_dict['data']['date'] = data_date
        return result_dict

def num_of_days(to_date,from_date):
    date_list=[]
    no_of_days = to_date - from_date
    no_of_days = int(re.findall('\d+', str(no_of_days))[0])
    for i in range(0, no_of_days + 1):
        date_list.append(str(from_date + timedelta(days=i)))
    return date_list

def static_production_data(request):
    final_data_dict = {}
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
    date_list = []
    #days_code
    to_date = datetime.date.today() - timedelta(1)
    from_dates = to_date - timedelta(6)
    days_list = num_of_days(to_date, from_dates)

    #weeks_code
    date = datetime.date.today()
    last_date = date - relativedelta(months=1)
    start_date = datetime.datetime(date.year, date.month, 1)
    from_date = datetime.datetime(last_date.year, last_date.month, 1).date()
    to_date = start_date.date() - relativedelta(days=1)
    days = (to_date - from_date).days
    days = days + 1
    months_dict = {}
    for i in range(0, days):
        date = from_date + datetime.timedelta(i)
        month = date.strftime("%B")
        if month in months_dict:
            months_dict[month].append(str(date))
        else:
            months_dict[month] = [str(date)]
    weeks = []
    weekdays = []
    if months_dict == {}:
        num_days = to_date.day
        start = 1
        end = 7 - from_date.weekday()
        while start <= num_days:
            weeks.append({'start': start, 'end': end})
            sdate = from_date + datetime.timedelta(start - 1)
            edate = from_date + datetime.timedelta(end - 1)
            weekdays.append({'start': sdate, 'end': edate})
            start = end + 1
            end = end + 7
            if end > num_days:
                end = num_days

    month_lst = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October','November', 'December']
    month_order = OrderedDict(sorted(months_dict.items(), key=lambda x: month_lst.index(x[0])))
    for month_na in tuple(month_order):
        one_month = months_dict[month_na]
        fro_mon = datetime.datetime.strptime(one_month[0], '%Y-%m-%d').date()
        to_mon = datetime.datetime.strptime(one_month[-1:][0], '%Y-%m-%d').date()
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
    week_list = []
    for w_days in weekdays:
        date_list = num_of_days(w_days['end'], w_days['start'])
        week_list.append(date_list)
    dwm_dict = {}
    employe_dates = {}
    dwm_dict['week'] = week_list
    for week in week_list:
        if week and employe_dates.has_key('days'):
            employe_dates['days'] = employe_dates['days'] + week
        else:
            employe_dates['days'] = week

    level_structure_key = {}
    if (work_packet) and (work_packet != 'undefined'): level_structure_key['work_packet'] = work_packet
    if (sub_project) and (sub_project != 'undefined'): level_structure_key['sub_project'] = sub_project
    if (sub_packet) and (sub_packet != 'undefined'): level_structure_key['sub_packet'] = sub_packet

    project = request.GET['project'].split('-')[0].strip()
    center_id = request.GET['center'].split('-')[0].strip()
    count = 0
    all_count = [count + 1 for key in level_structure_key.values() if key == "All"]
    if len(all_count) >= 2:
        if len(level_structure_key) != 3:
            level_structure_key = {}
        if len(all_count) == 3:
            level_structure_key = {}

    center = Center.objects.filter(name=center_id).values_list('id', flat=True)
    prj_id = Project.objects.filter(name=project).values_list('id', flat=True)
    if not level_structure_key:
        sub_pro_level = filter(None, RawTable.objects.filter(project=prj_id, center=center).values_list('sub_project',flat=True).distinct())
        if len(sub_pro_level) >= 1:
            level_structure_key['sub_project'] = "All"
        if not level_structure_key:
            work_pac_level = filter(None,RawTable.objects.filter(project=prj_id, center=center).values_list('work_packet',flat=True).distinct())
            if len(work_pac_level) >= 1:
                level_structure_key['work_packet'] = "All"
        if not level_structure_key:
            sub_pac_level = filter(None,RawTable.objects.filter(project=prj_id, center=center).values_list('sub_packet',flat=True).distinct())
            if len(sub_pac_level) >= 1:
                level_structure_key['sub_packet'] = "All"

    final_data = product_total_graph(days_list,prj_id,center,work_packet,level_structure_key)
    del final_data['prod_days_data']
    del final_data['volumes_data']['volume_type']
    del final_data['volumes_data']['volume_new_data']
    day_dict = {} 
    day_dict['data'] = {} 
    if final_data['data'].has_key('date'):
        day_dict['data']['date'] = final_data['data']['date']
    day_dict['data']['data'] = graph_data_alignment_color(final_data['data']['data'], 'data',level_structure_key, prj_id, center) 
    final_data_dict = day_dict

    #final_data_dict = final_data

    data_date = []
    week_num = 0
    week_names = []
    final_production = {}
    productivity_list = {}
    for week_key, week_dates in dwm_dict.iteritems():
        for week in week_dates:
            data_date.append(week[0] + ' to ' + week[-1])
            result = product_total_graph(week, prj_id, center, work_packet, level_structure_key)
            if len(result['prod_days_data']) > 0:
                week_name = str('week' + str(week_num))
                week_names.append(week_name)
                productivity_list[week_name] = result['volumes_data']['volume_values']
                week_num = week_num + 1
            else:
                week_name = str('week' + str(week_num))
                week_names.append(week_name)
                productivity_list[week_name] = {}
                week_num = week_num + 1

    final_production = prod_volume_week(week_names, productivity_list, final_production)
    error_volume_data = {}
    volume_new_data = []
    for key, value in final_production.iteritems():
        error_graph = []
        error_volume_data[key] = sum(value)
        error_graph.append(key.replace('NA_', '').replace('_NA', ''))
        error_graph.append(sum(value))
        volume_new_data.append(error_graph)

    final_data_dict['week_productivity_data'] = {}
    final_data_dict['week_productivity_data']['data'] = graph_data_alignment_color(final_production, 'data',level_structure_key, prj_id, center)
    final_data_dict['week_productivity_data']['date'] = data_date
    #month code
    current_date = datetime.date.today()
    last_mon_date = current_date - relativedelta(months=3)
    from_date = datetime.datetime(last_mon_date.year, last_mon_date.month, 1).date()
    start_date = datetime.datetime(current_date.year, current_date.month, 1)
    to_date = start_date.date() - relativedelta(days=1)
    days = (to_date - from_date).days
    days = days + 1
    months_dict = {}
    month_list = [[]]
    month_names_list = []
    month_count = 0
    for i in range(0, days):
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
    new_month_dict = {}
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October','November', 'December']
    k = OrderedDict(sorted(months_dict.items(), key=lambda x: months.index(x[0])))
    dwm_dict['month'] = months_dict
    month_names = []
    final_month_productivity = {}
    production_list = {}
    data_date = []
    for month_na,month_va in zip(month_names_list,month_list):
        month_name = month_na
        month_dates = month_va
        data_date.append(month_dates[0] + ' to ' + month_dates[-1])
        result = product_total_graph(month_dates, prj_id, center, work_packet, level_structure_key)
        if len(result['prod_days_data']) > 0:
            production_list[month_name] = result['volumes_data']['volume_values']
            month_names.append(month_name)
        else:
            production_list[month_name] = {}
            month_names.append(month_name)
        packet_sum_data = result['volumes_data']['volume_values']
    final_month_productivity = prod_volume_week(month_names, production_list, final_month_productivity)
    error_month_volume_data = {}
    volume_new_data = []
    for key, value in final_month_productivity.iteritems():
        error_month_graph = []
        error_month_volume_data[key] = sum(value)
        error_month_graph.append(key.replace('NA_', '').replace('_NA', ''))
        error_month_graph.append(sum(value))
        volume_new_data.append(error_month_graph)
    final_data_dict['month_productivity_data'] = {}
    final_data_dict['month_productivity_data']['data'] = graph_data_alignment_color(final_month_productivity, 'data', level_structure_key, prj_id,center)
    final_data_dict['month_productivity_data']['date'] = data_date
    del result['volumes_data']
    del result['prod_days_data']
    del result['data']
    return HttpResponse(final_data_dict)


def fte_calculation_sub_project_work_packet(result,level_structure_key):
    final_fte ={}
    count = 0
    if result.has_key('data'):
        new_date_list = result['new_date_list']
        wp_subpackets = result['wp_subpackets']
        for date_va in new_date_list:
            for wp_key_new, wp_name in wp_subpackets.iteritems():
                local_sum = 0
                for sub_packet in wp_name:
                    new_level_structu_key = {}
                    if level_structure_key.has_key('sub_project'):
                        new_level_structu_key['sub_project'] = level_structure_key['sub_project']
                    new_level_structu_key['work_packet'] = wp_key_new
                    new_level_structu_key['sub_packet'] = sub_packet
                    final_work_packet = level_hierarchy_key(level_structure_key, new_level_structu_key)

                    if result['data']['data'].has_key(final_work_packet):
			if len(result['data']['data'][final_work_packet]) >= count:
			    try:
                            	local_sum = local_sum + result['data']['data'][final_work_packet][count]
			    except:
				local_sum = local_sum
			else:
			    local_sum = local_sum
                    else:
                        local_sum = local_sum
                    if level_structure_key.get('work_packet', '') != 'All':
                        if final_fte.has_key(final_work_packet):
                            final_fte_sum = float('%.2f' % round(local_sum, 2))
                            final_fte[final_work_packet].append(final_fte_sum)
                        else:
                            final_fte_sum = float('%.2f' % round(local_sum, 2))
                            final_fte[final_work_packet] = [final_fte_sum]
                if level_structure_key.get('work_packet', '') == 'All':
                    if level_structure_key.has_key('sub_project'):
                        new_level_structu_key['sub_project'] = level_structure_key['sub_project']
                    new_level_structu_key['work_packet'] = wp_key_new
                    wp_final_work_packet = level_hierarchy_key(level_structure_key, new_level_structu_key)
                    if final_fte.has_key(wp_final_work_packet):
                        final_fte_sum = float('%.2f' % round(local_sum, 2))
                        final_fte[wp_final_work_packet].append(final_fte_sum)
                    else:
                        final_fte_sum = float('%.2f' % round(local_sum, 2))
                        final_fte[wp_final_work_packet] = [final_fte_sum]
            count = count + 1
        return final_fte


def fte_wp_total(final_fte):
    work_packet_fte = {}
    work_packet_fte['wp_fte'] = {}
    work_packet_fte['wp_fte'] = [sum(i) for i in zip(*final_fte.values())]
    work_packet_fte['wp_fte'] = [float('%.2f' % round(wp_values, 2)) for wp_values in work_packet_fte['wp_fte']]
    return work_packet_fte


def fte_calculation_sub_project_sub_packet(prj_id,center_obj,work_packet_query,level_structure_key,date_list):
    packets_target = {}
    new_date_list = []
    conn = redis.Redis(host="localhost", port=6379, db=0)
    prj_name = Project.objects.filter(id=prj_id).values_list('name', flat=True)
    center_name = Center.objects.filter(id=center_obj).values_list('name', flat=True)
    """work_packets = Targets.objects.filter(**work_packet_query).values('sub_project', 'work_packet', 'sub_packet','fte_target').distinct()
    for wp_dict in work_packets:
        packets_target[wp_dict['sub_packet']] = int(wp_dict['fte_target'])"""
    distinct_wp = Targets.objects.filter(**work_packet_query).values_list('work_packet', flat=True).distinct()
    wp_subpackets = {}
    new_work_packet_query = work_packet_query
    for wrk_pkt in distinct_wp:
        work_packet_query['work_packet'] = wrk_pkt
        distinct_sub_pkt = Targets.objects.filter(**work_packet_query).values_list('sub_packet', flat=True).distinct()
        wp_subpackets[wrk_pkt] = distinct_sub_pkt
    raw_query_set = {}
    raw_query_set['project'] = prj_id
    raw_query_set['center'] = center_obj
    date_values = {}
    volumes_dict = {}
    result = {}
    for date_va in date_list:
        new_work_packet_query['from_date__gte'] = date_va
        new_work_packet_query['to_date__lte'] = date_va
        if new_work_packet_query.has_key('work_packet'):
            del new_work_packet_query['work_packet']
        work_packets = Targets.objects.filter(**new_work_packet_query).values('sub_project', 'work_packet', 'sub_packet','fte_target').distinct()
        for wp_dict in work_packets:
            packets_target[wp_dict['sub_packet']] = int(wp_dict['fte_target'])
        total_done_value = RawTable.objects.filter(project=prj_id, center=center_obj, date=date_va).aggregate(Max('per_day'))
        if total_done_value['per_day__max'] > 0:
            new_date_list.append(date_va)
            for wp_key, wp_name in wp_subpackets.iteritems():
                for sub_packet in wp_name:
                    new_level_structu_key = {}
                    if level_structure_key.has_key('sub_project'):
                        new_level_structu_key['sub_project'] = level_structure_key['sub_project']
                    new_level_structu_key['work_packet'] = wp_key
                    new_level_structu_key['sub_packet'] = sub_packet
                    final_work_packet = level_hierarchy_key(level_structure_key, new_level_structu_key)
                    date_pattern = '{0}_{1}_{2}_{3}'.format(prj_name[0], str(center_name[0]), str(final_work_packet),date_va)
                    key_list = conn.keys(pattern=date_pattern)
                    if not key_list:
                        if date_values.has_key(final_work_packet):
                            date_values[final_work_packet].append(0)
                        else:
                            date_values[final_work_packet] = [0]
                    #import pdb;pdb.set_trace()
                    for cur_key in key_list:
                        var = conn.hgetall(cur_key)
                        for key, value in var.iteritems():
                            if value == 'None':
                                value = 0
                            if date_values.has_key(key):
                                try:
                                    fte_sum = float(value) / packets_target[sub_packet]
                                except:
                                    fte_sum = 0
                                #final_fte = float('%.2f' % round(fte_sum, 2))
                                #date_values[key].append(final_fte)
                                date_values[key].append(fte_sum)
                            else:
                                if packets_target.has_key(sub_packet)>0:
                                    if packets_target[sub_packet]>0:
                                        fte_sum = float(value) / packets_target[sub_packet]
                                        #final_fte = float('%.2f' % round(fte_sum, 2))
                                        #date_values[key] = [final_fte]
                                        date_values[key] = [fte_sum]
                        volumes_dict['data'] = date_values
                        volumes_dict['date'] = date_list
                        result['data'] = volumes_dict
    result['wp_subpackets'] = wp_subpackets
    result['new_date_list'] = new_date_list
    return result



def fte_calculation(request,prj_id,center_obj,date_list,level_structure_key):
    query_set = {} 
    query_set['project'] = prj_id
    query_set['center'] = center_obj
    prj_name = Project.objects.filter(id=prj_id).values_list('name', flat=True)
    center_name = Center.objects.filter(id=center_obj).values_list('name', flat=True)
    work_packet_query =  query_set_generation(prj_id,center_obj,level_structure_key,[])
    work_packet_query['from_date__gte'] = date_list[0]
    work_packet_query['to_date__lte'] = date_list[-1]
    work_packets = Targets.objects.filter(**work_packet_query).values('sub_project','work_packet','sub_packet','fte_target').distinct()
    sub_packet_query = query_set_generation(prj_id,center_obj,level_structure_key,[])
    sub_packet_query['from_date__gte'] = date_list[0]
    sub_packet_query['to_date__lte'] = date_list[-1]
    sub_packets = filter(None,Targets.objects.filter(**sub_packet_query).values_list('sub_packet',flat=True).distinct())
    print "sub_packets",sub_packets
    conn = redis.Redis(host="localhost", port=6379, db=0)
    new_date_list = []
    status = 0
    if len(sub_packets) == 0:
        #work_packet_query['from_date__lte'] = date_list[0]
        #work_packet_query['to_date__gte'] = date_list[-1]
        work_packets = Targets.objects.filter(**work_packet_query).values('sub_project', 'work_packet', 'sub_packet','fte_target').distinct()
        print 'targte',work_packets
        date_values = {}
        volumes_dict = {}
        result = {}
        for date_va in date_list:
            total_done_value = RawTable.objects.filter(project=prj_id, center=center_obj, date=date_va).aggregate(Max('per_day'))
            if total_done_value['per_day__max'] > 0:
                new_date_list.append(date_va)
                for wp_packet in work_packets:
                    final_work_packet = level_hierarchy_key(level_structure_key, wp_packet)
                    date_pattern = '{0}_{1}_{2}_{3}'.format(prj_name[0], str(center_name[0]), str(final_work_packet),date_va)
                    key_list = conn.keys(pattern=date_pattern)
                    if wp_packet['fte_target'] >0:
                        if not key_list:
                            if date_values.has_key(final_work_packet):
                                date_values[final_work_packet].append(0)
                            else:
                                date_values[final_work_packet] = [0]
                        for cur_key in key_list:
                            var = conn.hgetall(cur_key)
                            for key, value in var.iteritems():
                                if value == 'None':
                                    value = 0
                                if date_values.has_key(key):
                                    fte_sum = float(value) / int(wp_packet['fte_target'])
                                    #final_fte = float('%.2f' % round(fte_sum, 2))
                                    #date_values[key].append(final_fte)
                                    date_values[key].append(fte_sum)
                                else:
                                    fte_sum = float(value) / int(wp_packet['fte_target'])
                                    #final_fte = float('%.2f' % round(fte_sum, 2))
                                    #date_values[key] = [final_fte]
                                    date_values[key] = [fte_sum]
                        volumes_dict['data'] = date_values
                        volumes_dict['date'] = date_list
                        result['data'] = volumes_dict
    else:
        if level_structure_key.get('sub_project','')=='All':
            sub_projects = filter(None, Targets.objects.filter(**sub_packet_query).values_list('sub_project',flat=True).distinct())
            final_fte = {}
            for sub_project in sub_projects:
                sub_project_query = {}
                sub_project_query['project'] = prj_id
                sub_project_query['center'] = center_obj
                sub_project_query['sub_project'] = sub_project
                new_level_structu_key = {}
                new_level_structu_key['sub_project'] = sub_project
                new_level_structu_key['work_packet'] = 'All'
                new_level_structu_key['sub_packet'] = 'All'
                result = fte_calculation_sub_project_sub_packet(prj_id, center_obj, sub_project_query, new_level_structu_key,date_list)
                sub_packet_data = fte_calculation_sub_project_work_packet(result, new_level_structu_key)
                if sub_packet_data :
                    wp_total_data = fte_wp_total(sub_packet_data)
                    if len(wp_total_data['wp_fte']) > 0:
                        final_fte[sub_project] = wp_total_data['wp_fte']
        else:
            result = fte_calculation_sub_project_sub_packet(prj_id,center_obj,work_packet_query,level_structure_key,date_list)
    
    count = 0
    if (len(sub_packets) == 0) :
        final_fte = {}
        if result.has_key('data'):
            final_fte= result['data']['data']
            for wp_key, wp_value in final_fte.iteritems():
                final_fte[wp_key] = [float('%.2f' % round(wp_values, 2)) for wp_values in wp_value]
    else :
        if level_structure_key.get('sub_project', '') != 'All':
            final_fte = {}
            if result.has_key('data'):
                new_date_list = result['new_date_list']
                wp_subpackets = result['wp_subpackets']
                for date_va in new_date_list:
                    for wp_key_new, wp_name in wp_subpackets.iteritems():
                        local_sum = 0
                        for sub_packet in wp_name:
                            if level_structure_key.has_key('sub_project'):
                                if (level_structure_key.get('sub_project','All')!= 'All') and (level_structure_key.get('work_packet','All')!='All') and (level_structure_key.get('sub_packet','All')=='All'):
                                    local_sum = 0
                            new_level_structu_key = {}
                            if level_structure_key.has_key('sub_project'):
                                new_level_structu_key['sub_project']=level_structure_key['sub_project']
                            new_level_structu_key['work_packet'] = wp_key_new
                            new_level_structu_key['sub_packet'] = sub_packet
                            #final_work_packet = wp_key+'_'+sub_packet
                            final_work_packet = level_hierarchy_key(level_structure_key, new_level_structu_key)

                            if result['data']['data'].has_key(final_work_packet):
                                try:#local_sum = local_sum + result['data']['data'][final_work_packet][count]
                                    local_sum = local_sum + result['data']['data'][final_work_packet][count]
                                except:
                                    local_sum = 0
                            else:
                                local_sum = local_sum
                            if level_structure_key.get('work_packet','') != 'All' :
                                if final_fte.has_key(final_work_packet):
                                    final_fte_sum = float('%.2f' % round(local_sum, 2))
                                    final_fte[final_work_packet].append(final_fte_sum)
                                else:
                                    final_fte_sum = float('%.2f' % round(local_sum, 2))
                                    final_fte[final_work_packet] = [final_fte_sum]
                        if level_structure_key.get('work_packet','') == 'All' :
                            new_wp_level_structu_key = {}
                            if level_structure_key.has_key('sub_project'):
                                new_wp_level_structu_key['sub_project']=level_structure_key['sub_project']
                            new_wp_level_structu_key['work_packet'] = wp_key_new
                            wp_final_work_packet = level_hierarchy_key(level_structure_key, new_wp_level_structu_key)
                            if final_fte.has_key(wp_final_work_packet):
                                final_fte_sum = float('%.2f' % round(local_sum, 2))
                                final_fte[wp_final_work_packet].append(final_fte_sum)
                            else:
                                final_fte_sum = float('%.2f' % round(local_sum, 2))
                                final_fte[wp_final_work_packet] = [final_fte_sum]
                    count =count+1
    type = request.GET['type']
    if request.GET['project'].split(' - ')[0] == 'NTT DATA Services TP': 
        if type == "day":
            work_packet_fte = {} 
            work_packet_fte['total_fte'] = {} 
            work_packet_fte['total_fte'] = [sum(i) for i in zip(*final_fte.values())]
            #work_packet_fte['total_fte'] = [float('%.2f' % round(wp_values, 2)) for wp_values in work_packet_fte['total_fte']]
            work_packet_fte['total_fte'] = [round(wp_values, 2) for wp_values in work_packet_fte['total_fte']]
            fte_high_charts = {} 
            #fte_high_charts['total_fte'] = graph_data_alignment_color(work_packet_fte, 'data', level_structure_key, prj_id, center_obj)
            fte_high_charts['total_fte'] = work_packet_fte
            #fte_high_charts['work_packet_fte'] = graph_data_alignment(final_fte, name_key='data')
            fte_high_charts['work_packet_fte'] = graph_data_alignment_color(final_fte, 'data', level_structure_key, prj_id, center_obj,'')
            fte_high_charts['work_packet_fte'] =final_fte
            #fte_high_charts['fte_date_list'] = new_date_list
        if type == "week" or type == "month":
            work_packet_fte = {}
            packet_fte = {}
            #count = 0
            for key,value in final_fte.iteritems():
                count = 0
                if final_fte.has_key(key):
                    if 0.0 in value:
                        count = collections.Counter(value)
                        count_value = count[0.0]
                    else:
                        count_value = 0
                count_num = len(value) - count_value
                fte_sum = sum(value)/count_num
                packet_fte[key] = float('%.2f' % round(fte_sum, 2))
            fte_high_charts = {}
            fte_high_charts['total_fte'] = {}
            #fte_high_charts['total_fte'] = sum(packet_fte.values())
            final_fte_values = sum(packet_fte.values())
            fte_high_charts['total_fte']['total_fte'] = [float('%.2f' % round(final_fte_values, 2))]
            fte_high_charts['work_packet_fte'] = graph_data_alignment_color(final_fte, 'data', level_structure_key, prj_id, center_obj,'')
            fte_high_charts['work_packet_fte'] = final_fte
        return fte_high_charts 
    else:
        work_packet_fte = {} 
        work_packet_fte['total_fte'] = {} 
        work_packet_fte['total_fte'] = [sum(i) for i in zip(*final_fte.values())]
        #work_packet_fte['total_fte'] = [float('%.2f' % round(wp_values, 2)) for wp_values in work_packet_fte['total_fte']]
        work_packet_fte['total_fte'] = [round(wp_values, 2) for wp_values in work_packet_fte['total_fte']]
        fte_high_charts = {} 
        #fte_high_charts['total_fte'] = graph_data_alignment_color(work_packet_fte, 'data', level_structure_key, prj_id, center_obj)
        fte_high_charts['total_fte'] = work_packet_fte
        #fte_high_charts['work_packet_fte'] = graph_data_alignment(final_fte, name_key='data')
        fte_high_charts['work_packet_fte'] = graph_data_alignment_color(final_fte, 'data', level_structure_key, prj_id, center_obj,'')
        fte_high_charts['work_packet_fte'] =final_fte
        return fte_high_charts

def top_five_emp(center,prj_id,dwm_dict,level_key_structure):
    all_details_list = []
    final_list = []
    emplyee_packet_query = query_set_generation(prj_id,center,level_key_structure,dwm_dict['days'])
    packets_list = RawTable.objects.filter(**emplyee_packet_query).values_list('work_packet',flat=True).distinct()
    for i in packets_list:
        dict_to_render = []
        employee_name = RawTable.objects.filter(project=prj_id,center=center,date__range=[dwm_dict['days'][0],dwm_dict['days'][-1:][0]],work_packet=i).values_list('employee_id').distinct()
        for name in employee_name:
            values = RawTable.objects.filter(project=prj_id,center=center,date__range=[dwm_dict['days'][0],dwm_dict['days'][-1:][0]],work_packet=i,employee_id=name[0]).values_list('per_day','date')
            result = 0
            for val in values:
                tar = Targets.objects.filter(project=prj_id,center=center,work_packet=i,from_date__lte=val[1],to_date__gte=val[1]).values_list('target',flat=True)
                if tar:
                    if tar[0]>0:
                        productivity = float(val[0]) / int(tar[0])
                    else:
                        productivity = 0
                    result = result + productivity
            result = float('%.2f' % round(result, 2))
            dict_to_render.append({'employee_id':name[0],'work_packet':i,'productivity':result})
            all_details_list.append({'employee_id':name[0],'work_packet':i,'productivity':result})
        max_in_packet = max([i['productivity'] for i in dict_to_render])
        top_in = [i if i['productivity'] == max_in_packet else '' for i in dict_to_render]
        required_top = [x for x in top_in if x]
        for i in required_top:
            final_list.append(i)
    if len(packets_list) > 1:
        return final_list
    else:
        return all_details_list
    """ dict_to_render = []
    all_packets_list = RawTable.objects.filter(project=prj_id,center=center,date__range=[dwm_dict['days'][0], dwm_dict['days'][-1:][0]]).values_list('work_packet').distinct()
    for one_pack in all_packets_list:
        targets = Targets.objects.filter(project=prj_id, center=center,work_packet=one_pack[0]).values_list('target',flat=True).distinct()
        max_value = RawTable.objects.filter(project=prj_id, center=center, work_packet=one_pack[0],
            date__range=[dwm_dict['days'][0], dwm_dict['days'][-1:][0]]).aggregate(Max('per_day'))['per_day__max']
        list_of_values = RawTable.objects.filter(project=prj_id, center=center, work_packet=one_pack[0],
            date__range=[dwm_dict['days'][0], dwm_dict['days'][-1:][0]], per_day=max_value).values('employee_id',
                            'date', 'per_day','work_packet')
        if len(list_of_values) > 0:
            list_of_values = list_of_values[0]
        else:
            continue
        for key, value in list_of_values.items():
            list_of_values[key] = str(value)
            if key == 'per_day':
                if targets:
                    productivity = float(value)/int(targets[0])
                    vol_values = float('%.2f' % round(productivity, 2))
                    list_of_values['productivity'] =vol_values
        dict_to_render.append(list_of_values)
    return dict_to_render"""


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
    level_structure_key ={}
    """if work_packet== 'all' :
        work_packet = 'undefined'
    if sub_project== 'all':
        sub_project ='undefined'
    if sub_packet == 'all':
        sub_packet = 'undefined'"""
    if (work_packet) and (work_packet !='undefined'): level_structure_key['work_packet']=work_packet
    if (sub_project) and (sub_project !='undefined'): level_structure_key['sub_project'] = sub_project
    if (sub_packet) and (sub_packet !='undefined'): level_structure_key['sub_packet'] = sub_packet

    project = request.GET['project'].split('-')[0].strip()
    center_id = request.GET['center'].split('-')[0].strip()
    count = 0
    all_count = [count + 1 for key in level_structure_key.values() if key == "All"]
    if len(all_count) >= 2:
        if len(level_structure_key) !=3:
            level_structure_key = {}
        if len(all_count) == 3:
            level_structure_key = {}
    
    center = Center.objects.filter(name=center_id).values_list('id', flat=True)
    prj_id = Project.objects.filter(name=project).values_list('id', flat=True)
    if not level_structure_key:
        #sub_pro_level = RawTable.objects.filter(project=prj_id, center=center).values_list('sub_project',flat=True).distinct()
        sub_pro_level = filter(None,RawTable.objects.filter(project=prj_id, center=center).values_list('sub_project',flat=True).distinct())
        if len(sub_pro_level)>= 1:
            level_structure_key['sub_project'] = "All"
        if not level_structure_key:
            #work_pac_level = RawTable.objects.filter(project=prj_id, center=center).values_list('work_packet',flat=True).distinct()
            work_pac_level = filter(None,RawTable.objects.filter(project=prj_id, center=center).values_list('work_packet',flat=True).distinct())
            if len(work_pac_level)>=1:
                level_structure_key['work_packet'] = "All"
        if not level_structure_key:
            #sub_pac_level = RawTable.objects.filter(project=prj_id, center=center).values_list('sub_packet',flat=True).distinct()
            sub_pac_level = filter(None,RawTable.objects.filter(project=prj_id, center=center).values_list('sub_packet',flat=True).distinct())
            if len(sub_pac_level)>=1:
                level_structure_key['sub_packet'] = "All"

    #center = request.GET['center'].split('-')[0].strip()
    date_list = []
    month_names_list = []
    month_list = []
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
        for i in range(0, days):
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
        for i in range(0, days):
            date = from_date + datetime.timedelta(i)
            weeks_data.append(str(date))
            """month = date.strftime("%B")
            if month in months_dict:
                months_dict[month].append(str(date))
            else:
                months_dict[month] = [str(date)]"""
        weeks = []
        weekdays = []
        """if months_dict == {}:
            num_days = to_date.day
            start = 1
            end = 7 - from_date.weekday()
            while start <= num_days:
                weeks.append({'start': start, 'end': end})
                sdate = from_date + datetime.timedelta(start - 1)
                edate = from_date + datetime.timedelta(end - 1)
                weekdays.append({'start': sdate, 'end': edate})
                start = end + 1
                end = end + 7
                if end > num_days:
                    end = num_days
        #for key, valu in months_dict.iteritems():
        month_lst = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September','October', 'November', 'December']
        month_order = OrderedDict(sorted(months_dict.items(), key=lambda x: month_lst.index(x[0])))
        for month_na in tuple(month_order):
            one_month = months_dict[month_na]
            fro_mon = datetime.datetime.strptime(one_month[0], '%Y-%m-%d').date()
            to_mon = datetime.datetime.strptime(one_month[-1:][0], '%Y-%m-%d').date()
            no_of_days = to_mon- fro_mon
            num_days = int(re.findall('\d+', str(no_of_days))[0])+1
            #num_days = 4
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
        week_list=[]"""
        fro_mon = datetime.datetime.strptime(weeks_data[0],'%Y-%m-%d').date()
        to_mon = datetime.datetime.strptime(weeks_data[-1],'%Y-%m-%d').date()
        no_of_days = to_mon - fro_mon
        num_days = int(re.findall('\d+', str(no_of_days))[0]) + 1
        week_list=[]
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
            #new_month_dict[month_na] = months_dict[month_na]
            new_month_dict[month_na] = {}
            if employe_dates.has_key('days'):
                employe_dates['days'] = employe_dates['days']+months_dict[month_na]
            else:
                employe_dates['days']=months_dict[month_na]
        """for month_name,month_values in months_dict.iteritems():
            if employe_dates.has_key('days'):
                employe_dates['days'] = employe_dates['days']+month_values
            else:
                employe_dates['days']=month_values"""
        #dwm_dict['month'] = months_dict
        dwm_dict['month'] = {'month_names':month_names_list, 'month_dates':month_list}

    if type == 'week':
        dwm_dict['week'] = week_list
        for week in week_list:
            if week and  employe_dates.has_key('days'):
                employe_dates['days'] = employe_dates['days']+week
            else:
                employe_dates['days'] = week


    resul_data = {}
    center = Center.objects.filter(name=center_id).values_list('id', flat=True)
    prj_id = Project.objects.filter(name=project).values_list('id',flat=True)
    #top_five_employee_details = top_five_emp(center,prj_id,employe_dates)
    top_five_employee_details = top_five_emp(center,prj_id,employe_dates,level_structure_key)
    top_five_employee_details = sorted(top_five_employee_details, key=lambda k: k['productivity'],reverse=True)
    emp_rank = [1,2,3,4,5]
    table_headers = []
    if len(top_five_employee_details) >= 5:
        only_top_five = top_five_employee_details[:5]
        for a1,a2 in zip(only_top_five,emp_rank):
            a1['rank'] = a2
            table_headers = ['Rank','Employee Name','Productivity','Packet']
    else:
        only_top_five = top_five_employee_details
        for a1,a2 in zip(only_top_five,emp_rank):
            a1['rank'] = a2
            table_headers = ['Rank', 'Employee Name', 'Productivity', 'Packet']
    final_result_dict = day_week_month(request,dwm_dict,prj_id,center,work_packet,level_structure_key)
    final_result_dict['top_five_employee_details'] = top_five_employee_details
    final_result_dict['only_top_five'] = only_top_five
    #volumes_graphs_details = volumes_graphs_data(date_list,prj_id,center,level_structure_key)
    volumes_graphs_details = volumes_graphs_data_table(employe_dates['days'],prj_id,center,level_structure_key)
    agent_internal_pareto_data = agent_pareto_data_generation(request,employe_dates['days'],prj_id,center,level_structure_key)
    extrnl_agent_pareto_data = agent_external_pareto_data_generation(request, employe_dates['days'], prj_id, center, level_structure_key)
    #category_error_count = sample_pareto_analysis(request, date_list, prj_id, center, level_structure_key,"Internal")
    category_error_count = sample_pareto_analysis(request, employe_dates['days'], prj_id,center, level_structure_key,"Internal")
    #extrnl_category_error_count = sample_pareto_analysis(request, date_list, prj_id, center, level_structure_key, "External")
    extrnl_category_error_count = sample_pareto_analysis(request, employe_dates['days'], prj_id, center, level_structure_key, "External")
    error_graphs_data = internal_extrnal_graphs(request, employe_dates['days'], prj_id, center,{},level_structure_key)
    final_dict = {}
    if error_graphs_data.has_key('internal_accuracy_graph'):
        final_dict['internal_accuracy_graph'] = graph_data_alignment_color(error_graphs_data['internal_accuracy_graph'], 'y', level_structure_key, prj_id, center,'internal_error_accuracy')
    if error_graphs_data.has_key('external_accuracy_graph'):
        final_dict['external_accuracy_graph'] = graph_data_alignment_color(error_graphs_data['external_accuracy_graph'], 'y', level_structure_key, prj_id, center,'external_error_accuracy')
    if error_graphs_data.has_key('extr_err_accuracy'):
        final_extrn_accuracy = {}
        for perc_key,perc_value in error_graphs_data['extr_err_accuracy']['packets_percntage'].iteritems():
            final_extrn_accuracy[perc_key] = perc_value[0]
        final_dict['external_accuracy_graph'] = graph_data_alignment_color(final_extrn_accuracy, 'y', level_structure_key, prj_id, center,'external_error_accuracy')
 
    final_result_dict.update(final_dict)
    final_result_dict['volumes_graphs_details'] = volumes_graphs_details
    final_result_dict['Internal_Error_Category'] = category_error_count
    final_result_dict['External_Error_Category'] = extrnl_category_error_count
    final_result_dict['External_Pareto_data'] = extrnl_agent_pareto_data
    final_result_dict['Pareto_data'] = agent_internal_pareto_data 
    internal_error_types = internal_extrnal_error_types(request, employe_dates['days'], prj_id, center, level_structure_key,"Internal")
    external_error_types = internal_extrnal_error_types(request, employe_dates['days'], prj_id, center,level_structure_key, "External")
    final_result_dict['internal_errors_types'] = graph_data_alignment_color(internal_error_types,'y',level_structure_key,prj_id,center,'')
    final_result_dict['external_errors_types'] = graph_data_alignment_color(external_error_types,'y',level_structure_key,prj_id,center,'')
    final_result_dict['days_type'] = type
    return HttpResponse(final_result_dict)

def volume_graph_data(date_list,prj_id,center_obj,level_structure_key):
    conn = redis.Redis(host="localhost", port=6379, db=0)
    result = {}
    volumes_dict = {}
    date_values = {}
    prj_name = Project.objects.filter(id=prj_id).values_list('name',flat=True)
    center_name = Center.objects.filter(id=center_obj).values_list('name', flat=True)
    query_set = query_set_generation(prj_id,center_obj,level_structure_key,date_list)
    volume_list = worktrack_internal_external_workpackets_list(level_structure_key,'Worktrack',query_set)
    for date_va in date_list:
        total_done_value = RawTable.objects.filter(project=prj_id, center=center_obj, date=date_va).aggregate(Max('per_day'))
        if total_done_value['per_day__max'] > 0:
            count =0
            for vol_type in volume_list:
                final_work_packet = level_hierarchy_key(level_structure_key,vol_type)
                if not final_work_packet:
                    final_work_packet = level_hierarchy_key(volume_list[count],vol_type)
                count = count+1
                date_pattern = '{0}_{1}_{2}_{3}_worktrack'.format(prj_name[0], str(center_name[0]), str(final_work_packet), date_va)
                key_list = conn.keys(pattern=date_pattern)
                if not key_list:
                    if date_values.has_key(final_work_packet):
                        date_values[final_work_packet]['opening'].append(0)
                        date_values[final_work_packet]['received'].append(0)
                        date_values[final_work_packet]['completed'].append(0)
                        date_values[final_work_packet]['non_workable_count'].append(0)
                        date_values[final_work_packet]['closing_balance'].append(0)
                    else:
                        date_values[final_work_packet] = {}
                        date_values[final_work_packet]['opening']= [0]
                        date_values[final_work_packet]['received']= [0]
                        date_values[final_work_packet]['completed'] = [0]
                        date_values[final_work_packet]['non_workable_count'] = [0]
                        date_values[final_work_packet]['closing_balance']= [0]
                for cur_key in key_list:
                    var = conn.hgetall(cur_key)
                    for key,value in var.iteritems():
                        if (value == 'None') or (value == ''):
                            value = 0
                        if not date_values.has_key(final_work_packet):
                            date_values[final_work_packet] = {}
                        if date_values.has_key(final_work_packet):
                            if date_values[final_work_packet].has_key(key):
                                date_values[final_work_packet][key].append(int(value))
                            else:
                                date_values[final_work_packet][key]=[int(value)]

                    volumes_dict['data'] = date_values
                    volumes_dict['date'] = date_list
                    result['data'] = volumes_dict
    if result.has_key('data'):
        opening,received,nwc,closing_bal,completed = [],[],[],[],[]
        for vol_key in result['data']['data'].keys():
            for volume_key,vol_values in result['data']['data'][vol_key].iteritems():
                if volume_key == 'opening':
                    opening.append(vol_values)
                elif volume_key == 'received':
                    received.append(vol_values)
                elif volume_key == 'completed':
                    completed.append(vol_values)
                elif volume_key == 'closing_balance':
                    closing_bal.append(vol_values)
                elif volume_key == 'non_workable_count':
                    nwc.append(vol_values)
        worktrack_volumes = OrderedDict()
        #worktrack_volumes = {}
        worktrack_volumes['Opening'] = [sum(i) for i in zip(*opening)]
        worktrack_volumes['Received'] = [sum(i) for i in zip(*received)]
        worktrack_volumes['Non Workable Count'] = [sum(i) for i in zip(*nwc)]
        worktrack_volumes['Completed'] = [sum(i) for i in zip(*completed)]
        worktrack_volumes['Closing balance'] = [sum(i) for i in zip(*closing_bal)]
        worktrack_timeline = OrderedDict()
        #worktrack_timeline = {}
        day_opening =[worktrack_volumes['Opening'], worktrack_volumes['Received']]
        worktrack_timeline['Opening'] = [sum(i) for i in zip(*day_opening)]
        worktrack_timeline['Completed'] = worktrack_volumes['Completed']
        final_volume_graph = {}
        final_volume_graph['bar_data']  = worktrack_volumes
        final_volume_graph['line_data'] = worktrack_timeline
        return final_volume_graph

        print result
    else:
        final_volume_graph ={}
        final_volume_graph['bar_data'] = {}
        final_volume_graph['line_data'] = {}
        return final_volume_graph

def volume_graph_data_week_month(date_list,prj_id,center_obj,level_structure_key):
    conn = redis.Redis(host="localhost", port=6379, db=0)
    result = {}
    volumes_dict = {}
    date_values = {}
    prj_name = Project.objects.filter(id=prj_id).values_list('name',flat=True)
    center_name = Center.objects.filter(id=center_obj).values_list('name', flat=True)
    query_set = query_set_generation(prj_id,center_obj,level_structure_key,date_list)
    volume_list = worktrack_internal_external_workpackets_list(level_structure_key,'Worktrack',query_set)
    for date_va in date_list:
        total_done_value = RawTable.objects.filter(project=prj_id, center=center_obj, date=date_va).aggregate(Max('per_day'))
        if total_done_value['per_day__max'] > 0:
            count =0
            for vol_type in volume_list:
                final_work_packet = level_hierarchy_key(level_structure_key,vol_type)
                if not final_work_packet:
                    final_work_packet = level_hierarchy_key(volume_list[count],vol_type)
                count = count+1
                date_pattern = '{0}_{1}_{2}_{3}_worktrack'.format(prj_name[0], str(center_name[0]), str(final_work_packet), date_va)
                key_list = conn.keys(pattern=date_pattern)
                if not key_list:
                    if date_values.has_key(final_work_packet):
                        date_values[final_work_packet]['opening'].append(0)
                        date_values[final_work_packet]['received'].append(0)
                        date_values[final_work_packet]['completed'].append(0)
                        date_values[final_work_packet]['non_workable_count'].append(0)
                        date_values[final_work_packet]['closing_balance'].append(0)
                    else:
                        date_values[final_work_packet] = {}
                        date_values[final_work_packet]['opening']= [0]
                        date_values[final_work_packet]['received']= [0]
                        date_values[final_work_packet]['completed'] = [0]
                        date_values[final_work_packet]['non_workable_count'] = [0]
                        date_values[final_work_packet]['closing_balance']= [0]
                for cur_key in key_list:
                    var = conn.hgetall(cur_key)
                    for key,value in var.iteritems():
                        if (value == 'None') or (value == ''):
                            value = 0
                        if not date_values.has_key(final_work_packet):
                            date_values[final_work_packet] = {}
                        if date_values.has_key(final_work_packet):
                            if date_values[final_work_packet].has_key(key):
                                date_values[final_work_packet][key].append(int(value))
                            else:
                                date_values[final_work_packet][key]=[int(value)]

                    volumes_dict['data'] = date_values
                    volumes_dict['date'] = date_list
                    result['data'] = volumes_dict
    if result.has_key('data'):
        opening,received,nwc,closing_bal,completed = [],[],[],[],[]
        for vol_key in result['data']['data'].keys():
            for volume_key,vol_values in result['data']['data'][vol_key].iteritems():
                if volume_key == 'opening':
                    opening.append(vol_values)
                elif volume_key == 'received':
                    received.append(vol_values)
                elif volume_key == 'completed':
                    completed.append(vol_values)
                elif volume_key == 'closing_balance':
                    closing_bal.append(vol_values)
                elif volume_key == 'non_workable_count':
                    nwc.append(vol_values)
        worktrack_volumes= {}
        worktrack_volumes['Received'] = [sum(i) for i in zip(*received)]
        worktrack_volumes['Opening'] = [sum(i) for i in zip(*opening)]
        worktrack_volumes['Non Workable Count'] = [sum(i) for i in zip(*nwc)]
        worktrack_volumes['Completed'] = [sum(i) for i in zip(*completed)]
        worktrack_volumes['Closing balance'] = [sum(i) for i in zip(*closing_bal)]
        worktrack_timeline = {}
        worktrack_timeline['Completed'] = worktrack_volumes['Completed']
        worktrack_timeline['Received'] = worktrack_volumes['Received']
        worktrack_timeline['Opening'] = worktrack_volumes['Opening']
        final_volume_graph = {}
        final_volume_graph['bar_data']  = worktrack_volumes
        final_volume_graph['line_data'] = worktrack_timeline
        #import pdb;pdb.set_trace()
        return final_volume_graph
        print result
    else:
        final_volume_graph ={}
        final_volume_graph['bar_data'] = {}
        final_volume_graph['line_data'] = {}
        return final_volume_graph        

def volumes_graphs_data_table(date_list,prj_id,center,level_structure_key):
    conn = redis.Redis(host="localhost", port=6379, db=0)
    result = {}
    volumes_dict = {}
    date_values = {}
    prj_name = Project.objects.filter(id=prj_id).values_list('name',flat=True)
    center_name = Center.objects.filter(id=center).values_list('name', flat=True)
    query_set = query_set_generation(prj_id,center,level_structure_key,date_list)
    volume_list = worktrack_internal_external_workpackets_list(level_structure_key,'Worktrack',query_set)
    for date_va in date_list:
        total_done_value = RawTable.objects.filter(project=prj_id, center=center, date=date_va).aggregate(Max('per_day'))
        if total_done_value['per_day__max'] > 0:
            count =0
            for vol_type in volume_list:
                final_work_packet = level_hierarchy_key(level_structure_key,vol_type)
                if not final_work_packet:
                    final_work_packet = level_hierarchy_key(volume_list[count],vol_type)
                count = count+1
                date_pattern = '{0}_{1}_{2}_{3}_worktrack'.format(prj_name[0], str(center_name[0]), str(final_work_packet), date_va)
                key_list = conn.keys(pattern=date_pattern)
                if not key_list:
                    if date_values.has_key(final_work_packet):
                        date_values[final_work_packet]['opening'].append(0)
                        date_values[final_work_packet]['received'].append(0)
                        date_values[final_work_packet]['completed'].append(0)
                        date_values[final_work_packet]['non_workable_count'].append(0)
                        date_values[final_work_packet]['closing_balance'].append(0)
                    else:
                        date_values[final_work_packet] = {}
                        date_values[final_work_packet]['opening']= [0]
                        date_values[final_work_packet]['received']= [0]
                        date_values[final_work_packet]['completed'] = [0]
                        date_values[final_work_packet]['non_workable_count'] = [0]
                        date_values[final_work_packet]['closing_balance']= [0]
                for cur_key in key_list:
                    var = conn.hgetall(cur_key)
                    for key,value in var.iteritems():
                        if (value == 'None') or (value == ''):
                            value = 0
                        if not date_values.has_key(final_work_packet):
                            date_values[final_work_packet] = {}
                        if date_values.has_key(final_work_packet):
                            if date_values[final_work_packet].has_key(key):
                                date_values[final_work_packet][key].append(int(value))
                            else:
                                date_values[final_work_packet][key]=[int(value)]

                    volumes_dict['data'] = date_values
                    volumes_dict['date'] = date_list
                    result['data'] = volumes_dict
    if result.has_key('data'):
        opening,received,nwc,closing_bal,completed = [],[],[],[],[]
        for vol_key in result['data']['data'].keys():
            for volume_key,vol_values in result['data']['data'][vol_key].iteritems():
                if volume_key == 'opening':
                    opening.append(vol_values)
                elif volume_key == 'received':
                    received.append(vol_values)
                elif volume_key == 'completed':
                    completed.append(vol_values)
                elif volume_key == 'closing_balance':
                    closing_bal.append(vol_values)
                elif volume_key == 'non_workable_count':
                    nwc.append(vol_values)

        worktrack_volumes= {}

        worktrack_volumes['opening'] = [sum(i) for i in zip(*opening)]
        worktrack_volumes['received'] = [sum(i) for i in zip(*received)]
        worktrack_volumes['non_workable_count'] = [sum(i) for i in zip(*nwc)]
        worktrack_volumes['completed'] = [sum(i) for i in zip(*completed)]
        worktrack_volumes['closing_balance'] = [sum(i) for i in zip(*closing_bal)]
        worktrack_timeline = {}
        day_opening =[worktrack_volumes['opening'], worktrack_volumes['received']]
        worktrack_timeline['day opening'] = [sum(i) for i in zip(*day_opening)]
        worktrack_timeline['day completed'] = worktrack_volumes['completed']
        final_volume_graph = {}
        final_volume_graph['bar_data']  = worktrack_volumes
        volume_status_table = {}
        volume_status_final_table = {}
        volume_status_final_table['volume_data'] = []
        new_dates = []
        status_count = 0
        for date_va in date_list:
            total_done_value = RawTable.objects.filter(project=prj_id, center=center, date=date_va).aggregate(Max('per_day'))
            print total_done_value['per_day__max']
            if total_done_value['per_day__max'] > 0:
                volume_status_table[date_va] = {}
                volume_status_table[date_va]['opening'] = worktrack_volumes['opening'][status_count]
                volume_status_table[date_va]['completed'] = worktrack_volumes['completed'][status_count]
                volume_status_table[date_va]['received'] = worktrack_volumes['received'][status_count]
                volume_status_table[date_va]['closing_balance'] = worktrack_volumes['closing_balance'][status_count]
                volume_status_table[date_va]['non_workable_count'] = worktrack_volumes['non_workable_count'][status_count]
                volume_status_table[date_va]['date'] = date_va
                status_count = status_count +1
                new_dates.append(volume_status_table[date_va])
        return new_dates
    else:
        final_volume_graph ={}
        volume_status_table = {}
        final_volume_graph['bar_data'] = {}
        return volume_status_table



def accuracy_query_generations(pro_id,cen_id,date,main_work_packet):
    accuracy_query_set = {}
    accuracy_query_set['project'] = pro_id
    accuracy_query_set['center'] = cen_id
    if isinstance(date, list):
        accuracy_query_set['date__range']=[date[0], date[-1]]
    else:
        accuracy_query_set['date'] = date
    if '_' in main_work_packet:
        packets_list = main_work_packet.split('_')
        accuracy_query_set['work_packet'] = packets_list[0]
        accuracy_query_set['sub_packet'] = packets_list[1]
    else:
        accuracy_query_set['work_packet'] = main_work_packet

    return accuracy_query_set



def internal_bar_data(pro_id, cen_id, from_, to_, main_work_packet, chart_type,project):
    if (project == "Probe" and chart_type == 'External Accuracy') or (project == 'Ujjivan' and chart_type in ['External Accuracy','Internal Accuracy']) or (project == "IBM" and chart_type == 'External Accuracy'):
        date_range = num_of_days(to_, from_)
        final_internal_bar_drilldown = {} 
        final_internal_bar_drilldown['type'] = chart_type
        final_internal_bar_drilldown['project'] = project
        list_data = []
        table_headers = []
        for date in date_range:
            accuracy_query_set = accuracy_query_generations(pro_id,cen_id,date,main_work_packet)
            if chart_type == 'External Accuracy':
                list_of = Externalerrors.objects.filter(**accuracy_query_set).values_list('employee_id','date','work_packet','total_errors','sub_packet')
            elif project == 'Ujjivan' and chart_type == 'Internal Accuracy':
                list_of = Internalerrors.objects.filter(**accuracy_query_set).values_list('employee_id', 'date','work_packet','total_errors','sub_packet')
            for i in list_of:
                per_day_value = RawTable.objects.filter(employee_id=i[0],date=i[1],work_packet=i[2]).values_list('per_day')
                try: 
                    per_day_value = per_day_value[0][0]
                except:
                    per_day_value = 0
                if per_day_value > 0:
                    #list_data.append({'name':i[0], 'date':str(i[1]), 'work_packet':i[2],'total_errors':i[3], 'productivity': per_day_value})
                    list_data.append({'date':str(i[1]), 'total_errors':i[3], 'productivity': per_day_value})
                    Productivity_value = 0
                    Error_count = 0
                for ans in list_data:
                    if ans['productivity']:
                        Productivity_value = Productivity_value + ans['productivity']
                    if ans['total_errors']:
                        Error_count = Error_count + ans['total_errors']
                    if ans['productivity'] > 0:
                        accuracy = 100 - ((float(ans['total_errors']) / float(ans['productivity']))) * 100
                        accuracy_agg = float('%.2f' % round(accuracy, 2))
                        ans['accuracy'] = accuracy_agg
            if len(list_data)>0:
                table_headers = ['date','productivity','total_errors']
        final_internal_bar_drilldown['data'] = list_data
        final_internal_bar_drilldown['table_headers'] = table_headers
        final_internal_bar_drilldown['Productivity_value'] = Productivity_value
        final_internal_bar_drilldown['Error_count'] = Error_count
        return final_internal_bar_drilldown
    '''if project == "Ujjivan" and chart_type == 'External Accuracy':
        date_range = num_of_days(to_, from_)
        final_internal_bar_drilldown = {}
        final_internal_bar_drilldown['type'] = chart_type
        final_internal_bar_drilldown['project'] = project
        list_data = []
        table_headers = []
        for date in date_range:
            list_of = Externalerrors.objects.filter(project=pro_id, center=cen_id, date=date, work_packet=main_work_packet).values_list('employee_id','date','work_packet','total_errors')
            for i in list_of:
                per_day_value = RawTable.objects.filter(employee_id=i[0],date=i[1],work_packet=i[2]).values_list('per_day')
                try:
                    per_day_value = per_day_value[0][0]
                except:
                    per_day_value = 0
                if per_day_value > 0:
                    list_data.append({'name':i[0], 'date':str(i[1]), 'work_packet':i[2],'total_errors':i[3], 'productivity': per_day_value})
                for ans in list_data:
                    if ans['productivity'] > 0:
                        accuracy = 100 - ((float(ans['total_errors']) / float(ans['productivity']))) * 100
                        accuracy_agg = float('%.2f' % round(accuracy, 2))
                        ans['accuracy'] = accuracy_agg
            if len(list_data)>0:
                table_headers = ['date','name', 'productivity', 'total_errors', 'accuracy']
        final_internal_bar_drilldown['data'] = list_data
        final_internal_bar_drilldown['table_headers'] = table_headers
        return final_internal_bar_drilldown'''

    date_range = num_of_days(to_,from_)
    final_internal_bar_drilldown = {} 
    final_internal_bar_drilldown['type'] = chart_type
    final_internal_bar_drilldown['project'] = project
    internal_bar_list = []
    table_headers = []
    list_of = []

    for date in date_range:
        if chart_type == 'Internal Accuracy' or chart_type == 'Internal_Bar_Pie':
            packets_list = main_work_packet.split('_')
            packets_list_type = ''
            if len(packets_list) == 2:
                sub_project_statuts = Internalerrors.objects.filter(center=cen_id, project=pro_id,date=date).values_list('sub_project',flat=True)
                sub_project_statuts = filter(None, sub_project_statuts)
                if len(sub_project_statuts) > 0:
                    sub_project, work_packet = main_work_packet.split('_')
                    list_of = Internalerrors.objects.filter(project=pro_id, center=cen_id, date=date,sub_project=sub_project,work_packet=work_packet).values_list('employee_id', 'date', 'work_packet', 'audited_errors', 'total_errors')
                work_packet_statuts = Internalerrors.objects.filter(center=cen_id, project=pro_id,date=date).values_list('work_packet', flat=True)
                work_packet_statuts = filter(None, work_packet_statuts)
                if len(sub_project_statuts) == 0 and len(work_packet_statuts)>0:
                    work_packet, sub_packet = main_work_packet.split('_')
                    is_work_pac_exist = Internalerrors.objects.filter(center=cen_id, project=pro_id, date=date).values_list('work_packet', 'sub_packet').distinct()
                    if len(is_work_pac_exist) > 1:
                        list_of = Internalerrors.objects.filter(center=cen_id, project=pro_id, date=date,work_packet=work_packet).values_list('employee_id', 'date', 'work_packet', 'audited_errors', 'total_errors')
                    else:
                        list_of = Internalerrors.objects.filter(center=cen_id, project=pro_id, date=date,work_packet=work_packet).values_list('employee_id', 'date', 'work_packet', 'audited_errors', 'total_errors')
            elif len(packets_list) == 3:
                if '_' in work_packet:
                    sub_project, work_packet, sub_packet = main_work_packet.split('_')
                    list_of = Internalerrors.objects.filter(center=cen_id, project=pro_id, date=date,work_packet=work_packet,sub_packet=sub_packet).values_list('employee_id', 'date', 'work_packet', 'audited_errors', 'total_errors')
                else:
                    is_work_pac_exist = Internalerrors.objects.filter(center=cen_id, project=pro_id, date=date).values_list('work_packet', 'sub_packet').distinct()
                    if len(is_work_pac_exist) > 1:
                        list_of = Internalerrors.objects.filter(center=cen_id, project=pro_id, date=date,work_packet=work_packet).values_list('employee_id', 'date', 'work_packet', 'audited_errors', 'total_errors')
                    else:
                        list_of = Internalerrors.objects.filter(center=cen_id, project=pro_id, date=date,work_packet=work_packet).values_list('employee_id', 'date', 'work_packet', 'audited_errors', 'total_errors')
            else:
                sub_project_statuts = Internalerrors.objects.filter(center=cen_id, project=pro_id,date=date).values_list('sub_project',flat=True)
                sub_project_statuts = filter(None, sub_project_statuts)
                if len(sub_project_statuts) > 0:
                    packets_list_type = 'sub_project'
                    is_work_pac_exist = Internalerrors.objects.filter(center=cen_id, project=pro_id, date=date).values_list('sub_project', 'work_packet', 'sub_packet').distinct()
                    if len(is_work_pac_exist) > 1:
                        # detail_list = RawTable.objects.filter(center=cen_id,project=pro_id,date=to_date[0],work_packet=work_packet).values_list('employee_id','per_day','sub_packet','date')
                        list_of = Internalerrors.objects.filter(center=cen_id, project=pro_id, date=date,sub_project=packets_list[0]).values_list('employee_id', 'date', 'work_packet', 'audited_errors', 'total_errors')
                    else:
                        list_of = Internalerrors.objects.filter(center=cen_id, project=pro_id, date=date,sub_project=packets_list[0]).values_list('employee_id', 'date', 'work_packet', 'audited_errors', 'total_errors')
                else:
                    packets_list_type = 'work_packet'
                    #import pdb;pdb.set_trace()
                    is_work_pac_exist = Internalerrors.objects.filter(center=cen_id, project=pro_id, date=date).values_list('work_packet', 'sub_packet').distinct()
                    if len(is_work_pac_exist) > 1:
                        list_of = Internalerrors.objects.filter(center=cen_id, project=pro_id, date=date,work_packet=packets_list[0]).values_list('employee_id', 'date', 'work_packet', 'audited_errors', 'total_errors')
                    else:
                        list_of = Internalerrors.objects.filter(center=cen_id, project=pro_id, date=date,work_packet=packets_list[0]).values_list('employee_id', 'date', 'work_packet', 'audited_errors', 'total_errors')
                        # list_of_internal = Internalerrors.objects.filter(project=pro_id,center=cen_id,date=to_date[0],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors')

        else:
            packets_list = main_work_packet.split('_')
            packets_list_type = ''
            list_of =[]
            if len(packets_list) == 2:
                sub_project_statuts = Externalerrors.objects.filter(center=cen_id, project=pro_id,date=date).values_list('sub_project', flat=True)
                sub_project_statuts = filter(None, sub_project_statuts)
                sub_project, work_packet = main_work_packet.split('_')
                if len(sub_project_statuts) > 0:
                    list_of = Externalerrors.objects.filter(project=pro_id, center=cen_id, date=date,sub_project=sub_project,work_packet=work_packet).values_list('employee_id', 'date','work_packet','audited_errors','total_errors')
                work_packet_statuts = Externalerrors.objects.filter(center=cen_id, project=pro_id,date=date).values_list('work_packet', flat=True)
                work_packet_statuts = filter(None, work_packet_statuts)
                if len(sub_project_statuts) == 0 and len(work_packet_statuts) > 0:
                    work_packet, sub_packet = main_work_packet.split('_')
                    is_work_pac_exist = Externalerrors.objects.filter(center=cen_id, project=pro_id,date=date).values_list('work_packet','sub_packet').distinct()
                    if len(is_work_pac_exist) > 1:
                        list_of = Externalerrors.objects.filter(center=cen_id, project=pro_id, date=date,work_packet=work_packet).values_list('employee_id','date','sub_packet','audited_errors','total_errors')

            elif len(packets_list) == 3:
                if '_' in work_packet:
                    sub_project, work_packet, sub_packet = main_work_packet.split('_')
                    list_of = Externalerrors.objects.filter(center=cen_id, project=pro_id, date=date,work_packet=work_packet, sub_packet=sub_packet).values_list('employee_id', 'date', 'work_packet', 'audited_errors', 'total_errors')
                else:
                    is_work_pac_exist = Externalerrors.objects.filter(center=cen_id, project=pro_id,date=date).values_list('work_packet','sub_packet').distinct()
                    if len(is_work_pac_exist) > 1:
                        list_of = Externalerrors.objects.filter(center=cen_id, project=pro_id, date=date,work_packet=work_packet).values_list('employee_id','date','work_packet','audited_errors','total_errors')
                    else:
                        list_of = Externalerrors.objects.filter(center=cen_id, project=pro_id, date=date,work_packet=work_packet).values_list('employee_id','date','work_packet','audited_errors','total_errors')
            else:
                sub_project_statuts = Externalerrors.objects.filter(center=cen_id, project=pro_id,date=date).values_list('sub_project', flat=True)
                sub_project_statuts = filter(None, sub_project_statuts)

                if len(sub_project_statuts) > 0:
                    packets_list_type = 'sub_project'
                    is_work_pac_exist = Externalerrors.objects.filter(center=cen_id, project=pro_id,date=date).values_list('sub_project','work_packet','sub_packet').distinct()
                    if len(is_work_pac_exist) > 1:
                        list_of = Externalerrors.objects.filter(center=cen_id, project=pro_id, date=date,sub_project=packets_list[0]).values_list('employee_id','date','work_packet','audited_errors','total_errors')
                    else:
                        list_of = Externalerrors.objects.filter(center=cen_id, project=pro_id, date=date,sub_project=packets_list[0]).values_list('employee_id','date','work_packet','audited_errors','total_errors')
                else:
                    packets_list_type = 'work_packet'
                    is_work_pac_exist = Externalerrors.objects.filter(center=cen_id, project=pro_id,date=date).values_list('work_packet','sub_packet').distinct()
                    if len(is_work_pac_exist) > 1:
                        list_of = Externalerrors.objects.filter(center=cen_id, project=pro_id, date=date,work_packet=packets_list[0]).values_list('employee_id','date','work_packet','audited_errors','total_errors')
                    else:
                        list_of = Externalerrors.objects.filter(center=cen_id, project=pro_id, date=date,work_packet=packets_list[0]).values_list('employee_id','date','work_packet','audited_errors','total_errors')
        for i in list_of:
            #internal_bar_list.append({'name':i[0], 'date':str(i[1]), 'audited_count':i[3], 'total_errors':i[4]})
            internal_bar_list.append({'date':str(i[1]), 'audited_count':i[3], 'total_errors':i[4]})
            audited_value = 0
            Error_count = 0
            for ans in internal_bar_list:
                if ans['audited_count']:
                    audited_value = audited_value + ans['audited_count']
                if ans['total_errors']:
                    Error_count = Error_count + ans['total_errors']
                if ans['total_errors'] >0 and ans['audited_count']>0:
                    accuracy = 100 - ((float(ans['total_errors']) / float(ans['audited_count']))) * 100
                    accuracy_agg = float('%.2f' % round(accuracy, 2))
                    ans['accuracy'] = accuracy_agg
                elif ans['total_errors']==0 and ans['audited_count']==0:
                    ans['accuracy'] = 0
                else:
                    ans['accuracy'] = 100
    if len(internal_bar_list) > 0:
        #table_headers = ['date','name','audited_count', 'total_errors', 'accuracy']
        table_headers = ['date','audited_count', 'total_errors']
    final_internal_bar_drilldown['data'] = internal_bar_list
    final_internal_bar_drilldown['project'] = project
    final_internal_bar_drilldown['table_headers'] = table_headers
    final_internal_bar_drilldown['audited_value'] = audited_value
    final_internal_bar_drilldown['Error_count'] = Error_count
    return final_internal_bar_drilldown


def internal_chart_data_multi(pro_id,cen_id,to_date,work_packet,chart_type,project):
    if (project == 'Probe' and chart_type == 'External Accuracy Trends') or (project == 'Ujjivan' and chart_type == 'External Accuracy Trends') or (project == 'IBM' and chart_type == 'External Accuracy Trends'):
        final_internal_drilldown = {}
        final_internal_drilldown['type'] = chart_type
        final_internal_drilldown['project'] = project
        #list_of_internal = Externalerrors.objects.filter(project=pro_id,center=cen_id,date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','work_packet','total_errors','date')
        accuracy_query_set = accuracy_query_generations(pro_id, cen_id, to_date, work_packet)
        if project == 'Ujjivan' and chart_type == 'Internal Accuracy Trends':
            #list_of_internal = Internalerrors.objects.filter(project=pro_id,center=cen_id,date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','work_packet','total_errors','date')
            list_of_internal = Internalerrors.objects.filter(**accuracy_query_set).values_list('employee_id','work_packet','total_errors','date')
        elif chart_type == 'External Accuracy Trends':
            list_of_internal = Externalerrors.objects.filter(**accuracy_query_set).values_list('employee_id','work_packet','total_errors','date')

        list_ext_data = []
        for i in list_of_internal:
            per_day_value = RawTable.objects.filter(employee_id=i[0],date=i[3],work_packet=i[1]).values_list('per_day')
            try:
                per_day_value = per_day_value[0][0]
            except:
                per_day_value = 0
            if per_day_value > 0:
                #list_ext_data.append({'name': i[0],'date':str(i[3]),'work_packet': i[1],'total_errors': i[2],'productivity': per_day_value})
                list_ext_data.append({'date':str(i[3]),'total_errors': i[2],'productivity': per_day_value  })
            Productivity_value = 0
            Error_count = 0
            for ans in list_ext_data:
                if ans['total_errors']:
                    Error_count = Error_count + ans['total_errors']
                if ans['productivity']:
                    Productivity_value = Productivity_value + ans['productivity']
                accuracy = 100 - ((float(ans['total_errors']) / float(ans['productivity']))) * 100
                accuracy_agg = float('%.2f' % round(accuracy, 2))
                ans['accuracy'] = accuracy_agg
        if len(list_ext_data) > 0:
                table_headers = ['date','productivity','total_errors']
        final_internal_drilldown['data'] = list_ext_data
        final_internal_drilldown['table_headers'] = table_headers
        final_internal_drilldown['Productivity_value'] = Productivity_value
        final_internal_drilldown['Error_count'] = Error_count
        return final_internal_drilldown

    '''if project == 'Ujjivan' and chart_type == 'External Accuracy Trends':
        final_internal_drilldown = {}
        final_internal_drilldown['type'] = chart_type
        final_internal_drilldown['project'] = project
        list_of_internal = Externalerrors.objects.filter(project=pro_id,center=cen_id,date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','work_packet','total_errors','date')
        list_ext_data = []
        for i in list_of_internal:
            per_day_value = RawTable.objects.filter(employee_id=i[0],date=i[3],work_packet=i[1]).values_list('per_day')
            try:
                per_day_value = per_day_value[0][0]
            except:
                per_day_value = 0
            if per_day_value > 0:
                list_ext_data.append({'name': i[0],'date':str(i[3]),'work_packet': i[1],'total_errors': i[2],'productivity': per_day_value})
            for ans in list_ext_data:
                accuracy = 100 - ((float(ans['total_errors']) / float(ans['productivity']))) * 100
                accuracy_agg = float('%.2f' % round(accuracy, 2))
                ans['accuracy'] = accuracy_agg
        if len(list_ext_data) > 0:
                table_headers = ['date','name','productivity','total_errors', 'accuracy']
        final_internal_drilldown['data'] = list_ext_data
        final_internal_drilldown['table_headers'] = table_headers
        return final_internal_drilldown'''

    if project == 'Ujjivan' and chart_type == 'Internal Accuracy Trends':
        final_internal_drilldown = {}
        final_internal_drilldown['type'] = chart_type
        final_internal_drilldown['project'] = project
        list_of_internal = Internalerrors.objects.filter(project=pro_id,center=cen_id,date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','work_packet','total_errors','date')
        list_ext_data = []
        for i in list_of_internal:
            per_day_value = RawTable.objects.filter(employee_id=i[0],date=i[3],work_packet=i[1]).values_list('per_day')
            try:
                per_day_value = per_day_value[0][0]
            except:
                per_day_value = 0
            if per_day_value > 0:
                #list_ext_data.append({'name': i[0],'date':str(i[3]),'work_packet': i[1],'total_errors': i[2],'productivity': per_day_value})
                list_ext_data.append({'date':str(i[3]),'total_errors': i[2],'productivity': per_day_value})
            Productivity_value = 0
            Error_count = 0 
            for ans in list_ext_data:
                if ans['productivity']:
                    Productivity_value = Productivity_value + ans['productivity']
                if ans['total_errors']:
                    Error_count = Error_count + ans['total_errors'] 
                accuracy = 100 - ((float(ans['total_errors']) / float(ans['productivity']))) * 100
                accuracy_agg = float('%.2f' % round(accuracy, 2))
                ans['accuracy'] = accuracy_agg
        if len(list_ext_data) > 0:
                table_headers = ['date','productivity','total_errors']
        final_internal_drilldown['data'] = list_ext_data
        final_internal_drilldown['table_headers'] = table_headers
        final_internal_drilldown['Productivity_value'] = Productivity_value
        final_internal_drilldown['Error_count'] = Error_count
        return final_internal_drilldown

    elif chart_type == 'Internal Accuracy Trends':
        packets_list = work_packet.split('_')
        packets_list_type = ''
        if len(packets_list) == 2:
            sub_project_statuts = Internalerrors.objects.filter(center=cen_id, project=pro_id,date__range=[to_date[0], to_date[-1]]).values_list('sub_project', flat=True)
            sub_project_statuts = filter(None, sub_project_statuts)
            if len(sub_project_statuts) > 0:
                sub_project, work_packet = work_packet.split('_')
                list_of_internal = Internalerrors.objects.filter(project=pro_id, center=cen_id, date__range=[to_date[0], to_date[-1]],sub_project=sub_project,work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
            work_packet_statuts = Internalerrors.objects.filter(center=cen_id, project=pro_id,date__range=[to_date[0], to_date[-1]]).values_list('work_packet',flat=True)
            work_packet_statuts = filter(None, work_packet_statuts)
            if len(sub_project_statuts) == 0 and len(work_packet_statuts) > 0:
                work_packet, sub_packet = work_packet.split('_')
                is_work_pac_exist = Internalerrors.objects.filter(center=cen_id, project=pro_id, date__range=[to_date[0], to_date[-1]]).values_list('work_packet','sub_packet').distinct()[0]
                if len(is_work_pac_exist) > 1:
                    list_of_internal = Internalerrors.objects.filter(center=cen_id, project=pro_id, date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
                else:
                    list_of_internal = Internalerrors.objects.filter(center=cen_id, project=pro_id, date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
        elif len(packets_list) == 3:
            if '_' in work_packet:
                sub_project, work_packet, sub_packet = work_packet.split('_')
                list_of_internal = Internalerrors.objects.filter(center=cen_id, project=pro_id, date__range=[to_date[0], to_date[-1]],work_packet=work_packet,sub_packet=sub_packet).values_list('employee_id','audited_errors','total_errors','date')
            else:
                is_work_pac_exist = Internalerrors.objects.filter(center=cen_id, project=pro_id, date__range=[to_date[0], to_date[-1]]).values_list('work_packet','sub_packet').distinct()[0]
                if len(is_work_pac_exist) > 1:
                    list_of_internal = Internalerrors.objects.filter(center=cen_id, project=pro_id, date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
                else:
                    list_of_internal = Internalerrors.objects.filter(center=cen_id, project=pro_id, date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
        else:
            sub_project_statuts = Internalerrors.objects.filter(center=cen_id, project=pro_id,date__range=[to_date[0], to_date[-1]]).values_list('sub_project', flat=True)
            sub_project_statuts = filter(None, sub_project_statuts)
            if len(sub_project_statuts) > 0:
                packets_list_type = 'sub_project'
                is_work_pac_exist = Internalerrors.objects.filter(center=cen_id, project=pro_id, date__range=[to_date[0], to_date[-1]]).values_list('sub_project','work_packet','sub_packet').distinct()[0]
                if len(is_work_pac_exist) > 1:
                    # detail_list = RawTable.objects.filter(center=cen_id,project=pro_id,date=to_date[0],work_packet=work_packet).values_list('employee_id','per_day','sub_packet','date')
                    list_of_internal = Internalerrors.objects.filter(center=cen_id, project=pro_id, date__range=[to_date[0], to_date[-1]],sub_project=packets_list[0]).values_list('employee_id', 'audited_errors', 'total_errors','date')
                else:
                    list_of_internal = Internalerrors.objects.filter(center=cen_id, project=pro_id, date__range=[to_date[0], to_date[-1]],sub_project=packets_list[0]).values_list('employee_id', 'audited_errors', 'total_errors','date')
            else:
                packets_list_type = 'work_packet'
                is_work_pac_exist = Internalerrors.objects.filter(center=cen_id, project=pro_id, date__range=[to_date[0], to_date[-1]]).values_list('work_packet','sub_packet').distinct()[0]
                if len(is_work_pac_exist) > 1:
                    list_of_internal = Internalerrors.objects.filter(center=cen_id, project=pro_id, date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
                else:
                    list_of_internal = Internalerrors.objects.filter(center=cen_id, project=pro_id, date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
        #list_of_internal = Internalerrors.objects.filter(project=pro_id,center=cen_id,date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
    else:
        packets_list = work_packet.split('_')
        packets_list_type = ''
        if len(packets_list) == 2:
            sub_project_statuts = Externalerrors.objects.filter(center=cen_id, project=pro_id,date__range=[to_date[0], to_date[-1]]).values_list('sub_project', flat=True)
            sub_project_statuts = filter(None, sub_project_statuts)
            if len(sub_project_statuts) > 0:
                sub_project, work_packet = work_packet.split('_')
                list_of_internal = Externalerrors.objects.filter(project=pro_id, center=cen_id,date__range=[to_date[0], to_date[-1]],sub_project=sub_project,work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
            work_packet_statuts = Externalerrors.objects.filter(center=cen_id, project=pro_id,date__range=[to_date[0], to_date[-1]]).values_list('work_packet',flat=True)
            work_packet_statuts = filter(None, work_packet_statuts)
            if len(sub_project_statuts) == 0 and len(work_packet_statuts) > 0:
                work_packet, sub_packet = work_packet.split('_')
                is_work_pac_exist = Externalerrors.objects.filter(center=cen_id, project=pro_id,date__range=[to_date[0], to_date[-1]]).values_list('work_packet', 'sub_packet').distinct()[0]
                if len(is_work_pac_exist) > 1:
                    list_of_internal = Externalerrors.objects.filter(center=cen_id, project=pro_id,date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
                else:
                    list_of_internal = Externalerrors.objects.filter(center=cen_id, project=pro_id,date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
        elif len(packets_list) == 3:
            if '_' in work_packet:
                sub_project, work_packet, sub_packet = work_packet.split('_')
                list_of_internal = Externalerrors.objects.filter(center=cen_id, project=pro_id,date__range=[to_date[0], to_date[-1]],work_packet=work_packet,sub_packet=sub_packet).values_list('employee_id','audited_errors','total_errors','date')
            else:
                is_work_pac_exist = Externalerrors.objects.filter(center=cen_id, project=pro_id,date__range=[to_date[0], to_date[-1]]).values_list('work_packet', 'sub_packet').distinct()[0]
                if len(is_work_pac_exist) > 1:
                    list_of_internal = Externalerrors.objects.filter(center=cen_id, project=pro_id,date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
                else:
                    list_of_internal = Externalerrors.objects.filter(center=cen_id, project=pro_id,date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
        else:
            sub_project_statuts = Externalerrors.objects.filter(center=cen_id, project=pro_id,date__range=[to_date[0], to_date[-1]]).values_list('sub_project', flat=True)
            sub_project_statuts = filter(None, sub_project_statuts)
            if len(sub_project_statuts) > 0:
                packets_list_type = 'sub_project'
                is_work_pac_exist = Externalerrors.objects.filter(center=cen_id, project=pro_id,date__range=[to_date[0], to_date[-1]]).values_list('sub_project', 'work_packet', 'sub_packet').distinct()[0]
                if len(is_work_pac_exist) > 1:
                    list_of_internal = Externalerrors.objects.filter(center=cen_id, project=pro_id,date__range=[to_date[0], to_date[-1]],sub_project=packets_list[0]).values_list('employee_id', 'audited_errors', 'total_errors', 'date')
                else:
                    list_of_internal = Externalerrors.objects.filter(center=cen_id, project=pro_id,date__range=[to_date[0], to_date[-1]],sub_project=packets_list[0]).values_list('employee_id', 'audited_errors', 'total_errors', 'date')
            else:
                packets_list_type = 'work_packet'
                is_work_pac_exist = Externalerrors.objects.filter(center=cen_id, project=pro_id,date__range=[to_date[0], to_date[-1]]).values_list('work_packet', 'sub_packet').distinct()[0]
                if len(is_work_pac_exist) > 1:
                    list_of_internal = Externalerrors.objects.filter(center=cen_id, project=pro_id,date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
                else:
                    list_of_internal = Externalerrors.objects.filter(center=cen_id, project=pro_id,date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
    internal_list = []
    table_headers = []
    final_internal_drilldown = {}
    final_internal_drilldown['type'] = chart_type

    for i in list_of_internal:
        #internal_list.append({'name':i[0],'audited_count':i[1], 'total_errors':i[2],'date':str(i[3])})
        internal_list.append({'audited_count':i[1], 'total_errors':i[2],'date':str(i[3])})
        audited_value = 0
        Error_count = 0 
        for ans in internal_list:
            if ans['audited_count']:
                audited_value = audited_value + ans['audited_count']
            if ans['total_errors']:
                Error_count = Error_count + ans['total_errors']
            if ans['audited_count'] > 0:
                accuracy = 100 - ((float(ans['total_errors']) / float(ans['audited_count']))) * 100
            else:
                accuracy = 0
            accuracy_agg = float('%.2f' % round(accuracy, 2))
            ans['accuracy'] = accuracy_agg
    if len(internal_list) > 0:
            table_headers = ['date','audited_count','total_errors']

    final_internal_drilldown['data'] = internal_list
    final_internal_drilldown['table_headers'] = table_headers
    final_internal_drilldown['audited_value'] = audited_value
    final_internal_drilldown['Error_count'] = Error_count
    return final_internal_drilldown


def internal_chart_data(pro_id,cen_id,to_date,work_packet,chart_type,project):
    if (project == 'Probe' and chart_type == 'External Accuracy Trends') or (project == "Ujjivan" and chart_type in ['External Accuracy Trends','Internal Accuracy Trends']) or (project == 'IBM' and chart_type == 'External Accuracy Trends'):
        if len(to_date) == 2:
            final_internal_drilldown = {}
            final_val_res = internal_chart_data_multi(pro_id,cen_id,to_date,work_packet,chart_type,project)
            final_internal_drilldown['type'] = chart_type
            final_internal_drilldown['project'] = project
            final_internal_drilldown['data'] = final_val_res['data']
            final_internal_drilldown['table_headers'] = final_val_res['table_headers']
            return final_internal_drilldown
        else:
            #import pdb;pdb.set_trace()
            packets_list = work_packet.split('_')
            packets_list_type = ''
            accuracy_query_set = accuracy_query_generations(pro_id, cen_id, to_date[0], work_packet)
            if project == 'Ujjivan' and chart_type == 'Internal Accuracy Trends':
                list_of_internal = Internalerrors.objects.filter(**accuracy_query_set).values_list('employee_id','work_packet','total_errors','date','sub_packet')
            elif chart_type == 'External Accuracy Trends':
                list_of_internal = Externalerrors.objects.filter(**accuracy_query_set).values_list('employee_id','work_packet','total_errors','date','sub_packet')
            final_internal_drilldown = {}
            final_internal_drilldown['type'] = chart_type
            final_internal_drilldown['project'] = project
            list_ext_data = []
            table_headers = []
            #import pdb;pdb.set_trace()
            for i in list_of_internal:
                per_day_value = RawTable.objects.filter(employee_id=i[0],date=i[3],work_packet=i[1],sub_packet=i[4]).values_list('per_day')
                try:
                    per_day_value = per_day_value[0][0]
                except:
                    per_day_value = 0
                if per_day_value > 0:
                    #list_ext_data.append({'name': i[0],'date':str(i[3]),'work_packet': i[1],'total_errors': i[2],'productivity': per_day_value})
                    list_ext_data.append({'date':str(i[3]),'total_errors': i[2],'productivity': per_day_value})
                Productivity_value = 0
                Error_count = 0
                for ans in list_ext_data:
                    if ans['total_errors']:
                        Error_count = Error_count + ans['total_errors']
                    if ans['productivity']:
                        Productivity_value = Productivity_value + ans['productivity']
                    accuracy = 100 - ((float(ans['total_errors']) / float(ans['productivity']))) * 100
                    accuracy_agg = float('%.2f' % round(accuracy, 2))
                    ans['accuracy'] = accuracy_agg
                if len(list_ext_data) >0:
                    table_headers = ['date', 'productivity', 'total_errors']
            final_internal_drilldown['data'] = list_ext_data
            final_internal_drilldown['table_headers'] = table_headers
            final_internal_drilldown['Productivity_value'] = Productivity_value
            final_internal_drilldown['Error_count'] = Error_count
            return final_internal_drilldown

    if chart_type == 'Internal Accuracy Trends':
        if len(to_date) == 2:
            final_internal_drilldown = {}
            final_val_res = internal_chart_data_multi(pro_id,cen_id,to_date,work_packet,chart_type,project)
            final_internal_drilldown['type'] = chart_type
            final_internal_drilldown['project'] = project
            final_internal_drilldown['data'] = final_val_res['data']
            final_internal_drilldown['table_headers'] = final_val_res['table_headers']
            return final_internal_drilldown
        else:
            packets_list = work_packet.split('_')
            packets_list_type = ''
            if len(packets_list) == 2:
                sub_project_statuts = Internalerrors.objects.filter(center=cen_id, project=pro_id,date=to_date[0]).values_list('sub_project', flat=True)
                sub_project_statuts = filter(None, sub_project_statuts)
                if len(sub_project_statuts) > 0:
                    sub_project, work_packet = work_packet.split('_')
                    list_of_internal = Internalerrors.objects.filter(project=pro_id, center=cen_id, date=to_date[0],sub_project=sub_project,work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
                work_packet_statuts = Internalerrors.objects.filter(center=cen_id, project=pro_id,date=to_date[0]).values_list('work_packet',flat=True)
                work_packet_statuts = filter(None, work_packet_statuts)
                if len(sub_project_statuts) == 0 and len(work_packet_statuts) > 0:
                    work_packet, sub_packet = work_packet.split('_')
                    is_work_pac_exist = Internalerrors.objects.filter(center=cen_id, project=pro_id, date=to_date[0]).values_list('work_packet','sub_packet').distinct()[0]
                    if len(is_work_pac_exist) > 1:
                        list_of_internal = Internalerrors.objects.filter(center=cen_id, project=pro_id, date=to_date[0],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
                    else:
                        list_of_internal = Internalerrors.objects.filter(center=cen_id, project=pro_id, date=to_date[0],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
            elif len(packets_list) == 3:
                if '_' in work_packet:
                    sub_project, work_packet, sub_packet = work_packet.split('_')
                    list_of_internal = Internalerrors.objects.filter(center=cen_id, project=pro_id, date=to_date[0],work_packet=work_packet, sub_packet=sub_packet).values_list('employee_id','audited_errors','total_errors','date')
                else:
                    is_work_pac_exist = Internalerrors.objects.filter(center=cen_id, project=pro_id, date=to_date[0]).values_list('work_packet','sub_packet').distinct()[0]
                    if len(is_work_pac_exist) > 1:
                        list_of_internal = Internalerrors.objects.filter(center=cen_id, project=pro_id, date=to_date[0],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
                    else:
                        list_of_internal = Internalerrors.objects.filter(center=cen_id, project=pro_id, date=to_date[0],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
            else:
                sub_project_statuts = Internalerrors.objects.filter(center=cen_id, project=pro_id,date=to_date[0]).values_list('sub_project', flat=True)
                sub_project_statuts = filter(None, sub_project_statuts)
                if len(sub_project_statuts) > 0:
                    packets_list_type = 'sub_project'
                    is_work_pac_exist = Internalerrors.objects.filter(center=cen_id, project=pro_id, date=to_date[0]).values_list('sub_project','work_packet','sub_packet').distinct()[0]
                    if len(is_work_pac_exist) > 1:
                        list_of_internal = Internalerrors.objects.filter(center=cen_id, project=pro_id, date=to_date[0],sub_project=packets_list[0]).values_list('employee_id','audited_errors','total_errors','date')
                    else:
                        list_of_internal = Internalerrors.objects.filter(center=cen_id, project=pro_id, date=to_date[0],sub_project=packets_list[0]).values_list('employee_id','audited_errors','total_errors','date')
                else:
                    packets_list_type = 'work_packet'
                    is_work_pac_exist = Internalerrors.objects.filter(center=cen_id, project=pro_id, date=to_date[0]).values_list('work_packet','sub_packet').distinct()[0]
                    if len(is_work_pac_exist) > 1:
                        list_of_internal = Internalerrors.objects.filter(center=cen_id, project=pro_id, date=to_date[0],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
                    else:
                        list_of_internal = Internalerrors.objects.filter(center=cen_id, project=pro_id, date=to_date[0],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')

    else:
        packets_list = work_packet.split('_')
        packets_list_type = ''
        final_external_drilldown = {}
        if len(to_date)>1:
            final_val_res = internal_chart_data_multi(pro_id, cen_id, to_date, work_packet, chart_type, project)
            final_external_drilldown['type'] = chart_type
            final_external_drilldown['project'] = project
            final_external_drilldown['data'] = final_val_res['data']
            final_external_drilldown['table_headers'] = final_val_res['table_headers']
            return final_external_drilldown
        if len(packets_list) == 2:
            sub_project_statuts = Externalerrors.objects.filter(center=cen_id, project=pro_id,date=to_date[0]).values_list('sub_project', flat=True)
            sub_project_statuts = filter(None, sub_project_statuts)
            if len(sub_project_statuts) > 0:
                sub_project, work_packet = work_packet.split('_')
                list_of_internal = Externalerrors.objects.filter(project=pro_id, center=cen_id, date=to_date[0],sub_project=sub_project,work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
            work_packet_statuts = Externalerrors.objects.filter(center=cen_id, project=pro_id,date=to_date[0]).values_list('work_packet', flat=True)
            work_packet_statuts = filter(None, work_packet_statuts)
            if len(sub_project_statuts) == 0 and len(work_packet_statuts) > 0:
                work_packet, sub_packet = work_packet.split('_')
                is_work_pac_exist = Externalerrors.objects.filter(center=cen_id, project=pro_id, date=to_date[0]).values_list('work_packet','sub_packet').distinct()
                if len(is_work_pac_exist) > 1:
                    list_of_internal = Externalerrors.objects.filter(center=cen_id, project=pro_id, date=to_date[0],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
                else:
                    list_of_internal = Externalerrors.objects.filter(center=cen_id, project=pro_id, date=to_date[0],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
        elif len(packets_list) == 3:
            if '_' in work_packet:
                sub_project, work_packet, sub_packet = work_packet.split('_')
                list_of_internal = Externalerrors.objects.filter(center=cen_id, project=pro_id, date=to_date[0],work_packet=work_packet,sub_packet=sub_packet).values_list('employee_id','audited_errors','total_errors','date')
            else:
                is_work_pac_exist = Externalerrors.objects.filter(center=cen_id, project=pro_id, date=to_date[0]).values_list('work_packet','sub_packet').distinct()[0]
                if len(is_work_pac_exist) > 1:
                    list_of_internal = Externalerrors.objects.filter(center=cen_id, project=pro_id, date=to_date[0],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
                else:
                    list_of_internal = Externalerrors.objects.filter(center=cen_id, project=pro_id, date=to_date[0],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
        else:
            sub_project_statuts = Externalerrors.objects.filter(center=cen_id, project=pro_id,date=to_date[0]).values_list('sub_project', flat=True)
            sub_project_statuts = filter(None, sub_project_statuts)
            if len(sub_project_statuts) > 0:
                packets_list_type = 'sub_project'
                is_work_pac_exist = Externalerrors.objects.filter(center=cen_id, project=pro_id, date=to_date[0]).values_list('sub_project','work_packet','sub_packet').distinct()[0]
                if len(is_work_pac_exist) > 1:
                    list_of_internal = Externalerrors.objects.filter(center=cen_id, project=pro_id, date=to_date[0],sub_project=packets_list[0]).values_list('employee_id', 'audited_errors', 'total_errors','date')
                else:
                    list_of_internal = Externalerrors.objects.filter(center=cen_id, project=pro_id, date=to_date[0],sub_project=packets_list[0]).values_list('employee_id', 'audited_errors', 'total_errors','date')
            else:
                packets_list_type = 'work_packet'
                is_work_pac_exist = Externalerrors.objects.filter(center=cen_id, project=pro_id, date=to_date[0]).values_list('work_packet','sub_packet').distinct()
                if len(is_work_pac_exist) > 1:
                    list_of_internal = Externalerrors.objects.filter(center=cen_id, project=pro_id, date=to_date[0],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
                else:
                    list_of_internal = Externalerrors.objects.filter(center=cen_id, project=pro_id, date=to_date[0],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')

    final_internal_drilldown = {}
    final_internal_drilldown['type'] = chart_type
    final_internal_drilldown['project'] = project
    internal_list = []
    table_headers = []
    for i in list_of_internal:
        #internal_list.append({'name':i[0],'audited_count':i[1], 'total_errors':i[2],'date':str(i[3])})
        internal_list.append({'audited_count':i[1], 'total_errors':i[2],'date':str(i[3])})
        audited_value = 0 
        Error_count = 0
        for ans in internal_list:
            if ans['audited_count']:
                audited_value = audited_value + ans['audited_count']
            if ans['total_errors']:
                Error_count = Error_count + ans['total_errors']
            if ans['audited_count']>0:
                accuracy = 100 - ((float(ans['total_errors']) / float(ans['audited_count']))) * 100
            else:
                accuracy = 0
            accuracy_agg = float('%.2f' % round(accuracy, 2))
            ans['accuracy'] = accuracy_agg

        if len(internal_list)>0:
            #table_headers = ['date','name','audited_count','total_errors','accuracy']
            table_headers = ['date','audited_count','total_errors']
    final_internal_drilldown['data'] = internal_list
    final_internal_drilldown['table_headers'] = table_headers
    final_internal_drilldown['audited_value'] = audited_value
    final_internal_drilldown['Error_count'] = Error_count
    return final_internal_drilldown



def productivity_chart_data_multi(pro_id,cen_id,to_date,work_packet,chart_type,project):
    final_productivity_drilldown = {}
    final_productivity_drilldown['type'] = chart_type
    final_productivity_drilldown['project'] = project
    packets_list = work_packet.split('_')
    packets_list_type = ''

    if len(packets_list) == 2:
        sub_project_statuts = RawTable.objects.filter(center=cen_id, project=pro_id,date__range=[to_date[0], to_date[-1]]).values_list('sub_project', flat=True)
        sub_project_statuts = filter(None, sub_project_statuts)
        if len(sub_project_statuts) > 0:
            sub_project, work_packet = work_packet.split('_')
            detail_list = RawTable.objects.filter(center=cen_id, project=pro_id, date__range=[to_date[0], to_date[-1]],sub_project=sub_project, work_packet=work_packet).values_list('employee_id', 'per_day', 'sub_packet','date')
            packets_list_type = 'sub_packet'
        else:
            packets_list_type = 'sub_packet'
            is_work_pac_exist = RawTable.objects.filter(center=cen_id, project=pro_id, date__range=[to_date[0], to_date[-1]]).values_list('work_packet','sub_packet').distinct()[0]
            if len(is_work_pac_exist) > 1:
                detail_list = RawTable.objects.filter(center=cen_id, project=pro_id, date__range=[to_date[0], to_date[-1]],work_packet=packets_list[0]).values_list('employee_id', 'per_day','date')
            else:
                detail_list = RawTable.objects.filter(center=cen_id, project=pro_id, date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id', 'per_day','date')
        packet_dict = []


    elif len(packets_list) == 3:
        if '_' in work_packet:
            sub_project,work_packet,sub_packet = work_packet.split('_')
            detail_list = RawTable.objects.filter(center=cen_id,project=pro_id,date__range=[to_date[0], to_date[-1]],work_packet=work_packet,sub_packet=sub_packet).values_list('employee_id','per_day','date')
        else:
            is_work_pac_exist = RawTable.objects.filter(center=cen_id,project=pro_id,date__range=[to_date[0], to_date[-1]]).values_list('work_packet','sub_packet').distinct()[0]
            if len(is_work_pac_exist) > 1:
                detail_list = RawTable.objects.filter(center=cen_id,project=pro_id,date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','per_day','sub_packet','date')
            else:
                detail_list = RawTable.objects.filter(center=cen_id,project=pro_id,date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','per_day','date')
        packet_dict = []
    else:
        sub_project_statuts = RawTable.objects.filter(center=cen_id, project=pro_id, date__range=[to_date[0], to_date[-1]]).values_list('sub_project', flat=True)
        sub_project_statuts = filter(None, sub_project_statuts)
        if len(sub_project_statuts) > 0:
            is_work_pac_exist = RawTable.objects.filter(center=cen_id,project=pro_id,date__range=[to_date[0], to_date[-1]]).values_list('sub_project','work_packet','sub_packet').distinct()[0]
            if len(is_work_pac_exist) > 1:
                detail_list = RawTable.objects.filter(center=cen_id,project=pro_id,date__range=[to_date[0], to_date[-1]],sub_project=packets_list[0]).values_list('employee_id', 'per_day', 'work_packet','date')
            else:
                detail_list = RawTable.objects.filter(center=cen_id,project=pro_id,date__range=[to_date[0], to_date[-1]],sub_project=packets_list[0]).values_list('employee_id','per_day','date')
            packets_list_type = 'work_packet'
        else:
            sub_packet_statuts = RawTable.objects.filter(center=cen_id, project=pro_id,date__range=[to_date[0], to_date[-1]]).values_list('sub_packet', flat=True)
            sub_packet_statuts = filter(None, sub_packet_statuts) 
            packets_list_type = 'work_packet'
            if sub_packet_statuts:
                detail_list = RawTable.objects.filter(center=cen_id, project=pro_id,date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id', 'per_day', 'sub_packet','date')
                packets_list_type = 'sub_packet'
            else: 
                is_work_pac_exist = RawTable.objects.filter(center=cen_id, project=pro_id, date__range=[to_date[0], to_date[-1]]).values_list('work_packet','sub_packet').distinct()[0]
                if len(is_work_pac_exist) > 1:
                    detail_list = RawTable.objects.filter(center=cen_id, project=pro_id, date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id', 'per_day','date')
                else:
                    detail_list = RawTable.objects.filter(center=cen_id, project=pro_id, date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id', 'per_day','date')
        packet_dict = []
    table_headers = []
    for i in detail_list:
        if i[1]>0:
            if len(i) == 3:
                packet_dict.append({'name':i[0],'done':i[1],'date': str(i[2])})
            else:
                packet_dict.append({'name':i[0],'done':i[1],packets_list_type:i[2], 'date': str(i[3])})
        if len(packet_dict) > 0:
            table_headers = ['date','name', 'done']
            if len(packet_dict[0]) == 4:
                table_headers = ['date','name', packets_list_type, 'done']
    final_productivity_drilldown['data'] = packet_dict
    final_productivity_drilldown['table_headers'] = table_headers
    return final_productivity_drilldown



def productivity_chart_data(pro_id,cen_id,to_date,work_packet,chart_type,project):
    final_productivity_drilldown = {} 
    final_productivity_drilldown['type'] = chart_type
    final_productivity_drilldown['project'] = project
    #import pdb;pdb.set_trace()
    if len(to_date) == 2:
        final_val_result = productivity_chart_data_multi(pro_id,cen_id,to_date,work_packet,chart_type,project)
        return final_val_result
    else:
        packets_list = work_packet.split('_')
        packets_list_type = ''
        if len(packets_list) == 2:
            sub_project_statuts = RawTable.objects.filter(center=cen_id,project=pro_id,date=to_date[0]).values_list('sub_project',flat=True)
            sub_project_statuts  = filter(None,sub_project_statuts)
            if len(sub_project_statuts) > 0:
                sub_project,work_packet = work_packet.split('_')
                detail_list = RawTable.objects.filter(center=cen_id,project=pro_id,date=to_date[0],sub_project=sub_project,work_packet=work_packet).values_list('employee_id','per_day','sub_packet')
                packets_list_type = 'sub_packet'
            else:
                packets_list_type = 'sub_packet'
                is_work_pac_exist = RawTable.objects.filter(center=cen_id,project=pro_id,date=to_date[0]).values_list('work_packet','sub_packet').distinct()[0]
                if len(is_work_pac_exist) > 1:
                    detail_list = RawTable.objects.filter(center=cen_id,project=pro_id,date=to_date[0],work_packet=packets_list[0]).values_list('employee_id','per_day')
                else:
                    detail_list = RawTable.objects.filter(center=cen_id,project=pro_id,date=to_date[0],work_packet=work_packet).values_list('employee_id','per_day')
            packet_dict = []
        elif len(packets_list) == 3:
            if '_' in work_packet:
                sub_project,work_packet,sub_packet = work_packet.split('_')
                detail_list = RawTable.objects.filter(center=cen_id,project=pro_id,date=to_date[0],work_packet=work_packet,sub_packet=sub_packet).values_list('employee_id','per_day')
            else:
                is_work_pac_exist = RawTable.objects.filter(center=cen_id,project=pro_id,date=to_date[0]).values_list('work_packet','sub_packet').distinct()[0]
                if len(is_work_pac_exist) > 1:
                    detail_list = RawTable.objects.filter(center=cen_id,project=pro_id,date=to_date[0],work_packet=work_packet).values_list('employee_id','per_day','sub_packet')
                else:
                    detail_list = RawTable.objects.filter(center=cen_id,project=pro_id,date=to_date[0],work_packet=work_packet).values_list('employee_id','per_day')
            packet_dict = []
        else:
            sub_project_statuts = RawTable.objects.filter(center=cen_id, project=pro_id, date=to_date[0]).values_list('sub_project', flat=True)
            sub_project_statuts = filter(None, sub_project_statuts)
            if len(sub_project_statuts) > 0:
                packets_list_type = 'work_packet'
                is_work_pac_exist = RawTable.objects.filter(center=cen_id,project=pro_id,date=to_date[0]).values_list('sub_project','work_packet','sub_packet').distinct()[0]
                if len(is_work_pac_exist) > 1:
                    detail_list = RawTable.objects.filter(center=cen_id, project=pro_id, date=to_date[0],sub_project=packets_list[0]).values_list('employee_id', 'per_day','work_packet', 'date')
                else:
                    detail_list = RawTable.objects.filter(center=cen_id,project=pro_id,date=to_date[0],sub_project=packets_list[0]).values_list('employee_id','per_day','date')
            else:
                sub_packet_statuts = RawTable.objects.filter(center=cen_id, project=pro_id,date=to_date[0]).values_list('sub_packet', flat=True)
                sub_packet_statuts = filter(None, sub_packet_statuts) 
                packets_list_type = 'work_packet'
                if sub_packet_statuts:
                    detail_list = RawTable.objects.filter(center=cen_id, project=pro_id,date=to_date[0],work_packet=work_packet).values_list('employee_id', 'per_day','sub_packet')
                    packets_list_type = 'sub_packet'
                else:
                    packets_list_type = 'work_packet'
                    is_work_pac_exist = RawTable.objects.filter(center=cen_id, project=pro_id, date=to_date[0]).values_list('work_packet','sub_packet').distinct()[0]
                    if len(is_work_pac_exist) > 1:
                        detail_list = RawTable.objects.filter(center=cen_id, project=pro_id, date=to_date[0],work_packet=work_packet).values_list('employee_id', 'per_day')
                    else:
                        detail_list = RawTable.objects.filter(center=cen_id, project=pro_id, date=to_date[0],work_packet=work_packet).values_list('employee_id', 'per_day','date')
            packet_dict = []
        table_headers = []
        for i in detail_list:
            if i[1] > 0:
                if len(i) == 2:
                    packet_dict.append({'name':i[0],'done':i[1]})

                else:
                    packet_dict.append({'name': i[0], 'done': i[1], packets_list_type: i[2]})
        if len(packet_dict) > 0:
            table_headers = ['name', 'done']
            if len(packet_dict[0])==3:
                table_headers = ['name',packets_list_type, 'done']
        final_productivity_drilldown['data'] = packet_dict
        final_productivity_drilldown['table_headers'] = table_headers
        return final_productivity_drilldown


def chart_data(request):
    #import pdb;pdb.set_trace()
    user_id = request.user.id
    project = request.GET['project'].strip(' - ')
    center = request.GET['center'].strip(' - ')
    drilldown_res = Customer.objects.filter(name_id=user_id).values_list('is_drilldown')
    if not drilldown_res:
        drilldown_res = ''
    else:
        drilldown_res = drilldown_res[0][0]
    user_group = request.user.groups.values_list('name', flat=True)[0]
    if drilldown_res or user_group != 'customer':
        pro_id = Project.objects.filter(name=project).values_list('id')[0][0]
        cen_id = Center.objects.filter(name=center).values_list('id')[0][0]
        chart_type = str(request.GET['type'])
        if chart_type == 'Internal Accuracy' or chart_type == 'External Accuracy' or chart_type == 'Internal_Bar_Pie' or chart_type == 'External_Bar_Pie':
            from_ = datetime.datetime.strptime(request.GET['from'], '%Y-%m-%d').date()
            to_ = datetime.datetime.strptime(request.GET['to'], '%Y-%m-%d').date()
        else:
            drilldown_dates = [] 
            date_taken = request.GET['date']
            if 'to' in request.GET['date']:
                to_date_1 = date_taken.split('to')[0].strip()
                to_date_2 = date_taken.split('to')[1].strip()
                drilldown_dates.append(to_date_1)
                drilldown_dates.append(to_date_2)
            else:
                to_date = datetime.datetime.strptime(request.GET['date'], '%Y-%m-%d').date()
                drilldown_dates.append(to_date)
        work_packet = str(request.GET['packet'])
        if ' # ' in work_packet:
            work_packet = work_packet.replace(' # ','#')
        if ' and ' in work_packet:
            work_packet = work_packet.replace(' and ',' & ')
        final_dict = ''
        if chart_type == 'Internal Accuracy Trends' or chart_type == 'External Accuracy Trends':
            final_dict = internal_chart_data(pro_id,cen_id,drilldown_dates,work_packet,chart_type,project)
        elif chart_type == 'Internal Accuracy' or chart_type == 'External Accuracy' or chart_type == 'Internal_Bar_Pie' or chart_type == 'External_Bar_Pie':
            final_dict = internal_bar_data(pro_id, cen_id, from_, to_, work_packet, chart_type,project)
        else:
            final_dict = productivity_chart_data(pro_id,cen_id,drilldown_dates,work_packet,chart_type,project)
        return HttpResponse(final_dict)
    else:
        return HttpResponse('Drilldown disabled')


def workpackets_list(level_structure_key,table_model_name,query_set):
    table_model = apps.get_model('api', 'Headcount')
    #table_model= get_model(table_model_name, 'Headcount')
    if level_structure_key.has_key('sub_project'):
        if level_structure_key['sub_project'] == "All":
            volume_list = table_model.objects.filter(**query_set).values('sub_project').distinct()
        else:
            if level_structure_key.has_key('work_packet'):
                if level_structure_key['work_packet'] == "All":
                    volume_list = table_model.objects.filter(**query_set).values('sub_project', 'work_packet').distinct()
                else:
                    volume_list = table_model.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()
    elif level_structure_key.has_key('work_packet') and len(level_structure_key) == 1:
        if level_structure_key['work_packet'] == "All":
            volume_list = table_model.objects.filter(**query_set).values('work_packet').distinct()
        else:
            volume_list = table_model.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()
    elif level_structure_key.has_key('work_packet') and level_structure_key.has_key('sub_packet'):
        volume_list = table_model.objects.filter(**query_set).values('sub_project', 'work_packet', 'sub_packet').distinct()
    else:
        volume_list = []
    return volume_list



def workpackets_list_utilization(level_structure_key,table_model_name,query_set):
    table_model = apps.get_model('api', 'Headcount')
    if level_structure_key.has_key('sub_project'):
        if level_structure_key['sub_project'] == "All":
            volume_list = table_model.objects.filter(**query_set).values('sub_project','work_packet').distinct()
        else:
            if level_structure_key.has_key('work_packet'):
                if level_structure_key['work_packet'] == "All":
                    volume_list = table_model.objects.filter(**query_set).values('sub_project', 'work_packet').distinct()
                else:
                    volume_list = table_model.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()
    elif level_structure_key.has_key('work_packet') and len(level_structure_key) == 1:
        if level_structure_key['work_packet'] == "All":
            volume_list = table_model.objects.filter(**query_set).values('work_packet').distinct()
        else:
            volume_list = table_model.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()
    elif level_structure_key.has_key('work_packet') and level_structure_key.has_key('sub_packet'):
        volume_list = table_model.objects.filter(**query_set).values('sub_project', 'work_packet', 'sub_packet').distinct()
    else:
        volume_list = []
    return volume_list



def worktrack_internal_external_workpackets_list(level_structure_key,table_model_name,query_set):
    table_model = apps.get_model('api', table_model_name)
    volume_list = []
    if level_structure_key.has_key('sub_project'):
        if level_structure_key['sub_project'] == "All":
            volume_list = table_model.objects.filter(**query_set).values('sub_project').distinct()
        else:
            if level_structure_key.has_key('work_packet'):
                if level_structure_key['work_packet'] == "All":
                    volume_list = table_model.objects.filter(**query_set).values('sub_project', 'work_packet').distinct()
                else:
                    sub_packet = filter(None, Worktrack.objects.filter(**query_set).values('sub_packet').distinct())
                    volume_list = table_model.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()
                    if sub_packet:
                        volume_list = table_model.objects.filter(**query_set).values('sub_project','work_packet').distinct()
    elif level_structure_key.has_key('work_packet') and len(level_structure_key) == 1:
        if level_structure_key['work_packet'] == "All":
            volume_list = table_model.objects.filter(**query_set).values('sub_project', 'work_packet').distinct()
        else:
            sub_packet = filter(None, table_model.objects.filter(**query_set).values('sub_packet').distinct())
            volume_list = table_model.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()
            if sub_packet:
                volume_list = table_model.objects.filter(**query_set).values('sub_project', 'work_packet').distinct()
    elif level_structure_key.has_key('work_packet') and level_structure_key.has_key('sub_packet'):
        volume_list = table_model.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()
    else:
        volume_list = []
    return volume_list

def modified_utilization_calculations(center,prj_id,date_list,level_structure_key):
    final_utilization_result = {}
    final_utilization_result['fte_utilization'] = {}
    final_utilization_result['fte_utilization']['fte_utilization'] = []
    final_utilization_result['operational_utilization'] = {}
    final_utilization_result['operational_utilization']['operational_utilization'] = []
    final_utilization_result['overall_utilization'] = {}
    final_utilization_result['overall_utilization']['overall_utilization'] = []
    status = 0
    if level_structure_key.get('sub_project','') == 'All':
        status = 1
    elif level_structure_key.get('work_packet','') == 'All':
        status = 1
    if status:
        final_prodictivity = {} 
        product_date_values = {} 
        utilization_date_values = {} 
        product_date_values['total_prodictivity'] = [] 
        utilization_date_values['total_utilization'] = [] 
        for date_value in date_list:
            total_done_value = RawTable.objects.filter(project=prj_id, center=center, date=date_value).aggregate(Max('per_day'))
            if total_done_value['per_day__max'] > 0: 
                headcount_details = Headcount.objects.filter(project=prj_id, center=center, date=date_value).aggregate(Sum('billable_hc'),
                                    Sum('billable_agents'),Sum('buffer_agents'),Sum('qc_or_qa'),Sum('teamlead'),
                                    Sum('trainees_and_trainers'),Sum('managers'),Sum('mis'))
                headcount_data = {}
                for hc_key,hc_value in headcount_details.iteritems():
                    headcount_data[hc_key] = hc_value
                    if hc_value == None:
                        headcount_data[hc_key] = 0
                util_numerator = headcount_data['billable_hc__sum']

                fte_denominator = headcount_data['billable_agents__sum'] + headcount_data['buffer_agents__sum'] + headcount_data['qc_or_qa__sum'] + headcount_data['teamlead__sum']
                operational_denominator  = fte_denominator + headcount_data['trainees_and_trainers__sum']
                overall_util_denominator = operational_denominator + headcount_data['managers__sum'] + headcount_data['mis__sum']
                if fte_denominator > 0:
                    fte_value = (float(float(util_numerator) / float(fte_denominator))) * 100
                    fte_value = float('%.2f' % round(fte_value, 2))
                else:
                    fte_value = 0
                final_utilization_result['fte_utilization']['fte_utilization'].append(fte_value)
                if operational_denominator > 0:
                    operational_value = (float(float(util_numerator) / float(operational_denominator))) * 100
                    operational_value = float('%.2f' % round(operational_value, 2))
                else:
                    operational_value = 0
                final_utilization_result['operational_utilization']['operational_utilization'].append(operational_value)
                if overall_util_denominator > 0:
                    overall_util_value = (float(float(util_numerator) / float(overall_util_denominator))) * 100
                    overall_util_value = float('%.2f' % round(overall_util_value, 2))
                else:
                    overall_util_value = 0
                final_utilization_result['overall_utilization']['overall_utilization'].append(overall_util_value)
    return final_utilization_result 



def modified_main_productit(center,prj_id,date_list,level_structure_key):
    final_prodictivity = {}



def main_productivity_data(center,prj_id,date_list,level_structure_key):
    work_packet_dict = {}
    final_prodictivity = {}
    final_data = []
    final_prodictivity['utilization'] = {}
    final_prodictivity['utilization']['utilization']= []
    packet_names = Headcount.objects.filter(project=prj_id, center=center, date__range=[date_list[0],date_list[-1]]).values('sub_project', 'work_packet', 'sub_packet').distinct()
    count = 0
    prj_name = Project.objects.filter(id=prj_id).values_list('name', flat=True)
    if prj_name[0] in ['Probe']:
        count = count+1
    for i in packet_names:
        if all(value == '' for value in i.values()):
            count = count+1
    status = 0
    if level_structure_key.get('sub_project','') == 'All':
        status = 1
    elif level_structure_key.get('sub_project','') == '' and level_structure_key.get('work_packet','') == 'All':
        status = 1
    final_work_packet = ''
    if status and count:
        final_prodictivity = {}
        product_date_values = {}
        utilization_date_values = {}
        product_date_values['total_prodictivity'] = []
        utilization_date_values['total_utilization'] = []
        for date_value in date_list:
            print "first productivity"
            total_done_value = RawTable.objects.filter(project=prj_id, center=center, date=date_value).aggregate(Max('per_day'))
            if total_done_value['per_day__max'] > 0:
                billable_emp_count = Headcount.objects.filter(project=prj_id, center=center, date=date_value).values_list('billable_agents', flat=True)
                #total_emp_count = Headcount.objects.filter(project=prj_id, center=center, date=date_value).values_list('total', flat=True)
                total_work_done = RawTable.objects.filter(project=prj_id, center=center, date=date_value).values_list('per_day').aggregate(Sum('per_day'))
                total_work_done = total_work_done.get('per_day__sum')
                print 'billable_emp_count', billable_emp_count
                print 'total_work_done', total_work_done
            # below code for productivity

                if len(billable_emp_count) > 0 and billable_emp_count[0] != 0:
                    productivity_value = float(total_work_done / float(sum(billable_emp_count)))
                else:
                    productivity_value = 0
                final_prodictivity_value = float('%.2f' % round(productivity_value, 2))
                product_date_values['total_prodictivity'].append(final_prodictivity_value)
                # below code for utilization
                """if len(total_emp_count) > 0:
                    utilization_value = (float(float(billable_emp_count[0]) / float(total_emp_count[0]))) * 100
                else:
                    utilization_value = 0
                final_utilization_value = float('%.2f' % round(utilization_value, 2))
                utilization_date_values['total_utilization'].append(final_utilization_value)"""
        final_prodictivity['productivity'] = product_date_values
        final_prodictivity['utilization'] = utilization_date_values
    else:
        new_date_list = []
        product_date_values = {}
        utilization_date_values = {}
        query_set = query_set_generation(prj_id[0], center[0], level_structure_key, date_list)
        volume_list = workpackets_list(level_structure_key, 'Headcount', query_set)
        for date_value in date_list:
            print "sencond productivity"
            packet_count = 0
            total_done_value = RawTable.objects.filter(project=prj_id, center=center[0], date=date_value).aggregate(Max('per_day'))
            if total_done_value['per_day__max'] > 0:
                for vol_type in volume_list:
                    if level_structure_key.has_key('sub_project'):
                        local_level_hierarchy_key = vol_type
                    else:
                        local_level_hierarchy_key = level_structure_key
                    final_work_packet = level_hierarchy_key(local_level_hierarchy_key, vol_type)
                    total_work_query_set = {}
                    total_work_query_set['project'] = prj_id[0]
                    total_work_query_set['center'] = center[0]
                    total_work_query_set['date'] = date_value
                    for vol_key, vol_value in vol_type.iteritems():
                        total_work_query_set[vol_key] = vol_value
                    billable_emp_count = Headcount.objects.filter(**total_work_query_set).values_list('billable_agents',flat=True)
                    #total_emp_count = Headcount.objects.filter(**total_work_query_set).values_list('total', flat=True)
                    total_work_done = RawTable.objects.filter(**total_work_query_set).values_list('per_day').aggregate(Sum('per_day'))
                    total_work_done = total_work_done.get('per_day__sum')
                    # below code for productivity
                    #import pdb;pdb.set_trace()
                    if len(billable_emp_count) > 0 and total_work_done != None:
                        if billable_emp_count[0] != 0:
                            productivity_value = float(total_work_done / float(billable_emp_count[0]))
                        else: 
                            productivity_value = 0
                    else:
                        productivity_value = 0
                    final_prodictivity_value = float('%.2f' % round(productivity_value, 2))

                    if product_date_values.has_key(final_work_packet):
                        product_date_values[final_work_packet].append(final_prodictivity_value)
                    else:
                        product_date_values[final_work_packet] = [final_prodictivity_value]

                    """if len(total_emp_count) > 0:
                        utilization_value = (float(float(billable_emp_count[0]) / float(total_emp_count[0]))) * 100
                    else:
                        utilization_value = 0
                    final_utilization_value = float('%.2f' % round(utilization_value, 2))
                    packet_count += 1
                    if utilization_date_values.has_key(final_work_packet):
                        utilization_date_values[final_work_packet].append(final_utilization_value)
                    else:
                        utilization_date_values[final_work_packet] = [final_utilization_value]

        total = 0
        if len(utilization_date_values) > 0:
            first_key = utilization_date_values[utilization_date_values.keys()[0]]
            packet_count = len(utilization_date_values.keys())
        else:
            first_key = ''

        for i in range(len(first_key)):
            packet_sum = 0
            zero_packet_count = 0
            for key in utilization_date_values.keys():
                packet_value = utilization_date_values[key][i]
                if packet_value == 0:
                    zero_packet_count = zero_packet_count + 1
                packet_sum += utilization_date_values[key][i]
            final_data.append(packet_sum)
            total = total + 1
            if packet_count > 0:
                local_packet_count = packet_count - zero_packet_count
                if local_packet_count > 0:
                    packet_data = float(final_data[i]) / local_packet_count
                else:
                    packet_data = 0
            else:
                packet_data = 0
            final_packet_data = float('%.2f' % round(packet_data, 2))
            final_prodictivity['utilization']['utilization'].append(final_packet_data)"""
        final_prodictivity['productivity'] = product_date_values
        #final_prodictivity['utilization'] = utilization_date_values
    return final_prodictivity


def utilization_work_packet_data(center,prj_id,date_list,level_structure_key):
    final_data = []
    work_packet_dict = {}
    final_prodictivity = {}
    final_prodictivity['utilization'] = {}
    final_prodictivity['utilization']['utilization']= []
    final_work_packet = ''
    packet_names = Headcount.objects.filter(project=prj_id, center=center, date__range=[date_list[0],date_list[-1]]).values('sub_project', 'work_packet', 'sub_packet').distinct()
    count = 0
    prj_name = Project.objects.filter(id=prj_id).values_list('name', flat=True)
    if prj_name[0] in ['Probe']:
        count = count+1
    for i in packet_names:
        if all(value == '' for value in i.values()):
            count = count+1
    status = 0
    if level_structure_key.get('sub_project','') == 'All':
        status = 1
    elif level_structure_key.get('sub_project','') == '' and level_structure_key.get('work_packet','') == 'All':
        status = 1


    if status and count:
        final_prodictivity = {}
        product_date_values = {}
        utilization_date_values = {}
        product_date_values['total_prodictivity'] = []
        utilization_date_values['total_utilization'] = []
        for date_value in date_list:
            total_done_value = RawTable.objects.filter(project=prj_id, center=center, date=date_value).aggregate(Max('per_day'))
            if total_done_value['per_day__max'] > 0:
                billable_count = Headcount.objects.filter(project=prj_id, center=center, date=date_value).values_list('billable_agent', 'buffer_agent').distinct()
                new_billable_count = [] 
                if len(billable_count)>=2:
                    for b_count in billable_count:
                        if len(new_billable_count) == 0:
                            new_billable_count.append(b_count[0])
                            new_billable_count.append(b_count[1])
                        else:
                            new_billable_count[0]= b_count[0]+new_billable_count[0]
                            new_billable_count[1] = b_count[1]+new_billable_count[1]
                    billable_count = [tuple(new_billable_count)]

                for i in billable_count:
                    if i[0] > 0:
                        utilization_value = (float(float(i[0]) / float(i[0] + i[1]))) * 100
                        final_utilization_value = float('%.2f' % round(utilization_value, 2))
                    else:
                        final_utilization_value = 0
                    utilization_date_values['total_utilization'].append(final_utilization_value)
        final_prodictivity['utilization'] = utilization_date_values
    else:
        new_date_list = []
        product_date_values = {}
        utilization_date_values = {}
        query_set = query_set_generation(prj_id[0], center[0], level_structure_key, date_list)
        volume_list = workpackets_list_utilization(level_structure_key, 'Headcount', query_set)
        for date_value in date_list:
            packet_count = 0
            total_done_value = RawTable.objects.filter(project=prj_id, center=center[0], date=date_value).aggregate(Max('per_day'))
            if total_done_value['per_day__max'] > 0:
                for vol_type in volume_list:
                    if level_structure_key.has_key('sub_project'):
                        local_level_hierarchy_key = vol_type
                    else:
                        local_level_hierarchy_key = level_structure_key
                    final_work_packet = level_hierarchy_key(local_level_hierarchy_key, vol_type)
                    total_work_query_set = {}
                    total_work_query_set['project'] = prj_id[0]
                    total_work_query_set['center'] = center[0]
                    total_work_query_set['date'] = date_value
                    for vol_key, vol_value in vol_type.iteritems():
                        if vol_value != '':
                            total_work_query_set[vol_key] = vol_value

                    #billable_emp_count = Headcount.objects.filter(**total_work_query_set).values_list('billable_agent',flat=True)
                    billable_count = Headcount.objects.filter(**total_work_query_set).values_list('billable_agent','buffer_agent').distinct()

                    for i in billable_count:
                        if i[0] > 0:
                            utilization_value = (float(float(i[0]) / float(i[0] + i[1]))) * 100
                            final_utilization_value = float('%.2f' % round(utilization_value, 2))
                        else:
                            final_utilization_value = 0

                        packet_count += 1

                        if utilization_date_values.has_key(final_work_packet):
                            utilization_date_values[final_work_packet].append(final_utilization_value)
                        else:
                            utilization_date_values[final_work_packet] = [final_utilization_value]
                    if not billable_count:
                        if utilization_date_values.has_key(final_work_packet):
                            utilization_date_values[final_work_packet].append(0)
                        else:
                            utilization_date_values[final_work_packet] = [0]

        total = 0
        if len(utilization_date_values) > 0:
            first_key = utilization_date_values[utilization_date_values.keys()[0]]
            packet_count = len(utilization_date_values.keys())
        else:
            first_key = ''

        for i in range(len(first_key)):
            packet_sum = 0
            zero_packet_count =0
            for key in utilization_date_values.keys():
                packet_value = utilization_date_values[key][i]
                if packet_value == 0:
                    zero_packet_count = zero_packet_count+1
                packet_sum += utilization_date_values[key][i]
            final_data.append(packet_sum)
            if packet_count > 0:
                local_packet_count = packet_count - zero_packet_count
                if local_packet_count > 0:
                    packet_data = float(final_data[i]) / local_packet_count
                else:
                    packet_data = 0
            else:
                packet_data = 0
            final_packet_data = float('%.2f' % round(packet_data, 2))
            final_prodictivity['utilization']['utilization'].append(final_packet_data)
            total = total + 1

    return final_prodictivity


def utilization_operational_data(center,prj_id,date_list,level_structure_key):
    work_packet_dict = {}
    final_prodictivity = {}
    final_data = []

    final_prodictivity['utilization'] = {}
    final_prodictivity['utilization']['total_utilization']= []
    final_work_packet = ''
    packet_names = Headcount.objects.filter(project=prj_id, center=center, date__range=[date_list[0],date_list[-1]]).values('sub_project', 'work_packet', 'sub_packet').distinct()
    count = 0
    for i in packet_names:
        if all(value == '' for value in i.values()):
            count = count+1
    status = 0
    if level_structure_key.get('sub_project','') == 'All':
        status = 1
    elif level_structure_key.get('sub_project','') == '' and level_structure_key.get('work_packet','') == 'All':
        status = 1

    if status and count:
        final_prodictivity = {}
        product_date_values = {}
        utilization_date_values = {}
        product_date_values['total_prodictivity'] = []
        utilization_date_values['total_utilization'] = []
        for date_value in date_list:
            total_done_value = RawTable.objects.filter(project=prj_id, center=center, date=date_value).aggregate(Max('per_day'))
            if total_done_value['per_day__max'] > 0:
                billable_count = Headcount.objects.filter(project=prj_id, center=center, date=date_value).values_list('billable_agent', 'buffer_agent', 'billable_support', 'buffer_support').distinct()
                new_billable_count = [] 
                if len(billable_count)>=2:
                    for b_count in billable_count:
                        if len(new_billable_count) == 0:
                            new_billable_count.append(b_count[0])
                            new_billable_count.append(b_count[1])
                            new_billable_count.append(b_count[2])
                            new_billable_count.append(b_count[3])
                        else:
                            new_billable_count[0]= b_count[0]+new_billable_count[0]
                            new_billable_count[1] = b_count[1]+new_billable_count[1]
                            new_billable_count[2] = b_count[2]+new_billable_count[2]
                            new_billable_count[3] = b_count[3]+new_billable_count[3]
                    billable_count = [tuple(new_billable_count)]

                for i in billable_count:
                    if i[0] > 0:
                        utilization_value = (float(float(i[0]) / float(i[0] + i[1] + i[2] + i[3]))) * 100
                        final_utilization_value = float('%.2f' % round(utilization_value, 2))
                    else:
                        final_utilization_value = 0
                    utilization_date_values['total_utilization'].append(final_utilization_value)
        final_prodictivity['utilization'] = utilization_date_values
    else:
        new_date_list = []
        product_date_values = {}
        utilization_date_values = {}
        query_set = query_set_generation(prj_id[0], center[0], level_structure_key, date_list)
        volume_list = workpackets_list_utilization(level_structure_key, 'Headcount', query_set)

        for date_value in date_list:
            packet_count = 0
            total_done_value = RawTable.objects.filter(project=prj_id, center=center[0], date=date_value).aggregate(Max('per_day'))
            if total_done_value['per_day__max'] > 0:
                for vol_type in volume_list:
                    if level_structure_key.has_key('sub_project'):
                        local_level_hierarchy_key = vol_type
                    else:
                        local_level_hierarchy_key = level_structure_key
                    final_work_packet = level_hierarchy_key(local_level_hierarchy_key, vol_type)
                    total_work_query_set = {}
                    total_work_query_set['project'] = prj_id[0]
                    total_work_query_set['center'] = center[0]
                    total_work_query_set['date'] = date_value
                    for vol_key, vol_value in vol_type.iteritems():
                        if vol_value != '':
                            total_work_query_set[vol_key] = vol_value
                    #billable_emp_count = Headcount.objects.filter(**total_work_query_set).values_list('billable_agent',flat=True)
                    billable_count = Headcount.objects.filter(**total_work_query_set).values_list('billable_agent','buffer_agent','billable_support','buffer_support').distinct()
                    new_billable_count = []
                    if len(billable_count)>=2:
                        for b_count in billable_count:
                            if len(new_billable_count) == 0:
                                new_billable_count.append(b_count[0])
                                new_billable_count.append(b_count[1])
                                new_billable_count.append(b_count[2])
                                new_billable_count.append(b_count[3])
                            else:
                                new_billable_count[0]= b_count[0]+new_billable_count[0]
                                new_billable_count[1] = b_count[1]+new_billable_count[1]
                                new_billable_count[2] = b_count[2]+new_billable_count[2]
                                new_billable_count[3]= b_count[3]+new_billable_count[3]
                        billable_count = [tuple(new_billable_count)]

                    for i in billable_count:
                        if i[0] > 0:
                            utilization_value = (float(float(i[0]) / float(i[0] + i[1] + i[2] + i[3]))) * 100
                            final_utilization_value = float('%.2f' % round(utilization_value, 2))
                        else:
                            final_utilization_value = 0
                        packet_count += 1
                        if utilization_date_values.has_key(final_work_packet):
                            utilization_date_values[final_work_packet].append(final_utilization_value)
                        else:
                            utilization_date_values[final_work_packet] = [final_utilization_value]
                    if not billable_count:
                        if utilization_date_values.has_key(final_work_packet):
                            utilization_date_values[final_work_packet].append(0)
                        else:
                            utilization_date_values[final_work_packet] = [0]
        total = 0

        if len(utilization_date_values) > 0:
            first_key = utilization_date_values[utilization_date_values.keys()[0]]
            packet_count = len(utilization_date_values.keys())
        else:
            first_key = ''
        for i in range(len(first_key)):
            packet_sum = 0
            zero_packet_count =0
            for key in utilization_date_values.keys():
                packet_value = utilization_date_values[key][i]
                if packet_value == 0:
                    zero_packet_count = zero_packet_count+1
                packet_sum += utilization_date_values[key][i]
            final_data.append(packet_sum)
            if packet_count > 0:
                local_packet_count = packet_count-zero_packet_count
                if local_packet_count > 0:
                    packet_data = float(final_data[i]) / local_packet_count
                else:
                    packet_data = 0
            else:
                packet_data = 0
            final_packet_data = float('%.2f' % round(packet_data, 2))
            final_prodictivity['utilization']['total_utilization'].append(final_packet_data)
            total = total + 1

    return final_prodictivity


def previous_sum(volumes_dict):
    new_dict = {}
    for key, value in volumes_dict.iteritems():
        new_dict[key] = []
        for i in range(len(value)):
            if i == 0:
                new_dict[key].append(value[i])
            else:
                new_dict[key].append(new_dict[key][i - 1] + value[i])
    return new_dict


def target_query_generations(pro_id,cen_id,date,main_work_packet,level_structure_key):
    target_query_set = {}
    target_query_set['project'] = pro_id
    target_query_set['center'] = cen_id
    if isinstance(date, list):
        target_query_set['from_date__lte']=[date[0], date[-1]]
        target_query_set['to_date__gte'] = [date[0], date[-1]]
    else:
        target_query_set['from_date__lte'] = date
        target_query_set['to_date__gte'] = date

    if '_' in main_work_packet:
        packets_list = main_work_packet.split('_')
        if len(packets_list) == 3:
            target_query_set['sub_project'] = packets_list[0]
            target_query_set['work_packet'] = packets_list[1]
            target_query_set['sub_packet'] = packets_list[2]
        elif len(packets_list) == 2:
            if level_structure_key.has_key('sub_project'):
                target_query_set['sub_project'] = packets_list[0]
                target_query_set['work_packet'] = packets_list[1]
            else:
                target_query_set['work_packet'] = packets_list[0]
                target_query_set['sub_packet'] = packets_list[1]

        else:
            if level_structure_key.has_key('sub_project'):
                target_query_set['sub_project'] = packets_list[0]
            else:
                target_query_set['work_packet'] = packets_list[0]
        #target_query_set['sub_packet'] = packets_list[1]
    else:
        if level_structure_key.has_key('sub_project'):
            target_query_set['sub_project'] = main_work_packet
        else:
            target_query_set['work_packet'] = main_work_packet

    return target_query_set


def rawtable_query_generations(pro_id,cen_id,date,main_work_packet,level_structure_key):
    rawtable_query_set = {}
    rawtable_query_set['project'] = pro_id
    rawtable_query_set['center'] = cen_id
    rawtable_query_set['date'] = date
    if '_' in main_work_packet:
        packets_list = main_work_packet.split('_')
        if len(packets_list) == 3:
            rawtable_query_set['sub_project'] = packets_list[0]
            rawtable_query_set['work_packet'] = packets_list[1]
            rawtable_query_set['sub_packet'] = packets_list[2]
        elif len(packets_list) == 2:
            if level_structure_key.has_key('sub_project'):
                rawtable_query_set['sub_project'] = packets_list[0]
                rawtable_query_set['work_packet'] = packets_list[1]
            else:
                rawtable_query_set['work_packet'] = packets_list[0]
                rawtable_query_set['sub_packet'] = packets_list[1]

        else:
            rawtable_query_set['work_packet'] = packets_list[0]
        #target_query_set['sub_packet'] = packets_list[1]
    else:
        if level_structure_key.has_key('sub_project'):
            rawtable_query_set['sub_project'] = main_work_packet
        else:
            rawtable_query_set['work_packet'] = main_work_packet
    return rawtable_query_set

def tat_table_query_generations(pro_id,cen_id,date,main_work_packet,level_structure_key):
    tat_table_query_set = {}
    tat_table_query_set['project'] = pro_id
    tat_table_query_set['center'] = cen_id
    tat_table_query_set['date'] = date
    if '_' in main_work_packet:
        packets_list = main_work_packet.split('_')
        if len(packets_list) == 3:
            tat_table_query_set['sub_project'] = packets_list[0]
            tat_table_query_set['work_packet'] = packets_list[1]
            tat_table_query_set['sub_packet'] = packets_list[2]
        elif len(packets_list) == 2:
            if level_structure_key.has_key('sub_project'):
                tat_table_query_set['sub_project'] = packets_list[0]
                tat_table_query_set['work_packet'] = packets_list[1]
            else:
                tat_table_query_set['work_packet'] = packets_list[0]
                tat_table_query_set['sub_packet'] = packets_list[1]

        else:
            tat_table_query_set['work_packet'] = packets_list[0]
    else:
        if level_structure_key.has_key('sub_project'):
            tat_table_query_set['sub_project'] = main_work_packet
        else:
            tat_table_query_set['work_packet'] = main_work_packet
    return tat_table_query_set


def Monthly_Volume_graph(date_list, prj_id, center, level_structure_key):
    data_list = []
    conn = redis.Redis(host="localhost", port=6379, db=0)
    date_values = {}
    date_targets = {}
    tar_count = 0
    final_target = []
    final_done_value = []
    done_value = 0
    volume_list = []
    prj_name = Project.objects.filter(id=prj_id).values_list('name', flat=True)
    center_name = Center.objects.filter(id=center).values_list('name', flat=True)
    query_set = query_set_generation(prj_id, center, level_structure_key, date_list)
    target_query_set=target_query_set_generation(prj_id, center, level_structure_key, date_list)
    if level_structure_key.has_key('sub_project'):
        if level_structure_key['sub_project'] == "All":
            sub_packet = filter(None, Targets.objects.filter(**target_query_set).values_list('sub_packet',flat=True).distinct())
            if not sub_packet:
                volume_list = RawTable.objects.filter(**query_set).values('sub_project', 'work_packet').distinct()
            else:
                volume_list = RawTable.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()
        else:
            if level_structure_key.has_key('work_packet'):
                if level_structure_key['work_packet'] == "All":
                    sub_packet = filter(None, Targets.objects.filter(**target_query_set).values_list('sub_packet',flat=True).distinct())
                    if level_structure_key['sub_packet'] == "All":
                        if not sub_packet:
                            volume_list = RawTable.objects.filter(**query_set).values('sub_project','work_packet').distinct()
                        else:
                            volume_list = RawTable.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()

                else:
                    sub_packet = filter(None, Targets.objects.filter(**target_query_set).values_list('sub_packet',flat=True).distinct())
                    if level_structure_key.get('sub_packet','') == "All":
                        if not sub_packet:
                            volume_list = RawTable.objects.filter(**query_set).values('sub_project','work_packet').distinct()
                        else:
                            volume_list = RawTable.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()
                    else:
                        volume_list = []
                        if sub_packet:
                            volume_list = RawTable.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()
    elif level_structure_key.has_key('work_packet') and len(level_structure_key) == 1:
        if level_structure_key['work_packet'] == "All":
            sub_packet = filter(None, Targets.objects.filter(**target_query_set).values_list('sub_packet',flat=True).distinct())
            if level_structure_key.get('sub_packet','') == "All" and sub_packet:
                volume_list = RawTable.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()
            else:
                volume_list = RawTable.objects.filter(**query_set).values('sub_project', 'work_packet').distinct()
        else:
            if level_structure_key.get('sub_packet','') == "All":
                volume_list = RawTable.objects.filter(**query_set).values('sub_project', 'work_packet').distinct()
            else:
                volume_list = RawTable.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()
    elif level_structure_key.has_key('work_packet') and level_structure_key.has_key('sub_packet'):
        sub_packet = filter(None,Targets.objects.filter(**target_query_set).values_list('sub_packet', flat=True).distinct())
        if level_structure_key['sub_packet'] == "All":
            if not sub_packet:
                volume_list = RawTable.objects.filter(**query_set).values('sub_project', 'work_packet').distinct()
        else:
            volume_list = []
            if sub_packet:
                volume_list = RawTable.objects.filter(**query_set).values('sub_project', 'work_packet','sub_packet').distinct()

    else:
        volume_list = []
    new_date_list = []
    volumes_dict = {}
    _targets_list = {}
    final_values = {}
    final_targets = {}
    final_values['total_workdone'] = []
    final_targets['total'] = []
    final_work_packet = ''
    for date in date_list:
        total_done_value = RawTable.objects.filter(project=prj_id, center=center, date=date).aggregate(Max('per_day'))
        if total_done_value['per_day__max'] > 0:
            new_date_list.append(date)
            count = 0
            for vol_type in volume_list:
                if level_structure_key.has_key('sub_project'):
                    local_level_hierarchy_key = vol_type
                else:
                    local_level_hierarchy_key = level_structure_key
                final_work_packet = level_hierarchy_key(local_level_hierarchy_key, vol_type) 
                target_query_set = target_query_generations(prj_id, center, date, final_work_packet,level_structure_key)
                rawtable_query_set = rawtable_query_generations(prj_id, center, date, final_work_packet,level_structure_key)
                employee_names = RawTable.objects.filter(**rawtable_query_set).values_list('employee_id')
                employee_count = len(employee_names)
                targets_list = Targets.objects.filter(**target_query_set).values_list('target',flat=True).distinct()
                target_consideration = Targets.objects.filter(**target_query_set).values('target','fte_target').distinct()
                fte_targets_list = Targets.objects.filter(**target_query_set).values_list('fte_target',flat=True).distinct()
                if len(target_consideration) > 0:
                    if target_consideration[0]['target'] < target_consideration[0]['fte_target']:
                        if len(fte_targets_list) > 0:
                            if _targets_list.has_key(final_work_packet):
                                _targets_list[final_work_packet].append(int(fte_targets_list[0]) * employee_count)
                            else:
                                _targets_list[final_work_packet] = [int(fte_targets_list[0]) * employee_count]
                    elif target_consideration[0]['target'] >= target_consideration[0]['fte_target']:
                        if len(targets_list) > 0:
                            if _targets_list.has_key(final_work_packet):
                                _targets_list[final_work_packet].append(int(targets_list[0]))
                            else:
                                _targets_list[final_work_packet] = [int(targets_list[0])]
                else:
                    if _targets_list.has_key(final_work_packet):
                        _targets_list[final_work_packet].append(0)
                    else:
                        _targets_list[final_work_packet] = [0]
                if not final_work_packet:
                        final_work_packet = level_hierarchy_key(volume_list[count], vol_type)
                count = count + 1
                date_pattern = '{0}_{1}_{2}_{3}'.format(prj_name[0], str(center_name[0]), str(final_work_packet),date)
                key_list = conn.keys(pattern=date_pattern)
                if not key_list:
                    if date_values.has_key(final_work_packet):
                        date_values[final_work_packet].append(0)
                    else:
                        date_values[final_work_packet] = [0]
                for cur_key in key_list:
                    var = conn.hgetall(cur_key)
                    for key, value in var.iteritems():
                        if value == 'None':
                            value = 0
                        if date_values.has_key(key):
                            date_values[key].append(int(value))
                        else:
                            date_values[key] = [int(value)]


    total = 0
    wp_lenght = date_values.keys()
    if len(wp_lenght)>0:
        wp_lenght = date_values[wp_lenght[0]]
    else:
        wp_lenght = ''
    for i in range(len(wp_lenght)):
        packet_sum = 0
        for key in date_values.keys():
            try:
                packet_sum += date_values[key][i]
            except:
                packet_sum = packet_sum
        final_values['total_workdone'].append(packet_sum)
        total = total + 1
    volumes_dict = final_values
    new_dict = previous_sum(volumes_dict)

    result = 0
    if len(_targets_list)>0:
        first_key = _targets_list[_targets_list.keys()[0]]
    else:
        first_key = ''
    for i in range(len(first_key)):
        packet_sum = 0
        for key in _targets_list.keys():
            try:
                packet_sum += _targets_list[key][i]
            except:
                packet_sum = packet_sum
        final_targets['total'].append(packet_sum)
        result = result + 1
    total_target = previous_sum(final_targets)
    new_total_target = {}
    for tr_key, tr_value in total_target.iteritems():
        new_total_target[tr_key + '_target'] = tr_value
    new_dict.update(new_total_target)

    return new_dict


def yesterdays_data(request):
    yesterday = date.today() - timedelta(1)
    date_list = []
    date_list.append(str(yesterday))
    conn = redis.Redis(host="localhost", port=6379, db=0)
    #below varaibles for productivity,wpf graphs
    result = {}
    volumes_dict = {}
    date_values = {}
    volume_list = RawTable.objects.values_list('volume_type', flat=True).distinct()
    distinct_volumes = [x.encode('UTF8') for x in volume_list]
    for date_va in date_list:
        #below code for product,wpf graphs
        for vol_type in volume_list:
            date_pattern = '*{0}_{1}'.format(vol_type,date_va)
            key_list = conn.keys(pattern=date_pattern)
            if not key_list:
                if date_values.has_key(vol_type):
                    date_values[vol_type].append(0)
                else:
                    date_values[vol_type] = [0]
            for cur_key in key_list:
                var = conn.hgetall(cur_key)
                for key,value in var.iteritems():
                    if date_values.has_key(key):
                        date_values[key].append(int(value))
                    else:
                        date_values[key]=[int(value)]
                volumes_dict['data'] = date_values
                volumes_dict['date'] = date_list
                result['data'] = volumes_dict
    #below code for productivity,wpf graph
    volumes_data = result['data']['data']
    volume_bar_data = {}
    volume_bar_data['volume_type']= volumes_data.keys()
    volume_keys_data ={}
    for key,value in volumes_data.iteritems():
        volume_keys_data[key]= sum(value)
    for vol in distinct_volumes:
        if vol not in volume_keys_data and "DetailFinancial" not in vol:
            volume_keys_data[vol]=0
    volume_bar_data['volume_values'] = volume_keys_data
    result['volumes_data'] = volume_bar_data
    return HttpResponse(result)

from django.db.models import Q

def get_annotations(request):

    series_name = request.GET['series_name']
    chart_name = request.GET.get('chart_name')
    try:
        day_type = request.GET['type']
    except:
        day_type = ''

    if day_type:
        series_name = series_name + '<##>annotation-week'
        annotations = Annotation.objects.filter(key__contains=series_name)
    else:
        annotations = Annotation.objects.filter(Q(key__contains=series_name) & ~Q(key__contains='week') & Q(key__contains=chart_name))

    annotations_data = []

    if annotations:
        for annotation in annotations:

            final_data = {}
            final_data['chart_type_name_id'] = annotation.chart_type_name_id
            final_data['center_id'] = annotation.center_id
            final_data['text'] = annotation.text
            final_data['epoch'] = annotation.epoch
            final_data['dt_created'] = str(annotation.dt_created)
            final_data['key'] = annotation.key
            final_data['created_by_id'] = annotation.created_by_id
            final_data['project_id'] = annotation.project_id
            final_data['id'] = annotation.key.split('<##>')[1]

            annotations_data.append(final_data)

    return HttpResponse(annotations_data)

def add_annotation(request):

    anno_id = request.POST.get('id')
    epoch = request.POST.get("epoch")
    text = request.POST.get("text")
    graph_name = request.POST.get("graph_name")
    series_name = request.POST.get("series_name")
    key = request.POST.get("series_name")
    key = key + '<##>' + anno_id
    widget_name = request.POST.get("widget_name")
    created_by = request.user
    dt_created = datetime.datetime.now()
    prj_obj = Project.objects.filter(name='Probe')
    center = Center.objects.filter(name='Salem')
    if '<##>' in graph_name:
        widget_obj = Widgets.objects.filter(config_name=graph_name.split('<##>')[0])[0]
    else:
        widget_obj = Widgets.objects.filter(config_name=graph_name)[0]
    #widget_obj = Widgets.objects.filter(config_name=graph_name)[0]
    annotation = Annotation.objects.create(epoch=epoch, text=text, key=key, project=prj_obj[0],\
                                            dt_created=dt_created, created_by=created_by,\
                                            center=center[0], chart_type_name=widget_obj.chart_type_name)


    if not graph_name:
        graph_name = 'sss'
    if not series_name:
        series_name = 'wid'
    entity_json = {}

    entity_json['id'] = anno_id
    entity_json['epoch'] = epoch
    entity_json['text'] = text
    entity_json['graph_name'] = graph_name
    entity_json['level_name'] = 12
    entity_json['series_name'] = series_name

    return HttpResponse(entity_json)

def update_annotation(request):
    action = request.POST.get("action", "update")
    epoch = request.POST.get("epoch")
    annotation_id = request.POST.get("id")
    series = request.POST.get('series_name')
    text = request.POST.get("text")
    
    if action == "delete":
        anno = Annotation.objects.filter(key__contains = request.POST['id'])
        if anno:
            anno = anno[0]
            anno.delete()
        return HttpResponse(json.dumps({"status": "success", "message": "deleted successfully"}))

    if series is not None:
        series = series.split('<##>')[0]
        annotation = Annotation.objects.filter(epoch=epoch,created_by=request.user,key__contains=series)
        annotation = annotation[0]
        annotation.text = text
        annotation.save()
        return HttpResponse(json.dumps({"status": "success", "message": "successfully updated"}))

"""
    if not annotation_id:

        return HttpResponse(json.dumps({"status": "error", "message": "Invalid ID"}), "error")

    if not annotation:"""

def dropdown_data_types(request):
    project = request.GET['project'].split('-')[0].strip()
    center_id = request.GET['center'].split('-')[0].strip()
    center = Center.objects.filter(name=center_id).values_list('id', flat=True)
    prj_id = Project.objects.filter(name=project).values_list('id', flat=True)
    result = {} 
    sub_project = RawTable.objects.filter(project_id=prj_id[0],center_id = center[0]).values_list('sub_project',flat=True).distinct()
    sub_project = filter(None, sub_project)
    print 'dropdown' , sub_project
    work_packet = RawTable.objects.filter(project_id=prj_id[0],center_id = center[0]).values_list('work_packet',flat=True).distinct()
    work_packet = filter(None, work_packet)
    print 'dropdown' , work_packet
    sub_packet = RawTable.objects.filter(project_id=prj_id[0], center_id=center[0]).values_list('sub_packet',flat=True).distinct()
    sub_packet = filter(None, sub_packet)
    result['sub_project'] = 0
    if len(sub_project) > 0: 
        result['sub_project'] = 1
    result['work_packet'] = 0
    if len(work_packet) > 0: 
        result['work_packet'] = 1
    result['sub_packet'] = 0
    if len(sub_packet) > 0: 
        result['sub_packet'] = 1
    return HttpResponse(result)

