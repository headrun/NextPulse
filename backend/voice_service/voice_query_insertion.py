import datetime
from api.models import *
from common.utils import getHttpResponse as json_HttpResponse

def data_bulk_insertion(table_name, data_dict):
    """ saving the data in inbound hourly table """

    db_objs = []
    for key, value in data_dict.iteritems():
    	obj = table_name(**value)
    	db_objs.append(obj)

    table_name.objects.bulk_create(db_objs)

    return 'success'

def save_transfers(table_name, data_list):
	""" Saving transfers """
	for item in data_list:
		table_name.objects.create(call=table_name.objects.get(call_id=item[0]), transfer=item[1])
	return 'success'

"""
def outbound_hourly_query_insertion(customer_data, prj_obj, center_obj,teamleader_obj_name):
    outbnd_hourly_date = customer_data['call_date']

    return outbnd_hourly_date

def inbound_daily_query_insertion(customer_data, prj_obj, center_obj,teamleader_obj_name):
    inbnd_daily_date = customer_data['call_date']
    
    return inbnd_daily_date

def outbound_daily_query_insertion(customer_data, prj_obj, center_obj,teamleader_obj_name):
    outbnd_daily_date = customer_data['call_date']

    return outbnd_daily_date
 
"""
