
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

    result     = {}
    main_data  = data_dict(request.GET)
    project_id = main_data['pro_cen_mapping'][0][0]
    center_id  = main_data['pro_cen_mapping'][1][0]
    dates      = main_data['dates']

    if len(dates) > 1:
        raw_query = RawTable.objects.filter(project=project_id,center=center_id,date__range=[dates[0],dates[-1]])
    else:
        raw_query = RawTable.objects.filter(project=project_id,center=center_id,date=dates[0])
    packets          = raw_query.values_list('work_packet',flat=True).distinct()
    agents           = raw_query.values_list('employee_id',flat=True).distinct()
    prodution        = raw_query.aggregate(Sum('per_day'))
    total_production = prodution['per_day__sum']
    
    packets_result, packet_data = get_the_packet_and_agent_data(packets,dates,project_id,center_id,filter_type='packets')
    result['config_packets']    = packets_result
    result['packets']           = packet_data['packets']
    result['packet_value']      = packet_data['packetsvalue']
    result['packet_details']    = packet_data['packets_details']
    
    agents_result, agent_data   = get_the_packet_and_agent_data(agents,dates,project_id,center_id,filter_type='agents')
    result['config_agents']     = agents_result
    result['agents']            = agent_data['agents']
    result['agent_value']       = agent_data['agentsvalue']
    result['agent_details']     = agent_data['agents_details']

    result['total_production']  = total_production
    return JsonResponse(result) 


def get_the_packet_and_agent_data(required_data,dates,project_id,center_id,filter_type):

    ####===generates the output for displaying top5 packets and agents based on historical data===####

    packet_or_agent_config = {}
    
    data_list   = []
    
    if filter_type  == 'packets':
        config_value = Project.objects.get(id=project_id,center=center_id).no_of_packets
        query_field  = 'work_packet'
    else:
        config_value = Project.objects.get(id=project_id,center=center_id).no_of_agents
        query_field  = 'employee_id'

    result, details  = generate_accuracy_for_packet_and_agent(required_data,project_id,center_id,dates,query_field)
    sorted_data      = (sorted(result.items(), key=itemgetter(1)))[:config_value]
    sorted_names     = [re.sub(r'[^\x00-\x7F]+',' ', names[0]) for names in sorted_data]
    for name in required_data:
        if name not in sorted_names:
            data_list.append(re.sub(r'[^\x00-\x7F]+',' ', name))
    packet_or_agent_config[filter_type] = data_list
    packet_or_agent_config[filter_type+'value'] = config_value
    packet_or_agent_config[filter_type+'_details'] = details
    return sorted_names, packet_or_agent_config


