from django.core.management.base import BaseCommand, CommandError

from api.models import Claim, ClaimsProvSummary
import json

class Command(BaseCommand):

    def handle(self, *args, **options):
        months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        for month in months:
            data = {}
            for obj in Claim.objects.filter(paid_date__month=month):
                loc = obj.member.mem_adr_zip
                disease = obj.disease_category
                plan = obj.member.health_plan
                procedure = obj.cpt4

                key = '_'.join([loc, disease, plan, procedure])
                if data.has_key(key):
                    _data = data[key]
                else:
                    _data = {'prov': {}}

                prov = _data['prov'].get(obj.office_name, {'total':0, 'total_amount':0})
                prov['total'] += 1
                prov['total_amount'] += float(obj.amt_charge)

                _data['prov'][obj.office_name] = prov
                data[key] = _data

            print "Loading started"
            objs = []
            for key, _data in data.iteritems():
                loc, disease, plan, procedure = key.split('_')
                doc = {}
                doc['location'] = loc
                doc['disease'] = disease
                doc['procedure'] = procedure
                doc['plan'] = plan
                doc['month'] = month
                doc['data'] = json.dumps(_data['prov'])

                objs.append(ClaimsProvSummary(**doc))

            print "objs", len(objs)
            ClaimsProvSummary.objects.bulk_create(objs, batch_size=2000)
