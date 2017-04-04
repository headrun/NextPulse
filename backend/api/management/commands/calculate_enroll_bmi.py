from django.core.management.base import BaseCommand, CommandError

from api.models import Claim, Enrollment
import random

class Command(BaseCommand):

    def handle(self, *args, **options):

        for obj in Claim.objects.filter(disease_category='other'):
            print obj.dx_1