def generate_accuracy_for_packet_and_agent(required_data,project_id,center_id,dates,query_field):

    packet_or_agent_error = {}

    packet_or_agent_details = {}

    dates_lists = generate_required_dates(dates, [15,30,60,90])
    values      = [1, 0.5, 0.25, 0.125]
    
    for name in required_data:
        field_accuracy, audited_list, error_list, names_list = [], [], [], []
        for date_values, factor in zip(dates_lists,values):
            query_dict           = {'project':project_id,'center':center_id,'date__range':[date_values[-1],date_values[0]],query_field:name}
            internal_data        = Internalerrors.objects.filter(**query_dict)
            external_data        = Externalerrors.objects.filter(**query_dict)
            internal_errors      = internal_data.aggregate(Sum('total_errors'))
            internal_audits      = internal_data.aggregate(Sum('audited_errors'))
            external_errors      = external_data.aggregate(Sum('total_errors'))
            external_audits      = external_data.aggregate(Sum('audited_errors'))
            internal_packets     = internal_data.values_list('work_packet',flat=True).distinct()
            external_packets     = external_data.values_list('work_packet',flat=True).distinct()
            internal_agents      = internal_data.values_list('employee_id',flat=True).distinct()
            external_agents      = external_data.values_list('employee_id',flat=True).distinct()
            audit_value, error_value, external_aduit_value, external_error_value = 0, 0, 0, 0
            
            if (name in internal_packets) or (name in internal_agents):
                error_value          = internal_errors['total_errors__sum'] if internal_errors['total_errors__sum'] is not None else 0
                audit_value          = internal_audits['audited_errors__sum'] if internal_audits['audited_errors__sum'] is not None else 0
                if audit_value <= 0:
                    audit_value = prodution_accuracy_generation(date_values,project_id,name,query_field)
            if (name in external_packets) or (name in external_agents):
                external_aduit_value = external_audits['audited_errors__sum'] if external_audits['audited_errors__sum'] is not None else 0
                external_error_value = external_errors['total_errors__sum'] if external_errors['total_errors__sum'] is not None else 0
                if external_aduit_value <= 0:
                    external_aduit_value = prodution_accuracy_generation(date_values,project_id,name,query_field)
            
            if ((name in internal_packets) or (name in external_packets)) or ((name in internal_agents) or (name in external_agents)):
                final_audit  = audit_value + external_aduit_value
                final_errors = error_value + external_error_value

                audited_list.append(final_audit)
                error_list.append(final_errors)

                if final_audit:
                    accuracy = 1 - (float(final_errors)/final_audit)
                    accuracy = accuracy*factor
                else:
                    accuracy = 1

                field_accuracy.append(accuracy)
                packet_or_agent_error.update({name: round(sum(field_accuracy),2)})
            
            if ((name not in internal_packets) and (name not in external_packets) and (query_field == 'work_packet')) or \
                ((name not in internal_agents) and (name not in external_agents) and (query_field == 'employee_id')):
                final_audit  = audit_value + external_aduit_value
                final_errors = error_value + external_error_value
                if final_audit:
                    accuracy = 1 - (float(final_errors)/final_audit)
                    accuracy = accuracy*factor
                else:
                    accuracy = 1*factor
                audited_list.append(final_audit)
                error_list.append(final_errors)
                field_accuracy.append(accuracy)
        names_list.append(name)
        name = re.sub(r'[^\x00-\x7F]+',' ', name)
        packet_or_agent_details.update({query_field:name, name+'_audited':audited_list, name+'_error':error_list,\
                name+'_accuracy':field_accuracy, name+'_final':round(sum(field_accuracy),2)})

    final_details = {}
    for packet_or_agent in required_data:
        packet_or_agent = re.sub(r'[^\x00-\x7F]+',' ', packet_or_agent)
        if sum(packet_or_agent_details[packet_or_agent+'_audited']):
            final_details[packet_or_agent+'_audited']  = packet_or_agent_details[packet_or_agent+'_audited']
            final_details[packet_or_agent+'_final']    = packet_or_agent_details[packet_or_agent+'_final']
            final_details[packet_or_agent+'_error']    = packet_or_agent_details[packet_or_agent+'_error']
            final_details[packet_or_agent+'_accuracy'] = packet_or_agent_details[packet_or_agent+'_accuracy']

    return packet_or_agent_error, final_details


def prodution_accuracy_generation(date_values,project_id,name,query_field):


    per_day_value     = 0

    query_dict        = {'project':project_id,'date__range':[date_values[-1],date_values[0]],query_field:name}

    work_done         = RawTable.objects.filter(**query_dict).aggregate(Sum('per_day'))
    per_day_value     = work_done['per_day__sum']
    
    if per_day_value != None:
        per_day_value = per_day_value

    return per_day_value


def generate_required_dates(dates, required_dates):

    ####======generates past 15, 30, 60 and 90 dates based on current database date=====####

    dates       = dates[0]
    
    check_date  = date(*map(int, dates.split('-')))
    dates_lists = [list(), list(), list(), list()]
    
    for index, date_value in enumerate(required_dates):
        for day in range(0, date_value):
            dates_lists[index].append((check_date - dt.timedelta(day)).strftime('%Y-%m-%d'))
    
    return dates_lists
    

