
import xlrd
import datetime
from django.apps import apps
from api.models import *
from api.redis_operations import redis_insert
from api.basics import *
from api.utils import *
from api.query_generations import *
from xlrd import open_workbook
from api.commons import data_dict
from voice_service.voice_uploads import *
from voice_service.models import *
from datetime import time
from common.utils import getHttpResponse as json_HttpResponse

def upload_new(request):
    #import pdb;pdb.set_trace()
    teamleader_obj_name = TeamLead.objects.filter(name_id=request.user.id)[0]
    #teamleader_obj = (teamleader_obj_name.project_id, teamleader_obj_name.center_id)
    teamleader_obj = TeamLead.objects.filter(name_id=request.user.id).values_list('project','center')[0]
    #prj_obj = teamleader_obj_name.project
    prj_obj = Project.objects.filter(id=teamleader_obj[0])[0]
    prj_name= prj_obj.name
    #center_obj = teamleader_obj_name.center
    center_obj = Center.objects.filter(id=teamleader_obj[1])[0]
    prj_id = prj_obj.id
    fname = request.FILES['myfile']
    var = fname.name.split('.')[-1].lower()
    if var not in ['xls', 'xlsx', 'xlsb']:
        return json_HttpResponse("Invalid File")
    else:
        try:
            open_book = open_workbook(filename=None, file_contents=fname.read())
        except:
            return json_HttpResponse("Invalid File")
        excel_sheet_names = open_book.sheet_names()
        file_sheet_names = Authoringtable.objects.filter(project=prj_obj,center=center_obj).\
                            values_list('sheet_name',flat=True).distinct()

        sheet_names, raw_table_mapping, internal_error_mapping = {}, {}, {}
        external_error_mapping, worktrack_mapping, headcount_mapping = {}, {}, {}
        target_mapping, tat_mapping, upload_mapping, incoming_error_mapping, authoring_dates = {}, {}, {}, {}, {}
        aht_individual_mapping, aht_team_mapping, ivr_vcr_mapping, risk_mapping, time_mapping = {}, {}, {}, {}, {}

        ignorablable_fields, other_fileds = [], []
        voice_check = prj_obj.is_voice
        if voice_check == True:
            voice_data = voice_upload(request, prj_obj, center_obj, open_book)

        sub_project_boolean_check =  prj_obj.sub_project_check
        if sub_project_boolean_check == True:
            project_names = sub_project_names(request, open_book)

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

        headcount_map_query = Authoring_mapping(prj_obj,center_obj,'HeadcountAuthoring')
        for map_key, map_value in headcount_map_query.iteritems():
            if map_key == 'sheet_name':
                sheet_names['headcount_sheet'] = map_value
            if map_value != '' and map_key not in mapping_ignores:
                headcount_mapping[map_key] = map_value.lower()
                if map_key == 'date':
                    authoring_dates['headcount_date'] = map_value.lower()

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

        tat_map_query = Authoring_mapping(prj_obj, center_obj, 'TatAuthoring')
        for map_key, map_value in tat_map_query.iteritems():
            if map_key == 'sheet_name':
                sheet_names['tat_sheet'] = map_value
            if map_value != '' and map_key not in mapping_ignores:
                tat_mapping[map_key] = map_value.lower()
                if map_key == 'date':
                    authoring_dates['tat_date'] = map_value.lower()

        upload_map_query = Authoring_mapping(prj_obj,center_obj,'UploadAuthoring')
        for map_key, map_value in upload_map_query.iteritems():
            if map_key == 'sheet_name':
                sheet_names['upload_sheet'] = map_value
            if map_value != '' and map_key not in mapping_ignores:
                upload_mapping[map_key] = map_value.lower()
                if map_key == 'date':
                    authoring_dates['upload_date'] = map_value.lower()

        incoming_error_map_query = Authoring_mapping(prj_obj,center_obj,'IncomingerrorAuthoring')
        for map_key, map_value in incoming_error_map_query.iteritems():
            if map_key == 'sheet_name':
                sheet_names['incoming_error_sheet'] = map_value
            if map_value != '' and map_key not in mapping_ignores:
                incoming_error_mapping[map_key] = map_value.lower()
                if map_key == 'date':
                    authoring_dates['incoming_error_date'] = map_value.lower()

        aht_individual_map_query = Authoring_mapping(prj_obj,center_obj,'AHTIndividualAuthoring')
        for map_key, map_value in aht_individual_map_query.iteritems():
            if map_key == 'sheet_name':
                sheet_names['aht_individual_sheet'] = map_value
            if map_value != '' and map_key not in mapping_ignores:
                aht_individual_mapping[map_key] = map_value.lower()
                if map_key == 'date':
                    authoring_dates['aht_individual_date'] = map_value.lower()

        aht_team_map_query = Authoring_mapping(prj_obj,center_obj,'AHTTeamAuthoring')
        for map_key, map_value in aht_team_map_query.iteritems():
            if map_key == 'sheet_name':
                sheet_names['aht_team_sheet'] = map_value
            if map_value != '' and map_key not in mapping_ignores:
                aht_team_mapping[map_key] = map_value.lower()
                if map_key == 'date':
                    authoring_dates['aht_team_date'] = map_value.lower()

        IVR_VCR_map_query = Authoring_mapping(prj_obj,center_obj,'IVR_VCR_authoring')
        for map_key, map_value in IVR_VCR_map_query.iteritems():
            if map_key == 'sheet_name':
                sheet_names['IVR_VCR_sheet'] = map_value
            if map_value != '' and map_key not in mapping_ignores:
                ivr_vcr_mapping[map_key] = map_value.lower()
                if map_key == 'date':
                    authoring_dates['IVR_VCR_date'] = map_value.lower()

        risk_map_query = Authoring_mapping(prj_obj,center_obj,'Risk_authoring')
        for map_key, map_value in risk_map_query.iteritems():
            if map_key == 'sheet_name':
                sheet_names['Risk_sheet'] = map_value
            if map_value != '' and map_key not in mapping_ignores:
                risk_mapping[map_key] = map_value.lower()
                if map_key == 'date':
                    authoring_dates['Risk_date'] = map_value.lower()

        time_map_query = Authoring_mapping(prj_obj,center_obj,'Time_authoring')
        for map_key, map_value in time_map_query.iteritems():
            if map_key == 'sheet_name':
                sheet_names['Time_sheet'] = map_value
            if map_value != '' and map_key not in mapping_ignores:
                time_mapping[map_key] = map_value.lower()
                if map_key == 'date':
                    authoring_dates['Time_date'] = map_value.lower()


        other_fileds = filter(None, other_fileds)
        file_sheet_names = sheet_names.values()
        sheet_index_dict = {}
        for sh_name in file_sheet_names:
            if sh_name in excel_sheet_names:
                sheet_index_dict[sh_name] = open_book.sheet_names().index(sh_name) # sheet_index_dict['IVR-VCR'] = 6
        db_check = str(Project.objects.filter(name=prj_obj,center=center_obj).values_list('project_db_handling',flat=True))
        raw_table_dataset, internal_error_dataset, external_error_dataset, work_track_dataset, headcount_dataset = {}, {}, {}, {},{}
        target_dataset, tats_table_dataset, upload_table_dataset, incoming_error_dataset, ivr_vcr_dataset = {}, {}, {}, {}, {}
        aht_individual_dataset, aht_team_dataset, risk_dataset, time_dataset = {}, {}, {}, {}

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
                    elif column != "date" :
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

                if key == sheet_names.get('tat_sheet', ''):
                    date_name = authoring_dates['tat_date']
                    if not tats_table_dataset.has_key(customer_data[date_name]):
                        tats_table_dataset[str(customer_data[date_name])] = {}
                    local_tat_data = {}
                    for raw_key, raw_value in tat_mapping.iteritems():

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

                if key == sheet_names.get('incoming_error_sheet', ''):
                    date_name = authoring_dates['incoming_error_date']
                    if not incoming_error_dataset.has_key(customer_data[date_name]):
                        incoming_error_dataset[str(customer_data[date_name])] = {}
                    local_incoming_error_data = {}
                    for raw_key, raw_value in incoming_error_mapping.iteritems():
                        local_incoming_error_data[raw_key] = customer_data[raw_value]
                    emp_key = '{0}_{1}_{2}_{3}'.format(local_incoming_error_data.get('sub_project', 'NA'),
                                                       local_incoming_error_data.get('work_packet', 'NA'),
                                                       local_incoming_error_data.get('sub_packet', 'NA'),
                                                       local_incoming_error_data.get('employee_id', 'NA'))
                    if 'not_applicable' not in local_incoming_error_data.values():
                        if incoming_error_dataset.has_key(str(customer_data[date_name])):
                            if incoming_error_dataset[str(customer_data[date_name])].has_key(emp_key):
                                for extr_key, extr_value in local_incoming_error_data.iteritems():
                                    if extr_key not in incoming_error_dataset[str(customer_data[date_name])][emp_key].keys():
                                        incoming_error_dataset[str(customer_data[date_name])][emp_key][extr_key] = extr_value
                                    else:
                                        if (extr_key == 'total_errors') or (extr_key == 'audited_errors'):
                                            try:
                                                extr_value = float(extr_value)
                                            except:
                                                extr_value = 0
                                            try:
                                                dataset_value = float(incoming_error_dataset[str(customer_data[date_name])][emp_key][extr_key])
                                            except:
                                                dataset_value = 0
                                            if db_check == 'aggregate':
                                                incoming_error_dataset[str(customer_data[date_name])][emp_key][extr_key] = extr_value + dataset_value
                                            elif db_check == 'update':
                                                incoming_error_dataset[str(customer_data[date_name])][emp_key][extr_key] = extr_value
                            else:
                                incoming_error_dataset[str(customer_data[date_name])][emp_key] = local_incoming_error_data


                if key == sheet_names.get('upload_sheet', ''):
                    date_name = authoring_dates['upload_date']
                    if not upload_table_dataset.has_key(customer_data[date_name]):
                        upload_table_dataset[str(customer_data[date_name])] = {}
                        local_upload_data = {}
                        for raw_key, raw_value in upload_mapping.iteritems():
                            local_upload_data[raw_key] = customer_data[raw_value]
                        emp_key = '{0}_{1}_{2}_{3}'.format(local_upload_data.get('sub_project', 'NA'),
                                                           local_upload_data.get('work_packet', 'NA'),
                                                           local_upload_data.get('sub_packet', 'NA'),
                                                           local_upload_data.get('employee_id', 'NA'))
                        if 'not_applicable' not in local_upload_data.values():
                            if upload_table_dataset.has_key(str(customer_data[date_name])):
                                if upload_table_dataset[str(customer_data[date_name])].has_key(emp_key):
                                    for extr_key, extr_value in local_upload_data.iteritems():
                                        if extr_key not in upload_table_dataset[str(customer_data[date_name])][emp_key].keys():
                                            upload_table_dataset[str(customer_data[date_name])][emp_key][extr_key] = extr_value
                                        else:
                                            if (extr_key == 'total_errors') or (extr_key == 'audited_errors'):
                                                try:
                                                    extr_value = float(extr_value)
                                                except:
                                                    extr_value = 0
                                                try:
                                                    dataset_value = float(upload_table_dataset[str(customer_data[date_name])][emp_key][extr_key])
                                                except:
                                                    dataset_value = 0
                                                if db_check == 'aggregate':
                                                    upload_table_dataset[str(customer_data[date_name])][emp_key][extr_key] = extr_value + dataset_value
                                                elif db_check == 'update':
                                                    upload_table_dataset[str(customer_data[date_name])][emp_key][extr_key] = extr_value
                                else:
                                    upload_table_dataset[str(customer_data[date_name])][emp_key] = local_upload_data

                if key == sheet_names.get('aht_individual_sheet', ''):
                    date_name = authoring_dates['aht_individual_date']
                    if not aht_individual_dataset.has_key(customer_data[date_name]):
                        aht_individual_dataset[str(customer_data[date_name])] = {}
                    local_aht_individual_data = {}
                    for raw_key, raw_value in aht_individual_mapping.iteritems():
                        local_aht_individual_data[raw_key] = customer_data[raw_value]
                    emp_key = '{0}_{1}_{2}_{3}'.format(local_aht_individual_data.get('sub_project', 'NA'),
                                                       local_aht_individual_data.get('work_packet', 'NA'),
                                                       local_aht_individual_data.get('sub_packet', 'NA'),
                                                       local_aht_individual_data.get('emp_name', 'NA'))
                    if aht_individual_dataset.has_key(customer_data[date_name]):
                        if aht_individual_dataset[str(customer_data[date_name])].has_key(emp_key):
                            for key, value in local_aht_individual_data.iteritems():
                                if key not in aht_individual_dataset[str(customer_data[date_name])][emp_key].keys():
                                    aht_individual_dataset[str(customer_data[date_name])][emp_key][key] = value
                                else:
                                    if key == 'AHT':
                                        try:
                                            value = float(value)
                                        except:
                                            value = 0
                                        try:
                                            dataset_value = float([str(customer_data[date_name])][emp_key][key])
                                        except:
                                            dataset_value = 0
                                        if db_check == 'aggregate':
                                            aht_individual_dataset[str(customer_data[date_name])][emp_key][key] = value + dataset_value
                                        elif db_check == 'update':
                                            aht_individual_dataset[str(customer_data[date_name])][emp_key][key] = value + dataset_value
                        else:
                            aht_individual_dataset[str(customer_data[date_name])][emp_key] = local_aht_individual_data

                if key == sheet_names.get('aht_team_sheet', ''):
                    date_name = authoring_dates['aht_team_date']
                    if not aht_team_dataset.has_key(customer_data[date_name]):
                        aht_team_dataset[str(customer_data[date_name])] = {}
                    local_aht_team_data = {}
                    for raw_key, raw_value in aht_team_mapping.iteritems():
                        local_aht_team_data[raw_key] = customer_data[raw_value]
                    emp_key = '{0}_{1}_{2}_{3}'.format(local_aht_team_data.get('sub_project', 'NA'),
                                                       local_aht_team_data.get('work_packet', 'NA'),
                                                       local_aht_team_data.get('sub_packet', 'NA'),
                                                       local_aht_team_data.get('emp_name', 'NA'))
                    if aht_team_dataset.has_key(customer_data[date_name]):
                        if aht_team_dataset[str(customer_data[date_name])].has_key(emp_key):
                            for key, value in local_aht_team_data.iteritems():
                                if key not in aht_team_dataset[str(customer_data[date_name])][emp_key].keys():
                                    aht_team_dataset[str(customer_data[date_name])][emp_key][key] = value
                                else:
                                    if key == 'AHT':
                                        try:
                                            value = float(value)
                                        except:
                                            value = 0
                                        try:
                                            dataset_value = float([str(customer_data[date_name])][emp_key][key])
                                        except:
                                            dataset_value = 0
                                        if db_check == 'aggregate':
                                            aht_team_dataset[str(customer_data[date_name])][emp_key][key] = value + dataset_value
                                        elif db_check == 'update':
                                            aht_team_dataset[str(customer_data[date_name])][emp_key][key] = value + dataset_value
                        else:
                            aht_team_dataset[str(customer_data[date_name])][emp_key] = local_aht_team_data


                if key == sheet_names.get('IVR_VCR_sheet', ''):
                    date_name = authoring_dates['IVR_VCR_date']
                    if not ivr_vcr_dataset.has_key(customer_data[date_name]):
                        ivr_vcr_dataset[str(customer_data[date_name])]={}
                    local_raw_data = {}
                    for ivr_key,ivr_value in ivr_vcr_mapping.iteritems():
                        local_raw_data[ivr_key] = customer_data[ivr_value]

                    emp_key = '{0}_{1}_{2}'.format(local_raw_data.get('sub_project', 'NA'),
                                                       local_raw_data.get('work_packet', 'NA'),
                                                       local_raw_data.get('sub_packet', 'NA'))


                    if 'not_applicable' not in local_raw_data.values():
                        if ivr_vcr_dataset.has_key(str(customer_data[date_name])):
                            if ivr_vcr_dataset[str(customer_data[date_name])].has_key(emp_key):
                                for pdct_key,pdct_value in local_raw_data.iteritems():
                                    if pdct_key not in ivr_vcr_dataset[str(customer_data[date_name])][emp_key].keys():
                                        ivr_vcr_dataset[str(customer_data[date_name])][emp_key][pdct_key] = pdct_value
                                    else:
                                        if (pdct_key in ['Approved Verified','Grossed Up 1','Grossed Up 2','Count']) :
                                            try:
                                                pdct_value = int(float(pdct_value))
                                            except:
                                                pdct_value = 0
                                            try:
                                                dataset_value = int(float(ivr_vcr_dataset[str(customer_data[date_name])][emp_key][pdct_key]))
                                            except:
                                                dataset_value =0
                                            if db_check == 'aggregate':
                                                ivr_vcr_dataset[str(customer_data[date_name])][emp_key][pdct_key] = pdct_value + dataset_value
                                            elif db_check == 'update':
                                                ivr_vcr_dataset[str(customer_data[date_name])][emp_key][pdct_key] = pdct_value
                            else:
                                ivr_vcr_dataset[str(customer_data[date_name])][emp_key] = local_raw_data

                if key == sheet_names.get('Risk_sheet', ''):
                    date_name = authoring_dates['Risk_date']
                    if not risk_dataset.has_key(customer_data[date_name]):
                        risk_dataset[str(customer_data[date_name])]={}
                    local_raw_data = {}
                    for ivr_key,ivr_value in risk_mapping.iteritems():
                        local_raw_data[ivr_key] = customer_data[ivr_value]

                    emp_key = '{0}_{1}_{2}'.format(local_raw_data.get('sub_project', 'NA'),
                                                       local_raw_data.get('work_packet', 'NA'),
                                                       local_raw_data.get('sub_packet', 'NA'))


                    if 'not_applicable' not in local_raw_data.values():
                        if risk_dataset.has_key(str(customer_data[date_name])):
                            if risk_dataset[str(customer_data[date_name])].has_key(emp_key):
                                for pdct_key,pdct_value in local_raw_data.iteritems():
                                    if pdct_key not in risk_dataset[str(customer_data[date_name])][emp_key].keys():
                                        risk_dataset[str(customer_data[date_name])][emp_key][pdct_key] = pdct_value
                                    else:
                                        if (pdct_key in ['data entry Volume','data entry done AHT','HIGH Volume','LOW Volume','MEDIUM Volume','HIGH AHT','LOW AHT','MEDIUM AHT','Pre Populated Volume','Pre Populated AHT']) :
                                            try:
                                                pdct_value = int(float(pdct_value))
                                            except:
                                                pdct_value = 0
                                            try:
                                                dataset_value = int(float(risk_dataset[str(customer_data[date_name])][emp_key][pdct_key]))
                                            except:
                                                dataset_value =0
                                            if db_check == 'aggregate':
                                                risk_dataset[str(customer_data[date_name])][emp_key][pdct_key] = pdct_value + dataset_value
                                            elif db_check == 'update':
                                                risk_dataset[str(customer_data[date_name])][emp_key][pdct_key] = pdct_value
                            else:
                                risk_dataset[str(customer_data[date_name])][emp_key] = local_raw_data



                if key == sheet_names.get('Time_sheet', ''):
                    date_name = authoring_dates['Time_date']
                    if not time_dataset.has_key(customer_data[date_name]):
                        time_dataset[str(customer_data[date_name])]={}
                    local_raw_data = {}
                    for time_key,time_value in time_mapping.iteritems():
                        local_raw_data[time_key] = customer_data[time_value]

                    emp_key = '{0}_{1}_{2}_{3}'.format(local_raw_data.get('sub_project', 'NA'),
                                                       local_raw_data.get('work_packet', 'NA'),
                                                       local_raw_data.get('sub_packet', 'NA'),
                                                       local_raw_data.get('emp_name','NA'))


                    if 'not_applicable' not in local_raw_data.values():
                        if time_dataset.has_key(str(customer_data[date_name])):
                            if time_dataset[str(customer_data[date_name])].has_key(emp_key):
                                for pdct_key,pdct_value in local_raw_data.iteritems():
                                    if pdct_key not in time_dataset[str(customer_data[date_name])][emp_key].keys():
                                        con_value = convert_excel_time(float(pdct_value))                                        
                                        time_dataset[str(customer_data[date_name])][emp_key][pdct_key] = con_value
                                    else:
                                        if (pdct_key in ['busy','ready','total']) :
                                            con_value = convert_excel_time(float(pdct_value))                                            
                                            try:
                                                pdct_value = con_value
                                            except:
                                                pdct_value = float(0)
                                            
                                            if db_check == 'aggregate':
                                                time_dataset[str(customer_data[date_name])][emp_key][pdct_key] = pdct_value + dataset_value  
                                            elif db_check == 'update':
                                                time_dataset[str(customer_data[date_name])][emp_key][pdct_key] = pdct_value
                            else:
                                time_dataset[str(customer_data[date_name])][emp_key] = local_raw_data

                





        #sub_prj_check = Project.objects.filter(id=prj_id).values_list('sub_project_check',flat=True)[0]
        sub_prj_check = prj_obj.sub_project_check
        #teamleader_obj = TeamLead.objects.filter(name_id=request.user.id).values_list('project_id','center_id')[0]

        #prj_obj = Project.objects.filter(id=teamleader_obj[0])[0]
        for date_key,date_value in internal_error_dataset.iteritems():
            for emp_key,emp_value in date_value.iteritems():
                emp_data = Error_checking(emp_value,intrnl_error_check)
                if sub_prj_check == True:
                    proje_id = date_value[emp_key]['sub_project']
                    proje_id = prj_obj.name +  " " + proje_id
                    proje_obj = Project.objects.filter(name = proje_id)[0]
                    internalerror_insert1 = internalerror_query_insertion(emp_data, proje_obj, center_obj,teamleader_obj_name,db_check)
                    #prj_obj = prj_obj
                    internalerror_insert = internalerror_query_insertion(emp_data, prj_obj, center_obj,teamleader_obj_name,db_check)
                #else:
                    #prj_obj = prj_obj
                    #center_obj = center_obj
                internalerror_insert = internalerror_query_insertion(emp_data, prj_obj, center_obj,teamleader_obj_name,db_check)

        for date_key,date_value in external_error_dataset.iteritems():
            for emp_key,emp_value in date_value.iteritems():
                emp_data = Error_checking(emp_value,extrnl_error_check)
                if sub_prj_check == True:
                    proje_id = date_value[emp_key]['sub_project']
                    proje_id = prj_obj.name +  " " + proje_id
                    proje_obj = Project.objects.filter(name = proje_id)[0]
                    externalerror_insert1 = externalerror_query_insertion(emp_value, proje_obj, center_obj,teamleader_obj_name,db_check)
                    #prj_obj = prj_obj
                    externalerror_insert = externalerror_query_insertion(emp_value, prj_obj, center_obj,teamleader_obj_name,db_check)
                #else:
                    #prj_obj = prj_obj
                    #center_obj = center_obj
                externalerror_insert = externalerror_query_insertion(emp_value, prj_obj, center_obj,teamleader_obj_name,db_check)

        for date_key,date_value in work_track_dataset.iteritems():
            for emp_key,emp_value in date_value.iteritems():
                if sub_prj_check == True:
                    proje_id = date_value[emp_key]['sub_project']
                    proje_id = prj_obj.name +  " " + proje_id
                    proje_obj = Project.objects.filter(name = proje_id)[0]
                    externalerror_insert1 = worktrack_query_insertion(emp_value, proje_obj, center_obj,teamleader_obj_name,db_check)
                    #prj_obj = prj_obj
                    externalerror_insert = worktrack_query_insertion(emp_value, prj_obj, center_obj,teamleader_obj_name,db_check)
                #else:
                    #prj_obj = prj_obj
                    #center_obj = center_obj
                externalerror_insert = worktrack_query_insertion(emp_value, prj_obj, center_obj,teamleader_obj_name,db_check)

        for date_key, date_value in headcount_dataset.iteritems():
            for emp_key, emp_value in date_value.iteritems():
                if sub_prj_check == True:
                    proje_id = date_value[emp_key]['sub_project']
                    proje_id = prj_obj.name +  " " + proje_id
                    proje_obj = Project.objects.filter(name = proje_id)[0]
                    headcount_insert1 = headcount_query_insertion(emp_value, proje_obj, center_obj, teamleader_obj_name,db_check)
                    #prj_obj = prj_obj
                    headcount_insert = headcount_query_insertion(emp_value, prj_obj, center_obj, teamleader_obj_name,db_check)
                #else:
                #    prj_obj = prj_obj
                #    center_obj = center_obj
                headcount_insert = headcount_query_insertion(emp_value, prj_obj, center_obj, teamleader_obj_name,db_check)

        for date_key, date_value in target_dataset.iteritems():
            for emp_key, emp_value in date_value.iteritems():
                if sub_prj_check == True:
                    proje_id = date_value[emp_key]['sub_project']
                    proje_id = prj_obj.name +  " " + proje_id
                    proje_obj = Project.objects.filter(name = proje_id)[0]
                    externalerror_insert = target_table_query_insertion(emp_value, proje_obj, center_obj, teamleader_obj_name,db_check)
                    #prj_obj = prj_obj
                    externalerror_insert = target_table_query_insertion(emp_value, prj_obj, center_obj, teamleader_obj_name,db_check)
                #else:
                #    prj_obj = prj_obj
                #    center_obj = center_obj
                externalerror_insert = target_table_query_insertion(emp_value, prj_obj, center_obj, teamleader_obj_name,db_check)

        for date_key, date_value in tats_table_dataset.iteritems():
            for emp_key, emp_value in date_value.iteritems():
                externalerror_insert = tat_query_insertion(emp_value, prj_obj, center_obj, teamleader_obj_name,db_check)

        for date_key, date_value in upload_table_dataset.iteritems():
            for emp_key, emp_value in date_value.iteritems():
                externalerror_insert = upload_query_insertion(emp_value, prj_obj, center_obj, teamleader_obj_name,db_check)

        for date_key, date_value in incoming_error_dataset.iteritems():
            for emp_key, emp_value in date_value.iteritems():
                externalerror_insert = incoming_error_query_insertion(emp_value, prj_obj, center_obj, teamleader_obj_name,db_check)

        for key, value in aht_individual_dataset.iteritems():
            for emp_key, emp_value in value.iteritems():
                aht_data_insert = aht_individual_query_insertion(emp_value, prj_obj, center_obj, teamleader_obj_name,db_check)

        for key, value in aht_team_dataset.iteritems():
            for emp_key, emp_value in value.iteritems():
                aht_team_data_insert = aht_team_query_insertion(emp_value, prj_obj, center_obj, teamleader_obj_name,db_check)

        for key, value in ivr_vcr_dataset.iteritems():
            for emp_key, emp_value in value.iteritems():
                ivr_vcr_data_insert = ivr_vcr_query_insertion(emp_value, prj_obj, center_obj, teamleader_obj_name,db_check)

        for key, value in risk_dataset.iteritems():
            for emp_key, emp_value in value.iteritems():
                risk_data_insert = risk_query_insertion(emp_value, prj_obj, center_obj, teamleader_obj_name,db_check)

        for key, value in time_dataset.iteritems():
            for emp_key, emp_value in value.iteritems():
                time_data_insert = time_query_insertion(emp_value, prj_obj, center_obj, teamleader_obj_name,db_check)

        for date_key,date_value in raw_table_dataset.iteritems():
            for emp_key,emp_value in date_value.iteritems():
                try:
                    per_day_value = int(float(emp_value.get('per_day', '')))
                except:
                    per_day_value = 0

                if sub_prj_check == True:
                    proje_id = date_value[emp_key]['sub_project']
                    proje_id = prj_obj.name +  " " + proje_id
                    proje_obj = Project.objects.filter(name = proje_id)[0]
                    raw_table_insert = raw_table_query_insertion(emp_value, proje_obj, center_obj, teamleader_obj_name,per_day_value, db_check)
                    #prj_obj = prj_obj
                    raw_table_insert = raw_table_query_insertion(emp_value, prj_obj, center_obj, teamleader_obj_name,per_day_value, db_check)
                #else:
                #    prj_obj = prj_obj
                #    center_obj = center_obj
                raw_table_insert = raw_table_query_insertion(emp_value, prj_obj, center_obj, teamleader_obj_name,per_day_value, db_check)

        # if len(raw_table_dataset)>0:
        #     sorted_dates = dates_sorting(raw_table_dataset)
        #     if sub_prj_check == True:
        #         for emp_key,emp_value in date_value.iteritems():
        #             proje_id = date_value[emp_key]['sub_project']
        #             proje_id = prj_obj.name +  " " + proje_id
        #             proje_obj = Project.objects.filter(name = proje_id)[0]
        #             insert = redis_insert(proje_obj, center_obj,sorted_dates , key_type='Production')
        #             #prj_obj = prj_obj
        #             insert = redis_insert(prj_obj, center_obj,sorted_dates , key_type='Production')
        #     else:
        #         insert = redis_insert(prj_obj, center_obj,sorted_dates , key_type='Production')

        # if len(internal_error_dataset) > 0:
        #     sorted_dates = dates_sorting(internal_error_dataset)
        #     if sub_prj_check == True:
        #         for emp_key,emp_value in date_value.iteritems():
        #             proje_id = date_value[emp_key]['sub_project']
        #             proje_id = prj_obj.name +  " " + proje_id
        #             proje_obj = Project.objects.filter(name = proje_id)[0]
        #             insert = redis_insert(proje_obj, center_obj, sorted_dates, key_type='Internal')
        #         #prj_obj = prj_obj
        #         insert = redis_insert(prj_obj, center_obj,sorted_dates , key_type='Internal')
        #     else:
        #         insert = redis_insert(prj_obj, center_obj, sorted_dates, key_type='Internal')

        # if len(external_error_dataset):
        #     sorted_dates = dates_sorting(external_error_dataset)
        #     if sub_prj_check == True:
        #         for emp_key,emp_value in date_value.iteritems():
        #             proje_id = date_value[emp_key]['sub_project']
        #             proje_id = prj_obj.name +  " " + proje_id
        #             proje_obj = Project.objects.filter(name = proje_id)[0]
        #             insert = redis_insert(proje_obj, center_obj, sorted_dates, key_type='External')
        #         prj_obj = prj_obj
        #         insert = redis_insert(prj_obj, center_obj, sorted_dates, key_type='External')
        #     else:
        #         insert = redis_insert(prj_obj, center_obj, sorted_dates, key_type='External')


        # if len(work_track_dataset) > 0:
        #     sorted_dates = dates_sorting(work_track_dataset)
        #     if sub_prj_check == True:
        #         for emp_key,emp_value in date_value.iteritems():
        #             proje_id = date_value[emp_key]['sub_project']
        #             proje_id = prj_obj.name +  " " + proje_id
        #             proje_obj = Project.objects.filter(name = proje_id)[0]
        #             insert = redis_insert(proje_obj, center_obj, sorted_dates, key_type='WorkTrack')
        #             #prj_obj = prj_obj
        #             insert = redis_insert(prj_obj, center_obj, sorted_dates, key_type='WorkTrack')
        #     else:
        #         insert = redis_insert(prj_obj, center_obj, sorted_dates, key_type='WorkTrack')
        var ='hello'
        return json_HttpResponse(var)


