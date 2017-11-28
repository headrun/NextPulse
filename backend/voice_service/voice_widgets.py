
import collections
import datetime
from voice_service.models import *


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
    else:
        _term = term
    filter_param = create_filters([location, skill, disposition, project, dates])


    data_set = table_name.objects.filter(**filter_param).values_list('start_time', _term).order_by(_term)

    for item in data_set:
        result_dict = {}
        for time in xrange(0, 24):
            result_dict.update({time : 0})

        if not _dict.has_key(item[1]):
            _dict.update({item[1]: result_dict})
        _dict[item[1]][item[0].hour] +=1

    _dict = calculate_average(_dict, float(len(dates['date'])))
    final_dict = create_result(_dict, 'hour', term)
    
    return final_dict


def create_result(result_dict, type, term):
    """creating result data for output
    """
    
    final_dict = {'date':range(24), 'type':type, term:[]}
    locations = []
    print result_dict
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
            #result_dict[key][value_key] = "%.2f" % (value_value/no_of_days)
            result_dict[key][value_key] = float('%.2f' % round((value_value/no_of_days), 2))

    return result_dict


"""
def actual_required_hourly(project, dates, table_name, location={}, skill={}, disposition={}):
    ""Its hourly record for actualvsrequired
    "
    
    result_dict = {}
    filter_param = create_filters([location, skill, disposition, project, dates])
    import pdb;pdb.set_trace()
    data_sets = table_name.objects.filter(**filter_param).values()

    for data_set in data_sets:
        _dict = {}
        for time in xrange(0, 24):
            _dict.update({time : {
                'total_calls': 0,
                'actual_present':[],
                'required':0
                }})
        if not result_dict.has_key(data_set['date']):
            result_dict.update({data_set['date']: _dict})
        result_dict[data_set['date']][data_set[start_time.hour]]['total_calls'] += 1
        if data_set['status'] == 'Answered':
            result_dict[data_set['date']][data_set[start_time.hour]]['actual_present'].append(data_set['agent'].name)

"""