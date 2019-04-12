from django.core import mail
from django.core.mail import send_mail, BadHeaderError
from django.core.mail import EmailMessage
from django.db.models import Max, Sum
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
import os
import datetime
# from api.weekly_report_generation import *
from api.models import *
from django.db.models import *
# from api.generate_metric_mail import *
from api.weekly_mobile_sms import *


class Command(BaseCommand):

    commands = ['weekly_sms_report',]
    args = '[command]'
    help = 'generating sms weekly report for production and accuracy'

    def handle(self, *args, **options):        
        customers = Customer.objects.filter(name__is_active=True, project__is_weekly_sms=True,\
             project__is_voice=False, project__display_project=True, weekly_sms=True, \
                 weekly_sms_metrics = False).distinct()

        tls = TeamLead.objects.filter(name__is_active=True, project__is_voice=False,\
             project__display_project=True, project__is_weekly_sms=True, weekly_sms=True).\
                 distinct()
                 
        customer_metric_weekly = Customer.objects.filter(name__is_active=True, \
            project__is_weekly_sms=True, project__is_voice=False, project__display_project=True, \
                 weekly_sms_metrics=True, weekly_sms = False).distinct()        
        
        for cust_obj in customers:
            customer_details = Customer.objects.filter(id=cust_obj.id, project__is_weekly_sms=True,\
                weekly_sms=True, weekly_sms_metrics=False).values_list('project', flat=True).distinct()
            weekly_mobile_notifications(customer_details, cust_obj, 'customer') 

        for cus_obj in customer_metric_weekly:
            cust_details = Customer.objects.filter(id=cus_obj.id, project__is_weekly_sms=True,\
                 weekly_sms=False, weekly_sms_metrics=True).\
                     values_list('project', flat=True).distinct()
            weekly_mobile_metric_notifications(cust_details, cus_obj) 

        for tl_obj in tls:
            tl_details = TeamLead.objects.filter(id=tl_obj.id ,project__is_weekly_sms=True,\
                weekly_sms=True).values_list('project',flat=True).distinct()
            weekly_mobile_notifications(tl_details, tl_obj, 'team_lead')

