import datetime
from django.core.mail import EmailMessage
from api.models import *
from django.db.models import Max
from api.generate_accuracy_values import generate_logos_format


def send_metric_mail(user, customer_details):
    user_data = User.objects.filter(id=user.name_id)
    user_name = user_data[0].first_name
    yesterdays_date = datetime.datetime.now() - datetime.timedelta(days=1)
    proj = []
    for data in customer_details:
        project = data
        upload_date = RawTable.objects.filter(project=project).aggregate(Max('created_at'))
        upload_date = upload_date['created_at__max']
        if upload_date != None:
            if upload_date.date() == yesterdays_date.date():
                project_name = Project.objects.get(id=project).name
                proj.append(project_name)
    if len(proj) >= 1:
        proj_data = ', '.join(proj)
        _data = "Dear %s, <p>Recent Data has been Uploaded for %s, Please find the Details on NextPulse Dashboard.</p>"\
                        % (user_name, proj_data)
        dashboard_url = "https://nextpulse.nextwealth.in"
        mail_logos = generate_logos_format(dashboard_url)
        mail_body = _data + mail_logos
        to = [user_data[0].email]
        msg = EmailMessage("NextPulse High Level Metrics - Daily Report", mail_body, 'nextpulse@nextwealth.in', to)
        msg.content_subtype = "html"
        msg.send()
    return "success"


def send_weekly_metric_mail(user, customer_details):
    user_data = User.objects.filter(id=user.name_id)
    user_name = user_data[0].first_name
    today = datetime.date.today()
    week_from_date = today - datetime.timedelta(days=today.weekday(),weeks=1)
    week_to_date = week_from_date + datetime.timedelta(days=6)
    from_date = week_from_date
    to_date = week_to_date
    from_d = datetime.datetime.strftime(from_date,"%d  %b  %Y")
    to_d = datetime.datetime.strftime(to_date,"%d  %b  %Y")
    w_dates = str(from_d)+ " to " +str(to_d)
    proj = []
    for data in customer_details:
        project = data
        project_name = Project.objects.get(id=project).name
        proj.append(project_name)
    if len(proj) >= 1:
        proj_name = ', '.join(proj)
        _data = "Dear %s, <p>Recent Data has been Uploaded for %s from %s. Please find the Details on NextPulse Dashboard.</p>"\
                        % (user_name, proj_name, w_dates)
        dashboard_url = "https://nextpulse.nextwealth.in"
        mail_logos = generate_logos_format(dashboard_url)
        mail_body = _data + mail_logos
        to = [user_data[0].email]
        msg = EmailMessage("NextPulse High Level Metrics - Weekly Report", mail_body, 'nextpulse@nextwealth.in', to)
        msg.content_subtype = "html"
        msg.send()
    return "success"