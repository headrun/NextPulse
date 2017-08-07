# Import Section ---------

from dateutil.relativedelta import *
import redis
import collections
import datetime
from api.models import Project
from peoples_dashboard.models import *
from peoples_dashboard.constants import *
#conn = redis.Redis(host="localhost", port=6379, db=0)




# Global variable
PROJECTS = ["Probe-Salem", "NTT DATA Services TP-Salem", "NTT DATA Services Coding-Salem", "IBM-Salem", "Federal Bank-Salem",\
            "Gooru-Salem", "Walmart Salem-Salem", "Ujjivan-Salem"]

MONTHS = ["April", "May"]

SLA = ['productivity', "external_accuracy", 'internal_accuracy', 'production', 'tat']

PEOPLES = ["fte_utilisation", "operational_utilization", "absenteeism", "attrition"]
#PEOPLES = ["absentisim"]



# Logics -----------------------------

def get_dash_data(projects=PROJECTS, tab=SLA):
    """ get SLA related data """
    
    if not projects:
        #projects= Project.objects.all().values_list('id', 'name', 'center__name')
        projects = PROJECTS
    #import pdb;pdb.set_trace()
    conn = redis.Redis(host="localhost", port=6379, db=0)
    result = []
    month_name = []
    for t in xrange(1, 4):
        one_month_ago = datetime.datetime.now() - relativedelta(months=t)
        month_name.append(one_month_ago.strftime("%B"))
       
    for project in projects:
        #_id, _project, center = project
        _project, center = project.split("-")
        row_data = {'project': _project, 'center': center, 'color': {}}
        i = 1
        for month in month_name:
            m_key = "Month"+ str(i)
            row_data.update({m_key : month})
            #_project, center = project.split("-")
            #row_data = {'project': _project, 'center': center, 'month': month}
            for pro in tab:
                key = _project +"_"+ center + "_" + month+ "_" + pro
                _key = pro + "_" + m_key
                row_data.update({_key : conn.hgetall(key).get(pro, 0)})
                #row_data.update({_key : 0})
                #_target = ColorCoding.objects.get(project__id =_id, widget__id = WIDGET_SYNC[pro]).soft_target
                _target = 99
                row_data['color'].update({_key : get_color(row_data[_key], _target)}) 
            i +=1
        result.append(row_data)
    return result

def get_color(val, target):
    """ getting the color """
    if val < target:
        color = "Red"
    elif val == target:
        color = "Orange"
    else:
        color = "Green"
    return color

