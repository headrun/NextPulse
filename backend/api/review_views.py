import calendar
import datetime
from collections import OrderedDict
from django.http import HttpResponse
from django.core.mail import EmailMultiAlternatives

from common.utils import getHttpResponse as json_HttpResponse
from api.models import *


def get_top_reviews(request):
    """ get list of reviews """
    search_term = request.GET.get('search', "")
    timeline = request.GET.get('timeline', "future")
    filter_param = {}
    try:
        rev_ids = ReviewMembers.objects.filter(member = request.user).values_list("review__id", flat = True)
        filter_param.update({'id__in' : rev_ids})
        if search_term:
            filter_param.update({'review_name__contains': search_term})
        if timeline == 'past':
            filter_param.update({'review_date__lt' :datetime.datetime.now()})
            search_param = "-review_date"
        else:
            filter_param.update({'review_date__gte' :datetime.datetime.now()})
            search_param = "review_date"

        rev_objs = Review.objects.filter( **filter_param).order_by(search_param)
        all_result = OrderedDict()
        user_id = request.user.id
        tl_objs = TeamLead.objects.filter(name = user_id)

        if tl_objs:
            is_team_lead = True
        else:
            is_team_lead = False

        color = {}
        i = 0
        colors = ['#3385E8', '#DD4130', '#27B678']
        for item in rev_objs:
            if i > 2:
                i = 0
            data = {}
            data['name'] = item.review_name
            review_date = item.review_date
            data['date'] = review_date.strftime("%d %b, %Y")
            date = review_date.strftime("%d_%b")
            data['time'] = review_date.strftime("%I:%M %p")
            data['id'] = item.id

            week_day = calendar.day_name[review_date.weekday()]
            key = date + "_" + week_day

            if key  not in all_result:

                all_result[key] = []
                color[key] = colors[i]
                i += 1
            data['color'] = color[key]
            data['is_team_lead'] = is_team_lead
            all_result[key].append(data)
        all_data = {'all_data': all_result, 'is_team_lead': is_team_lead}
        return json_HttpResponse(all_data)
    except:
        return json_HttpResponse("Failed")

