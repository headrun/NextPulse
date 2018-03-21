
import datetime
from api.models import *
from common.utils import getHttpResponse as json_HttpResponse

def accuracy_query_generations(pro_id,cen_id,date,main_work_packet):
    accuracy_query_set = {}
    accuracy_query_set['project'] = pro_id
    accuracy_query_set['center'] = cen_id
    if isinstance(date, list):
        accuracy_query_set['date__range']=[date[0], date[-1]]
    else:
        accuracy_query_set['date'] = date
    if '_' in main_work_packet:
        packets_list = main_work_packet.split('_')
        accuracy_query_set['work_packet'] = packets_list[0]
        accuracy_query_set['sub_packet'] = packets_list[1]
    else:
        accuracy_query_set['work_packet'] = main_work_packet

    return accuracy_query_set


def query_set_generation(prj_id,center_obj,level_structure_key,date_list):
    query_set = {}
    query_set['project'] = prj_id
    query_set['center'] = center_obj
    if date_list:
        query_set['date__range'] = [date_list[0], date_list[-1]]
    if level_structure_key.has_key('sub_project'):
        if level_structure_key['sub_project'] != "All":
            query_set['sub_project'] = level_structure_key['sub_project']
    if level_structure_key.has_key('work_packet'):
        if level_structure_key['work_packet'] != "All":
            query_set['work_packet'] = level_structure_key['work_packet']
    if level_structure_key.has_key('sub_packet'):
        if level_structure_key['sub_packet'] != "All":
            query_set['sub_packet'] = level_structure_key['sub_packet']
    return query_set

def target_query_set_generation(prj_id,center_obj,level_structure_key,date_list):
    query_set = {}
    query_set['project'] = prj_id
    query_set['center'] = center_obj
    if date_list:
        query_set['from_date__lte'] = date_list[0]
        query_set['to_date__gte'] = date_list[-1]
    if level_structure_key.has_key('sub_project'):
        if level_structure_key['sub_project'] != "All":
            query_set['sub_project'] = level_structure_key['sub_project']
    if level_structure_key.has_key('work_packet'):
        if level_structure_key['work_packet'] != "All":
            query_set['work_packet'] = level_structure_key['work_packet']
    if level_structure_key.has_key('sub_packet'):
        if level_structure_key['sub_packet'] != "All":
            query_set['sub_packet'] = level_structure_key['sub_packet']
    return query_set


def worktrack_query_insertion(customer_data, prj_obj, center_obj,teamleader_obj_name, db_check):
    worktrac_date_list = customer_data['date']
    check_query = Worktrack.objects.filter(project=prj_obj, sub_project=customer_data.get('sub_project', ''),
                                          work_packet=customer_data['work_packet'],
                                          sub_packet=customer_data.get('sub_packet', ''),
                                          date=customer_data['date'],
                                          center=center_obj).values('opening','received', 'non_workable_count','completed','closing_balance')

    try:
        opening = int(float(customer_data['opening']))
    except:
        opening = 0
    try:
        received = int(float(customer_data['received']))
    except:
        received = 0
    try:
        non_workable_count = int(float(customer_data['non_workable_count']))
    except:
        non_workable_count = 0
    try:
        completed = int(float(customer_data['completed']))
    except:
        completed = 0
    try:
        closing_balance = int(float(customer_data['closing_balance']))
    except:
        closing_balance = 0

    if len(check_query) == 0:
        new_can = Worktrack(sub_project=customer_data.get('sub_project', ''),
                            work_packet=customer_data['work_packet'],
                            sub_packet=customer_data.get('sub_packet', ''), date=customer_data['date'],
                            opening=opening,
                            received = received,
                            non_workable_count = non_workable_count,
                            completed = completed,
                            closing_balance = closing_balance,
                            project=prj_obj, center=center_obj)
        if new_can:
            try:
                new_can.save()
            except:
		        pass
    else:
        if db_check == 'aggregate':
            opening = opening + int(check_query[0]['opening'])
            received = received + int(check_query[0]['received'])
            non_workable_count = non_workable_count + int(check_query[0]['non_workable_count'])
            completed = completed + int(check_query[0]['completed'])
            closing_balance = closing_balance + int(check_query[0]['closing_balance'])
            new_can_agr = Worktrack.objects.filter(id=int(check_query[0]['id'])).update(opening=opening,
                            received = received,
                            non_workable_count = non_workable_count,
                            completed = completed,
                            closing_balance = closing_balance,)
        elif db_check == 'update':
            new_can_upd = Internalerrors.objects.filter(id=int(check_query[0]['id'])).update(opening=opening,
                            received = received,
                            non_workable_count = non_workable_count,
                            completed = completed,
                            closing_balance = closing_balance,)
    return worktrac_date_list

