# Import Section ---------

from dateutil.relativedelta import *
import redis
import collections
import datetime
#conn = redis.Redis(host="localhost", port=6379, db=0)




# Global variable
PROJECTS = ["Probe-Salem", "NTT DATA Services TP-Salem", "NTT DATA Services Coding-Salem", "IBM-Salem", "Federal Bank-Salem",\
            "Gooru-Salem", "Walmart Salem-Salem", "Ujjivan-Salem"]

MONTHS = ["April", "May"]

SLA = ['productivity', "external_accuracy", "internal_accuracy", 'production', 'tat']

PEOPLES = ["fte_utilisation", "operational_utilization", "absenteeism", "attrition"]
#PEOPLES = ["absentisim"]



# Logics -----------------------------

def get_dash_data(projects=PROJECTS, tab=SLA):
    """ get SLA related data """

    if not projects:
        projects=PROJECTS
    conn = redis.Redis(host="localhost", port=6379, db=0)
    result = []
    month_name = []
    for t in xrange(1, 4):
        one_month_ago = datetime.datetime.now() - relativedelta(months=t)
        month_name.append(one_month_ago.strftime("%B"))
       
    for project in projects:
        _project, center = project.split("-")
        row_data = {'project': _project, 'center': center}
        i = 1
        for month in month_name:
            m_key = "Month"+ str(i)
            row_data.update({m_key : month})
            #_project, center = project.split("-")
            #row_data = {'project': _project, 'center': center, 'month': month}
            for pro in tab:
                key = project.replace("-", "_") + "_" + month+ "_" + pro
                _key = pro + "_" + m_key
                row_data.update({_key : conn.hgetall(key).get(pro)})
            i +=1
        result.append(row_data)
    return result





