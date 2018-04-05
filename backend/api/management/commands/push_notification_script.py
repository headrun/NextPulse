

from django.core.management.base import BaseCommand, CommandError
#import requests
#import json

class Command(BaseCommand):

    commands = ['push_notification_report',]
    args = '[command]',
    help = 'push_notification_data'

    def handle(self, *args, **options):
	
	from django.db.models import Max, Sum
	from api.models import Project,Center,RawTable,TeamLead,Customer,Nextwealthmanager,Centermanager
	import datetime
	import json
	import urllib2


	projects = Project.objects.all()
    	not_req = ["Nextgen", "Quarto", "Bridgei2i", "3i VAPP", "E4U", "Webtrade"]
    	projects_list = filter(lambda x: x.name not in not_req, list(projects))
    	projects_list = projects_list[:1]
    	yesterday_date = datetime.datetime.now() - datetime.timedelta(days=1)
    	for project in projects_list:
            max_date = RawTable.objects.filter(project=project.id).aggregate(Max('created_at'))
    	    tls = TeamLead.objects.filter(project=project).values_list('name',flat=True)
	    #import pdb;pdb.set_trace()	
            customers = Customer.objects.filter(project=project).values_list('name',flat=True)
	    header = {"Content-Type": "application/json; charset=utf-8",
	              "Authorization": "Basic MWNhMjliMjAtNzAxMy00N2Y4LWIxYTUtYzdjNjQzMDkzOTZk"}

	    payload = {"app_id": "d0d6000e-27ee-459b-be52-d65ed4b3d025",
		       #"include_player_ids": ["64e097f5-161b-4120-b4eb-1bc6cdd79122"],
	                "included_segments": ["All"],
	                "contents": {"en": "English Message"}}
	 
	    #req = urllib2.urlopen("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
            url = "https://onesignal.com/api/v1/notifications"
	    opener = urllib2.build_opener(urllib2.HTTPHandler)
	    request = urllib2.Request(url, data=json.dumps(payload))
	    request.add_header("Content-Type", "application/json; charset=utf-8") #Header, Value
	    request.add_header("Authorization", "Basic MWNhMjliMjAtNzAxMy00N2Y4LWIxYTUtYzdjNjQzMDkzOTZk")                                        
	    print opener.open(request)	
 
	    #print(req.status_code, req.reason)
