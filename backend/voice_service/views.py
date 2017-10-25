from django.shortcuts import render
import xlrd
import datetime
from django.apps import apps
from api.models import *
from api.redis_operations import redis_insert
from api.basics import *
from api.uploads import *
from api.utils import *
from api.query_generations import *
from voice_service.voice_query_insertion import *
from xlrd import open_workbook
from api.commons import data_dict
from common.utils import getHttpResponse as json_HttpResponse

def voice_upload(request, prj_obj, center_obj, open_book):
    excel_sheet_names = open_book.sheet_names()
    file_sheet_names = Authoringtable.objects.filter(project=prj_obj,center=center_obj).values_list('sheet_name',flat=True).distinct()
    sheet_names, raw_table_mapping, internal_error_mapping, external_error_mapping, worktrack_mapping, headcount_mapping, \
    target_mapping, authoring_dates, inbound_hourly_mapping, outbound_hourly_mapping, inbound_daily_mapping, \
    outbound_daily_mapping = {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}
    ignorablable_fields, other_fileds = [], []
    mapping_ignores = ['project_id','center_id','_state','sheet_name','id','total_errors_require', 'updated_at', 'created_at']
    """
    raw_table_map_query = Authoring_mapping(prj_obj,center_obj,'RawtableAuthoring')
    for map_key,map_value in raw_table_map_query.iteritems():
        if map_key == 'sheet_name':
            sheet_names['raw_table_sheet'] = map_value
        if map_value != '' and map_key not in mapping_ignores:
            if map_key == 'ignorable_fileds':
                ignorablable_fields = map_value.split('#<>#')
            else:
                raw_table_mapping[map_key]= map_value.lower()
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
            if map_key == 'date':
                authoring_dates['extr_error_date'] = map_value.lower()

    worktrack_map_query = Authoring_mapping(prj_obj,center_obj,'WorktrackAuthoring')
    for map_key,map_value in worktrack_map_query.iteritems():
        if map_key == 'sheet_name':
            sheet_names['worktrack_sheet'] = map_value
        if map_value != '' and map_key not in mapping_ignores:
            worktrack_mapping[map_key]= map_value.lower()
            if map_key == 'date':
                authoring_dates['worktrack_date'] = map_value.lower()

    target_map_query = Authoring_mapping(prj_obj, center_obj, 'TargetsAuthoring')
    for map_key, map_value in target_map_query.iteritems():
        if map_key == 'sheet_name':
            sheet_names['target_sheet'] = map_value
        if map_value != '' and map_key not in mapping_ignores:
            target_mapping[map_key] = map_value.lower()
            if map_key in ['from_date','to_date']:
                if map_key == 'from_date':
                    authoring_dates['target_from_date'] = map_value.lower()
                else:
                    authoring_dates['target_to_date'] = map_value.lower()

    headcount_map_query = Authoring_mapping(prj_obj,center_obj,'HeadcountAuthoring')
    for map_key, map_value in headcount_map_query.iteritems():
        if map_key == 'sheet_name':
            sheet_names['headcount_sheet'] = map_value
        if map_value != '' and map_key not in mapping_ignores:
            headcount_mapping[map_key] = map_value.lower()
            if map_key == 'date':
                authoring_dates['headcount_date'] = map_value.lower()
    """
    inbound_hourly_map_query = Authoring_mapping(prj_obj,center_obj, 'InboundHourlyCallAuthoring', 'voice_service')
    for map_key, map_value in inbound_hourly_map_query.iteritems():
        if map_key == 'sheet_name':
            sheet_names['inbound_hourly_sheet'] = map_value
        if map_value != '' and map_key not in mapping_ignores:
            inbound_hourly_mapping[map_key] = map_value.lower()
            if map_key == 'call_date':
                authoring_dates['inbound_hourly_date'] = map_value.lower()

    outbound_hourly_map_query = Authoring_mapping(prj_obj,center_obj, 'OutboundHourlyCallAuthoring', 'voice_service')
    for map_key, map_value in outbound_hourly_map_query.iteritems():
        if map_key == 'sheet_name':
            sheet_names['outbound_hourly_sheet'] = map_value
        if map_value != '' and map_key not in mapping_ignores:
            outbound_hourly_mapping[map_key] = map_value.lower()
            if map_key == 'call_date':
                authoring_dates['outbound_hourly_date'] = map_value.lower()

    inbound_daily_map_query = Authoring_mapping(prj_obj,center_obj, 'InboundDailyAuthoring', 'voice_service')
    for map_key, map_value in inbound_daily_map_query.iteritems():
        if map_key == 'sheet_name':
            sheet_names['inbound_daily_sheet'] = map_value
        if map_value != '' and map_key not in mapping_ignores:
            inbound_daily_mapping[map_key] = map_value.lower()
            if map_key == 'call_date':
                authoring_dates['inbound_daily_date'] = map_value.lower()
    
    outbound_daily_map_query = Authoring_mapping(prj_obj,center_obj, 'OutboundDailyAuthoring', 'voice_service')
    for map_key, map_value in outbound_daily_map_query.iteritems():
        if map_key == 'sheet_name':
            sheet_names['outbound_daily_sheet'] = map_value
        if map_value != '' and map_key not in mapping_ignores:
            outbound_daily_mapping[map_key] = map_value.lower()
            if map_key == 'call_date':
                authoring_dates['outbound_daily_date'] = map_value.lower()

    other_fileds = filter(None, other_fileds)
    file_sheet_names = sheet_names.values()
    sheet_index_dict = {}
    for sh_name in file_sheet_names:
        if sh_name in excel_sheet_names:
            sheet_index_dict[sh_name] = open_book.sheet_names().index(sh_name)
    db_check = str(Project.objects.filter(name=prj_obj,center=center_obj).values_list('project_db_handling',flat=True))
    raw_table_dataset, internal_error_dataset, external_error_dataset, work_track_dataset,headcount_dataset = {}, {}, {}, {},{}
    target_dataset, inbound_hourly_dataset, inbound_daily_dataset, outbound_hourly_dataset, outbound_daily_dataset = {}, {}, {}, {}, {}

    for key,value in sheet_index_dict.iteritems():
        one_sheet_data, mapping_table = {}, {}
        prod_date_list,internal_date_list,external_date_list,main_headers = [],[],[],[]
        open_sheet = open_book.sheet_by_index(value)
        SOH_XL_HEADERS = open_sheet.row_values(0)
        SOH_XL_MAN_HEADERS = [x.title() for x in main_headers]
        sheet_headers = validate_sheet(open_sheet,request,SOH_XL_HEADERS,SOH_XL_MAN_HEADERS)
        for row_idx in xrange(1, open_sheet.nrows):
            customer_data = {}
            for column, col_idx in sheet_headers:
                cell_data = get_cell_data(open_sheet, row_idx, col_idx)
                if column in authoring_dates.values():
                    cell_data = xlrd.xldate_as_tuple(int(cell_data.split('.')[0]), 0)
                    cell_data = '%s-%s-%s' % (cell_data[0], cell_data[1], cell_data[2])
                    customer_data[column] = ''.join(cell_data)
                elif column != "date" or "call_date":
                    customer_data[column] = ''.join(cell_data)

            if key == sheet_names['raw_table_sheet']:
                date_name = authoring_dates['raw_table_date']
                if not raw_table_dataset.has_key(customer_data[date_name]):
                    raw_table_dataset[str(customer_data[date_name])]={}
                local_raw_data = {}
                for raw_key,raw_value in raw_table_mapping.iteritems():
                    local_raw_data[raw_key] = customer_data[raw_value]
                    emp_key = '{0}_{1}_{2}_{3}'.format(local_raw_data.get('sub_project', 'NA'),
                                                       local_raw_data.get('work_packet', 'NA'),
                                                       local_raw_data.get('sub_packet', 'NA'),
                                                       local_raw_data.get('employee_id', 'NA'))

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
                                            raw_table_dataset[str(customer_data[date_name])][emp_key][pdct_key] = pdct_value+dataset_value
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
                        if (raw_key== 'error_category') or (raw_key== 'error_count') or (raw_key== 'type_error'):
                            if raw_key== 'type_error':
                                if customer_data.get(internal_error_mapping['type_error']) != '':
                                     error_name = customer_data[internal_error_mapping['type_error']]
                                     error_count = customer_data[internal_error_mapping['error_count']]
                                     if error_count == '':
                                         error_count = 0
                                     local_internalerror_data['sub_errors']={}
                                     type_key = customer_data[raw_value].replace(' ','_') +'_' + customer_data['error category'].replace(' ','_')
                                     local_internalerror_data['sub_errors'][type_key] = error_count
                                else:
                                    local_internalerror_data['sub_errors']={}
                                    local_internalerror_data['sub_errors']['no_data']='no_data'
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
                            if (local_internalerror_data.has_key('individual_errors') and internal_error_dataset[str(customer_data[date_name])][emp_key].has_key('individual_errors')) or (local_internalerror_data.has_key('sub_errors') and internal_error_dataset[str(customer_data[date_name])][emp_key].has_key('sub_errors')):
                                individual_errors = local_internalerror_data['individual_errors']
                                sub_errors = local_internalerror_data['sub_errors']
                                individual_errors.update(internal_error_dataset[str(customer_data[date_name])][emp_key]['individual_errors'])
                                sub_errors.update(internal_error_dataset[str(customer_data[date_name])][emp_key]['sub_errors'])
                                internal_error_dataset[str(customer_data[date_name])][emp_key]['individual_errors'] = local_internalerror_data['individual_errors']
                                internal_error_dataset[str(customer_data[date_name])][emp_key]['sub_errors'] = local_internalerror_data['sub_errors']
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
                        if (raw_key== 'error_category') or (raw_key== 'error_count') or (raw_key== 'type_error'):
                            if raw_key== 'type_error':
                                if customer_data.get(internal_error_mapping['type_error']) != '':
                                    error_count = customer_data[external_error_mapping['error_count']]
                                    if error_count == '':
                                        error_count = 0
                                    local_externalerror_data['sub_errors']={}
                                    type_key = customer_data[raw_value].replace(' ','_') +'_' + customer_data['error category'].replace(' ','_')
                                    local_externalerror_data['sub_errors'][type_key] = error_count
                                else:
                                    local_externalerror_data['sub_errors']={}
                                    local_externalerror_data['sub_errors']['no_data']='no_data'
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
                            if (local_externalerror_data.has_key('individual_errors') and external_error_dataset[str(customer_data[date_name])][emp_key].has_key('individual_errors')) or (local_externalerror_data.has_key('sub_errors') and external_error_dataset[str(customer_data[date_name])][emp_key].has_key('sub_errors')):
                                individual_errors = local_externalerror_data['individual_errors']
                                sub_errors = local_externalerror_data['sub_errors']
                                individual_errors.update(external_error_dataset[str(customer_data[date_name])][emp_key]['individual_errors'])
                                sub_errors.update(external_error_dataset[str(customer_data[date_name])][emp_key]['sub_errors'])
                                external_error_dataset[str(customer_data[date_name])][emp_key]['individual_errors'] = local_externalerror_data['individual_errors']
                                external_error_dataset[str(customer_data[date_name])][emp_key]['sub_errors'] = local_externalerror_data['sub_errors']
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
                                                work_track_dataset[str(customer_data[date_name])][emp_key][extr_key] = extr_value+dataset_value
                                            elif db_check == 'update':
                                                work_track_dataset[str(customer_data[date_name])][emp_key][extr_key] = extr_value
                            else:
                                work_track_dataset[str(customer_data[date_name])][emp_key] = local_worktrack_data

            if key == sheet_names.get('headcount_sheet', ''):
                date_name = authoring_dates['headcount_date']
                if not headcount_dataset.has_key(customer_data[date_name]):
                    headcount_dataset[str(customer_data[date_name])] = {}
                local_headcount_data = {}
                for raw_key, raw_value in headcount_mapping.iteritems():
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
                                            headcount_dataset[str(customer_data[date_name])][emp_key][extr_key] = extr_value+dataset_value
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
                    if ('#<>#' not in raw_value) and (raw_value in customer_data.keys()):
                        local_target_data[raw_key] = customer_data[raw_value]
                emp_key = '{0}_{1}_{2}_{3}_{4}'.format(local_target_data.get('sub_project', 'NA'),
                                                       local_target_data.get('work_packet', 'NA'),
                                                       local_target_data.get('sub_packet', 'NA'),
                                                       local_target_data.get('employee_id', 'NA'),
                                                       local_target_data.get('target_type', 'NA'))
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

            if key == sheet_names.get('inbound_hourly_sheet', ''):
                date_name = authoring_dates['inbound_hourly_date']
                if not inbound_hourly_dataset.has_key(customer_data[date_name]):
                    inbound_hourly_dataset[str(customer_data[date_name])] = {}
                local_inbound_hourly = {}
                for key, value in inbound_hourly_mapping.iteritems():
                    local_inbound_hourly[key] = customer_data[value]
                emp_key = '{0}_{1}_{2}'.format(local_inbound_hourly.get('sub_project', 'NA'),
                                               local_inbound_hourly.get('work_packet', 'NA'),
                                               local_inbound_hourly.get('sub_packet', 'NA'))
                if inbound_hourly_dataset.has_key(str(customer_data[date_name])):
                    if inbound_hourly_dataset[str(customer_data[date_name])].has_key(emp_key):
                        for key, value in local_inbound_hourly.iteritems():
                            if key not in inbound_hourly_dataset[str(customer_data[date_name])][emp_key].keys():
                                inbound_hourly_dataset[str(customer_data[date_name])][emp_key][key] = value
                    else:
                        inbound_hourly_dataset[str(customer_data[date_name])][emp_key] = local_inbound_hourly
            
            if key == sheet_names.get('outbound_hourly_sheet', ''):
                date_name = authoring_dates['outbound_hourly_date']
                if not outbound_hourly_dataset.has_key(customer_data[date_name]):
                    outbound_hourly_dataset[str(customer_data[date_name])] = {}
                local_outbound_hourly = {}
                for key, value in outbound_hourly_mapping.iteritems():
                    local_outbound_hourly[key] = customer_data[value] 
                emp_key = '{0}_{1}_{2}'.format(local_outbound_hourly.get('sub_project', 'NA'),
                                               local_outbound_hourly.get('work_packet', 'NA'),
                                               local_outbound_hourly.get('sub_packet', 'NA'))
                if outbound_hourly_dataset.has_key(str(customer_data[date_name])):
                    if outbound_hourly_dataset[str(customer_data[date_name])].has_key(emp_key):
                        for key, value in local_outbound_hourly.iteritems():
                            if key not in outbound_hourly_dataset[str(customer_data[date_name])][emp_key].keys():
                                outbound_hourly_dataset[str(customer_data[date_name])][emp_key][key] = value
                    else:   
                        outbound_hourly_dataset[str(customer_data[date_name])][emp_key] = local_outbound_hourly

            if key == sheet_names.get('inbound_daily_sheet', ''):
                date_name = authoring_dates['inbound_daily_date']
                if not inbound_daily_dataset.has_key(customer_data[date_name]):
                    inbound_daily_dataset[str(customer_data[date_name])] = {}
                local_inbound_daily = {}
                for key, value in inbound_daily_mapping.iteritems():
                    local_inbound_daily[key] = customer_data[value] 
                emp_key = '{0}_{1}_{2}'.format(local_inbound_daily.get('sub_project', 'NA'),
                                               local_inbound_daily.get('work_packet', 'NA'),
                                               local_inbound_daily.get('sub_packet', 'NA'))
                if inbound_daily_dataset.has_key(str(customer_data[date_name])):
                    if inbound_daily_dataset[str(customer_data[date_name])].has_key(emp_key):
                        for key, value in local_inbound_daily.iteritems():
                            if key not in inbound_daily_dataset[str(customer_data[date_name])][emp_key].keys():
                                inbound_daily_dataset[str(customer_data[date_name])][emp_key][key] = value
                    else:   
                        inbound_daily_dataset[str(customer_data[date_name])][emp_key] = local_inbound_daily

            if key == sheet_names.get('outbound_daily_sheet', ''):
                date_name = authoring_dates['outbound_daily_date']
                if not outbound_daily_dataset.has_key(customer_data[date_name]):
                    outbound_daily_dataset[str(customer_data[date_name])] = {}
                local_outbound_daily = {}
                for key, value in outbound_daily_mapping.iteritems():
                    local_outbound_daily[key] = customer_data[value] 
                emp_key = '{0}_{1}_{2}'.format(local_outbound_daily.get('sub_project', 'NA'),
                                               local_outbound_daily.get('work_packet', 'NA'),
                                               local_outbound_daily.get('sub_packet', 'NA'))
                if outbound_daily_dataset.has_key(str(customer_data[date_name])):
                    if outbound_daily_dataset[str(customer_data[date_name])].has_key(emp_key):
                        for key, value in local_outbound_daily.iteritems():
                            if key not in outbound_daily_dataset[str(customer_data[date_name])][emp_key].keys():
                                outbound_daily_dataset[str(customer_data[date_name])][emp_key][key] = value
                    else:
                        outbound_daily_dataset[str(customer_data[date_name])][emp_key] = local_outbound_daily

    for date_key,date_value in internal_error_dataset.iteritems():
        for emp_key,emp_value in date_value.iteritems():
            emp_data = Error_checking(emp_value,intrnl_error_check)
            internalerror_insert = internalerror_query_insertion(emp_data, prj_obj, center_obj,teamleader_obj_name,db_check)

    for date_key,date_value in external_error_dataset.iteritems():
        for emp_key,emp_value in date_value.iteritems():
            emp_data = Error_checking(emp_value,extrnl_error_check)
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

    for date_key,date_value in raw_table_dataset.iteritems():
        for emp_key,emp_value in date_value.iteritems():
            try:
                per_day_value = int(float(emp_value.get('per_day', '')))
            except:
                per_day_value = 0
            raw_table_insert = raw_table_query_insertion(emp_value, prj_obj, center_obj, teamleader_obj_name,per_day_value, db_check)
    
    for voice_key, voice_value in inbound_hourly_dataset.iteritems():
        for key, value in voice_value.iteritems():
            inbound_hourly_insert = inbound_hourly_query_insertion(emp_value, prj_obj, center_obj, teamleader_obj_name)

    for voice_key, voice_value in outbound_hourly_dataset.iteritems():
        for key, value in voice_value.iteritems():
            outbound_hourly_insert = outbound_hourly_query_insertion(emp_value, prj_obj, center_obj, teamleader_obj_name)

    for voice_key, voice_value in inbound_daily_dataset.iteritems():
        for key, value in voice_value.iteritems():
            inbound_daily_insert = inbound_daily_query_insertion(emp_value, prj_obj, center_obj, teamleader_obj_name)

    for voice_key, voice_value in outbound_daily_dataset.iteritems():
        for key, value in voice_value.iteritems():
            outbound_daily_insert = outbound_daily_query_insertion(emp_value, prj_obj, center_obj, teamleader_obj_name)
    
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