def packet_agent_audit_random(request):

    ###=====claculation of audit%=====###

    result = {}
    data_dict         = ast.literal_eval(request.POST.keys()[0])
    
    packets           = data_dict.get('packets', "")
    agents            = data_dict.get('agents', "")
    start_date        = data_dict.get('from', "")
    end_date          = data_dict.get('to', "")
    project           = data_dict.get('project', "")
    center            = data_dict.get('center', "").split(' - ')[0]
    workdone_value    = int(data_dict.get('total_production', ""))
    audited_value     = int(data_dict.get('audit_value', 0))
    random_value      = int(data_dict.get('random_value', 0))
    project_id        = Project.objects.get(name=project).id
    center_id         = Center.objects.get(name=center).id
    
    k, t, l = 0, 0, 0
    audit_and_case_value, audit_or_case_value = 0, 0
 
    audit_and_case_dict, random_dict, common_dict = OrderedDict(), OrderedDict(), OrderedDict()
    audit_or_case_dict = OrderedDict()
    production_records = RawTable.objects.filter(project=project_id,center=center_id,date=start_date)

    for i in xrange(len(production_records)):
        agent       = re.sub(r'[^\x00-\x7F]+',' ', production_records[i].employee_id)
        work_done   = production_records[i].per_day
        sub_project = production_records[i].sub_project
        work_packet = production_records[i].work_packet
        sub_packet  = production_records[i].sub_packet

        data = {"work_done":work_done,"sub_project":sub_project,"work_packet":work_packet,\
                "sub_packet":sub_packet,"agent":agent,"date":start_date}
            
        if ((work_packet in packets) and (agent in agents)) and (audited_value):
            audit_and_case_value   += work_done
            audit_and_case_dict[k]  = data
            k += 1
        else:
            common_dict[t]          = data
            t += 1
        
    random_index = 0
    for index in xrange(len(common_dict)):
        work_packet = common_dict[index]["work_packet"]
        agent       = re.sub(r'[^\x00-\x7F]+',' ', common_dict[index]["agent"])
        work_done   = common_dict[index]["work_done"]
        sub_project = common_dict[index]["sub_project"]
        sub_packet  = common_dict[index]["sub_packet"]

        _data = {"work_done":work_done,"sub_project":sub_project,"work_packet":work_packet,\
                "sub_packet":sub_packet,"agent":agent,"date":start_date}
        
        if ((work_packet in packets) or (agent in agents)) and (audited_value):
            audit_or_case_value      += work_done
            audit_or_case_dict[l]     = _data
            l += 1
        else:
            random_dict[random_index] = common_dict[index]
            random_index += 1
   
    if audited_value:        
        if audit_and_case_value > audited_value:
            result['audit'] = generate_and_case_calculation_for_intelligent_audit(audited_value,audit_and_case_dict,\
                audit_and_case_value)
        else:
            result['audit'] = generate_or_case_calculation_for_intelligent_audit(audited_value,audit_and_case_value,\
                                audit_or_case_value,audit_or_case_dict,audit_and_case_dict)
        
    if random_value:
        result['random']    = generate_random_data(random_dict,random_value)

    return JsonResponse(result)


def generate_and_case_calculation_for_intelligent_audit(audited_value,audit_and_case_dict,and_case_value):

    
    and_percentage = round((float(audited_value)/and_case_value)*100)

    for index in xrange(len(audit_and_case_dict)):
        work_done  = round((float(and_percentage)/100) * audit_and_case_dict[index]['work_done'])
        if work_done:
            audit_and_case_dict[index].update({'work_done': work_done})
    return audit_and_case_dict


