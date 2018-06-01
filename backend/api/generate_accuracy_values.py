
import datetime
from email.MIMEImage import MIMEImage

from django.db.models import Sum,Max
from django.core import mail
from django.core.mail import send_mail, BadHeaderError
from django.core.mail import EmailMessage

from api.models import *

def send_mail_data(user_details, user, user_group):

    user_data = User.objects.filter(id=user.name_id)
    user_name = user_data[0].first_name
    _text1 = "Dear %s, <p>Below is a snapshot of  'Target'  and  'Actual'  values of SLA/KPI.</p>"\
                    % (user_name)

    mail_data = ''
    prj_count = []
    for data in user_details:
        project = data
        is_send_mail = Project.objects.get(id=project).is_enable_push
        if (is_send_mail):
            result = generate_targets_data(project)
            project_name = Project.objects.get(id=project).name
            date = RawTable.objects.filter(project=project).aggregate(Max('date'))
            mail_data = mail_data + '<html></br></html>' + "%s"%(project_name) + generate_mail_table_format(result, project, date, user_group)
            prj_count.append(project)
    if len(prj_count) >= 1:
        dashboard_url = "https://nextpulse.nextwealth.in"
        mail_logos = generate_logos_format(dashboard_url)
        mail_body = _text1 + mail_data + mail_logos
        to = [user_data[0].email]
        msg = EmailMessage("NextPulse KPI/SLA Report", mail_body, 'nextpulse@nextwealth.in', to)
        msg.content_subtype = "html"
        msg.send()

    return "success"


def generate_targets_data(project):
    
    result = {}
    date_query = RawTable.objects.filter(project_id=project).aggregate(Max('date'))
    last_date = str(date_query['date__max'])
    rawtable_query = RawTable.objects.filter(project=project, date=last_date).aggregate(Sum('per_day'))
    production_value = rawtable_query['per_day__sum']
    target_query = Targets.objects.filter(\
                    project=project,from_date__lte=last_date,target_method='SLA', \
                    to_date__gte=last_date,target_type='Productivity').values_list('target_value',flat=True)
    headcount_data = Headcount.objects.filter(project=project,date=last_date).aggregate(Sum('billable_agents'))
    agent_data = 0
    if not headcount_data['billable_agents__sum'] == None:
        agent_data = headcount_data['billable_agents__sum']
    prod_target_value = 0
    if target_query:
        prod_target_value = target_query
    if agent_data != 0:
        productivity = float('%.2f' % round(float(production_value)/float(agent_data),2))
    else:
        productivity = 0
    color = 'black'
    if production_value < prod_target_value:
        color = 'Red'
    target_method = 'KPI'
    table_name = Internalerrors
    internal_data = generate_internal_and_external_values(\
                    project, table_name, last_date, production_value, target_method)
    result.update({'internal_target': internal_data['target'], 'internal_actual': internal_data['accuracy'],\
    'internal_color': internal_data['color']})
    target_method = 'SLA'
    table_name = Externalerrors
    external_data = generate_internal_and_external_values(\
                    project, table_name, last_date, production_value, target_method)
    result.update({'external_target': external_data['target'], 'external_actual': external_data['accuracy'],\
    'external_color': external_data['color']})
    result.update({'prod_target': prod_target_value, 'prod_actual': production_value,\
    'prod_color': color})
    aht_check = AHTTeam.objects.filter(project=project,date=last_date).aggregate(Sum('AHT'))
    tat_check = TatTable.objects.filter(project=project,date=last_date)
    met_cnt = tat_check.aggregate(Sum('met_count'))
    not_met = tat_check.aggregate(Sum('non_met_count'))
    if aht_check != None:
        aht_data = generate_aht_data(project,last_date,aht_check)
        result.update({'aht_target':aht_data['target'],'aht':aht_data['aht'],'aht_color':aht_data['color']})
    if met_cnt['met_count__sum'] != None:
        tat_data = generate_tat_data(project,met_cnt,not_met,last_date)
        result.update({'tat_target':tat_data['target'],'tat':tat_data['tat'],'tat_color':tat_data['color']})
    return result


