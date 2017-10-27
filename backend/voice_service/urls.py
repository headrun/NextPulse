from django.conf.urls import include, url 
from django.contrib import admin
from voice_service import views as voice_serviceviews

urlpatterns = [ 
        url(r'^voice_upload/',voice_serviceviews.voice_upload)
    ]   

