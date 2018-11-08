
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
        raw_query    = RawTable.objects.filter(project=project_id,center=center_id,date__range=[dates[0],dates[-1]])
    else:
        raw_query    = RawTable.objects.filter(project=project_id,center=center_id,date=dates[0])
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
    
    if filter_type  == 'packets':
        config_value = Project.objects.get(id=project_id,center=center_id).no_of_packets
        query_field  = 'work_packet'
    else:
        config_value = Project.objects.get(id=project_id,center=center_id).no_of_agents
        query_field  = 'employee_id'

    result, details  = generate_accuracy_for_packet_and_agent(required_data,project_id,center_id,dates,query_field,config_value)
    sorted_data      = (sorted(result.items(), key=itemgetter(1)))
    sorted_names     = [re.sub(r'[^\x00-\x7F]+',' ', names[0]) for names in sorted_data]
    remaining_names  = sorted_names[config_value:]
    packet_or_agent_config[filter_type] = remaining_names
    packet_or_agent_config[filter_type+'value'] = config_value
    packet_or_agent_config[filter_type+'_details'] = details
    return sorted_names[:config_value], packet_or_agent_config


def generate_accuracy_for_packet_and_agent(required_data,project_id,center_id,dates,query_field,config_value):

    packet_or_agent_error, packet_or_agent_details = {}, {}
    
    dates_lists = generate_required_dates(dates, [90,60,30,15])
    values      = [0.125,0.25,0.5,1]
    config_percentage = Project.objects.get(id=project_id).external_audit_percentage
    external_config = 100 + config_percentage
    query_params = {'project': project_id,'center': center_id,'date__range': [dates_lists[0][-1],dates_lists[0][0]]}
    internal_query = Internalerrors.objects.filter(**query_params).values_list(query_field,flat=True).distinct()
    external_query = Externalerrors.objects.filter(**query_params).values_list(query_field,flat=True).distinct()    
    for name in required_data:    
        field_accuracy, int_accuracy_list, extnl_accuracy_list = [], [], []
        audit_list, error_list, ext_audit_list, ext_error_list = [], [], [], []
        
        for date_values, factor in zip(dates_lists,values):
            query_dict           = {'project':project_id,'center':center_id,'date__range':[date_values[-1],date_values[0]],query_field:name}
            internal_sub_query   = Internalerrors.objects.filter(**query_dict)
            external_sub_query   = Externalerrors.objects.filter(**query_dict)
            internal_errors      = internal_sub_query.aggregate(Sum('total_errors'))
            internal_audits      = internal_sub_query.aggregate(Sum('audited_errors'))
            external_errors      = external_sub_query.aggregate(Sum('total_errors'))
            external_audits      = external_sub_query.aggregate(Sum('audited_errors'))
            internal_check       = internal_sub_query.values_list(query_field,flat=True).distinct()
            external_check       = external_sub_query.values_list(query_field,flat=True).distinct()
            
            audit_value, error_value, external_audit_value, external_error_value = 0, 0, 0, 0

            if (name in internal_check):
                error_value          = internal_errors['total_errors__sum'] if internal_errors['total_errors__sum'] is not None else 0
                audit_value          = internal_audits['audited_errors__sum'] if internal_audits['audited_errors__sum'] is not None else 0
                if audit_value <= 0:
                    audit_value = prodution_accuracy_generation(date_values,project_id,name,query_field)
                internal_accuracy = 1 - (float(error_value)/audit_value)
                
            if (name in external_check):
                external_audit_value = external_audits['audited_errors__sum'] if external_audits['audited_errors__sum'] is not None else 0
                external_error_value = external_errors['total_errors__sum'] if external_errors['total_errors__sum'] is not None else 0
                if external_audit_value <= 0:
                    external_audit_value = prodution_accuracy_generation(date_values,project_id,name,query_field)
                ext_accuracy = 1 - (float(external_error_value)/external_audit_value)
                external_accuracy = (float(external_config)/100)*ext_accuracy
                            
            if (name in internal_check) and (name in external_check):
                accuracy_1 = internal_accuracy
                accuracy_2 = external_accuracy
                
            elif ((name in internal_check) and (name not in external_query)) or ((name in internal_check) and (name in external_query)):
                accuracy_1 = internal_accuracy
                accuracy_2 = 1*(float(external_config)/100)
            
            elif ((name in external_check) and (name not in internal_query)) or ((name in external_check) and (name in internal_query)):
                accuracy_1 = 1
                accuracy_2 = external_accuracy
                
            elif (name in internal_query) and (name in external_query) or ((name not in internal_query) and (name in external_query)) or \
                ((name not in external_query) and (name in internal_query)):
                accuracy_1 = 1
                accuracy_2 = 1*(float(external_config)/100)
                
            if (name in internal_query) or (name in external_query):
                accuracy  = (accuracy_1 + accuracy_2)*factor
                field_accuracy.append(accuracy)
                audit_list.append(audit_value)
                error_list.append(error_value)
                ext_audit_list.append(external_audit_value)
                ext_error_list.append(external_error_value)
                int_accuracy_list.append(accuracy_1)
                extnl_accuracy_list.append(accuracy_2)
                field_name = re.sub(r'[^\x00-\x7F]+',' ', name)
                packet_or_agent_error.update({field_name: sum(field_accuracy)})
                packet_or_agent_details.update({field_name+'_audited':audit_list,field_name+'_error':error_list,field_name+'_accuracy':int_accuracy_list,\
                field_name+'_final':sum(field_accuracy),field_name+'_extrnl_audited':ext_audit_list,field_name+'_extrnl_error':ext_error_list,\
                field_name+'_extrnl_accuracy':extnl_accuracy_list})

    return packet_or_agent_error, packet_or_agent_details


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
    remaining_packets = data_dict.get('remaining_packets', "")
    remaining_agents  = data_dict.get('remaining_agents', "")
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

    and_case_packets, and_case_agents = [], []

    audit_and_case_dict, random_dict, common_dict = OrderedDict(), OrderedDict(), OrderedDict()
    audit_or_case_dict = OrderedDict()
    production_records = RawTable.objects.filter(project=project_id,center=center_id,date=start_date)

    for i in range(len(production_records)):
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
            and_case_packets.append(work_packet)
            and_case_agents.append(agent)
            k += 1
        else:
            common_dict[t]          = data
            t += 1
    
    iterating_packets = list(set(packets) - set(and_case_packets))
    iterating_agents  = list(set(agents)  - set(and_case_agents))

    if (iterating_packets):
        packet_agent = [(packet, agent) for packet in iterating_packets for agent in remaining_agents]

        packet_list = []
        for data in packet_agent:
            if data[0] not in packet_list:
                for key, value in common_dict.iteritems():
                    if (data[0] == value['work_packet'] and data[1] == value['agent']):
                        audit_and_case_dict[k] = value
                        audit_and_case_value  += value["work_done"]
                        packet_list.append(data[0])
                        packet_agent = filter(lambda a: a[0] != data[0], packet_agent)
                        del common_dict[key]
                        k += 1
                        break

    if (iterating_agents):
        agent_packet = [(agent, packet) for agent in iterating_agents for packet in remaining_packets]

        agents_list = []
        for data in agent_packet:
            if data[0] not in agents_list:
                for key, value in common_dict.iteritems():
                    if (data[0] == value['agent'] and data[1] == value['work_packet']):
                        audit_and_case_dict[k] = value
                        audit_and_case_value  += value['work_done']
                        agents_list.append(data[0])
                        agent_packet = filter(lambda a: a[0] != data[0], agent_packet)
                        del common_dict[key]
                        k += 1
                        break

    random_index = 0
    for index in range(len(common_dict)):
        if (index in common_dict.keys()):
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
                                audit_and_case_dict,common_dict,packets,agents,remaining_packets,remaining_agents,k)
        
    if random_value:
        result['random']    = generate_random_data(random_dict,random_value)

    return JsonResponse(result)


