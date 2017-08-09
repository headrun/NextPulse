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
        _id = Project.objects.get(name = _project, center__name = center).id
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

                _target_objs = ColorCoding.objects.filter(project__id =_id, widget__config_name = WIDGET_SYNC[pro])
                if not _target_objs:
                    if pro in ["absenteeism", "attrition"]:
                        _target = 5.0
                    else:
                        _target = 99.0
                else:
                    _target = _target_objs[0].soft_target
                
                row_data['color'].update({_key : ['Green', _target]})
                if not row_data[_key] == "NA":
                    row_data['color'].update({_key : [get_color(float(row_data[_key]), _target), _target]}) 

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

