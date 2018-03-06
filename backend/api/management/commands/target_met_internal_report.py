from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User


class Command(BaseCommand):


    commands = ['target_met_report',]
    args = '[command]'
    help = 'generating target met report for Internal accuracy'

    def handle(self, *args, **options):


        from django.core import mail
        from django.core.mail import send_mail, BadHeaderError
        from django.core.mail import EmailMessage
        from django.db.models import Max, Sum
        from api.models import Project,RawTable,TeamLead,Targets,Internalerrors

        
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
                                to_date__gte=last_date, target_type='Internal accuracy').aggregate(Sum('target_value'))
                audited_errors = Internalerrors.objects.filter(project=project.id, date=last_date).aggregate(Sum('audited_errors'))
                total_errors = Internalerrors.objects.filter(project=project.id, date=last_date).aggregate(Sum('total_errors'))
                audited_count, error_count, target_value = 0, 0, 0
                if not audited_errors['audited_errors__sum'] == None:
                    audited_count = audited_errors['audited_errors__sum']
                if not total_errors['total_errors__sum'] == None:
                    error_count = total_errors['total_errors__sum']
                if not target_query['target_value__sum'] == None:
                    target_value = target_query['target_value__sum']
                if audited_count != 0:
                    accuracy = 100 - (error_count/audited_count)*100
                elif audited_count == 0:
                    accuracy = 100 - (error_count/production_value)*100
                if target_value > accuracy:
                    msg = str(project) + ' deos not met the given internal accuracy target'
                    result.update({'msg': msg, 'target': 'Target value is '+str(target_value), 'actual': 'Actual value is '+str(accuracy)})
                    content = "<h4>"+result['msg']+"</h4>"+"<ul>"+"<li>"+result['target']+"</li>"+"<li>"+result['actual']+"</li></ul>"
                    text = "<p> Kindly Login into the NextPulse https://nextpulse.nextwealth.in to view the metrics.</p>"
                    mail_body = content + text
                    to = [tl_email]
                    msg = EmailMessage("NextPulse Internal Accuracy Status", mail_body, 'nextpulse@nextwealth.in', to)
                    msg.content_subtype = "html"
                      
                    
  
