
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
from collections import OrderedDict
from api.models import *
from voice_service.models import *
from common.utils import getHttpResponse as json_HttpResponse
from django.core.mail import EmailMessage


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
        user_name = user_obj[0].first_name +' '+user_obj[0].last_name
        auth_key = hashlib.sha1(str(random.random())).hexdigest()[:5]
        user_data = Profile()
        user_data.user_id = user_id
        user_data.activation_key = auth_key
        user_data.save()
        return user_id,auth_key,user_name
    else:
        return 'Email id not found',0 ,0


def forgot_password(request):
    email_id = request.GET['email']
    user_id, auth_key,user_name = get_details(email_id)    
    var = 'http://nextpulse.nextwealth.in/#!/reset/'+str(user_id)+'/'+str(auth_key)    
    if auth_key:
        _data = "Hi %s, <p>Click the following link to reset your password.   %s</p>"\
                    % (user_name, var)        
        mail_logos = generate_logos_format()
        mail_body = _data + mail_logos
        to = [email_id]
        msg = EmailMessage("Reset Password", mail_body, 'nextpulse@nextwealth.in', to)
        msg.content_subtype = "html"
        msg.send()
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
            cell_data = re.sub(r'[^\x00-\x7F]+',' ', cell_data)
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
        sub_pro_level = filter(None,RawTable.objects.filter(project=pro_cen_mapping[0][0], center=pro_cen_mapping[1][0])\
                        .values_list('sub_project',flat=True).distinct())
        if len(sub_pro_level)>= 1:
            level_structure_key['sub_project'] = "All"
        if not level_structure_key:
            work_pac_level = filter(None,RawTable.objects.filter(project=pro_cen_mapping[0][0], center=pro_cen_mapping[1][0])\
                                .values_list('work_packet',flat=True).distinct())
            if len(work_pac_level)>=1:
                level_structure_key['work_packet'] = "All"
        if not level_structure_key:
            sub_pac_level = filter(None,RawTable.objects.filter(project=pro_cen_mapping[0][0], center=pro_cen_mapping[1][0])\
                            .values_list('sub_packet',flat=True).distinct())
            if len(sub_pac_level)>=1:
                level_structure_key['sub_packet'] = "All"
    return level_structure_key


def latest_dates(request,prj_id):
    result= {}
    req_from_date = request.GET.get('from', '')
    req_last_date = request.GET.get('to', '')
    if len(prj_id) == 1:
        project_check = Project.objects.filter(id=prj_id).values_list('is_voice',flat=True).distinct()[0]
        proj_check = Project.objects.filter(id=prj_id).values_list('is_hourly_dashboard',flat=True).distinct()[0]
        if project_check == True:
            latest_date = InboundHourlyCall.objects.filter(project=prj_id).all().aggregate(Max('date'))
            to_date = latest_date['date__max']
        elif proj_check == True:
            latest_date = live_transaction_table.objects.filter(project=prj_id).aggregate(Max('start_time'))
            to_date = datetime.date.today()
        else:
            latest_date = RawTable.objects.filter(project=prj_id).all().aggregate(Max('date'))
            to_date = latest_date['date__max']
           
        if to_date and ((req_from_date == '') or (req_from_date == 'undefined')) and proj_check == False:
            from_date = to_date - timedelta(6)
            result['from_date'] = str(from_date)
            result['to_date'] = str(to_date)
        elif proj_check == True:
            from_date = to_date - timedelta(6)
            result['from_date'] = str(from_date)
            result['to_date'] = str(to_date)
        elif req_from_date:
            result['from_date'] = str(req_from_date)
            result['to_date'] = str(req_last_date)
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
    teamleader_obj = TeamLead.objects.filter(name_id=request.user.id).values_list('project','center')[0]
    prj_obj = Project.objects.filter(id=teamleader_obj[0])[0]
    center = TeamLead.objects.filter(name_id=request.user.id).values_list('center',flat=True)[0]
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


