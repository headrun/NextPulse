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
from voice_service.constrants import *
from xlrd import open_workbook
from api.commons import data_dict
from common.utils import getHttpResponse as json_HttpResponse

def voice_upload(request, prj_obj, center_obj, open_book):
    project = prj_obj
    excel_sheet_names = open_book.sheet_names()
    sheet_names, authoring_dates, inbound_hourly_mapping = {}, {}, {}
    outbound_hourly_mapping, inbound_daily_mapping, outbound_daily_mapping = {}, {}, {}
    agent_performance_mapping, ignorablable_fields = {}, []
    
    mapping_ignores = ['project_id','center_id','_state','sheet_name','id','total_errors_require', 'updated_at', 'created_at']

    sheet_names, inbound_hourly_mapping, authoring_dates = matching_with_authoring(prj_obj, center_obj,\
                    InboundHourlyCallAuthoring, 'inbound_hourly_sheet', 'inbound_hourly_date',\
                    authoring_dates, inbound_hourly_mapping, excel_sheet_names, mapping_ignores, sheet_names)

    sheet_names, outbound_hourly_mapping, authoring_dates = matching_with_authoring(prj_obj, center_obj,\
                    OutboundHourlyCallAuthoring, 'outbound_hourly_sheet', 'outbound_hourly_date',\
                    authoring_dates, outbound_hourly_mapping, excel_sheet_names, mapping_ignores, sheet_names)

    sheet_names, agent_performance_mapping, authoring_dates = matching_with_authoring(prj_obj, center_obj,\
                    AgentPerformanceAuthoring, 'agent_performance_sheet', 'agent_performance_date',\
                    authoring_dates, agent_performance_mapping, excel_sheet_names, mapping_ignores, sheet_names)

    sheet_index_dict = {}
    for sh_name in excel_sheet_names:
        #if sh_name in excel_sheet_names:
        sheet_index_dict[sh_name] = open_book.sheet_names().index(sh_name)

    db_check = str(Project.objects.filter(name=prj_obj,center=center_obj).values_list('project_db_handling',flat=True))
    raw_table_dataset, internal_error_dataset, external_error_dataset, work_track_dataset= {}, {}, {},{}
    headcount_dataset, target_dataset, inbound_hourly_dataset, inbound_daily_dataset = {}, {}, {},{}
    outbound_hourly_dataset, outbound_daily_dataset = {}, {}
    

    for key,value in sheet_index_dict.iteritems():
        _agents = []
        _data_dict = {}
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
                if column in DATES:
                    _date = cell_data
                    customer_data[column] = datetime.datetime.strptime(_date, "%d/%m/%Y")
                    #cell_data = xlrd.xldate_as_tuple(int(cell_data.split('.')[0]), 0)
                    #cell_data = '%s-%s-%s' % (cell_data[0], cell_data[1], cell_data[2])
                    #customer_data[column] = ''.join(cell_data)
                elif column in SECONDS_STORAGE:
                    customer_data[column] = convert_to_sec(cell_data)
                elif column in INTEGER_NUMBERS:
                    customer_data[column] = int(float(cell_data))
                elif column in DATETIME_STORAGE:
                    customer_data[column] = datetime.datetime.strptime((_date + cell_data), "%d/%m/%Y%H:%M:%S")
                elif column not in DATES:
                    customer_data[column] = ''.join(cell_data)

            if key == 'Inbound Hourly':                
                local_inbound_hourly = {}
                for key1, value1 in inbound_hourly_mapping.iteritems():
                    local_inbound_hourly[key1] = customer_data[value1]

                _data_dict.update({local_inbound_hourly['call_id'] : local_inbound_hourly})

            elif key == 'Outbound Hourly':        
                local_outbound_hourly = {}
                for key1, value1 in outbound_hourly_mapping.iteritems():
                    local_outbound_hourly[key1] = customer_data[value1]

                local_outbound_hourly['agent'] = local_outbound_hourly['call_flow'].split('(')[-1]
                local_outbound_hourly['agent'] = local_outbound_hourly['agent'].split(')')[0]
                _data_dict.update({local_outbound_hourly['call_id'] : local_outbound_hourly})

            elif key == 'Agent Transfer':                
                local_agent_performance = {}
                for key1, value1 in agent_performance_mapping.iteritems():
                    local_agent_performance[key1] = customer_data[value1]

                key2 = '%s_%s_%s' % (local_agent_performance['agent'], str(local_agent_performance['date'].date()),\
                                    local_agent_performance['call_type'])
                _data_dict.update({key2 : local_agent_performance})

        saving_data(_data_dict, prj_obj, key)


