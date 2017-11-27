
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
	filter_param = create_filters([location, skill, disposition, project, dates])

	data_set = table_name.objects.filter(**filter_param).values_list('start_time', term).order_by(term)

	for item in data_set:
		result_dict = {}
		for time in xrange(0, 24):
			result_dict.update({time : 0})

		if not _dict.has_key(item[1]):
			_dict.update({item[1]: result_dict})
		_dict[item[1]][item[0].hour] +=1
	final_dict = create_result(_dict, 'hour')
	
	return final_dict


def create_result(result_dict, type='hour'):
	"""creating result data for output
	"""
	
	final_dict = {'date':range(24), 'type':type, 'location':[]}
	locations = []
	print result_dict
	for key, value in result_dict.iteritems():
		term_dict = {'data':[]}
		term_dict.update({'name':key})
		for value_key, value_value in value.iteritems():
			term_dict['data'].append(value_value)
		final_dict['location'].append(term_dict)
	return final_dict
