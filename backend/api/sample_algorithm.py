
from django.http import HttpResponse, JsonResponse

import datetime as dt
from datetime import date
from operator import itemgetter

from api.basics import *
from api.commons import data_dict
from api.models import Project, Center, RawTable, Internalerrors


def packet_agent_data(request):

	result = {}

	main_data = data_dict(request.GET)
	project_id = main_data['pro_cen_mapping'][0][0]
	center_id = main_data['pro_cen_mapping'][1][0]
	dates = main_data['dates']
	
	if len(dates) > 1:
		raw_query = RawTable.objects.filter(project=project_id,center=center_id,date__range=[dates[0],dates[-1]])
	else:
		raw_query = RawTable.objects.filter(project=project_id,center=center_id,date=dates[0])
	packets = raw_query.values_list('work_packet',flat=True).distinct()
	agents = raw_query.values_list('employee_id',flat=True).distinct()

	packets_result = get_the_packet_and_agent_data(packets,dates,project_id,center_id,filter_type='work_packet')
	result['packets'] = packets_result
	agents_result = get_the_packet_and_agent_data(agents,dates,project_id,center_id,filter_type='employee_id')
	result['agents'] = agents_result
	
	return JsonResponse(result)


def get_the_packet_and_agent_data(required_data,dates,project_id,center_id,filter_type):

	result_dict = {}
	result = {}

	dates_lists = generate_required_dates(dates, [15,30,60,90])

	values = [1, 0.5, 0.25, 0.125]
	for data in required_data:
		for date_values, factor in zip(dates_lists,values):
			if filter_type == 'work_packet':
				internal_data = Internalerrors.objects.filter(project=project_id,center=center_id,\
					work_packet=data,date__range=[date_values[-1],date_values[0]])
				config_value = Project.objects.get(id=project_id,center=center_id).no_of_packets
			else:
				internal_data = Internalerrors.objects.filter(project=project_id,center=center_id,\
					employee_id=data,date__range=[date_values[-1],date_values[0]])
				config_value = Project.objects.get(id=project_id,center=center_id).no_of_agents
			errors = internal_data.aggregate(Sum('total_errors'))
			audited = internal_data.aggregate(Sum('audited_errors'))

			if errors['total_errors__sum'] != None and audited['audited_errors__sum'] != None:
				error_value = (float(errors['total_errors__sum'])/float(audited['audited_errors__sum']))
			else:
				error_value = 0
			if result_dict.has_key(data):
				result_dict[data].append(round((factor*error_value), 2))
			else:
				result_dict[data] = [round((factor*error_value), 2)]

	for key,value in result_dict.iteritems():
		result[key] = sum(value)

	sorted_data = (sorted(result.items(), key=itemgetter(1)))[-config_value:]
	sorted_names = [names[0] for names in sorted_data]
	sorted_names.reverse()
	return sorted_names


def generate_required_dates(dates, required_dates):

	dates = dates[0]
	check_date = date(*map(int, dates.split('-')))
	dates_lists = [list(), list(), list(), list()]
    
	for index, date_value in enumerate(required_dates):
		for day in range(0, date_value):
			dates_lists[index].append((check_date - dt.timedelta(day)).strftime('%Y-%m-%d'))
	
	return dates_lists



