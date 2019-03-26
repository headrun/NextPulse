
from django.core import mail
from django.core.mail import send_mail, BadHeaderError
from django.core.mail import EmailMessage
from django.db.models import Max, Sum
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
import os
import datetime
from itertools import chain
from api.send_mobile_data import *
from api.models import *
from django.db.models import *


class Command(BaseCommand):

    commands = ['mobile_sms_report',]
    args = '[command]'
    help = 'generating mobile report for production and accuracy to customers and teamleads'

    def handle(self, *args, **options):
        
        customers = Customer.objects.filter(name__is_active=True, daily_sms=True)                
        tls = TeamLead.objects.filter(name__is_active=True,  daily_sms=True)                      
        
        for customer in customers:
            project_list = Customer.objects.filter(id=customer.id, project__is_daily_sms=True, \
                project__is_voice=False, project__display_project=True,).\
                    values_list('project', flat=True).distinct()            
            if len(project_list) > 0:
                send_mobile_notifications(project_list, customer, 'customer')

        for tl in tls:
            project_list = TeamLead.objects.filter(id=tl.id, project__is_voice=False,\
                 project__display_project=True, project__is_daily_sms=True).\
                     values_list('project',flat=True).distinct()                                    
            if len(project_list) > 0:
                send_mobile_notifications(project_list, tl, 'team_lead')
            

        


        