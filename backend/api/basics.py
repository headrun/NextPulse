
import hashlib
import json
import random
import re
import datetime
from django.apps import apps
from django.db.models import Sum
from django.db.models import Max
from django.core.mail import send_mail
from datetime import timedelta
from django.utils.encoding import smart_str

from api.models import *
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
    #if "auth_key" in data_to.keys():
    if data_to.has_key('auth_key'):
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
    result['from_date'] = '2017-01-05'
    result['to_date'] = '2017-01-11'
    if len(prj_id) == 1:
        latest_date = RawTable.objects.filter(project=prj_id).all().aggregate(Max('date'))
        to_date = latest_date['date__max']
        if to_date:
            from_date = to_date - timedelta(6)
            result['from_date'] = str(from_date)
            result['to_date'] = str(to_date)    
        
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

    teamleader_objs = TeamLead.objects.filter(name_id=request.user.id)
    if teamleader_objs:
        teamleader_obj = teamleader_objs[0]
        prj_obj = teamleader_obj.project
        center = teamleader_obj.center

    #teamleader_obj = TeamLead.objects.filter(name_id=request.user.id).values_list('project_id','center_id')[0]
    #prj_obj = Project.objects.filter(id=teamleader_obj[0])[0]
    #center = TeamLead.objects.filter(name_id=request.user.id).values_list('center_id',flat=True)[0]
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

"""
def from_too(request):
    return json_HttpResponse('Cool')
"""

def upload_target_data(date_list, prj_id, center):
    result_data = []
    final_result = {}
    final_data = []
    for date in date_list:
        total_done_value = RawTable.objects.filter(project=prj_id, center=center, date=date).aggregate(Max('per_day'))
        if total_done_value['per_day__max'] > 0:
            #target = UploadDataTable.objects.filter(project=prj_id,center=center,date=date).aggregate(Sum('target'))
            #upload = UploadDataTable.objects.filter(project=prj_id,center=center,date=date).aggregate(Sum('upload'))
            _data = UploadDataTable.objects.filter(project=prj_id,center=center,date=date).aggregate(Sum('upload'), Sum('target'))
            if _data['target__sum'] > 0 and _data['upload__sum'] > 0:
                percentage = (float(_data['upload__sum'])/float(_data['target__sum'])) * 100
                final_percentage = (float('%.2f' % round(percentage, 2)))
            else:
                final_percentage = 0
            final_data.append(final_percentage)
    final_result['data'] = final_data
    return final_result


def dropdown_data_types(request):
    project = request.GET['project'].split('-')[0].strip()
    center_id = request.GET['center'].split('-')[0].strip()
    #center = Center.objects.filter(name=center_id).values_list('id', flat=True)
    #prj_id = Project.objects.filter(name=project).values_list('id', flat=True)
    prj = Project.objects.filter(name=project).values_list('id', 'center__id')[0]
    prj_id, center = prj
    result = {}
    sub_project = RawTable.objects.filter(project_id=prj_id,center_id = center).values_list('sub_project',flat=True).distinct()
    sub_project = filter(None, sub_project)
    work_packet = RawTable.objects.filter(project_id=prj_id,center_id = center).values_list('work_packet',flat=True).distinct()
    work_packet = filter(None, work_packet)
    sub_packet = RawTable.objects.filter(project_id=prj_id, center_id=center).values_list('sub_packet',flat=True).distinct()
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
    return json_HttpResponse(result)


def dates_sorting(timestamps):
    dates = [datetime.datetime.strptime(ts, "%Y-%m-%d") for ts in timestamps]
    dates.sort()
    sorted_values = [datetime.datetime.strftime(ts, "%Y-%m-%d") for ts in dates]
    return sorted_values


def Authoring_mapping(prj_obj,center_obj,model_name):
    table_model = apps.get_model('api', model_name)
    map_query = table_model.objects.filter(project=prj_obj, center=center_obj)
    if map_query.count() > 0:
        map_query = map_query[0].__dict__
    else:
        map_query = {}
    return map_query


