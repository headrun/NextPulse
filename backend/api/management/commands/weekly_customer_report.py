from django.core import mail
from django.core.mail import send_mail, BadHeaderError
from django.core.mail import EmailMessage
from django.db.models import Max, Sum
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
import os
import datetime
from itertools import chain
from api.weekly_report_generation import *
from api.models import *
from django.db.models import *
from api.generate_metric_mail import *


class Command(BaseCommand):

    commands = ['weekly_mail_report',]
    args = '[command]'
    help = 'generating  weekly report for production and accuracy'

    def handle(self, *args, **options):

        nw_managers = Nextwealthmanager.objects.filter(name__is_active=True, weekly_mail=True)
        center_managers = Centermanager.objects.filter(name__is_active=True, weekly_mail=True)
        customers = Customer.objects.filter(name__is_active=True, project__is_weekly_mail=True,\
             project__is_voice=False, project__display_project=True, weekly_mail=True, \
                 disable_weekly_metrics = False).distinct()
        tls = TeamLead.objects.filter(name__is_active=True, project__is_voice=False,\
             project__display_project=True, project__is_weekly_mail=True, weekly_mail=True).\
                 distinct()
        customer_metric_weekly = Customer.objects.filter(name__is_active=True, \
            project__is_weekly_mail=True, project__is_voice=False, project__display_project=True, \
                 disable_weekly_metrics=True, weekly_mail = False).distinct()
        custom_list = [30,112,160,129,159,117,180,181,182,123,113,162,114,126,119,115,118,130,127,\
            154,158,121,156,161,116,132]
        
        for customer in customers:
            customer_details = Customer.objects.filter(id=customer.id, project__is_weekly_mail=True,\
                 weekly_mail=True, disable_weekly_metrics=False).\
                     values_list('project', flat=True).distinct()                        
            if len(customer_details) > 0:
                weekly_mail_data(customer_details, customer, 'customer')
        
        for customer in customer_metric_weekly:
            customer_details = Customer.objects.filter(id=customer.id, project__is_weekly_mail=True,\
                 disable_weekly_metrics=True, weekly_mail=False).\
                     values_list('project', flat=True).distinct()
            if len(customer_details) > 0:
                send_weekly_metric_mail(customer, customer_details)

        for tl in tls:
            tl_details = TeamLead.objects.filter(id=tl.id, project__is_weekly_mail=True,\
                 weekly_mail=True).values_list('project',flat=True).distinct()                        
            if tl_details:
                weekly_mail_data(tl_details, tl, 'team_lead') 

        for nw_manager in nw_managers:
            ordering_list = {k:v for v,k in enumerate(custom_list)}         
            projects_list = Project.objects.filter(is_voice=False, display_project=True, \
                is_weekly_mail=True).order_by('name').values_list('id', flat=True).distinct()
            projects_list = list(projects_list)
            projects_list.sort(key=ordering_list.get)                        
            if projects_list:
                weekly_mail_data(projects_list, nw_manager, 'NW_manager')
        
        for cm_manager in center_managers:
            ordering_list = {k:v for v,k in enumerate(custom_list)}         
            center = Centermanager.objects.get(id=cm_manager.id).center_id
            projects_list = Project.objects.filter(center=center, display_project=True,\
                 is_voice=False, is_weekly_mail=True).order_by('name').\
                     values_list('id', flat=True).distinct()
            projects_list = list(projects_list)
            projects_list.sort(key=ordering_list.get)            
            if projects_list:
                weekly_mail_data(projects_list, cm_manager, 'C_manager')


        
