from django.core.management.base import BaseCommand, CommandError

from api.models import Claim, ClaimsSummary
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
        months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        for month in months:
            data = {}
            print month
            for obj in Claim.objects.filter(paid_date__month=month):
                loc = obj.member.mem_adr_zip
                disease = obj.disease_category
                plan = obj.member.health_plan
                procedure = obj.cpt4
                age_group = self.get_age_group(obj.member.age)

                key = '_'.join([loc, disease, plan, procedure, age_group])
                if data.has_key(key):
                    _data = data[key]
                else:
                    _data = {'total':0, 'total_amount':0, 'insuer':0, 'pocket': 0, 'smoker':0, 'non_smoker':0, 'obese':0, 'fit':0, 'cut_off':0, 'healthy':0, 'unhealthy':0, 'patients':[]}

                _data['total'] += 1
                _data['total_amount'] += obj.amt_charge
                _data['insuer'] += obj.amt_paid_to_prov
                _data['pocket'] += obj.amt_copay + obj.amt_deduct
                _data['patients'].append(obj.member.mem_id)
                if obj.member.smoking == 'Y':
                    _data['smoker'] += 1
                else:
                    _data['non_smoker'] += 1
                if obj.amt_charge > 125000:
                    _data['cut_off'] += 1

                if obj.member.pre_existing_illness == 'No':
                    _data['healthy'] += 1
                else:
                    _data['unhealthy'] += 1

                if obj.member.bmi>25:
                    _data['obese'] += 1
                else:
                    _data['fit'] += 1

                data[key] = _data

            print "Loading started"
            for key, _data in data.iteritems():
                loc, disease, plan, procedure, age_group = key.split('_')
                doc = {}
                doc['location'] = loc
                doc['age_group'] = age_group
                doc['disease'] = disease
                doc['procedure'] = procedure
                doc['plan'] = plan
                doc['month'] = month
                doc.update(_data)
                doc['patients'] = len(list(set(doc['patients'])))

                ClaimsSummary.objects.create(**doc)
