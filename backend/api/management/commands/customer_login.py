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

        customers = Customer.objects.all()

        details = []
        mail_data = ''

        for customer in customers:
            cust_data = User.objects.filter(id=customer.name_id)[0]
            cust_data_last_login = cust_data.last_login
            if cust_data.last_login !=None:
                check_date = datetime.datetime.now().date() - cust_data_last_login.date()
                final_date = check_date.days
                mes = 'Last login ' + str(final_date) + ' days ago'
                updated_on = 'Last login on ' + str(cust_data.last_login.date())
                customer_name = cust_data.username
                details.append({'message':mes, 'last_login_on':updated_on, 'customer':customer_name})
	    if cust_data.last_login == None:
		customer_name = cust_data.username
		details.append({'message': 'Last login - never', 'last_login_on': '', 'customer':customer_name})

        for one in details:
            mail_data += "<h4>"+one['customer']+"</h4>"+"<ul>"+"<li>"+one['last_login_on']+"</li>"+"<li>"+one['message']+"</li></ul>"


	to = ['asifa@headrun.net','yatish@headrun.com','rishi@headrun.com', \
            'kannan.sundar@nextwealth.in','poornima.mitta@nextwealth.in','sankar.k@mnxw.org']

        msg = EmailMessage("Next Pulse : Customer last login details" , mail_data, 'nextpulse@nextwealth.in', to) 

        msg.content_subtype = "html"
        msg.send()