def matching_with_authoring(prj_obj, center_obj, table_name, _sheet_name, _authoring_date, authoring_dates, _dict, excel_sheet_names, mapping_ignores, sheet_names):
    
    _map_query = {}
    item = table_name.objects.filter(project=prj_obj, center=center_obj)
    if item:
        _map_query = item[0].__dict__ 
    for map_key, map_value in _map_query.iteritems():
        if map_key == 'sheet_name':
            sheet_names[_sheet_name] = map_value
        if map_value != '' and map_key not in mapping_ignores:
            _dict[map_key] = map_value.lower()
            if map_key == 'call_date' or 'date':
                authoring_dates[_authoring_date] = map_value.lower()

    return sheet_names, _dict, authoring_dates


def remove_existing_data_hourly(table_name, call_dicts):
    """ Removing the keys which are existing in DB already """
    existing_calls = list(table_name.objects.filter(call_id__in=call_dicts.keys()).values_list('call_id', flat=True))
    for key in existing_calls:
        del call_dicts[key]
    return call_dicts


def remove_existing_data_performance(table_name, call_dicts):
    """ Removing the keys which are existing in DB already """   
    existing_calls = list(table_name.objects.all().values_list('agent__name', 'date', 'call_type'))

    for item in existing_calls:
        key = '%s_%s_%s' % (item[0], item[1], item[2])
        del call_dicts[key]
    return call_dicts


def convert_from_sec(duration):
    """ converting time to seconds to display in DB """
    m, s = divmod(int(duration), 60)
    h, m = divmod(m, 60)
    duration = "%d:%02d:%02d" % (h, m, s)
    duration


def convert_to_sec(duration):
    """ convert time from sec to display """  
    _duration = duration.split(":")
    _duration1 = (int(_duration[0]) * 60 * 60) + (int(_duration[1]) * 60) + int(_duration[2])
    return _duration1


def get_agent_details(data_dict, _agents, project):
    """ get the user details """
    agent_dict = {}
    agent_list = []
    agents = list(set(_agents))
    
    for agent in agents:
        obj, created = Agent.objects.get_or_create(name= agent, project= project)
        agent_list.append(obj)
    for item in agent_list:
        agent_dict.update({item.name: item})
    for key, value in data_dict.iteritems():
        value['agent'] = agent_dict[value['agent']]
        value['project'] = project
        value['center'] = project.center
    return data_dict


def check_transfer(data_dict, _agents, sheet_name):
    ''' checking for transfer '''
    agent_transfer_list, skill_transfer_list, location_transfer_list, disposition_transfer_list = [], [], [], []

    for key, value in data_dict.iteritems():   
        agent_transfer_list, data_dict[key], _agents = show_transfer(value, 'agent', agent_transfer_list, _agents, key)
        if sheet_name == 'Inbound Hourly':
            skill_transfer_list, data_dict[key], _agents = show_transfer(value, 'skill', skill_transfer_list, _agents, key)
            location_transfer_list, data_dict[key], _agents = show_transfer(value, 'location', location_transfer_list, _agents, key)   
        disposition_transfer_list, data_dict[key], _agents = show_transfer(value, 'disposition', disposition_transfer_list, _agents,key)

    return data_dict, agent_transfer_list, skill_transfer_list, location_transfer_list,\
                                        disposition_transfer_list, _agents


def show_transfer(data_dict, term, transfer_call_list, _agents, key):
    """ transfer function for all process """
    _data = data_dict[term]

    data = data_dict[term].split(' -> ')

    if len(data) > 1:
        data_dict[term] = data[-1]

        if term == 'disposition':
            if data_dict[term] in CANCEL_DISPOSITION:
                data_dict[term] = 'None'

        transfer_call_list.append([data_dict['call_id'], _data])
    if term == 'agent':
        _agents.append(data[-1])

    return transfer_call_list, data_dict, _agents


