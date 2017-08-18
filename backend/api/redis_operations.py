
import redis
from django.db.models import Sum
from api.models import *
from api.basics import *
from common.utils import getHttpResponse as json_HttpResponse

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
            single_row_dict, query_set = {}, {}
            query_set['date'] = date
            query_set['project'] = prj_obj
            query_set['center'] = center_obj
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
                type_errors = Internalerrors.objects.filter(**query_set).values('type_error','sub_error_count')
                total_error_types = different_error_type(error_types)
                total_type_errors = different_sub_error_type(type_errors)
                value_dict['total_audit'] = str(total_audit['audited_errors__sum'])
                value_dict['total_errors'] = str(total_errors['total_errors__sum'])
                value_dict['sub_error_types'] = json.dumps(total_type_errors)
                value_dict['types_of_errors'] = json.dumps(total_error_types)
                data_dict[redis_key] = value_dict
            if key_type == 'External':
                redis_key = '{0}_{1}_{2}_{3}_externalerror'.format(prj_name,center_name,final_work_packet,str(date_is))
                total_audit = Externalerrors.objects.filter(**query_set).values_list('audited_errors').aggregate(Sum('audited_errors'))
                total_errors = Externalerrors.objects.filter(**query_set).values_list('total_errors').aggregate(Sum('total_errors'))
                error_types = Externalerrors.objects.filter(**query_set).values('error_types', 'error_values')
                type_errors = Externalerrors.objects.filter(**query_set).values('type_error','sub_error_count')
                total_type_errors = different_sub_error_type(type_errors)
                total_error_types = different_error_type(error_types)
                value_dict['total_audit'] = str(total_audit['audited_errors__sum'])
                value_dict['total_errors'] = str(total_errors['total_errors__sum'])
                value_dict['types_of_errors'] = json.dumps(total_error_types)
                value_dict['sub_error_types'] = json.dumps(total_type_errors)
                data_dict[redis_key] = value_dict
            if key_type == 'WorkTrack':
                redis_key = '{0}_{1}_{2}_{3}_worktrack'.format(prj_name, center_name, final_work_packet,str(date_is))
                closing_balance = Worktrack.objects.filter(**query_set).values_list('closing_balance').aggregate(Sum('closing_balance'))
                received = Worktrack.objects.filter(**query_set).values_list('received').aggregate(Sum('received'))
                completed = Worktrack.objects.filter(**query_set).values_list('completed').aggregate(Sum('completed'))
                opening = Worktrack.objects.filter(**query_set).values_list('opening').aggregate(Sum('opening'))
                non_workable_count = Worktrack.objects.filter(**query_set).values_list('non_workable_count').aggregate(Sum('non_workable_count'))
                try:
                    value_dict['closing_balance'] = str(closing_balance['closing_balance__sum'])
                except:
                    value_dict['closing_balance'] = ''
                try:
                    value_dict['completed'] = str(completed['completed__sum'])
                except:
                    value_dict['completed'] = ''
                try:
                    value_dict['opening'] = str(opening['opening__sum'])
                except:
                    value_dict['opening'] = ''
                try:
                    value_dict['non_workable_count'] = str(non_workable_count['non_workable_count__sum'])
                except:
                    value_dict['non_workable_count'] = ''
                try:
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