def headcount_query_insertion(customer_data, prj_obj, center_obj,teamleader_obj_name, db_check):
    head_date_list = customer_data['date']
    check_query = Headcount.objects.filter(project=prj_obj, sub_project=customer_data.get('sub_project', ''),
                                          work_packet=customer_data.get('work_packet',''),
                                          sub_packet=customer_data.get('sub_packet', ''),
                                          date=customer_data['date'],
                                          center=center_obj).values('billable_hc','billable_agents','buffer_agents','qc_or_qa','teamlead','trainees_and_trainers','managers','mis')

    try:
        billable_hc = float(customer_data['billable_hc'])
    except:
        billable_hc = 0
    try:
        billable_agents = float(customer_data['billable_agents'])
    except:
        billable_agents = 0
    try:
        buffer_agents = float(customer_data['buffer_agents'])
    except:
        buffer_agents = 0
    try:
        qc_or_qa = float(customer_data['qc_or_qa'])
    except:
        qc_or_qa = 0
    try:
        teamlead = float(customer_data['teamlead'])
    except:
        teamlead = 0
    try:
        trainees_and_trainers = float(customer_data['trainees_and_trainers'])
    except:
        trainees_and_trainers = 0
    try:
        managers = float(customer_data['managers'])
    except:
        managers = 0
    try:
        mis = float(customer_data['mis'])
    except:
        mis = 0


    if len(check_query) == 0:
        new_can = Headcount(sub_project=customer_data.get('sub_project', ''),
                            work_packet=customer_data.get('work_packet',''),
                            sub_packet=customer_data.get('sub_packet', ''), date=customer_data['date'],
                            billable_hc = billable_hc,billable_agents = billable_agents,
                            buffer_agents = buffer_agents, qc_or_qa = qc_or_qa,teamlead = teamlead,
                            trainees_and_trainers = trainees_and_trainers, managers = managers,mis = mis,
                            project=prj_obj, center=center_obj)
        if new_can:
            try:
                new_can.save()
            except:
		        pass
    else:    
        if db_check == 'aggregate':
            billable_hc = billable_hc + float(check_query[0]['billable_hc'])
            billable_agents = billable_agents + float(check_query[0]['billable_agents'])
            buffer_agents = buffer_agents + float(check_query[0]['buffer_agents'])
            qc_or_qa = qc_or_qa +float(check_query[0]['qc_or_qa'])
            teamlead = teamlead +float(check_query[0]['teamlead'])
            trainees_and_trainers = trainees_and_trainers+float(check_query[0]['trainees_and_trainers'])
            managers = managers+float(check_query[0]['managers'])
            mis = mis + float(check_query[0]['mis'])

            new_can_agr = Headcount.objects.filter(id=int(check_query[0]['id'])).update(billable_hc = billable_hc,
                            billable_agents = billable_agents,buffer_agents = buffer_agents, qc_or_qa = qc_or_qa,teamlead = teamlead,
                            trainees_and_trainers = trainees_and_trainers, managers = managers,mis = mis)

        elif db_check == 'update':
            new_can_agr = Headcount.objects.filter(id=int(check_query[0]['id'])).update(billable_hc = billable_hc,
                            billable_agents = billable_agents,buffer_agents = buffer_agents, qc_or_qa = qc_or_qa,teamlead = teamlead,
                            trainees_and_trainers = trainees_and_trainers, managers = managers,mis = mis)
    return head_date_list


