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
from api.generate_metric_mail import *


class Command(BaseCommand):

    commands = ['target_met_report',]
    args = '[command]'
    help = 'generating target met report for production and accuracy'

    def handle(self, *args, **options):

        nw_managers = Nextwealthmanager.objects.filter(name__is_active=True, daily_mail=True)
        center_managers = Centermanager.objects.filter(name__is_active=True, daily_mail=True)
        customers = Customer.objects.filter(name__is_active=True, project__is_daily_mail=True, project__is_voice=False, project__display_project=True, daily_mail=True,disable_daily_metrics=False).distinct()
        tls = TeamLead.objects.filter(name__is_active=True, project__is_voice=False, project__display_project=True, project__is_daily_mail=True, daily_mail=True).distinct()
        customer_metric_daily = Customer.objects.filter(name__is_active=True, disable_daily_metrics=True, project__is_daily_mail=True, project__is_voice=False, project__display_project=True, daily_mail=False).distinct()
        custom_list = [30, 112, 160, 129, 159, 117, 180, 181, 182, 123, 113, 162, 114, 126, 119, 115, 118, 130, 127,
                       154, 158, 121, 156, 161, 116, 132]
        print nw_managers, center_managers, customers, tls, customer_metric_daily                      
        for customer in customers:
            customer_details = Customer.objects.filter(id=customer.id, project__is_daily_mail=True, daily_mail=True, disable_daily_metrics=False).values_list('project', flat=True).distinct()                        
            if len(customer_details) > 0:
                send_mail_data(customer_details, customer, 'customer')
        
        for customer in customer_metric_daily:
            customer_details = Customer.objects.filter(id=customer.id, project__is_daily_mail=True, disable_daily_metrics=True, daily_mail=False).values_list('project', flat=True).distinct()
            if len(customer_details) > 0:
                send_metric_mail(customer, customer_details)

        # for tl in tls:
        #     tl_details = TeamLead.objects.filter(id=tl.id,project__is_daily_mail=True, daily_mail=True).values_list('project',flat=True).distinct()                        
        #     if tl_details:
        #         send_mail_data(tl_details, tl, 'team_lead')

        # for nw_manager in nw_managers:
        #     ordering_list = {k: v for v, k in enumerate(custom_list)}
        #     projects_list = Project.objects.filter(is_voice=False ,display_project=True, is_daily_mail=True).order_by('name').values_list('id', flat=True).distinct()
        #     projects_list = list(projects_list)
        #     projects_list.sort(key=ordering_list.get)
        #     if projects_list:
        #         send_mail_data(projects_list, nw_manager, 'NW_manager')
        
        # for cm_manager in center_managers:
        #     ordering_list = {k: v for v, k in enumerate(custom_list)}
        #     center = Centermanager.objects.get(id=cm_manager.id).center_id
        #     projects = Project.objects.filter(center=center, display_project=True, is_voice=False, is_daily_mail=True).order_by('name').values_list('id', flat=True).distinct()
        #     projects_list = list(projects)
        #     projects_list.sort(key=ordering_list.get)
        #     if projects_list:
        #         send_mail_data(projects_list, cm_manager, 'C_manager')


        
