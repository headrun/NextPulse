
from django.db.models import Max
from models import *
from basic import latest_dates
from common.utils import getHttpResponse as json_HttpResponse


def project(request):

    try:
        multi_center, multi_project = request.GET.get('name').split(' - ')
    except: 
        multi_center, multi_project = '',''

    user_group = request.user.groups.values_list('name', flat=True)[0]
    user_group_id = Group.objects.filter(name=user_group).values_list('id', flat=True)
    list_wid = []
    layout_list = []
    final_dict = {}

    if 'team_lead' in user_group:
        team_lead_obj = TeamLead.objects.filter(name_id=request.user.id) 
        center = team_lead_obj.values_list('center', flat=True)
        prj_id = team_lead_obj.values_list('project', flat=True)

    if 'customer' in user_group:
        select_list = []
        details = {}
        customer_objs = Customer.objects.filter(name_id=request.user.id) 
        center_list = Customer.objects.filter(name_id=request.user.id).values_list('center')
        project_list = Customer.objects.filter(name_id=request.user.id).values_list('project')
        if (len(center_list) & len(project_list)) == 1:
            select_list.append('none')
        if len(center_list) < 2: 
            center_name = str(Center.objects.filter(id=center_list[0][0])[0])
            for project in project_list:
                project_name = str(Project.objects.filter(id=project[0])[0])
                vari = center_name + ' - ' + project_name
                select_list.append(vari)
        elif len(center_list) >= 2:
            for center in center_list:
                center_name = str(Center.objects.filter(id=center[0])[0])
                for project in project_list:
                    project_name = str(Project.objects.filter(id=project[0])[0])
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
        center_list = Nextwealthmanager.objects.filter(name_id=request.user.id).values_list('center')
        if len(center_list) < 2:
            center_name = str(Center.objects.filter(id=center_list[0][0])[0])
            center_id = Center.objects.filter(name = center_name)[0].id
            project_list = Project.objects.filter(center_id=center_id)
            for project in project_list:
                project_name = str(project)
                select_list.append(project_name)

        elif len(center_list) >= 2:
            for center in center_list:
                center_name = str(Center.objects.filter(id=center[0])[0])
                center_id = Center.objects.filter(id=center[0])[0].id
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
        center_list = Centermanager.objects.filter(name_id=request.user.id).values_list('center')
        if len(center_list) < 2:
            center_name = str(Center.objects.filter(id=center_list[0][0])[0])
            center_id = Center.objects.filter(name = center_name)[0].id
            project_list = Project.objects.filter(center_id=center_id)
            for project in project_list:
                project_name = str(project)
                select_list.append(project_name)

        elif len(center_list) >= 2:
            for center in center_list:
                center_name = str(Center.objects.filter(id=center[0])[0])
                center_id = Center.objects.filter(id=center[0])[0].id
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
        widgets_id = Widgets_group.objects.filter(User_Group_id=user_group_id, project=prj_id[0][0],center=prj_id[0][1]).values('widget_priority', 'is_drilldown','is_display', 'widget_name','col')
    else:
        widgets_id = Widgets_group.objects.filter(User_Group_id=user_group_id, project=prj_id,center=center).values('widget_priority', 'is_drilldown','is_display', 'widget_name','col')

    for data in widgets_id:
        if data['is_display'] == True:
            widgets_data = Widgets.objects.filter(id=data['widget_name']).values('config_name', 'name', 'id_num', 'opt', 'day_type_widget', 'api')
            if user_group in ['nextwealth_manager','center_manager','customer']:
                alias_name = Alias_Widget.objects.filter(project=prj_id[0][0],widget_name_id=data['widget_name']).values('alias_widget_name')
            else:
                alias_name = Alias_Widget.objects.filter(project=prj_id,widget_name_id=data['widget_name']).values('alias_widget_name')
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
        center_list = TeamLead.objects.filter(name_id=request.user.id).values_list('center')
        project_list = TeamLead.objects.filter(name_id=request.user.id).values_list('project')
        if (len(center_list) & len(project_list)) == 1:
            select_list.append('none')
        if len(center_list) < 2:
            center_name = str(Center.objects.filter(id=center_list[0][0])[0])
            for project in project_list:
                project_name = str(Project.objects.filter(id=project[0])[0])
                vari = center_name + ' - ' + project_name
                select_list.append(vari)
        elif len(center_list) >= 2:
            for center in center_list:
                center_name = str(Center.objects.filter(id=center[0])[0])
                for project in project_list:
                    project_name = str(Project.objects.filter(id=project[0])[0])
                    select_list.append(center_name + ' - ' + project_name)
        details['list'] = select_list
        details['role'] = 'team_lead'
        details['lay'] = layout_list
        details['final'] = final_details
        new_dates = latest_dates(request, project_list)
        details['dates'] = new_dates
        return json_HttpResponse(details)

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
        details['list'] = select_list
        details['role'] = 'center_manager'
        details['lay'] = layout_list
        details['final'] = final_details
        if len(project_names) > 1: 
            if multi_project:
                prj_id = Project.objects.filter(name=multi_project).values_list('id',flat=True)
            else:
                prj_id = Project.objects.filter(name=project_names[1]).values_list('id',flat=True)
            new_dates = latest_dates(request, prj_id)
        else:
            new_dates = latest_dates(request, project_names)
        details['dates'] = new_dates
        return json_HttpResponse(details)

    if 'nextwealth_manager' in user_group:
        final_details = {}
        details = {}
        select_list = []
        center_list = Nextwealthmanager.objects.filter(name_id=request.user.id).values_list('center')
        if len(center_list) < 2:
            center_name = str(Center.objects.filter(id=center_list[0][0])[0])
            center_id = Center.objects.filter(name = center_name)[0].id
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
                center_id = Center.objects.filter(id=center[0])[0].id
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

        details['list'] = select_list
        details['role'] = 'nextwealth_manager'
        details['lay'] = layout_list
        details['final'] = final_details
        if len(select_list) > 1:
            if multi_project:
                prj_id = Project.objects.filter(name=multi_project).values_list('id',flat=True)
            else:
                prj_name = select_list[1].split('- ')[1].strip()
                prj_id = Project.objects.filter(name=prj_name).values_list('id',flat=True)
            new_dates = latest_dates(request, prj_id)
        else:
            new_dates = latest_dates(request, project_list)
        details['dates'] = new_dates
        return json_HttpResponse(details)

    if 'customer' in user_group:
        final_details = {}
        details = {}
        select_list = []
        center_list = Customer.objects.filter(name_id=request.user.id).values_list('center')
        project_list = Customer.objects.filter(name_id=request.user.id).values_list('project')
        if (len(center_list) & len(project_list)) == 1:
            select_list.append('none')
        if len(center_list) < 2:
            center_name = str(Center.objects.filter(id=center_list[0][0])[0])
            for project in project_list:
                project_name = str(Project.objects.filter(id=project[0])[0])
                vari = center_name + ' - ' + project_name
                select_list.append(vari)
        elif len(center_list) >= 2:
            for center in center_list:
                center_name = str(Center.objects.filter(id=center[0])[0])
                for project in project_list:
                    project_name = str(Project.objects.filter(id=project[0])[0])
                    select_list.append(center_name + ' - ' + project_name)
        details['list'] = select_list
        details['role'] = 'customer'
        details['lay'] = layout_list
        details['final'] = final_details
        project_names = project_list
        if len(project_names) > 1: 
            if multi_project:
                prj_id = Project.objects.filter(name=multi_project).values_list('id',flat=True)
            else:
                prj_id = Project.objects.filter(name=project_names[1]).values_list('id',flat=True)
            new_dates = latest_dates(request, prj_id)
        else:
            new_dates = latest_dates(request, project_names)
        details['dates'] = new_dates

        details['dates'] = new_dates
        return json_HttpResponse(details)