def generate_or_case_calculation_for_intelligent_audit(audited_value,and_case_value,or_case_value,audit_or_case_dict,audit_and_case_dict):
    
    or_percentage = round((float(audited_value-and_case_value)/(or_case_value))*100)
    k             = len(audit_and_case_dict.keys())
    check_value   = or_case_value + and_case_value

    if check_value > audited_value:
        for index in xrange(len(audit_or_case_dict)):
            work_done = round((float(or_percentage)/100) * audit_or_case_dict[index]['work_done'])
            if work_done:
                audit_or_case_dict[index].update({'work_done': work_done})
                audit_and_case_dict[k] = audit_or_case_dict[index]
                k += 1
        return audit_and_case_dict
    else:
        return "Please select either packets or agents Or select low random value to audit the samples"


def generate_random_data(random_dict,random_value):

    ###==== Random data generation ====###

    from random import *

    _dict = OrderedDict()
    total = 0
    keys  = random_dict.keys()
    for index in xrange((len(random_dict))-1):
        if total <= random_value: 
            value             = int(round(random() * len(random_dict)))
            if value in keys:
                _dict[index]  = random_dict[value]
                done_value    = random_dict[value]["work_done"]
                total        += done_value
        else:
            break
    
    if total >= random_value:
        return _dict
    else:
        return "Please Select Low Random Value"


