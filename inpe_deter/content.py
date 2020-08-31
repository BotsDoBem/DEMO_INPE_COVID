__author__='thiagocastroferreira'

import sys
sys.path.append('../')
import inpe_deter.inpe as inpe
import numpy as np

from inpe_deter.load_data import setting_dados_deter
import xml.etree.ElementTree as ET
from xml.dom import minidom

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


def content(month, year):
    month, year = int(month), int(year)
    messages = []

    # TOTAL DEFORESTATION
    total_deforestation = inpe.desmatamento_total_por_mes(year, month)
    messages.append({
        'intent': 'TOTAL_DEFORESTATION',
        'attributes': {
            'area': round(total_deforestation),
            'year': int(year),
            'month': int(month),
            'location': 'deter-amz'
        }
    })

    # LAST_MONTH_VARIATION_DEFORESTATION
    month_variation = inpe.dado_variacao_percentual_por_mes(year, month) # dado_variacao_percentual_por_mes
    if month_variation > 0:
        messages.append({
            'intent': 'LAST_MONTH_VARIATION_DEFORESTATION',
            'attributes': {
                'variation': round(month_variation, 2),
                'month': int(month),
                'year': int(year),
                'location': 'deter-amz'
            }
        })

    # 12_MONTH_VARIATION_DEFORESTATION
    year_variation = inpe.dado_variacao_percentual_12meses(year, month)
    if year_variation > 0 and year_variation != month_variation:
        messages.append({
            'intent': '12_MONTH_VARIATION_DEFORESTATION',
            'attributes': {
                'variation': round(year_variation, 2),
                'month': int(month),
                'year': int(year),
                'location': 'deter-amz'
            }
        })

    # state
    states = inpe.desmatamento_estados_por_mes(year, month) # dado_estados_por_mes
    avg, std = np.mean(list(states.values())), np.std(list(states.values()))

    state_messages = []
    for state in states:
        if states[state] > avg + std:
            state_messages.append({
                'intent': 'TOTAL_DEFORESTATION',
                'attributes': {
                    'area': round(states[state]),
                    'year': int(year),
                    'month': int(month),
                    'location': 'deter-amz',
                    'state': state
                }
        })
    state_messages = sorted(state_messages, key=lambda x: x['attributes']['area'], reverse=True)[:1]
    messages.extend(state_messages)

    # city
    cities = inpe.desmatamento_municipios_por_mes(year, month)
    avg, std = np.mean(list(cities.values())), np.std(list(cities.values()))

    city_messages = []
    for state, city in cities.keys():
        if cities[(state, city)] > avg + std:
            city_messages.append({
                'intent': 'TOTAL_DEFORESTATION',
                'attributes': {
                    'area': round(cities[(state, city)]),
                    'year': int(year),
                    'month': int(month),
                    'location': 'deter-amz',
                    'state': state,
                    'city': city
                }
            })
    city_messages = sorted(city_messages, key=lambda x: x['attributes']['area'], reverse=True)[:1]
    messages.extend(city_messages)

    # reserve
    reserves = inpe.desmatamento_UCs_por_mes(year, month)
    avg, std = np.mean(list(reserves.values())), np.std(list(reserves.values()))

    reserve_messages = []
    for UC in reserves:
        if reserves[UC] > avg + std:
            estados, municipios = inpe.get_UC_location(UC)
            reserve_messages.append({
                'intent': 'TOTAL_DEFORESTATION',
                'attributes': {
                    'area': round(reserves[UC]),
                    'year': int(year),
                    'month': int(month),
                    'location': 'deter-amz',
                    'state': ','.join(estados),
                    'city': ','.join(municipios),
                    'UC': UC
                }
            })

    reserve_messages = sorted(reserve_messages, key=lambda x: x['attributes']['area'], reverse=True)[:1]
    messages.extend(reserve_messages)

    # cause
    causes = inpe.desmatamento_cause_por_mes(year, month)

    max_area = max(causes.values())
    cause = [cause for cause, area in causes.items() if area == max_area][0]

    cause_message = {
        'intent': 'CAUSE',
        'attributes': {
            'area': round(max_area),
            'cause': cause,
            'year': int(year),
            'month': int(month),
            'location': 'deter-amz'
        }
    }
    messages.append(cause_message)

    date = '-'.join([str(year), str(month), '01'])
    messages = format_input(messages)
    return messages, date


def run():
    dados, estados, municipios, UCs, causas = setting_dados_deter()

    # get months
    dates = []
    for row in dados['features']:
        year = row["properties"]["g"][0]
        month = row["properties"]["g"][1]
        dates.append((month, year))
    dates = set(dates)

    data = []
    for month, year in dates:
        print(month, year)
        messages, date = content(month, year)
        data.append((messages, date))

    return data

if __name__ == '__main__':
    data = run()

    str_xml = to_xml(data)

    with open('inpe_corpus.xml', 'w') as f:
        f.write(str_xml)