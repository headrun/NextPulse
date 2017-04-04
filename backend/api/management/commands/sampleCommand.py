from django.core.management.base import BaseCommand, CommandError

'''
Sample Command, you need to run it as follows
python manage.py sampleCommand
'''

class Command(BaseCommand):

    def handle(self, *args, **options):
      pass
