
from django.conf.urls import include, url 
from django.contrib import admin
from peoples_dashboard.views import *

urlpatterns = [ 
        url(r'^get_sla_data', get_sla_data),
        url(r'^get_peoples_data', get_peoples_data),
        url(r'^get_individual_target', get_individual_target),
    ]
