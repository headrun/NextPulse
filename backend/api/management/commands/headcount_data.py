
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    commands = ['generatedata',]
    args = '[command]'
    help = 'generate data'

    def handle(self, *args, **options):

        from api.models import Project,Center,RawTable,Headcount
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
        proje_cent = ['Probe','Gooru','Ujjivan','Federal Bank']
        for pro_cen in proje_cent:
            values = Project.objects.filter(name=pro_cen).values_list('id','center_id')
            prj_id = values[0][0]
            center_id = values[0][1]
            prj_name = pro_cen
            center_name = Center.objects.filter(project=prj_id).values_list('name',flat=True)[0]
            #project_salem_count, project_chittoor_count = [] , []
            #billa_sal, buf_sal, others_sal, total_sal = [], [], [], []
            #billa_chi, buf_chi, others_chi, total_chi = [], [], [], []
            for month_name,month_dates in months_dict.iteritems():
                final_dict = {}
                dates_list = month_dates
                date_li = []
                project_salem_count, project_chittoor_count = [] , []
                billa_sal, buf_sal, others_sal, total_sal = [], [], [], []
                billa_chi, buf_chi, others_chi, total_chi = [], [], [], []
                import pdb;pdb.set_trace()
                for date in dates_list:
                    per_day_val = RawTable.objects.filter(project=prj_id, center=center_id, date=date).aggregate(Max('per_day'))
                    if per_day_val['per_day__max'] > 0:
                        date_li.append(date)
                head_count = Headcount.objects.filter(project = prj_id, center = center_id, date = date_li[-1]).aggregate(Sum('billable_hc'),Sum('billable_agents'),Sum('buffer_agents'),Sum('qc_or_qa'),Sum('teamlead'),Sum('trainees_and_trainers'),Sum('managers'),Sum('mis'))
                if head_count['billable_hc__sum'] != None:
                    billable_head = head_count['billable_hc__sum']
                    billable_head = float('%.2f' % round(billable_head, 2))
                    billable_agents = head_count['billable_agents__sum']
                    billable_agents = float('%.2f' % round(billable_agents, 2))
                    buffer_agents = head_count['buffer_agents__sum']
                    buffer_agents = float('%.2f' % round(buffer_agents, 2))
                    other_support = head_count['qc_or_qa__sum'] + head_count['managers__sum'] + head_count['teamlead__sum'] + head_count['mis__sum'] + head_count['trainees_and_trainers__sum']
                    other_support = float('%.2f' % round(other_support, 2)) 
                    total = billable_head + buffer_agents + other_support
                else:
                    billable_head = 0
                    billable_agents = 0
                    buffer_agents = 0
                    other_support = 0
                    total = 0
                conn = redis.Redis(host="localhost", port=6379, db=0)
                final_dict['project'] = prj_name
                final_dict['center'] = center_name
                final_dict['billable'] = billable_head
                final_dict['buffer'] = buffer_agents
                final_dict['other_support'] = other_support
                final_dict['total'] = total
                #project_salem_count, project_chittoor_count = [] , []
                #billa_sal, buf_sal, others_sal, total_sal = [], [], [], []
                #billa_chi, buf_chi, others_chi, total_chi = [], [], [], []
                if center_name == 'Salem':    
                    project_salem_count.append(prj_name)
                    prj_len = len(project_salem_count)
                    billa_sal.append(billable_head)
                    buf_sal.append(buffer_agents)
                    others_sal.append(other_support)
                    total_sal.append(total)
                    billa_sum = sum(billa_sal)
                    buffer_sum = sum(buf_sal)
                    others_sum = sum(others_sal)
                    total_sum = sum(total_sal)
                else:
                    project_chittoor_count.append(prj_name)
                    prj_len = len(project_chittoor_count)
                    billa_chi.append(billable_head)
                    buf_chi.append(buffer_agents)
                    others_chi.append(other_support)
                    total_chi.append(total)
                    billa_sum = sum(billa_chi)
                    buffer_sum = sum(buf_chi)
                    others_sum = sum(others_chi)
                    total_sum = sum(total_chi)
                print prj_len , billa_sum , buffer_sum , others_sum , total_sum
                final_dict['center_billable'] = billa_sum
                final_dict['center_buffer'] = buffer_sum
                final_dict['center_others'] = others_sum
                final_dict['center_total'] = total_sum
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
                    if key == 'other_support':
                        redis_key = '{0}_{1}_{2}_other_support'.format(prj_name,center_name,month_name)
                        value_dict['other_support'] = str(other_support)
                        head_count_dict[redis_key] = value_dict
                    if key == 'total':
                        redis_key = '{0}_{1}_{2}_total'.format(prj_name,center_name,month_name)
                        value_dict['total'] = str(total)
                        head_count_dict[redis_key] = value_dict
                    if key == 'center_billable':
                        redis_key = '{0}_{1}_{2}_center_billable'.format(prj_name,center_name,month_name)
                        value_dict['center_billable'] = str(billa_sum)
                        head_count_dict[redis_key] = value_dict
                    if key == 'center_buffer':
                        redis_key = '{0}_{1}_{2}_center_buffer'.format(prj_name,center_name,month_name)
                        value_dict['center_buffer'] = str(buffer_sum)
                        head_count_dict[redis_key] = value_dict
                    if key == 'center_others':
                        redis_key = '{0}_{1}_{2}_center_others'.format(prj_name,center_name,month_name)
                        value_dict['center_others'] = str(others_sum)
                        head_count_dict[redis_key] = value_dict
                    if key == 'center_total':
                        redis_key = '{0}_{1}_{2}_center_total'.format(prj_name,center_name,month_name)
                        value_dict['center_total'] = str(total_sum)
                        head_count_dict[redis_key] = value_dict
                current_keys = []
                for key, value in head_count_dict.iteritems():
                    current_keys.append(key)
                    conn.hmset(key, value)
                    print key, value    