def previous_sum(volumes_dict):
    new_dict = {}
    for key, value in volumes_dict.iteritems():
        new_dict[key] = []
        for i in xrange(len(value)):
            if i == 0:
                new_dict[key].append(value[i])
            else:
                new_dict[key].append(new_dict[key][i - 1] + value[i])
    return new_dict



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
    return final_work_packet


def min_max_value_data(int_value_range):
    main_max_dict = {}
    if len(int_value_range) > 0:
        data_value = []
        if (min(int_value_range.values()) > 0):
            for i in int_value_range.values():
                for values in i:
                    data_value.append(values)
            int_min_value = int(round(min(data_value)-2))
            int_max_value = int(round(max(data_value)+2))
        else:
            int_min_value = int(round(min(int_value_range.values())))
            int_max_value = int(round(max(int_value_range.values()) + 2))
    else:
        int_min_value, int_max_value = 0, 0
    main_max_dict ['min_value'] = int_min_value
    main_max_dict ['max_value'] = int_max_value
    return main_max_dict


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


def error_insert(request):
    pass


def pre_scan_exception_data(date_list, prj_id, center):
    result_data_value = []
    final_result_dict = {}
    final_result_data = []
    for date_value in date_list:
        total_done_value = RawTable.objects.filter(project=prj_id, center=center, date=date_value).aggregate(Max('per_day'))
        if total_done_value['per_day__max'] > 0:
            #work_packet = RawTable.objects.filter(project=prj_id, center=center, date=date_value).values_list('work_packet',flat=True).distinct()
            final_packet_value = RawTable.objects.filter(project=prj_id, center=center, date=date_value,work_packet='Scanning').aggregate(Sum('per_day'))
            error_count = Incomingerror.objects.filter(project=prj_id, center=center, date=date_value,work_packet='Scanning').aggregate(Sum('error_values'))
            if error_count['error_values__sum'] > 0 and final_packet_value['per_day__sum'] > 0:
                percentage = (float(error_count['error_values__sum'])/float(error_count['error_values__sum'] + final_packet_value['per_day__sum'])) * 100
                final_percentage_va = (float('%.2f' % round(percentage, 2)))
            else:
                final_percentage_va = 0
            final_result_data.append(final_percentage_va)
    final_result_dict['data'] = final_result_data
    result_data_value.append(final_result_dict)
    return result_data_value


def overall_exception_data(date_list, prj_id, center,level_structure_key):
    result = {}
    for date_value in date_list:
        total_done_value = RawTable.objects.filter(project=prj_id, center=center, date=date_value).aggregate(Max('per_day'))
        if total_done_value['per_day__max'] > 0:
            packets = Incomingerror.objects.filter(project=prj_id, center=center, date=date_value).values_list('work_packet',flat =True).distinct()
            for packet in packets:
                if packet == 'Data Entry' or packet =='KYC Check':
                    #sub_packets = Incomingerror.objects.filter(project=prj_id, center=center, date=date_value,work_packet = packet).values_list('sub_packet',flat = True).distinct()
                    work_done = RawTable.objects.filter(project=prj_id, center=center, date=date_value,work_packet = packet).aggregate(Sum('per_day'))
                    error_value = Incomingerror.objects.filter(project=prj_id, center=center, date=date_value,work_packet=packet,sub_packet='Overall Exception').aggregate(Sum('error_values'))
                    if work_done['per_day__sum'] > 0 and error_value['error_values__sum'] > 0:
                        percentage = float(error_value['error_values__sum'])/float(work_done['per_day__sum'])*100
                        percentage = (float('%.2f' % round(percentage, 2)))
                    else:
                        percentage = 0
                    if result.has_key(packet):
                        result[packet].append(percentage)
                    else:
                        result[packet] = [percentage]
    return result


