import calendar
import collections
import datetime
import hashlib
import json
import re
import random
from collections import OrderedDict
from datetime import timedelta
from datetime import date
from dateutil.relativedelta import relativedelta

from django.apps import apps
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.db.models import Sum
from django.db.models import Max
from django.http import HttpResponse
from django.utils.timezone import utc
from django.utils.encoding import smart_str, smart_unicode
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import xlrd
import xlsxwriter
import redis
from xlrd import open_workbook
from xlwt import Workbook, easyxf, XFStyle

from models import *
from src import *

from common.utils import getHttpResponse as json_HttpResponse

from api.annotations import *
from api.basics import *
from api.utils import *
from api.chart import *
from api.commons import *
from api.fte_related import *
from api.graph_error import *
from api.graph_settings import *
from api.graphs import *
from api.internal_external_common import *
from api.monthly_graph import *
from api.per_day_calc import *
from api.production import *
from api.project import *
from api.query_generations import *
from api.redis_operations import *
from api.uploads import *
from api.weekly_graph import *
from api.voice_widgets import *
from api.aht_graph import *
from api.send_push_data import *
from api.sample_algorithm import *
from api.customer_data import *
#From api.location import *
#from api.basic import *
from api.Error_priority import *




#@loginRequired
