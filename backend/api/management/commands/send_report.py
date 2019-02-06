from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
class Command(BaseCommand):

    commands = ['sendreport',]
    args = '[command]'
    help = 'Send report'

    def handle(self, *args, **options):


        from django.core import mail
        from django.core.mail import send_mail, BadHeaderError
        from django.core.mail import EmailMessage
        from django.db.models import Max
        from api.models import Project,RawTable
        import datetime

        proj_list = Project.objects.filter(display_project = True).order_by('name').distinct()

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
        
        for one in details:
            mail_data += "<h4>"+one['project']+"</h4>"+"<ul>"+"<li>"+one['last_updated_on']+"</li>"+"<li>"+one['message']+"</li></ul>"


        to = ['prabhakaran.k@mnw.co.in','kannan.sundar@nextwealth.in','poornima.mitta@nextwealth.in', 'sankar.k@mnxw.org','Jagadish.sh@nextwealth.in']

        msg = EmailMessage("Next Pulse : Sheet upload status" , mail_data, 'nextpulse@nextwealth.in', to)
    
        msg.content_subtype = "html"
        msg.send()
