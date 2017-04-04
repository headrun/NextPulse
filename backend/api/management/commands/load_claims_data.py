from django.core.management.base import BaseCommand, CommandError
from openpyxl import load_workbook
from dateutil import parser
import datetime

from api.models import Claim

FIELDS = ['grp', 'cert_num', 'seq', 'cid', 'l_name', 'm_name', 'f_name', 'addr1', 'addr2', 'city', 'state', 'zip', 'plan_mm', 'status', 'dep_status_mm', 'mem_f_name', 'mem_l_name', 'mem_dob', 'mem_sex', 'rel', 'prov_1_key', 'prov_1_tin', 'office_name', 'provaddr1', 'provaddr2', 'provcity', 'provstate', 'provzip', 'spec1', 'drg', 'rev_code', 'dx_1', 'dx_2', 'dx_3', 'dx_4', 'px_code', 'amt_charge', 'amt_paid_to_prov', 'amt_disallowed', 'amt_copay', 'amt_deduct', 'clm_status', 'paid_date', 'svc_from', 'svc_to', 'admit_date', 'cob_amt_emp', 'cob_amt_prov', 'coins', 'amt_allowed', 'units', 'mod_1', 'mod_2', 'mod_3', 'cpt4', 'net_1', 'inelig_reason_code', 'amt_paid_to_pt', 'npi', 'disease_category']

class Command(BaseCommand):

    def handle(self, *args, **options):
        wb = load_workbook(filename='20151202-Medical.xlsx')
        ws = wb['Sheet1']
        count = 0
        print "Reading Started"
        for row in ws.rows:
            if count ==0:
                count += 1
                continue
            _row = []
            for cell in row:
                _row.append(cell.value if cell.value else '')


            row = dict(zip(FIELDS, _row))
            row['l_name'] = ''
            row['f_name'] = ''
            row['m_name'] = ''
            row['addr1'] = ''
            row['addr2'] = ''
            row['city'] = ''
            row['mem_f_name'] = ''
            row['mem_l_name'] = ''

            for key in row.keys():
                try:
                    row[key] = row[key].strip()
                except:
                    pass
                if not row[key]: row.pop(key)

            row['mem_dob'] = parser.parse(str(row['mem_dob']))
            row['paid_date'] = parser.parse(str(row['paid_date']))
            row['svc_from'] = parser.parse(str(row['svc_from']))
            row['svc_to'] = parser.parse(str(row['svc_to']))
            if row.has_key('admit_date'):
                row['admit_date'] = parser.parse(str(row['admit_date']))

            Claim.objects.create(**row)
