import datetime
import calendar
from datetime import timedelta
from dateutil.relativedelta import relativedelta
def month(months_dict):
    current_date = datetime.date.today()
    last_mon_date = current_date - relativedelta(months=3)
    from_date = datetime.datetime(last_mon_date.year, last_mon_date.month, 1).date()
    start_date = datetime.datetime(current_date.year, current_date.month, 1)
    to_date = start_date.date() - relativedelta(days=1)
    days = (to_date - from_date).days
    days = days + 1
    months_dict = {}
    for i in xrange(days):
        date = from_date + datetime.timedelta(i)
        month = date.strftime("%B")
        if month in months_dict:
            months_dict[month].append(str(date))
        else:
            months_dict[month] = [str(date)]
    print months_dict
    return months_dict
