from django.core.management.base import BaseCommand, CommandError
from openpyxl import load_workbook
from dateutil import parser
import datetime

from api.models import Enrollment

FIELDS = ['emp_id', 'enroll_start', 'enroll_end', 'status', 'mem_id', 'mem_fname', 'mem_lname', 'mem_gender', 'mem_dob', 'mem_adr_line1', 'mem_adr_line2', 'mem_adr_city', 'mem_adr_state', 'mem_adr_zip', 'phone_number', 'email', 'emp_self', 'health_plan', 'annual_hra_funding_amount', 'account_type_code', 'account_contribution', 'employer_contribution_to_fsa', 'pre_existing_illness', 'disease1', 'disease2', 'disease3', 'disease4', 'disease5', 'height', 'weight', 'bmi', 'smoking', 'drinking', 'hdl', 'ldl', 'bp', 'triglycerides', 'income', 'age']

class Command(BaseCommand):

    def handle(self, *args, **options):
        wb = load_workbook(filename='Enrollment_Data_Dummy.xlsx')
        ws = wb['Enrollment']
        count = 0
        for row in ws.rows:
            if count ==0:
                count += 1
                continue
            _row = []
            for cell in row:
                _row.append(cell.value if cell.value else '')
            age = (datetime.datetime.today() - _row[8]).days/365


            row = dict(zip(FIELDS, _row))
            row['age'] = age

            for key in row.keys():
                if not row[key]: row.pop(key)

            Enrollment.objects.create(**row)
