
# Import Section
from django.shortcuts import render
from django.http import HttpResponse
import json

from src import *





# views section

def get_sla_data(request):
    """ View to display dashboard content """
    data = {'status': 1, 'result' : "some bug is there"}
    proj = request.GET.get('project', None)
    #time = request.GET.get('time', None)
    try:
        data['result'] = get_dash_data(proj, SLA)
        data['center_total'] = get_center_totaldata(SLA)
    except:
        
        data['status'] = 0
    
    data = json.dumps(data)
    return HttpResponse(data)


def get_peoples_data(request):
    """ View to display dashboard content """
    data = {'status': 1, 'result' : "some bug is there"}
    proj = request.GET.get('project', None)
    #time = request.GET.get('time', None)
    try:
        data['result'] = get_dash_data(proj, PEOPLES)
        data['center_total'] = get_center_totaldata(PEOPLES)

    except:
        data['status'] = 0

    data = json.dumps(data)
    return HttpResponse(data)


def get_individual_target(request):
    """ View to display individual target in popup of peoples dashboard """
    data = {'status': 1, 'result' : "some bug is there"}
    core_key = request.GET.get('core_key', 'Gooru_Salem_June')
    column_name = request.GET.get('column_name', 'Productivity')
    try:
        #data['result'] = get_target(core_key)
        if column_name == 'Productivity':
            data['headers'], _remove_headers = get_headers_productivity(core_key)
        else:
            data['headers'], _remove_headers = get_headers(core_key)
        data['result'] = get_target(core_key, _remove_headers)
    except:
        data['status'] = 0

    data = json.dumps(data)
    return HttpResponse(data)





