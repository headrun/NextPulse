from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from models import *


@receiver(post_save, sender=TeamLead)
def set_agent(sender, instance, **kwargs):
    """
    widgets_list = [ 'Productivity Trends', 'Internal Accuracy', 'External Accuracy', 'Internal Error Types', 'External Error Types' ]
    widgets_objs = Widgets.objects.filter(name__in=widgets_list)
    for obj in widgets_objs:
        a = Widget_Mapping(widget_priority=1,is_display=True,is_drilldown=False,widget_name_id=obj.id,user_name_id=instance.id)
        a.save()
        print 'added'+obj.name
    """
    user_obj = User.objects.filter(username=instance.name).values_list('id', flat=True)
    group_obj = Group.objects.get(name='team_lead')
    group_obj.user_set.add(user_obj[0])


@receiver(post_save, sender=Customer)
def set_customer(sender, instance, **kwargs):
    user_obj = User.objects.filter(username=instance.name).values_list('id', flat=True)
    group_obj = Group.objects.get(name='customer')
    group_obj.user_set.add(user_obj[0])

@receiver(post_save, sender=Centermanager)
def set_centermanager(sender, instance, **kwargs):
    user_obj = User.objects.filter(username=instance.name).values_list('id', flat=True)
    group_obj = Group.objects.get(name='Center_Manager')
    group_obj.user_set.add(user_obj[0])


@receiver(post_save, sender=Nextwealthmanager)
def set_nextwealthmanager(sender, instance, **kwargs):
    user_obj = User.objects.filter(username=instance.name).values_list('id', flat=True)
    group_obj = Group.objects.get(name='Nextwealth_Manager')
    group_obj.user_set.add(user_obj[0])
