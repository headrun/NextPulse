
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
import os

from itertools import chain
from email.MIMEImage import MIMEImage

from api.generate_accuracy_values import generate_internal_and_external_values, generate_targets_data, generate_mail_table_format, generate_logos_format

class Command(BaseCommand):


    commands = ['target_met_report',]
    args = '[command]'
    help = 'generating target met report for production and accuracy'

    def handle(self, *args, **options):

        from django.core import mail
        from django.core.mail import send_mail, BadHeaderError
        from django.core.mail import EmailMessage
        from django.db.models import Max, Sum
        from api.models import *
        import datetime

        nw_managers = Nextwealthmanager.objects.all()
        cntr_managers = Centermanager.objects.all()
        custmrs = Customer.objects.all()
        tls = TeamLead.objects.all()
        managers = list(chain(nw_managers, cntr_managers, custmrs, tls))
        prv_date = datetime.datetime.now() - datetime.timedelta(days=1)

        for manager in managers:
            projects = Project.objects.filter(user=manager.id).values_list('id', flat=True)
            user_data = User.objects.filter(id=manager.id)
            user_email = user_data[0].email
            user_name = user_data[0].first_name
            _text1 = "Dear %s, <p>Below is a snapshot of  'Target'  and  'Actual'  values of SLA/KPI.</p>"\
                       % (user_name)
            mail_data = ''
            prj_count = []
            for project in projects:
                max_date = RawTable.objects.filter(project=project).aggregate(Max('created_at'))
                date = RawTable.objects.filter(project=project).aggregate(Max('date'))
                if str(max_date['created_at__max'].date()) != str(prv_date.date()):
                    prj_count.append(project)
                    result = generate_targets_data(project)
                    name = Project.objects.filter(id=project).values_list('name',flat=True).distinct()
                    project_name = name[0]
                    mail_data = mail_data + '<html></br></html>' + "%s"%(project_name) + generate_mail_table_format(result, project, date)
            if len(prj_count) > 0:
                dashboard_url = "https://nextpulse.nextwealth.in"
                mail_logos = generate_logos_format(dashboard_url)
                mail_body = _text1 + mail_data + mail_logos
                to = [user_email]
                msg = EmailMessage("NextPulse", mail_body, 'nextpulse@nextwealth.in', to)
                msg.content_subtype = "html"
                msg.send()
