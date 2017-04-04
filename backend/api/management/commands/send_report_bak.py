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

        details = []
        mail_data = ''

        yesterday_date = datetime.datetime.now() - datetime.timedelta(days=1)

        for proj in proj_list:
            proj_data = RawTable.objects.filter(project_id=proj.id)
            max_date = proj_data.aggregate(Max('created_at'))
            if max_date['created_at__max'] is not None:
                if yesterday_date.date() > max_date['created_at__max'].date():
                    mes = 'Sheet not uploaded yesterday'
                    updated_on = 'Last sheet upload on ' + str(max_date['created_at__max'].date())
                    project = proj.name
                else:
                    mes = 'Latest Sheet Uploaded'
                    updated_on = 'Latest sheet uploaded on '+ str(max_date['created_at__max'].date())
                    project = proj.name
                details.append({'message':mes, 'last_updated_on':updated_on, 'project':project})
            else:
                mes = 'No Data'
                updated_on = 'No Data'
                project = proj.name
                details.append({'message':mes, 'last_updated_on':updated_on, 'project':project})

        for one in details:
            mail_data += "<h4>"+one['project']+"</h4>"+"<ul>"+"<li>"+one['last_updated_on']+"</li>"+"<li>"+one['message']+"</li></ul>"

        """msg = EmailMessage("Next Pulse : Sheet upload status" , mail_data, 'nextpulse@nextwealth.in', \
            ['yeswanth@headrun.com','asifa@headrun.net','durgababu@headrun.net','yatish@headrun.com','karthik@headrun.com', \
            'kannan.sundar@nextwealth.in','poornima.mitta@nextwealth.in', 'sankar.k@mnxw.org','sai@headrun.com'])"""
        msg = EmailMessage("Next Pulse : Sheet upload status" , mail_data, 'nextpulse@nextwealth.in', \
            ['asifa@headrun.net'])

        msg.content_subtype = "html"
        msg.send()