def tat_query_insertion(customer_data, prj_obj, center_obj,teamleader_obj_name, db_check):
    tat_date_list = customer_data['date']
    check_query = TatTable.objects.filter(project=prj_obj, sub_project=customer_data.get('sub_project', ''),
                                          work_packet=customer_data['work_packet'],
                                          sub_packet=customer_data.get('sub_packet', ''),
                                          date=customer_data['date'],
                                          center=center_obj).values('total_received','met_count','non_met_count','tat_status')

    try:
        total_received = int(float(customer_data['total_received']))
    except:
        total_received = 0
    try:
        met_count = int(float(customer_data['met_count']))
    except:
        met_count = 0
    try:
        non_met_count = int(float(customer_data['non_met_count']))
    except:
        non_met_count = 0
    try:
        tat_status = customer_data['tat_status']
    except:
        tat_status = ''

    if len(check_query) == 0:
        new_can = TatTable(sub_project=customer_data.get('sub_project', ''),
                            work_packet=customer_data['work_packet'],
                            sub_packet=customer_data.get('sub_packet', ''), date=customer_data['date'],
                            total_received=total_received,
                            met_count = met_count,
                            non_met_count = non_met_count,
                            tat_status = tat_status,
                            project=prj_obj, center=center_obj)

        if new_can:
            new_can.save()

    else:
        if db_check == 'aggregate':
            total_received = total_received + int(check_query[0]['total_received'])
            met_count = met_count + int(check_query[0]['met_count'])
            non_met_count = non_met_count + int(check_query[0]['non_met_count'])
            new_can_agr = TatTable.objects.filter(id=int(check_query[0]['id'])).update(total_received=total_received,
                                                                                       met_count = met_count,
                                                                                       non_met_count = non_met_count,
                                                                                       tat_status = tat_status,)
        elif db_check == 'update':
            new_can_upd = TatTable.objects.filter(id=int(check_query[0]['id'])).update(total_received=total_received,
                                                                                       met_count = met_count,
                                                                                       non_met_count = non_met_count,)
    return tat_date_list

def upload_query_insertion(customer_data, prj_obj, center_obj,teamleader_obj_name, db_check):
    upload_date_list = customer_data['date']
    check_query = UploadDataTable.objects.filter(project=prj_obj, sub_project=customer_data.get('sub_project', ''),
                                  date=customer_data['date'],
                                  center=center_obj).values('target','upload')
    try:
        target = int(float(customer_data['target']))
    except:
        target = 0
    try:
        upload = int(float(customer_data['upload']))
    except:
        upload = 0
    if len(check_query) == 0:
        new_can = UploadDataTable(sub_project=customer_data.get('sub_project', ''),
                                  date = customer_data['date'],
                                  target = target,
                                  upload = upload,
                                  project=prj_obj, center=center_obj)
        if new_can:
            new_can.save()
    else:
        if db_check == 'aggregate':
            target = target + int(check_query[0]['target'])
            upload = upload + int(check_query[0]['upload'])
            new_can_agr = UploadDataTable.objects.filter(id=int(check_query[0]['id'])).update(target = target,
                                                                                              upload = upload,)
        elif db_check == 'update':
            new_can_upd = UploadDataTable.objects.filter(id=int(check_query[0]['id'])).update(target = target,
                                                                                       upload = upload,)
    return upload_date_list


