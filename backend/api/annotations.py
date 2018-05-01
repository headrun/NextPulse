
import datetime
import json
from django.db.models import Q
from api.models import *
from api.utils import *
from api.commons import *
from api.basics import *
from django.db.models import Count
from django.http import HttpResponse
from common.utils import getHttpResponse as json_HttpResponse
from django.db import IntegrityError
from datetime import date, timedelta


def get_annotations(request):

    dates_list = []
    main_data_dict = data_dict(request.GET)
    type = main_data_dict['type']
    if type == 'day':
        dates = main_data_dict['dwm_dict']['day']
        for date in dates:
            dates_list.append(date)
    elif type == 'week':
        dates = main_data_dict['dwm_dict']['week']
        for date in dates:
            dates_list.append(date[0] + ' to ' + date[-1])
    elif type == 'month':
        dates = main_data_dict['dwm_dict']['month']
        for month_na,month_va in zip(dates['month_names'],dates['month_dates']):
            month_dates = month_va
            dates_list.append(month_dates[0] + ' to ' + month_dates[-1])
    
    series_name = request.GET['series_name']
    chart_name = request.GET.get('chart_name')
    project_name = request.GET.get('project', '')
    center_name = request.GET.get('center', '')
    start_date = request.GET.get('from', '')
    end_date = request.GET.get('to', '')
    chart_type = request.GET.get('chart_type', '')
    if project_name:
        project_name = project_name.split(' - ')[0];
    if center_name:
        center_name = center_name.split(' -')[0];
    try:
        day_type = request.GET['type']
    except:
        day_type = ''

    #===================================================================================

    #if day_type in ['week', 'month']:



    #====================================================================================    
    
    if chart_type == 'bar':
        annotat_data = get_annotation_data(request)
        return json_HttpResponse(annotat_data)
    else:
        annotations = Annotation.objects.filter(key__contains='<##>' + chart_name + '<##>' + series_name + '<##>', center__name = center_name,
                                                project__name = project_name, chart_id = chart_name, epoch__in=dates_list)
        annotations_data = []

        if annotations:
            for annotation in annotations:
                final_data = {}
                final_data['chart_type_name_id'] = annotation.chart_type_name_id
                final_data['center_id'] = annotation.center_id
                final_data['text'] = annotation.text
                final_data['epoch'] = annotation.epoch
                final_data['dt_created'] = str(annotation.dt_created)
                final_data['key'] = annotation.key
                final_data['created_by_id'] = annotation.created_by_id
                final_data['project_id'] = annotation.project_id
                final_data['id'] = annotation.id
                annotations_data.append(final_data)
        else:
            if chart_type == 'bar':
                annotat_data = get_annotation_data(request)
            else:        
                annotations = Annotation.objects.filter(project__name = project_name,center__name=center_name,\
                                                        chart_id=chart_name, key=series_name, epoch__in=dates_list)
                if annotations:
                    for annotation in annotations:
                        final_data = {}
                        final_data['center_id'] = annotation.center_id
                        final_data['project_id'] = annotation.project_id
                        final_data['text'] = annotation.text
                        final_data['id'] = annotation.id
                        final_data['created_by_id'] = annotation.created_by_id
                        final_data['epoch'] = annotation.epoch
                        final_data['dt_created'] = str(annotation.dt_created)
                        annotations_data.append(final_data)
        return json_HttpResponse(annotations_data)


