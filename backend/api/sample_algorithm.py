
from django.http import HttpResponse, JsonResponse

import datetime as dt
import xlsxwriter
from xlsxwriter.workbook import Workbook
from datetime import date
from operator import itemgetter
import ast

from api.basics import *
from api.commons import data_dict
from api.models import Project, Center, RawTable, Internalerrors
from django.utils.encoding import smart_str


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
    prodution = raw_query.aggregate(Sum('per_day'))
    total_production = prodution['per_day__sum']

    packets_result, packet_data = get_the_packet_and_agent_data(packets,dates,project_id,center_id,filter_type='packet')
    result['config_packets'] = packets_result
    result['packets'] = packet_data['packets']
    result['packet_value'] = packet_data['packetvalue']

    agents_result, agent_data = get_the_packet_and_agent_data(agents,dates,project_id,center_id,filter_type='agent')
    result['config_agents'] = agents_result
    result['agents'] = agent_data['agents']
    result['agent_value'] = agent_data['agentvalue']

    result['total_production'] = total_production
    return JsonResponse(result) 


def get_the_packet_and_agent_data(required_data,dates,project_id,center_id,filter_type):

    ####===generates the output for displaying top5 packets and agents based on historical data===####

    result_dict = {}
    result = {}

    values_dict = {}

    data_list = []
    dates_lists = generate_required_dates(dates, [15,30,60,90])

    values = [1, 0.5, 0.25, 0.125]
    for data in required_data:
        for date_values, factor in zip(dates_lists,values):
            if filter_type == 'packet':
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
    values_dict[filter_type+'value'] = config_value
    for name in required_data:
        if name not in sorted_names:
            data_list.append(name)
    values_dict[filter_type+'s'] = data_list
    return sorted_names, values_dict


def generate_required_dates(dates, required_dates):

    ####======generates past 15, 30, 60 and 90 dates based on current database date=====####

    dates = dates[0]
    check_date = date(*map(int, dates.split('-')))
    dates_lists = [list(), list(), list(), list()]
    
    for index, date_value in enumerate(required_dates):
        for day in range(0, date_value):
            dates_lists[index].append((check_date - dt.timedelta(day)).strftime('%Y-%m-%d'))
    
    return dates_lists


def get_intelligent_audit_value(request):

    ###====  Calculates the audit production value for the selected audit percentage ====###

    audit_percentage = request.GET.get('audit_val','')
    production_value = request.GET.get('total_production','')

    if audit_percentage:
        audit_value = (float(audit_percentage)/100)*int(production_value)
    else:
        audit_value = 'Intelligence audit value not selected'

    return JsonResponse(audit_value, safe=False)


def get_random_audit_value(request):

    ###====  Calculates the random production value for the selected random percentage ====###

    random_percentage = request.GET.get('random_val','')
    production_value = request.GET.get('total_production','')

    if random_percentage:
        random_value = (float(random_percentage)/100)*int(production_value)
    else:
        random_value = 'Random audit value not selected'
    
    return JsonResponse(random_value, safe=False)


def packet_agent_audit_random(request):

    ###=====claculation of audit%=====###

    result = {}
    data_dict = ast.literal_eval(request.POST.keys()[0])

    audit_value = data_dict.get('audit', "")
    random_value = data_dict.get('random', "")
    packets = data_dict.get('packets', "")
    agents = data_dict.get('agents', "")
    start_date = data_dict.get('from', "")
    end_date = data_dict.get('to', "")
    project = data_dict.get('project', "")
    center = data_dict.get('center', "").split(' - ')[0]
    workdone_value = data_dict.get('total_production', "")
    
    project_id = Project.objects.get(name=project).id
    center_id = Center.objects.get(name=center).id

    workdone_value = RawTable.objects.filter(project=project_id,center=center_id,\
            date=start_date).aggregate(Sum('per_day'))
    workdone_value = workdone_value['per_day__sum']

    if audit_value:
        audited_percentage_value = (float(audit_value)/100)*(workdone_value)
    if random_value:
        random_percentage_value = (float(random_value)/100)*(workdone_value)

    k, t, total = 0, 0, 0

    audit_dict, random_dict = {}, {}

    production_records = RawTable.objects.filter(project=project_id,center=center_id,date=start_date)

    for i in xrange(len(production_records)):
        agent = production_records[i].employee_id
        work_done = production_records[i].per_day
        sub_project = production_records[i].sub_project
        work_packet = production_records[i].work_packet
        sub_packet = production_records[i].sub_packet

        data = {"work_done":work_done,"sub_project":sub_project,"work_packet":work_packet,\
                "sub_packet":sub_packet,"agent":agent,"date":start_date}

        if ((work_packet in packets) and (agent in agents)) or (work_packet in packets) or (agent in agents):
            audit_dict[k] = data
            k += 1
        else:
            random_dict[t] = data
            t += 1

    total_value = 0
    
    for i in xrange(len(audit_dict)):
        value = audit_dict[i]["work_done"]
        total_value += value

    if total_value >= audited_percentage_value:
        result['audit'] = audit_dict
    else:
        result['audit'] = "Please add more Packets and Agents"
    
    if random_value:
        result['random'] = generate_random_data(random_dict,random_percentage_value)

    return JsonResponse(result)


