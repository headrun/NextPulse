from django.core.management.base import BaseCommand

class Command(BaseCommand):

    commands = ['generatedata',]
    args = '[command]'
    help = 'generate data'

    def handle(self, *args, **options):

        from api.models import Project,Center,RawTable,Internalerrors,Externalerrors,Targets,Headcount,TatTable
        import datetime
        import calendar
        from django.db.models import Sum, Max
        from datetime import timedelta
        from dateutil.relativedelta import relativedelta
        import itertools
        import redis
        current_date = datetime.date.today()
        last_mon_date = current_date - relativedelta(months=3)
        from_date = datetime.datetime(last_mon_date.year, last_mon_date.month, 1).date()
        start_date = datetime.datetime(current_date.year, current_date.month, 1)  
        to_date = start_date.date() - relativedelta(days=1)
        days = (to_date - from_date).days
        days = days + 1
        months_dict = {}
        for i in xrange(days):
            date = from_date + datetime.timedelta(i)
            month = date.strftime("%B")
            if month in months_dict:
                months_dict[month].append(str(date))
            else:
                months_dict[month] = [str(date)]
        for month_name,month_dates in months_dict.iteritems():
            dates_list = month_dates
            proje_cent = ['Probe','NTT DATA Services TP','NTT DATA Services Coding','Federal Bank','Ujjivan','Gooru',\
                          'Walmart Salem','IBM','IBM South East Asia','IBM Pakistan','IBM Africa','IBM DCIW Arabia',\
                          'IBM Quality Control','IBM India and Sri Lanka','IBM NA and EU','IBM Arabia','IBM DCIW',\
                          'IBM Latin America','IBM Sri Lanka P2P', 'Walmart Chittor', 'Mobius','Jumio']
            ext_audit_sal, ext_audit_chi, int_audit_sal, int_audit_chi = [], [], [], []
            ext_err_sal, ext_err_chi, int_err_sal, int_err_chi = [], [], [], []
            for pro_cen in proje_cent:
                values = Project.objects.filter(name=pro_cen).values_list('id','center_id')
                prj_id = values[0][0]
                center_id = values[0][1]
                prj_name = pro_cen   
                conn = redis.Redis(host="localhost", port=6379, db=0)
                center_name = Center.objects.filter(project=prj_id).values_list('name',flat=True)[0]
                external = Externalerrors.objects.filter(project=prj_id,center=center_id,date__range=[dates_list[0],dates_list[-1]])
                external_packets = external.values('sub_project', 'work_packet').distinct()
                internal = Internalerrors.objects.filter(project=prj_id,center=center_id,date__range=[dates_list[0],dates_list[-1]])
                internal_packets = internal.values('sub_project', 'work_packet').distinct()
                volume = RawTable.objects.filter(project=prj_id,center=center_id,date__range=[dates_list[0],dates_list[-1]])
                prj_audit_val, prj_err_val, prj_int_audit_val, prj_int_err_val = [], [], [], []
                accuracy_dict = {}
                for ext_pack in external_packets:             
                    if ext_pack['work_packet'] != '' and ext_pack['sub_project'] != '':
                        packet = ext_pack['sub_project']
                        ext_error_data = external.filter(sub_project = packet).aggregate(Sum('total_errors'))
                        ext_audit_data = external.filter(sub_project = packet).aggregate(Sum('audited_errors'))
                        ext_volume_data = volume.filter(sub_project = packet).aggregate(Sum('per_day'))                        
                    else:
                        packet = ext_pack['work_packet']
                        ext_error_data = external.filter(work_packet = packet).aggregate(Sum('total_errors'))
                        ext_audit_data = external.filter(work_packet = packet).aggregate(Sum('audited_errors'))
                        ext_volume_data = volume.filter(work_packet = packet).aggregate(Sum('per_day'))     
                    if ext_audit_data['audited_errors__sum']:
                        ext_audited_val = ext_audit_data['audited_errors__sum']
                    else:
                        ext_audited_val = ext_volume_data['per_day__sum']
                    if ext_error_data['total_errors__sum']:
                        ext_error_val = ext_error_data['total_errors__sum']
                    else:
                        ext_error_val = 0
                    prj_audit_val.append(ext_audited_val)
                    prj_err_val.append(ext_error_val)
                if sum(prj_audit_val):
                    ext_acc = (float(sum(prj_err_val))/float(sum(prj_audit_val)))*100
                    ext_acc = 100 - float('%.2f' % round(ext_acc,2))
                else:
                    ext_acc = 'NA'

                for int_pack in internal_packets:
                    if int_pack['work_packet'] != '' and int_pack['sub_project'] != '':
                        packet = int_pack['sub_project']
                        int_error_data = internal.filter(sub_project = packet).aggregate(Sum('total_errors'))
                        int_audit_data = internal.filter(sub_project = packet).aggregate(Sum('audited_errors'))
                        int_volume_data = volume.filter(sub_project = packet).aggregate(Sum('per_day'))
                    else:
                        packet = int_pack['work_packet']
                        int_error_data = internal.filter(work_packet = packet).aggregate(Sum('total_errors'))
                        int_audit_data = internal.filter(work_packet = packet).aggregate(Sum('audited_errors'))
                        int_volume_data = volume.filter(work_packet = packet).aggregate(Sum('per_day'))
                    if int_audit_data['audited_errors__sum']:
                        int_audited_val = int_audit_data['audited_errors__sum']
                    else:
                        int_audited_val = int_volume_data['per_day__sum']
                    if int_error_data['total_errors__sum']:
                        int_error_val = int_error_data['total_errors__sum']
                    else:
                        int_error_val = 0
                    prj_int_audit_val.append(int_audited_val)
                    prj_int_err_val.append(int_error_val)

                if sum(prj_int_audit_val):
                    int_acc = (float(sum(prj_int_err_val))/float(sum(prj_int_audit_val)))*100
                    int_acc = 100 - float('%.2f' % round(int_acc,2))
                else:
                    int_acc = 'NA'
                if center_name == 'Salem' and prj_name != 'IBM':
                    ext_audit_sal.append(sum(prj_audit_val))
                    ext_err_sal.append(sum(prj_err_val))
                    int_audit_sal.append(sum(prj_int_audit_val))
                    int_err_sal.append(sum(prj_int_err_val))
                    if sum(ext_audit_sal):
                        cen_ext_acc = (float(sum(ext_err_sal))/float(sum(ext_audit_sal)))*100
                        cen_ext_acc = 100 - float('%.2f' % round(cen_ext_acc,2))
                    else:
                        cen_ext_acc = 'NA'
                    if sum(int_audit_sal):
                        cen_int_acc = (float(sum(int_err_sal))/float(sum(int_audit_sal)))*100
                        cen_int_acc = 100 - float('%.2f' % round(cen_int_acc,2))
                    else:
                        cen_int_acc = 'NA'
                if center_name == 'Chittoor' and prj_name != 'IBM':
                    ext_audit_chi.append(sum(prj_audit_val))
                    ext_err_chi.append(sum(prj_err_val))
                    int_audit_chi.append(sum(prj_int_audit_val))
                    int_err_chi.append(sum(prj_int_err_val))
                    if sum(ext_audit_chi):
                        cen_ext_acc = (float(sum(ext_err_chi))/float(sum(ext_audit_chi)))*100
                        cen_ext_acc = 100 - float('%.2f' % round(cen_ext_acc,2))
                    else:
                        cen_ext_acc = 'NA'
                    if sum(int_audit_chi):
                        cen_int_acc = (float(sum(int_err_chi))/float(sum(int_audit_chi)))*100
                        cen_int_acc = 100 - float('%.2f' % round(cen_int_acc,2))
                    else:
                        cen_int_acc = 'NA' 
                accuracy_dict['project'] = prj_name
                accuracy_dict['center']  = center_name
                accuracy_dict['month']  = month_name
                accuracy_dict['external_accuracy'] = ext_acc
                accuracy_dict['internal_accuracy'] = int_acc
                accuracy_dict['center_external_accuracy'] = cen_ext_acc
                accuracy_dict['center_internal_accuracy'] = cen_int_acc
                final_dict = {}
                for key, value in accuracy_dict.iteritems():
                    acc_dict = {}
                    if key == 'external_accuracy':
                        redis_key = '{0}_{1}_{2}_external_accuracy'.format(prj_name,center_name,month_name)
                        acc_dict['external_accuracy'] = str(ext_acc)
                        final_dict[redis_key] = acc_dict
                    if key == 'internal_accuracy':
                        redis_key = '{0}_{1}_{2}_internal_accuracy'.format(prj_name,center_name,month_name)
                        acc_dict['internal_accuracy'] = str(int_acc)
                        final_dict[redis_key] = acc_dict
                    if key == 'center_internal_accuracy':
                        redis_key = '{0}_{1}_center_internal_accuracy'.format(center_name,month_name)
                        acc_dict['center_internal_accuracy'] = str(cen_int_acc)
                        final_dict[redis_key] = acc_dict
                    if key == 'center_external_accuracy':
                        redis_key = '{0}_{1}_center_external_accuracy'.format(center_name,month_name)
                        acc_dict['center_external_accuracy'] = str(cen_ext_acc)
                        final_dict[redis_key] = acc_dict
                current_keys = []
                for key, value in final_dict.iteritems():
                    current_keys.append(key)
                    conn.hmset(key, value)
                    print key, value