def aht_individual_query_insertion(customer_data, prj_obj, center_obj, teamleader_obj_name, db_check):
    aht_date_list = customer_data['date']
    check_query = AHTIndividual.objects.filter(project=prj_obj, sub_project=customer_data.get('sub_project', ''),
                                               work_packet = customer_data.get('work_packet',''),
                                               sub_packet = customer_data.get('sub_packet',''),
                                               emp_name = customer_data.get('emp_name', ''),
                                               date = customer_data['date'],center=center_obj).values('AHT')
    try:
        aht = float(customer_data['AHT'])
    except:
        aht = 0
    if len(check_query) == 0:
        new_can = AHTIndividual(sub_project=customer_data.get('sub_project', ''), work_packet=customer_data.get('work_packet',''),
                                sub_packet=customer_data.get('sub_packet', ''), 
                                emp_name = customer_data.get('emp_name', ''), date=customer_data['date'],
                                AHT = aht, project= prj_obj, center = center_obj)
        if new_can:
            new_can.save()
    else:
        if db_check == 'aggregate':
            aht = aht + float(check_query[0]['AHT'])
            new_can_agr = AHTIndividual.objects.filter(id=float(check_query[0]['id'])).update(AHT = aht)
        if db_check == 'update':
            new_can_upd = AHTIndividual.objects.filter(id=float(check_query[0]['id'])).update(AHT = aht)
    return aht_date_list


def aht_team_query_insertion(customer_data, prj_obj, center_obj, teamleader_obj_name, db_check):
    aht_team_date = customer_data['date']
    check_query = AHTTeam.objects.filter(project = prj_obj, sub_project = customer_data.get('sub_project', ''),
                                         work_packet = customer_data.get('work_packet',''), 
                                         sub_packet = customer_data.get('sub_packet',''),
                                         date = customer_data['date'], center=center_obj).values('AHT')
    try:
        aht = float(customer_data['AHT'])
    except:
        aht = 0
    if len(check_query) == 0:
        new_can = AHTTeam(sub_project=customer_data.get('sub_project', ''), work_packet=customer_data.get('work_packet',''),
                          sub_packet=customer_data.get('sub_packet',''), date=customer_data['date'],
                          AHT=aht, project=prj_obj, center=center_obj)
        if new_can:
            new_can.save()
    else:
        if db_check == 'aggregate':
            aht = aht + float(check_query[0]['AHT'])
            new_can_agr = AHTTeam.objects.filter(id=float(check_query[0]['id'])).update(AHT = aht)
        elif db_check == 'update':
            new_can_upd = AHTTeam.objects.filter(id=float(check_query[0]['id'])).update(AHT = aht)
    return aht_team_date


def incoming_error_query_insertion(customer_data, prj_obj, center_obj,teamleader_obj_name, db_check):

    incoming_date_list = customer_data['date']
    check_query = Incomingerror.objects.filter(project=prj_obj, sub_project=customer_data.get('sub_project', ''),
                                               work_packet=customer_data['work_packet'],
                                               sub_packet=customer_data.get('sub_packet', ''),
                                               date=customer_data['date'],
                                               center=center_obj).values('error_values')
    try:
        error_values = int(float(customer_data['error_values']))
    except:
        error_values = 0

    if len(check_query) == 0:
        new_can = Incomingerror(sub_project=customer_data.get('sub_project', ''),
                                work_packet=customer_data['work_packet'],
                                sub_packet=customer_data.get('sub_packet', ''), date=customer_data['date'],
                                error_values=error_values,
                                project=prj_obj, center=center_obj)

        if new_can:
            new_can.save()
    else:
        if db_check == 'aggregate':
            error_values = error_values + int(check_query[0]['error_values'])
            new_can_agr = Incomingerror.objects.filter(id=int(check_query[0]['id'])).update(error_values = error_values)
        elif db_check == 'update':
            new_can_upd = Incomingerror.objects.filter(id=int(check_query[0]['id'])).update(error_values = error_values)
    return incoming_date_list


