__author__='thiagocastroferreira'

from collections import Counter
from db.operations import get_state_uc, get_state_city
from random import randint
import re

def train(trainset):
    references = {}
    for unit in trainset:
        for reference in unit['references']:
            entity = reference['entity']
            gender = reference['gender']
            number = reference['number']
            status = reference['status']
            refex = reference['refex'].strip()
            refex = refex[0].lower() + refex[1:]

            if entity not in references:
                references[entity] = {}
            if status not in references[entity]:
                references[entity][status] = []

            references[entity][status].append((refex, gender, number))

    for entity in references:
        for status in references[entity]:
            references[entity][status] = Counter(references[entity][status]).items()
            references[entity][status] = [{ 'refex': k[0], 'gender': k[1], 'number': k[2], 'frequency': v } for k, v in references[entity][status]]
    return references


def format_value(value):
    value = '{:,.2f}'.format(float(value))
    value = value.split('.')
    value[0] = value[0].replace(',', '.')
    if value[1] == '00':
        return  value[0]
    else:
        return ','.join(value)

def generate_month(entity):
    if entity == '1':
        return { 'refex': 'janeiro', 'gender': 'male', 'number': 'singular' }
    elif entity == '2':
        return { 'refex': 'fevereiro', 'gender': 'male', 'number': 'singular' }
    elif entity == '3':
        return { 'refex': 'março', 'gender': 'male', 'number': 'singular' }
    elif entity == '4':
        return { 'refex': 'abril', 'gender': 'male', 'number': 'singular' }
    elif entity == '5':
        return { 'refex': 'maio', 'gender': 'male', 'number': 'singular' }
    elif entity == '6':
        return { 'refex': 'junho', 'gender': 'male', 'number': 'singular' }
    elif entity == '7':
        return { 'refex': 'julho', 'gender': 'male', 'number': 'singular' }
    elif entity == '8':
        return { 'refex': 'agosto', 'gender': 'male', 'number': 'singular' }
    elif entity == '9':
        return { 'refex': 'setembro', 'gender': 'male', 'number': 'singular' }
    elif entity == '10':
        return { 'refex': 'outubro', 'gender': 'male', 'number': 'singular' }
    elif entity == '11':
        return { 'refex': 'novembro', 'gender': 'male', 'number': 'singular' }
    elif entity == '12':
        return { 'refex': 'dezembro', 'gender': 'male', 'number': 'singular' }

def generate_uc(entity, grammar):
    # state = get_state_uc(entity)
    if entity in grammar:
        gender = grammar[entity]['new'][0]['gender']
        reference = ['a']
        if gender == 'male':
            reference = ['o']
    else:
        reference, gender = ['a'], 'female'
        if 'parque' in entity.lower():
            reference, gender = ['o'], 'male'
    reference.append(entity)
    # reference.append('(' + state + ')')
    return { 'refex': ' '.join(reference), 'number': 'singular', 'gender': gender }

def generate_city(entity):
    # state = get_state_city(entity)
    reference = entity #+ ' (' + state + ')'
    return { 'refex': reference, 'number': 'singular', 'gender': 'male' }

def generate_state(entity):
    if entity == 'PA':
        return { 'refex': 'Pará', 'number': 'singular', 'gender': 'male' }
    elif entity == 'AC':
        return { 'refex': 'Acre', 'number': 'singular', 'gender': 'male' }
    elif entity == 'AM':
        return { 'refex': 'Amazonas', 'number': 'singular', 'gender': 'male' }
    elif entity == 'AP':
        return { 'refex': 'Amapá', 'number': 'singular', 'gender': 'male' }
    elif entity == 'MA':
        return { 'refex': 'Maranhão', 'number': 'singular', 'gender': 'male' }
    elif entity == 'MT':
        return { 'refex': 'Mato Grosso', 'number': 'singular', 'gender': 'male' }
    elif entity == 'RO':
        return { 'refex': 'Rondônia', 'number': 'singular', 'gender': 'male' }
    elif entity == 'RR':
        return { 'refex': 'Roraima', 'number': 'singular', 'gender': 'male' }
    elif entity == 'TO':
        return { 'refex': 'Tocantins', 'number': 'singular', 'gender': 'male' }


