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

SLA = ['productivity', 'prod_utili', "external_accuracy", 'internal_accuracy', 'tat']

PEOPLES = ["buffer","billable", "qc_or_qa", "team_lead", "other_support","total","fte_utilisation", "operational_utilization", "absenteeism", "attrition"]
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
                #import pdb;pdb.set_trace()
                core_key = _project +"_"+ center + "_" + month
                _key = core_key + "_" + pro
                _key1 = pro + "_" + m_key
                row_data.update({_key1 : conn.hgetall(_key).get(pro, 0)})
                #row_data.update({_key : 0})

                
                if pro == 'productivity':
                    _key3 = core_key + '_target_*_target'
                    target_lists = conn.keys(_key3)
                    _target_list = []
                    t = 0
                    #import pdb;pdb.set_trace()
                    for item in target_lists:
                        if 'single' not in item:
                            continue
                        try:
                            _target_list.append(float(conn.hgetall(item).values()[0]))
                            t += 1
                        except:
                            pass
                    if t > 0:
                        DEFAULT_TARGET['prod_utili'] = "%.2f" % (sum(_target_list)/ t)

                _target_objs = ColorCoding.objects.filter(project__id =_id, widget__config_name = WIDGET_SYNC.get(pro, ""), month = month)
                if not _target_objs:
                    _target = DEFAULT_TARGET.get(pro, 0)
                else:
                    _target = _target_objs[0].soft_target
                
                row_data['color'].update({_key1 : ['Green', _target, core_key]})
                if not row_data[_key1] == "NA":
                    row_data['color'].update({_key1 : [get_color(float(row_data[_key1]), _target, pro), _target, core_key]})

            i +=1
        
        result.append(row_data)

    return result


def get_target(core_key, _remove_headers=[]):
    conn = redis.Redis(host="localhost", port=6379, db=0)
    _key = core_key + '_' + "target" + '_' + '*'
    target_list = conn.keys(_key)
    target_dict = {}
    _target_list = []
    if _remove_headers:
        _r_header = _remove_headers[0]
        for item in target_list:
            if not item.endswith(_r_header):
                _target_list.append(item)
    else:
        _target_list = target_list

    for item in _target_list:
        target_dict.update({ item: conn.hgetall(item).values()[0]})
    return target_dict


def get_center_totaldata(total_data=SLA):
    """ Summing of all coloumns of all centers """
    conn = redis.Redis(host="localhost", port=6379, db=0)
    total = []
    #total_data = ['others', 'total', 'buffer', 'billable']
    centers = list(set([project.split("-")[-1] for project in PROJECTS]))
    for center in centers:
        dict1 = {}
        for t in xrange(1, 4): 
            _m_name = 'month_' + str(t)
            one_month_ago = datetime.datetime.now() - relativedelta(months=t)
            month_name = one_month_ago.strftime("%B")

            dict1.update({'center': center, _m_name: month_name})
            for _data in total_data:
                _key1 = 'center_' + _data
                _key = center +'_' + month_name + '_' + _key1
                _key2 = center + '_'+_data +'_'+ _m_name
                dict1.update({_key2 : conn.hgetall(_key).get(_key1, 0) })              

        total.append(dict1)
    return total


def get_headers(core_key):
    headers1 = ['Packet Type', 'Team Target', 'Actual Volume', 'Actual Target', '% Target Acheved']
    headers2 = ['Packet Type', 'FTE Target', 'No of Man Days', 'Actual Volume', 'Actual Target', '% Target Achieved']
    conn = redis.Redis(host="localhost", port=6379, db=0)
    _key = core_key + '_' + "target" + '_' + '*_no_of_agents'
    target_list = conn.keys(_key)
    values_list = []
    remove_headers = []

    for item in target_list:
        values_list.append(conn.hgetall(item).values()[0])

    values_list = list(filter(lambda x: x!= 'None', values_list))

    if values_list:
        headers = headers2
    else:
        headers = headers1
        remove_headers.append('_no_of_agents')

    return headers, remove_headers


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

