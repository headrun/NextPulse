from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
class Command(BaseCommand):

    commands = ['customer_login_report',]
    args = '[command]'
    help = 'customer_login_report'

    def handle(self, *args, **options):


        from django.core import mail
        from django.core.mail import send_mail, BadHeaderError
        from django.core.mail import EmailMessage
        from django.db.models import Max
        from api.models import Project,RawTable,Customer
        import datetime

        customers = Customer.objects.filter(name__is_active=True,project__display_project=True).order_by('name_id__username').distinct()

        details = []
        mail_data = ''

        for customer in customers:
            cust_data = User.objects.filter(id=customer.name_id)[0]
            proje = Customer.objects.filter(name_id=customer.name_id,project__display_project=True).values_list('project__name',flat=True).distinct()
            cust_data_last_login = cust_data.last_login
            if cust_data.last_login !=None and proje:
                check_date = datetime.datetime.now().date() - cust_data_last_login.date()
                final_date = check_date.days
                mes = 'Last login ' + str(final_date) + ' days ago'
                updated_on = 'Last login on ' + str(cust_data.last_login.date())
                proje = ','.join(proje)
                customer_name = cust_data.username
                details.append({'message':mes, 'last_login_on':updated_on, 'customer':customer_name, 'project':proje})

        detail = sorted(details, key = lambda x: x['project'])

        for one in detail:
            mail_data += "<h4>"+one['project']+" - "+one['customer']+"</h4>"+"<ul>"+"<li>"+one['last_login_on']+"</li>"+"<li>"+one['message']+"</li></ul>"


        to = ['kannan.sundar@nextwealth.in','poornima.mitta@nextwealth.in','sankar.k@mnxw.org','Jagadish.sh@nextwealth.in']

        msg = EmailMessage("Next Pulse : Customer last login details" , mail_data, 'nextpulse@nextwealth.in', to) 

        msg.content_subtype = "html"
        msg.send()
