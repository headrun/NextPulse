import os
import re
import xlrd
from xlrd import open_workbook
from glob import glob
#from django.conf import settings
import pdb;pdb.set_trace()
from api.models import *

#import pdb;pdb.set_trace()

#PAR_DIR = os.path.abspath(os.pardir)
PAR_DIR = os.getcwd()
FILES_DIR=os.path.join(PAR_DIR, 'media/documents')

excel_files = glob("%s/*" % (FILES_DIR))

def run():
    for fname in excel_files:
        open_book = xlrd.open_workbook(fname)
        file_name = os.path.basename(fname)
        var       = file_name.split('.')[-1].lower()
        if var not in ['xls', 'xlsx', 'xlsb']:
            return HttpResponse("Invalid File")
        else:
            try:
                open_book = open_workbook(filename=None, file_contents=fname.read())
                #open_sheet = open_book.sheet_by_index(0)
            except:
                return HttpResponse("Invalid File")
            import pdb;pdb.set_trace()
            excel_sheet_names = open_book.sheet_names()
            file_sheet_name = Authoringtable.objects.values_list('sheet_name',flat=True).distinct()
            file_sheet_names = [x.encode('UTF8') for x in file_sheet_name]
            sheet_index_dict = {}
            for sh_name in file_sheet_names:
                if sh_name in excel_sheet_names:
                    sheet_index_dict[sh_name] = open_book.sheet_names().index(sh_name)

        file_sheet_name = Authoringtable.objects.values_list('sheet_name',flat=True).distinct()



