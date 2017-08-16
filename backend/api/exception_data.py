
from django.db.models import Sum
from django.db.models import Max
from api.models import *


def pre_scan_exception_data(date_list, prj_id, center):
    result_data_value = []
    final_result_dict = {}
    final_result_data = []
    for date_value in date_list:
        total_done_value = RawTable.objects.filter(project=prj_id, center=center, date=date_value).aggregate(Max('per_day'))
        if total_done_value['per_day__max'] > 0:
            work_packet = RawTable.objects.filter(project=prj_id, center=center, date=date_value).values_list('work_packet',flat=True).distinct()
            final_packet_value = RawTable.objects.filter(project=prj_id, center=center, date=date_value,work_packet='Scanning').aggregate(Sum('per_day'))
            error_count = Incomingerror.objects.filter(project=prj_id, center=center, date=date_value,work_packet='Scanning').aggregate(Sum('error_values'))
            if error_count['error_values__sum'] > 0 and final_packet_value['per_day__sum'] > 0:
                percentage = (float(error_count['error_values__sum'])/float(error_count['error_values__sum'] + final_packet_value['per_day__sum'])) * 100
                final_percentage_va = (float('%.2f' % round(percentage, 2)))
            else:
                final_percentage_va = 0
            final_result_data.append(final_percentage_va)
    final_result_dict['data'] = final_result_data
    result_data_value.append(final_result_dict)
    return result_data_value

def overall_exception_data(date_list, prj_id, center,level_structure_key):
    result = {}
    for date_value in date_list:
        total_done_value = RawTable.objects.filter(project=prj_id, center=center, date=date_value).aggregate(Max('per_day'))
        if total_done_value['per_day__max'] > 0:
            packets = Incomingerror.objects.filter(project=prj_id, center=center, date=date_value).values_list('work_packet',flat =True).distinct()
            for packet in packets:
                if packet == 'Data Entry' or packet =='KYC Check':
                    sub_packets = Incomingerror.objects.filter(project=prj_id, center=center, date=date_value,work_packet = packet).values_list('sub_packet',flat = True).distinct()
                    work_done = RawTable.objects.filter(project=prj_id, center=center, date=date_value,work_packet = packet).aggregate(Sum('per_day'))
                    error_value = Incomingerror.objects.filter(project=prj_id, center=center, date=date_value,work_packet=packet,sub_packet='Overall Exception').aggregate(Sum('error_values'))
                    if work_done['per_day__sum'] > 0 and error_value['error_values__sum'] > 0:
                        percentage = float(error_value['error_values__sum'])/float(work_done['per_day__sum'])*100
                        percentage = (float('%.2f' % round(percentage, 2)))
                    else:
                        percentage = 0
                    if result.has_key(packet):
                        result[packet].append(percentage)
                    else:
                        result[packet] = [percentage]
    return result

def nw_exception_data(date_list, prj_id, center,level_structure_key):
    result = {}
    for date_value in date_list:
        total_done_value = RawTable.objects.filter(project=prj_id, center=center, date=date_value).aggregate(Max('per_day'))
        if total_done_value['per_day__max'] > 0:
            packets = Incomingerror.objects.filter(project=prj_id, center=center, date=date_value).values_list('work_packet',flat =True).distinct()
            for packet in packets:
                if packet == 'Data Entry' or packet =='KYC Check':
                    sub_packets = Incomingerror.objects.filter(project=prj_id, center=center,work_packet = packet, date=date_value).values_list('sub_packet',flat = True).distinct()
                    error_value = Incomingerror.objects.filter(project=prj_id, center=center, work_packet=packet,sub_packet='NW Exception', date=date_value).aggregate(Sum('error_values'))
                    if error_value['error_values__sum'] > 0: 
                        percentage = float(error_value['error_values__sum'])
                    else:
                        percentage = 0
                    if result.has_key(packet):
                        result[packet].append(percentage)
                    else:
                        result[packet] = [percentage]
    return result
