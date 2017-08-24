
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    commands = ['generatedata',]
    args = '[command]'
    help = 'generate data'

    def handle(self, *args, **options):

        from api.models import Project,Center,Headcount
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
        proje_cent = Project.objects.values_list('name',flat=True)
        not_req = ["3i VAPP", "Bridgei2i", "E4U", "indix", "Nextgen", "IBM Sri Lanka P2P", "Quarto","Tally", "Sulekha", "Webtrade", "Walmart Chittor", "Future Energie Tech"]
        proje_cent = filter(lambda x: x not in not_req, list(proje_cent))
        for pro_cen in proje_cent:
            values = Project.objects.filter(name=pro_cen).values_list('id','center_id')
            prj_id = values[0][0]
            center_id = values[0][1]
            prj_name = pro_cen
            center_name = Center.objects.filter(project=prj_id).values_list('name',flat=True)[0] 
            for month_name,month_dates in months_dict.iteritems():
                final_dict = {}
                dates_list = month_dates
                head_count = Headcount.objects.filter(project = prj_id, center = center_id, date = dates_list[-1]).aggregate(Sum('billable_hc'),Sum('billable_agents'),Sum('buffer_agents'),Sum('qc_or_qa'),Sum('teamlead'),Sum('trainees_and_trainers'),Sum('managers'),Sum('mis'))
                if head_count['billable_hc__sum'] != None:
                    billable_head = head_count['billable_hc__sum']
                    billable_head = float('%.2f' % round(billable_head, 2))
                    billable_agents = head_count['billable_agents__sum']
                    billable_agents = float('%.2f' % round(billable_agents, 2))
                    buffer_agents = head_count['buffer_agents__sum']
                    buffer_agents = float('%.2f' % round(buffer_agents, 2))
                    other_support = head_count['qc_or_qa__sum'] + head_count['managers__sum'] + head_count['teamlead__sum'] + head_count['mis__sum'] + head_count['trainees_and_trainers__sum']
                    other_support = float('%.2f' % round(other_support, 2)) 
                    total = billable_head + billable_agents + buffer_agents + other_support
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
                current_keys = []
                for key, value in head_count_dict.iteritems():
                    current_keys.append(key)
                    conn.hmset(key, value)
                    print key, value    
