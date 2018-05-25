from api.models import *
from django.http import JsonResponse
import datetime
import datetime as dt
from django.db.models import Sum
from operator import itemgetter
from dateutil.relativedelta import relativedelta
from collections import OrderedDict
def generate_dates(project, center, required_dates):

	days_lists = [list(), list(), list()]

	# Getting latest sheet uploded date for requsted project and center
	latest_date = RawTable.objects.filter(project=project, center=center).latest('date').date

	# Calculating the dates from the latest sheet uploded date  to last 30 days, 60 days, 90 days.
	for index, date in enumerate(required_dates):
		for day in range(0, date):
			days_lists[index].append((latest_date - dt.timedelta(day)).strftime('%Y-%m-%d'))
	return days_lists

def dates_data(project, center):
	days_list = generate_dates(project, center, [30, 60, 90])
	thirty_days_list =days_list[0]
	sixty_days_list =days_list[1]
	ninty_days_list = days_list[2]
	dates_list = [thirty_days_list, sixty_days_list, ninty_days_list]
	return dates_list


def	get_days_data(project, center, thirty_days, sixty_days, ninty_days):
	final_dict = {}
	thirty_days = thirty_days
	sixty_days = sixty_days
	ninty_days = ninty_days
	tables= [Internalerrors, Externalerrors]

	pro_id = project
	center_id = center

	# For thirty_days_internal_external_data
	total_employees_list = ['', '']
	for index, table in enumerate(tables):
		total_employees_list[index] = table.objects.filter(project=pro_id, center=center_id, date__range = (thirty_days[-1], thirty_days[0])).filter(total_errors__gt=0).values_list('employee_id', flat=True).distinct()
	
	thirty_days_error_data = [list(), list()]
	for index, employees_list in enumerate(total_employees_list):
		for employee in employees_list:
			thirty_days_error_data[index].append({'error':tables[index].objects.filter(project=pro_id, center=center_id, date__range = (thirty_days[-1], thirty_days[0]), employee_id=employee).aggregate(Sum('total_errors'))['total_errors__sum'], 'employee':employee})
	

	for i in range(0, len(thirty_days_error_data)):
		thirty_days_error_data[i] = sorted(thirty_days_error_data[i], key=itemgetter('error'))
		thirty_days_error_data[i] = thirty_days_error_data[i][-6:-1]

	# For sixty_days_internal_external_data
	total_employees_list = ['', '']
	for index, table in enumerate(tables):
		total_employees_list[index] = table.objects.filter(project=pro_id, center=center_id, date__range = (sixty_days[-1], sixty_days[0])).filter(total_errors__gt=0).values_list('employee_id', flat=True).distinct()
	
	sixty_days_error_data = [list(), list()]
	for index, employees_list in enumerate(total_employees_list):
		for employee in employees_list:
			sixty_days_error_data[index].append({'error':tables[index].objects.filter(project=pro_id, center=center_id, date__range = (sixty_days[-1], sixty_days[0]), employee_id=employee).aggregate(Sum('total_errors'))['total_errors__sum'], 'employee':employee})
	
	for i in range(0, len(sixty_days_error_data)):
		sixty_days_error_data[i] = sorted(sixty_days_error_data[i], key=itemgetter('error'))
		sixty_days_error_data[i] = sixty_days_error_data[i][-6:-1]
	
	# For Ninty_days_internal_external_data
	total_employees_list = ['', '']
	for index, table in enumerate(tables):
		total_employees_list[index]= table.objects.filter(project=pro_id, center=center_id, date__range = (ninty_days[-1], ninty_days[0])).filter(total_errors__gt=0).values_list('employee_id', flat=True).distinct()
	
	ninty_days_error_data = [list(), list()]
	for index, employees_list in enumerate(total_employees_list):
		for employee in employees_list:
			ninty_days_error_data[index].append({'error':tables[index].objects.filter(project=pro_id, center=center_id, date__range = (ninty_days[-1], ninty_days[0]), employee_id=employee).aggregate(Sum('total_errors'))['total_errors__sum'], 'employee':employee})
	
	for i in range(0, len(ninty_days_error_data)):
		ninty_days_error_data[i] = sorted(ninty_days_error_data[i], key=itemgetter('error'))
		ninty_days_error_data[i] = ninty_days_error_data[i][-6:-1]

	
	final_dict['result'] = {}
	final_dict['result']['dates'] = {30:"Thirty Days", 60:"Sixty Days", 90:"Ninty Days"}
	final_dict['result']['thirty_days_data'] = {}
	final_dict['result']['thirty_days_data']['internalerrors'] = {}
	final_dict['result']['thirty_days_data']['externalerrors'] = {}
	

	for error_list in thirty_days_error_data[0]:
		final_dict['result']['thirty_days_data']['internalerrors'][error_list['employee']] = error_list['error']

	for error_list in thirty_days_error_data[1]:
		final_dict['result']['thirty_days_data']['externalerrors'][error_list['employee']] = error_list['error']
	

	final_dict['result']['sixty_days_data'] = {}
	final_dict['result']['sixty_days_data']['internalerrors'] = {}
	final_dict['result']['sixty_days_data']['externalerrors'] = {}

	for error_list in sixty_days_error_data[0]:
		final_dict['result']['sixty_days_data']['internalerrors'][error_list['employee']] = error_list['error']

	for error_list in sixty_days_error_data[1]:
		final_dict['result']['sixty_days_data']['externalerrors'][error_list['employee']] = error_list['error']

	
	final_dict['result']['ninty_days_data'] = {}
	final_dict['result']['ninty_days_data']['internalerrors'] = {}
	final_dict['result']['ninty_days_data']['externalerrors'] = {}

	for error_list in ninty_days_error_data[0]:
		final_dict['result']['ninty_days_data']['internalerrors'][error_list['employee']] = error_list['error']

	for error_list in ninty_days_error_data[1]:
		final_dict['result']['ninty_days_data']['externalerrors'][error_list['employee']] = error_list['error']
	
	return final_dict


