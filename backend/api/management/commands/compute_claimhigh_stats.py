from django.core.management.base import BaseCommand, CommandError

from api.models import ClaimsSummary, ClaimsAll
import json

class Command(BaseCommand):

    def handle(self, *args, **options):
        months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        locs = ['Loc1', 'Loc2', 'Loc3']
        plans = ['Plan1', 'Plan2', 'Plan3', 'Plan4', 'Plan5']
        for month in months:
            for _loc in locs:
                for plan in plans:
                    top_diseases, claims_proc, claims_healthy = {}, {}, {}
                    claims_smoking, claims_bmi, claims_loc, claims_age, claims_cutoff = {}, {}, {}, {}, {}
                    avg_claims = {'pocket':0, 'insurer':0}
                    claims_trends = {'total': 0, 'total_amount': 0}
                    for obj in ClaimsSummary.objects.filter(month=month, plan=plan, location=_loc):
                        claims_trends['total'] = claims_trends.get('total', 0) + obj.total
                        claims_trends['total_amount'] = claims_trends.get('total_amount', 0) + float(obj.total_amount)

                        avg_claims['insurer'] = avg_claims.get('insurer', 0) + float(obj.insuer)
                        avg_claims['pocket'] = avg_claims.get('pocket', 0) + float(obj.pocket)

                        disease = top_diseases.get(obj.disease, {'total':0, 'patients':0, 'total_amount':0, 'proc':{}})
                        disease['total'] += obj.total
                        disease['patients'] += obj.patients
                        disease['total_amount'] += float(obj.total_amount)
                        proc = disease['proc'].get(obj.procedure, {'total':0, 'total_amount':0})
                        proc['total'] += float(obj.total)
                        proc['total_amount'] += float(obj.total_amount)
                        disease['proc'][obj.procedure] = proc
                        top_diseases[obj.disease] = disease

                        proc = claims_proc.get(obj.procedure, {'total':0, 'patients':0, 'total_amount':0})
                        proc['total'] += obj.total
                        proc['patients'] += obj.patients
                        proc['total_amount'] += float(obj.total_amount)
                        claims_proc[obj.procedure] = proc

                        health = claims_healthy.get(obj.disease, {'healthy':0, 'unhealthy':0})
                        health['healthy'] += obj.healthy
                        health['unhealthy'] += obj.unhealthy
                        claims_healthy[obj.disease] = health

                        smoking = claims_smoking.get(obj.disease, {'smoker':0, 'non_smoker':0})
                        smoking['smoker'] += obj.smoker
                        smoking['non_smoker'] += obj.non_smoker
                        claims_smoking[obj.disease] = smoking

                        bmi = claims_bmi.get(obj.disease, {'obese':0, 'fit':0})
                        bmi['obese'] += obj.obese
                        bmi['fit'] += obj.fit
                        claims_bmi[obj.disease] = bmi

                        loc = claims_loc.get(obj.location, {'total':0, 'total_amount':0})
                        loc['total'] += float(obj.total)
                        loc['total_amount'] += float(obj.total_amount)
                        claims_loc[obj.location] = loc

                        age_group = claims_age.get(obj.age_group, {'total':0, 'total_amount':0})
                        age_group['total'] += float(obj.total)
                        age_group['total_amount'] += float(obj.total_amount)
                        claims_age[obj.age_group] = age_group

                        if  obj.total_amount > 125000:
                            cutoff = claims_cutoff.get(obj.disease, {'total':0, 'total_amount':0})
                            cutoff['total'] += float(obj.total)
                            cutoff['total_amount'] += float(obj.total_amount)
                            claims_cutoff[obj.disease] = cutoff

                    final_data = {}
                    final_data['claims_trends'] = claims_trends
                    final_data['avg_claims'] = avg_claims
                    final_data['top_diseases'] = top_diseases
                    final_data['claims_proc'] = claims_proc
                    final_data['claims_healthy'] = claims_healthy
                    final_data['claims_smoking'] = claims_smoking
                    final_data['claims_bmi'] = claims_bmi
                    final_data['claims_loc'] = claims_loc
                    final_data['claims_age'] = claims_age
                    final_data['claims_cutoff'] = claims_cutoff

                    doc = {}
                    doc['month'] = month
                    doc['plan'] = plan
                    doc['location'] = _loc
                    doc['data'] = json.dumps(final_data)

                    ClaimsAll.objects.create(**doc)
