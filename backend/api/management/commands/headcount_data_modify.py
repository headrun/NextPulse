
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    commands = ['generatedata',]
    args = '[command]'
    help = 'generate data'

    def handle(self, *args, **options):

        from api.models import Project,Center,RawTable,Headcount,Targets
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
        proje_cent = ['Probe','NTT DATA Services TP','NTT DATA Services Coding','Federal Bank','Ujjivan','Gooru','Walmart Salem','IBM','IBM South East Asia','IBM Pakistan','IBM Africa','IBM DCIW Arabia','IBM Quality Control','IBM India and Sri Lanka','IBM NA and EU','IBM Arabia','IBM DCIW','IBM Latin America','IBM Sri Lanka P2P', 'Mobius', 'Walmart Chittor']
        #proje_cent = ['Mobius', 'Walmart Chittor']
        for month_name,month_dates in months_dict.iteritems():
            project_salem_count, project_chittoor_count = [] , []
            billa_sal, buf_sal, qc_qa_sal, tl_sal, others_sal, total_sal = [], [], [], [], [], []
            billa_chi, buf_chi, qc_qa_chi, tl_chi, others_chi, total_chi = [], [], [], [], [], []
            volume_sl_data, volume_chi_data, targets_sl_data, targets_chi_data = [], [], [], []
            dates_list = month_dates
            for pro_cen in proje_cent:
                final_dict = {}
                date_li = []
                values = Project.objects.filter(name=pro_cen).values_list('id','center_id')
                prj_id = values[0][0]
                center_id = values[0][1]
                prj_name = pro_cen
                center_name = Center.objects.filter(project=prj_id).values_list('name',flat=True)[0]
                for date in dates_list:
                    per_day_val = Headcount.objects.filter(project=prj_id, center=center_id, date=date).aggregate(Max('billable_hc'))
                    if per_day_val['billable_hc__max'] > 0:
                        date_li.append(date)
                if date_li:
                    head_count = Headcount.objects.filter(project = prj_id, center = center_id, date = date_li[-1]).aggregate(Sum('billable_hc'),Sum('billable_agents'),Sum('buffer_agents'),Sum('qc_or_qa'),Sum('teamlead'),Sum('trainees_and_trainers'),Sum('managers'),Sum('mis'))
                else:
                    break
                volumes = RawTable.objects.filter(project=prj_id, center=center_id, date__range=[dates_list[0],dates_list[-1]]).aggregate(Sum('per_day'))
                volumes = volumes['per_day__sum']
                if head_count['billable_hc__sum'] != None:
                    billable_head = head_count['billable_hc__sum']
                    billable_head = float('%.2f' % round(billable_head, 2))
                    billable_agents = head_count['billable_agents__sum']
                    billable_agents = float('%.2f' % round(billable_agents, 2))
                    buffer_agents = head_count['buffer_agents__sum']
                    buffer_agents = float('%.2f' % round(buffer_agents, 2))
                    qc_qa = head_count['qc_or_qa__sum']
                    qc_qa = float('%.2f' % round(qc_qa, 2))
                    tl = head_count['teamlead__sum']
                    tl = float('%.2f' % round(tl, 2))
                    other_support = head_count['managers__sum'] + head_count['mis__sum'] + head_count['trainees_and_trainers__sum']
                    other_support = float('%.2f' % round(other_support, 2)) 
                    total = billable_head + buffer_agents + other_support + qc_qa + tl
                else:
                    billable_head = 0
                    billable_agents = 0
                    buffer_agents = 0
                    qc_qa = 0
                    tl = 0
                    other_support = 0
                    total = 0
                conn = redis.Redis(host="localhost", port=6379, db=0)
                final_dict['project'] = prj_name
                final_dict['center'] = center_name
                final_dict['billable'] = billable_head
                final_dict['buffer'] = buffer_agents
                final_dict['qc_or_qa'] = qc_qa
                final_dict['team_lead'] = tl
                final_dict['other_support'] = other_support
                final_dict['total'] = total
                if center_name == 'Salem' and prj_name != 'IBM':    
                    billa_sal.append(billable_head)
                    buf_sal.append(buffer_agents)
                    qc_qa_sal.append(qc_qa)
                    tl_sal.append(tl)
                    others_sal.append(other_support)
                    total_sal.append(total)
                    billa_sum = sum(billa_sal)
                    buffer_sum = sum(buf_sal)
                    others_sum = sum(others_sal)
                    total_sum = sum(total_sal)
                    qc_qa_sum = sum(qc_qa_sal)
                    tl_sum = sum(tl_sal)
                elif center_name == 'Chittoor' and prj_name != 'IBM':
                    billa_chi.append(billable_head)
                    buf_chi.append(buffer_agents)
                    qc_qa_chi.append(qc_qa)
                    tl_chi.append(tl)
                    others_chi.append(other_support)
                    total_chi.append(total)
                    billa_sum = sum(billa_chi)
                    buffer_sum = sum(buf_chi)
                    qc_qa_sum = sum(qc_qa_chi)
                    tl_sum = sum(tl_chi)
                    others_sum = sum(others_chi)
                    total_sum = sum(total_chi)
                final_dict['center_billable'] = billa_sum
                final_dict['center_buffer'] = buffer_sum
                final_dict['center_qc_or_qa'] = qc_qa_sum
                final_dict['center_team_lead'] = tl_sum
                final_dict['center_other_support'] = others_sum
                final_dict['center_total'] = total_sum
                fte_deno = billa_sum + buffer_sum + qc_qa_sum + tl_sum
                fte_util = (float(billa_sum)/ float(fte_deno))*100
                fte_utiliti = float('%.2f' % round(fte_util,2))
                opera_util = (float(billa_sum)/ float(fte_deno + others_sum))*100
                opera_utiliti = float('%.2f' % round(opera_util,2))
                final_dict['center_fte_utilisation'] = fte_utiliti
                final_dict['center_operational_utilization'] = opera_utiliti
                conn = redis.Redis(host="localhost", port=6379, db=0)
                head_count_dict = {}
                for key,value in final_dict.iteritems():
                    value_dict = {}
                    if key == 'billable':
                        redis_key = '{0}_{1}_{2}_billable'.format(prj_name,center_name,month_name)
                        value_dict['billable'] = str(billable_head)
                        head_count_dict[redis_key] = value_dict
                    if key == 'buffer':
                        redis_key = '{0}_{1}_{2}_buffer'.format(prj_name,center_name,month_name)
                        value_dict['buffer'] = str(buffer_agents)
                        head_count_dict[redis_key] = value_dict
                    if key == 'qc_or_qa':
                        redis_key = '{0}_{1}_{2}_qc_or_qa'.format(prj_name,center_name,month_name)
                        value_dict['qc_or_qa'] = str(qc_qa)
                        head_count_dict[redis_key] = value_dict
                    if key == 'team_lead':
                        redis_key = '{0}_{1}_{2}_team_lead'.format(prj_name,center_name,month_name)
                        value_dict['team_lead'] = str(tl)
                        head_count_dict[redis_key] = value_dict
                    if key == 'other_support':
                        redis_key = '{0}_{1}_{2}_other_support'.format(prj_name,center_name,month_name)
                        value_dict['other_support'] = str(other_support)
                        head_count_dict[redis_key] = value_dict
                    if key == 'total':
                        redis_key = '{0}_{1}_{2}_total'.format(prj_name,center_name,month_name)
                        value_dict['total'] = str(total)
                        head_count_dict[redis_key] = value_dict
                    if key == 'center_fte_utilisation':
                        redis_key = '{0}_{1}_center_fte_utilisation'.format(center_name,month_name)
                        value_dict['center_fte_utilisation'] = str(fte_utiliti)
                        head_count_dict[redis_key] = value_dict
                    if key == 'center_operational_utilization':
                        redis_key = '{0}_{1}_center_operational_utilization'.format(center_name,month_name)
                        value_dict['center_operational_utilization'] = str(opera_utiliti)
                        head_count_dict[redis_key] = value_dict
                    if key == 'center_billable':
                        redis_key = '{0}_{1}_center_billable'.format(center_name,month_name)
                        value_dict['center_billable'] = str(billa_sum)
                        head_count_dict[redis_key] = value_dict
                    if key == 'center_qc_or_qa':
                        redis_key = '{0}_{1}_center_qc_or_qa'.format(center_name,month_name)
                        value_dict['center_qc_or_qa'] = str(qc_qa_sum)
                        head_count_dict[redis_key] = value_dict
                    if key == 'center_team_lead':
                        redis_key = '{0}_{1}_center_team_lead'.format(center_name,month_name)
                        value_dict['center_team_lead'] = str(tl_sum)
                        head_count_dict[redis_key] = value_dict
                    if key == 'center_buffer':
                        redis_key = '{0}_{1}_center_buffer'.format(center_name,month_name)
                        value_dict['center_buffer'] = str(buffer_sum)
                        head_count_dict[redis_key] = value_dict
                    if key == 'center_other_support':
                        redis_key = '{0}_{1}_center_other_support'.format(center_name,month_name)
                        value_dict['center_other_support'] = str(others_sum)
                        head_count_dict[redis_key] = value_dict
                    if key == 'center_total':
                        redis_key = '{0}_{1}_center_total'.format(center_name,month_name)
                        value_dict['center_total'] = str(total_sum)
                        head_count_dict[redis_key] = value_dict
                current_keys = []
                for key, value in head_count_dict.iteritems():
                    current_keys.append(key)
                    conn.hmset(key, value)
                    print key, value    
