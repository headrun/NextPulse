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
        #proje_cent = Project.objects.values_list('name',flat=True)
        #not_req = ["3i VAPP", "Bridgei2i", "E4U", "indix", "Nextgen", "IBM Sri Lanka P2P", "Quarto","Tally", "Sulekha", "Webtrade", "Walmart Chittor", "Future Energie Tech"]
        #proje_cent = filter(lambda x: x not in not_req, list(proje_cent))
        proje_cent = ['Probe','NTT DATA Services TP','NTT DATA Services Coding','Federal Bank','Ujjivan','Gooru','Walmart Salem','IBM','IBM South East Asia','IBM Pakistan','IBM Africa','IBM DCIW Arabia','IBM Quality Control','IBM India and Sri Lanka','IBM NA and EU','IBM Arabia','IBM DCIW','IBM Latin America','IBM Sri Lanka P2P']
        for pro_cen in proje_cent:
            values = Project.objects.filter(name=pro_cen).values_list('id','center_id')
            prj_id = values[0][0]
            center_id = values[0][1]
            prj_name = pro_cen
            conn = redis.Redis(host="localhost", port=6379, db=0)
            center_name = Center.objects.filter(project=prj_id).values_list('name',flat=True)[0]
            for month_name,month_dates in months_dict.iteritems():
                dates_list = month_dates
                final_productivity_list,final_actual_val,final_target_val = [], [], []
                billable_hc = Headcount.objects.filter(project=prj_id, center=center_id, date__range=[dates_list[0],dates_list[-1]]).aggregate(Sum('billable_hc'))
                tars = Targets.objects.filter(project=prj_id, center=center_id,from_date__gte=dates_list[0],to_date__lte=dates_list[-1]) 
                if tars:
                    tar_packs = tars.values('sub_project','work_packet','sub_packet').distinct()
                else:
                    tars = Targets.objects.filter(project=prj_id, center=center_id,from_date__lte=dates_list[0],to_date__gte=dates_list[-1])
                    tar_packs = tars.values('sub_project','work_packet').distinct()
                    tar_packs = tar_packs[1:]
                for pac in tar_packs:
                    targets_vals, actual_vals = {}, {}
                    if pac['work_packet'] != '' and pac['sub_project'] == '':
                        work_pack = pac['work_packet']
                        billable_count = Headcount.objects.filter(project=prj_id, center=center_id, date__range=[dates_list[0],dates_list[-1]],work_packet = work_pack).aggregate(Sum('billable_agents'))
                    elif  pac['work_packet'] != '' and pac['sub_project'] != '':
                        work_pack = pac['work_packet']
                        sub_proj = pac['sub_project']
                        billable_count = Headcount.objects.filter(project=prj_id, center=center_id, date__range=[dates_list[0],dates_list[-1]],work_packet = work_pack,sub_project = sub_proj).aggregate(Sum('billable_agents'))
                    elif pac['work_packet'] == '' and pac['sub_project'] != '':
                        sub_proj = pac['sub_project']
                        billable_count = Headcount.objects.filter(project=prj_id, center=center_id, date__range=[dates_list[0],dates_list[-1]],sub_project = sub_proj).aggregate(Sum('billable_agents'))
                    for date_va in dates_list:
                        if pac['work_packet'] != '' and pac['sub_project'] == '':
                            total_done_value = RawTable.objects.filter(project=prj_id, center=center_id, date=date_va, work_packet=work_pack).aggregate(Sum('per_day'))
                        elif pac['work_packet'] != '' and pac['sub_project'] != '':
                            total_done_value = RawTable.objects.filter(project=prj_id, center=center_id, date=date_va, sub_project=sub_proj,work_packet=work_pack).aggregate(Sum('per_day'))
                        elif pac['work_packet'] == '' and pac['sub_project'] != '':
                            total_done_value = RawTable.objects.filter(project=prj_id, center=center_id, date=date_va, sub_project=sub_proj).aggregate(Sum('per_day'))
                        if total_done_value['per_day__sum']>0:
                            if pac['work_packet'] != '' and pac['sub_project'] == '':
                                pack_tar = Targets.objects.filter(project=prj_id, center=center_id,from_date__lte=date_va,to_date__gte=date_va,work_packet=work_pack)
                                tar_va =  pack_tar.filter(target_type='FTE Target').values_list('target_value',flat=True).distinct()
                                tar_vals = sum(tar_va)
                                to_tar_va = pack_tar.filter(target_type='Target').values_list('target_value',flat=True).distinct()
                                to_tar_vals = sum(to_tar_va)
                                billable = Headcount.objects.filter(project=prj_id, center=center_id, date=date_va, work_packet=work_pack).aggregate(Sum('billable_agents'))
                                packet = work_pack
                            elif pac['work_packet'] != '' and pac['sub_project'] != '':
                                pack_tar = Targets.objects.filter(project=prj_id, center=center_id,from_date__lte=date_va,to_date__gte=date_va,work_packet=work_pack, sub_project = sub_proj)
                                tar_va =  pack_tar.filter(target_type='FTE Target').values_list('target_value',flat=True).distinct()
                                tar_vals = sum(tar_va)
                                to_tar_va = pack_tar.filter(target_type='Target').values_list('target_value',flat=True).distinct()
                                to_tar_vals = sum(to_tar_va)
                                billable = Headcount.objects.filter(project=prj_id, center=center_id, date=date_va, sub_project = sub_proj,work_packet=work_pack).aggregate(Sum('billable_agents'))
                                packet = sub_proj+'_'+work_pack
                            elif pac['work_packet'] == '' and pac['sub_project'] != '':
                                pack_tar = Targets.objects.filter(project=prj_id, center=center_id,from_date__lte=date_va,to_date__gte=date_va,sub_project = sub_proj)
                                tar_va =  pack_tar.filter(target_type='FTE Target').values_list('target_value',flat=True).distinct()
                                tar_vals = sum(tar_va)
                                to_tar_va = pack_tar.filter(target_type='Target').values_list('target_value',flat=True).distinct()
                                to_tar_vals = sum(to_tar_va)
                                billable = Headcount.objects.filter(project=prj_id, center=center_id, date=date_va, sub_project = sub_proj).aggregate(Sum('billable_agents'))
                                packet = sub_proj
                            if tar_vals:
                                if billable['billable_agents__sum'] != None:
                                    targ_value = tar_vals * billable['billable_agents__sum']
                                    sing_targ = tar_vals
                                else:
                                    targ_value, tar_vals = 0 , 0
                            
                            elif to_tar_va:
                                targ_value = to_tar_vals
                                sing_targ = to_tar_vals
                            else:
                                targets_vals = {}
                            if targets_vals.has_key(packet):
                                targets_vals[packet].append(targ_value)
                                actual_vals[packet].append(total_done_value['per_day__sum'])
                            else:
                                targets_vals[packet] = [targ_value]
                                actual_vals[packet] = [total_done_value['per_day__sum']]
                    tar_values = targets_vals.values()
                    act_values = actual_vals.values()
                    if tar_values != [] and act_values != []:
                        pac_tar_vals = sum(tar_values[0])
                        pac_act_vals = sum(act_values[0])
                        pac_sin_tar = sing_targ
                        pac_days = len(act_values[0])
                        if pac_tar_vals != 0:
                            prod_cal = (float(pac_act_vals) / float(pac_tar_vals))*100
                            prod_fin_cal = float('%.2f' % round(prod_cal,2))
                        else:
                            prod_fin_cal = 0
                    else:
                        pac_tar_vals, pac_act_vals, pac_days, pac_sin_tar, prod_fin_cal = 0 , 0 , 0 , 0 , 0
                    if pac_tar_vals:
                        final_actual_val.append(pac_act_vals)
                        final_target_val.append(pac_tar_vals)
                        final_month_val = (float(sum(final_actual_val))/float(sum(final_target_val))) * 100
                        final_month_val = float('%.2f' % round(final_month_val,2))
                    else:
                        final_month_val = 0
                    if billable_hc['billable_hc__sum'] != None:
                        bill_ppl = billable_hc['billable_hc__sum']
                        productivity_val = float(sum(final_actual_val))/float(bill_ppl)
                        prod_utility  = float('%.2f' % round(productivity_val,2))
                    else:
                        bill_ppl = 0
                        prod_utility = 0
                    final_target_values = {}
                    final_target_values['project'] = prj_name
                    final_target_values['center'] = center_name
                    final_target_values['month'] = month_name
                    final_target_values['_target_'+packet+'_name'] = packet
                    final_target_values['_target_'+packet+'_single_target'] = pac_sin_tar
                    final_target_values['_target_'+packet+'_target'] = pac_tar_vals
                    final_target_values['_target_'+packet+'_actual'] = pac_act_vals
                    final_target_values['_target_'+packet+'_no_of_days'] = pac_days
                    final_target_values['_target_'+packet+'_no_of_agents'] = billable_count['billable_agents__sum']
                    final_target_values['_target_'+packet+'_prod_percen'] = prod_fin_cal
                    final_target_values['_target_final_product_val'] = final_month_val
                    final_target_values['_target_prod_utility'] = prod_utility
                    final_target_values['_target_bill_ppl'] = bill_ppl
                    final_target_values['_target_final_actual'] = sum(final_actual_val)
                    conn = redis.Redis(host="localhost", port=6379, db=0)
                    redi_dict = {}
                    for key,value in final_target_values.iteritems():
                        vals_dict = {}
                        if key == '_target_'+packet+'_name':
                            redis_key = prj_name+'_'+center_name+'_'+month_name+'_target_'+packet+'_name'
                            vals_dict['_target_'+packet+'_name'] = str(packet)      
                            redi_dict[redis_key] = vals_dict
                        if key == '_target_'+packet+'_single_target':
                            redis_key = prj_name+'_'+center_name+'_'+month_name+'_target_'+packet+'_single_target'
                            vals_dict['_target_'+packet+'_single_target'] = str(pac_sin_tar)
                            redi_dict[redis_key] = vals_dict
                        if key == '_target_'+packet+'_target':   
                            redis_key = prj_name+'_'+center_name+'_'+month_name+'_target_'+packet+'_target'
                            vals_dict['_target_'+packet+'_target'] = str(pac_tar_vals)
                            redi_dict[redis_key] = vals_dict
                        if key == '_target_'+packet+'_actual':
                            redis_key = prj_name+'_'+center_name+'_'+month_name+'_target_'+packet+'_actual'
                            vals_dict['_target_'+packet+'_actual'] = str(pac_act_vals)
                            redi_dict[redis_key] = vals_dict
                        if key == '_target_final_actual':
                            redis_key = prj_name+'_'+center_name+'_'+month_name+'_target_final_actual'
                            vals_dict['_target_final_actual'] = str(sum(final_actual_val))
                            redi_dict[redis_key] = vals_dict
                        if key == '_target_prod_utility':
                            redis_key = prj_name+'_'+center_name+'_'+month_name+'_target_prod_utility'
                            vals_dict['_target_prod_utility'] = str(prod_utility)
                            redi_dict[redis_key] = vals_dict
                        if key == '_target_bill_ppl':
                            redis_key = prj_name+'_'+center_name+'_'+month_name+'_target_bill_ppl'
                            vals_dict['_target_bill_ppl'] = str(bill_ppl)
                            redi_dict[redis_key] = vals_dict
                        if key == '_target_final_product_val':
                            redis_key = prj_name+'_'+center_name+'_'+month_name+'_target_final_product_val'
                            vals_dict['_target_final_product_val'] = str(final_month_val)
                            redi_dict[redis_key] = vals_dict
                        if key == '_target_'+packet+'_no_of_agents':
                            redis_key = prj_name+'_'+center_name+'_'+month_name+'_target_'+packet+'_no_of_agents'
                            vals_dict['_target_'+packet+'_no_of_agents'] = str(billable_count['billable_agents__sum'])
                            redi_dict[redis_key] = vals_dict
                        if key == '_target_'+packet+'_no_of_days':
                            redis_key = prj_name+'_'+center_name+'_'+month_name+'_target_'+packet+'_no_of_days'
                            vals_dict['_target_'+packet+'_no_of_days'] = str(pac_days)
                            redi_dict[redis_key] = vals_dict
                        if key == '_target_'+packet+'_prod_percen':
                            redis_key = prj_name+'_'+center_name+'_'+month_name+'_target_'+packet+'_prod_percen'
                            vals_dict['_target_'+packet+'_prod_percen'] = str(prod_fin_cal)
                            redi_dict[redis_key] = vals_dict
                    current_keys = []
                    for key, value in redi_dict.iteritems():
                        current_keys.append(key)
                        conn.hmset(key, value)
                        print key, value
            
                                
