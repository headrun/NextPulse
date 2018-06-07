
from django.http import HttpResponse, JsonResponse

import datetime as dt
import xlsxwriter
from datetime import date
from operator import itemgetter

from api.basics import *
from api.commons import data_dict
from api.models import Project, Center, RawTable, Internalerrors


def historical_packet_agent_data(request):

    ###====return the json response of agents and packets data====###

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

    ####===generates the output for displaying top5 packets and agents based on historical data===####

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

    ####======generates past 15, 30, 60 and 90 dates based on current database date=====####

    dates = dates[0]
    check_date = date(*map(int, dates.split('-')))
    dates_lists = [list(), list(), list(), list()]
    
    for index, date_value in enumerate(required_dates):
        for day in range(0, date_value):
            dates_lists[index].append((check_date - dt.timedelta(day)).strftime('%Y-%m-%d'))
    
    return dates_lists


def packet_agent_audit_random(request):

    ###=====claculation of audit%=====###

    result = {}

    audit_value = eval(request.POST['json']).get('audit', "")
    packets = eval(request.POST['json']).get('packets', "")
    agents = eval(request.POST['json']).get('agents', "")
    start_date = eval(request.POST['json']).get('from', "")
    end_date = eval(request.POST['json']).get('to', "")
    project = eval(request.POST['json']).get('project', "")
    center = eval(request.POST['json']).get('center', "").split(' - ')[0]

    project_id = Project.objects.get(name=project).id
    center_id = Center.objects.get(name=center).id

    workdone_value = RawTable.objects.filter(project=project_id,center=center_id,\
            date=start_date).aggregate(Sum('per_day'))
    workdone_value = workdone_value['per_day__sum']

    audited_percentage_value = (float(audit_value)/100)*(workdone_value)

    i, k, total = 0, 0, 0

    for agent in agents:
        if total <= audited_percentage_value:
            agent_workdone = RawTable.objects.filter(project=project_id,center=center_id,date=start_date,\
                employee_id=agents[i]).aggregate(Sum('per_day'))
            total += agent_workdone['per_day__sum']
            result[agents[i]] = agent_workdone['per_day__sum']
            i += 1
            if total < audited_percentage_value:
                for packet in packets:
                    packet_workdone = RawTable.objects.filter(project=project_id,center=center_id,\
                        date=start_date,work_packet=packets[k]).aggregate(Sum('per_day'))
                    total += packet_workdone['per_day__sum']
                    result[packets[k]] = packet_workdone['per_day__sum']
                    k += 1
                    break
    return JsonResponse(result)


def generate_excel_for_audit_data(request):

    ##=====generates agents and packets data in excel=====##

    workbook = xlsxwriter.Workbook('audit_data.xlsx')
    worksheet = workbook.add_worksheet()

    i = 1
    for key, value in data.iteritems():
        worksheet.write('A'+str(i), key)
        worksheet.write('B'+str(i), value)
        i +=1
    workbook.close()