def upload_acc(request):
    final_dict = {}
    data_date = []
    week_names,month_names = [], []
    week_num = 0
    new_date_list = []
    upload_target_dt = {}
    main_data_dict = data_dict(request.GET)
    if main_data_dict['dwm_dict'].has_key('day') and main_data_dict['type'] == 'day':
        main_dates_list = [ main_data_dict['dwm_dict']['day']]
    elif main_data_dict['dwm_dict'].has_key('week') and main_data_dict['type'] == 'week':
        main_dates_list = main_data_dict['dwm_dict']['week']
    elif main_data_dict['dwm_dict'].has_key('month') and main_data_dict['type'] == 'month':
        main_dates_list = main_data_dict['dwm_dict']['month']['month_dates']
    prj_id = main_data_dict['pro_cen_mapping'][0][0]
    center = main_data_dict['pro_cen_mapping'][1][0]
    date_value = []
    final_data = {}
    final_data['data'] = []
    final_data['date'] = []
    if main_data_dict['dwm_dict'].has_key('day') and main_data_dict['type'] == 'day':
        for sing_list in main_dates_list:
            upload_target_details =  upload_target_data(sing_list, prj_id, center)
        for i in xrange(0,len(upload_target_details['data'])):
            if upload_target_details['data'][i]:
                final_data['data'].append(upload_target_details['data'][i])
                final_data['date'].append(sing_list[i])
        pre_final_data = {}
        pre_final_data['data'] = final_data['data']
        final_data['data'] = [pre_final_data]
        final_dict['upload_target_data'] = final_data
    elif main_data_dict['dwm_dict'].has_key('week') and main_data_dict['type'] == 'week':
        for sing_list in main_dates_list:
            data_date.append(sing_list[0] + ' to ' + sing_list[-1])
            week_name = str('week' + str(week_num))
            week_names.append(week_name)
            week_num = week_num + 1
            upload_target_details = upload_target_data(sing_list, prj_id, center)
            upload_target_dt[week_name] = upload_target_details
        final_upload_target_details = prod_volume_upload_week_util(week_names,upload_target_dt, {})
        for i in xrange(0,len(final_upload_target_details['data'])):
            if final_upload_target_details['data'][i]:
                final_data['data'].append(final_upload_target_details['data'][i])
                final_data['date'].append(data_date[i])
        pre_final_data = {}
        pre_final_data['data'] = final_data['data']
        final_data['data'] = [pre_final_data]
        final_dict['upload_target_data'] = final_data
    else:
        for month_na,month_va in zip(main_data_dict['dwm_dict']['month']['month_names'],main_data_dict['dwm_dict']['month']['month_dates']):
            month_name = month_na
            month_dates = month_va
            data_date.append(month_dates[0] + ' to ' + month_dates[-1])
            month_names.append(month_name)
            upload_target_details = upload_target_data(month_dates, prj_id, center)
            upload_target_dt[month_name]  = upload_target_details
        final_upload_target_details = prod_volume_upload_week_util(month_names, upload_target_dt, {})
        for i in xrange(0,len(final_upload_target_details['data'])):
            if final_upload_target_details['data'][i]:
                final_data['data'].append(final_upload_target_details['data'][i])
                final_data['date'].append(data_date[i])
        pre_final_data = {}
        pre_final_data['data'] = final_data['data']
        final_data['data'] = [pre_final_data]
        final_dict['upload_target_data'] = final_data
    final_dict['type'] = main_data_dict['type']
    final_dict['is_annotation'] = annotation_check(request)
    return json_HttpResponse(final_dict)
