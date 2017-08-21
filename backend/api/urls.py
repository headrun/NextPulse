from django.conf.urls import include, url
from django.contrib import admin
from api import views as apiviews
from api import review_views

urlpatterns = [
    # Examples:
    url(r'^error_board',apiviews.error_insert),
    url(r'^upload/',apiviews.upload_new),
    url(r'^user_data/', apiviews.user_data),
    url(r'^from_to/', apiviews.from_to),
    url(r'^project/', apiviews.project),
    url(r'^chart_data/', apiviews.chart_data),
    #url(r'^yesterdays_data/', apiviews.yesterdays_data),
    url(r'^dropdown_data/', apiviews.dropdown_data),
    url(r'^dropdown_data_types/', apiviews.dropdown_data_types, name="dropdown_data_types"),
    url(r'^annotations/$', apiviews.get_annotations),
    url(r'^annotations/create/$', apiviews.add_annotation),
    url(r'^annotations/update/$', apiviews.update_annotation),
    url(r'^static_production_data/',apiviews.static_production_data),
    url(r'^change_password/', apiviews.change_password),
    url(r'^forgot_password/', apiviews.forgot_password),
    url(r'^utilisation_all', apiviews.utilisation_all),
    url(r'^productivity', apiviews.productivity),
    url(r'^cate_error', apiviews.cate_error),
    url(r'^pareto_cate_error', apiviews.pareto_cate_error),
    url(r'^agent_cate_error', apiviews.agent_cate_error),
    url(r'^alloc_and_compl', apiviews.alloc_and_compl),
    url(r'^prod_avg_perday', apiviews.prod_avg_perday),
    url(r'^main_prod', apiviews.main_prod),
    url(r'^fte_graphs', apiviews.fte_graphs),
    url(r'^monthly_volume', apiviews.monthly_volume),
    url(r'^error_bar_graph', apiviews.error_bar_graph),
    url(r'^pre_scan_exce',apiviews.pre_scan_exce),
    url(r'^nw_exce', apiviews.nw_exce),
    url(r'^overall_exce', apiviews.overall_exce),
    url(r'^upload_acc', apiviews.upload_acc),
    url(r'^err_field_graph',apiviews.err_field_graph),
    url(r'^tat_data',apiviews.tat_data),
    url(r'^get_packet_details', apiviews.get_packet_details),
    
    url(r'^get_top_reviews',review_views.get_top_reviews),
    url(r'^create_reviews',review_views.create_reviews),
    url(r'^get_review_details',review_views.get_review_details),
    url(r'^remove_attachment',review_views.remove_attachment),
    url(r'^upload_review_doc',review_views.upload_review_doc),
    url(r'^get_related_user',review_views.get_related_user),
    url(r'^saving_members',review_views.saving_members),
    url(r'^download_attachments',review_views.download_attachments),

]
