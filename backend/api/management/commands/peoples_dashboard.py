
from django.core.management.base import BaseCommand, CommandError
from backend.settings import DATABASES
import MySQLdb
import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import redis

class Command(BaseCommand):
    help = 'Calculation of absentism and attrition for peoples dashboard'


    def handle(self, *args, **options):
        conn = MySQLdb.connect(db="nextpulse", user='root', passwd='hdrn59!', charset="utf8")
        cur = conn.cursor()
        #========================================================
        # LOGIC HERE
        #========================================================
        current_date = datetime.date.today()
        last_mon_date = current_date - relativedelta(months=3)
        from_date = datetime.datetime(last_mon_date.year, last_mon_date.month, 1).date()
        start_date = datetime.datetime(current_date.year, current_date.month, 1)
        to_date = start_date.date() - relativedelta(days=1)
        days = (to_date - from_date).days
        days = days + 1
        months_dict = {}
        month_count = 0
        for i in range(0, days):
            date = from_date + datetime.timedelta(i)
            month = date.strftime("%B")
            if month in months_dict:
                months_dict[month].append(str(date))
            else:
                months_dict[month] = [str(date)]
        projects = []
        teams = 'select distinct(team) from hrm_employee_process;'
        cur.execute(teams)
        prj_teams = cur.fetchall()
        prj_teams = list(prj_teams)
        for team in prj_teams:
            team = team[0]
            pr_team = team.split(" - ")[0]
            projects.append(pr_team)
        project = set(projects)
        not_req = ["indix", "Mahendra", "Bench", "HR", "Jeeves", "MIS", "E4U", "3i", "Admin", "Master Mind", "IT", "CureCrew", "QualityTeam", "WIPRO", "Worxogo", "StoreKing" ,"Training", "Pixm", "Accounts", "BCT", "Snap Diligence", "Compliance", "Kredx", "ER", "Indix", "Bridgei2i", "Tech","WIPRO" ,"MindTree"]
        project = filter(lambda x: x not in not_req, list(project))
        for month_name,month_dates in months_dict.iteritems():
            #final_data = {}
            absen_da, attri_da, attri_prj, absen_prj = [], [], [], []
            for prj in project:
                final_data = {}
                date_values = month_dates
                query = 'select distinct(empid) from hrm_employee_process where team like "%%%s%%" and start_date < "%s" and (end_date like "0000-00-00" or (end_date between "%s" and "%s"));' %(prj, date_values[-1], date_values[0], date_values[-1])
                cur.execute(query)
                rows = cur.fetchall()
                na_count = 0
                fin_na_list = []
                temp_rows = ""
                for emp_id in rows:
                    emp_id = emp_id[0]
                    month =  date_values[0].split("-")[1] +"-" + date_values[0].split("-")[0]
                    query1 = 'select * from hrm_attendance where empid = "%s" and month like "%%%s%%"' %(emp_id, month);
                    cur.execute(query1)
                    row_val = cur.fetchall()
                    if row_val:
                        for wrk_day in row_val[0]:
                            if wrk_day in [ "CL", "PL", "FL", "AL", "HD", "3HD", "UL", "ML" ]:
                                na_count = na_count + 1
                        temp_rows += '", "' + emp_id
                    else:
                        na_count = 0
                temp_rows += '"'
                fin_na_list.append(na_count)
                if len(rows):
                    absent = (float(sum(fin_na_list))/float((len(rows)) * 21))*100
                    absent_value = float('%.2f' % round(absent, 2))
                else:
                    absent_value = 0
                attri_value = 0
                if len(temp_rows) > 2:
                    query2 = 'select count(empid) from hrm_employee_resignation where empid in (%s) and (lastday between "%s" and "%s");' %(temp_rows[2:], date_values[0], date_values[-1])
                    cur.execute(query2)
                    values = cur.fetchall()
                    if rows:
                        attri = float(sum(values[0]))/float(len(rows))*100
                        attri_value = float('%.2f' % round(attri, 2))
                if prj == "Walmart":
                    prj = "Walmart Salem"
                elif prj == "gooru":
                    prj = "Gooru"
                elif prj == "Dell-TP":
                    prj = "NTT DATA Services TP"
                elif prj == "Dell-Coding":
                    prj = "NTT DATA Services Coding"
                else:
                    prj = prj
                center_name = "Salem"
                final_data['project'] = prj;
                final_data['center'] = center_name;
                final_data['month'] = month_name;
                final_data['absenteeism'] = absent_value;
                final_data['attrition'] = attri_value;
                if absent_value:
                    absen_da.append(absent_value)
                    absen_prj.append(prj)
                    absen_sum = sum(absen_da)/len(absen_prj)
                else:
                    absen_sum = 0
                if attri_value:
                    attri_da.append(attri_value)
                    attri_prj.append(prj)
                    attri_sum = sum(attri_da)/len(attri_prj)
                else:
                    attri_sum = 0
                final_data['center_absenteeism'] = absen_sum
                final_data['center_attrition'] = attri_sum
                data_dict = {}
                for key,value in final_data.iteritems():
                    value_dict = {}
                    if key == 'absenteeism':
                        redis_key = '{0}_{1}_{2}_absenteeism'.format(prj,center_name,month_name)
                        value_dict['absenteeism'] = str(absent_value)
                        data_dict[redis_key] = value_dict
                    if key == 'attrition':
                        redis_key = '{0}_{1}_{2}_attrition'.format(prj,center_name,month_name)
                        value_dict['attrition'] = str(attri_value)
                        data_dict[redis_key] = value_dict
                    if key == 'center_absenteeism':
                        redis_key = '{0}_{1}_center_absenteeism'.format(center_name,month_name)
                        value_dict['center_absenteeism'] = str(absen_sum)
                        data_dict[redis_key] = value_dict
                    if key == 'center_attrition':
                        redis_key = '{0}_{1}_center_attrition'.format(center_name,month_name)
                        value_dict['center_attrition'] = str(attri_sum)
                        data_dict[redis_key] = value_dict
                conn1 = redis.Redis(host="localhost", port=6379, db=0)
                current_keys = []
                for key, value in data_dict.iteritems():
                    current_keys.append(key)
                    conn1.hmset(key, value)
                    print key, value
                print prj
                print center_name
        cur.close()
        conn.close()
