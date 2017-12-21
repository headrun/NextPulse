import datetime
from django.db.models import Max
from django.shortcuts import redirect
from api.models import *
from api.basics import latest_dates
from api.security import get_permitted_user
from common.utils import getHttpResponse as json_HttpResponse

def project(request):

    try:
        multi_center, multi_project = request.GET.get('name').split(' - ')
    except: 
        multi_center, multi_project = '',''
    try:
        project_vals = Project.objects.filter(name=multi_project).values_list('id','center_id')
        _project, _center = project_vals[0][0], project_vals[0][1]
    except:
        _project, _center = '', ''

    user_group = request.user.groups.values_list('name', flat=True)[0]
    user_group_id = Group.objects.filter(name=user_group).values_list('id', flat=True)
    list_wid = []
    layout_list = []
    final_dict = {}

    if 'team_lead' in user_group:
        
        team_lead_obj = TeamLead.objects.filter(name_id=request.user.id).values_list('center', 'project')
        center, prj_id = [],[]
        for item in team_lead_obj:
            center.append(item[0])
            prj_id.append(item[1])
        """
        team_lead_obj = TeamLead.objects.filter(name_id=request.user.id)
        center = team_lead_obj.values_list('center', flat=True)
        prj_id = team_lead_obj.values_list('project', flat=True)
        """
    if 'customer' in user_group:
        select_list = []
        details = {}      
        customer_objs = Customer.objects.filter(name_id=request.user.id)
        center_list = customer_objs.values_list('center', flat = True)
        project_list = customer_objs.values_list('project', flat =True)
        #center_list = Customer.objects.filter(name_id=request.user.id).values_list('center')
        #project_list = Customer.objects.filter(name_id=request.user.id).values_list('project')
        if (len(center_list) & len(project_list)) == 1:
            select_list.append('none')
        if len(center_list) < 2:  
            #center_name = str(Center.objects.filter(id=center_list[0][0])[0])
            center_name = str(Center.objects.filter(id=center_list[0])[0])
            for project in project_list:
                #project_name = str(Project.objects.filter(id=project[0])[0])
                project_name = str(Project.objects.filter(id=project)[0])
                vari = center_name + ' - ' + project_name
                select_list.append(vari)
        elif len(center_list) >= 2:
            for center in center_list:
                #center_name = str(Center.objects.filter(id=center[0])[0])
                center_name = str(Center.objects.filter(id=center)[0])
                for project in project_list:
                    #project_name = str(Project.objects.filter(id=project[0])[0])
                    project_name = str(Project.objects.filter(id=project)[0])
                    select_list.append(center_name + ' - ' + project_name) 
        details['list'] = select_list

        if len(select_list) > 1:
              if multi_project:
                 prj_id = Project.objects.filter(name=multi_project).values_list('id','center_id')
              else:
                 prj_name = select_list[1].split(' - ')[1]
                 prj_id = Project.objects.filter(name=prj_name).values_list('id','center_id') 


    if 'nextwealth_manager' in user_group:
        select_list = []
        center_list = Nextwealthmanager.objects.filter(name_id=request.user.id).values_list('center', flat=True)
        if center_list.count() < 2:
            center_obj = Center.objects.filter(id=center_list[0])[0]
            center_name, center_id = center_obj.name, center_obj.id
            project_list = Project.objects.filter(center_id=center_id)
            for project in project_list:
                project_name = str(project)
                select_list.append(project_name)

        elif center_list.count() >= 2:
            for center in center_list:
                center_query = Center.objects.filter(id=center)
                #center_name = str(Center.objects.filter(id=center)[0])
                center_name = str(center_query[0])
                #center_id = Center.objects.filter(id=center)[0].id
                center_id = center_query[0].id
                project_list = Project.objects.filter(center_id=center_id)
                for project in project_list:
                    project_name = str(project)
                    select_list.append(project_name)

        if len(select_list) > 1:
            if multi_project:
                prj_id = Project.objects.filter(name=multi_project).values_list('id','center_id')
            else:
                prj_name = select_list[1]
                prj_id = Project.objects.filter(name=prj_name).values_list('id','center_id')

    if 'center_manager' in user_group:
        select_list = []
        center_list = Centermanager.objects.filter(name_id=request.user.id).values_list('center', flat=True)        
        if center_list.count() < 2:
            center_obj = Center.objects.filter(id=center_list[0])[0]
            center_name, center_id = center_obj.name, center_obj.id
            project_list = Project.objects.filter(center_id=center_id)
            for project in project_list:
                project_name = str(project)
                select_list.append(project_name)

        elif len(center_list) >= 2:
            for center in center_list:
                center_query = Center.objects.filter(id=center)
                center_name = str(center_query[0])
                center_id = center_query[0].id
                #center_name = str(Center.objects.filter(id=center)[0])
                #center_id = Center.objects.filter(id=center)[0].id
                project_list = Project.objects.filter(center_id=center_id)
                for project in project_list:
                    project_name = str(project)
                    select_list.append(project_name)

        if len(select_list) > 1:
            if multi_project:
                prj_id = Project.objects.filter(name=multi_project).values_list('id','center_id')
            else:
                prj_name = select_list[1]
                prj_id = Project.objects.filter(name=prj_name).values_list('id','center_id')

        else:
            if multi_project:
                prj_id = Project.objects.filter(name=multi_project).values_list('id','center_id')
            else:
                prj_name = select_list[0]
                prj_id = Project.objects.filter(name=prj_name).values_list('id','center_id') 

    if user_group in ['nextwealth_manager','center_manager','customer']:
        widgets_id = Widgets_group.objects.filter(\
                        User_Group_id=user_group_id, project=prj_id[0][0],center=prj_id[0][1])\
                        .values('widget_priority', 'is_drilldown','is_display', 'widget_name','col', 'display_value')
        project_display_value = Project.objects.filter(\
                                id=prj_id[0][0], center=prj_id[0][1]).values_list('display_value', flat=True)[0]
    else:
        widgets_id = Widgets_group.objects.filter(\
                        User_Group_id=user_group_id, project__in=prj_id,center__in=center)\
                        .values('widget_priority', 'is_drilldown','is_display', 'widget_name','col', 'display_value')
        project_display_value = Project.objects.filter(\
                                id__in=prj_id, center__in=center)\
                                .values_list('display_value', flat=True)[0]

    for data in widgets_id:
        if data['is_display'] == True:
            widgets_data = Widgets.objects.filter(\
                            id=data['widget_name']).values('config_name', 'name', 'id_num', 'opt', 'day_type_widget', 'api')
            if user_group in ['nextwealth_manager','center_manager','customer']:
                alias_name = Alias_Widget.objects.filter(\
                             project=prj_id[0][0],widget_name_id=data['widget_name']).values('alias_widget_name')
            else:
                alias_name = Alias_Widget.objects.filter(\
                             project__in=prj_id,widget_name_id=data['widget_name']).values('alias_widget_name')
            new_dict ={}
            if len(alias_name) > 0:
                if alias_name[0]['alias_widget_name']:
                    for wd_key,wd_value in widgets_data[0].iteritems():
                        if wd_key == 'name': 
                            new_dict[wd_key] = str(alias_name[0]['alias_widget_name'])
                        else:
                            new_dict[wd_key] = wd_value 
                    widgets_data[0].update(new_dict)
            if new_dict: 
                wid_dict = new_dict
            else:
                wid_dict = widgets_data[0]
            wid_dict['widget_priority'] = data['widget_priority']
            wid_dict['is_drilldown'] = data['is_drilldown']
            wid_dict['col'] = data['col']
            if project_display_value == True and data['display_value'] == True:
                wid_dict['display_value'] = True
            else:
                wid_dict['display_value'] = False
            list_wid.append(wid_dict)            
    sorted_dict = sorted(list_wid, key=lambda k: k['widget_priority'])
    lay_out_order = []
    for i in sorted_dict:
        config_name = i.pop('config_name')
        lay_out_order.append(config_name)
        final_dict[config_name] = i
    layout_list.append(final_dict)
    layout_list.append({'layout': lay_out_order}) 

    if 'team_lead' in user_group:
        final_details = {}
        details = {}
        select_list = []
        tl_query = TeamLead.objects.filter(name_id=request.user.id)
        center_list = tl_query.values_list('center', flat = True)
        project_list = tl_query.values_list('project', flat = True)
        if (len(center_list) & len(project_list)) == 1:
            select_list.append('none')
        if len(center_list) < 2:
            center_name = str(Center.objects.filter(id=center_list[0])[0])
            for project in project_list:
                project_name = str(Project.objects.filter(id=project)[0])
                vari = center_name + ' - ' + project_name
                select_list.append(vari)
        elif len(center_list) >= 2:
            for center in center_list:
                center_name = str(Center.objects.filter(id=center)[0])
                for project in project_list:
                    project_name = str(Project.objects.filter(id=project)[0])
                    select_list.append(center_name + ' - ' + project_name)
        new_dates = latest_dates(request, project_list)
        user = request.user.id
        user_status = get_permitted_user(_project, _center, user)
        role = 'team_lead'
        final_values = common_user_data(request, select_list, role, layout_list, new_dates, user_status)
        _type       = request.GET.get('link_type', '') 
        first_date  = request.GET.get('from', '') 
        last_date   = request.GET.get('to', '') 
        if _type == 'dashboard':
            parameters = multi_center+'%20-%20'+multi_project+'&from='+first_date+'&to='+last_date
            redirectional_url = 'http://stats.headrun.com/#!/page1/'+parameters
            return redirect(redirectional_url)
        return json_HttpResponse(final_values)

    if 'center_manager' in user_group:
        final_details = {}
        details = {}
        select_list = []
        center = Centermanager.objects.filter(name_id=request.user.id).values_list('center', flat=True)[0]
        center_name = Center.objects.filter(id=center).values_list('name', flat=True)[0]
        project_names = Project.objects.filter(center_id=center).values_list('name', flat=True)
        for project in project_names:
            vari = center_name + ' - ' + project
            select_list.append(center_name + ' - ' + project)
        if len(project_names) > 1: 
            if multi_project:
                prj_id = Project.objects.filter(name=multi_project).values_list('id',flat=True)
            else:
                prj_id = Project.objects.filter(name=project_names[1]).values_list('id',flat=True)
            new_dates = latest_dates(request, prj_id)
        else:
            new_dates = latest_dates(request, project_names)
        role = 'center_manager'
        user = request.user.id 
        user_status = get_permitted_user(_project, _center, user)
        final_values = common_user_data(request, select_list, role, layout_list, new_dates, user_status)
        _type       = request.GET.get('link_type', '') 
        first_date  = request.GET.get('from', '') 
        last_date   = request.GET.get('to', '') 
        if _type == 'dashboard':
            parameters = multi_center+'%20-%20'+multi_project+'&from='+first_date+'&to='+last_date
            redirectional_url = 'http://stats.headrun.com/#!/page1/'+parameters
            return redirect(redirectional_url)
        return json_HttpResponse(final_values)

    if 'nextwealth_manager' in user_group:
        final_details = {}
        details = {}
        select_list = []
        center_list = Nextwealthmanager.objects.filter(name_id=request.user.id).values_list('center')
        if len(center_list) < 2:
            center_name = str(Center.objects.filter(id=center_list[0][0])[0])
            center_id = center[0]
            project_list = Project.objects.filter(center_id=center_id)
            for project in project_list:
                project_name = str(project)
                try:
                    lay_list = json.loads(str(Project.objects.filter(name=project_name).values_list('layout')[0][0]))
                except:
                    lay_list = ''
                vari = center_name + ' - ' + project_name
                select_list.append(center_name + ' - ' + project_name)

        elif len(center_list) >= 2:
            for center in center_list:
                center_name = str(Center.objects.filter(id=center[0])[0])
                center_id = center[0]
                project_list = Project.objects.filter(center_id=center_id)
                for project in project_list:
                    project_name = str(project)
                    try:
                        lay_list = json.loads(str(Project.objects.filter(name=project_name).values_list('layout')[0][0]))
                    except:
                        lay_list = ''
                    vari = center_name + ' - ' + project_name
                    layout_list.append({vari:lay_list})
                    select_list.append(center_name + ' - ' + project_name)

        if len(select_list) > 1:
            if multi_project:
                prj_id = Project.objects.filter(name=multi_project).values_list('id',flat=True)
            else:
                prj_name = select_list[1].split('- ')[1].strip()
                prj_id = Project.objects.filter(name=prj_name).values_list('id',flat=True)
            new_dates = latest_dates(request, prj_id)
        else:
            new_dates = latest_dates(request, project_list)
        user = request.user.id
        user_status = get_permitted_user(_project, _center, user)
        role = 'nextwealth_manager'
        final_values = common_user_data(request, select_list, role, layout_list, new_dates, user_status)
        _type       = request.GET.get('link_type', '')
        first_date  = request.GET.get('from', '')
        last_date   = request.GET.get('to', '')
        if _type == 'dashboard':
            parameters = multi_center+'%20-%20'+multi_project+'&from='+first_date+'&to='+last_date
            redirectional_url = 'http://stats.headrun.com/#!/page1/'+parameters
            return redirect(redirectional_url)
        return json_HttpResponse(final_values)

    if 'customer' in user_group:
        final_details = {}
        details = {}
        select_list = []
        customer_query = Customer.objects.filter(name_id=request.user.id)
        center_list = customer_query.values_list('center', flat = True)
        project_list = customer_query.values_list('project', flat = True)
        if (len(center_list) & len(project_list)) == 1:
            select_list.append('none')
        if len(center_list) < 2:
            center_name = str(Center.objects.filter(id=center_list[0])[0])
            for project in project_list:
                project_name = str(Project.objects.filter(id=project)[0])
                vari = center_name + ' - ' + project_name
                select_list.append(vari)
        elif len(center_list) >= 2:
            for center in center_list:
                center_name = str(Center.objects.filter(id=center)[0])
                for project in project_list:
                    project_name = str(Project.objects.filter(id=project)[0])
                    select_list.append(center_name + ' - ' + project_name)
        project_names = project_list
        if len(project_names) > 1: 
            if multi_project:
                prj_id = Project.objects.filter(name=multi_project).values_list('id',flat=True)
            else:
                prj_id = Project.objects.filter(name=project_names[1]).values_list('id',flat=True)
            new_dates = latest_dates(request, prj_id)
        else:
            new_dates = latest_dates(request, project_names)
        user = request.user.id
        user_status = get_permitted_user(_project, _center, user)
        role = 'customer'
        final_values = common_user_data(request, select_list, role, layout_list, new_dates, user_status)
        _type       = request.GET.get('link_type', '') 
        first_date  = request.GET.get('from', '') 
        last_date   = request.GET.get('to', '') 
        if _type == 'dashboard':
            parameters = multi_center+'%20-%20'+multi_project+'&from='+first_date+'&to='+last_date
            redirectional_url = 'http://stats.headrun.com/#!/page1/'+parameters
            return redirect(redirectional_url)
        return json_HttpResponse(final_values)


def common_user_data(request, projects_list, role, widgets_list, dates, user_status):

    "passing parameters required for opening of dashboard page"

    result_dict = {}
    first_date = request.GET.get('from', '')
    last_date  = request.GET.get('to', '')
    data_type  = request.GET.get('type', '')
    sub_project = request.GET.get('sub_project', '')
    work_packet = request.GET.get('work_packet', '')
    sub_packet  = request.GET.get('sub_packet', '')
    result_dict['from_date'] = first_date
    result_dict['to_date'] = last_date
    result_dict['type'] = data_type
    result_dict['sub_project'] = sub_project
    result_dict['work_packet'] = work_packet
    result_dict['sub_packet'] = sub_packet
    result_dict['list'] = projects_list
    result_dict['dates'] = dates
    result_dict['lay'] = widgets_list
    result_dict['role'] = role
    result_dict['user_status'] = user_status
    
    return result_dict