def get_intern_extern_error_category_data(project, center, thirty_days, sixty_days, ninty_days):
	final_dict = {}
	project = project
	center = center
	tables = [Internalerrors, Externalerrors]
	
	# thirty days error_category data
	thirty_days_error_category_data = {}
	thirty_days_error_types_list = [list(), list()]
	for index, table in enumerate(tables):
		thirty_days_error_types_list[index] = table.objects.filter(project=project, center=center, date__range = (thirty_days[-1], thirty_days[0])).filter(error_values__gt=0).exclude(error_types='no_data').values('error_types', 'error_values')

	for index, error_type_category in enumerate(thirty_days_error_types_list):
		thirty_days_data = {}
		for error_data in error_type_category:
			error_types = error_data['error_types'].split('#<>#')
			error_values = error_data['error_values'].split('#<>#')
			for error, value in zip(error_types, error_values):
				if error in thirty_days_data:
					thirty_days_data[error]+=int(value)

				else:
					thirty_days_data[error] = int(value)
		thirty_days_error_category_data[str(index)] = thirty_days_data
		

	# sixty days error_category data
	sixty_days_error_category_data = {}
	sixty_days_error_types_list = [list(), list()]
	for index, table in enumerate(tables):
		sixty_days_error_types_list[index] = table.objects.filter(project=project, center=center, date__range = (sixty_days[-1], sixty_days[0])).filter(error_values__gt=0).exclude(error_types='no_data').values('error_types', 'error_values')

	for index, error_type_category in enumerate(sixty_days_error_types_list):
		sixty_days_data = {}
		for error_data in error_type_category:
			error_types = error_data['error_types'].split('#<>#')
			error_values = error_data['error_values'].split('#<>#')
			for error, value in zip(error_types, error_values):
				if error in sixty_days_data:
					sixty_days_data[error]+=int(value)

				else:
					sixty_days_data[error] = int(value)
		sixty_days_error_category_data[str(index)] = sixty_days_data


	# ninty days error_category data
	ninty_days_error_category_data = {}
	ninty_days_error_types_list = [list(), list()]
	for index, table in enumerate(tables):
		ninty_days_error_types_list[index] = table.objects.filter(project=project, center=center, date__range = (ninty_days[-1], ninty_days[0])).filter(error_values__gt=0).exclude(error_types='no_data').values('error_types', 'error_values')

	for index, error_type_category in enumerate(ninty_days_error_types_list):
		ninty_days_data = {}
		for error_data in error_type_category:
			error_types = error_data['error_types'].split('#<>#')
			error_values = error_data['error_values'].split('#<>#')
			for error, value in zip(error_types, error_values):
				if error in ninty_days_data:
					ninty_days_data[error]+=int(value)

				else:
					ninty_days_data[error] = int(value)
		ninty_days_error_category_data[str(index)] = ninty_days_data

	final_dict['result'] = {}
	final_dict['result']['dates'] = { '30':"Thirty Days", '60':"Sixty Days", '90':"Ninty Days" }
	final_dict['result']['thirty_days'] = {}
	final_dict['result']['thirty_days']['internalerrors'] = {}
	final_dict['result']['thirty_days']['externalerrors'] = {}
	
	thirty_days_data_internal = thirty_days_error_category_data['0']
	thirty_days_data_external = thirty_days_error_category_data['1']

	thirty_days_data_intrenal_sorted = sorted(thirty_days_data_internal.iteritems(), key = lambda (k,v): (v,k))
	thirty_days_data_extrenal_sorted = sorted(thirty_days_data_external.iteritems(), key = lambda (k,v): (v,k))

	top_5_internals = thirty_days_data_intrenal_sorted[-6:-1]
	top_5_externals = thirty_days_data_extrenal_sorted[-6:-1]

	for item in top_5_internals:
		final_dict['result']['thirty_days']['internalerrors'][item[0]] = item[1]

	for item in top_5_externals:
		final_dict['result']['thirty_days']['externalerrors'][item[0]] = item[1]

	final_dict['result']['sixty_days'] = {}
	final_dict['result']['sixty_days']['internalerrors'] = {}
	final_dict['result']['sixty_days']['externalerrors'] = {}
	sixty_days_data_internal = sixty_days_error_category_data['0']
	sixty_days_data_external = sixty_days_error_category_data['1']

	sixty_days_data_intrenal_sorted = sorted(sixty_days_data_internal.iteritems(), key = lambda (k,v): (v,k))
	sixty_days_data_extrenal_sorted = sorted(sixty_days_data_external.iteritems(), key = lambda (k,v): (v,k))

	top_5_internals = sixty_days_data_intrenal_sorted[-6:-1]
	top_5_externals = sixty_days_data_extrenal_sorted[-6:-1]

	for item in top_5_internals:
		final_dict['result']['sixty_days']['internalerrors'][item[0]] = item[1]

	for item in top_5_externals:
		final_dict['result']['sixty_days']['externalerrors'][item[0]] = item[1]


	final_dict['result']['ninty_days'] = {}
	final_dict['result']['ninty_days']['internalerrors'] = {}
	final_dict['result']['ninty_days']['externalerrors'] = {}
	ninty_days_data_internal = ninty_days_error_category_data['0']
	ninty_days_data_external = ninty_days_error_category_data['1']

	ninty_days_data_intrenal_sorted = sorted(ninty_days_data_internal.iteritems(), key = lambda (k,v): (v,k))
	ninty_days_data_extrenal_sorted = sorted(ninty_days_data_external.iteritems(), key = lambda (k,v): (v,k))

	top_5_internals = ninty_days_data_intrenal_sorted[-6:-1]
	top_5_externals = ninty_days_data_extrenal_sorted[-6:-1]

	for item in top_5_internals:
		final_dict['result']['ninty_days']['internalerrors'][item[0]] = item[1]

	for item in top_5_externals:
		final_dict['result']['ninty_days']['externalerrors'][item[0]] = item[1]
	return final_dict


