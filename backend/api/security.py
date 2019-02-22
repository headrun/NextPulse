# from api.review_views import get_all_related_user
from api.models import *

def get_permitted_user(project, center, user):
    """Check whether the user is permitted for the project or not
    """
    var = 'Valid User'
    if project and center:
        user_dict = get_all_related_user(project, center)
        if user not in user_dict['id_list']:
            var = 'Invalid User'
        if Project.objects.filter(id=project,display_project = True).count() == 0:
            var = 'Invalid User'
    return var




def get_all_related_user(project, center, tl_obj=''):
    result_data = {'name_list' : [], 'id_list' : []}
    nxtwlth_managers = Nextwealthmanager.objects.all()
    if nxtwlth_managers:
        for nxtwlth_manager in nxtwlth_managers:
            _name = nxtwlth_manager.name.first_name + " " + nxtwlth_manager.name.last_name
            result_data['name_list'].append(_name)
            result_data['id_list'].append(nxtwlth_manager.name.id)

    if tl_obj:
        tls = TeamLead.objects.filter(project__id = project, center__id = center).exclude(id = tl_obj.id)
    else:
        tls = TeamLead.objects.filter(project__id = project, center__id = center)

    if tls:
        for tl in tls:
            _name = tl.name.first_name + " " + tl.name.last_name
            result_data['name_list'].append(_name)
            result_data['id_list'].append(tl.name.id)

    customers = Customer.objects.filter(project__id = project, center__id = center)
    if customers:
        for customer in customers:
            _name = customer.name.first_name + " " + customer.name.last_name
            result_data['name_list'].append(_name)
            result_data['id_list'].append(customer.name.id)

    centermanagers = Centermanager.objects.filter(center__id = center)
    if centermanagers:
        for centermanager in centermanagers:
            _name = centermanager.name.first_name + " " + centermanager.name.last_name
            result_data['name_list'].append(_name)
            result_data['id_list'].append(centermanager.name.id)
    return result_data
