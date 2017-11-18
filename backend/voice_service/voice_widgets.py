import datetime
from voice_service.models import *


def create_filters(filter_params):
	""" creating filters for voice """

	filter_dict = {}
	for item in filter_params:
		for key, value in item.iteritems():
			if value:
				_key = '%s__in' %key
				filter_dict.update(_key:value)

	return filter_dict 


def get_hourly_sum(project, dates, table_name, location={}, skill={}, disposition={}):
	""" take hourly summary of a selected date range """

	result_dict = {}
	filter_param = create_filters([location, skill, disposition, project, dates])

	for time in xrange(0, 24):
		result_dict.update({time : 0})

	data_set = table_name.objects.filter(**filter_param).values_list('start_time', flat=True)
	for item in data_set:
		result_dict[item.hour] +=1

	return result_dict






