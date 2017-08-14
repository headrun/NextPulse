import json
from django.http import HttpResponse

def getHttpResponse(resp, error=0, status=200, content_type="application/json"):
    retVal = {"error": 0, "result": resp}
    if error:
        retVal = {"error": 1, "msg": resp}
    return HttpResponse(json.dumps(retVal), content_type, status)
