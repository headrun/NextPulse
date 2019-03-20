import datetime
from django.core.mail import EmailMessage
from api.models import *
from django.db.models import Max


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
        proj_data = ' , '.join(proj)
        _data = "Dear %s, <p>Recent Data has been Uploaded for following project %s, Please find the Details on NextPulse Dashboard.</p>"\
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
        proj_name = ' , '.join(proj)
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


def generate_logos_format(dashboard_url):

    _text1 = "<html>\
              <body>"
    _text2 = "<p> Please login to NextPulse for details on metrics and graphs by clicking the following link,  <br> %s"\
            "<br>\
            <p>Thanks and Regards</p>\
            <p>NextPulse Team</p>\
            <p>NextWealth Entrepreneurs Pvt Ltd</p>" % dashboard_url

    logo = "<table class=NormalTable border=0 cellspacing=0 cellpadding=0>\
                <tbody>\
                    <tr>\
                        <td width=450 style=width:337.5px; padding: 0px 0px 0px 0px;>\
                            <div align=center>\
                                <table class=NormalTable border=0 cellspacing=0 cellpadding=0>\
                                    <tbody>\
                                        <tr>\
                                            <td valign=top style=padding: 0px 0px 0px 0px;>\
                                                <p class=MsoNormal>\
                                                    <span>\
                                                        <u></u>\
                                                        <u></u>\
                                                        <u></u>\
                                                    </span>\
                                                </p>\
                                            </td>\
                                            <td>\
                                                <span></span>\
                                            </td>\
                                            <td style=padding:0px 0px 0px 0px;>\
                                                <p class=MsoNoraml>\
                                                    <span>\
                                                        <span style=font-size:1.0pt;>\
                                                            <u></u>\
                                                            <u></u>\
                                                            <u></u>\
                                                        </span>\
                                                    </span>\
                                                </p>\
                                            </td>\
                                            <td>\
                                                <span></span>\
                                            </td>\
                                            <td valign=top style=padding: 0px 0px 0px 0px;>\
                                                <p class=MsoNormal>\
                                                    <span>\
                                                        <u></u>\
                                                        <u></u>\
                                                        <u></u>\
                                                    </span>\
                                                </p>\
                                            </td>\
                                            <td>\
                                                <span></span>\
                                            </td>\
                                        </tr>\
                                        <tr style=height:132.0pt;>\
                                            <td width=130 valign=top style=width:97.5pt;padding:0px 0px 0px 0px;>\
                                                <table class=MsoNormalTable border=0 cellspacing=0 cellpadding=0>\
                                                    <tbody>\
                                                        <tr>\
                                                            <td style=padding:7.5pt 0in 0in 0in;>\
                                                                <p class=MsoNormal>\
                                                                    <span>\
                                                                    </span>\
                                                                    <span style=font-size:10.5pt;font-family:Arial,sans-serif;color:#7f7f7f>\
                                                                    <img width=127 height=81 style=width:1.3229in;height:.8437in src=http://stats.headrun.com/images/nextwealth.png>\
                                                                    <u></u>\
                                                                    <u></u>\
                                                                    </span>\
                                                                </p>\
                                                            </td>\
                                                            <td>\
                                                                <span></span>\
                                                            </td>\
                                                        </tr>\
                                                    </tbody>\
                                                </table>\
                                                <span></span>\
                                            </td>\
                                            <td>\
                                                <span></span>\
                                            </td>\
                                            <td width=10 style=width:7.5pt;padding:0in 0in 0in 0in;height:132.0pt>\
                                                <p class=MsoNormal>\
                                                    <span>\
                                                        <span style=font-size:1.0pt>\
                                                            <u></u>\
                                                            <u></u>\
                                                            <u></u>\
                                                        </span>\
                                                    </span>\
                                                </p>\
                                            </td>\
                                            <td>\
                                                <span></span>\
                                            <td>\
                                            <td width=240 valign=top style=width:2.5in;padding:0in 0in 0in 0in;height:132.0pt>\
                                                <table class=NormalTable border=0 cellspacing=0 cellpadding=0>\
                                                    <tbody>\
                                                        <tr>\
                                                            <td style=padding:7.5pt 0in 0in 0in>\
                                                                <table class=NormalTable border=0 cellspacing=0 cellpadding=0 width=100% style=width:100.0%>\
                                                                    <tbody>\
                                                                        <tr></tr>\
                                                                        <tr>\
                                                                            <td width=7% style=width:7.0%;padding:0in 0in 0in 0in>\
                                                                                <p class=MsoNoraml>\
                                                                                    <span>\
                                                                                        <img width=9 height=18 style=width:.125in;height:.2083in src=http://stats.headrun.com/images/location_new.jpg>\
                                                                                        <u></u>\
                                                                                        <u></u>\
                                                                                    </span>\
                                                                                </p>\
                                                                            </td>\
                                                                            <td>\
                                                                                <span></span>\
                                                                            </td>\
                                                                            <td width=110% style=width:110%;padding:0in 0in 7.5pt 0in>\
                                                                                <p class=MsoNormal>\
                                                                                    <span></span>\
                                                                                    <a href=https://www.google.com/maps?q=728,+6th+B+Cross+Road,+Koramangala,+3rd+Block&entry=gmail&source=g target=_blank>\
                                                                                        <span>\
                                                                                            <span style=font-size:9.0pt;font-family:Arial,sans-serif;> 6th B Cross Road, Koramangala, 3rd Block, Bengaluru - 560034, Karnataka, INDIA\
                                                                                            </span>\
                                                                                        </span>\
                                                                                        <span></span>\
                                                                                    </a>\
                                                                                    <span>\
                                                                                        <span style=font-size:9.0pt;font-family:Arial,sans-serif>\
                                                                                            <u></u>\
                                                                                            <u></u>\
                                                                                        </span>\
                                                                                    </span>\
                                                                                </p>\
                                                                            </td>\
                                                                            <td>\
                                                                                <span></span>\
                                                                            </td>\
                                                                        </tr>\
                                                                        <tr>\
                                                                            <td width=7% style=width:7.0%;padding:0in 0in 0in 0in>\
                                                                                <p class=MsoNoraml>\
                                                                                    <span>\
                                                                                        <img width=9 height=18 style=width:.125in;height:.2083in src=http://stats.headrun.com/images/office_new.jpg>\
                                                                                        <u></u>\
                                                                                        <u></u>\
                                                                                    </span>\
                                                                                </p>\
                                                                            </td>\
                                                                            <td>\
                                                                                <span></span>\
                                                                            </td>\
                                                                            <td width=93% style=width:93.0%;padding:0in 0in 0in 0in;height:15.0pt>\
                                                                                <p class=MsoNormal>\
                                                                                    <span></span>\
                                                                                    <a href=www.nextwealth.in target=_blank>\
                                                                                        <span>\
                                                                                            <span style=font-size:9.0pt;font-family:Arial,sans-serif;>www.nextwealth.in\
                                                                                            </span>\
                                                                                        </span>\
                                                                                        <span></span>\
                                                                                    </a>\
                                                                                    <span>\
                                                                                        <span style=font-size:9.0pt;font-family:Arial,sans-serif>\
                                                                                            <u></u>\
                                                                                            <u></u>\
                                                                                        </span>\
                                                                                    </span>\
                                                                                </p>\
                                                                            </td>\
                                                                            <td>\
                                                                                <span></span>\
                                                                            </td>\
                                                                        </tr>\
                                                                    </tbody>\
                                                                </table>\
                                                                <span></span>\
                                                                <p class=MsoNormal>\
                                                                    <span>\
                                                                        <u></u>\
                                                                        <u></u>\
                                                                    </span>\
                                                                </p>\
                                                            </td>\
                                                            <td>\
                                                                <span></span>\
                                                            </td>\
                                                        </tr>\
                                                    </tbody>\
                                                </table>\
                                                <span></span>\
                                            </td>\
                                            <td>\
                                                <span></span>\
                                            </td>\
                                        </tr>\
                                    </tbody>\
                                </table>\
                            </div>\
                            <span></span>\
                        </td>\
                        <td>\
                            <span></span>\
                        </td>\
                    </tr>\
                    <tr>\
                        <td style=background:#f7f7f7;padding:0in 0in 0in 0in>\
                            <div align=center>\
                                <table class=MsoNormalTable border=0 cellpadding=0>\
                                    <tbody>\
                                        <tr>\
                                            <td style=padding:.75pt .75pt .75pt 7.5pt>\
                                                <p class=MsoNormal>\
                                                    <span></span>\
                                                    <a href=https://www.facebook.com/NextWealth/ target=_blank>\
                                                        <span>\
                                                            <span style=text-decoration:none>\
                                                                <img border=0 width=20 height=27 style=width:.2083in;height:.2812in src=http://stats.headrun.com/images/facebook.png>\
                                                            </span>\
                                                        </span>\
                                                        <span></span>\
                                                    </a>\
                                                    <span>\
                                                        <u></u>\
                                                        <u></u>\
                                                    </span>\
                                                </p>\
                                            </td>\
                                            <td></td>\
                                            <td style=padding:.75pt .75pt .75pt 7.5pt>\
                                                <p class=MsoNormal>\
                                                    <span></span>\
                                                    <a href=https://twitter.com/NextWealth target=_blank>\
                                                        <span>\
                                                            <span style=text-decoration:none>\
                                                                <img border=0 width=20 height=27 style=width:.2083in;height:.2812in src=http://stats.headrun.com/images/twitter.png>\
                                                            </span>\
                                                        </span>\
                                                        <span></span>\
                                                    </a>\
                                                    <span>\
                                                        <u></u>\
                                                        <u></u>\
                                                    </span>\
                                                </p>\
                                            </td>\
                                            <td></td>\
                                            <td style=padding:.75pt .75pt .75pt 7.5pt>\
                                                <p class=MsoNormal>\
                                                    <span></span>\
                                                    <a href=https://www.linkedin.com/company-beta/3512470/?pathWildcard=3512470 target=_blank>\
                                                        <span>\
                                                            <span style=text-decoration:none>\
                                                                <img border=0 width=20 height=27 style=width:.2083in;height:.2812in src=http://stats.headrun.com/images/linkedin.png>\
                                                            </span>\
                                                        </span>\
                                                        <span></span>\
                                                    </a>\
                                                    <span>\
                                                        <u></u>\
                                                        <u></u>\
                                                    </span>\
                                                </p>\
                                            </td>\
                                            <td></td>\
                                        </tr>\
                                    </tbody>\
                                </table>\
                            </div>\
                            <span></span>\
                        </td>\
                        <td>\
                            <span></span>\
                        </td>\
                    </tr>\
                </tbody>\
            </table><br>\
            </body>\
            </html>"

    urls = "<div class=row>\
                <span>\
                    <a href=%s>\
                        <img id=fb_icon, src=http://stats.headrun.com/images/facebook.png\
                        alt=facebook_logo />\
                    </a>\
                </span>\
                <span>\
                    <a href=%s>\
                        <img id=tw_icon, src=http://stats.headrun.com/images/twitter.png\
                        alt=twitter_logo />\
                    </a>\
                </span>\
                <span>\
                    <a href=%s>\
                        <img id=li_icon, src=http://stats.headrun.com/images/linkedin.png\
                        alt=linkedin_logo />\
                    </a>\
                </span>\
            </div>\
            </body>\
            </html>" %("www.facebook.com/NextWealth/", "twitter.com/NextWealth", \
                    "https://www.linkedin.com/company-beta/3512470/?pathWildcard=3512470")
    mail_body = _text1 + _text2 + logo
    return mail_body