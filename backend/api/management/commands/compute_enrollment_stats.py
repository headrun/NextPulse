from django.core.management.base import BaseCommand, CommandError

from api.models import Enrollment, EnrollmentSummary

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

    def get_income_group(self, income):
        if income<=50000:
            return '50K'
        elif income>50000 and income<=80000:
            return '50-80K'
        elif income>80000 and income<=100000:
            return '80-100K'
        elif income>100000 and income<=120000:
            return '100-120K'
        elif income>120000 and income<=150000:
            return '120-150K'
        elif income>150000 and income<=200000:
            return '150-200K'
        else:
            return '200K'

    def handle(self, *args, **options):
        years = [2010, 2011, 2012, 2013, 2014, 2015, 2016]
        for year in years:
            data = {}
            print year
            for obj in Enrollment.objects.all():
                is_process = False
                if year>=obj.enroll_start.year and year<=obj.enroll_end.year:
                    is_process = True
                if not is_process:
                    continue
                loc = obj.mem_adr_zip
                gender = obj.mem_gender
                age_group = self.get_age_group(obj.age)
                income_group = self.get_income_group(obj.income)
                plan = obj.health_plan

                key = '_'.join([loc, gender, age_group, income_group, plan])
                if data.has_key(key):
                    _data = data[key]
                else:
                    _data = {'total':0, 'emp_total':0}

                _data['total'] += 1
                if obj.emp_self == 'Self':
                    _data['emp_total'] += 1

                data[key] = _data

            for key, count in data.iteritems():
                loc, gender, age_group, income_group, plan = key.split('_')
                doc = {}
                doc['location'] = loc
                doc['gender'] = gender
                doc['age_group'] = age_group
                doc['income_group'] = income_group
                doc['plan'] = plan
                doc['year'] = year
                doc.update(count)

                EnrollmentSummary.objects.create(**doc)