def raw_table_query_insertion(customer_data,prj_obj,center_obj,teamleader_obj_name,per_day_value,db_check):
    prod_date_list = customer_data['date']
    new_can = 0
    check_query = RawTable.objects.filter(project=prj_obj, sub_project=customer_data.get('sub_project', ''),
                                          work_packet=customer_data['work_packet'],
                                          sub_packet=customer_data.get('sub_packet', ''),
                                          employee_id=customer_data.get('employee_id', ''), date=customer_data['date'],
                                          center=center_obj).values('per_day','id')
    if len(check_query) == 0:
        new_can = RawTable(project=prj_obj, sub_project=customer_data.get('sub_project', ''),
                           work_packet=customer_data['work_packet'],
                           sub_packet=customer_data.get('sub_packet', ''),
                           employee_id=customer_data.get('employee_id', ''),
                           per_hour=0,
                           per_day=per_day_value, date=customer_data['date'],
                           norm=int(float(customer_data.get('target',0))),
                           team_lead=teamleader_obj_name, center=center_obj)
        if new_can:
            try:
                new_can.save()
            except:
		pass
    if len(check_query) > 0:
        if db_check == 'aggregate':
            per_day_value = per_day_value + int(check_query[0]['per_day'])
            new_can_agr = RawTable.objects.filter(id=int(check_query[0]['id'])).update(per_day=per_day_value)
        elif db_check == 'update':
            new_can_upd = RawTable.objects.filter(id=int(check_query[0]['id'])).update(per_day=per_day_value)

    return prod_date_list

def internalerror_query_insertion(customer_data, prj_obj, center_obj,teamleader_obj_name, db_check):
    internal_date_list = customer_data['date']
    check_query = Internalerrors.objects.filter(project=prj_obj, sub_project=customer_data.get('sub_project', ''),
                                          work_packet=customer_data['work_packet'],
                                          sub_packet=customer_data.get('sub_packet', ''),
                                          employee_id=customer_data.get('employee_id', ''),date=customer_data['date'],
                                          center=center_obj).values('audited_errors','total_errors', 'id')
    try:
        total_errors = int(float(customer_data['total_errors']))
    except:
        total_errors = 0
    try:
        if customer_data.get('audited_errors', ''):
            audited_count = int(float(customer_data.get('audited_errors', '')))
        else:
            audited_count = 0
    except:
        audited_count = 0

    if len(check_query) == 0:
        new_can = Internalerrors(employee_id=customer_data.get('employee_id', ''),
                                 sub_project=customer_data.get('sub_project', ''),
                                 work_packet=customer_data['work_packet'],
                                 sub_packet=customer_data.get('sub_packet', ''), date=customer_data['date'],
                                 audited_errors=int(float(audited_count)),
                                 total_errors=total_errors,
                                 error_types = customer_data.get('error_types', ''),
                                 error_values = customer_data.get('error_values', ''),
                                 sub_error_count = customer_data.get('sub_error_count',''),
                                 type_error = customer_data.get('type_error', ''),
                                 project=prj_obj, center=center_obj)
        if new_can:
            try:
                new_can.save()
            except:
		pass
    if len(check_query) > 0:
        if db_check == 'aggregate':
            audited_count = audited_count + int(check_query[0]['audited_errors'])
            total_errors = total_errors + int(check_query[0]['total_errors'])
            new_can_agr = Internalerrors.objects.filter(id=int(check_query[0]['id'])).update(audited_errors=audited_count,total_errors=total_errors)
        elif db_check == 'update':
            new_can_upd = Internalerrors.objects.filter(id=int(check_query[0]['id'])).update(audited_errors=audited_count,total_errors=total_errors)
    return internal_date_list