def generate(tag, entity, status, grammar, strategy='random'):
    type_ = re.findall(r'(.+)_[0-9]+', tag)[0].lower()
    if type_ in ['deaths', 'cases', 'active_cases']:
        entity = float(entity)
        gender, number = 'male', 'singular'
        if entity > 1:
            number = 'plural'

        return { 'refex': format_value(entity), 'number': number, 'gender': gender }
    elif type_ == 'variation':
        gender, number = 'male', 'plural'
        return { 'refex': format_value(abs(float(entity) * 100)) + '%', 'number': number, 'gender': gender }
    elif type_ == 'month':
        return generate_month(entity)
    elif type_ in 'area':
        entity = float(entity)
        gender, number = 'male', 'singular'
        if entity > 1:
            number = 'plural'
        return { 'refex': format_value(entity) + ' km²', 'number': number, 'gender': gender }
    elif type_ in ['daily_accumulation', 'day']:
        entity = float(entity)
        gender, number = 'male', 'singular'
        if entity > 1:
            number = 'plural'
        return { 'refex': format_value(entity), 'number': number, 'gender': gender }
    elif type_ == 'uc':
        return generate_uc(entity, grammar)
    elif type_ == 'city':
        return generate_city(entity)
    elif type_ == 'state':
        return generate_state(entity)
    elif entity in grammar:
        try:
            references = grammar[entity][status]
        except:
            if 'new' in grammar[entity]:
                references = grammar[entity]['new']
            else:
                references = grammar[entity]['old']
        if strategy == 'random':
            result = references[randint(0, len(references)-1)]
        else:
            result = sorted(references, key=lambda x: x['frequency'], reverse=True)[0]
        return result
    else:
        return { 'refex': entity, 'gender': 'male', 'number': 'singular' }

def realize(templates, grammar, strategy='random'):
    paragraphs, entitychain = [], []
    for pidx, p in enumerate(templates):
        paragraph = []
        for sntidx, sentence in enumerate(p):
            template, entitymap = sentence['template'], sentence['entitymap']

            for z, tag in enumerate(template.split()):
                isTag = False
                if tag in entitymap:
                    entity = entitymap[tag]
                    # set reference status
                    status = 'new'
                    if entity in entitychain:
                        status = 'old'
                    # generate referring expression
                    result = generate(tag, entity, status, grammar, strategy)
                    refex, gender, number = result['refex'], result['gender'], result['number']
                    # replace referring expression
                    template = template.replace(tag + ' ', refex + ' ', 1)
                    # replace person, gender and number on verb phrase
                    template = template.replace('gender=' + tag, 'gender=' + gender)
                    template = template.replace('number=' + tag, 'number=' + number)
                    template = template.replace('person=' + tag, 'person=3rd')

                    entitychain.append(entity)
                elif tag == 'COUNTRY_1':
                    entity = 'Brasil'
                    # set reference status
                    status = 'new'
                    if entity in entitychain:
                        status = 'old'
                    result = generate(tag, entity, status, grammar, strategy)

                    refex, gender, number = result['refex'], result['gender'], result['number']
                    # replace referring expression
                    template = template.replace(tag + ' ', refex + ' ', 1)
                    # replace person, gender and number on verb phrase
                    template = template.replace('gender=' + tag, 'gender=' + gender)
                    template = template.replace('number=' + tag, 'number=' + number)
                    template = template.replace('person=' + tag, 'person=3rd')

                    entitychain.append(entity)
                elif tag == 'INSTITUTE_1':
                    entity = 'INPE'
                    # set reference status
                    status = 'new'
                    if entity in entitychain:
                        status = 'old'
                    result = generate(tag, entity, status, grammar, strategy)

                    refex, gender, number = result['refex'], result['gender'], result['number']
                    # replace referring expression
                    template = template.replace(tag + ' ', refex + ' ', 1)
                    # replace person, gender and number on verb phrase
                    template = template.replace('gender=' + tag, 'gender=' + gender)
                    template = template.replace('number=' + tag, 'number=' + number)
                    template = template.replace('person=' + tag, 'person=3rd')

                    entitychain.append(entity)
            paragraph.append(template)
        paragraphs.append(paragraph)
    return paragraphs