def generate_random_data(random_dict,random_value):

    from random import *

    _dict = {}
    k = 0
    total, total_value = 0, 0
    keys = random_dict.keys()
    
    for i in xrange(len(random_dict)): 
        value = round(random() * len(random_dict))
        if k in keys:
            _dict[k] = random_dict[value]
            check_value = random_dict[value]["work_done"]
            if total <= random_value:
                total += check_value
                k += 1

    for i in xrange(len(_dict)):
        value = _dict[i]["work_done"]
        total_value += value
    
    if total_value >= random_value:
        return _dict
    else:
        return "Please Select More Random Value"


def generate_excel_for_audit_data(request):

    ##=====generates agents and packets data in excel=====##
    if request.method == 'POST':
        data = ast.literal_eval(request.POST.keys()[0])
        workbook = xlsxwriter.Workbook('audit_data.xlsx')
        bold = workbook.add_format({'bold': True})
        worksheet = workbook.add_worksheet('audit_data')
        audit_dict = data.get('audit','')
        random_dict = data.get('random','')

        worksheet.write('A'+str(1), 'Intelligent sampling', bold)
        worksheet.write('A'+str(2), 'Date', bold)
        worksheet.write('B'+str(2), 'Emp Name', bold)
        worksheet.write('C'+str(2), 'Sub Project', bold)
        worksheet.write('D'+str(2), 'Work Packet', bold)
        worksheet.write('E'+str(2), 'Sub Packet', bold)
        worksheet.write('F'+str(2), 'Audit count',bold)
        i = 3
        k = 0
        
        for data in xrange(len(audit_dict)):
            worksheet.write('A'+str(i), audit_dict[str(k)]["date"])
            worksheet.write('B'+str(i), audit_dict[str(k)]["agent"])
            worksheet.write('C'+str(i), audit_dict[str(k)]["sub_project"])
            worksheet.write('D'+str(i), audit_dict[str(k)]["work_packet"])
            worksheet.write('E'+str(i), audit_dict[str(k)]["sub_packet"])
            worksheet.write('F'+str(i), audit_dict[str(k)]["work_done"])
            i += 1
            k += 1
        
        worksheet.write('A'+str(k+4), 'Random sampling', bold)
        t = i + 2
        _index = 0    
        for data in xrange(len(random_dict)):
            worksheet.write('A'+str(t), random_dict[str(_index)]["date"])
            worksheet.write('B'+str(t), random_dict[str(_index)]["agent"])
            worksheet.write('C'+str(t), random_dict[str(_index)]["sub_project"])
            worksheet.write('D'+str(t), random_dict[str(_index)]["work_packet"])
            worksheet.write('E'+str(t), random_dict[str(_index)]["sub_packet"])
            worksheet.write('F'+str(t), random_dict[str(_index)]["work_done"])
            t += 1
            _index += 1

        workbook.close()
        with open('audit_data.xlsx', 'rb')as xl:
            xl_data = xl.read();

        response = HttpResponse(xl_data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=%s' % ('audit_data.xlsx')
        return response
    else:
        return HttpResponse('Please use the post method to send the data.')