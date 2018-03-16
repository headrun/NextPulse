import datetime
import redis
from api.models import *
from api.basics import *
import collections
from django.db.models import Max, Sum
from api.query_generations import query_set_generation
from api.graph_settings import graph_data_alignment_color
from common.utils import getHttpResponse as json_HttpResponse


def fte_trend_scope(date_list, prj_id, center, level_structure_key):

    final_dict,data_dict,packet_dict = {}, {}, {}
    req_dict, packet_dict = {}, {}
    date_arr,trend_list = [],  []
    Fte_arr = []
    fte_trend_data = []
    if (prj_id == 2 or prj_id == 3):
        filter_params, _packet = getting_required_params(level_structure_key, prj_id, center, date_list)
        raw_params = filter_params
        raw_query = RawTable.objects.filter(**filter_params)
        dates = RawTable.objects.filter(project=prj_id, center=center, date__range=[date_list[0], date_list[-1]]).values_list('date', flat=True).distinct()
        target_params = filter_params
        target_params.pop('date__range', None)
        target_params['from_date__lte'] = date_list[0]
        target_params['to_date__gte'] = date_list[-1]
        target_params['target_type'] = 'FTE Target'

        if level_structure_key.has_key('sub_project'):
            if _packet == 'sub_project':
                work_done = raw_query.values('date',_packet,'work_packet','sub_packet').annotate(w_d=Sum('per_day'))
                target_query = Targets.objects.filter(**target_params).values('from_date','to_date',_packet,'work_packet','sub_packet').annotate(target=Sum('target_value'))
                packet_details = raw_query.values_list(_packet, flat=True).distinct()
                captured_date = []
                for check_date in dates:
                    for index in work_done:
                        if str(check_date) == str(index['date']):
                            captured_date.append(index['date'])

                for missdate in list(set(dates)-set(captured_date)):
                    for pack in packet_details:
                        Fte_arr.append({"date":str(missdate),"sub_project":pack ,"work_packet":'' ,"sub_packet": '',"result": 0 })

            elif _packet == 'work_packet':
                work_done = raw_query.values('date','sub_project',_packet,'sub_packet').annotate(w_d=Sum('per_day'))
                target_query = Targets.objects.filter(**target_params).values('from_date','to_date','sub_project',_packet,'sub_packet').annotate(target=Sum('target_value'))                    
                packet_details = raw_query.values_list(_packet, flat=True).distinct()
                captured_date = []
                for check_date in dates:
                    for index in work_done:
                        if str(check_date) == str(index['date']):
                            captured_date.append(index['date'])

                for missdate in list(set(dates)-set(captured_date)):
                    for pack in packet_details:
                        Fte_arr.append({"date":str(missdate),"sub_project":filter_params['sub_project'],"work_packet":pack ,"sub_packet": '',"result": 0 })
            else:
                work_done = raw_query.values('date','sub_project','work_packet',_packet).annotate(w_d=Sum('per_day'))
                target_query = Targets.objects.filter(**target_params).values('from_date','to_date','sub_project','work_packet',_packet).annotate(target=Sum('target_value'))
                packet_details = raw_query.values_list(_packet, flat=True).distinct()
                captured_date = []
                for check_date in dates:
                    for index in work_done:
                        if str(check_date) == str(index['date']):
                            captured_date.append(index['date'])

                for missdate in list(set(dates)-set(captured_date)):
                    if filter_params.has_key('sub_packet'):
                        Fte_arr.append({"date":str(missdate),"sub_project":filter_params['sub_project'],"work_packet":filter_params['work_packet'],"sub_packet":filter_params['sub_packet'],"result": 0 })

            packet_list = [];
            for r_data in work_done:
                for tar in target_query:
                    if (tar['from_date'] <= r_data['date'] <= tar['to_date']):
                        if ((r_data['work_packet'] == tar['work_packet']) and (r_data['sub_packet'] == tar['sub_packet']) and (r_data['sub_project'] == tar['sub_project'])):
                            Fte_arr.append({"date":str(r_data['date']),"sub_project":r_data['sub_project'],"work_packet":r_data['work_packet'],"sub_packet":r_data['sub_packet'],"result": (float(r_data['w_d'])/float(tar['target'])) })

            seen = set()
            Fte_arr_new = []
            for dup in Fte_arr:
                t = tuple(dup.items())
                if t not in seen:
                    seen.add(t)
                    Fte_arr_new.append(dup)

            Fte_a = []
            for check_date in dates:
                packet_list = []
                for index in Fte_arr_new:
                    if str(check_date) == index['date']:
                        packet_list.append(index[_packet])
                if len(packet_list) > 0:
                    packet_list = sorted(list(set(packet_list)))
                    packet_list = map(str, packet_list)
                    for pack in packet_details:
                        if str(pack) not in packet_list:
                            if _packet == 'sub_project':
                                Fte_arr_new.append({"date": check_date, _packet:pack,'work_packet':'' ,"sub_packet":'', "result":0})
                            elif _packet == 'work_packet':
                                Fte_arr_new.append({"date": check_date,"sub_project":'', _packet:pack,'sub_packet':'', "result":0})
                            else:
                                Fte_arr_new.append({"date": check_date,"sub_project":'', _packet:pack,'work_packet':'', "result":0})

            if _packet == 'sub_project':
                tmp_obj = {}
                for tmp in Fte_arr_new:
                    if tmp_obj.has_key(str(tmp['date'])):
                        if tmp_obj[str(tmp['date'])].has_key(tmp['sub_project']):
                            tmp_obj[str(tmp['date'])][tmp['sub_project']] = tmp_obj[str(tmp['date'])][tmp['sub_project']] + tmp['result']
                        else:
                            tmp_obj[str(tmp['date'])].update({tmp['sub_project'] : tmp['result']})
                    else:
                        tmp_obj[str(tmp['date'])] = {tmp['sub_project'] : tmp['result']}

                ordi = collections.OrderedDict(tmp_obj)
                tmp_obj = sorted(ordi.items(), key=lambda x: x)
                fte_trend_data = []
                for tk in tmp_obj:
                    date_arr.append(tk[0])
                    val = 0
                    for k, v in tk[1].iteritems():
                        v = float('%.2f' % round(v, 2))
                        if not data_dict.has_key(k):
                            data_dict[k] = [v]
                        else:
                            data_dict[k].append(v)
                        val += v
                    val = float('%.2f' % round(val, 2))
                    fte_trend_data.append(val)

            elif _packet == 'work_packet':
                tmp_obj = {}
                for tmp in Fte_arr_new:
                    if tmp_obj.has_key(str(tmp['date'])):
                        if tmp_obj[str(tmp['date'])].has_key(tmp['sub_project']+'_'+tmp['work_packet']):
                            tmp_obj[str(tmp['date'])][tmp['sub_project']+'_'+tmp['work_packet']] = tmp_obj[str(tmp['date'])][tmp['sub_project']+'_'+tmp['work_packet']] + tmp['result']
                        else:
                            tmp_obj[str(tmp['date'])].update({tmp['sub_project']+'_'+tmp['work_packet'] : tmp['result']})
                    else:
                        tmp_obj[str(tmp['date'])] = {tmp['sub_project']+'_'+tmp['work_packet'] : tmp['result']}

                ordi = collections.OrderedDict(tmp_obj)
                tmp_obj = sorted(ordi.items(), key=lambda x: x)
                fte_trend_data = []
                for tk in tmp_obj:
                    date_arr.append(tk[0])
                    val = 0
                    for k, v in tk[1].iteritems():
                        v = float('%.2f' % round(v, 2))
                        key = k.split('_')
                        if not data_dict.has_key(key[1]):
                            data_dict[key[1]] = [v]
                        else:
                            data_dict[key[1]].append(v)
                        val += v
                    val = float('%.2f' % round(val, 2))
                    fte_trend_data.append(val)
            else:
                tmp_obj = {}
                for tmp in Fte_arr_new:
                    if tmp_obj.has_key(str(tmp['date'])):
                        if tmp_obj[str(tmp['date'])].has_key(tmp['sub_project']+"_"+tmp['work_packet']+"_"+tmp['sub_packet']):
                            tmp_obj[str(tmp['date'])][tmp['sub_project']+"_"+tmp['work_packet']+"_"+tmp['sub_packet'] ]= tmp_obj[str(tmp['date'])][tmp['sub_project']+"_"+tmp['work_packet']+"_"+tmp['sub_packet']] + tmp['result']
                        else:
                            tmp_obj[str(tmp['date'])].update({tmp['sub_project']+"_"+tmp['work_packet']+"_"+tmp['sub_packet'] : tmp['result']})
                    else:
                        tmp_obj[str(tmp['date'])] = {tmp['sub_project']+"_"+tmp['work_packet']+"_"+tmp['sub_packet'] : tmp['result']}

                ordi = collections.OrderedDict(tmp_obj)
                tmp_obj = sorted(ordi.items(), key=lambda x: x)
                fte_trend_data = []
                for tk in tmp_obj:
                    date_arr.append(tk[0])
                    val = 0
                    for k, v in tk[1].iteritems():
                        key = k.split('_')
                        v = float('%.2f' % round(v, 2))
                        if not data_dict.has_key(key[2]):
                            data_dict[key[2]] = [v]
                        else:
                            data_dict[key[2]].append(v)
                        val += v
                    val = float('%.2f' % round(val, 2))
                    fte_trend_data.append(val)

        elif level_structure_key.has_key('work_packet'):
            if _packet == 'work_packet':
                work_done = raw_query.values('date',_packet,'sub_packet').annotate(w_d=Sum('per_day'))
                target_query = Targets.objects.filter(**target_params).values('from_date','to_date',_packet,'sub_packet').annotate(target=Sum('target_value'))                
                packet_details = raw_query.values_list(_packet, flat=True).distinct()
                captured_date = []
                for check_date in dates:
                    for index in work_done:
                        if str(check_date) == str(index['date']):
                            captured_date.append(index['date'])
                for missdate in list(set(dates)-set(captured_date)):
                    for pack in packet_details:
                        Fte_arr.append({"date":str(missdate),"sub_project":filter_params['sub_project'],"work_packet":pack ,"sub_packet": '',"result": 0 })
            else:
                work_done = raw_query.values('date','work_packet',_packet).annotate(w_d=Sum('per_day'))
                target_query = Targets.objects.filter(**target_params).values('from_date','to_date','work_packet',_packet).annotate(target=Sum('target_value'))
                packet_details = raw_query.values_list(_packet, flat=True).distinct()
                captured_date = []
                for check_date in dates:
                    for index in work_done:
                        if str(check_date) == str(index['date']):
                            captured_date.append(index['date'])

                for missdate in list(set(dates)-set(captured_date)):
                    if filter_params.has_key('sub_packet'):
                        Fte_arr.append({"date":str(missdate),"work_packet":filter_params['work_packet'],"sub_packet":filter_params['sub_packet'],"result": 0 })
            packet_list = [];
            for r_data in work_done:
                for tar in target_query:
                    if (tar['from_date'] <= r_data['date'] <= tar['to_date']):
                        if tar['sub_packet']:
                            if ((r_data['work_packet'] == tar['work_packet']) and (r_data['sub_packet'] == tar['sub_packet'])):
                                Fte_arr.append({"date":str(r_data['date']),"work_packet":r_data['work_packet'],"sub_packet":r_data['sub_packet'],"result": (float(r_data['w_d'])/float(tar['target'])) })
                            else:
                                pass
                        else:
                            if ((r_data['work_packet'] == tar['work_packet'])):
                                Fte_arr.append({"date":str(r_data['date']),"work_packet":r_data['work_packet'],"sub_packet": '', "result": (float(r_data['w_d'])/float(tar['target'])) })
                            else:
                                pass
            seen = set()
            Fte_arr_new = []
            for dup in Fte_arr:
                t = tuple(dup.items())
                if t not in seen:
                    seen.add(t)
                    Fte_arr_new.append(dup)
            Fte_a = []
            for check_date in dates:
                packet_list = []
                for index in Fte_arr_new:
                    if str(check_date) == index['date']:
                        packet_list.append(index['work_packet'])

                if len(packet_list) > 0:
                    packet_list = sorted(list(set(packet_list)))
                    packet_list = map(str, packet_list)
                    for pack in packet_details:
                        if str(pack) not in packet_list:
                            if _packet == 'work_packet':
                                Fte_arr_new.append({"date": check_date, _packet:pack,'sub_packet':'', "result":0})
                            else:
                                Fte_arr_new.append({"date": check_date, _packet:pack,'work_packet':'', "result":0})

            if _packet == 'work_packet':
                tmp_obj = {}
                for tmp in Fte_arr_new:
                    if tmp_obj.has_key(str(tmp['date'])):
                        if tmp_obj[str(tmp['date'])].has_key(tmp['work_packet']+"_"+tmp['sub_packet']):
                            tmp_obj[str(tmp['date'])][tmp['work_packet']+"_"+tmp['sub_packet']] = tmp_obj[str(tmp['date'])][tmp['work_packet']+"_"+tmp['sub_packet']] + tmp['result']
                        else:
                            tmp_obj[str(tmp['date'])].update({tmp['work_packet']+"_"+tmp['sub_packet'] : tmp['result']})
                    else:
                        tmp_obj[str(tmp['date'])] = {tmp['work_packet']+"_"+tmp['sub_packet'] : tmp['result']}

                ordi = collections.OrderedDict(tmp_obj)
                tmp_obj = sorted(ordi.items(), key=lambda x: x)
                for tk in tmp_obj:
                    date_arr.append(tk[0])
                    val = 0
                    for k, v in tk[1].iteritems():
                        v = float('%.2f' % round(v, 2))
                        key = k.split("_")
                        if not data_dict.has_key(key[0]):
                            data_dict[key[0]] = [v]
                        else:
                            data_dict[key[0]].append(v)
                        val += v
                    val = float('%.2f' % round(val, 2))
                    fte_trend_data.append(val)
            else:
                tmp_obj = {}
                for tmp in Fte_arr_new:
                    if tmp_obj.has_key(str(tmp['date'])):
                        if tmp_obj[str(tmp['date'])].has_key(tmp['work_packet']+"_"+tmp['sub_packet']):
                            tmp_obj[str(tmp['date'])][tmp['work_packet']+"_"+tmp['sub_packet'] ]= tmp_obj[str(tmp['date'])][tmp['work_packet']+"_"+tmp['sub_packet']] + tmp['result']
                        else:
                            tmp_obj[str(tmp['date'])].update({tmp['work_packet']+"_"+tmp['sub_packet'] : tmp['result']})
                    else:
                        tmp_obj[str(tmp['date'])] = {tmp['work_packet']+"_"+tmp['sub_packet'] : tmp['result']}

                ordi = collections.OrderedDict(tmp_obj)
                tmp_obj = sorted(ordi.items(), key=lambda x: x)
                fte_trend_data = []
                for tk in tmp_obj:
                    date_arr.append(tk[0])
                    val = 0
                    for k, v in tk[1].iteritems():
                        key = k.split('_')
                        v = float('%.2f' % round(v, 2))
                        if not data_dict.has_key(key[1]):
                            data_dict[key[1]] = [v]
                        else:
                            data_dict[key[1]].append(v)
                        val += v
                    val = float('%.2f' % round(val, 2))
                    fte_trend_data.append(val)

    date_comp = (list(set(date_arr)))
    final_dict['fte_scope'] = data_dict
    req_dict['total_fte'] = fte_trend_data
    final_dict['fte_trend'] = req_dict
    final_dict['date'] = date_comp

    return final_dict



