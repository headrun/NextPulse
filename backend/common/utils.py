import json
from django.http import HttpResponse

def getHttpResponse(resp, error=0, status=200, content_type="application/json"):

  retVal = None

  if error:
    retVal = {"error": 1,\
              "msg"  : resp}
  else:
    retVal = {"error" : 0,\
              "result": resp}

  resp = json.dumps(retVal)

  return HttpResponse(resp, content_type, status)
