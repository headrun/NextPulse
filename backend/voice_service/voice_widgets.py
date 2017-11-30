
import datetime
from voice_service.models import *
from voice_service.constants import *

def create_filters(filter_params):
    """Creating filters for voice
    """

    filter_dict = {}
    for item in filter_params:
        for key, value in item.iteritems():
            if value:
                _key = '%s__in' %key
                filter_dict.update({_key:value})

    return filter_dict 


def get_hourly_sum(project, dates, table_name, location={}, skill={}, disposition={}, term='disposition'):
    """take hourly summary of a selected date range
    """

    _dict = {}
    if term == 'outbound_disposition':
        _term = 'disposition'
    elif term == 'outbnd_dispo_common':
        _term = 'disposition'
    elif term == 'call_status':
        _term = 'status'
    else:
        _term = term
    print [location, skill, disposition, project, dates]
    filter_param = create_filters([location, skill, disposition, project, dates])

    _date = []
    data_set = table_name.objects.filter(**filter_param).values_list('start_time', _term, 'date')\
                .order_by(_term)

    for item in data_set:
        _date.append(str(item[2]))
        if not _dict.has_key(item[1]):
            result_dict = {}
            for time in xrange(0, 24):
                result_dict.update({time : 0})

            _dict.update({item[1]: result_dict})
        _dict[item[1]][item[0].hour] +=1

    _date = list(set(_date))
    _dict = calculate_average(_dict, float(len(_date)))
    final_dict = create_result(_dict, 'hour', term)
    
    return final_dict


def create_result(result_dict, type, term):
    """creating result data for output
    """
    
    final_dict = {'date':range(24), 'type':type, term:[]}

    for key, value in result_dict.iteritems():
        term_dict = {'data':[]}
        term_dict.update({'name':key})
        for value_key, value_value in value.iteritems():
            term_dict['data'].append(value_value)
        final_dict[term].append(term_dict)
    return final_dict


def calculate_average(result_dict, no_of_days):
    """this function calculates average of the hour data
    """

    for key, value in result_dict.iteritems():
        for value_key, value_value in value.iteritems():
            result_dict[key][value_key] = float('%.2f' % round((value_value/no_of_days), 2))

    return result_dict


#========================================== ACTUAL VS REQUIRED CODE ======================================

def actual_required_hourly(project, dates, table_name, location={}, skill={}, disposition={}):
    """Its hourly record for actualvsrequired
    """
    
    result_dict = {}
    filter_param = create_filters([location, skill, disposition, project, dates])
    data_sets = table_name.objects.filter(**filter_param).values()

    for data_set in data_sets:
        _dict = {}
        for time in xrange(0, 24):
            _dict.update({time : {
                'total_calls': 0,
                'actual_present':[],
                'actual_login':0,
                'required_login':0
                }})
        if not result_dict.has_key(str(data_set['date'])):
            result_dict.update({str(data_set['date']): _dict})
        result_dict[str(data_set['date'])][data_set['start_time'].hour]['total_calls'] += 1
        if data_set['status'] == 'Answered':
            result_dict[str(data_set['date'])][data_set['start_time'].hour]['actual_present']\
                    .append(data_set['agent_id'])

    result_dict=calculate_actual_required(result_dict)
    result_dict = avg_actual_required(result_dict)
    result_dict = create_result_actual_required(result_dict, 'hour')

    return result_dict


def calculate_actual_required(result_dict):
    """Calculating the actual and required deployment. 
    """

    for key, value in result_dict.iteritems():
        for key1, value1 in value.iteritems():
            value1['required_login']= float('%.2f' % round((value1['total_calls']/float(CALL_TARGET_PER_AGENT)), 2))
            value1['actual_login'] = len(set(value1['actual_present']))
            del value1['actual_present']
    return result_dict


def avg_actual_required(result_dict):
    """ It will calculate average of all days in hour format
    """

    _dict = {}
    for time in xrange(0, 24):
        _dict.update({time : {
            'total_calls': 0,
            'actual_login':0,
            'required_login':0
            }})
    no_of_days = len(result_dict.keys())
    for key, value in result_dict.iteritems():
        for key1, value1 in value.iteritems():
            _dict[key1]['total_calls'] += value1['total_calls']
            _dict[key1]['actual_login'] += value1['actual_login']
            _dict[key1]['required_login'] += value1['required_login']

    _dict = calculate_average(_dict, no_of_days)
    return _dict


def create_result_actual_required(result_dict, type):
    """creating final result
    """

    term = 'agent_required'
    final_dict = {'date':range(24), 'type':type, term: []}
    temp_dict = {}
    for key, value in result_dict.iteritems():
        for key1, value1 in value.iteritems():
            if key1 not in temp_dict.keys():
                temp_dict[key1] = []
            temp_dict[key1].append(value1)

    for key, value in temp_dict.iteritems():
        final_dict[term].append({'data': value, 'name':key})
    return final_dict 

#====================================== ACTUAL VS REQUIRED CODE ENDS =======================================