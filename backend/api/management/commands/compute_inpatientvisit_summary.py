from django.core.management.base import BaseCommand, CommandError

#from api.models import Claim, InpatientVisitTrend
from api.models import Claim, OutpatientVisitTrend
import json

class Command(BaseCommand):

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
                _data = {'trends':{}, 'cost':{}}

            _data['trends'][obj.paid_date.month] = _data['trends'].get(obj.paid_date.month, 0) + 1
            cost = _data['cost'].get(obj.paid_date.month, {'total':0, 'paid':0, 'total_amount':0})
            cost['total_amount'] += obj.amt_charge
            cost['total'] += 1
            cost['paid'] += obj.amt_copay + obj.amt_deduct
            _data['cost'][obj.paid_date.month] = cost

            data[key] = _data

        print len(data)
        for key, _data in data.iteritems():
            loc, disease, plan= key.split('_')
            doc = {}
            doc['geography'] = loc
            doc['claimsdriver'] = disease
            doc['plan'] = plan
            doc['population'] = 'alli'
            doc.update(_data)
            doc['trends_type'] = 'trends_type'

            #InpatientVisitTrend.objects.create(**doc)
            OutpatientVisitTrend.objects.create(**doc)
