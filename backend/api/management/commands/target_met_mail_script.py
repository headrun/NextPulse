
from django.core import mail
from django.core.mail import send_mail, BadHeaderError
from django.core.mail import EmailMessage
from django.db.models import Max, Sum
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

import os
import datetime

from itertools import chain
from email.MIMEImage import MIMEImage

from api.generate_accuracy_values import *
from api.models import *


class Command(BaseCommand):


    commands = ['target_met_report',]
    args = '[command]'
    help = 'generating target met report for production and accuracy'

    def handle(self, *args, **options):

        nw_managers = Nextwealthmanager.objects.all()
        center_managers = Centermanager.objects.all()
        customers = Customer.objects.all()
        tls = TeamLead.objects.all()
        
        for customer in customers:
            customer_details = Customer.objects.filter(id=customer.id).\
            values_list('project', flat=True)
            send_mail_data(customer_details, customer, 'customer')

        for tl in tls:
            tl_details = TeamLead.objects.filter(id=tl.id, project__isnull = False).\
                values_list('project',flat=True)
            send_mail_data(tl_details, tl, 'team_lead')

        for nw_manager in nw_managers:
            projects = Project.objects.all()
            projects_list = []
            for project in projects:
                project = project.id
                projects_list.append(project)
            send_mail_data(projects_list, nw_manager, 'NW_manager')
        
        for cm_manager in center_managers:
            center = Centermanager.objects.get(id=cm_manager.id).center_id
            projects = Project.objects.filter(center=center).values_list('id', flat=True)
            send_mail_data(projects, cm_manager, 'C_manager')


        