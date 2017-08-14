def internal_chart_data_multi(pro_id,cen_id,to_date,work_packet,chart_type,project):
    if (project == 'Probe' and chart_type == 'External Accuracy Trends') or (project == 'Ujjivan' and chart_type == 'External Accuracy Trends') or (project == 'IBM' and chart_type == 'External Accuracy Trends'):
        final_internal_drilldown = {}
        final_internal_drilldown['type'] = chart_type
        final_internal_drilldown['project'] = project
        accuracy_query_set = accuracy_query_generations(pro_id, cen_id, to_date, work_packet)
        if project == 'Ujjivan' and chart_type == 'Internal Accuracy Trends':
            list_of_internal = Internalerrors.objects.filter(**accuracy_query_set).values_list('employee_id','work_packet','total_errors','date')
        elif chart_type == 'External Accuracy Trends':
            list_of_internal = Externalerrors.objects.filter(**accuracy_query_set).values_list('employee_id','work_packet','total_errors','date')
        list_ext_data = []
        for i in list_of_internal:
            per_day_value = RawTable.objects.filter(employee_id=i[0],date=i[3],work_packet=i[1]).values_list('per_day')
            try:
                per_day_value = per_day_value[0][0]
            except:
                per_day_value = 0
            if per_day_value > 0:
                list_ext_data.append({'date':str(i[3]),'total_errors': i[2],'productivity': per_day_value  })
            Productivity_value = 0
            Error_count = 0
            for ans in list_ext_data:
                if ans['total_errors']:
                    Error_count = Error_count + ans['total_errors']
                if ans['productivity']:
                    Productivity_value = Productivity_value + ans['productivity']
                accuracy = 100 - ((float(ans['total_errors']) / float(ans['productivity']))) * 100
                accuracy_agg = float('%.2f' % round(accuracy, 2))
                ans['accuracy'] = accuracy_agg
        if len(list_ext_data) > 0:
                table_headers = ['date','productivity','total_errors']
        final_internal_drilldown['data'] = list_ext_data
        final_internal_drilldown['table_headers'] = table_headers
        final_internal_drilldown['Productivity_value'] = Productivity_value
        final_internal_drilldown['Error_count'] = Error_count
        return final_internal_drilldown

    if project == 'Ujjivan' and chart_type == 'Internal Accuracy Trends':
        final_internal_drilldown = {}
        final_internal_drilldown['type'] = chart_type
        final_internal_drilldown['project'] = project
        list_of_internal = Internalerrors.objects.filter(project=pro_id,center=cen_id,date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','work_packet','total_errors','date')
        list_ext_data = []
        for i in list_of_internal:
            per_day_value = RawTable.objects.filter(employee_id=i[0],date=i[3],work_packet=i[1]).values_list('per_day')
            try:
                per_day_value = per_day_value[0][0]
            except:
                per_day_value = 0
            if per_day_value > 0:
                list_ext_data.append({'date':str(i[3]),'total_errors': i[2],'productivity': per_day_value})
            Productivity_value = 0
            Error_count = 0 
            for ans in list_ext_data:
                if ans['productivity']:
                    Productivity_value = Productivity_value + ans['productivity']
                if ans['total_errors']:
                    Error_count = Error_count + ans['total_errors'] 
                accuracy = 100 - ((float(ans['total_errors']) / float(ans['productivity']))) * 100
                accuracy_agg = float('%.2f' % round(accuracy, 2))
                ans['accuracy'] = accuracy_agg
        if len(list_ext_data) > 0:
                table_headers = ['date','productivity','total_errors']
        final_internal_drilldown['data'] = list_ext_data
        final_internal_drilldown['table_headers'] = table_headers
        final_internal_drilldown['Productivity_value'] = Productivity_value
        final_internal_drilldown['Error_count'] = Error_count
        return final_internal_drilldown

    elif chart_type == 'Internal Accuracy Trends':
        packets_list = work_packet.split('_')
        packets_list_type = ''
        if len(packets_list) == 2:
            sub_project_statuts = Internalerrors.objects.filter(project=pro_id, center=cen_id, date__range=[to_date[0], to_date[-1]]).values_list('sub_project', flat=True)
            sub_project_statuts = filter(None, sub_project_statuts)
            if len(sub_project_statuts) > 0:
                sub_project, work_packet = work_packet.split('_')
                list_of_internal = Internalerrors.objects.filter(project=pro_id, center=cen_id, date__range=[to_date[0], to_date[-1]],sub_project=sub_project,work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
            work_packet_statuts = Internalerrors.objects.filter(project=pro_id,center=cen_id, date__range=[to_date[0], to_date[-1]]).values_list('work_packet',flat=True)
            work_packet_statuts = filter(None, work_packet_statuts)
            if len(sub_project_statuts) == 0 and len(work_packet_statuts) > 0:
                work_packet, sub_packet = work_packet.split('_')
                is_work_pac_exist = Internalerrors.objects.filter(project=pro_id, center=cen_id, date__range=[to_date[0], to_date[-1]]).values_list('work_packet','sub_packet').distinct()[0]
                if len(is_work_pac_exist) > 1:
                    list_of_internal = Internalerrors.objects.filter(project=pro_id, center=cen_id, date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
                else:
                    list_of_internal = Internalerrors.objects.filter(project=pro_id, center=cen_id, date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
        elif len(packets_list) == 3:
            if '_' in work_packet:
                sub_project, work_packet, sub_packet = work_packet.split('_')
                list_of_internal = Internalerrors.objects.filter(center=cen_id, project=pro_id, date__range=[to_date[0], to_date[-1]],work_packet=work_packet,sub_packet=sub_packet).values_list('employee_id','audited_errors','total_errors','date')
            else:
                is_work_pac_exist = Internalerrors.objects.filter(project=pro_id, center=cen_id, date__range=[to_date[0], to_date[-1]]).values_list('work_packet','sub_packet').distinct()[0]
                if len(is_work_pac_exist) > 1:
                    list_of_internal = Internalerrors.objects.filter(project=pro_id, center=cen_id, date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
                else:
                    list_of_internal = Internalerrors.objects.filter(project=pro_id, center=cen_id, date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
        else:
            sub_project_statuts = Internalerrors.objects.filter(project=pro_id,center=cen_id, date__range=[to_date[0], to_date[-1]]).values_list('sub_project', flat=True)
            sub_project_statuts = filter(None, sub_project_statuts)
            if len(sub_project_statuts) > 0:
                packets_list_type = 'sub_project'
                is_work_pac_exist = Internalerrors.objects.filter(project=pro_id,center=cen_id, date__range=[to_date[0], to_date[-1]]).values_list('sub_project','work_packet','sub_packet').distinct()[0]
                if len(is_work_pac_exist) > 1:
                    list_of_internal = Internalerrors.objects.filter(project=pro_id, center=cen_id, date__range=[to_date[0], to_date[-1]],sub_project=packets_list[0]).values_list('employee_id', 'audited_errors', 'total_errors','date')
                else:
                    list_of_internal = Internalerrors.objects.filter(project=pro_id, center=cen_id, date__range=[to_date[0], to_date[-1]],sub_project=packets_list[0]).values_list('employee_id', 'audited_errors', 'total_errors','date')
            else:
                packets_list_type = 'work_packet'
                is_work_pac_exist = Internalerrors.objects.filter(project=pro_id,center=cen_id,  date__range=[to_date[0], to_date[-1]]).values_list('work_packet','sub_packet').distinct()[0]
                if len(is_work_pac_exist) > 1:
                    list_of_internal = Internalerrors.objects.filter(project=pro_id,center=cen_id, date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
                else:
                    list_of_internal = Internalerrors.objects.filter(project=pro_id,center=cen_id, date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
    else:
        packets_list = work_packet.split('_')
        packets_list_type = ''
        if len(packets_list) == 2:
            sub_project_statuts = Externalerrors.objects.filter(project=pro_id,center=cen_id, date__range=[to_date[0], to_date[-1]]).values_list('sub_project', flat=True)
            sub_project_statuts = filter(None, sub_project_statuts)
            if len(sub_project_statuts) > 0:
                sub_project, work_packet = work_packet.split('_')
                list_of_internal = Externalerrors.objects.filter(project=pro_id, center=cen_id,date__range=[to_date[0], to_date[-1]],sub_project=sub_project,work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
            work_packet_statuts = Externalerrors.objects.filter(project=pro_id,center=cen_id, date__range=[to_date[0], to_date[-1]]).values_list('work_packet',flat=True)
            work_packet_statuts = filter(None, work_packet_statuts)
            if len(sub_project_statuts) == 0 and len(work_packet_statuts) > 0:
                work_packet, sub_packet = work_packet.split('_')
                is_work_pac_exist = Externalerrors.objects.filter(project=pro_id,center=cen_id, date__range=[to_date[0], to_date[-1]]).values_list('work_packet', 'sub_packet').distinct()[0]
                if len(is_work_pac_exist) > 1:
                    list_of_internal = Externalerrors.objects.filter(project=pro_id,center=cen_id, date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
                else:
                    list_of_internal = Externalerrors.objects.filter(project=pro_id,center=cen_id, date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
        elif len(packets_list) == 3:
            if '_' in work_packet:
                sub_project, work_packet, sub_packet = work_packet.split('_')
                list_of_internal = Externalerrors.objects.filter(center=cen_id, project=pro_id,date__range=[to_date[0], to_date[-1]],work_packet=work_packet,sub_packet=sub_packet).values_list('employee_id','audited_errors','total_errors','date')
            else:
                is_work_pac_exist = Externalerrors.objects.filter(project=pro_id,center=cen_id, date__range=[to_date[0], to_date[-1]]).values_list('work_packet', 'sub_packet').distinct()[0]
                if len(is_work_pac_exist) > 1:
                    list_of_internal = Externalerrors.objects.filter(project=pro_id,center=cen_id, date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
                else:
                    list_of_internal = Externalerrors.objects.filter(project=pro_id,center=cen_id, date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
        else:
            sub_project_statuts = Externalerrors.objects.filter(project=pro_id,center=cen_id, date__range=[to_date[0], to_date[-1]]).values_list('sub_project', flat=True)
            sub_project_statuts = filter(None, sub_project_statuts)
            if len(sub_project_statuts) > 0:
                packets_list_type = 'sub_project'
                is_work_pac_exist = Externalerrors.objects.filter(project=pro_id,center=cen_id, date__range=[to_date[0], to_date[-1]]).values_list('sub_project', 'work_packet', 'sub_packet').distinct()[0]
                if len(is_work_pac_exist) > 1:
                    list_of_internal = Externalerrors.objects.filter(project=pro_id,center=cen_id, date__range=[to_date[0], to_date[-1]],sub_project=packets_list[0]).values_list('employee_id', 'audited_errors', 'total_errors', 'date')
                else:
                    list_of_internal = Externalerrors.objects.filter( project=pro_id, center=cen_id,date__range=[to_date[0], to_date[-1]],sub_project=packets_list[0]).values_list('employee_id', 'audited_errors', 'total_errors', 'date')
            else:
                packets_list_type = 'work_packet'
                is_work_pac_exist = Externalerrors.objects.filter(project=pro_id,center=cen_id,date__range=[to_date[0], to_date[-1]]).values_list('work_packet', 'sub_packet').distinct()[0]
                if len(is_work_pac_exist) > 1:
                    list_of_internal = Externalerrors.objects.filter(project=pro_id,center=cen_id,date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
                else:
                    list_of_internal = Externalerrors.objects.filter(project=pro_id,center=cen_id,date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
    internal_list, table_headers = [], []
    final_internal_drilldown = {}
    final_internal_drilldown['type'] = chart_type
    for i in list_of_internal:
        internal_list.append({'audited_count':i[1], 'total_errors':i[2],'date':str(i[3])})
        audited_value = 0
        Error_count = 0 
        for ans in internal_list:
            if ans['audited_count']:
                audited_value = audited_value + ans['audited_count']
            if ans['total_errors']:
                Error_count = Error_count + ans['total_errors']
            if ans['audited_count'] > 0:
                accuracy = 100 - ((float(ans['total_errors']) / float(ans['audited_count']))) * 100
            else:
                accuracy = 0
            accuracy_agg = float('%.2f' % round(accuracy, 2))
            ans['accuracy'] = accuracy_agg
    if len(internal_list) > 0:
            table_headers = ['date','audited_count','total_errors']

    final_internal_drilldown['data'] = internal_list
    final_internal_drilldown['table_headers'] = table_headers
    final_internal_drilldown['audited_value'] = audited_value
    final_internal_drilldown['Error_count'] = Error_count
    return final_internal_drilldown

def internal_chart_data(pro_id,cen_id,to_date,work_packet,chart_type,project):
    if (project == 'Probe' and chart_type == 'External Accuracy Trends') or (project == "Ujjivan" and chart_type in ['External Accuracy Trends','Internal Accuracy Trends']) or (project == 'IBM' and chart_type == 'External Accuracy Trends'):
        if len(to_date) == 2:
            final_internal_drilldown = {}
            final_val_res = internal_chart_data_multi(pro_id,cen_id,to_date,work_packet,chart_type,project)
            final_internal_drilldown['type'] = chart_type
            final_internal_drilldown['project'] = project
            final_internal_drilldown['data'] = final_val_res['data']
            final_internal_drilldown['table_headers'] = final_val_res['table_headers']
            return final_internal_drilldown
        else:
            packets_list = work_packet.split('_')
            packets_list_type = ''
            accuracy_query_set = accuracy_query_generations(pro_id, cen_id, to_date[0], work_packet)
            if project == 'Ujjivan' and chart_type == 'Internal Accuracy Trends':
                list_of_internal = Internalerrors.objects.filter(**accuracy_query_set).values_list('employee_id','work_packet','total_errors','date','sub_packet')
            elif chart_type == 'External Accuracy Trends':
                list_of_internal = Externalerrors.objects.filter(**accuracy_query_set).values_list('employee_id','work_packet','total_errors','date','sub_packet')
            final_internal_drilldown = {}
            final_internal_drilldown['type'] = chart_type
            final_internal_drilldown['project'] = project
            list_ext_data, table_headers = [], []
            for i in list_of_internal:
                per_day_value = RawTable.objects.filter(employee_id=i[0],date=i[3],work_packet=i[1],sub_packet=i[4]).values_list('per_day')
                try:
                    per_day_value = per_day_value[0][0]
                except:
                    per_day_value = 0
                if per_day_value > 0:
                    list_ext_data.append({'date':str(i[3]),'total_errors': i[2],'productivity': per_day_value})
                Productivity_value = 0
                Error_count = 0
                for ans in list_ext_data:
                    if ans['total_errors']:
                        Error_count = Error_count + ans['total_errors']
                    if ans['productivity']:
                        Productivity_value = Productivity_value + ans['productivity']
                    accuracy = 100 - ((float(ans['total_errors']) / float(ans['productivity']))) * 100
                    accuracy_agg = float('%.2f' % round(accuracy, 2))
                    ans['accuracy'] = accuracy_agg
                if len(list_ext_data) >0:
                    table_headers = ['date', 'productivity', 'total_errors']
            final_internal_drilldown['data'] = list_ext_data
            final_internal_drilldown['table_headers'] = table_headers
            final_internal_drilldown['Productivity_value'] = Productivity_value
            final_internal_drilldown['Error_count'] = Error_count
            return final_internal_drilldown

    if chart_type == 'Internal Accuracy Trends':
        if len(to_date) == 2:
            final_internal_drilldown = {}
            final_val_res = internal_chart_data_multi(pro_id,cen_id,to_date,work_packet,chart_type,project)
            final_internal_drilldown['type'] = chart_type
            final_internal_drilldown['project'] = project
            final_internal_drilldown['data'] = final_val_res['data']
            final_internal_drilldown['table_headers'] = final_val_res['table_headers']
            return final_internal_drilldown
        else:
            packets_list = work_packet.split('_')
            packets_list_type = ''
            if len(packets_list) == 2:
                sub_project_statuts = Internalerrors.objects.filter(project=pro_id,center=cen_id, date=to_date[0]).values_list('sub_project', flat=True)
                sub_project_statuts = filter(None, sub_project_statuts)
                if len(sub_project_statuts) > 0:
                    sub_project, work_packet = work_packet.split('_')
                    list_of_internal = Internalerrors.objects.filter(project=pro_id, center=cen_id, date=to_date[0],sub_project=sub_project,work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
                work_packet_statuts = Internalerrors.objects.filter(center=cen_id, project=pro_id,date=to_date[0]).values_list('work_packet',flat=True)
                work_packet_statuts = filter(None, work_packet_statuts)
                if len(sub_project_statuts) == 0 and len(work_packet_statuts) > 0:
                    work_packet, sub_packet = work_packet.split('_')
                    is_work_pac_exist = Internalerrors.objects.filter(project=pro_id, center=cen_id, date=to_date[0]).values_list('work_packet','sub_packet').distinct()[0]
                    if len(is_work_pac_exist) > 1:
                        list_of_internal = Internalerrors.objects.filter(project=pro_id, center=cen_id, date=to_date[0],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
                    else:
                        list_of_internal = Internalerrors.objects.filter(project=pro_id, center=cen_id, date=to_date[0],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
            elif len(packets_list) == 3:
                if '_' in work_packet:
                    sub_project, work_packet, sub_packet = work_packet.split('_')
                    list_of_internal = Internalerrors.objects.filter(project=pro_id,center=cen_id,  date=to_date[0],work_packet=work_packet, sub_packet=sub_packet).values_list('employee_id','audited_errors','total_errors','date')
                else:
                    is_work_pac_exist = Internalerrors.objects.filter(project=pro_id,center=cen_id, date=to_date[0]).values_list('work_packet','sub_packet').distinct()[0]
                    if len(is_work_pac_exist) > 1:
                        list_of_internal = Internalerrors.objects.filter(project=pro_id, date=to_date[0], center=cen_id, work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
                    else:
                        list_of_internal = Internalerrors.objects.filter(project=pro_id, center=cen_id, date=to_date[0],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
            else:
                sub_project_statuts = Internalerrors.objects.filter(project=pro_id,center=cen_id, date=to_date[0]).values_list('sub_project', flat=True)
                sub_project_statuts = filter(None, sub_project_statuts)
                if len(sub_project_statuts) > 0:
                    packets_list_type = 'sub_project'
                    is_work_pac_exist = Internalerrors.objects.filter(project=pro_id, center=cen_id, date=to_date[0]).values_list('sub_project','work_packet','sub_packet').distinct()[0]
                    if len(is_work_pac_exist) > 1:
                        list_of_internal = Internalerrors.objects.filter(project=pro_id, center=cen_id, date=to_date[0],sub_project=packets_list[0]).values_list('employee_id','audited_errors','total_errors','date')
                    else:
                        list_of_internal = Internalerrors.objects.filter(project=pro_id,center=cen_id, date=to_date[0],sub_project=packets_list[0]).values_list('employee_id','audited_errors','total_errors','date')
                else:
                    packets_list_type = 'work_packet'
                    is_work_pac_exist = Internalerrors.objects.filter(project=pro_id,center=cen_id,  date=to_date[0]).values_list('work_packet','sub_packet').distinct()[0]
                    if len(is_work_pac_exist) > 1:
                        list_of_internal = Internalerrors.objects.filter(project=pro_id,center=cen_id,  date=to_date[0],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
                    else:
                        list_of_internal = Internalerrors.objects.filter(project=pro_id,center=cen_id, date=to_date[0],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')

    else:
        packets_list = work_packet.split('_')
        packets_list_type = ''
        final_external_drilldown = {}
        if len(to_date)>1:
            final_val_res = internal_chart_data_multi(pro_id, cen_id, to_date, work_packet, chart_type, project)
            final_external_drilldown['type'] = chart_type
            final_external_drilldown['project'] = project
            final_external_drilldown['data'] = final_val_res['data']
            final_external_drilldown['table_headers'] = final_val_res['table_headers']
            return final_external_drilldown
        if len(packets_list) == 2:
            sub_project_statuts = Externalerrors.objects.filter(project=pro_id,center=cen_id, date=to_date[0]).values_list('sub_project', flat=True)
            sub_project_statuts = filter(None, sub_project_statuts)
            if len(sub_project_statuts) > 0:
                sub_project, work_packet = work_packet.split('_')
                list_of_internal = Externalerrors.objects.filter(project=pro_id, center=cen_id, date=to_date[0],sub_project=sub_project,work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
            work_packet_statuts = Externalerrors.objects.filter(project=pro_id,center=cen_id, date=to_date[0]).values_list('work_packet', flat=True)
            work_packet_statuts = filter(None, work_packet_statuts)
            if len(sub_project_statuts) == 0 and len(work_packet_statuts) > 0:
                work_packet, sub_packet = work_packet.split('_')
                is_work_pac_exist = Externalerrors.objects.filter(project=pro_id,center=cen_id, date=to_date[0]).values_list('work_packet','sub_packet').distinct()
                if len(is_work_pac_exist) > 1:
                    list_of_internal = Externalerrors.objects.filter(project=pro_id,center=cen_id, date=to_date[0],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
                else:
                    list_of_internal = Externalerrors.objects.filter(project=pro_id,center=cen_id, date=to_date[0],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
        elif len(packets_list) == 3:
            if '_' in work_packet:
                sub_project, work_packet, sub_packet = work_packet.split('_')
                list_of_internal = Externalerrors.objects.filter(center=cen_id, project=pro_id, date=to_date[0],work_packet=work_packet,sub_packet=sub_packet).values_list('employee_id','audited_errors','total_errors','date')
            else:
                is_work_pac_exist = Externalerrors.objects.filter(project=pro_id,center=cen_id, date=to_date[0]).values_list('work_packet','sub_packet').distinct()[0]
                if len(is_work_pac_exist) > 1:
                    list_of_internal = Externalerrors.objects.filter(project=pro_id,center=cen_id, date=to_date[0],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
                else:
                    list_of_internal = Externalerrors.objects.filter(project=pro_id, center=cen_id, date=to_date[0],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
        else:
            sub_project_statuts = Externalerrors.objects.filter(project=pro_id,center=cen_id, date=to_date[0]).values_list('sub_project', flat=True)
            sub_project_statuts = filter(None, sub_project_statuts)
            if len(sub_project_statuts) > 0:
                packets_list_type = 'sub_project'
                is_work_pac_exist = Externalerrors.objects.filter(project=pro_id, center=cen_id, date=to_date[0]).values_list('sub_project','work_packet','sub_packet').distinct()[0]
                if len(is_work_pac_exist) > 1:
                    list_of_internal = Externalerrors.objects.filter(project=pro_id, center=cen_id,sub_project=packets_list[0], date=to_date[0]).values_list('employee_id', 'audited_errors', 'total_errors','date')
                else:
                    list_of_internal = Externalerrors.objects.filter(project=pro_id, center=cen_id,sub_project=packets_list[0], date=to_date[0]).values_list('employee_id', 'audited_errors', 'total_errors','date')
            else:
                packets_list_type = 'work_packet'
                is_work_pac_exist = Externalerrors.objects.filter(project=pro_id, center=cen_id, date=to_date[0]).values_list('work_packet','sub_packet').distinct()
                if len(is_work_pac_exist) > 1:
                    list_of_internal = Externalerrors.objects.filter(project=pro_id, center=cen_id, date=to_date[0],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')
                else:
                    list_of_internal = Externalerrors.objects.filter(project=pro_id, center=cen_id, date=to_date[0],work_packet=work_packet).values_list('employee_id','audited_errors','total_errors','date')

    final_internal_drilldown = {}
    final_internal_drilldown['type'] = chart_type
    final_internal_drilldown['project'] = project
    internal_list, table_headers = [], []
    for i in list_of_internal:
        internal_list.append({'audited_count':i[1], 'total_errors':i[2],'date':str(i[3])})
        audited_value, Error_count = 0, 0
        for ans in internal_list:
            if ans['audited_count']:
                audited_value = audited_value + ans['audited_count']
            if ans['total_errors']:
                Error_count = Error_count + ans['total_errors']
            if ans['audited_count']>0:
                accuracy = 100 - ((float(ans['total_errors']) / float(ans['audited_count']))) * 100
            else:
                accuracy = 0
            accuracy_agg = float('%.2f' % round(accuracy, 2))
            ans['accuracy'] = accuracy_agg

        if len(internal_list)>0:
            table_headers = ['date','audited_count','total_errors']
    final_internal_drilldown['data'] = internal_list
    final_internal_drilldown['table_headers'] = table_headers
    final_internal_drilldown['audited_value'] = audited_value
    final_internal_drilldown['Error_count'] = Error_count
    return final_internal_drilldown

def productivity_chart_data_multi(pro_id,cen_id,to_date,work_packet,chart_type,project):
    final_productivity_drilldown = {}
    final_productivity_drilldown['type'] = chart_type
    final_productivity_drilldown['project'] = project
    packets_list = work_packet.split('_')
    packets_list_type = ''
    if len(packets_list) == 2:
        sub_project_statuts = RawTable.objects.filter(project=pro_id,center=cen_id, date__range=[to_date[0], to_date[-1]]).values_list('sub_project', flat=True)
        sub_project_statuts = filter(None, sub_project_statuts)
        if len(sub_project_statuts) > 0:
            sub_project, work_packet = work_packet.split('_')
            detail_list = RawTable.objects.filter(center=cen_id, project=pro_id, date__range=[to_date[0], to_date[-1]],sub_project=sub_project, work_packet=work_packet).values_list('employee_id', 'per_day', 'sub_packet','date')
            packets_list_type = 'sub_packet'
        else:
            packets_list_type = 'sub_packet'
            is_work_pac_exist = RawTable.objects.filter(project=pro_id, center=cen_id, date__range=[to_date[0], to_date[-1]]).values_list('work_packet','sub_packet').distinct()[0]
            if len(is_work_pac_exist) > 1:
                detail_list = RawTable.objects.filter(project=pro_id,center=cen_id,  date__range=[to_date[0], to_date[-1]],work_packet=packets_list[0]).values_list('employee_id', 'per_day','date')
            else:
                detail_list = RawTable.objects.filter(project=pro_id, center=cen_id, date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id', 'per_day','date')
        packet_dict = []
    elif len(packets_list) == 3:
        if '_' in work_packet:
            sub_project,work_packet,sub_packet = work_packet.split('_')
            detail_list = RawTable.objects.filter(project=pro_id,center=cen_id,date__range=[to_date[0], to_date[-1]],work_packet=work_packet,sub_packet=sub_packet).values_list('employee_id','per_day','date')
        else:
            is_work_pac_exist = RawTable.objects.filter(project=pro_id,center=cen_id, date__range=[to_date[0], to_date[-1]]).values_list('work_packet','sub_packet').distinct()[0]
            if len(is_work_pac_exist) > 1:
                detail_list = RawTable.objects.filter(project=pro_id,center=cen_id, date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','per_day','sub_packet','date')
            else:
                detail_list = RawTable.objects.filter(project=pro_id,center=cen_id, date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id','per_day','date')
        packet_dict = []
    else:
        sub_project_statuts = RawTable.objects.filter(project=pro_id,center=cen_id, date__range=[to_date[0], to_date[-1]]).values_list('sub_project', flat=True)
        sub_project_statuts = filter(None, sub_project_statuts)
        if len(sub_project_statuts) > 0:
            is_work_pac_exist = RawTable.objects.filter(project=pro_id,center=cen_id, date__range=[to_date[0], to_date[-1]]).values_list('sub_project','work_packet','sub_packet').distinct()[0]
            if len(is_work_pac_exist) > 1:
                detail_list = RawTable.objects.filter(project=pro_id,center=cen_id, date__range=[to_date[0], to_date[-1]],sub_project=packets_list[0]).values_list('employee_id', 'per_day', 'work_packet','date')
            else:
                detail_list = RawTable.objects.filter(project=pro_id,center=cen_id, date__range=[to_date[0], to_date[-1]],sub_project=packets_list[0]).values_list('employee_id','per_day','date')
            packets_list_type = 'work_packet'
        else:
            sub_packet_statuts = RawTable.objects.filter(project=pro_id,center=cen_id, date__range=[to_date[0], to_date[-1]]).values_list('sub_packet', flat=True)
            sub_packet_statuts = filter(None, sub_packet_statuts) 
            packets_list_type = 'work_packet'
            if sub_packet_statuts:
                detail_list = RawTable.objects.filter(project=pro_id,center=cen_id, date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id', 'per_day', 'sub_packet','date')
                packets_list_type = 'sub_packet'
            else: 
                is_work_pac_exist = RawTable.objects.filter(project=pro_id, center=cen_id, date__range=[to_date[0], to_date[-1]]).values_list('work_packet','sub_packet').distinct()[0]
                if len(is_work_pac_exist) > 1:
                    detail_list = RawTable.objects.filter(project=pro_id, center=cen_id, date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id', 'per_day','date')
                else:
                    detail_list = RawTable.objects.filter(project=pro_id, center=cen_id, date__range=[to_date[0], to_date[-1]],work_packet=work_packet).values_list('employee_id', 'per_day','date')
        packet_dict = []
    table_headers = []
    for i in detail_list:
        if i[1]>0:
            if len(i) == 3:
                packet_dict.append({'name':i[0],'done':i[1],'date': str(i[2])})
            else:
                packet_dict.append({'name':i[0],'done':i[1],packets_list_type:i[2], 'date': str(i[3])})
        if len(packet_dict) > 0:
            table_headers = ['date','name', 'done']
            if len(packet_dict[0]) == 4:
                table_headers = ['date','name', packets_list_type, 'done']
    final_productivity_drilldown['data'] = packet_dict
    final_productivity_drilldown['table_headers'] = table_headers
    return final_productivity_drilldown

def productivity_chart_data(pro_id,cen_id,to_date,work_packet,chart_type,project):
    final_productivity_drilldown = {} 
    final_productivity_drilldown['type'] = chart_type
    final_productivity_drilldown['project'] = project
    if len(to_date) == 2:
        final_val_result = productivity_chart_data_multi(pro_id,cen_id,to_date,work_packet,chart_type,project)
        return final_val_result
    else:
        packets_list = work_packet.split('_')
        packets_list_type = ''
        if len(packets_list) == 2:
            sub_project_statuts = RawTable.objects.filter(project=pro_id,center=cen_id, date=to_date[0]).values_list('sub_project',flat=True)
            sub_project_statuts  = filter(None,sub_project_statuts)
            if len(sub_project_statuts) > 0:
                sub_project,work_packet = work_packet.split('_')
                detail_list = RawTable.objects.filter(project=pro_id,center=cen_id,date=to_date[0],sub_project=sub_project,work_packet=work_packet).values_list('employee_id','per_day','sub_packet')
                packets_list_type = 'sub_packet'
            else:
                packets_list_type = 'sub_packet'
                is_work_pac_exist = RawTable.objects.filter(project=pro_id, center=cen_id,date=to_date[0]).values_list('work_packet','sub_packet').distinct()[0]
                if len(is_work_pac_exist) > 1:
                    detail_list = RawTable.objects.filter(project=pro_id,center=cen_id,date=to_date[0],work_packet=packets_list[0]).values_list('employee_id','per_day')
                else:
                    detail_list = RawTable.objects.filter(project=pro_id,center=cen_id,date=to_date[0],work_packet=work_packet).values_list('employee_id','per_day')
            packet_dict = []
        elif len(packets_list) == 3:
            if '_' in work_packet:
                sub_project,work_packet,sub_packet = work_packet.split('_')
                detail_list = RawTable.objects.filter(project=pro_id,center=cen_id,date=to_date[0],work_packet=work_packet,sub_packet=sub_packet).values_list('employee_id','per_day')
            else:
                is_work_pac_exist = RawTable.objects.filter(project=pro_id,center=cen_id,date=to_date[0]).values_list('work_packet','sub_packet').distinct()[0]
                if len(is_work_pac_exist) > 1:
                    detail_list = RawTable.objects.filter(project=pro_id, center=cen_id, date=to_date[0],work_packet=work_packet).values_list('employee_id','per_day','sub_packet')
                else:
                    detail_list = RawTable.objects.filter(project=pro_id,center=cen_id,date=to_date[0],work_packet=work_packet).values_list('employee_id','per_day')
            packet_dict = []
        else:
            sub_project_statuts = RawTable.objects.filter(project=pro_id,center=cen_id, date=to_date[0]).values_list('sub_project', flat=True)
            sub_project_statuts = filter(None, sub_project_statuts)
            if len(sub_project_statuts) > 0:
                packets_list_type = 'work_packet'
                is_work_pac_exist = RawTable.objects.filter(project=pro_id,center=cen_id,date=to_date[0]).values_list('sub_project','work_packet','sub_packet').distinct()[0]
                if len(is_work_pac_exist) > 1:
                    detail_list = RawTable.objects.filter(project=pro_id,center=cen_id, date=to_date[0],sub_project=packets_list[0]).values_list('employee_id', 'per_day','work_packet', 'date')
                else:
                    detail_list = RawTable.objects.filter(project=pro_id,center=cen_id,date=to_date[0],sub_project=packets_list[0]).values_list('employee_id','per_day','date')
            else:
                sub_packet_statuts = RawTable.objects.filter(project=pro_id,center=cen_id,date=to_date[0]).values_list('sub_packet', flat=True)
                sub_packet_statuts = filter(None, sub_packet_statuts) 
                packets_list_type = 'work_packet'
                if sub_packet_statuts:
                    detail_list = RawTable.objects.filter(project=pro_id,center=cen_id,date=to_date[0],work_packet=work_packet).values_list('employee_id', 'per_day','sub_packet')
                    packets_list_type = 'sub_packet'
                else:
                    packets_list_type = 'work_packet'
                    is_work_pac_exist = RawTable.objects.filter(project=pro_id, center=cen_id, date=to_date[0]).values_list('work_packet','sub_packet').distinct()[0]
                    if len(is_work_pac_exist) > 1:
                        detail_list = RawTable.objects.filter(project=pro_id, center=cen_id, date=to_date[0],work_packet=work_packet).values_list('employee_id', 'per_day')
                    else:
                        detail_list = RawTable.objects.filter(project=pro_id,center=cen_id, date=to_date[0],work_packet=work_packet).values_list('employee_id', 'per_day','date')
            packet_dict = []
        table_headers = []
        for i in detail_list:
            if i[1] > 0:
                if len(i) == 2:
                    packet_dict.append({'name':i[0],'done':i[1]})

                else:
                    packet_dict.append({'name': i[0], 'done': i[1], packets_list_type: i[2]})
        if len(packet_dict) > 0:
            table_headers = ['name', 'done']
            if len(packet_dict[0])==3:
                table_headers = ['name',packets_list_type, 'done']
        final_productivity_drilldown['data'] = packet_dict
        final_productivity_drilldown['table_headers'] = table_headers
        return final_productivity_drilldown

def chart_data(request):
    user_id = request.user.id
    project = request.GET['project'].strip(' - ')
    center = request.GET['center'].strip(' - ')
    drilldown_res = Customer.objects.filter(name_id=user_id).values_list('is_drilldown')
    if not drilldown_res:
        drilldown_res = ''
    else:
        drilldown_res = drilldown_res[0][0]
    user_group = request.user.groups.values_list('name', flat=True)[0]
    if drilldown_res or user_group != 'customer':
        pro_id = Project.objects.filter(name=project).values_list('id')[0][0]
        cen_id = Center.objects.filter(name=center).values_list('id')[0][0]
        chart_type = str(request.GET['type'])
        if chart_type == 'Internal Accuracy' or chart_type == 'External Accuracy' or chart_type == 'Internal_Bar_Pie' or chart_type == 'External_Bar_Pie':
            from_ = datetime.datetime.strptime(request.GET['from'], '%Y-%m-%d').date()
            to_ = datetime.datetime.strptime(request.GET['to'], '%Y-%m-%d').date()
        else:
            drilldown_dates = [] 
            date_taken = request.GET['date']
            if 'to' in request.GET['date']:
                to_date_1 = date_taken.split('to')[0].strip()
                to_date_2 = date_taken.split('to')[1].strip()
                drilldown_dates.append(to_date_1)
                drilldown_dates.append(to_date_2)
            else:
                to_date = datetime.datetime.strptime(request.GET['date'], '%Y-%m-%d').date()
                drilldown_dates.append(to_date)
        work_packet = str(request.GET['packet'])
        if ' # ' in work_packet:
            work_packet = work_packet.replace(' # ','#')
        if ' and ' in work_packet:
            work_packet = work_packet.replace(' and ',' & ')
        final_dict = ''
        if chart_type == 'Internal Accuracy Trends' or chart_type == 'External Accuracy Trends':
            final_dict = internal_chart_data(pro_id,cen_id,drilldown_dates,work_packet,chart_type,project)
        elif chart_type == 'Internal Accuracy' or chart_type == 'External Accuracy' or chart_type == 'Internal_Bar_Pie' or chart_type == 'External_Bar_Pie':
            final_dict = internal_bar_data(pro_id, cen_id, from_, to_, work_packet, chart_type,project)
        else:
            final_dict = productivity_chart_data(pro_id,cen_id,drilldown_dates,work_packet,chart_type,project)
        return json_HttpResponse(final_dict)
    else:
        return json_HttpResponse('Drilldown disabled')
