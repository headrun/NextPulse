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
PROJECTS = ["Probe-Salem", "NTT DATA Services TP-Salem", "NTT DATA Services Coding-Salem", "Federal Bank-Salem","Gooru-Salem",\
            "Walmart Salem-Salem", "Ujjivan-Salem", "IBM-Salem", "IBM Africa-Salem", "IBM Arabia-Salem", "IBM DCIW-Salem",\
            "IBM DCIW Arabia-Salem", "IBM India and Sri Lanka-Salem", "IBM Latin America-Salem", "IBM NA and EU-Salem",\
            "IBM Pakistan-Salem", "IBM Quality Control-Salem", "IBM South East Asia-Salem", "Mobius-Chittoor"]

MONTHS = ["April", "May"]

SLA = ['productivity', "external_accuracy", 'internal_accuracy', 'prod_utili', 'tat']

PEOPLES = ["buffer","billable", "other_support","total","fte_utilisation", "operational_utilization", "absenteeism", "attrition"]
#PEOPLES = ["absentisim"]             TARGETS



# Logics -----------------------------

def get_dash_data(projects=PROJECTS, tab=SLA):
    """ get SLA related data """    
    if not projects:
        #projects= Project.objects.all().values_list('id', 'name', 'center__name')
        projects = PROJECTS
    
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
                core_key = _project +"_"+ center + "_" + month
                _key = core_key + "_" + pro
                _key = pro + "_" + m_key
                row_data.update({_key : conn.hgetall(_key).get(pro, 0)})
                #row_data.update({_key : 0})

                _target_objs = ColorCoding.objects.filter(project__id =_id, widget__config_name = WIDGET_SYNC.get(pro, ""), month = month)
                if not _target_objs:
                    _target = DEFAULT_TARGET.get(pro, 0)
                else:
                    _target = _target_objs[0].soft_target
                
                row_data['color'].update({_key : ['Green', _target]})
                if not row_data[_key] == "NA":
                    row_data['color'].update({_key : [get_color(float(row_data[_key]), _target, pro), _target, core_key]})

            i +=1
        result.append(row_data)
    return result


def get_target(core_key):
    
    conn = redis.Redis(host="localhost", port=6379, db=0)
    _key = core_key + '_' + "target" + '_' + '*'
    target_list = conn.keys(_key)
    target_dict = {}
    for item in target_list:
        target_dict.update({ item: conn.hgetall(item).values()[0]})
    return target_dict

def get_color(val, target, pro):
    """ getting the color """
    if pro in REVERSE_TARGET:
        if val > target:
            color = "Red"
        elif val == target:
            color = "Orange"
        else:
            color = "Green"
    else:     
        if val < target:
            color = "Red"
        elif val == target:
            color = "Orange"
        else:
            color = "Green"
    return color

