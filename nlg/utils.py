__author__='thiagocastroferreira'

import re

def intent_to_str(message):
    return message['intent'] + '(' + ','.join([attr + '=' + value for attr, value in message['attributes']]) + ')'

def intent_to_dict(message):
    intent, attributes = re.findall('(.+?)\((.+?)\)', message)[-1]
    attributes = dict([w.split('=') for w in attributes.split(',')])
    return { 'intent': intent, 'attributes': attributes }