from django.core.management.base import BaseCommand, CommandError

#from api.models import Claim, InpatientCostDriver
from api.models import Claim, OutpatientCostDriver
import json

class Command(BaseCommand):

    def get_age_group(self, age):
        if age<=20:
            return '20'
        elif age>20 and age<=30:
            return '20-30'
        elif age>30 and age<=40:
            return '30-40'
        elif age>40 and age<=50:
            return '40-50'
        elif age>50 and age<=60:
            return '50-60'
        elif age>60 and age<=70:
            return '60-70'
        elif age>70 and age<=80:
            return '70-80'
        else:
            return '80+'

    def handle(self, *args, **options):
        data = {}
        #for obj in Claim.objects.exclude(admit_date=None):
        for obj in Claim.objects.filter(admit_date=None):
            loc = obj.state
            disease = obj.disease_category
            plan = obj.member.health_plan

            key = '_'.join([loc, disease, plan])
            if data.has_key(key):
                _data = data[key]
            else:
                _data = {'total':0, 'facilities':{}}

            _data['total'] += obj.amt_charge
            facility = _data['facilities'].get(obj.office_name, {'total_amount':0, 'total':0})
            facility['total'] += 1
            facility['total_amount'] += obj.amt_charge
            _data['facilities'][obj.office_name] = facility

            data[key] = _data

        print len(data)
        for key, _data in data.iteritems():
            loc, disease, plan= key.split('_')
            doc = {}
            doc['geography'] = loc
            doc['claimsdriver'] = disease
            doc['plan'] = plan
            doc['population'] = 'alli'
            doc['claims'] = _data['total']
            doc['facilities'] = _data['facilities']
            doc['claims_service'] = 'claims_service'
            doc['claims_cost_service'] = 'claims_cost_service'

            #InpatientCostDriver.objects.create(**doc)
            OutpatientCostDriver.objects.create(**doc)
