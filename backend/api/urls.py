from django.conf.urls import include, url
from django.contrib import admin
from api import views as apiviews

urlpatterns = [
    # Examples:
    url(r'^error_board',apiviews.error_insert),
    url(r'^upload/',apiviews.upload_new),
    url(r'^user_data/', apiviews.user_data),
    url(r'^from_to/', apiviews.from_to),
    url(r'^project/', apiviews.project),
    url(r'^chart_data/', apiviews.chart_data),
    url(r'^yesterdays_data/', apiviews.yesterdays_data),
    url(r'^dropdown_data/', apiviews.dropdown_data),
    url(r'^dropdown_data_types/', 'api.views.dropdown_data_types', name="dropdown_data_types"),
    url(r'^annotations/$', apiviews.get_annotations),
    url(r'^annotations/create/$', apiviews.add_annotation),
    url(r'^annotations/update/$', apiviews.update_annotation),
    url(r'^static_production_data/',apiviews.static_production_data),
    url(r'^change_password/', apiviews.change_password),
    url(r'^forgot_password/', apiviews.forgot_password),

]
