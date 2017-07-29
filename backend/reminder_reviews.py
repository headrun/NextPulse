
import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
import django
django.setup()

from datetime import datetime, timedelta
from api.models import *

from api.views import *
curdate = datetime.datetime.now()
curtime = curdate.time()


def get_all_review_members():
    """ This function gets all members and reviews in that 30 min slots"""
    time_after_half_hour = curdate + timedelta(minutes = 30)

    reviews = Review.objects.filter(review_date__range = (curdate, time_after_half_hour))

    for review in reviews:
        rev_obj = create_dict_data(review)
        members = ReviewMembers.objects.filter(review = review, reminder_mail= False)
        for member in members:
            try:
                send_review_mail(rev_obj, 'reminder', member)
                member.reminder_mail = True
                member.save()
            except:
                pass

get_all_review_members()





