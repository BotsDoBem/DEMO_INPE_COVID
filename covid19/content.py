__author__='thiagocastroferreira'

from datetime import datetime, timedelta
from db.model import CoronaVirus
import numpy as np

import xml.etree.ElementTree as ET
from xml.dom import minidom


MSGS = [
    'TOTAL_CASES',
    'TOTAL_DEATHS',
    'ACTIVE_CASES',
    'NEW_CASES',
    'NEW_DEATHS'
    'CASES_VARIATION_LAST_DAY',
    'DEATHS_VARIATION_LAST_DAY',
    'ACTIVE_CASES_VARIATION_LAST_DAY'
]

def format_input(messages):
    intents = []
    for str_intent in messages:
        # sort attributes in alphabetical order
        attributes = sorted(messages[str_intent].items(), key=lambda x: x[0].lower())

        parameters = ','.join([w[0]+'=\"'+str(w[1])+'\"' for w in attributes])
        str_msg = str_intent + '(' + parameters + ')'

        delex_attributes = '(' + ','.join([attr[0] + '=' + attr[0].upper() for attr in attributes]) + ')'
        delex_format = str_intent + delex_attributes

        intent = {
            'intent': str_intent,
            'attributes': messages[str_intent],
            'str_msg': str_msg,
            'delex_msg': delex_format
        }
        intents.append(intent)

    return sorted(intents, key=lambda x: x['str_msg'])


def to_xml(data):
    tree = ET.fromstring('<?xml version="1.0"?><entries></entries>')

    for row in data:
        meaning, date = row
        entry = ET.SubElement(tree, 'entry')
        entry.attrib['date'] = date

        meaning_xml = ET.SubElement(entry, 'meaning')
        for msg in meaning:
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


def content(date, country='Brazil', offset=0):
    dbdata = CoronaVirus.objects(date__lte=date, country=country).order_by('date')[offset:]
    data, messages = [], {}
    for i, case in enumerate(dbdata):
        messages = {}

        cases = case.cases
        deaths = case.deaths
        active_cases = case.cases - (case.recovered + case.deaths)
        new_cases, new_deaths, cases_variation, deaths_variation, active_variation = 0, 0, 0, 0, 0

        if len(data) > 0:
            # cases
            new_cases = cases - data[i-1]['cases']
            if data[i-1]['cases'] > 0:
                cases_variation = round((cases - data[i-1]['cases']) / data[i-1]['cases'], 2)
            # deaths
            new_deaths = deaths - data[i-1]['deaths']
            if data[i-1]['deaths'] > 0:
                deaths_variation = round((deaths - data[i-1]['deaths']) / data[i-1]['deaths'], 2)

            # active_cases
            if data[i-1]['active_cases'] > 0:
                active_variation = round((active_cases - data[i-1]['active_cases']) / data[i-1]['active_cases'], 2)

        # If active cases decrease after 22:50 (21:50 Oregon time), prioritize this. Otherwise, display total cases and deaths.
        now = datetime.now() - timedelta(hours=3)
        limit = datetime(now.year, now.month, now.day, 22, 50, 0, 0)
        if active_variation < 0 and now > limit:
            messages['ACTIVE_CASES'] = { 'active_cases': active_cases }
            messages['ACTIVE_CASES_VARIATION_LAST_DAY'] = { 'variation': active_variation, 'trend': 'low' }
        else:
            messages['TOTAL_CASES'] = {'cases': cases}
            if deaths > 0:
                messages['TOTAL_DEATHS'] = {'deaths': deaths}

        # NEW_DEATHS
        prev_new_deaths = [w['new_deaths'] for w in data if w['new_deaths'] > 0]

        if len(prev_new_deaths) > 0:
            max_new_deaths = max(prev_new_deaths)
            avg_new_deaths, std_new_deaths = np.mean(prev_new_deaths), np.std(prev_new_deaths)

            if new_deaths > max_new_deaths:
                messages['NEW_DEATHS'] = { 'deaths': new_deaths, 'highest': True }
            elif new_deaths > avg_new_deaths+std_new_deaths:
                messages['NEW_DEATHS'] = { 'deaths': new_deaths, 'highest': False }
                messages['DEATHS_VARIATION_LAST_DAY'] = { 'variation': deaths_variation, 'trend': 'high' }

        # NEW_CASES
        prev_new_cases = [w['new_cases'] for w in data if w['new_cases'] > 0]

        if len(prev_new_cases) > 0:
            max_new_cases = max(prev_new_cases)
            avg_new_cases, std_new_cases = np.mean(prev_new_cases), np.std(prev_new_cases)

            if new_cases > max_new_cases:
                messages['NEW_CASES'] = { 'cases': new_cases, 'highest': True }
            elif new_cases > avg_new_cases+std_new_cases:
                messages['NEW_CASES'] = { 'cases': new_cases, 'highest': False }
                messages['CASES_VARIATION_LAST_DAY'] = { 'variation': cases_variation, 'trend': 'high' }

        #     print(case.date, case.cases, case.deaths, new_deaths, round(deaths_variation, 2))
        data.append({
            'cases': cases,
            'deaths': deaths,
            'active_cases': active_cases,
            'new_cases': new_cases,
            'new_deaths': new_deaths,
            'cases_variation': cases_variation,
            'deaths_variation': deaths_variation,
            'active_variation': active_variation,
            'date': case.date
        })

    # format input
    intents = format_input(messages)
    return intents