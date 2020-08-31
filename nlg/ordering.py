__author__='thiagocastroferreira'

from random import randint

def prepare_input(messages):
    '''
    :param messages:
    :return: messages in the format of a string, sorted by alphabetical order
    '''
    messages = sorted(messages, key=lambda x: (x['intent'], len(list(x['attributes'].keys()))))

    inp, freq = [], {}
    for i, msg in enumerate(messages):
        delex_msg = msg['delex_msg']
        if delex_msg not in freq:
            freq[delex_msg] = 0
        freq[delex_msg] += 1
        # give an ID for each message from a meaning representation
        messages[i]['id'] = messages[i]['delex_msg'] + '_' + str(freq[delex_msg])

    return ';'.join([msg['id'] for msg in messages])


def train(trainset):
    trainorder = {}
    for unit in trainset:
        messages = unit['messages']
        src = prepare_input(messages)
        if src not in trainorder:
            trainorder[src] = {}

        order = ','.join([str(msg['order']) for msg in messages])
        if order not in trainorder[src]:
            trainorder[src][order] = 0
        trainorder[src][order] += 1

    for src in trainorder:
        trainorder[src] = [{ 'order': k, 'frequency': v } for k, v in trainorder[src].items()]
    return trainorder


def generate(messages, grammar, strategy='random'):
    src = prepare_input(messages)

    orders = grammar[src]
    if strategy == 'random':
        order = orders[randint(0, len(orders)-1)]['order']
    else:
        order = sorted(orders, key=lambda x: x['frequency'], reverse=True)[0]['order']

    result = []
    for idx in order.split(','):
        result.append(messages[int(idx)])
    return result