def upload_target_data(date_list, prj_id, center):
    result_data = []
    final_result = {}
    final_data = []
    dates = generate_dates(date_list, prj_id, center)
    for date in dates:
        upload_query = UploadDataTable.objects.filter(project=prj_id,center=center,date=date)
        target = upload_query.aggregate(Sum('target'))
        upload = upload_query.aggregate(Sum('upload'))
        if target['target__sum'] > 0 and upload['upload__sum'] > 0:
            percentage = (float(upload['upload__sum'])/float(target['target__sum'])) * 100
            final_percentage = (float('%.2f' % round(percentage, 2)))
        else:
            final_percentage = 0
        final_data.append(final_percentage)
    final_result['data'] = final_data
    return final_result


def dropdown_data_types(request):
    project = request.GET['project'].split('-')[0].strip()
    center_id = request.GET['center'].split('-')[0].strip()
    center = Center.objects.filter(name=center_id).values_list('id', flat=True)
    prj_id = Project.objects.filter(name=project).values_list('id', flat=True)
    result = {}
    packet_query = RawTable.objects.filter(project_id=prj_id[0],center_id = center[0])
    sub_project = packet_query.values_list('sub_project',flat=True).distinct()
    sub_project = filter(None, sub_project)
    work_packet = packet_query.values_list('work_packet',flat=True).distinct()
    work_packet = filter(None, work_packet)
    sub_packet = packet_query.values_list('sub_packet',flat=True).distinct()
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


def Authoring_mapping(prj_obj,center_obj,model_name, app_name='api'):
    #print model_name
    table_model = apps.get_model(app_name, model_name)
    map_query = table_model.objects.filter(project=prj_obj, center=center_obj)
    if len(map_query) > 0:
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
    return  final_work_packet


def min_max_value_data(int_value_range):
    main_max_dict = {}
    if len(int_value_range) > 0:
        data_value = []
        if int_value_range.values():
            for i in int_value_range.values():
                for values in i:
                    data_value.append(values)
            if 0.0 in data_value:
                int_min_value = 0
                int_max_value = int(round(max(data_value)+2))
            else:
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

def error_insert(request):
    pass


def pre_scan_exception_data(date_list, prj_id, center, level_structure_key, main_dates,request):

    result_data_value = []
    final_result_dict = {}
    final_result_data, new_date_list = [], []
    dates = generate_dates(date_list, prj_id, center)
    for date in dates:
        final_packet_value = RawTable.objects.filter(project=prj_id,center=center,date=date,work_packet='Scanning')\
                             .aggregate(Sum('per_day'))
        error_count = Incomingerror.objects.filter(project=prj_id,center=center,date=date,work_packet='Scanning')\
                        .aggregate(Sum('error_values'))
        if error_count['error_values__sum'] > 0 and final_packet_value['per_day__sum'] > 0:
            percentage = (float(error_count['error_values__sum'])\
                         /float(error_count['error_values__sum'] + final_packet_value['per_day__sum'])) * 100
            final_percentage_va = (float('%.2f' % round(percentage, 2)))
        else:
            final_percentage_va = 0
        final_result_data.append(final_percentage_va)
    final_result_dict['data'] = final_result_data
    result_data_value.append(final_result_dict)
    return result_data_value


def overall_exception_data(date_list, prj_id, center,level_structure_key, main_dates,request):

    result = {} 
    new_date_list = []
    dates = generate_dates(date_list, prj_id, center)
    for date in dates:
        packets = ['Data Entry', 'KYC Check']
        for packet in packets:
            work_done = RawTable.objects.filter(project=prj_id, center=center, date=date,work_packet = packet)\
                        .aggregate(Sum('per_day'))
            error_value = Incomingerror.objects.filter(\
                            project=prj_id,center=center,date=date,work_packet=packet,sub_packet='Overall Exception')\
                            .aggregate(Sum('error_values'))
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