def create_reviews(request):
    """ creating reviews """
    curdate = datetime.datetime.now()
    review_name = eval(request.POST['json']).get('reviewname', "")
    agenda =  eval(request.POST['json']).get('reviewagenda', "")
    _review_date = eval(request.POST['json']).get('reviewdate', '')
    review_type = eval(request.POST['json']).get('review_type', '')
    _venue = eval(request.POST['json']).get('venue', "")
    _bridge = eval(request.POST['json']).get('bridge', "")
    
    if not review_name or not agenda or not review_type or not _review_date:
        return json_HttpResponse('Mandatory Field Not present')
    
    _date = ' '.join(_review_date.split()[1:5]
    _id = eval(request.POST['json'])['track_id']

    user_id = request.user.id
    tl_objs = TeamLead.objects.filter(name = user_id)
    tl = ""
    project = ""
    if not tl_objs:
        return json_HttpResponse('User is not TeamLead')
    res = check_string(review_name)
    if not res:
        return HttpResponse("Improper File name")

    tl_obj = tl_objs[0]
    tl = tl_obj
    project = tl_obj.project
    try:
        review_date = datetime.datetime.strptime(_date, "%b %d %Y %H:%M:%S")
        if not _id:
            review_obj = Review.objects.create(project = project, review_name = review_name, review_date= review_date, team_lead = tl,
                            review_agenda = agenda, review_type = review_type, bridge = _bridge, venue = _venue)
        else:
            review_obj = Review.objects.filter(id = _id)
            ext_objs = Review.objects.filter(project = project, review_name = review_name, review_date__contains= review_date.date())\
                    .exclude(id = _id)
            if ext_objs:
                return json_HttpResponse("Review with same name already exist in same date.")
            if review_obj:
                review_obj = review_obj[0]
                review_obj.review_name = review_name
                review_obj.review_date = review_date
                review_obj.review_agenda = agenda
                review_obj.review_type = review_type
                review_obj.bridge = _bridge
                review_obj.venue = _venue
                review_obj.save()
        return json_HttpResponse(review_obj.id)
    except:
        return json_HttpResponse("Failed")

def get_review_details(request):
    """ getting detail of the review """
    from django.utils import timezone
    review_id = request.GET.get('review_id', "")
    rev_objs = Review.objects.filter(id = review_id)
    if not rev_objs:
        return json_HttpResponse('Failed')
    else:
        try:
            item = rev_objs[0]
            data = create_dict_data(item)
            data['rev_files'] = []
            review_date = item.review_date
            data['jq_date'] = review_date.strftime("%Y %m %d %H %M %S").split(" ")
            _df_time = review_date.date() - timezone.now().date()
            _df_time = _df_time.days
            if _df_time < 0:
                data['remained'] = "PAST"
            elif _df_time < 1:
                data['remained'] = "Today"
            elif _df_time < 2:
                data['remained'] = "Tomorrow"
            elif _df_time < 8:
                data['remained'] = "This Week"
            elif _df_time < 32:
                data['remained'] = "This Month"
            else:
                data['remained'] = ""

            users = Customer.objects.filter(project = item.project).values_list('name__first_name', flat = True)
            rev_fil_objs = ReviewFiles.objects.filter(review__id = item.id)
            for obj in rev_fil_objs:
                url = obj.file_name.url
                name = obj.original_file_name + "#" + str(obj.id)
                data['rev_files'].append({ 'name' : name, 'file_id': str(obj.id)})
            data['members'] = get_rel_users(item.id)
            return json_HttpResponse(data)
        except:
            return json_HttpResponse("Failed")

def get_rel_users(review_id):
    """ function to display all related users """
    all_users = []
    users = ReviewMembers.objects.filter(review__id = review_id)
    for user in users:
        name = user.member.first_name + " " + user.member.last_name
        _id = user.id
        all_users.append({'name': name, 'id': _id})
    return all_users

def remove_attachment(request):
    """ API to delete atachments from reviews """
    term_type = request.GET.get('term_type', '')
    revies_file_id = request.GET.get('file_id', '')
    if not revies_file_id or not term_type:
        return json_HttpResponse("ID not given")

    try:
        if term_type == "attachment":
            table = "ReviewFiles"
        elif term_type == "member":
            table = "ReviewMembers"
        elif term_type == "review":
            table = "Review"

        objs = eval(table).objects.filter(id = revies_file_id)
        if term_type != "review":
            rev_id = objs[0].review.id
            res = {'rev_id': rev_id}
        else:
            obj = objs[0]
            users = ReviewMembers.objects.filter(review = obj)
            data = create_dict_data(obj)
            for user in users:
                send_review_mail(data, 'deleted', user)

            rev_id = "success"
            res = {'status': rev_id}
        objs.delete()
        return json_HttpResponse(res)
    except:
        return json_HttpResponse("Failed")

def upload_review_doc(request):
    """ to upload the review documents """
    attach_files = request.FILES.getlist('myfile', "")
    review_id = request.POST.get('review_id', "")
    try:
        if not attach_files or not review_id:
            return json_HttpResponse('Improper data')

        r_obj = Review.objects.get(id = review_id)
        for item in attach_files:
            res = check_string(item.name)
            if not res:
                return HttpResponse("Improper File name")
            original_file_name = item.name
            name = item.name.split(".")
            item.name = "%s_%s_%s.%s" %(name[0], r_obj.review_name.lower().replace(" ", "_"), str(r_obj.review_date.date()), name[-1])
            rev_fil_objs = ReviewFiles.objects.filter(original_file_name = original_file_name, review = r_obj)
            if rev_fil_objs:
                rfo = rev_fil_objs[0]
                rfo.file_name = item
                rfo.save()
            else:
                rfo, created = ReviewFiles.objects.get_or_create(file_name = item, review = r_obj,
                defaults = {'original_file_name': original_file_name})

        return json_HttpResponse(review_id)
    except:
        return json_HttpResponse("Failed")

def check_string(word):
    """ Check the string is proper or not"""
    result = True
    symbol = "~`!@#$%^&*+={}[]:>;,</?*+"
    for i in word:
        if i in symbol:
           result = False
           return result
    return result
    
def get_related_user(request):
    """ Get all the users Related to that project """
    user_id = request.user.id
    tl_objs = TeamLead.objects.filter(name = user_id)
    tl = ""
    project = ""
    result_data = {'name_list' : [], 'id_list' : []}
    if not tl_objs:
        return json_HttpResponse('User is not TeamLead')
    tl_obj = tl_objs[0]
    project = tl_obj.project
    center = tl_obj.center

    nxtwlth_managers = Nextwealthmanager.objects.all()
    if nxtwlth_managers:
        for nxtwlth_manager in nxtwlth_managers:
            _name = nxtwlth_manager.name.first_name + " " + nxtwlth_manager.name.last_name
            result_data['name_list'].append(_name)
            result_data['id_list'].append(nxtwlth_manager.name.id)

    tls = TeamLead.objects.filter(project = project, center = center).exclude(id = tl_obj.id)
    if tls:
        for tl in tls:
            _name = tl.name.first_name + " " + tl.name.last_name
            result_data['name_list'].append(_name)
            result_data['id_list'].append(tl.name.id)

    customers = Customer.objects.filter(project = project, center = center)
    if customers:
        for customer in customers:
            _name = customer.name.first_name + " " + customer.name.last_name
            result_data['name_list'].append(_name)
            result_data['id_list'].append(customer.name.id)

    centermanagers = Centermanager.objects.filter(center = center)
    if centermanagers:
        for centermanager in centermanagers:
            _name = centermanager.name.first_name + " " + centermanager.name.last_name
            result_data['name_list'].append(_name)
            result_data['id_list'].append(centermanager.name.id)

    return json_HttpResponse(result_data)


def saving_members(request):
    """ saving members to DB """
    data = request.POST.get('json', "")
    data = json.loads(data)
    review_id = data.get("review_id", "")
    users = data.get('uids', "")

    if not review_id:
        return json_HttpResponse("Improper Data")

    rev_objs = Review.objects.filter(id = review_id)

    if not rev_objs:
        return json_HttpResponse("Wrong Review ID")

    item = rev_objs[0]
    data = create_dict_data(item)
    _users = [request.user.id] + users
    users = User.objects.filter(id__in = _users)
    existing_member_objs = ReviewMembers.objects.filter(review = item)
    existing_members = existing_member_objs.values_list('member__id', flat = True)
    _remove_member = list(set(existing_members) - set(_users))
    if _remove_member:
        for r in _remove_member:
            memb_obj = ReviewMembers.objects.get(member__id = r, review = item)
            send_review_mail(data, 'deleted', memb_obj)
            memb_obj.delete()
    for uid in users:
        try:
            exs_mem_obj = ReviewMembers.objects.filter(review = item, member = uid)
            if not exs_mem_obj:
                memb_obj = ReviewMembers.objects.create(review = item, member = uid)
                send_review_mail(data, 'created', memb_obj)
            else:
                send_review_mail(data, 'edited', exs_mem_obj[0])
        except:
            pass

    return json_HttpResponse("Success")

def send_review_mail(data, task, memb_obj = ""):
    """mail sending module for review"""
    process = {
        'created' : "Our Review is organised with given details",
        'edited' : "Our Review is updated with given details",
        'deleted': "Our Review is deleted with given details",
        'reminder' : "It is a reminder for our review with given details"
        }
    try:
        if memb_obj:
            _text = "Hi %s %s, <p> %s </p>" %( memb_obj.member.first_name, memb_obj.member.last_name, process[task])
        else:
            _text = "Hi %s, %s, <p> %s </p>" %("Abhishek", "Yeswanth", process[task] )

        mail_body = create_mail_body(_text, data)
        to = ['yeswanth@headrun.com', 'abhishek@headrun.com']
        to.append(memb_obj.member.email)
        msg = EmailMultiAlternatives("%s - %s Review for NextWealth - %s" % (task.upper(), data['review_type'], data['project']), "",
                'nextpulse@nextwealth.in', to)
        msg.attach_alternative(mail_body, "text/html")

        msg.send()
    except:
        pass
    
def create_dict_data(item):
    """ create review dictionary from object """
    data = {}
    data['review_type'] = item.review_type
    data['name'] = item.review_name
    data['agenda'] = item.review_agenda
    review_date = item.review_date
    data['project'] = item.project.name
    data['day'] = review_date.strftime("%A")
    data['date'] = review_date.strftime("%d %b %Y")
    data['time'] = review_date.strftime("%I:%M %p")
    data['venue'] = item.venue
    data['bridge'] = item.bridge
    data['tl']   = item.team_lead.name.first_name+ " " + item.team_lead.name.last_name
    return data

def create_mail_body(text, data):
    """ create mail box to send """
    mail_body = "<html>\
            <head>\
                <style>\
                table {\
                    font-family: arial, sans-serif;\
                    border-collapse: collapse;\
                    width: 50%;\
                }\
                td, th {\
                    border: 1px solid #dddddd;\
                    text-align: center;\
                    padding: 8px;\
                }\
                tr:nth-child(even) {\
                    background-color: #dddddd;\
                }\
                </style>\
            </head>\
            <body>\
                <table align= 'center'>"

    _time  = "<tr>\
                <td>\
                <label> <b>Time </b></label>\
                </td>\
                <td>\
                  %s\
                </td>\
                </tr>" % data['time']

    _date = "<tr>\
             <td>\
             <label> <b>Date </b></label>\
             </td>\
             <td>\
              %s, %s\
             </td>\
             </tr>" % (data['date'], data['day'])

    _day = "<tr>\
            <td>\
            <label> <b>Day </b></label>\
            </td>\
            <td>\
             %s\
            </td>\
            </tr>" % data['day']

    _name = "<tr>\
             <td>\
             <label> <b>Name </b></label>\
             </td>\
             <td>\
              %s\
             </td>\
             </tr>" % data['name']

    _venue = "<tr>\
             <td>\
             <label> <b>Venue </b></label>\
             </td>\
             <td>\
              %s\
             </td>\
             </tr>" % data['venue']

    _bridge = "<tr>\
             <td>\
             <label> <b>Bridge </b></label>\
             </td>\
             <td>\
              %s\
             </td>\
             </tr>\
             </table> </br> </br>" % data['bridge']

    _agenda = " <tr>\
                <td>\
                <b>Agenda </b>\
                </td>\
                <td>\
                %s\
                </td>\
                </tr>" % data['agenda']

    extra = "<p> </p> <p> </p> Kindly log into NextPulse - http://nextpulse.nextwealth.in/ \
            with your userid and password to view all the metrics ahead of the meeting.\
            <p>Additional documents for the review can be found in the Review Section of the NextPulse itself. </p>\
            <p>If you have any difficulty please reach to your Project Team Lead (%s). </p> \
            <p> </p>\
            <p>Thanks and Regards,</p>\
            <p>NextPulse Team</p>\
            </body>\
        </html>" %(data['tl'])

    text +=  mail_body + _date + _time + _name + _agenda + _venue + _bridge + extra
    return text

def download_attachments(request):
    """ Downloading attachment for reviews """
    doc_id = request.GET.get("doc_id", "")
    if not doc_id:
        return json_HttpResponse("ID is not sent")

    rev_fil_objs = ReviewFiles.objects.filter(id = doc_id)
    obj = rev_fil_objs[0]

    with open(obj.file_name.path, 'r') as x:
        data = x.read()
    response = HttpResponse(data, content_type='application/force-download')
    response['Content-Disposition'] = "attachment; filename= %s" % (obj.original_file_name)
    return response



