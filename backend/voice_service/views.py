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
from xlrd import open_workbook
from api.commons import data_dict
from common.utils import getHttpResponse as json_HttpResponse





