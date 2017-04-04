from django.core.management.base import BaseCommand, CommandError

from api.models import Claim, EnrollClaimSummary

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
        for obj in Claim.objects.all():
            loc = obj.member.mem_adr_zip
            gender = obj.member.mem_gender
            plan = obj.member.health_plan
            age_group = self.get_age_group(obj.member.age)

            key = '_'.join([loc, gender, plan, age_group])
            if data.has_key(key):
                _data = data[key]
            else:
                _data = {'total':0, 'emp_total':[]}

            _data['total'] += 1
            _data['emp_total'].append(obj.member.mem_id)

            data[key] = _data

        print "Loading started", len(data)
        for key, _data in data.iteritems():
            loc, gender, plan, age_group = key.split('_')
            doc = {}
            doc['location'] = loc
            doc['age_group'] = age_group
            doc['gender'] = gender
            doc['plan'] = plan
            doc.update(_data)
            doc['emp_total'] = len(list(set(doc['emp_total'])))
            EnrollClaimSummary.objects.create(**doc)
