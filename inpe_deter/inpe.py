__author__='thiagocastroferreira'

import sys
sys.path.append('../')

import operator
from collections import Counter
from datetime import datetime
from mongoengine.queryset.visitor import Q
from db.model import DeforestationDeterINPE

def get_states():
    return DeforestationDeterINPE.objects().distinct('state')


def get_cities():
    return DeforestationDeterINPE.objects().distinct('city')


def get_UCs():
    ucs = DeforestationDeterINPE.objects().distinct('UC')
    return [w for w in ucs if w]


def get_UC_location(UC):
    data = DeforestationDeterINPE.objects(UC=UC)
    states = data.distinct('state')
    cities = data.distinct('city')
    return states, cities


def get_causes():
    return DeforestationDeterINPE.objects().distinct('cause')


def desmatamento_total_por_mes(ano, mes):
    start_date = datetime(ano, mes, 1)
    if mes == 12:
        end_date = datetime(ano + 1, 1, 1)
    else:
        end_date = datetime(ano, mes+1, 1)
    # get all cases with date greater than or equal start date and less than end_date
    data = DeforestationDeterINPE.objects((Q(date__gte=start_date) & Q(date__lt=end_date)) &
                                          (Q(cause='DESMATAMENTO_CR') | Q(cause='DESMATAMENTO_VEG') |
                                           Q(cause='MINERACAO')))
    # return the sum of city_area
    return data.sum('city_area')


def dado_variacao_percentual_por_mes(ano, mes):
    if mes == 1:
        prev_mes = 12
        prev_ano = ano - 1
    else:
        prev_mes = mes - 1
        prev_ano = ano

    prev_area = desmatamento_total_por_mes(prev_ano, prev_mes)
    area = desmatamento_total_por_mes(ano, mes)

    if prev_area == 0:
        return 0
    else:
        return (area - prev_area) / prev_area


def dado_variacao_percentual_12meses(ano, mes):
    prev_ano = ano - 1
    prev_area = desmatamento_total_por_mes(prev_ano, mes)
    area = desmatamento_total_por_mes(ano, mes)

    if prev_area == 0:
        return 0
    else:
        return (area - prev_area) / prev_area


def desmatamento_estados_por_mes(ano, mes):
    states = get_states()

    start_date = datetime(ano, mes, 1)
    if mes == 12:
        end_date = datetime(ano + 1, 1, 1)
    else:
        end_date = datetime(ano, mes + 1, 1)

    state2area = {}
    for state in states:
        area = DeforestationDeterINPE.objects((Q(date__gte=start_date) & Q(date__lt=end_date)) &
                                              (Q(cause='DESMATAMENTO_CR') | Q(cause='DESMATAMENTO_VEG') |
                                               Q(cause='MINERACAO')) & Q(state=state)).sum('city_area')
        state2area[state] = area
    return state2area


def desmatamento_municipios_por_mes(ano, mes):
    cities = get_cities()

    start_date = datetime(ano, mes, 1)
    if mes == 12:
        end_date = datetime(ano + 1, 1, 1)
    else:
        end_date = datetime(ano, mes + 1, 1)

    city2area = {}
    for city in cities:
        state = DeforestationDeterINPE.objects(city=city).distinct('state')[0]
        area = DeforestationDeterINPE.objects((Q(date__gte=start_date) & Q(date__lt=end_date)) &
                                              (Q(cause='DESMATAMENTO_CR') | Q(cause='DESMATAMENTO_VEG') |
                                               Q(cause='MINERACAO')) & Q(city=city)).sum('city_area')
        city2area[(state, city)] = area
    return city2area


def desmatamento_municipio_mes(city, ano, mes):

    start_date = datetime(ano, mes, 1)
    if mes == 12:
        end_date = datetime(ano + 1, 1, 1)
    else:
        end_date = datetime(ano, mes + 1, 1)

    query = DeforestationDeterINPE.objects((Q(date__gte=start_date) & Q(date__lt=end_date)) &
                                          (Q(cause='DESMATAMENTO_CR') | Q(cause='DESMATAMENTO_VEG') |
                                           Q(cause='MINERACAO')) & Q(city=city))
    area = query.sum('city_area')
    dias = query.distinct('date')
    return area, len(dias)


def desmatamento_municipio_dia(date, city):
    query = DeforestationDeterINPE.objects((Q(date=date) & Q(city=city) & Q(UC=None)) &
                                          (Q(cause='DESMATAMENTO_CR') | Q(cause='DESMATAMENTO_VEG') |
                                           Q(cause='MINERACAO')))

    area = query.sum('city_area')
    causes = [row.cause for row in query]
    main_cause = max(Counter(causes), key=operator.itemgetter(1))
    return area, main_cause


def desmatamento_UC_dia(date, UC):
    query = DeforestationDeterINPE.objects((Q(date=date) & Q(UC=UC)) &
                                          (Q(cause='DESMATAMENTO_CR') | Q(cause='DESMATAMENTO_VEG') |
                                           Q(cause='MINERACAO')))


    causes = [row.cause for row in query]
    main_cause = max(Counter(causes), key=operator.itemgetter(1))
    area = query.sum('uc_area')
    return area, main_cause


def desmatamento_UCs_por_mes(ano, mes):
    UCs = get_UCs()

    start_date = datetime(ano, mes, 1)
    if mes == 12:
        end_date = datetime(ano + 1, 1, 1)
    else:
        end_date = datetime(ano, mes + 1, 1)

    uc2area = {}
    for uc in UCs:
        area = DeforestationDeterINPE.objects((Q(date__gte=start_date) & Q(date__lt=end_date)) &
                                              (Q(cause='DESMATAMENTO_CR') | Q(cause='DESMATAMENTO_VEG') |
                                               Q(cause='MINERACAO')) & Q(UC=uc)).sum('uc_area')
        uc2area[uc] = area
    return uc2area


def desmatamento_UC_mes(uc, ano, mes):
    start_date = datetime(ano, mes, 1)
    if mes == 12:
        end_date = datetime(ano + 1, 1, 1)
    else:
        end_date = datetime(ano, mes + 1, 1)

    query = DeforestationDeterINPE.objects((Q(date__gte=start_date) & Q(date__lt=end_date)) &
                                           (Q(cause='DESMATAMENTO_CR') | Q(cause='DESMATAMENTO_VEG') |
                                            Q(cause='MINERACAO')) & Q(UC=uc))
    area = query.sum('uc_area')
    dias = query.distinct('date')
    return area, len(dias)


def desmatamento_cause_por_mes(ano, mes):
    causes = get_causes()

    start_date = datetime(ano, mes, 1)
    if mes == 12:
        end_date = datetime(ano + 1, 1, 1)
    else:
        end_date = datetime(ano, mes + 1, 1)

    cause2area = {}
    for cause in [c for c in causes if c in ['DESMATAMENTO_CR', 'DESMATAMENTO_VEG', 'MINERACAO']]:
        area = DeforestationDeterINPE.objects(date__gte=start_date, date__lt=end_date, cause=cause).sum('city_area')
        cause2area[cause] = area
    return cause2area