def nw_exception_data(date_list, prj_id, center,level_structure_key):
    result = {}
    for date_value in date_list:
        total_done_value = RawTable.objects.filter(project=prj_id, center=center, date=date_value).aggregate(Max('per_day'))
        if total_done_value['per_day__max'] > 0:
            packets = Incomingerror.objects.filter(project=prj_id, center=center, date=date_value).values_list('work_packet',flat =True).distinct()
            for packet in packets:
                if packet == 'Data Entry' or packet =='KYC Check':
                    #sub_packets = Incomingerror.objects.filter(project=prj_id, center=center,work_packet = packet, date=date_value).values_list('sub_packet',flat = True).distinct()
                    error_value = Incomingerror.objects.filter(project=prj_id, center=center, work_packet=packet,sub_packet='NW Exception', date=date_value).aggregate(Sum('error_values'))
                    if error_value['error_values__sum'] > 0: 
                        percentage = float(error_value['error_values__sum'])
                    else:
                        percentage = 0
                    if result.has_key(packet):
                        result[packet].append(percentage)
                    else:
                        result[packet] = [percentage]
    return result


def fte_wp_total(final_fte):
    work_packet_fte = {}
    work_packet_fte['wp_fte'] = {}
    work_packet_fte['wp_fte'] = [sum(i) for i in zip(*final_fte.values())]
    work_packet_fte['wp_fte'] = [float('%.2f' % round(wp_values, 2)) for wp_values in work_packet_fte['wp_fte']]
    return work_packet_fte


def different_sub_error_type(total_type_errors):
    all_errors = {}
    new_all_errors = {}
    if len(total_type_errors) > 0:
        for error_dict in total_type_errors:
            error_names= error_dict['type_error'].split('#<>#')
            error_values = error_dict['sub_error_count'].split('#<>#')
            for er_key,er_value in zip(error_names,error_values):
                if all_errors.has_key(er_key):
                    all_errors[er_key].append(int(er_value))
                else:
                    if er_key != '':
                        all_errors[er_key] = [int(er_value)]
        for type_error,sub_error_count in all_errors.iteritems():
            try:
                new_all_errors[str(type_error)] = sum(sub_error_count)
            except:
                type_error = smart_str(type_error)
                new_all_errors[type_error] = sum(sub_error_count)
    return new_all_errors


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

    return new_final_dict


def Error_checking(employee_data,error_match=False):
    employee_data['status'] = 'mis_match'
    if employee_data.has_key('individual_errors') or employee_data.has_key('sub_errors'):
        if employee_data['individual_errors'].has_key('no_data'):
           employee_data['status'] = 'matched'
        try:
            total_errors = int(float(employee_data['total_errors']))
        except:
            total_errors = 0

        if employee_data['sub_errors'].has_key('no_data'):
            employee_data['status'] = 'matched'
        try:
            total_errors = int(float(employee_data['total_errors']))
        except:
            total_errors = 0

        all_error_values = []
        sub_error_values = []

        for er_value in employee_data['individual_errors'].values():
            try:
                er_value = int(float(er_value))
            except:
                er_value = 0
            all_error_values.append(er_value)

        for er_value in employee_data['sub_errors'].values():
            try:
                er_value = int(float(er_value))
            except:
                er_value = 0
            sub_error_values.append(er_value)
        if error_match == True:
            if total_errors == sum(sub_error_values):
                sub_error_values = [str(value) for value in sub_error_values]
                employee_data['status'] = 'matched'
                type_error = '#<>#'.join(employee_data['sub_errors'].keys())
                sub_error_count = '#<>#'.join(sub_error_values)
            else:
                employee_data['type_error'] = None
                employee_data['sub_error_count'] = 0

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
            sub_error_values = [str(value) for value in sub_error_values]
            error_types = '#<>#'.join(employee_data['individual_errors'].keys())
            type_error = '#<>#'.join(employee_data['sub_errors'].keys())
            error_values = '#<>#'.join(all_error_values)
            sub_error_count = '#<>#'.join(sub_error_values)
            employee_data['error_types'] = error_types
            employee_data['type_error'] = type_error
            employee_data['sub_error_count'] = sub_error_count
            employee_data['error_values'] = error_values
    return employee_data


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