def generate_and_case_calculation_for_intelligent_audit(audited_value,audit_and_case_dict,and_case_value):

    ### and percentage calculation ###

    and_percentage = round((float(audited_value)/and_case_value)*100)

    for index in xrange(len(audit_and_case_dict)):
        work_done  = round((float(and_percentage)/100) * audit_and_case_dict[index]['work_done'])
        if work_done:
            audit_and_case_dict[index].update({'work_done': work_done})
    return audit_and_case_dict


def generate_or_case_calculation_for_intelligent_audit(audited_value,and_case_value,audit_and_case_dict,common_dict,packets,agents,\
    remaining_packets,remaining_agents,next_index):

    packet_agent_keys = [(packets[0], agent) for agent in remaining_agents]
    agent_packet_keys = [(agents[0], packet) for packet in remaining_packets]
    
    for packet_agent in packet_agent_keys:
        if and_case_value <= audited_value:
            for key, value in common_dict.iteritems():
                if packet_agent[0] == value['work_packet'] and packet_agent[1] == value['agent']:
                    audit_and_case_dict[next_index] = value
                    and_case_value += value['work_done']
                    del common_dict[key]
                    next_index += 1
        
    for agent_packet in agent_packet_keys:
        if and_case_value <= audited_value:
            for key, value in common_dict.iteritems():
                if agent_packet[0] == value['agent'] and agent_packet[1] == value['work_packet']:
                    audit_and_case_dict[next_index] = value
                    and_case_value += value['work_done']
                    del common_dict[key]
                    next_index += 1

    if and_case_value >= audited_value:
        return audit_and_case_dict
    else: 
        packets.pop(0)
        agents.pop(0)
        if len(packets) != 0 and len(agents) != 0:
            return generate_or_case_calculation_for_intelligent_audit(audited_value,and_case_value,audit_and_case_dict,common_dict,packets,agents,\
                remaining_packets,remaining_agents,next_index)
        else:
            return "Select low random value or choose packets or agents to meet the sample"


