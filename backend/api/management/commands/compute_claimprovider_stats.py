from django.core.management.base import BaseCommand, CommandError

from api.models import Claim, ClaimsProvidersSummary
import json

class Command(BaseCommand):

    def handle(self, *args, **options):
        data = {}
        for obj in Claim.objects.all():
            loc = obj.state
            disease = obj.disease_category
            procedure = obj.cpt4

            key = '_'.join([loc, disease, procedure])
            if data.has_key(key):
                _data = data[key]
            else:
                _data = {'prov': {}}

            prov = _data['prov'].get(obj.office_name, {'total':0, 'total_amount':0})
            prov['total'] += 1
            prov['total_amount'] += float(obj.amt_charge)

            _data['prov'][obj.office_name] = prov
            data[key] = _data

        print "Loading started", len(data)
        objs = []
        for key, _data in data.iteritems():
            loc, disease, procedure = key.split('_')
            doc = {}
            doc['location'] = loc
            doc['disease'] = disease
            doc['procedure'] = procedure
            doc['data'] = json.dumps(_data['prov'])
            doc['total'] = len(_data['prov'])

            try:
                ClaimsProvidersSummary.objects.update_or_create(**doc)
            except:
                pass
