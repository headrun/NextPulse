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


def	get_internal_external_agent_error_data(project, center, thirty_days, sixty_days, ninty_days):

	final_dict = {}
	dates_list = [thirty_days, sixty_days, ninty_days]
	tables= [Internalerrors, Externalerrors]
	agents_error_data = [{}, {}, {}, {}, {}, {}]

	pro_id = project
	center_id = center
	i = 0

	for date_list in dates_list:
		for table in tables:
			employees_list = table.objects.filter(project=pro_id, center=center_id, date__range=(date_list[-1], date_list[0])).filter(total_errors__gt=0).values_list('employee_id', flat=True).distinct()
			employees_error_data = {}
			for employee in employees_list:
				employees_error_data[employee] = table.objects.filter(project=pro_id, center=center_id, date__range=(date_list[-1], date_list[0]), employee_id=employee).aggregate(Sum('total_errors'))['total_errors__sum']
			agents_error_data[i] = employees_error_data
			i+=1

	final_dict['result'] = OrderedDict()

	months_names = [('thirty_days_data', 0, 1), ('sixty_days_data', 2, 3), ('ninty_days_data', 4, 5)]

	for month in months_names:
		final_dict['result'][month[0]] = OrderedDict()
		final_dict['result'][month[0]]['internalerrors'] = OrderedDict(sorted(agents_error_data[month[1]].items(), key=itemgetter(1), reverse=True)[:5])
		final_dict['result'][month[0]]['externalerrors'] = OrderedDict(sorted(agents_error_data[month[2]].items(), key=itemgetter(1), reverse=True)[:5])

	return final_dict


def get_internal_external_error_category_data(project, center, thirty_days, sixty_days, ninty_days):
	final_dict = {}
	project = project
	center = center
	errors_category_data = [{}, {}, {}, {}, {}, {}]
	dates_list = [thirty_days, sixty_days, ninty_days]
	tables = [Internalerrors, Externalerrors]

	i=0
	for date_list in dates_list:
		for table in tables:
			error_types =table.objects.filter(project=project, center=center, date__range = (date_list[-1], date_list[0])).filter(error_values__gt=0).exclude(error_types='no_data').values('error_types', 'error_values')
			for error_data in error_types:
				errors = error_data['error_types'].split('#<>#')
				values = error_data['error_values'].split('#<>#')
				for error,value in zip(errors, values):
					if error in errors_category_data[i]:
						errors_category_data[i][error]+=int(value)
					else:
						errors_category_data[i][error] = int(value)
			i+=1
	
	final_dict['result'] = OrderedDict()

	months_names = [('thirty_days_data', 0, 1), ('sixty_days_data', 2, 3), ('ninty_days_data', 4, 5)]

	for month in months_names:
		final_dict['result'][month[0]] = OrderedDict()
		final_dict['result'][month[0]]['internalerrors'] = OrderedDict(sorted(errors_category_data[month[1]].items(), key=itemgetter(1), reverse=True)[:5])
		final_dict['result'][month[0]]['externalerrors'] = OrderedDict(sorted(errors_category_data[month[2]].items(), key=itemgetter(1), reverse=True)[:5])

	return final_dict


# month_list = [[]]
# month_list1 = [[]]
# month_list2=[[]]
# final_dates=[]



# def generate_one_months(pro_id, center_id):
#         latest_date = RawTable.objects.filter(project=pro_id, center=center_id).latest('date').date
#         last_mon_date = latest_date - relativedelta(months=1)
#         days = (latest_date - last_mon_date).days
#         days = days + 1
#         months_dict = {}
       
#         month_names_list = []
#         month_count=0
#         for i in xrange(days):
#             date = last_mon_date + datetime.timedelta(i)
#             month = date.strftime("%B")
#             if month not in month_names_list:
#                 month_names_list.append(month)
#                 month_list[month_count].append(str(date))
#             if month in months_dict:
                
#                 months_dict[month].append(str(date))
#                 month_list[month_count].append(str(date))
#             else:
                
#                 months_dict[month] = [str(date)]
       

# def generate_two_months(pro_id, center_id):
       
#         latest_date = RawTable.objects.filter(project=pro_id, center=center_id).latest('date').date

#         last_mon_date = latest_date - relativedelta(months=2)
      