def generate_random_data(random_dict,random_value):

    ###==== Random data generation ====###

    from random import *

    _dict, final_dict = OrderedDict(), OrderedDict()
    
    prev_value = 0

    for data in random_dict.values():
        data.update({'work_done': data['work_done'] + prev_value})
        prev_value = data['work_done']

    for number in range(0, random_value):
        random_number = int(round(random() * prev_value))
        for value in random_dict.values():
            if value['work_done'] >= random_number:
                _dict.update({number: value})
                break

    final_done = []
    index = 0 
    for value in _dict.values():
        if value['work_done'] not in final_done:
            value['count'] = 1
            final_dict.update({index: value})
            final_done.append(value['work_done'])
            index += 1
        else:
            value['count'] = value['count'] + 1
            final_dict.update({index: value})
            final_done.append(value['work_done'])
            del final_dict[index]
            index += 1
    return final_dict


def generate_excel_for_audit_data(request):

    ##=====generates agents and packets data in excel=====##
    if request.method == 'POST':
        
        data           = ast.literal_eval(request.POST.keys()[0])['excel_data']
        packet_details = ast.literal_eval(request.POST.keys()[0])['packet_details']
        agent_details  = ast.literal_eval(request.POST.keys()[0])['agent_details']
        project        = ast.literal_eval(request.POST.keys()[0])['project']
        start_date     = ast.literal_eval(request.POST.keys()[0])['date']
        end_date       = (date(*map(int, start_date.split('-'))) - dt.timedelta(90)).strftime('%Y-%m-%d')
        workbook       = xlsxwriter.Workbook('audit_data.xlsx')                                                                                                                                                                                                                                                                                                                                                                                            
        bold           = workbook.add_format({'bold': True})
        worksheet      = workbook.add_worksheet('audit_data')
        worksheet_1    = workbook.add_worksheet('calculation')
        worksheet_2    = workbook.add_worksheet('External')
        worksheet_3    = workbook.add_worksheet('Internal')
        audit_dict     = data.get('audit','')
        random_dict    = data.get('random','')
        audit_headers  = ['Date','Emp Name','Sub Project','Work Packet','Sub Packet','Audit count']
        auidt_letters  = ['A','B','C','D','E','F']
        audit_sample_data = ["date","agent","sub_project","work_packet","sub_packet","work_done"]
        random_sample_data = ["date","agent","sub_project","work_packet","sub_packet","count"]

        for header, letter in zip(audit_headers, auidt_letters):
            worksheet.write(letter+str(2), header, bold)
        
        numbers = ['15','30','60','90']
        number_letters = ['B','H','N','T']
        calculation_headers = ['Audited','Errors','Accuracy','Ext.Audited','Ext.Errors','Ext.Accuracy',\
                'Audited','Errors','Accuracy','Ext.Audited','Ext.Errors','Ext.Accuracy',\
                'Audited','Errors','Accuracy','Ext.Audited','Ext.Errors','Ext.Accuracy',\
                'Audited','Errors','Accuracy','Ext.Audited','Ext.Errors','Ext.Aaccuracy','Calculation']
        calculation_letters = ['B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
        letters_list = [['B','C','D','E','F','G'],['H','I','J','K','L','M'],['N','O','P','Q','R','S'],['T','U','V','W','X','Y','Z']]

        worksheet_1.write('A'+str(1), 'Work Packet', bold)
        worksheet_1.write('A'+str(3), 'Name', bold)
        for number, num_letter in zip(numbers, number_letters):
            worksheet_1.write(num_letter+str(2), number, bold)
        
        for header, letter in zip(calculation_headers, calculation_letters):
            worksheet_1.write(letter+str(3), header, bold)

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
            ext_audit = packet_details[name+'_extrnl_audited']
            ext_err   = packet_details[name+'_extrnl_error']
            extrnl_accuracy = packet_details[name+'_extrnl_accuracy']
            details_list = [[audited[3],errors[3],accuracy[3],ext_audit[3],ext_err[3],extrnl_accuracy[3]],\
                [audited[2],errors[2],accuracy[2],ext_audit[2],ext_err[2],extrnl_accuracy[2]],\
                [audited[1],errors[1],accuracy[1],ext_audit[1],ext_err[1],extrnl_accuracy[1]],\
                [audited[0],errors[0],accuracy[0],ext_audit[0],ext_err[0],extrnl_accuracy[0],final]]
            worksheet_1.write('A'+str(v), name)
            for details, letter in zip(details_list, letters_list):
                worksheet_1.write(letter[0]+str(v), details[0])
                worksheet_1.write(letter[1]+str(v), details[1])
                worksheet_1.write(letter[2]+str(v), details[2])
                worksheet_1.write(letter[3]+str(v), details[3])
                worksheet_1.write(letter[4]+str(v), details[4])
                worksheet_1.write(letter[5]+str(v), details[5])
                if len(details) != 6:
                    worksheet_1.write(letter[6]+str(v), details[6])

            v += 1
                
        worksheet_1.write('A'+str(v+1), 'Agents', bold)        
        m = v + 2
        
        for name in agent_names:
            audited  = agent_details[name+'_audited']
            errors   = agent_details[name+'_error']
            accuracy = agent_details[name+'_accuracy']
            final    = agent_details[name+'_final']
            ext_audit = agent_details[name+'_extrnl_audited']
            ext_err   = agent_details[name+'_extrnl_error']
            extrnl_accuracy = agent_details[name+'_extrnl_accuracy']
            agent_details_list = [[audited[3],errors[3],accuracy[3],ext_audit[3],ext_err[3],extrnl_accuracy[3]],\
                [audited[2],errors[2],accuracy[2],ext_audit[2],ext_err[2],extrnl_accuracy[2]],\
                [audited[1],errors[1],accuracy[1],ext_audit[1],ext_err[1],extrnl_accuracy[1]],\
                [audited[0],errors[0],accuracy[0],ext_audit[0],ext_err[0],extrnl_accuracy[0],final]]
            worksheet_1.write('A'+str(m), name)
            for details, letter in zip(agent_details_list, letters_list):
                worksheet_1.write(letter[0]+str(m), details[0])
                worksheet_1.write(letter[1]+str(m), details[1])
                worksheet_1.write(letter[2]+str(m), details[2])
                worksheet_1.write(letter[3]+str(m), details[3])
                worksheet_1.write(letter[4]+str(m), details[4])
                worksheet_1.write(letter[5]+str(m), details[5])
                if len(details) != 6:
                    worksheet_1.write(letter[6]+str(m), details[6])

            m += 1
                
        if audit_dict:
            worksheet.write('A'+str(1), 'Intelligent sampling', bold)
            i = 3
            k = 0
            
            for data in xrange(len(audit_dict)):
                for sample_name, letter in zip(audit_sample_data, auidt_letters):
                    worksheet.write(letter+str(i), audit_dict[str(k)][sample_name])
                i += 1
                k += 1
        
        if random_dict != '' and audit_dict == '':
            worksheet.write('A'+str(1), 'Random sampling', bold)
            t = 3
            for data in random_dict.values():
                for random_name, letter in zip(random_sample_data, auidt_letters):
                    worksheet.write(letter+str(t), data[random_name])
                t += 1

        elif random_dict != '' and audit_dict != '':
            worksheet.write('A'+str(k+4), 'Random sampling', bold)
            t = i + 2
            for data in random_dict.values():
                for random_name, letter in zip(random_sample_data, auidt_letters):
                    worksheet.write(letter+str(t), data[random_name])
                t += 1
    
        if audit_dict and random_dict:
            err_agent_details = set([value['agent'] for value in audit_dict.values()])
            err_agent_details.update(set([value['agent'] for value in random_dict.values()]))

        elif audit_dict:
            err_agent_details = set([value['agent'] for value in audit_dict.values()])

        elif random_dict:
            err_agent_details = set([value['agent'] for value in random_dict.values()])
        
        agent_error_details = generate_agent_internal_external_error_details(project,start_date,end_date,err_agent_details)
        if agent_error_details:     
            internal_details = agent_error_details['internal']
            external_details = agent_error_details['external']
            error_headers = ['Date','Emp Name','Sub Project','Work Packet','Sub Packet','Audited Count','Total Errors','Error Category','Error Count']
            error_cols = ['A','B','C','D','E','F','G','H','I']
            for col, header in zip(error_cols, error_headers):
                worksheet_2.write(col+str(1), header, bold)
                worksheet_3.write(col+str(1), header, bold)

            internal_cnt, external_cnt = 2, 2
            for value in external_details.values():
                worksheet_2.write('A'+str(external_cnt),value['date'])
                worksheet_2.write('B'+str(external_cnt),value['employee_id'])
                worksheet_2.write('C'+str(external_cnt),value['sub_project'])
                worksheet_2.write('D'+str(external_cnt),value['work_packet'])
                worksheet_2.write('E'+str(external_cnt),value['sub_packet'])
                worksheet_2.write('F'+str(external_cnt),value['audited_errors'])
                worksheet_2.write('G'+str(external_cnt),value['total_errors'])
                worksheet_2.write('H'+str(external_cnt),value['error_types'])
                worksheet_2.write('I'+str(external_cnt),value['error_values'])

                external_cnt += 1

            for value in internal_details.values():
                worksheet_3.write('A'+str(internal_cnt),value['date'])
                worksheet_3.write('B'+str(internal_cnt),value['employee_id'])
                worksheet_3.write('C'+str(internal_cnt),value['sub_project'])
                worksheet_3.write('D'+str(internal_cnt),value['work_packet'])
                worksheet_3.write('E'+str(internal_cnt),value['sub_packet'])
                worksheet_3.write('F'+str(internal_cnt),value['audited_errors'])
                worksheet_3.write('G'+str(internal_cnt),value['total_errors'])
                worksheet_3.write('H'+str(internal_cnt),value['error_types'])
                worksheet_3.write('I'+str(internal_cnt),value['error_values'])

                internal_cnt += 1

        workbook.close()
        with open('audit_data.xlsx', 'rb')as xl:
            xl_data = xl.read();

        response = HttpResponse(xl_data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=%s' % ('audit_data.xlsx')
        return response
    else:
        return HttpResponse('Please use the post method to send the data.')


def generate_agent_internal_external_error_details(project,start_date,end_date,err_agent_details):

    result, internal_dict, external_dict = {}, {}, {}
    intrnl_cnt, extrnl_cnt = 0, 0

    project_id  = Project.objects.get(name=project).id
    agent_names = err_agent_details
    
    for agent in agent_names:
        internal_data = Internalerrors.objects.filter(project=project_id,date__range=[end_date,start_date],employee_id=agent).\
                        filter(error_values__gt=0)
        external_data = Externalerrors.objects.filter(project=project_id,date__range=[end_date,start_date],employee_id=agent).\
                        filter(error_values__gt=0)

        if external_data:
            external_values = external_data.values_list('date','sub_project','work_packet','sub_packet','total_errors','audited_errors','error_types','error_values')
            for value in external_values:
                if '#<>#' not in value[6]:
                    external_dict.update({extrnl_cnt: {'employee_id':agent,'date':str(value[0]),'sub_project':value[1],'work_packet':value[2],'sub_packet':value[3],\
                        'total_errors':value[4],'audited_errors':value[5],'error_types':value[6],'error_values':value[7]}})
                    extrnl_cnt += 1
                else:
                    error_names = value[6].split('#<>#')
                    error_count = value[7].split('#<>#')
                    error_cnt = 0
                    for name, count in zip(error_names, error_count):
                        if name != 'no_data' and error_cnt >= 1:
                            external_dict.update({extrnl_cnt: {'employee_id':agent,'date':str(value[0]),'sub_project':value[1],'work_packet':value[2],'sub_packet':value[3],\
                                'total_errors':'','audited_errors':value[5],'error_types':name,'error_values':count}})
                        elif name != 'no_data':
                            external_dict.update({extrnl_cnt: {'employee_id':agent,'date':str(value[0]),'sub_project':value[1],'work_packet':value[2],'sub_packet':value[3],\
                                'total_errors':value[4],'audited_errors':value[5],'error_types':name,'error_values':count}})        
                        extrnl_cnt += 1
                        error_cnt += 1
        if internal_data:
            internal_values = internal_data.values_list('date','sub_project','work_packet','sub_packet','total_errors','audited_errors','error_types','error_values')
            for value in internal_values:
                if '#<>#' not in value[6]:
                    internal_dict.update({intrnl_cnt: {'employee_id':agent,'date':str(value[0]),'sub_project':value[1],'work_packet':value[2],'sub_packet':value[3],\
                        'total_errors':value[4],'audited_errors':value[5],'error_types':value[6],'error_values':value[7]}})
                    intrnl_cnt += 1                 
                else:
                    error_names = value[6].split('#<>#')
                    error_count = value[7].split('#<>#')
                    error_cnt = 0
                    for name, count in zip(error_names, error_count):
                        if name != 'no_data' and error_cnt >= 1:
                            internal_dict.update({intrnl_cnt: {'employee_id':agent,'date':str(value[0]),'sub_project':value[1],'work_packet':value[2],'sub_packet':value[3],\
                            'total_errors':'','audited_errors':value[5],'error_types':name,'error_values':count}})
                        elif name != 'no_data':
                            internal_dict.update({intrnl_cnt: {'employee_id':agent,'date':str(value[0]),'sub_project':value[1],'work_packet':value[2],'sub_packet':value[3],\
                            'total_errors':value[4],'audited_errors':value[5],'error_types':name,'error_values':count}})
                        intrnl_cnt += 1
                        error_cnt += 1

    result['internal'] = internal_dict
    result['external'] = external_dict
    return result




