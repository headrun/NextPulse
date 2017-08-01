
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
    except:
        data['status'] = 0

    data = json.dumps(data)
    return HttpResponse(data)


