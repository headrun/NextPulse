
import datetime

from api.models import *
from common.utils import getHttpResponse as json_HttpResponse
from voice_service.models import * 


def data_bulk_insertion(table_name, data_dict):
    """Saving the data in inbound hourly table
    """

    dates = []
    db_objs = []
    # creating model objects 
    for key, value in data_dict.iteritems():
    	obj = table_name(**value)
    	db_objs.append(obj)
    	dates.append(obj.date)
        
    table_name.objects.bulk_create(db_objs, batch_size=1500)

    return dates

def save_transfers(table_name, data_list):
	"""Saving transfers
    """
    
	for item in data_list:
		table_name.objects.create(call=InboundHourlyCall.objects.get(call_id=item[0]), transfers=item[1])
	return 'success'


