
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
import os

from email.MIMEImage import MIMEImage


from api.generate_accuracy_values import generate_internal_and_external_values, generate_targets_data

class Command(BaseCommand):


    commands = ['target_met_report',]
    args = '[command]'
    help = 'generating target met report for production and accuracy'

    def handle(self, *args, **options):

        from django.core import mail
        from django.core.mail import send_mail, BadHeaderError
        from django.core.mail import EmailMessage
        from django.db.models import Max, Sum
        from api.models import Project,Center,RawTable,TeamLead,Customer
        import datetime


        result = {}
        mail_body = ''
        projects = Project.objects.all()
        not_req = ["Nextgen", "Quarto", "Bridgei2i", "3i VAPP", "E4U", "Webtrade"]
        projects_list = filter(lambda x: x.name not in not_req, list(projects))
        projects_list = projects_list[:1]
        yesterday_date = datetime.datetime.now() - datetime.timedelta(days=1)
        for project in projects_list:
            max_date = RawTable.objects.filter(project=project.id).aggregate(Max('created_at'))
            center = Center.objects.filter(project=project.id).values_list('name', flat=True)
            center = center[0]
            tls = TeamLead.objects.filter(project=project).values_list('name', flat=True)[:1]
            customers = Customer.objects.filter(project=project).values_list('name', flat=True)
            name = center+'-'+project.name
            dashboard_url = "http://stats.headrun.com/#!/page1/"+center+"%20-%20"+project.name
            result = generate_targets_data(project)
            for tl in tls:
                tl_id = User.objects.filter(id=tl)
                tl_email = tl_id[0].email
                _text1 = "Dear %s, <p>Below is a snapshot of  'Target'  and  'Actual'  values of SLA/KPI.</p>"\
                        % (tl_id[0].first_name)

                mail_body = "<html>\
                                <head>\
                                    <style>\
                                        table {\
                                            font-family: arial, sans-serif;\
                                            border-collapse: collapse;\
                                            width: 50%;\
                                        }\
                                        td, th {\
                                            text-align: center;\
                                            padding: 8px;\
                                        }\
                                        tr:nth-child(even) {\
                                            background-color: #dddddd;\
                                        }\
                                        img {\
                                            width: 20%;\
                                            height: 25%;\
                                        }\
                                        span>a>img {\
                                            width: 4%;\
                                            height: 9%;\
                                        }\
                                        span>a {\
                                            margin-right: 10%;\
                                            color: white !important;\
                                        }\
                                    </style>\
                                </head>\
                                <body>\
                                <table align='center'>"
                headers = "<tr>\
                                <th>Name</th>\
                                <th>Target</th>\
                                <th>Actual</th>\
                             </tr>"
                first_row = "<tr>\
                                <td>Production</td>\
                                <td>%s</td>\
                                <td><font color=%s>%s</font></td>\
                            </tr>" % (result['prod_target'], result['prod_color'], result['prod_actual'])
                second_row = "<tr>\
                                <td>Internal Accuracy</td>\
                                <td>%s</td>\
                                <td><font color=%s>%s</font></td>\
                             </tr>" % (result['internal_target'], result['internal_color'], result['internal_actual'])
                third_row = "<tr>\
                                <td>External Accuracy</td>\
                                <td>%s</td>\
                                <td><font color=%s>%s</font></td>\
                            </tr>\
                        </table>" % (result['external_target'], result['external_color'], result['external_actual'])

                _text2 = "<p> For further details on metrics and graphs click on NextPulse link  %s"\
                         "<br>\
                         <p>Thanks and Regards</p>\
                         <p>NextPulse Team-NextWealth Entrepreneurs Pvt Ltd</p>" % dashboard_url

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
                                                                                                <img width=9 height=18 style=width:.125in;height:.2083in src=http://stats.headrun.com/images/location.png>\
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
                                                                                                <img width=9 height=18 style=width:.125in;height:.2083in src=http://stats.headrun.com/images/office.png>\
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
                mail_body = _text1 + mail_body + headers + first_row + second_row + third_row + _text2 + logo
                #to = [tl_email, "kannan.sundar@nextwealth.in", "poornima.mitta@nextwealth.in", "rishi@headrun.com"]
                to = [tl_email]
                msg = EmailMessage("NextPulse KPI/SLA Report", mail_body, 'nextpulse@nextwealth.in', to)
                msg.content_subtype = "html"
                msg.send()
