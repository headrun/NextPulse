from django.core.management.base import BaseCommand, CommandError

from api.models import Claim, StayAnalysis
import json

class Command(BaseCommand):

    def handle(self, *args, **options):
        data = {}
        for obj in Claim.objects.exclude(admit_date=None).filter(paid_date__month__in=[1,2,3]):
            loc = obj.state
            disease = obj.disease_category
            plan = obj.member.health_plan

            key = '_'.join([loc, disease, plan])
            if data.has_key(key):
                _data = data[key]
            else:
                _data = {'total':0, 'days':0}

            _data['total'] += 1
            days = ((obj.svc_to - obj.svc_from).days + 1)
            _data['days'] += days

            data[key] = _data

        print "len>>>>", len(data)
        for key, _data in data.iteritems():
            loc, disease, plan= key.split('_')
            doc = {}
            doc['geography'] = loc
            doc['claimsdriver'] = disease
            doc['plan'] = plan
            doc['population'] = 'alli'
            doc['quarter'] = 'Q1'
            doc.update(_data)

            StayAnalysis.objects.create(**doc)
