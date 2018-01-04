from django.conf.urls import include, url 
from django.contrib import admin
from voice_service import views as voice_serviceviews

urlpatterns = [ 
        url(r'^voice_upload/',voice_serviceviews.voice_upload),
        url(r'^location_data/', voice_serviceviews.location_data),
        url(r'^skill_data/', voice_serviceviews.skill_data),
        url(r'^disposition_data/', voice_serviceviews.disposition_data),
        url(r'^call_status_data/', voice_serviceviews.call_status_data)
    ]   