def generate_internal_and_external_values(project,table_name,date,production,target_method):
    
    result = {}
    audited_errors = table_name.objects.filter(project=project, date=date).aggregate(Sum('audited_errors'))
    total_errors = table_name.objects.filter(project=project, date=date).aggregate(Sum('total_errors'))
    agent_count = table_name.objects.filter(project=project, date=date).values('employee_id').count()
    audited_count = audited_errors['audited_errors__sum'] 
    errors_count = total_errors['total_errors__sum']
    target_query = Targets.objects.filter(\
                    project=project, from_date__lte=date, to_date__gte=date, \
                    target_method=target_method).aggregate(Sum('target_value'))
    target_value = target_query['target_value__sum']
    if errors_count >= 0 and audited_count > 0:
        accuracy_value = 100 - (float(errors_count)/float(audited_count))*100
        accuracy_value = float('%.2f' % round(accuracy_value, 2))
    elif errors_count >= 0 and audited_count == None:
        accuracy_value = 100 - (float(errors_count)/float(production))*100
        accuracy_value = float('%.2f' % round(accuracy_value, 2))
    elif errors_count == None and audited_count == None and agent_count == 0:
        target_value = target_value
        accuracy_value = 0
    if (target_value > accuracy_value) and (agent_count > 0):
        target = target_value
        accuracy = accuracy_value
        color = 'Red'
    elif (target_value < accuracy_value) and (agent_count > 0):
        target = target_value
        accuracy = accuracy_value
        color = 'black'
    elif target_value == None and accuracy_value > 0:
        target = 'No data'
        accuracy = accuracy_value
        color = 'black'
    elif agent_count == 0 and target_value > 0:
        target = target_value
        accuracy = 'No data'
        color = 'black'
    elif agent_count == 0 and target_value == None:
        target = 'No data'
        accuracy = 'No data'
        color = 'black'

    result['target'] = target
    result['accuracy'] = accuracy
    result['color'] = color
    return result


def generate_aht_data(project,date,aht_value):

    result = {}
    aht_value = aht_value['AHT__sum']
    target_value = Targets.objects.filter(project=project,from_date__lte=date,to_date__gte=date,\
                    target_type='AHT').aggregate(Sum('target_value'))
    target_value = target_value['target_value__sum']
    if target_value > aht_value:
        result['target'] = target_value
        result['aht'] = aht_value
        result['color'] = 'Red'
    elif target_value < aht_value:
        result['target'] = target_value
        result['aht'] = aht_value
        result['color'] = 'black'
    elif target_value == None:
        result['target'] = target_value
        result['aht'] = aht_value
        result['color'] = 'black'
    return result


def generate_tat_data(project,met_cnt,not_met,date):

    result = {}
    target_value = Targets.objects.filter(project=project,from_date__lte=date,to_date__gte=date,\
                    target_type='TAT').aggregate(Sum('target_value'))
    met_val = met_cnt['met_count__sum']
    not_met_val = not_met['non_met_count__sum']
    value = (float(met_val) /float(met_val + not_met_val))*100
    value = float('%.2f' % round(value, 2))
    target = target_value['target_value__sum']
    if target > value:
        target = target
        tat_val = value
        color = 'Red'
    elif target < value:
        target = target
        tat_val = value
        color = 'black'
    elif target == None:
        target = 'No data'
        tat_val = value
        color = 'black'

    result['tat'] = tat_val
    result['target'] = target
    result['color'] = color
    return result


def generate_mail_table_format(result, project, date, user_group):

    date = date['date__max']

    aht_data = AHTTeam.objects.filter(project=project,date=date).values('AHT').count()

    tat_data = TatTable.objects.filter(project=project,date=date).values('met_count').count()

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
                        <table align='center' border='1'>"
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
                </tr>" % (result['external_target'], result['external_color'], result['external_actual'])

    if aht_data and tat_data:
        fourth_row = "<tr>\
                        <td>AHT</td>\
                        <td>%s</td>\
                        <td><font color=%s>%s</font></td>\
                    </tr>" % (result['aht_target'], result['aht_color'], result['aht'])
        fifth_row = "<tr>\
                        <td>TAT</td>\
                        <td>%s</td>\
                        <td><font color=%s>%s</font></td>\
                    </tr>\
                    </table>" % (result['tat_target'], result['tat_color'], result['tat'])
    elif aht_data:
        sixth_row = "<tr>\
                        <td>AHT</td>\
                        <td>%s</td>\
                        <td><font color=%s>%s</font></td>\
                    </tr>\
                    </table>" % (result['aht_target'], result['aht_color'], result['aht'])
    elif tat_data:
        seventh_row = "<tr>\
                        <td>TAT</td>\
                        <td>%s</td>\
                        <td><font color=%s>%s</font></td>\
                    </tr>\
                    </table>" % (result['tat_target'], result['tat_color'], result['tat'])
    body =  "</body>\
             </html>"
    if aht_data and tat_data and user_group != 'customer':
        _text = mail_body + headers + first_row + second_row + third_row + fourth_row + fifth_row + body
    elif aht_data and user_group != 'customer':
        _text = mail_body + headers + first_row + second_row + third_row + sixth_row + body
    elif tat_data and user_group != 'customer':
        _text = mail_body + headers + first_row + second_row + third_row + seventh_row + body
    elif user_group != 'customer':            
        _text = mail_body + headers + first_row + second_row + third_row + body
    else:
        _text = mail_body + headers + first_row + third_row + body
    return _text


def generate_logos_format(dashboard_url):

    _text1 = "<html>\
              <body>"
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