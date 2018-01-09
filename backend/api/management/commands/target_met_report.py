from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User


class Command(BaseCommand):


    commands = ['target_met_report',]
    args = '[command]'
    help = 'generating target met report for production and accuracy'

    def handle(self, *args, **options):

        from django.core import mail
        from django.core.mail import send_mail, BadHeaderError
        from django.core.mail import EmailMessage
        from django.db.models import Max, Sum
        from api.models import Project,RawTable,TeamLead,Targets,Internalerrors,Externalerrors

        result = {}
        mail_body = ''
        projects = Project.objects.all()
        not_req = ["Nextgen", "Quarto", "Bridgei2i", "3i VAPP", "E4U", "Webtrade"]
        projects_list = filter(lambda x: x.name not in not_req, list(projects))
        projects_list = projects_list[:4]
        for project in projects_list:
            tls = TeamLead.objects.filter(project=project).values_list('name', flat=True)[:1]
            for tl in tls:
                tl_id = User.objects.filter(id=tl)
                tl_name = tl_id[0].username
                tl_email = tl_id[0].email
                date_query = RawTable.objects.filter(project_id=project.id).aggregate(Max('date'))
                last_date = str(date_query['date__max'])
                rawtable_query = RawTable.objects.filter(project=project.id, date=last_date).aggregate(Sum('per_day'))
                production_value = rawtable_query['per_day__sum']
                target_query = Targets.objects.filter(\
                                project=project.id, from_date__lte=last_date, \
                                to_date__gte=last_date, target_type='Production').aggregate(Sum('target_value'))
                if target_query['target_value__sum'] == None:
                    prod_target_value = 0
                else:
                    prod_target_value = target_query['target_value__sum']
                if prod_target_value > production_value:
                    msg = str(project) + ' deos not met the given production target'
                    result.update({'msg': msg, 'target': 'Target value is '+str(prod_target_value), 'actual': 'Actual value is '+str(production_value)})
                    content = "<h4>"+result['msg']+"</h4>"+"<ul>"+"<li>"+result['target']+"</li>"+"<li>"+result['actual']+"</li></ul>"
                    text = "<p> Kindly Login into the NextPulse https://nextpulse.nextwealth.in to view the metrics.</p>"
                    mail_body = content + text
                    to = [tl_email]
                    msg = EmailMessage("NextPulse Production Status", mail_body, 'nextpulse@nextwealth.in', to)
                    msg.content_subtype = "html"
                    msg.send()
