from django.core import mail
from django.core.mail import send_mail, BadHeaderError
from django.core.mail import EmailMessage
from django.db.models import Max, Sum
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
import os
import datetime
from itertools import chain
from api.generate_accuracy_values import *
from api.models import *
from django.db.models import *


class Command(BaseCommand):

    commands = ['target_met_report',]
    args = '[command]'
    help = 'generating target met report for production and accuracy'

    def handle(self, *args, **options):

        projects_list = Project.objects.filter(is_voice=False ,display_project=True, is_enable_mail=True).values_list('id', flat=True).distinct()                                
        nw_managers = Nextwealthmanager.objects.filter(name__is_active=True, enable_mail=True)                               
        center_managers = Centermanager.objects.filter(name__is_active=True, enable_mail=True)                               
        customers = Customer.objects.filter(name__is_active=True, project__is_enable_mail=True, project__is_voice=False, project__display_project=True, enable_mail=True)                
        tls = TeamLead.objects.filter(name__is_active=True, project__is_voice=False, project__display_project=True, project__is_enable_mail=True, enable_mail=True)                
        
        
        for customer in customers:
            customer_details = Customer.objects.filter(id=customer.id, project__is_enable_mail=True, enable_mail=True).values_list('project', flat=True).distinct()                        
            if len(customer_details) > 0:
                send_mail_data(customer_details, customer, 'customer')

        for tl in tls:
            tl_details = TeamLead.objects.filter(id=tl.id,project__is_enable_mail=True, enable_mail=True).values_list('project',flat=True).distinct()                        
            if tl_details:
                send_mail_data(tl_details, tl, 'team_lead')

        for nw_manager in nw_managers:
            projects_list = Project.objects.filter(is_voice=False ,display_project=True, is_enable_mail=True).values_list('id', flat=True).distinct()                        
            if projects_list:
                send_mail_data(projects_list, nw_manager, 'NW_manager')
        
        for cm_manager in center_managers:
            center = Centermanager.objects.get(id=cm_manager.id).center_id
            projects = Project.objects.filter(center=center, display_project=True, is_voice=False, is_enable_mail=True).values_list('id', flat=True).distinct()
            if projects_list:
                send_mail_data(projects, cm_manager, 'C_manager')


        
