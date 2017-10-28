from django.shortcuts import render
import xlrd
import datetime
from django.apps import apps
from api.models import *
from api.redis_operations import redis_insert
from api.basics import *
from api.uploads import *
from api.utils import *
from api.query_generations import *
from voice_service.voice_query_insertion import *
from voice_service.constrants import *
from api.voice_widgets import *
from xlrd import open_workbook
from api.commons import data_dict
from common.utils import getHttpResponse as json_HttpResponse


def location_data(prj_id, center, dates_list):
    import pdb;pdb.set_trace()
    result = {}
    return result


def skill_data(prj_id, center, dates_list):
    result = {}

    return result

def disposition_data(prj_id, center, dates_list):
    result = {}

    return result