# ===============

month_list = [[]]
month_list1 = [[]]
month_list2=[[]]
final_dates=[]



def generate_one_months(pro_id, center_id):
        latest_date = RawTable.objects.filter(project=pro_id, center=center_id).latest('date').date
        last_mon_date = latest_date - relativedelta(months=1)
        days = (latest_date - last_mon_date).days
        days = days + 1
        months_dict = {}
       
        month_names_list = []
        month_count=0
        for i in xrange(days):
            date = last_mon_date + datetime.timedelta(i)
            month = date.strftime("%B")
            if month not in month_names_list:
                month_names_list.append(month)
                month_list[month_count].append(str(date))
            if month in months_dict:
                
                months_dict[month].append(str(date))
                month_list[month_count].append(str(date))
            else:
                
                months_dict[month] = [str(date)]
       

def generate_two_months(pro_id, center_id):
       
        latest_date = RawTable.objects.filter(project=pro_id, center=center_id).latest('date').date

        last_mon_date = latest_date - relativedelta(months=2)
      
        days = (latest_date - last_mon_date).days
        days = days + 1
        months_dict = {}
        month_names_list = []
        month_count=0
        for i in xrange(days):
            date = last_mon_date + datetime.timedelta(i)
            month = date.strftime("%B")
            if month not in month_names_list:
                 month_names_list.append(month)
                 month_list1[month_count].append(str(date))
            if month in months_dict:
              
                months_dict[month].append(str(date))
                month_list1[month_count].append(str(date))
               
            else:
                
                months_dict[month] = [str(date)]
       