def generate_excel_for_audit_data(request):

    ##=====generates agents and packets data in excel=====##
    if request.method == 'POST':
        data           = ast.literal_eval(request.POST.keys()[0])['excel_data']
        packet_details = ast.literal_eval(request.POST.keys()[0])['packet_details']
        agent_details  = ast.literal_eval(request.POST.keys()[0])['agent_details']
        workbook       = xlsxwriter.Workbook('audit_data.xlsx')                                                                                                                                                                                                                                                                                                                                                                                            
        bold           = workbook.add_format({'bold': True})
        worksheet      = workbook.add_worksheet('audit_data')
        worksheet_1    = workbook.add_worksheet('calculation')
        audit_dict     = data.get('audit','')
        random_dict    = data.get('random','')
        worksheet.write('A'+str(2), 'Date', bold)
        worksheet.write('B'+str(2), 'Emp Name', bold)
        worksheet.write('C'+str(2), 'Sub Project', bold)
        worksheet.write('D'+str(2), 'Work Packet', bold)
        worksheet.write('E'+str(2), 'Sub Packet', bold)
        worksheet.write('F'+str(2), 'Audit count',bold)
        if audit_dict:
            worksheet_1.write('A'+str(1), 'Work Packet', bold)
            worksheet_1.write('A'+str(3), 'Name', bold)
            worksheet_1.write('B'+str(2), '15', bold)
            worksheet_1.write('E'+str(2), '30', bold)
            worksheet_1.write('H'+str(2), '60', bold)
            worksheet_1.write('K'+str(2), '90', bold)
            worksheet_1.write('B'+str(3), 'Audited', bold)
            worksheet_1.write('C'+str(3), 'Errors', bold)
            worksheet_1.write('D'+str(3), 'Accuracy', bold)
            worksheet_1.write('E'+str(3), 'Audited', bold)
            worksheet_1.write('F'+str(3), 'Errors', bold)
            worksheet_1.write('G'+str(3), 'Accuracy', bold)
            worksheet_1.write('H'+str(3), 'Audited', bold)
            worksheet_1.write('I'+str(3), 'Errors', bold)
            worksheet_1.write('J'+str(3), 'Accuracy', bold)
            worksheet_1.write('K'+str(3), 'Audited', bold)
            worksheet_1.write('L'+str(3), 'Errors', bold)
            worksheet_1.write('M'+str(3), 'Accuracy', bold)
            worksheet_1.write('O'+str(3), 'Calculation', bold)

            packet_names, agent_names = [], []
            
            for name in packet_details.keys():
                if name != 'work_packet':
                    packet_names.append(name.split('_')[0])
            packet_names = set(packet_names)

            for name in agent_details.keys():
                if name != 'employee_id':
                    agent_names.append(name.split('_')[0])
            agent_names  = set(agent_names)

            v = 4
            for name in packet_names:
                audited  = packet_details[name+'_audited']
                errors   = packet_details[name+'_error']
                accuracy = packet_details[name+'_accuracy']
                final    = packet_details[name+'_final']
                worksheet_1.write('A'+str(v), name)
                worksheet_1.write('B'+str(v), audited[0])
                worksheet_1.write('C'+str(v), errors[0])
                worksheet_1.write('D'+str(v), accuracy[0])
                worksheet_1.write('E'+str(v), audited[1])
                worksheet_1.write('F'+str(v), errors[1])
                worksheet_1.write('G'+str(v), accuracy[1])
                worksheet_1.write('H'+str(v), audited[2])
                worksheet_1.write('I'+str(v), errors[2])
                worksheet_1.write('J'+str(v), accuracy[2])
                worksheet_1.write('K'+str(v), audited[3])
                worksheet_1.write('L'+str(v), errors[3])
                worksheet_1.write('M'+str(v), accuracy[3])
                worksheet_1.write('O'+str(v), final)
                v += 1

            worksheet_1.write('A'+str(v+1), 'Agents', bold)        
            m = v + 2
            
            for name in agent_names:
                audited  = agent_details[name+'_audited']
                errors   = agent_details[name+'_error']
                accuracy = agent_details[name+'_accuracy']
                final    = agent_details[name+'_final']
                worksheet_1.write('A'+str(m), name)
                worksheet_1.write('B'+str(m), audited[0])
                worksheet_1.write('C'+str(m), errors[0])
                worksheet_1.write('D'+str(m), accuracy[0])
                worksheet_1.write('E'+str(m), audited[1])
                worksheet_1.write('F'+str(m), errors[1])
                worksheet_1.write('G'+str(m), accuracy[1])
                worksheet_1.write('H'+str(m), audited[2])
                worksheet_1.write('I'+str(m), errors[2])
                worksheet_1.write('J'+str(m), accuracy[2])
                worksheet_1.write('K'+str(m), audited[3])
                worksheet_1.write('L'+str(m), errors[3])
                worksheet_1.write('M'+str(m), accuracy[3])
                worksheet_1.write('O'+str(m), final)
                m += 1

        if audit_dict:
            worksheet.write('A'+str(1), 'Intelligent sampling', bold)
            i = 3
            k = 0
            
            for data in xrange(len(audit_dict)):
                worksheet.write('A'+str(i), audit_dict[str(k)]["date"])
                worksheet.write('B'+str(i), audit_dict[str(k)]["agent"].decode('utf-8'))
                worksheet.write('C'+str(i), audit_dict[str(k)]["sub_project"])
                worksheet.write('D'+str(i), audit_dict[str(k)]["work_packet"])
                worksheet.write('E'+str(i), audit_dict[str(k)]["sub_packet"])
                worksheet.write('F'+str(i), audit_dict[str(k)]["work_done"])
                i += 1
                k += 1
                
        if random_dict != '' and audit_dict == '':
            worksheet.write('A'+str(1), 'Random sampling', bold)
            t, _index = 3, 0
            for data in xrange(len(random_dict)):
                worksheet.write('A'+str(t), random_dict[str(_index)]["date"])
                worksheet.write('B'+str(t), random_dict[str(_index)]["agent"].decode('utf-8'))
                worksheet.write('C'+str(t), random_dict[str(_index)]["sub_project"])
                worksheet.write('D'+str(t), random_dict[str(_index)]["work_packet"])
                worksheet.write('E'+str(t), random_dict[str(_index)]["sub_packet"])
                worksheet.write('F'+str(t), random_dict[str(_index)]["work_done"])
                t += 1
                _index += 1

        elif random_dict != '' and audit_dict != '':
            worksheet.write('A'+str(k+4), 'Random sampling', bold)
            t = i + 2
            _index = 0  
            for data in xrange(len(random_dict)):
                worksheet.write('A'+str(t), random_dict[str(_index)]["date"])
                worksheet.write('B'+str(t), random_dict[str(_index)]["agent"].decode('utf-8'))
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