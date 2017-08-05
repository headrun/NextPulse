
from django.db import models
from api import models as api_models


class ColorCoding(models.Model):
    project = models.ForeignKey(
        api_models.Project, db_index=True, related_name='projects_color_codings')
    widget = models.ForeignKey(
        api_models.Project, db_index=True, related_name='widgets_color_codings')
    month = models.CharField(max_length=255)
    hard_limit = models.FloatField(null=True, blank=True, default=0.0)
    soft_limit = models.FloatField(null=True, blank=True, default=0.0)
    created_at  = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