def get_annotation_data(request):

    series_name = request.GET['series_name']
    chart_name = request.GET.get('chart_name')
    project_name = request.GET.get('project', '')
    center_name = request.GET.get('center', '')
    start_date = request.GET.get('from', '')
    end_date = request.GET.get('to', '')
    chart_type = request.GET.get('chart_type', '')
    if project_name:
        project_name = project_name.split(' - ')[0];
    if center_name:
        center_name = center_name.split(' -')[0];
    try:
        day_type = request.GET['type']
    except:
        day_type = ''
    
    check_dates = []
    d1 = date(int(start_date.split('-')[0]), int(start_date.split('-')[1]), int(start_date.split('-')[2]))
    d2 = date(int(end_date.split('-')[0]), int(end_date.split('-')[1]), int(end_date.split('-')[2]))
    delta = d2 - d1
    for i in range(delta.days + 1):
        check_dates.append(str(d1 + timedelta(days=i)))

    annotations = Annotation.objects.filter(key__contains='<##>' + chart_name + '<##>' + series_name + '<##>', center__name = center_name,
                                            project__name = project_name, chart_id = chart_name)
    
    if annotations:
        result = get_anno_output_data(annotations,check_dates)
    else:
        annotations = Annotation.objects.filter(key__contains=series_name,project__name=project_name,chart_id=chart_name,\
                        center__name=center_name)
        result = get_anno_output_data(annotations,check_dates)       
    return result


def get_anno_output_data(annotations,check_dates):

    annotations_data = []
    for annotation in annotations:
            first_date = annotation.start_date
            last_date = annotation.end_date
            dates = []
            delta = last_date - first_date
            for i in range(delta.days + 1):
                dates.append(str(first_date + timedelta(days=i)))
            final_dates = []
            for date_val in check_dates:
                if date_val in dates:
                    final_dates.append(date_val)
            check_val = float(len(final_dates))/float(len(check_dates))
            print check_val
            check_val = float('%.2f' % round(check_val, 2))
            
            if check_val >= 0.75:
                final_data = {}
                final_data['chart_type_name_id'] = annotation.chart_type_name_id
                final_data['center_id'] = annotation.center_id
                final_data['text'] = annotation.text
                final_data['epoch'] = annotation.epoch
                final_data['dt_created'] = str(annotation.dt_created)
                final_data['key'] = annotation.key
                final_data['created_by_id'] = annotation.created_by_id
                final_data['project_id'] = annotation.project_id
                final_data['id'] = annotation.id
                annotations_data.append(final_data)
    return annotations_data


def add_annotation(request):
    
    anno_id = request.POST.get('id','')
    epoch = request.POST.get('epoch','')
    text = request.POST.get("text",'')
    graph_name = request.POST.get("graph_name",'')
    series_name = request.POST.get("series_name",'')
    widget_id = request.POST.get('widget_id','')
    key = '<##>' + widget_id + '<##>' + series_name + '<##>' + anno_id
    created_by = request.user
    dt_created = datetime.datetime.now()
    prj_name = request.POST.get('project', '')
    prj_name = prj_name.split(' - ')[0];
    cen_name = request.POST.get('center', '')
    cen_name = cen_name.split(' - ')[0]
    prj_obj = Project.objects.filter(name = prj_name)
    center = Center.objects.filter(name = cen_name)
    start_date = request.POST.get('from', '')
    end_date = request.POST.get('to', '')
    
    existed_annotations = Annotation.objects.filter(text=text, project=prj_obj[0],center=center[0],\
                                                key=key,dt_created=dt_created)
    if existed_annotations:
        return json_HttpResponse('Annotation already exist')
    try:
        annotation = Annotation.objects.create(epoch=epoch, text=text, key=key, project=prj_obj[0],\
                                            dt_created=dt_created, created_by=created_by,\
                                            center=center[0],chart_id = widget_id,start_date=start_date,\
                                            end_date=end_date)
    except IntegrityError:
        
        delete_annotation = Annotation.objects.filter(epoch=epoch, project=prj_obj[0],\
                                created_by=created_by, center=center[0],key=key,\
                                chart_id=widget_id)
        if delete_annotation:
            delete_anno = delete_annotation
            delete_anno.delete()
        annotation = Annotation(epoch=epoch, text=text, project=prj_obj[0],\
                                dt_created=dt_created, created_by=created_by,\
                                center=center[0], chart_id=widget_id , key=series_name,\
                                start_date=start_date,end_date=end_date)
        annotation.save()
        if not graph_name:
            graph_name = 'sss'
        if not series_name:
            series_name = 'wid'
        entity_json = {}
        entity_json['id'] = anno_id
        entity_json['epoch'] = epoch
        entity_json['text'] = text
        entity_json['graph_name'] = graph_name
        entity_json['level_name'] = 12
        entity_json['series_name'] = series_name
        return json_HttpResponse(entity_json)

    if not graph_name:
        graph_name = 'sss'
    if not series_name:
        series_name = 'wid'
    entity_json = {}
    entity_json['id'] = anno_id
    entity_json['epoch'] = epoch
    entity_json['text'] = text
    entity_json['graph_name'] = graph_name
    entity_json['level_name'] = 12
    entity_json['series_name'] = series_name
    return json_HttpResponse(entity_json)


