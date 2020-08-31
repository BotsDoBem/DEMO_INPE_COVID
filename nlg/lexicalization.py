__author__='thiagocastroferreira'

from random import randint

def prepare_input(sentence):
    entitymap, valuemap, freq = {}, {}, {}

    src = []
    # set mapping between tags and entities
    for message in sorted(sentence, key=lambda msg: msg['order']):
        attributes = message['attributes']
        for attr in attributes:
            # parse attribute value to string
            value = str(attributes[attr])
            # treat special case of highest attribute
            if attr == 'highest':
                valuemap[value] = value
            else: #elif attributes[attr] not in valuemap:
                if attr not in freq:
                    freq[attr] = 0
                freq[attr] += 1
                tag = attr.upper() + '_' + str(freq[attr])

                entitymap[tag] = value
                valuemap[value] = tag

        attributes = sorted(attributes.items(), key=lambda x: x[0].lower())
        delex_attributes = '(' + ','.join([attr[0] + '=' + valuemap[str(attr[1])] for attr in attributes]) + ')'
        src.append(message['intent'] + delex_attributes)

    src = ';'.join(src)
    return src, entitymap


def train(trainset):
    trainlex = {}
    for unit in trainset:
        messages = unit['messages']
        templates = unit['templates']
        struct = [(msg['paragraph'], msg['sentence']) for msg in messages]

        for paragraph, sentence in struct:
            template = [tmp for tmp in templates if tmp['paragraph'] == paragraph and tmp['sentence'] == sentence]
            template = template[0]['template'].strip()

            fmessages = [msg for msg in messages if msg['paragraph'] == paragraph and msg['sentence'] == sentence]
            src, _ = prepare_input(fmessages)

            if src not in trainlex:
                trainlex[src] = {}
            if template not in trainlex[src]:
                trainlex[src][template] = 0
            trainlex[src][template] += 1

    for src in trainlex:
        trainlex[src] = [{ 'template': k, 'frequency': v } for k, v in trainlex[src].items()]
    return trainlex


def generate(paragraphs, grammar, strategy='random'):
    templates, struct = [], []
    for paragraph in paragraphs:
        paragraph_struct, paragraph_template = [], []
        for sentence in paragraph:
            start, end = 0, len(sentence)

            while start < len(sentence):
                src, entitymap = prepare_input(sentence[start:end])
                if src in grammar:
                    candidates = grammar[src]

                    if strategy == 'random':
                        template = candidates[randint(0, len(candidates)-1)]['template']
                    else:
                        template = sorted(candidates, key=lambda x: x['frequency'], reverse=True)[0]['template']

                    paragraph_template.append({ 'template': template, 'entitymap': entitymap })
                    paragraph_struct.append(sentence[start:end])
                    start = end
                    end = len(sentence)
                else:
                    end -= 1
                    if start == end:
                        start += 1
                        end = len(sentence)
        struct.append(paragraph_struct)
        templates.append(paragraph_template)
    return templates, struct