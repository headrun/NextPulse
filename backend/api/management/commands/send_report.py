from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
class Command(BaseCommand):

    commands = ['sendreport',]
    args = '[command]'
    help = 'Send report'

    def handle(self, *args, **options):


        #reports = Log.objects.filter(date__gt=datetime.today(),date__lt=(datetime.today()+timedelta(days=2)))
        #for report in reports:
        from django.core import mail
        from django.core.mail import send_mail, BadHeaderError
        from django.core.mail import EmailMessage
        from django.db.models import Max
        from api.models import Project,RawTable
        import datetime

        proj_list = Project.objects.all()

        not_req = ["Nextgen", "Quarto", "Bridgei2i", "3i VAPP", "E4U"]
	proj_list = filter(lambda x: x.name not in not_req, list(proj_list))

        details = []
        mail_data = ''

        yesterday_date = datetime.datetime.now() - datetime.timedelta(days=1)

        for proj in proj_list:
            proj_data = RawTable.objects.filter(project_id=proj.id)
            max_date = proj_data.aggregate(Max('created_at'))
            if max_date['created_at__max'] is not None:
                if yesterday_date.date() > max_date['created_at__max'].date():
                    mes = 'Sheet Not Uploaded Yesterday'
                    updated_on = 'Last Sheet Upload On ' + str(max_date['created_at__max'].date())
                    project = proj.name
                else:
                    mes = 'Latest Sheet Uploaded'
                    updated_on = 'Latest Sheet Uploaded On '+ str(max_date['created_at__max'].date())
                    project = proj.name
                details.append({'message':mes, 'last_updated_on':updated_on, 'project':project})
            else:
                mes = 'No Data'
                updated_on = 'No Data'
                project = proj.name
                details.append({'message':mes, 'last_updated_on':updated_on, 'project':project})
        details.sort()
        for one in details:
            mail_data += "<h4>"+one['project']+"</h4>"+"<ul>"+"<li>"+one['last_updated_on']+"</li>"+"<li>"+one['message']+"</li></ul>"


	to = ['yeswanth@headrun.com','asifa@headrun.net','yatish@headrun.com', 'rishi@headrun.com', \
            'kannan.sundar@nextwealth.in','poornima.mitta@nextwealth.in', 'sankar.k@mnxw.org']

	#to = ['abhishek@headrun.com', 'asifa@headrun.net']
        msg = EmailMessage("Next Pulse : Sheet upload status" , mail_data, 'nextpulse@nextwealth.in', to)
    
        msg.content_subtype = "html"
        msg.send()
