from django.core.management.base import BaseCommand, CommandError

from api.models import Claim, FinancialClaimCostAnalysis
import json

class Command(BaseCommand):

    def handle(self, *args, **options):
        data = {}
        for obj in Claim.objects.filter(paid_date__month__in=[10,11,12]):
            loc = obj.state
            plan = obj.member.health_plan

            key = '_'.join([loc, plan])
            if data.has_key(key):
                _data = data[key]
            else:
                _data = {'emp_total':0, 'total_amount':0, 'mem_total':0}

            _data['total_amount'] += obj.amt_charge
            _data['mem_total'] += 1
            if obj.member.emp_self == 'Self':
                _data['emp_total'] += 1

            data[key] = _data
        print "Loading started", len(data)
        for key, _data in data.iteritems():
            loc, plan = key.split('_')
            doc = {}
            doc['location'] = loc
            doc['plan'] = plan
            doc['quarter'] = 'Q4'
            doc.update(_data)
            doc['sub_category'] = 'sub_category'
            doc['plan_cost'] = 'plan_cost'
            FinancialClaimCostAnalysis.objects.create(**doc)
