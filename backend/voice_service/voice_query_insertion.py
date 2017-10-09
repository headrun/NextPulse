import datetime
from api.models import *
from common.utils import getHttpResponse as json_HttpResponse

def inbound_hourly_query_insertion(customer_data, prj_obj, center_obj,teamleader_obj_name):
    inbnd_hourly_date = customer_data['call_date']    

    return inbnd_hourly_date


def outbound_hourly_query_insertion(customer_data, prj_obj, center_obj,teamleader_obj_name):
    outbnd_hourly_date = customer_data['call_date']

    return outbnd_hourly_date

def inbound_daily_query_insertion(customer_data, prj_obj, center_obj,teamleader_obj_name):
    inbnd_daily_date = customer_data['call_date']
    
    return inbnd_daily_date

def outbound_daily_query_insertion(customer_data, prj_obj, center_obj,teamleader_obj_name):
    outbnd_daily_date = customer_data['call_date']

    return outbnd_daily_date
 
