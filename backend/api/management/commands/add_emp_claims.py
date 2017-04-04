from django.core.management.base import BaseCommand, CommandError

from api.models import Claim, Enrollment
import random

class Command(BaseCommand):

    def handle(self, *args, **options):
        mem_objs = []
        print "Enrollment started"
        for mem in Enrollment.objects.all():
            mem_objs.append(mem)
        print "Claims started"
        for obj in Claim.objects.all():
            obj.member = random.choice(mem_objs)
            obj.save()