def externalerror_query_insertion(customer_data, prj_obj, center_obj,teamleader_obj_name, db_check):
    external_date_list = customer_data['date']
    new_can = 0
    check_query = Externalerrors.objects.filter(project=prj_obj, sub_project=customer_data.get('sub_project', ''),
                                          work_packet=customer_data['work_packet'],
                                          sub_packet=customer_data.get('sub_packet', ''),
                                          employee_id=customer_data.get('employee_id', ''),date=customer_data['date'],
                                          center=center_obj).values('audited_errors','total_errors', 'id')
    try:
        total_errors = int(float(customer_data['total_errors']))
    except:
        total_errors = 0
    try:
        if customer_data.get('audited_errors', ''):
            audited_count = int(float(customer_data.get('audited_errors', '')))
        else:
            audited_count = 0
    except:
        audited_count = 0
    if len(check_query) == 0:
        new_can = Externalerrors(employee_id=customer_data.get('employee_id', ''),
                                 sub_project=customer_data.get('sub_project', ''),
                                 work_packet=customer_data['work_packet'],
                                 sub_packet=customer_data.get('sub_packet', ''), date=customer_data['date'],
                                 audited_errors=int(float(audited_count)),
                                 total_errors=total_errors,
                                 error_types=customer_data.get('error_types', ''),
                                 error_values=customer_data.get('error_values', ''),
                                 type_error = customer_data.get('type_error', ''),
                                 sub_error_count = customer_data.get('sub_error_count',''),
                                 project=prj_obj, center=center_obj)
        if new_can:
            try:
                new_can.save()
            except:
		pass
    if len(check_query) > 0:
        if db_check == 'aggregate':
            audited_count = audited_count + int(check_query[0]['audited_errors'])
            total_errors = total_errors + int(check_query[0]['total_errors'])
            new_can_agr = Externalerrors.objects.filter(id=int(check_query[0]['id'])).update(audited_errors=audited_count,total_errors=total_errors)
        elif db_check == 'update':
            new_can_update = Externalerrors.objects.filter(id=int(check_query[0]['id'])).update(audited_errors=audited_count,total_errors=total_errors)

    return external_date_list

def target_table_query_insertion(customer_data,prj_obj,center_obj,teamleader_obj_name,db_check):
    prod_date_list = customer_data['from_date']
    new_can = 0
    check_query = Targets.objects.filter(project=prj_obj, sub_project=customer_data.get('sub_project', ''),
                                          work_packet=customer_data.get('work_packet', ''),
                                          sub_packet=customer_data.get('sub_packet', ''),
                                          from_date=customer_data['from_date'],
                                         to_date=customer_data['to_date'],
                                         target_type=customer_data['target_type'],
                                         target_method=customer_data.get('target_method', ''),
                                         center=center_obj).values('target','fte_target','target_value')

    try:
        target = int(float(customer_data['target']))
    except:
        target = 0
    try:
        target_value = int(float(customer_data['target_value']))
    except:
        target_value = 0
    try:
        fte_target = int(float(customer_data['fte_target']))
    except:
        fte_target = 0

    if len(check_query) == 0:
        new_can = Targets(project=prj_obj, sub_project=customer_data.get('sub_project', ''),
                           work_packet=customer_data.get('work_packet', ''),
                           sub_packet=customer_data.get('sub_packet', ''),
                           from_date=customer_data['from_date'],
                           to_date=customer_data['to_date'],
                           target_value = target_value,
                           target_type =customer_data['target_type'],
                           target_method=customer_data.get('target_method', ''), 
                           target=target,fte_target=fte_target,center=center_obj)
        if new_can:
            try:
                new_can.save()
            except:
		pass
    if len(check_query) > 0:
        if db_check == 'aggregate':
            target = target + int(check_query[0]['target'])
            fte_target = fte_target + int(check_query[0]['fte_target'])
            target_value = target_value + int(check_query[0]['target_value'])
            new_can_agr = Targets.objects.filter(id=int(check_query[0]['id'])).update(targer=target,fte_target=fte_target,target_value=target_value)
        elif db_check == 'update':
            new_can_upd = Targets.objects.filter(id=int(check_query[0]['id'])).update(targer=target,fte_target=fte_target,target_value=target_value)

    return prod_date_list
