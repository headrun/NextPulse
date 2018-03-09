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
        final_project_data = []
        proje_cent = ['Probe','NTT DATA Services TP','NTT DATA Services Coding','Federal Bank','Ujjivan','Gooru','Walmart Salem',\
                      'Walmart Chittor','Mobius','IBM','IBM South East Asia','IBM Pakistan','IBM Africa','IBM DCIW Arabia',\
                      'IBM Quality Control','IBM India and Sri Lanka','IBM NA and EU','IBM Arabia','IBM DCIW','IBM Latin America',\
                      'IBM Sri Lanka P2P']

        for month_name,month_dates in months_dict.iteritems():
            tat_met_sal, tat_not_met_sal = [], []
            tat_met_chi, tat_not_met_chi = [], []
            dates_list = month_dates
            for pro_cen in proje_cent:
                values = Project.objects.filter(name=pro_cen).values_list('id','center_id')
                prj_id = values[0][0]
                center_id = values[0][1]
                prj_name = pro_cen   
                final_productivity_list = []
                conn = redis.Redis(host="localhost", port=6379, db=0)
                center_name = Center.objects.filter(project=prj_id).values_list('name',flat=True)[0]
                volumes = RawTable.objects.filter(project=prj_id,center=center_id,date__range=[dates_list[0],dates_list[-1]])
                volume_list = volumes.values('sub_project').distinct()
                volumes_data = volumes.values('sub_project','work_packet').distinct()
                if volume_list:
                    if volume_list[0]['sub_project']:
                        volume_list = volume_list
                    else:
                        volume_list = volumes.values_list('work_packet',flat=True).distinct()
                else:
                    volume_list = []
                final_productivity_dict = {}
                new_date_list, tat_values = [] , []
                tat_data = {}
                fte_data, prod_utili = [], []
                operational_data, targ_list = [], []
                for date_va in dates_list:
                    total_done_value = RawTable.objects.filter(project=prj_id, center=center_id, date=date_va)\
                                        .aggregate(Max('per_day'))
                    if total_done_value['per_day__max']>0:
                        new_date_list.append(date_va)
                        for vol_type in volume_list:    
                            final_work_packet = vol_type                            
                            if volumes_data[0]['work_packet'] != '' and volumes_data[0]['sub_project'] != '':
                                final_work_packet = final_work_packet['sub_project']
                            else:
                                final_work_packet = final_work_packet

                           #generation of fte and operational headcount data
                        headcount_details = Headcount.objects.filter(\
                                            project=prj_id, center=center_id, date=date_va)\
                                            .aggregate(Sum('billable_hc'),Sum('buffer_agents'),Sum('qc_or_qa'),\
                                            Sum('teamlead'),Sum('trainees_and_trainers'))
                        if headcount_details['billable_hc__sum'] != None:
                            utilization_numerator = headcount_details['billable_hc__sum']
                            fte_utilization = headcount_details['billable_hc__sum'] + headcount_details['buffer_agents__sum']\
                                              + headcount_details['qc_or_qa__sum'] + headcount_details['teamlead__sum']
                            fte_value = (float(utilization_numerator)/float(fte_utilization))*100
                            fte_utili_value = float('%.2f' % round(fte_value,2))
                            operational_utilization = fte_utilization + headcount_details['trainees_and_trainers__sum']
                            operational_value = (float(utilization_numerator)/float(operational_utilization))*100
                            operational_utili_value = float('%.2f' % round(operational_value,2))
                            fte_data.append(fte_utili_value)
                            operational_data.append(operational_utili_value)
                        else:
                            fte_data.append(0)
                            operational_data.append(0)

                #calculation for productivity value
                tat = TatTable.objects.filter(project=prj_id, center=center_id, date__range = [dates_list[0],dates_list[-1]])
                met_cnt = tat.aggregate(Sum('met_count'))
                not_met_cnt = tat.aggregate(Sum('non_met_count'))
                if met_cnt['met_count__sum'] == None:
                    met_cnt = 0
                else:
                    met_cnt = met_cnt['met_count__sum']
                if not_met_cnt['non_met_count__sum'] == None:
                    not_met_cnt = 0
                else:
                    not_met_cnt = not_met_cnt['non_met_count__sum']

                if met_cnt:
                    tat_value = (float(met_cnt)/float(met_cnt+not_met_cnt))*100
                    tat_final_value = float('%.2f' % round(tat_value,2))
                else:
                    tat_final_value = 'NA' 
                if len(new_date_list):
                    fte_utiliti_value = sum(fte_data)/len(new_date_list)
                    operational_utiliti_value = sum(operational_data)/len(new_date_list)
                    final_fte = float('%.2f' % round(fte_utiliti_value,2))
                    final_operational = float('%.2f' % round(operational_utiliti_value,2))
                else:
                    final_fte = 0
                    final_operational = 0
                    final_prod_util = 0
                if center_name == 'Salem':
                    attrition = 0
                    absent = 0
                    final_productivity_dict['project'] = prj_name
                    final_productivity_dict['center'] = center_name
                    final_productivity_dict['month'] = month_name
                    final_productivity_dict['fte_utilisation'] = final_fte
                    final_productivity_dict['operational_utilization'] = final_operational
                    final_productivity_dict['tat'] = tat_final_value
                    final_productivity_dict['absenteeism'] = absent
                    final_productivity_dict['attrition'] = attrition
                    final_productivity_dict['center_absenteeism'] = absent
                    final_productivity_dict['center_attrition'] = attrition
                    final_productivity_dict[month_name+'_'+'start_date'] = dates_list[0]
                    final_productivity_dict[month_name+'_'+'end_date'] = dates_list[-1]
                    final_productivity_list.append(final_productivity_dict)
                else:
                    attrition = 'NA'
                    absent = 'NA'
                    final_productivity_dict['project'] = prj_name
                    final_productivity_dict['center'] = center_name
                    final_productivity_dict['month'] = month_name
                    final_productivity_dict['fte_utilisation'] = final_fte
                    final_productivity_dict['operational_utilization'] = final_operational
                    final_productivity_dict['tat'] = tat_final_value
                    final_productivity_dict['absenteeism'] = absent
                    final_productivity_dict['attrition'] = attrition
                    final_productivity_dict['center_absenteeism'] = absent
                    final_productivity_dict['center_attrition'] = attrition
                    final_productivity_dict[month_name+'_'+'start_date'] = dates_list[0]
                    final_productivity_dict[month_name+'_'+'end_date'] = dates_list[-1]
                if center_name == 'Salem' and prj_name != 'IBM':
                    #tat center data
                    tat_met_sal.append(met_cnt)
                    tat_not_met_sal.append(not_met_cnt)
                    if sum(tat_met_sal):
                        tat_sum = (float(sum(tat_met_sal))/float(sum(tat_met_sal)+sum(tat_not_met_sal)))*100
                    else:
                        tat_sum = 'NA'
                elif center_name == 'Chittoor' and prj_name != 'IBM':
                    #tat center data
                    tat_met_chi.append(met_cnt)
                    tat_not_met_chi.append(not_met_cnt)
                    if sum(tat_met_chi):
                        tat_sum = (float(sum(tat_met_chi))/float(sum(tat_met_chi)+sum(tat_not_met_chi)))*100
                    else:
                        tat_sum = 'NA'
                    
                final_productivity_dict['center_tat'] = tat_sum
                data_dict = {}
                for key,value in final_productivity_dict.iteritems():
                    value_dict = {}
                    if key == 'tat':
                        redis_key = '{0}_{1}_{2}_tat'.format(prj_name,center_name,month_name)
                        value_dict['tat'] = str(tat_final_value)
                        data_dict[redis_key] = value_dict
                    if key == month_name+'_'+'start_date':
                        redis_key = prj_name+'_'+center_name+'_'+month_name+'_'+month_name+'_'+'start_date'
                        value_dict[month_name+'_'+'start_date'] = str(dates_list[0])
                        data_dict[redis_key] = value_dict
                    if key == month_name+'_'+'end_date':
                        redis_key = prj_name+'_'+center_name+'_'+month_name+'_'+month_name+'_'+'end_date'
                        value_dict[month_name+'_'+'end_date'] = str(dates_list[-1])
                        data_dict[redis_key] = value_dict
                    if key == 'fte_utilisation':
                        redis_key = '{0}_{1}_{2}_fte_utilisation'.format(prj_name,center_name,month_name)
                        value_dict['fte_utilisation'] = str(final_fte)
                        data_dict[redis_key] = value_dict
                    if key == 'operational_utilization':
                        redis_key = '{0}_{1}_{2}_operational_utilization'.format(prj_name,center_name,month_name)
                        value_dict['operational_utilization'] = str(final_operational)
                        data_dict[redis_key] = value_dict
                    if key == 'center_tat':
                        redis_key = '{0}_{1}_center_tat'.format(center_name,month_name)
                        value_dict['center_tat'] = str(tat_sum)
                        data_dict[redis_key] = value_dict
                    if key == 'absenteeism':
                        redis_key = '{0}_{1}_{2}_absenteeism'.format(prj_name,center_name,month_name)
                        value_dict['absenteeism'] = str(absent)
                        data_dict[redis_key] = value_dict
                    if key == 'center_absenteeism':
                        redis_key = '{0}_{1}_center_absenteeism'.format(center_name,month_name)
                        value_dict['center_absenteeism'] = str(absent)
                        data_dict[redis_key] = value_dict
                    if key == 'center_attrition':
                        redis_key = '{0}_{1}_center_attrition'.format(center_name,month_name)
                        value_dict['center_attrition'] = str(attrition)
                        data_dict[redis_key] = value_dict
                    if key == 'attrition':
                        redis_key = '{0}_{1}_{2}_attrition'.format(prj_name,center_name,month_name)
                        value_dict['attrition'] = str(attrition)
                        data_dict[redis_key] = value_dict
                conn = redis.Redis(host="localhost", port=6379, db=0) 
                current_keys = []
                for key, value in data_dict.iteritems():
                    current_keys.append(key)
                    conn.hmset(key, value) 
                    print key, value 
            final_project_data.append(final_productivity_list)