def nw_exception_data(date_list, prj_id, center,level_structure_key, main_dates,request):

    result = {}
    new_date_list = []
    dates = generate_dates(date_list, prj_id, center)
    packets = ['Data Entry', 'KYC Check']
    for date in dates:
        for packet in packets:
            error_value = Incomingerror.objects.filter(\
                          project=prj_id, center=center, work_packet=packet,sub_packet='NW Exception', date=date)\
                          .aggregate(Sum('error_values'))
            if error_value['error_values__sum'] > 0: 
                value = float(error_value['error_values__sum'])
            else:
                value = 0
            if result.has_key(packet):
                result[packet].append(value)
            else:
                result[packet] = [value]
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


def get_query_parameters(level_structure_key, prj_id, center_obj, date_list):

    _dict = {}
    packet_1 = level_structure_key.get('sub_project', '') 
    packet_2 = level_structure_key.get('work_packet', '') 
    packet_3  = level_structure_key.get('sub_packet', '')

    if (packet_1 != '' and packet_2 != '' and packet_3 != '') or (packet_1 != ''):
        if (packet_1 == 'All' and packet_2 == 'All' and packet_3 == 'All') or (packet_1 == 'All'):
            _dict.update({'project': prj_id, 'center': center_obj, 'date__range': [date_list[0], date_list[-1]]})
        elif packet_1 != 'All' and packet_2 == 'All' and packet_3 == 'All':
            _dict.update({'project': prj_id, 'center': center_obj, 'date__range': [date_list[0], date_list[-1]], 'sub_project': packet_1})
        elif packet_1 != 'All' and packet_2 != 'All' and packet_3 == 'All':
            _dict.update({'project': prj_id, 'center': center_obj, 'date__range': [date_list[0], date_list[-1]], 'sub_project': packet_1,\
                'work_packet': packet_2})
        elif packet_1 != 'All' and packet_2 != 'All' and packet_3 != 'All':
            _dict.update({'project': prj_id, 'center': center_obj, 'date__range': [date_list[0], date_list[-1]], 'sub_project': packet_1,\
                'work_packet': packet_2, 'sub_packet': packet_3})

    elif packet_1 == '' and packet_2 != '' and packet_3 != '': 
        if packet_2 == 'All' and packet_3 == 'All':
            _dict.update({'project': prj_id, 'center': center_obj, 'date__range': [date_list[0], date_list[-1]]})
        elif packet_2 != 'All' and packet_3 == 'All':
            _dict.update({'project': prj_id, 'center': center_obj, 'date__range': [date_list[0], date_list[-1]], 'work_packet': packet_2})
        elif packet_2 != 'All' and packet_3 != 'All':
            _dict.update({'project': prj_id, 'center': center_obj, 'date__range': [date_list[0], date_list[-1]], 'work_packet': packet_2,\
                'sub_packet': packet_3})

    elif packet_1 == '' and packet_2 != '' and packet_3 == '': 
        if packet_2 == 'All':
            _dict.update({'project': prj_id, 'center': center_obj, 'date__range': [date_list[0], date_list[-1]]})
        elif packet_2 != 'All':
            _dict.update({'project': prj_id, 'center': center_obj, 'date__range': [date_list[0], date_list[-1]],\
                'work_packet': packet_2})

    return _dict