def get_agents_from_performance(data_dict):
    '''getting agents forperformance sheet'''
    _agents = []
    for key, value in data_dict.iteritems():
        _agents.append(value['agent'])
    return  _agents

    
def saving_data(data_dict, project, sheet_name):
    ''' final setup to save data '''
    _agents = []
    transfer_dict = []
    agent_transfer_list, skill_transfer_list, location_transfer_list, disposition_transfer_list = [], [], [], []
    if sheet_name == 'Inbound Hourly':
        table_name = InboundHourlyCall
    elif sheet_name == 'Outbound Hourly':
        table_name = OutboundHourlyCall
    if sheet_name == 'Agent Transfer':
        table_name = AgentPerformance
        data_dict = remove_existing_data_performance(table_name, data_dict)
        _agents = get_agents_from_performance(data_dict)
    else:
        data_dict = remove_existing_data_hourly(table_name, data_dict)
        data_dict, agent_transfer_list, skill_transfer_list, location_transfer_list,\
                    disposition_transfer_list, _agents = check_transfer(data_dict, _agents, sheet_name)

    _data_dict = get_agent_details(data_dict, _agents, project)
    date = []
    if _data_dict:
        date = data_bulk_insertion(table_name, _data_dict)
    for tkey, tvalue in TRANSFER.iteritems():
        if eval(tkey):
            _date = save_transfers(eval(tvalue), eval(tkey))

    if sheet_name in CONVERT_TO_DAILY and _data_dict:
        status = create_daily_from_hourly(sheet_name, project, date)

    return 'Success'


def create_daily_from_hourly(sheet_name, _project, dates):
    """ convert hourly data into daily data """

    if sheet_name == 'Inbound Hourly':
        table_name = InboundHourlyCall
        daily_table = InboundDaily
    elif sheet_name == 'Outbound Hourly':
        table_name = OutboundHourlyCall
        daily_table = OutboundDaily

    hourly_data_list = list(table_name.objects.filter(date__in=dates, project=_project).values())
    daily_data_dict = create_daily_data(hourly_data_list, _project, sheet_name)
    date = data_bulk_insertion(daily_table, daily_data_dict)
    return 'success'


def create_daily_data(hourly_list, _project, sheet_name):
    """ summarising data from hourly data to daily data """
    daily_data = {}
    daily_data_temp = {}
    __agents = {}
    for _item in hourly_list:

        _agent = Agent.objects.get(id=_item['agent_id'])
        key1 = '%s_%s_%s' %(_agent.name, str(_item['date']), _item['disposition'])
        if not daily_data_temp.has_key(key1):
            daily_data_temp[key1] = []

        daily_data_temp[key1].append(_item)
        __agents.update({_agent.id:_agent})

    for key, value in daily_data_temp.iteritems():
        daily_data[key] = {'date': '', 'agent': '', 'hours_worked' : 1, 'total_calls' : 0, 'connects_per_hr' : 0,\
                            'calls_answered' : 0, 'wrapup_time': 0, 'hold_time':0, 'talk_time':0, 'time_to_answer': 0,\
                            'disposition': '', 'project': '', 'center': ''}

        daily_data[key]['total_calls'] = len(value)

        daily_data[key]['connects_per_hr'] = float(daily_data[key]['total_calls']) / daily_data[key]['hours_worked']
        daily_data[key]['date'] = value[0]['date']
        daily_data[key]['agent'] = __agents[value[0]['agent_id']]

        for item in value:
            if sheet_name == 'Inbound Hourly':
                if item['status'] == 'Answered':
                    daily_data[key]['calls_answered'] += 1
                daily_data[key]['skill'] = item['skill']
                daily_data[key]['location'] = item['location']
                daily_data[key]['time_to_answer'] +=  item['time_to_answer']
            daily_data[key]['wrapup_time'] += item['wrapup_duration']
            daily_data[key]['hold_time'] += item['hold_time']
            daily_data[key]['talk_time'] += item['talk_time']
            #daily_data[key]['time_to_answer'] +=  item['time_to_answer']
            daily_data[key]['disposition'] = item['disposition']
            daily_data[key]['project'] = _project
            daily_data[key]['center'] = _project.center

    return daily_data

    






