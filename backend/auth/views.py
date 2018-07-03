import json
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import authenticate, login as authLogin,\
                                logout as authLogout

from decorators import loginRequired
from common.utils import getHttpResponse as HttpResponse
from common.decorators import allowedMethods
from api.models import *

def Get_Projects_Count(user):
  user_group = user.groups.values_list('name', flat=True)[0]
  user_group_id = Group.objects.filter(name=user_group).values_list('id', flat=True)
  if user_group == 'team_lead':
      table_name = TeamLead
  elif user_group == 'customer':
      table_name = Customer 
  elif user_group == 'nextwealth_manager':
      return 2;
  customer_objs = table_name.objects.filter(name_id=user.id,project__display_project = True)
  project_list = customer_objs.values_list('project', flat =True)
  return len(project_list)



def getRoles (user):
  return [group.name for group in user.groups.all()]

def getUserData(user):

  return {"userId"   : user.id,\
          "userName" : user.username,\
          "firstName": user.first_name,\
          "lastName" : user.last_name,\
          "email"    : user.email,
          "roles": getRoles(user)}

@allowedMethods(["POST"])
def login(request):

  username = request.POST.get("username")
  password = request.POST.get("password")

  if not username and not password:
    body = request.body

    try:
      body = json.loads(body)
      username = body.get("username")
      password = body.get("password")

    except ValueError:
      pass

  user = authenticate(username=username, password=password)

  resp = None

  if user is not None:

    if user.is_active:
      if Get_Projects_Count(user) != 0:
        authLogin(request, user)
        resp = HttpResponse(getUserData(user))
      else:
        resp = HttpResponse("Projects Not Available", error=1, status=401)  

    else:
      resp = HttpResponse("User Not Active", error=1, status=401)

  else:
    resp = HttpResponse("Invalid Credentials", error=1, status=401)
    
  return resp

@allowedMethods(["GET"])
@loginRequired
def logout(request):

  authLogout(request)

  return HttpResponse("logged out")

@ensure_csrf_cookie
def status(request):

  if request.user.is_authenticated():
    return HttpResponse({"user": getUserData(request.user)})

  return HttpResponse("Invalid Login")