#         days = (latest_date - last_mon_date).days
#         days = days + 1
#         months_dict = {}
#         month_names_list = []
#         month_count=0
#         for i in xrange(days):
#             date = last_mon_date + datetime.timedelta(i)
#             month = date.strftime("%B")
#             if month not in month_names_list:
#                  month_names_list.append(month)
#                  month_list1[month_count].append(str(date))
#             if month in months_dict:
              
#                 months_dict[month].append(str(date))
#                 month_list1[month_count].append(str(date))
               
#             else:
                
#                 months_dict[month] = [str(date)]
       

# def generate_three_months(pro_id, center_id):
    
#         latest_date = RawTable.objects.filter(project=pro_id, center=center_id).latest('date').date

#         last_mon_date = latest_date - relativedelta(months=3)
#         days = (latest_date - last_mon_date).days
#         days = days + 1
#         months_dict = {}
#         month_names_list = []
#         month_count=0
#         for i in xrange(days):
#             date = last_mon_date + datetime.timedelta(i)
#             month = date.strftime("%B")
#             if month not in month_names_list:
#                 month_names_list.append(month)
#                 month_list2[month_count].append(str(date))
#             if month in months_dict:
              
#                 months_dict[month].append(str(date))
#                 month_list2[month_count].append(str(date))
#             else:
                
#                 months_dict[month] = [str(date)]
      

# def generates_dates(pro_id, center_id):
#     generate_one_months(pro_id, center_id)
#     generate_two_months(pro_id, center_id)
#     generate_three_months(pro_id, center_id)
#     final_dates=month_list+month_list1+month_list2
#     return final_dates



    
# def get_packet_wise_error_data(request,Table_name):
    
#     project = request.GET.get('project', '')
#     center = request.GET.get('center', '').split(' -')[0]
    
#     # Getting project id from the projects table
#     pro_id = Project.objects.get(name=project).id
#     center_id = Center.objects.get(name=center).id

#     days_list = generates_dates(pro_id, center_id)
#     table_name=Table_name
#     final_dict = OrderedDict({})
#     thirty_days = days_list[0]
#     sixty_days = days_list[1]
#     ninty_days = days_list[2]
#     import pdb; pdb.set_trace()
#     error_query= table_name.objects.filter(project=pro_id,center=center_id)
   
    
#     packets=error_query.filter(date__range=(thirty_days[0],thirty_days[-1])).values('sub_project','work_packet','sub_packet').distinct()
#     total_errors = []
#     for packet in packets:
            
#             sub_project = packet.get('sub_project','')
#             work_packet = packet.get('work_packet','')
#             sub_packet = packet.get('sub_packet','')
                      
#             if sub_project != '' and work_packet != '' and sub_packet != '':
#                 key=sub_project+'_'+work_packet+'_'+sub_packet
#                 total_errors.append({'errors':table_name.objects.filter(date__range=(thirty_days[0],thirty_days[-1]),project=pro_id,\
#                     center=center_id,work_packet=work_packet,sub_project=sub_project,sub_packet=sub_packet).aggregate(Sum('total_errors'))['total_errors__sum'], 'packet':key})
               
#             elif sub_project != '' and work_packet != '' and sub_packet == '':
#                 key=sub_project+'_'+work_packet  
#                 total_errors.append({'errors':table_name.objects.filter(date__range=(thirty_days[0],thirty_days[-1]),project=pro_id,\
#                     center=center_id,work_packet=work_packet,sub_project=sub_project).aggregate(Sum('total_errors'))['total_errors__sum'],'packet':key})
                      
#             elif sub_project == '' and work_packet != '' and sub_packet != '':
#                 key=work_packet+'_'+sub_packet  
#                 total_errors.append({'errors':table_name.objects.filter(date__range=(thirty_days[0],thirty_days[-1]),project=pro_id,\
#                     center=center_id,work_packet=work_packet,sub_packet=sub_packet).aggregate(Sum('total_errors'))['total_errors__sum'],'packet':key})
                
#             elif sub_project == '' and work_packet != '' and sub_packet == '':
#                 key=work_packet
#                 total_errors.append({'errors':table_name.objects.filter(date__range=(thirty_days[0],thirty_days[-1]),project=pro_id,\
#                     center=center_id,work_packet=work_packet).aggregate(Sum('total_errors'))['total_errors__sum'],'packet':key})
#                 key=work_packet
#     import pdb; pdb.set_trace()
#     thirty_days_error = sorted(total_errors, key=itemgetter('errors'))
#     thirty_days_error = thirty_days_error[-6:-1]
#     thirty_days_error.sort(reverse=True)
    


