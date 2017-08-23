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
        #proje_cent = Project.objects.values_list('id','center_id','name')
        #generating last 3 months dates
        current_date = datetime.date.today()
        last_mon_date = current_date - relativedelta(months=3)
        from_date = datetime.datetime(last_mon_date.year, last_mon_date.month, 1).date()
        start_date = datetime.datetime(current_date.year, current_date.month, 1)
        to_date = start_date.date() - relativedelta(days=1)
        days = (to_date - from_date).days
        days = days + 1
        months_dict = {}
        month_list = [[]]
        month_names_list = []
        month_count = 0
        for i in xrange(days):
            date = from_date + datetime.timedelta(i)
            month = date.strftime("%B")
            if month not in month_names_list:
                month_names_list.append(month)
            if month in months_dict:
                months_dict[month].append(str(date))
                month_list[month_count].append(str(date))
            else:
                months_dict[month] = [str(date)]
                month_count = month_count + 1
                month_list.append([str(date)])
        final_project_data = []
        proje_cent = Project.objects.values_list('name',flat=True)
        not_req = ["3i VAPP", "3iKYC", "Bridgei2i", "E4U", "indix", "Nextgen", "IBM Sri Lanka P2P", "Quarto","Tally", "Sulekha", "Webtrade", "Walmart Chittor","Bigbasket","Future Energie Tech"]
        proje_cent = filter(lambda x: x not in not_req, list(proje_cent))
        #proje_cent = ["Probe"]
        for pro_cen in proje_cent:
            values = Project.objects.filter(name=pro_cen).values_list('id','center_id')
            prj_id = values[0][0]
            center_id = values[0][1]
            prj_name = pro_cen
            final_productivity_list = []
            conn = redis.Redis(host="localhost", port=6379, db=0)
            center_name = Center.objects.filter(project=prj_id).values_list('name',flat=True)[0]
            for month_name,month_dates in months_dict.iteritems():
                dates_list = month_dates
                volumes = RawTable.objects.filter(project=prj_id,center=center_id,date__range=[dates_list[0],dates_list[-1]])
                external_packets = Externalerrors.objects.filter(project=prj_id,center=center_id,date__range=[dates_list[0],dates_list[-1]])
                internal_packets = Internalerrors.objects.filter(project=prj_id,center=center_id,date__range=[dates_list[0],dates_list[-1]])
                volume_list = volumes.values('sub_project').distinct()
                volumes_data = volumes.values('sub_project','work_packet').distinct()
                if volume_list[0]['sub_project']:
                    volume_list = volume_list
                    internal_pack_list = internal_packets.values_list('sub_project',flat=True).distinct()
                    external_pack_list = external_packets.values_list('sub_project',flat=True).distinct()
                else:
                    volume_list = volumes.values_list('work_packet',flat=True).distinct()
                    internal_pack_list = internal_packets.values_list('work_packet',flat=True).distinct()
                    external_pack_list = external_packets.values_list('work_packet',flat=True).distinct()
                final_productivity_dict = {}
                new_date_list, tat_values = [] , []
                productivity, tat_data = {}, {}
                date_values, main_values = {}, {}
                acc_values, int_acc_values = {}, {}
                vol_error_values, int_vol_error_values = {}, {}
                vol_audit_data, int_vol_audit_data = {}, {} 
                all_error_types, int_all_error_types = [], []
                sub_error_types, int_sub_error_types = [], []
                fte_data, prod_utili = [], []
                operational_data = []
                for date_va in dates_list:
                    total_done_value = RawTable.objects.filter(project=prj_id, center=center_id, date=date_va).aggregate(Max('per_day'))
                    if total_done_value['per_day__max']>0:
                        new_date_list.append(date_va)
                        for vol_type in volume_list:    
                            final_work_packet = vol_type
                            
                            if volumes_data[0]['work_packet'] != '' and volumes_data[0]['sub_project'] != '':
                                final_work_packet = final_work_packet['sub_project']
                                #targets = Targets.objects.filter(project=prj_id,center=center_id,from_date__lte=date_va,to_date__gte=date_va,sub_project=final_work_packet,target_type = 'FTE Target').aggregate(Sum('target_value'))
                                #to_target = Targets.objects.filter(project=prj_id,center=center_id,from_date__lte=date_va,to_date__gte=date_va,sub_project=final_work_packet,target_type = 'Target').aggregate(Sum('target_value'))
                                tar = Targets.objects.filter(project=prj_id,center=center_id,from_date__lte=date_va,to_date__gte=date_va,sub_project=final_work_packet,target_type = 'FTE Target').values_list('target_value',flat=True).distinct()
                                targets = sum(tar)
                                to_tar = Targets.objects.filter(project=prj_id,center=center_id,from_date__lte=date_va,to_date__gte=date_va,sub_project=final_work_packet,target_type = 'Target').values_list('target_value',flat=True).distinct()
                                to_target = sum(to_tar)
                                emp_count = Headcount.objects.filter(project=prj_id, center=center_id, date=date_va,sub_project = final_work_packet).aggregate(Sum('billable_agents'))
                                tat_da = TatTable.objects.filter(project=prj_id, center=center_id, date=date_va, sub_project = final_work_packet)
                                met_va = tat_da.aggregate(Sum('met_count'))
                                not_met_va = tat_da.aggregate(Sum('non_met_count'))
                                tat_met_va = met_va['met_count__sum']
                                tat_not_met_va = not_met_va['non_met_count__sum']
                            else:
                                final_work_packet = final_work_packet
                                #to_target = Targets.objects.filter(project=prj_id,center=center_id,from_date__gte=date_va,to_date__lte=date_va,work_packet=final_work_packet,target_type = 'Target').aggregate(Sum('target_value'))
                                to_tar = Targets.objects.filter(project=prj_id,center=center_id,from_date=date_va,to_date=date_va,work_packet=final_work_packet,target_type = 'Target').values_list('target_value',flat=True).distinct()
                                to_target = sum(to_tar)
                                #targets = Targets.objects.filter(project=prj_id,center=center_id,from_date__gte=date_va,to_date__lte=date_va,work_packet=final_work_packet,target_type = 'FTE Target').aggregate(Sum('target_value'))
                                tar = Targets.objects.filter(project=prj_id,center=center_id,from_date=date_va,to_date=date_va,work_packet=final_work_packet,target_type = 'FTE Target').values_list('target_value',flat=True).distinct()
                                targets = sum(tar)
                                emp_count = Headcount.objects.filter(project=prj_id, center=center_id, date=date_va,work_packet = final_work_packet).aggregate(Sum('billable_agents'))
                                tat_da = TatTable.objects.filter(project=prj_id, center=center_id, date=date_va, work_packet = final_work_packet)
                                met_va = tat_da.aggregate(Sum('met_count'))
                                not_met_va = tat_da.aggregate(Sum('non_met_count'))
                                tat_met_va = met_va['met_count__sum']
                                tat_not_met_va = not_met_va['non_met_count__sum']    
                            if emp_count['billable_agents__sum'] == None:
                                emp_count['billable_agents__sum'] = 0
                            #import pdb;pdb.set_trace()
                            if targets > 0 and to_target == 0:
                                targets = targets * emp_count['billable_agents__sum']
                            else:
                                targets = to_target
                            date_pattern = '{0}_{1}_{2}_{3}'.format(prj_name, center_name, final_work_packet,date_va)
                            key_list = conn.keys(pattern=date_pattern)
                            if not key_list:
                                if date_values.has_key(final_work_packet):
                                    date_values[final_work_packet].append(0)
                                else:
                                    date_values[final_work_packet] = [0]
                            for cur_key in key_list:
                                var = conn.hgetall(cur_key)
                                for key, value in var.iteritems():
                                    if value == 'None':
                                        value = 0
                                    if date_values.has_key(key):
                                        if targets:
                                            pac_val = (float(value)/float(targets))*100
                                            pac_val = float('%.2f' % round(pac_val, 2))
                                            date_values[key].append(pac_val)
                                        else:
                                            date_values[key].append(0)
                                    else:
                                        if targets:
                                            pac_val = (float(value)/float(targets))*100
                                            pac_val = float('%.2f' % round(pac_val, 2))
                                            date_values[key] = [pac_val]
                                        else:
                                            date_values[key] = [0]
                                    """if main_values.has_key(key):
                                        if to_target:
                                            pak_val = (float(value)/float(to_target))*100
                                            pak_val = float('%.2f' % round(pak_val, 2))
                                            main_values[key].append(pak_val)
                                        else:
                                            main_values[key].append(0)
                                    else:
                                        if to_target:
                                            pak_val = (float(value)/float(to_target))*100
                                            pak_val = float('%.2f' % round(pak_val, 2))
                                            main_values[key] = [pak_val]
                                        else:
                                            main_values[key] = [0]"""
                                    #generating tat code
                                    
                                    if tat_data.has_key(key):
                                        if tat_met_va:
                                            met_val = (tat_met_va/(tat_met_va + tat_not_met_va)) * 100
                                            tat_data[key].append(met_val)
                                        else:
                                            tat_data[key].append(0)
                                    else:
                                        if tat_met_va:
                                            met_val = (tat_met_va/(tat_met_va + tat_not_met_va)) * 100
                                            tat_data[key] = [met_val]
                                        else:
                                            tat_data[key] = [0]
                        #generation of external accuracy code
                        for packet in external_pack_list:
                            work_packet = packet
                            key_pattern = '{0}_{1}_{2}_{3}_{4}'.format(prj_name, center_name, work_packet, date_va,'externalerror')
                            audit_key_list = conn.keys(pattern=key_pattern)
                            if not audit_key_list:
                                if vol_error_values.has_key(work_packet):
                                    vol_error_values[work_packet].append("NA")
                                    vol_audit_data[work_packet].append("NA")
                                else:
                                    vol_error_values[work_packet] = ["NA"]
                                    vol_audit_data[work_packet] = ["NA"]
                            var2 = [conn.hgetall(cur_key) for cur_key in audit_key_list]
                            if var2:
                                var2 = var2[0]
                            else:
                                var2 = {}
                            for key, value in var2.iteritems():
                                if key == 'types_of_errors':
                                    int_all_error_types.append(value)
                                elif key == 'sub_error_types':
                                    int_sub_error_types.append(value)
                                else:
                                    if value == 'None':
                                        value = "NA"
                                    error_vol_type = work_packet
                                    if key == 'total_errors':
                                        if vol_error_values.has_key(error_vol_type):
                                            if value =="NA":
                                                vol_error_values[error_vol_type].append(value)
                                            else:
                                                vol_error_values[error_vol_type].append(int(value))
                                        else:
                                            if value =="NA":
                                                vol_error_values[error_vol_type] = [value]
                                            else:
                                                vol_error_values[error_vol_type] = [int(value)]
                                    else:
                                        if vol_audit_data.has_key(error_vol_type):
                                            if value=="NA":
                                                vol_audit_data[error_vol_type].append(value)
                                            else:
                                                vol_audit_data[error_vol_type].append(int(value))
                                        else:
                                            if value=="NA":
                                                vol_audit_data[error_vol_type] = [value]
                                            else:
                                                vol_audit_data[error_vol_type] = [int(value)]
                            prod_pattern = '{0}_{1}_{2}_{3}'.format(prj_name, center_name, work_packet,date_va)
                            prod_key_list = conn.keys(pattern=prod_pattern)
                            if not prod_key_list:
                                if acc_values.has_key(work_packet):
                                    acc_values[work_packet].append(0)
                                else:
                                    acc_values[work_packet] = [0]
                            for curr_key in prod_key_list:
                                val = conn.hgetall(curr_key)
                                for key,value in val.iteritems():
                                    if value == 'None':
                                        value = 0
                                    if acc_values.has_key(key):
                                        acc_values[key].append(int(value))
                                    else:
                                        acc_values[key] = [int(value)]

                        #generation of internal accuracy
                        for int_packet in internal_pack_list:
                            int_work_packet = int_packet
                            int_key_pattern = '{0}_{1}_{2}_{3}_{4}'.format(prj_name, center_name, int_work_packet, date_va,'error')
                            int_audit_key_list = conn.keys(pattern=int_key_pattern)
                            if not int_audit_key_list:
                                if int_vol_error_values.has_key(int_work_packet):
                                    int_vol_error_values[int_work_packet].append("NA")
                                    int_vol_audit_data[int_work_packet].append("NA")
                                else:
                                    int_vol_error_values[int_work_packet] = ["NA"]
                                    int_vol_audit_data[int_work_packet] = ["NA"]
                            var1 = [conn.hgetall(cur_key) for cur_key in int_audit_key_list]
                            if var1:
                                var1 = var1[0]
                            else:
                                var1 = {}
                            for key, value in var1.iteritems():
                                if key == 'types_of_errors':
                                    int_all_error_types.append(value)
                                elif key == 'sub_error_types':
                                    int_sub_error_types.append(value)
                                else:
                                    if value == 'None':
                                        value = "NA"
                                    error_vol_type = int_work_packet
                                    if key == 'total_errors':
                                        if int_vol_error_values.has_key(error_vol_type):
                                            if value =="NA":
                                                int_vol_error_values[error_vol_type].append(value)
                                            else:
                                                int_vol_error_values[error_vol_type].append(int(value))
                                        else:
                                            if value =="NA":
                                                int_vol_error_values[error_vol_type] = [value]
                                            else:
                                                int_vol_error_values[error_vol_type] = [int(value)]
                                    else:
                                        if int_vol_audit_data.has_key(error_vol_type):
                                            if value=="NA":
                                                int_vol_audit_data[error_vol_type].append(value)
                                            else:   
                                                int_vol_audit_data[error_vol_type].append(int(value))
                                        else:
                                            if value=="NA":
                                                int_vol_audit_data[error_vol_type] = [value]
                                            else:
                                                int_vol_audit_data[error_vol_type] = [int(value)]
                            prod_int_pattern = '{0}_{1}_{2}_{3}'.format(prj_name, center_name, int_work_packet,date_va)
                            prod_int_key_list = conn.keys(pattern=prod_int_pattern)
                            if not prod_int_key_list:
                                if int_acc_values.has_key(int_work_packet):
                                    int_acc_values[int_work_packet].append(0)
                                else:
                                    int_acc_values[int_work_packet] = [0]
                            for curr_key in prod_int_key_list:
                                data = conn.hgetall(curr_key)
                                for key,value in data.iteritems():
                                    if value == 'None':
                                        value = 0
                                    if int_acc_values.has_key(key):
                                        int_acc_values[key].append(int(value))
                                    else:
                                        int_acc_values[key] = [int(value)]

                        #generation of fte and operational headcount data
                        prod_vals = RawTable.objects.filter(project=prj_id, center=center_id, date=date_va).aggregate(Sum('per_day'))
                        headcount_details = Headcount.objects.filter(project=prj_id, center=center_id, date=date_va).aggregate(Sum('billable_hc'),Sum('billable_agents'),Sum('buffer_agents'),Sum('qc_or_qa'),Sum('teamlead'),Sum('trainees_and_trainers'))
                        pro_da = prod_vals['per_day__sum']
                        if headcount_details['billable_hc__sum'] != None:
                            utilization_numerator = headcount_details['billable_hc__sum']
                            fte_utilization = headcount_details['billable_agents__sum'] + headcount_details['buffer_agents__sum'] + headcount_details['qc_or_qa__sum'] + headcount_details['teamlead__sum']
                            fte_value = (float(utilization_numerator)/float(fte_utilization))*100
                            fte_utili_value = float('%.2f' % round(fte_value,2))
                            operational_utilization = fte_utilization + headcount_details['trainees_and_trainers__sum']
                            operational_value = (float(utilization_numerator)/float(operational_utilization))*100
                            operational_utili_value = float('%.2f' % round(operational_value,2))
                            prod_utilisa = float(pro_da)/float(utilization_numerator)
                            prod_utili.append(prod_utilisa)
                            fte_data.append(fte_utili_value)
                            operational_data.append(operational_utili_value)
                        else:
                            fte_data.append(0)
                            operational_data.append(0)
                            prod_utili.append(0)
                #calculation for productivity value
                len_list, prod_len_list = [], []
                productivity_data, production_data = [], []
                packet_values = date_values.values()
                packet_data = [sum(x) for x in zip(*packet_values)]
                packet_len_values = [x for x in zip(*packet_values) if x != 0]
                for value in packet_len_values:
                    packet_len = [count for count in value if count != 0]
                    len_list.append(len(packet_len))
                for val,pac in zip(packet_data,len_list):
                    if pac:
                        productivity = float(float(val)/float(pac))
                        final_productivity = float('%.2f' % round(productivity,2))
                    else:
                        final_productivity = 0
                    productivity_data.append(final_productivity)
                if len(new_date_list) and sum(productivity_data):
                    productivity_value = float(float(sum(productivity_data))/len(new_date_list))
                    productivity_value = float('%.2f' % round(productivity_value,2))
                else:
                    productivity_value = "NA"
                #calculation for production value
                """prod_values = main_values.values()
                prod_data = [sum(x) for x in zip(*prod_values)]
                prod_len_values = [x for x in zip(*prod_values) if x != 0]
                for value in prod_len_values:
                    prod_packet_len = [count for count in value if count != 0]
                    prod_len_list.append(len(prod_packet_len))
                for ma_val,prod_val in zip(prod_data,prod_len_list):
                    if prod_val:
                        production = float(float(ma_val)/float(prod_val))
                        final_prod = float('%.2f' % round(production,2))
                    else:
                        final_prod = 0
                    production_data.append(final_prod)

                if len(new_date_list) and sum(production_data):
                    production_value = float(float(sum(production_data))/len(new_date_list))
                    production_value = float('%.2f' % round(production_value,2))
                else:
                    production_value = "NA" """
                #calculation of tat data
                tat_val_len, tat_fin_val  = [], []
                tat_val = tat_data.values()
                tat_pack_val = [sum(y) for y in zip(*tat_val)]
                tat_var = [x for x in zip(*tat_val) if x != 0]
                for data in tat_var:
                    tat_len = [va for va in data if va != 0]
                    tat_val_len.append(len(tat_len))
                for ta_val, ta_len_val in zip(tat_pack_val, tat_val_len):
                    if ta_len_val:
                        tat = float(ta_val)/ta_len_val
                        fin_tat = float('%.2f' % round(tat,2))
                    else:
                        fin_tat = 0
                    tat_fin_val.append(fin_tat)
                if len(new_date_list) and sum(tat_fin_val):
                    tat_final_value = float(sum(tat_fin_val))/len(new_date_list)
                    tat_final_value = float('%.2f' % round(tat_final_value,2))
                else:
                    tat_final_value = "NA"
                #calculation for external accuracy code
                acc_values_sum = {}
                for key, value in acc_values.iteritems():
                    production_data = [i for i in value if i!='NA']
                    acc_values_sum[key] = sum(production_data)
                error_volume_data = {}
                for key, value in vol_error_values.iteritems():
                    error_filter = [i for i in value if i!='NA']
                    error_volume_data[key] = sum(error_filter)
                error_audit_data = {}
                for key, value in vol_audit_data.iteritems():
                    error_filter = [i for i in value if i!='NA']
                    error_audit_data[key] = sum(error_filter)
                error_accuracy = {}
                for key,value in error_volume_data.iteritems():
                    if error_audit_data[key]:
                        percentage = ((float(value)/float(error_audit_data[key])))*100
                        percentage = 100 - float('%.2f' % round(percentage, 2))
                        error_accuracy[key] = [percentage]
                    else:
                        if error_audit_data[key] == 0 and acc_values_sum.has_key(key):
                            try:
                                percentage = (float(value) / acc_values_sum[key]) * 100
                                percentage = 100 - float('%.2f' % round(percentage, 2))
                                error_accuracy[key] = [percentage]
                            except:
                                error_accuracy[key] = [0]
                        else:
                            percentage = 0
                            error_accuracy[key] = [percentage] 

                accuracy_values = error_accuracy.values()
                err_values = [i for i in error_accuracy.values() if i != [0]]
                acc_err_values = [sum(k) for k in err_values]
                sum_acc_values = sum(acc_err_values)
                final_value = float('%.2f' % round(sum_acc_values,2))
                if len(err_values):
                    final_accuracy = float(float(final_value)/len(err_values))
                    final_external_accuracy = float('%.2f' % round(final_accuracy,2))
                else:
                    final_external_accuracy = "NA"
                #calculation for internal accuracy
                int_acc_values_sum = {}
                for key, value in int_acc_values.iteritems():
                    int_production_data = [i for i in value if i!='NA']
                    int_acc_values_sum[key] = sum(int_production_data)
                int_error_volume_data = {}
                for key, value in int_vol_error_values.iteritems():
                    int_error_filter = [i for i in value if i!='NA']
                    int_error_volume_data[key] = sum(int_error_filter)
                int_error_audit_data = {}
                for key, value in int_vol_audit_data.iteritems():
                    error_filter = [i for i in value if i!='NA']
                    int_error_audit_data[key] = sum(error_filter)

                int_error_accuracy = {}
                for key,value in int_error_volume_data.iteritems():
                    if int_error_audit_data[key]:
                        percentage = ((float(value)/float(int_error_audit_data[key])))*100
                        int_percentage = 100 - float('%.2f' % round(percentage, 2))
                        int_error_accuracy[key] = [int_percentage]
                    else:
                        if int_error_audit_data[key] == 0 and int_acc_values_sum.has_key(key):
                            try:
                                percentage = (float(value) / int_acc_values_sum[key]) * 100
                                int_percentage = 100 - float('%.2f' % round(percentage, 2))
                                int_error_accuracy[key] = [int_percentage]
                            except:
                                int_error_accuracy[key] = [0]
                        else:
                            int_percentage = 0
                            int_error_accuracy[key] = [int_percentage]
                
                int_accuracy_values = int_error_accuracy.values()
                int_err_values = [i for i in int_error_accuracy.values() if i != [0]]
                int_acc_err_values = [sum(k) for k in int_err_values]
                int_sum_acc_values = sum(int_acc_err_values)   
                int_final_value = float('%.2f' % round(int_sum_acc_values,2))
                if len(int_err_values):
                    final_int_accuracy = float(float(int_final_value)/len(int_err_values))
                    final_internal_accuracy = float('%.2f' % round(final_int_accuracy,2))
                else:
                    final_internal_accuracy = "NA"
                #fte,operational utilization calculations
                no_of_days = Project.objects.filter(name = prj_name).values('days_month')
                month_days = no_of_days[0]['days_month']
                if len(new_date_list):
                    fte_utiliti_value = sum(fte_data)/len(new_date_list)
                    operational_utiliti_value = sum(operational_data)/len(new_date_list)
                    final_fte = float('%.2f' % round(fte_utiliti_value,2))
                    final_operational = float('%.2f' % round(operational_utiliti_value,2))
                    produc_utilisation_val = sum(prod_utili)/len(new_date_list)
                    final_prod_util = float('%.2f' % round(produc_utilisation_val,2))
                else:
                    final_fte = 0
                    final_operational = 0
                    final_prod_util = 0
                final_productivity_dict['project'] = prj_name
                final_productivity_dict['center'] = center_name
                final_productivity_dict['month'] = month_name
                final_productivity_dict['productivity'] = productivity_value
                #final_productivity_dict['production'] = production_value
                final_productivity_dict['external_accuracy'] = final_external_accuracy
                final_productivity_dict['internal_accuracy'] = final_internal_accuracy
                final_productivity_dict['fte_utilisation'] = final_fte
                final_productivity_dict['operational_utilization'] = final_operational
                final_productivity_dict['tat'] = tat_final_value
                final_productivity_dict['prod_utili'] = final_prod_util
                final_productivity_list.append(final_productivity_dict)
                data_dict = {}
                for key,value in final_productivity_dict.iteritems():
                    value_dict = {}
                    if key == 'productivity':
                        redis_key = '{0}_{1}_{2}_productivity'.format(prj_name,center_name,month_name)
                        value_dict['productivity'] = str(productivity_value)
                        data_dict[redis_key] = value_dict

                    """if key == 'production':
                        redis_key = '{0}_{1}_{2}_production'.format(prj_name,center_name,month_name)
                        value_dict['production'] = str(production_value)
                        data_dict[redis_key] = value_dict"""

                    if key == 'external_accuracy':
                        redis_key = '{0}_{1}_{2}_external_accuracy'.format(prj_name,center_name,month_name)
                        value_dict['external_accuracy'] = str(final_external_accuracy)
                        data_dict[redis_key] = value_dict
                    if key == 'internal_accuracy':
                        redis_key = '{0}_{1}_{2}_internal_accuracy'.format(prj_name,center_name,month_name)
                        value_dict['internal_accuracy'] = str(final_internal_accuracy)
                        data_dict[redis_key] = value_dict
                    if key == 'fte_utilisation':
                        redis_key = '{0}_{1}_{2}_fte_utilisation'.format(prj_name,center_name,month_name)
                        value_dict['fte_utilisation'] = str(final_fte)
                        data_dict[redis_key] = value_dict
                    if key == 'operational_utilization':
                        redis_key = '{0}_{1}_{2}_operational_utilization'.format(prj_name,center_name,month_name)
                        value_dict['operational_utilization'] = str(final_operational)
                        data_dict[redis_key] = value_dict
                    if key == 'prod_utili':
                        redis_key = '{0}_{1}_{2}_prod_utili'.format(prj_name,center_name,month_name)
                        value_dict['prod_utili'] = str(final_prod_util)
                        data_dict[redis_key] = value_dict
                    if key == 'tat':
                        redis_key = '{0}_{1}_{2}_tat'.format(prj_name,center_name,month_name)
                        value_dict['tat'] = str(tat_final_value)
                        data_dict[redis_key] = value_dict
                conn = redis.Redis(host="localhost", port=6379, db=0) 
                current_keys = []
                for key, value in data_dict.iteritems():
                    current_keys.append(key)
                    conn.hmset(key, value) 
                    print key, value 
               #print productivity_data,productivity_value,fte_data,operational_data
            final_project_data.append(final_productivity_list)
