from django.views.decorators.csrf import csrf_exempt
from xlrd import open_workbook
import copy
import xlrd
import copy
import time
import datetime
import json
import traceback
import os
import operator
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect

from xlrd import open_workbook
from xlwt import Workbook, easyxf, XFStyle
from operator import *
from functools import wraps

from collections import OrderedDict

#from ARS.custom_decorators import login_required
#from ARS.models import *
#from Reports.models import *

#from Utils.utils import *
import xlsxwriter
from datetime import date, timedelta
#from ARS.views.base import init_logger
import datetime as DT
from django.conf import settings