#     packets=error_query.filter(date__range=(sixty_days[0],sixty_days[-1])).values('sub_project','work_packet','sub_packet').distinct()
#     total_errors = []
#     for packet in packets:
            
#             sub_project = packet.get('sub_project','')
#             work_packet = packet.get('work_packet','')
#             sub_packet = packet.get('sub_packet','')
                      
#             if sub_project != '' and work_packet != '' and sub_packet != '':
#                 key=sub_project+'_'+work_packet+'_'+sub_packet
#                 total_errors.append({'errors':table_name.objects.filter(date__range=(sixty_days[0],sixty_days[-1]),project=pro_id,\
#                     center=center_id,work_packet=work_packet,sub_project=sub_project,sub_packet=sub_packet).aggregate(Sum('total_errors'))['total_errors__sum'], 'packet':key})
               
#             elif sub_project != '' and work_packet != '' and sub_packet == '':
#                 key=sub_project+'_'+work_packet  
#                 total_errors.append({'errors':table_name.objects.filter(date__range=(sixty_days[0],sixty_days[-1]),project=pro_id,\
#                     center=center_id,work_packet=work_packet,sub_project=sub_project).aggregate(Sum('total_errors'))['total_errors__sum'],'packet':key})
                      
#             elif sub_project == '' and work_packet != '' and sub_packet != '':
#                 key=work_packet+'_'+sub_packet  
#                 total_errors.append({'errors':table_name.objects.filter(date__range=(sixty_days[0],sixty_days[-1]),project=pro_id,\
#                     center=center_id,work_packet=work_packet,sub_packet=sub_packet).aggregate(Sum('total_errors'))['total_errors__sum'],'packet':key})
                
#             elif sub_project == '' and work_packet != '' and sub_packet == '':
#                 key=work_packet
#                 total_errors.append({'errors':table_name.objects.filter(date__range=(sixty_days[0],sixty_days[-1]),project=pro_id,\
#                     center=center_id,work_packet=work_packet).aggregate(Sum('total_errors'))['total_errors__sum'],'packet':key})
                
#     sixty_days_error = sorted(total_errors, key=itemgetter('errors'))
#     sixty_days_error = sixty_days_error[-6:-1]
#     sixty_days_error.sort(reverse=True)
    


#     packets=error_query.filter(date__range=(ninty_days[0],ninty_days[-1])).values('sub_project','work_packet','sub_packet').distinct()

#     # import pdb; pdb.set_trace();
#     total_errors = []
#     for packet in packets:
            
#             sub_project = packet.get('sub_project','')
#             work_packet = packet.get('work_packet','')
#             sub_packet = packet.get('sub_packet','')
                      
#             if sub_project != '' and work_packet != '' and sub_packet != '':
#                 key=sub_project+'_'+work_packet+'_'+sub_packet
#                 total_errors.append({'errors':table_name.objects.filter(date__range=(ninty_days[0],ninty_days[-1]),project=pro_id,\
#                     center=center_id,work_packet=work_packet,sub_project=sub_project,sub_packet=sub_packet).aggregate(Sum('total_errors'))['total_errors__sum'], 'packet':key})
               
#             elif sub_project != '' and work_packet != '' and sub_packet == '':
#                 key=sub_project+'_'+work_packet  
#                 total_errors.append({'errors':table_name.objects.filter(date__range=(ninty_days[0],ninty_days[-1]),project=pro_id,\
#                     center=center_id,work_packet=work_packet,sub_project=sub_project).aggregate(Sum('total_errors'))['total_errors__sum'],'packet':key})
                      
#             elif sub_project == '' and work_packet != '' and sub_packet != '':
#                 key=work_packet+'_'+sub_packet  
#                 total_errors.append({'errors':table_name.objects.filter(date__range=(ninty_days[0],ninty_days[-1]),project=pro_id,\
#                     center=center_id,work_packet=work_packet,sub_packet=sub_packet).aggregate(Sum('total_errors'))['total_errors__sum'],'packet':key})
                
