
import datetime
import json
from django.db.models import Q
from api.models import *
from django.db.models import Count
from django.http import HttpResponse
from common.utils import getHttpResponse as json_HttpResponse
from django.db import IntegrityError

def get_annotations(request):

    series_name = request.GET['series_name']
    chart_name = request.GET.get('chart_name')
    project_name = request.GET.get('proj_name', '')
    center_name = request.GET.get('cen_name', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
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

    annotations = Annotation.objects.filter(key__contains='<##>' + chart_name + '<##>' + series_name + '<##>', center__name = center_name,
                                            project__name = project_name, chart_id = chart_name)
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
        annotations = Annotation.objects.filter(project__name = project_name,center__name=center_name,\
                                                chart_id=chart_name, key=series_name)
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


def add_annotation(request):
    #import pdb;pdb.set_trace()
    anno_id = request.POST.get('id','')
    epoch = request.POST.get('epoch','')
    text = request.POST.get("text",'')
    graph_name = request.POST.get("graph_name",'')
    series_name = request.POST.get("series_name",'')
    widget_id = request.POST.get('widget_id','')
    key = '<##>' + widget_id + '<##>' + series_name + '<##>' + anno_id
    created_by = request.user
    dt_created = datetime.datetime.now()
    prj_name = request.POST.get('project_live', '')
    prj_name = prj_name.split(' - ')[0];
    cen_name = request.POST.get('center_live', '')
    cen_name = cen_name.split(' - ')[0]
    prj_obj = Project.objects.filter(name = prj_name)
    center = Center.objects.filter(name = cen_name)
    start_date = request.POST.get('start_date', '')
    end_date = request.POST.get('end_date', '')
    #import pdb;pdb.set_trace()
    #widget_obj = Widgets.objects.filter(id_num = widget_id)[0]
    existed_annotations = Annotation.objects.filter(text=text, project=prj_obj[0],center=center[0],\
                                                key=key,dt_created=dt_created)
    if existed_annotations:
        return json_HttpResponse('Annotation already exist')
    try:
        annotation = Annotation.objects.create(epoch=epoch, text=text, key=key, project=prj_obj[0],\
                                            dt_created=dt_created, created_by=created_by,\
                                            center=center[0],chart_id = widget_id)
    except IntegrityError:
        delete_annotation = Annotation.objects.filter(epoch=epoch, project=prj_obj[0],\
                                created_by=created_by, center=center[0],key=key,\
                                chart_id=widget_id)
        if delete_annotation:
            delete_anno = delete_annotation
            delete_anno.delete()

        annotation = Annotation(epoch=epoch, text=text, project=prj_obj[0],\
                                dt_created=dt_created, created_by=created_by,\
                                center=center[0], chart_id=widget_id , key=series_name)
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
    chart_id = request.POST.get('chart_type_name_id','')
    center = request.POST.get('center_id','')
    project = request.POST.get('project_id','')
    if action == "delete":
        anno = Annotation.objects.filter(epoch = epoch, created_by = request.user, key = key_to)
        if anno:
            anno = anno[0]
            anno.delete()
            return json_HttpResponse(json.dumps({"status": "success", "message": "deleted successfully"}))
        elif action == 'delete' and text == '':
            return json_HttpResponse(json.dumps({"status": "success", "message": "deleted successfully"}))
        else:
            series = series.split('<##>')[0]
            anno = Annotation.objects.filter(epoch=epoch,created_by=request.user,key__contains=series)[0]
            anno.delete()
            return json_HttpResponse(json.dumps({"status": "success", "message": "deleted successfully"}))

    if series is not None:
        series = series.split('<##>')[0]
        annotation = Annotation.objects.filter(epoch=epoch,created_by=request.user,key__contains=series)
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