def update_annotation(request):
    
    action = request.POST.get("action", "update")
    epoch = request.POST.get("epoch")
    annotation_id = request.POST.get("id")
    series = request.POST.get('series_name')
    text = request.POST.get("text")
    widget_id = request.POST.get('widget_id','')
    key_to = request.POST.get('key', '')
    center = request.POST.get('center_id','')
    project = request.POST.get('project_id','')
    start_date = request.POST.get('from', '')
    end_date = request.POST.get('to', '')
    if '-' in annotation_id:
        annotation_id = ""
    #import pdb;pdb.set_trace()
    if action == "delete":
        if action == "delete" and text == "" and project == "" and annotation_id == "":
            anno = Annotation.objects.filter(text=text,epoch=epoch)
            if anno:
                anno.delete()
                return json_HttpResponse(json.dumps({"status": "success", "message": "deleted successfully"})) 
            else:
                return json_HttpResponse(json.dumps({"status": "success", "message": "deleted successfully"}))
        elif text != "" and epoch != "" and key_to != "" and project != "" and annotation_id != "":
            anno = Annotation.objects.filter(text=text,epoch=epoch,key=key_to,\
                                                    project=project,id=annotation_id)
        elif text != "" and epoch != "" and project != "" and annotation_id != "":
            anno = Annotation.objects.filter(text=text,epoch=epoch,project=project,id=annotation_id)
        elif text != "" and epoch != "" and annotation_id != "" and project == "":
            anno = Annotation.objects.filter(text=text,epoch=epoch,id=annotation_id)
        elif text != "" and epoch != "" and project != "" and annotation_id == "":
            anno = Annotation.objects.filter(text=text,epoch=epoch,project=project)
        elif text != "" and epoch != "" and project == "" and annotation_id == "":
            anno = Annotation.objects.filter(text=text,epoch=epoch)
        elif text == "" and epoch != "" and annotation_id != "":
            anno = Annotation.objects.filter(text=text,epoch=epoch)
        elif action == "delete" and text != "" and epoch != "" and widget_id != "":
            anno = Annotation.objects.filter(text=text,epoch=epoch,chart_id=widget_id)
        if anno:
            anno = anno[0]
            anno.delete()
            return json_HttpResponse(json.dumps({"status": "success", "message": "deleted successfully"}))
        else:
            series = series.split('<##>')[0]
            anno = Annotation.objects.filter(epoch=epoch,key__contains=series)
            if anno:
                anno = anno[0]
                anno.delete()
            return json_HttpResponse(json.dumps({"status": "success", "message": "deleted successfully"}))    

    if series is not None:
        series = series.split('<##>')[0]
        annotation = Annotation.objects.filter(epoch=epoch,created_by=request.user,key__contains=series,\
                                                id=annotation_id,project=project,center=center)
        annotation = annotation[0]
        annotation.text = text 
        annotation.save()
        return HttpResponse(json.dumps({"status": "success", "message": "successfully updated"}))
    else:
        annotation = Annotation.objects.filter(epoch=epoch,project=project,center=center,id=annotation_id)
    if annotation:
        annotation = annotation[0]
        annotation.text = text
        annotation.save()
    else:
        annotation = annotation
    return HttpResponse(json.dumps({"status": "success", "message": "successfully updated"}))

    return HttpResponse('Nothing happened')

