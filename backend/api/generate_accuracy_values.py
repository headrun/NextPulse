
import datetime

from django.db.models import Sum,Max

from api.models import RawTable, Internalerrors, Externalerrors, Targets


def generate_targets_data(project):
    
    result = {}
    date_query = RawTable.objects.filter(project_id=project.id).aggregate(Max('date'))
    last_date = str(date_query['date__max'])
    rawtable_query = RawTable.objects.filter(project=project.id, date=last_date).aggregate(Sum('per_day'))
    production_value = rawtable_query['per_day__sum']
    target_query = Targets.objects.filter(\
                    project=project.id, from_date__lte=last_date, \
                    to_date__gte=last_date, target_type='Production').aggregate(Sum('target_value'))
    prod_target_value = 0
    if not target_query['target_value__sum'] == None:
        prod_target_value = target_query['target_value__sum']
    color = 'black'
    if not prod_target_value < production_value:
        color = 'Red'
    target_type = 'Internal accuracy'
    table_name = Internalerrors
    internal_data = generate_internal_and_external_values(\
                    project.id, table_name, last_date, production_value, target_type)
    result.update({'internal_target': internal_data['target'], 'internal_actual': internal_data['accuracy'],\
    'internal_color': internal_data['color']})
    target_type = 'External accuracy'
    table_name = Externalerrors
    external_data = generate_internal_and_external_values(\
                    project.id, table_name, last_date, production_value, target_type)
    result.update({'external_target': external_data['target'], 'external_actual': external_data['accuracy'],\
    'external_color': external_data['color']})
    result.update({'prod_target': prod_target_value, 'prod_actual': production_value,\
    'prod_color': color})

    return result


def generate_internal_and_external_values(project,table_name,date,production,target_type):
    
    result = {}
    audited_errors = table_name.objects.filter(project=project, date=date).aggregate(Sum('audited_errors'))
    total_errors = table_name.objects.filter(project=project, date=date).aggregate(Sum('total_errors'))
    agent_count = table_name.objects.filter(project=project, date=date).values('employee_id').count()
    audited_count = audited_errors['audited_errors__sum'] 
    errors_count = total_errors['total_errors__sum']
    target_query = Targets.objects.filter(\
                    project=project, from_date__lte=date, to_date__gte=date, \
                    target_type=target_type).aggregate(Sum('target_value'))
    target_value = target_query['target_value__sum']
    if errors_count >= 0 and audited_count > 0:
        accuracy_value = 100 - (float(errors_count)/float(audited_count))*100
        accuracy_value = float('%.2f' % round(accuracy_value, 2))
    elif errors_count >= 0 and audited_count == None:
        accuracy_value = 100 - (float(errors_count)/float(production))*100
        accuracy_value = float('%.2f' % round(accuracy_value, 2))
    elif errors_count == None and audited_count == None and agent_count == 0:
        target_value = target_value
        accuracy_value = 0
    if (target_value > accuracy_value) and (agent_count > 0):
        target = target_value
        accuracy = accuracy_value
        color = 'Red'
    elif (target_value < accuracy_value) and (agent_count > 0):
        target = target_value
        accuracy = accuracy_value
        color = 'black'
    elif target_value == None and accuracy_value > 0:
        target = 'No data'
        accuracy = accuracy_value
        color = 'black'
    elif agent_count == 0 and target_value > 0:
        target = target_value
        accuracy = 'No data'
        color = 'black'
    elif agent_count == 0 and target_value == None:
        target = 'No data'
        accuracy = 'No data'
        color = 'black'

    result['target'] = target
    result['accuracy'] = accuracy
    result['color'] = color
    return result
