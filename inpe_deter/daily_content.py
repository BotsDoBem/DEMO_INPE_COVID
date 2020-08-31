__author__='thiagocastroferreira'

import sys
sys.path.append('../')
import inpe_deter.inpe as inpe

import xml.etree.ElementTree as ET
from xml.dom import minidom
from db.model import DeforestationDeterINPE
from mongoengine.queryset.visitor import Q

from random import shuffle

def format_input(messages):
    for i, msg in enumerate(messages):
        str_intent = msg['intent']

        attributes = sorted(msg['attributes'].items(), key=lambda x: x[0].lower())

        parameters = ','.join([w[0]+'=\"'+str(w[1])+'\"' for w in attributes])
        str_msg = str_intent + '(' + parameters + ')'

        delex_attributes = '(' + ','.join([attr[0] + '=' + attr[0].upper() for attr in attributes]) + ')'
        delex_format = str_intent + delex_attributes

        messages[i]['str_msg'] = str_msg
        messages[i]['delex_msg'] = delex_format

    return sorted(messages, key=lambda x: x['str_msg'])


def to_xml(data):
    tree = ET.fromstring('<?xml version="1.0"?><entries></entries>')

    for row in sorted(data, key=lambda x: x[1]):
        messages, date = row

        entry = ET.SubElement(tree, 'entry')
        entry.attrib['date'] = date

        meaning_xml = ET.SubElement(entry, 'meaning')
        for msg in messages:
            unit_xml = ET.SubElement(meaning_xml, 'unit')
            unit_xml.text = msg['str_msg']

        ET.SubElement(entry, 'ordering')
        ET.SubElement(entry, 'structuring')
        ET.SubElement(entry, 'lexicalization')
        ET.SubElement(entry, 'references')
        ET.SubElement(entry, 'text')

    rough_string = ET.tostring(tree, encoding='utf-8', method='xml')
    xml = minidom.parseString(rough_string).toprettyxml(indent="    ")
    return xml.encode('utf-8').decode('utf-8')


def content(date, state, city, uc):
    ano, mes, dia = date.year, date.month, date.day
    messages = []
    if uc:
        area, main_cause = inpe.desmatamento_UC_dia(date, uc)
        month_deforestation, daily_accumulation = inpe.desmatamento_UC_mes(mes=mes, ano=ano, uc=uc)
        daily_alert = {
            'intent': 'DAILY_ALERT',
            'attributes': {
                'year': ano, 'month': mes, 'day': dia,
                'location': 'deter-amz', 'state': state, 'city': city, 'uc': uc,
                'area': area
            }
        }
        if daily_accumulation > 1:
            daily_alert['attributes']['daily_accumulation'] = daily_accumulation
        messages.append(daily_alert)

        if month_deforestation != area:
            total_deforestation = {
                'intent': 'TOTAL_DEFORESTATION',
                'attributes': {
                    'year': ano, 'month': mes,
                    'location': 'deter-amz', 'state': state, 'city': city, 'uc': uc,
                    'area': month_deforestation
                }
            }
            messages.append(total_deforestation)

        cause = {
            'intent': 'CAUSE',
            'attributes': {
                'year': ano, 'month': mes,
                'location': 'deter-amz', 'state': state, 'city': city, 'uc': uc,
                'cause': main_cause
            }
        }
        messages.append(cause)
    else:
        area, main_cause = inpe.desmatamento_municipio_dia(date, city)
        month_deforestation, daily_accumulation = inpe.desmatamento_municipio_mes(mes=mes, ano=ano, city=city)
        daily_alert = {
            'intent': 'DAILY_ALERT',
            'attributes': {
                'year': ano, 'month': mes, 'day': dia,
                'location': 'deter-amz', 'state': state, 'city': city,
                'area': area
            }
        }
        if daily_accumulation > 1:
            daily_alert['attributes']['daily_accumulation'] = daily_accumulation
        messages.append(daily_alert)

        if month_deforestation != area:
            total_deforestation = {
                'intent': 'TOTAL_DEFORESTATION',
                'attributes': {
                    'year': ano, 'month': mes,
                    'location': 'deter-amz', 'state': state, 'city': city,
                    'area': month_deforestation
                }
            }
            messages.append(total_deforestation)

        cause = {
            'intent': 'CAUSE',
            'attributes': {
                'year': ano, 'month': mes,
                'location': 'deter-amz', 'state': state, 'city': city,
                'cause': main_cause
            }
        }
        messages.append(cause)

    messages = format_input(messages)
    return messages, str(date)


def run():
    dates = DeforestationDeterINPE.objects().distinct('date')

    data_city, data_uc = [], []
    for date in dates:
        print(date)
        query = DeforestationDeterINPE.objects(Q(date=date) & (Q(cause='DESMATAMENTO_CR') |
                                                            Q(cause='DESMATAMENTO_VEG') | Q(cause='MINERACAO')))
        cities = query.distinct('city')
        for city in cities:
            try:
                state = DeforestationDeterINPE.objects((Q(date=date) & Q(city=city) & Q(UC=None)) &
                                                       (Q(cause='DESMATAMENTO_CR') | Q(cause='DESMATAMENTO_VEG') |
                                                        Q(cause='MINERACAO'))).distinct('state')[0]

                messages, date_ = content(date=date, state=state, city=city, uc=None)
                data_city.append((messages, date_))
            except:
                pass

        ucs = query.distinct('UC')
        for uc in ucs:
            try:
                state = DeforestationDeterINPE.objects((Q(date=date) & Q(UC=uc)) &
                                                       (Q(cause='DESMATAMENTO_CR') | Q(cause='DESMATAMENTO_VEG') |
                                                        Q(cause='MINERACAO'))).distinct('state')[0]

                messages, date_ = content(date=date, state=state, city=None, uc=uc)
                data_uc.append((messages, date_))
            except:
                pass

    return data_city, data_uc

if __name__ == '__main__':
    data_city, data_uc = run()

    data = data_city + data_uc
    shuffle(data)

    dataprec = {}
    for row in data:
        messages, date = row

        delex = ' '.join([w['delex_msg'] for w in messages])
        if delex not in dataprec:
            dataprec[delex] = []
        if len(dataprec[delex]) < 5:
            intent = [w for w in messages if w['intent'] == 'DAILY_ALERT'][0]
            if intent['attributes']['area'] > 1:
                dataprec[delex].append(row)

    final = []
    for delex in dataprec:
        final.extend(dataprec[delex])
    str_xml = to_xml(final)

    with open('inpe_daily_corpus.xml', 'w') as f:
        f.write(str_xml)