def getting_required_params(level_structure_key, prj_id, center_obj, date_list):
    
    query_dict = {}
    packet_1 = level_structure_key.get('sub_project', '')
    packet_2 = level_structure_key.get('work_packet', '')
    packet_3  = level_structure_key.get('sub_packet', '')
    field = ''

    if (packet_1 != '' and packet_2 != '' and packet_3 != '') or (packet_1 != ''):
        if (packet_1 == 'All' and packet_2 == 'All' and packet_3 == 'All') or (packet_1 == 'All'):
            query_dict.update({'project': prj_id, 'center': center_obj, 'date__range': [date_list[0], date_list[-1]]})
            field = 'sub_project'
        elif packet_1 != 'All' and packet_2 == 'All' and packet_3 == 'All':
            query_dict.update({'project': prj_id, 'center': center_obj, 'date__range': [date_list[0], date_list[-1]],\
            'sub_project': packet_1})
            field = 'work_packet'
        elif packet_1 != 'All' and packet_2 != 'All' and packet_3 == 'All':
            query_dict.update({'project': prj_id, 'center': center_obj, 'date__range': [date_list[0], date_list[-1]],\
            'sub_project': packet_1,'work_packet': packet_2})
            field = 'sub_packet'
        elif packet_1 != 'All' and packet_2 != 'All' and packet_3 != 'All':
            query_dict.update({'project': prj_id, 'center': center_obj, 'date__range': [date_list[0], date_list[-1]],\
            'sub_project': packet_1,'work_packet': packet_2, 'sub_packet': packet_3})
            field = 'sub_packet'
        
    elif packet_1 == '' and packet_2 != '' and packet_3 != '':
        if packet_2 == 'All' and packet_3 == 'All':
            query_dict.update({'project': prj_id, 'center': center_obj, 'date__range': [date_list[0], date_list[-1]]})
            field = 'work_packet'
        elif packet_2 != 'All' and packet_3 == 'All':
            query_dict.update({'project': prj_id, 'center': center_obj, 'date__range': [date_list[0], date_list[-1]],\
            'work_packet': packet_2})
            field = 'sub_packet'
        elif packet_2 != 'All' and packet_3 != 'All':
            query_dict.update({'project': prj_id, 'center': center_obj, 'date__range': [date_list[0], date_list[-1]],\
            'work_packet': packet_2,'sub_packet': packet_3})
            field = 'sub_packet'

    elif packet_1 == '' and packet_2 != '' and packet_3 == '':
        if packet_2 == 'All':
            query_dict.update({'project': prj_id, 'center': center_obj, 'date__range': [date_list[0], date_list[-1]]})
            field = 'work_packet'
        elif packet_2 != 'All':
            query_dict.update({'project': prj_id, 'center': center_obj, 'date__range': [date_list[0], date_list[-1]],\
            'work_packet': packet_2})
            field = 'work_packet'
    return query_dict, field


def get_dashboard_opens_with_parameters_data(packet_1, packet_2, packet_3, project, center, date_list):

    query_params_dict = {}
    if (packet_1 != '') and (packet_2 == '') and (packet_3 == ''):
        query_params_dict.update({'project': project, 'center': center, 'date__range': [date_list[0], date_list[-1]], 'sub_project': packet_1})
        query_field = 'work_packet'        
    elif (packet_1 != '') and (packet_2 != '') and (packet_3 != ''):
        query_params_dict.update({'project': project, 'center': center, 'date__range': [date_list[0], date_list[-1]], \
            'sub_project': packet_1, 'work_packet': packet_2})
        query_field = 'sub_packet'
    elif (packet_1 != '') and (packet_2 != '') and (packet_3 != ''):
        query_dict.update({'project': project, 'center': center, 'date__range': [date_list[0], date_list[-1]],\
            'sub_project': packet_1,'work_packet': packet_2, 'sub_packet': packet_3})
        field = 'sub_packet'                
    elif (packet_1 == '') and (packet_2 != '') and (packet_3 == ''):
        query_params_dict.update({'project': project, 'center': center, 'date__range': [date_list[0], date_list[-1]], 'work_packet': packet_2})
        query_field = 'work_packet'
    elif (packet_1 == '') and (packet_2 != '') and (packet_3 != ''):
        query_params_dict.update({'project': project, 'center': center, 'date__range': [date_list[0], date_list[-1]], 'work_packet': packet_2, \
            'sub_packet': packet_3})
        query_field = 'sub_packet'

    return query_params_dict, query_field        
    

def generate_dates(date_list, prj_id, center):

    dates = []
    date_values = RawTable.objects.filter(\
                       project=prj_id, center=center, date__range=[date_list[0], date_list[-1]]).\
                       values_list('date',flat=True).distinct() 
    for date in date_values:
        dates.append(str(date))
    return dates


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

