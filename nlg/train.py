__author__='thiagocastroferreira'

import sys
sys.path.append('../')
import json
import os
import re
import xml.etree.ElementTree as ET

import nlg.ordering as ordering
import nlg.structuring as structuring
import nlg.lexicalization as lexicalization
import nlg.reference as reference

from nlg import contractions

def parse(path):
    tree = ET.parse(path)

    trainset = []
    for entry in tree.getroot():
        print(entry.attrib['date'])
        # reading content in meaning
        meaning = entry.find('meaning')
        intents = []
        for unit in meaning:
            str_unit = unit.text
            intent, attributes = re.findall('(.+?)\((.+?)\)', str_unit)[-1]
            # TO DO: fix quotes on .xml
            # attributes = dict([w.split('=') for w in attributes.split(',')])
            attributes = dict(re.findall('(.+?)=\"(.+?)\",*', attributes))

            delex_attributes = '(' + ','.join([attr[0] + '=' + attr[0].upper() for attr in sorted(attributes.items(), key=lambda x: x[0].lower())]) + ')'
            delex_format = intent + delex_attributes
            # parse intent, attributes and string format
            intents.append({
                'intent': intent,
                'attributes': attributes,
                'str_msg': str_unit,
                'delex_msg': delex_format,
            })
        intents = sorted(intents, key=lambda x: x['str_msg'])

        # reading ordering info
        ordering_xml = entry.find('ordering')
        ordintents, visited = [], []
        for i, unit in enumerate(ordering_xml):
            str_unit = unit.text
            for j, intent in enumerate(intents):
                if intent['str_msg'] == str_unit and j not in visited:
                    # set an order attribute to set the position
                    intents[j]['order'] = i
                    visited.append(j)
                    break

        # structuring
        structuring = entry.find('structuring')
        visited = []
        for pidx, paragraph in enumerate(structuring):
            for sntidx, snt in enumerate(paragraph):
                for unit in snt:
                    str_unit = unit.text
                    for j, intent in enumerate(intents):
                        if intent['str_msg'] == str_unit and j not in visited:
                            intent['paragraph'] = pidx
                            intent['sentence'] = sntidx
                            visited.append(j)
                            break

        # lexicalization
        templates = []
        lexicalization = entry.find('lexicalization')
        for pidx, paragraph in enumerate(lexicalization):
            for sntidx, snt in enumerate(paragraph):
                templates.append({
                    'paragraph': pidx,
                    'sentence': sntidx,
                    'template': contractions.parse(' '.join(snt.text.replace('\n', '').split()))
                })

        # references
        references, entities = [], []
        references_xml = entry.find('references')
        for pidx, paragraph in enumerate(references_xml):
            for sntidx, sentence in enumerate(paragraph):
                for ref in sentence:
                    entity = ref.attrib['entity']

                    status = 'old'
                    if entity not in entities:
                        entities.append(entity)
                        status = 'new'
                    references.append({
                        'entity': ref.attrib['entity'],
                        'gender': ref.attrib['gender'],
                        'number': ref.attrib['number'],
                        'status': status,
                        'refex': ref.text
                    })

        trainset.append({ 'messages': intents, 'templates': templates, 'references': references })
    return trainset


def run(inp_path, out_path):
    # parse xml
    trainset = parse(inp_path)

    # train order
    trainorder = ordering.train(trainset)
    json.dump(trainorder, open(os.path.join(out_path, 'ordering.json'), 'w'), separators=(',', ':'), indent=4)

    # train ordering/structuring
    trainstruct = structuring.train(trainset)
    json.dump(trainstruct, open(os.path.join(out_path, 'structuring.json'), 'w'), separators=(',', ':'), indent=4)

    # train lexicalization
    trainlex = lexicalization.train(trainset)
    json.dump(trainlex, open(os.path.join(out_path, 'lexicalization.json'), 'w'), separators=(',', ':'), indent=4)

    # train references
    trainref = reference.train(trainset)
    json.dump(trainref, open(os.path.join(out_path, 'references.json'), 'w'), separators=(',', ':'), indent=4)


if __name__ == '__main__':
    inp_path = '../inpe_deter/data/month_corpus.xml'
    out_path = '../inpe_deter/data/month_grammar'

    if not os.path.exists(out_path):
        os.mkdir(out_path)

    run(inp_path=inp_path, out_path=out_path)