#             elif sub_project == '' and work_packet != '' and sub_packet == '':
#                 key=work_packet
#                 total_errors.append({'errors':table_name.objects.filter(date__range=(ninty_days[0],ninty_days[-1]),project=pro_id,\
#                     center=center_id,work_packet=work_packet).aggregate(Sum('total_errors'))['total_errors__sum'],'packet':key})
                
#     ninty_days_error = sorted(total_errors, key=itemgetter('errors'))

    
#     ninty_days_error = ninty_days_error[-6:-1]
#     ninty_days_error.sort(reverse=True)
    
#     final_dict['result'] = OrderedDict({})
#     final_dict['result']['dates'] = [30, 60, 90]
#     final_dict['result']['thirty_days_packet_wise_error_count'] = OrderedDict({})
   
#     for item in thirty_days_error:
#         final_dict['result']['thirty_days_packet_wise_error_count'][item['packet']] = item['errors']
    
#     final_dict['result']['sixty_days_packet_wise_error_count'] = OrderedDict({})
#     for item in sixty_days_error:
#         final_dict['result']['sixty_days_packet_wise_error_count'][item['packet']] = item['errors']

    
#     final_dict['result']['ninty_days_packet_wise_error_count'] = OrderedDict({})
#     for item in ninty_days_error:
#         final_dict['result']['ninty_days_packet_wise_error_count'][item['packet']] = item['errors']
    
#     return final_dict

# def static_packet_wise_internal_data(request):
#         table_name=Internalerrors
#         result = get_packet_wise_error_data(request,table_name)
#         return JsonResponse(result)

# def static_packet_wise_external_data(request):
#         table_name=Externalerrors
#         result = get_packet_wise_error_data(request,table_name)
#         return JsonResponse(result)

def get_internal_external_packet_errors(project, center, thirty_days, sixty_days, ninty_days):

	final_dict = {}
	project=project
	center = center
	dates_list = [thirty_days, sixty_days, ninty_days]
	tables = [Internalerrors, Externalerrors]
	packet_wise_error=[{}, {}, {}, {}, {}, {}]
	i=0

	for date_list in dates_list:
	  for table in tables:
	    packets = table.objects.filter(project=project, center=center, date__range=(date_list[-1], date_list[0])).values_list('work_packet', flat=True).distinct()
	    for item in packets:
	      total_error = table.objects.filter(project=project, center=center, date__range=(date_list[-1], date_list[0]), work_packet=item).aggregate(Sum('total_errors'))['total_errors__sum']
	      packet_wise_error[i][item] = total_error
	    i+=1

	final_dict['result'] = OrderedDict()

	months_names = [('thirty_days_data', 0, 1), ('sixty_days_data', 2, 3), ('ninty_days_data', 4, 5)]
	
	for month in months_names:
		final_dict['result'][month[0]] = OrderedDict()
		final_dict['result'][month[0]]['internalerrors'] = OrderedDict(sorted(packet_wise_error[month[1]].items(), key=itemgetter(1), reverse=True)[:5])
		final_dict['result'][month[0]]['externalerrors'] = OrderedDict(sorted(packet_wise_error[month[2]].items(), key=itemgetter(1), reverse=True)[:5])

	return final_dict

def static_internal_external_packet_errors(request):

	project = request.GET.get('project', '')
	center = request.GET.get('center', '').split(' -')[0]

	pro_id = Project.objects.get(name=project).id
	center_id = Center.objects.get(name=center).id

	dates_list = dates_data(pro_id, center_id)

	result = get_internal_external_packet_errors(pro_id, center_id, dates_list[0], dates_list[1], dates_list[2])

	return JsonResponse(result)


def static_internal_external_agent_errors(request):

	project = request.GET.get('project', '')
	center = request.GET.get('center', '').split(' -')[0]

	pro_id = Project.objects.get(name=project).id
	center_id = Center.objects.get(name=center).id

	dates_list = dates_data(pro_id, center_id)

	result = get_internal_external_agent_error_data(pro_id, center_id, dates_list[0], dates_list[1], dates_list[2])

	return JsonResponse(result)

def static_internal_external_error_category(request):
	project = request.GET.get('project', '')
	center = request.GET.get('center', '').split(' -')[0]

	pro_id = Project.objects.get(name=project).id
	center_id = Center.objects.get(name=center).id

	dates_list = dates_data(pro_id, center_id)
	result = get_internal_external_error_category_data(pro_id, center_id, dates_list[0], dates_list[1], dates_list[2])
	return JsonResponse(result)