def generate_three_months(pro_id, center_id):
    
        latest_date = RawTable.objects.filter(project=pro_id, center=center_id).latest('date').date

        last_mon_date = latest_date - relativedelta(months=3)
        days = (latest_date - last_mon_date).days
        days = days + 1
        months_dict = {}
        month_names_list = []
        month_count=0
        for i in xrange(days):
            date = last_mon_date + datetime.timedelta(i)
            month = date.strftime("%B")
            if month not in month_names_list:
                month_names_list.append(month)
                month_list2[month_count].append(str(date))
            if month in months_dict:
              
                months_dict[month].append(str(date))
                month_list2[month_count].append(str(date))
            else:
                
                months_dict[month] = [str(date)]
      

def generate_dates(pro_id, center_id):
    generate_one_months(pro_id, center_id)
    generate_two_months(pro_id, center_id)
    generate_three_months(pro_id, center_id)
    final_dates=month_list+month_list1+month_list2
    return final_dates



    
def data(request,Table_name):
    
    project = request.GET.get('project', '')
    center = request.GET.get('center', '').split(' -')[0]
    
    # Getting project id from the projects table
    pro_id = Project.objects.get(name=project).id
    center_id = Center.objects.get(name=center).id

    days_list = generate_dates(pro_id, center_id)
    table_name=Table_name
    final_dict = OrderedDict({})
    thirty_days = days_list[0]
    sixty_days = days_list[1]
    ninty_days = days_list[2]
    error_query= table_name.objects.filter(project=pro_id,center=center_id)
   
    
    packets=error_query.filter(date__range=(thirty_days[0],thirty_days[-1])).values('sub_project','work_packet','sub_packet').distinct()
    total_errors = []
    for packet in packets:
            
            sub_project = packet.get('sub_project','')
            work_packet = packet.get('work_packet','')
            sub_packet = packet.get('sub_packet','')
                      
            if sub_project != '' and work_packet != '' and sub_packet != '':
                key=sub_project+'_'+work_packet+'_'+sub_packet
                total_errors.append({'errors':table_name.objects.filter(date__range=(thirty_days[0],thirty_days[-1]),project=pro_id,\
                    center=center_id,work_packet=work_packet,sub_project=sub_project,sub_packet=sub_packet).aggregate(Sum('total_errors'))['total_errors__sum'], 'packet':key})
               
            elif sub_project != '' and work_packet != '' and sub_packet == '':
                key=sub_project+'_'+work_packet  
                total_errors.append({'errors':table_name.objects.filter(date__range=(thirty_days[0],thirty_days[-1]),project=pro_id,\
                    center=center_id,work_packet=work_packet,sub_project=sub_project).aggregate(Sum('total_errors'))['total_errors__sum'],'packet':key})
                      
            elif sub_project == '' and work_packet != '' and sub_packet != '':
                key=work_packet+'_'+sub_packet  
                total_errors.append({'errors':table_name.objects.filter(date__range=(thirty_days[0],thirty_days[-1]),project=pro_id,\
                    center=center_id,work_packet=work_packet,sub_packet=sub_packet).aggregate(Sum('total_errors'))['total_errors__sum'],'packet':key})
                
            elif sub_project == '' and work_packet != '' and sub_packet == '':
                key=work_packet
                total_errors.append({'errors':table_name.objects.filter(date__range=(thirty_days[0],thirty_days[-1]),project=pro_id,\
                    center=center_id,work_packet=work_packet).aggregate(Sum('total_errors'))['total_errors__sum'],'packet':key})
                key=work_packet
    thirty_days_error = sorted(total_errors, key=itemgetter('errors'))
    thirty_days_error = thirty_days_error[-6:-1]
    thirty_days_error.sort(reverse=True)
    


    packets=error_query.filter(date__range=(sixty_days[0],sixty_days[-1])).values('sub_project','work_packet','sub_packet').distinct()
    total_errors = []
    for packet in packets:
            
            sub_project = packet.get('sub_project','')
            work_packet = packet.get('work_packet','')
            sub_packet = packet.get('sub_packet','')
                      
            if sub_project != '' and work_packet != '' and sub_packet != '':
                key=sub_project+'_'+work_packet+'_'+sub_packet
                total_errors.append({'errors':table_name.objects.filter(date__range=(sixty_days[0],sixty_days[-1]),project=pro_id,\
                    center=center_id,work_packet=work_packet,sub_project=sub_project,sub_packet=sub_packet).aggregate(Sum('total_errors'))['total_errors__sum'], 'packet':key})
               
            elif sub_project != '' and work_packet != '' and sub_packet == '':
                key=sub_project+'_'+work_packet  
                total_errors.append({'errors':table_name.objects.filter(date__range=(sixty_days[0],sixty_days[-1]),project=pro_id,\
                    center=center_id,work_packet=work_packet,sub_project=sub_project).aggregate(Sum('total_errors'))['total_errors__sum'],'packet':key})
                      
            elif sub_project == '' and work_packet != '' and sub_packet != '':
                key=work_packet+'_'+sub_packet  
                total_errors.append({'errors':table_name.objects.filter(date__range=(sixty_days[0],sixty_days[-1]),project=pro_id,\
                    center=center_id,work_packet=work_packet,sub_packet=sub_packet).aggregate(Sum('total_errors'))['total_errors__sum'],'packet':key})
                
            elif sub_project == '' and work_packet != '' and sub_packet == '':
                key=work_packet
                total_errors.append({'errors':table_name.objects.filter(date__range=(sixty_days[0],sixty_days[-1]),project=pro_id,\
                    center=center_id,work_packet=work_packet).aggregate(Sum('total_errors'))['total_errors__sum'],'packet':key})
                
    sixty_days_error = sorted(total_errors, key=itemgetter('errors'))
    sixty_days_error = sixty_days_error[-6:-1]
    sixty_days_error.sort(reverse=True)
    


    packets=error_query.filter(date__range=(ninty_days[0],ninty_days[-1])).values('sub_project','work_packet','sub_packet').distinct()
    total_errors = []
    for packet in packets:
            
            sub_project = packet.get('sub_project','')
            work_packet = packet.get('work_packet','')
            sub_packet = packet.get('sub_packet','')
                      
            if sub_project != '' and work_packet != '' and sub_packet != '':
                key=sub_project+'_'+work_packet+'_'+sub_packet
                total_errors.append({'errors':table_name.objects.filter(date__range=(ninty_days[0],ninty_days[-1]),project=pro_id,\
                    center=center_id,work_packet=work_packet,sub_project=sub_project,sub_packet=sub_packet).aggregate(Sum('total_errors'))['total_errors__sum'], 'packet':key})
               
            elif sub_project != '' and work_packet != '' and sub_packet == '':
                key=sub_project+'_'+work_packet  
                total_errors.append({'errors':table_name.objects.filter(date__range=(ninty_days[0],ninty_days[-1]),project=pro_id,\
                    center=center_id,work_packet=work_packet,sub_project=sub_project).aggregate(Sum('total_errors'))['total_errors__sum'],'packet':key})
                      
            elif sub_project == '' and work_packet != '' and sub_packet != '':
                key=work_packet+'_'+sub_packet  
                total_errors.append({'errors':table_name.objects.filter(date__range=(ninty_days[0],ninty_days[-1]),project=pro_id,\
                    center=center_id,work_packet=work_packet,sub_packet=sub_packet).aggregate(Sum('total_errors'))['total_errors__sum'],'packet':key})
                
            elif sub_project == '' and work_packet != '' and sub_packet == '':
                key=work_packet
                total_errors.append({'errors':table_name.objects.filter(date__range=(ninty_days[0],ninty_days[-1]),project=pro_id,\
                    center=center_id,work_packet=work_packet).aggregate(Sum('total_errors'))['total_errors__sum'],'packet':key})
                
    ninty_days_error = sorted(total_errors, key=itemgetter('errors'))

    
    ninty_days_error = ninty_days_error[-6:-1]
    ninty_days_error.sort(reverse=True)
    
    final_dict['result'] = OrderedDict({})
    final_dict['result']['dates'] = [30, 60, 90]
    final_dict['result']['thirty_days_packet_wise_error_count'] = OrderedDict({})
    for item in thirty_days_error:
        final_dict['result']['thirty_days_packet_wise_error_count'][item['packet']] = item['errors']
    
    final_dict['result']['sixty_days_packet_wise_error_count'] = OrderedDict({})
    for item in sixty_days_error:
        final_dict['result']['sixty_days_packet_wise_error_count'][item['packet']] = item['errors']

    
    final_dict['result']['ninty_days_packet_wise_error_count'] = OrderedDict({})
    for item in ninty_days_error:
        final_dict['result']['ninty_days_packet_wise_error_count'][item['packet']] = item['errors']
    
    return final_dict

def static_packet_wise_internal_data(request):
        table_name=Internalerrors
        result = data(request,table_name)
        return JsonResponse(result)

def static_packet_wise_external_data(request):
        table_name=Externalerrors
        result = data(request,table_name)
        return JsonResponse(result)

def employees_top_5_errors(request):

	project = request.GET.get('project', '')
	center = request.GET.get('center', '').split(' -')[0]

	pro_id = Project.objects.get(name=project).id
	center_id = Center.objects.get(name=center).id

	dates_list = dates_data(pro_id, center_id)

	result = get_days_data(pro_id, center_id, dates_list[0], dates_list[1], dates_list[2])

	return JsonResponse(result)

def static_intern_extern_error_category_data(request):
	project = request.GET.get('project', '')
	center = request.GET.get('center', '').split(' -')[0]

	pro_id = Project.objects.get(name=project).id
	center_id = Center.objects.get(name=center).id

	dates_list = dates_data(pro_id, center_id)
	result = get_intern_extern_error_category_data(pro_id, center_id, dates_list[0], dates_list[1], dates_list[2])
	return JsonResponse(result)