def annotation_check(request):
    
    is_annotation = False
    series_name = request.GET.get('series_name', '')
    chart_ids = request.GET.getlist('chart_name', '')
    project_name = request.GET.get('project', '')
    center_name = request.GET.get('center', '')
    start_date = request.GET.get('from', '')
    end_date = request.GET.get('to', '')
    sub_project = request.GET.get('sub_project', '')
    sub_packet = request.GET.get('sub_packet', '')
    work_packet = request.GET.get('work_packet', '')
    type = request.GET.get('type', '')
    if project_name:
        project_name = project_name.split(' - ')[0];
    if center_name:
        center_name = center_name.split(' -')[0];
    annotations = Annotation.objects.filter(center__name = center_name, project__name = project_name, chart_id__in = chart_ids)
    if len(annotations):
        is_annotation = True
    return is_annotation



def generate_logos_format():

    _text1 = "<html>\
              <body>"
    _text2 = "<p>Thanks and Regards</p>\
            <p>NextPulse Team</p>\
            <p>NextWealth Entrepreneurs Pvt Ltd</p>" 

    logo = "<table class=NormalTable border=0 cellspacing=0 cellpadding=0>\
                <tbody>\
                    <tr>\
                        <td width=450 style=width:337.5px; padding: 0px 0px 0px 0px;>\
                            <div align=center>\
                                <table class=NormalTable border=0 cellspacing=0 cellpadding=0>\
                                    <tbody>\
                                        <tr>\
                                            <td valign=top style=padding: 0px 0px 0px 0px;>\
                                                <p class=MsoNormal>\
                                                    <span>\
                                                        <u></u>\
                                                        <u></u>\
                                                        <u></u>\
                                                    </span>\
                                                </p>\
                                            </td>\
                                            <td>\
                                                <span></span>\
                                            </td>\
                                            <td style=padding:0px 0px 0px 0px;>\
                                                <p class=MsoNoraml>\
                                                    <span>\
                                                        <span style=font-size:1.0pt;>\
                                                            <u></u>\
                                                            <u></u>\
                                                            <u></u>\
                                                        </span>\
                                                    </span>\
                                                </p>\
                                            </td>\
                                            <td>\
                                                <span></span>\
                                            </td>\
                                            <td valign=top style=padding: 0px 0px 0px 0px;>\
                                                <p class=MsoNormal>\
                                                    <span>\
                                                        <u></u>\
                                                        <u></u>\
                                                        <u></u>\
                                                    </span>\
                                                </p>\
                                            </td>\
                                            <td>\
                                                <span></span>\
                                            </td>\
                                        </tr>\
                                        <tr style=height:132.0pt;>\
                                            <td width=130 valign=top style=width:97.5pt;padding:0px 0px 0px 0px;>\
                                                <table class=MsoNormalTable border=0 cellspacing=0 cellpadding=0>\
                                                    <tbody>\
                                                        <tr>\
                                                            <td style=padding:7.5pt 0in 0in 0in;>\
                                                                <p class=MsoNormal>\
                                                                    <span>\
                                                                    </span>\
                                                                    <span style=font-size:10.5pt;font-family:Arial,sans-serif;color:#7f7f7f>\
                                                                    <img width=127 height=81 style=width:1.3229in;height:.8437in src=http://stats.headrun.com/images/nextwealth.png>\
                                                                    <u></u>\
                                                                    <u></u>\
                                                                    </span>\
                                                                </p>\
                                                            </td>\
                                                            <td>\
                                                                <span></span>\
                                                            </td>\
                                                        </tr>\
                                                    </tbody>\
                                                </table>\
                                                <span></span>\
                                            </td>\
                                            <td>\
                                                <span></span>\
                                            </td>\
                                            <td width=10 style=width:7.5pt;padding:0in 0in 0in 0in;height:132.0pt>\
                                                <p class=MsoNormal>\
                                                    <span>\
                                                        <span style=font-size:1.0pt>\
                                                            <u></u>\
                                                            <u></u>\
                                                            <u></u>\
                                                        </span>\
                                                    </span>\
                                                </p>\
                                            </td>\
                                            <td>\
                                                <span></span>\
                                            <td>\
                                            <td width=240 valign=top style=width:2.5in;padding:0in 0in 0in 0in;height:132.0pt>\
                                                <table class=NormalTable border=0 cellspacing=0 cellpadding=0>\
                                                    <tbody>\
                                                        <tr>\
                                                            <td style=padding:7.5pt 0in 0in 0in>\
                                                                <table class=NormalTable border=0 cellspacing=0 cellpadding=0 width=100% style=width:100.0%>\
                                                                    <tbody>\
                                                                        <tr></tr>\
                                                                        <tr>\
                                                                            <td width=7% style=width:7.0%;padding:0in 0in 0in 0in>\
                                                                                <p class=MsoNoraml>\
                                                                                    <span>\
                                                                                        <img width=9 height=18 style=width:.125in;height:.2083in src=http://stats.headrun.com/images/location_new.jpg>\
                                                                                        <u></u>\
                                                                                        <u></u>\
                                                                                    </span>\
                                                                                </p>\
                                                                            </td>\
                                                                            <td>\
                                                                                <span></span>\
                                                                            </td>\
                                                                            <td width=110% style=width:110%;padding:0in 0in 7.5pt 0in>\
                                                                                <p class=MsoNormal>\
                                                                                    <span></span>\
                                                                                    <a href=https://www.google.com/maps?q=728,+6th+B+Cross+Road,+Koramangala,+3rd+Block&entry=gmail&source=g target=_blank>\
                                                                                        <span>\
                                                                                            <span style=font-size:9.0pt;font-family:Arial,sans-serif;> 6th B Cross Road, Koramangala, 3rd Block, Bengaluru - 560034, Karnataka, INDIA\
                                                                                            </span>\
                                                                                        </span>\
                                                                                        <span></span>\
                                                                                    </a>\
                                                                                    <span>\
                                                                                        <span style=font-size:9.0pt;font-family:Arial,sans-serif>\
                                                                                            <u></u>\
                                                                                            <u></u>\
                                                                                        </span>\
                                                                                    </span>\
                                                                                </p>\
                                                                            </td>\
                                                                            <td>\
                                                                                <span></span>\
                                                                            </td>\
                                                                        </tr>\
                                                                        <tr>\
                                                                            <td width=7% style=width:7.0%;padding:0in 0in 0in 0in>\
                                                                                <p class=MsoNoraml>\
                                                                                    <span>\
                                                                                        <img width=9 height=18 style=width:.125in;height:.2083in src=http://stats.headrun.com/images/office_new.jpg>\
                                                                                        <u></u>\
                                                                                        <u></u>\
                                                                                    </span>\
                                                                                </p>\
                                                                            </td>\
                                                                            <td>\
                                                                                <span></span>\
                                                                            </td>\
                                                                            <td width=93% style=width:93.0%;padding:0in 0in 0in 0in;height:15.0pt>\
                                                                                <p class=MsoNormal>\
                                                                                    <span></span>\
                                                                                    <a href=www.nextwealth.in target=_blank>\
                                                                                        <span>\
                                                                                            <span style=font-size:9.0pt;font-family:Arial,sans-serif;>www.nextwealth.in\
                                                                                            </span>\
                                                                                        </span>\
                                                                                        <span></span>\
                                                                                    </a>\
                                                                                    <span>\
                                                                                        <span style=font-size:9.0pt;font-family:Arial,sans-serif>\
                                                                                            <u></u>\
                                                                                            <u></u>\
                                                                                        </span>\
                                                                                    </span>\
                                                                                </p>\
                                                                            </td>\
                                                                            <td>\
                                                                                <span></span>\
                                                                            </td>\
                                                                        </tr>\
                                                                    </tbody>\
                                                                </table>\
                                                                <span></span>\
                                                                <p class=MsoNormal>\
                                                                    <span>\
                                                                        <u></u>\
                                                                        <u></u>\
                                                                    </span>\
                                                                </p>\
                                                            </td>\
                                                            <td>\
                                                                <span></span>\
                                                            </td>\
                                                        </tr>\
                                                    </tbody>\
                                                </table>\
                                                <span></span>\
                                            </td>\
                                            <td>\
                                                <span></span>\
                                            </td>\
                                        </tr>\
                                    </tbody>\
                                </table>\
                            </div>\
                            <span></span>\
                        </td>\
                        <td>\
                            <span></span>\
                        </td>\
                    </tr>\
                    <tr>\
                        <td style=background:#f7f7f7;padding:0in 0in 0in 0in>\
                            <div align=center>\
                                <table class=MsoNormalTable border=0 cellpadding=0>\
                                    <tbody>\
                                        <tr>\
                                            <td style=padding:.75pt .75pt .75pt 7.5pt>\
                                                <p class=MsoNormal>\
                                                    <span></span>\
                                                    <a href=https://www.facebook.com/NextWealth/ target=_blank>\
                                                        <span>\
                                                            <span style=text-decoration:none>\
                                                                <img border=0 width=20 height=27 style=width:.2083in;height:.2812in src=http://stats.headrun.com/images/facebook.png>\
                                                            </span>\
                                                        </span>\
                                                        <span></span>\
                                                    </a>\
                                                    <span>\
                                                        <u></u>\
                                                        <u></u>\
                                                    </span>\
                                                </p>\
                                            </td>\
                                            <td></td>\
                                            <td style=padding:.75pt .75pt .75pt 7.5pt>\
                                                <p class=MsoNormal>\
                                                    <span></span>\
                                                    <a href=https://twitter.com/NextWealth target=_blank>\
                                                        <span>\
                                                            <span style=text-decoration:none>\
                                                                <img border=0 width=20 height=27 style=width:.2083in;height:.2812in src=http://stats.headrun.com/images/twitter.png>\
                                                            </span>\
                                                        </span>\
                                                        <span></span>\
                                                    </a>\
                                                    <span>\
                                                        <u></u>\
                                                        <u></u>\
                                                    </span>\
                                                </p>\
                                            </td>\
                                            <td></td>\
                                            <td style=padding:.75pt .75pt .75pt 7.5pt>\
                                                <p class=MsoNormal>\
                                                    <span></span>\
                                                    <a href=https://www.linkedin.com/company-beta/3512470/?pathWildcard=3512470 target=_blank>\
                                                        <span>\
                                                            <span style=text-decoration:none>\
                                                                <img border=0 width=20 height=27 style=width:.2083in;height:.2812in src=http://stats.headrun.com/images/linkedin.png>\
                                                            </span>\
                                                        </span>\
                                                        <span></span>\
                                                    </a>\
                                                    <span>\
                                                        <u></u>\
                                                        <u></u>\
                                                    </span>\
                                                </p>\
                                            </td>\
                                            <td></td>\
                                        </tr>\
                                    </tbody>\
                                </table>\
                            </div>\
                            <span></span>\
                        </td>\
                        <td>\
                            <span></span>\
                        </td>\
                    </tr>\
                </tbody>\
            </table><br>\
            </body>\
            </html>"

    urls = "<div class=row>\
                <span>\
                    <a href=%s>\
                        <img id=fb_icon, src=http://stats.headrun.com/images/facebook.png\
                        alt=facebook_logo />\
                    </a>\
                </span>\
                <span>\
                    <a href=%s>\
                        <img id=tw_icon, src=http://stats.headrun.com/images/twitter.png\
                        alt=twitter_logo />\
                    </a>\
                </span>\
                <span>\
                    <a href=%s>\
                        <img id=li_icon, src=http://stats.headrun.com/images/linkedin.png\
                        alt=linkedin_logo />\
                    </a>\
                </span>\
            </div>\
            </body>\
            </html>" %("www.facebook.com/NextWealth/", "twitter.com/NextWealth", \
                    "https://www.linkedin.com/company-beta/3512470/?pathWildcard=3512470")
    mail_body = _text1 + _text2 + logo
    return mail_body