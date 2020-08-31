__author__='thiagocastroferreira'

from itertools import combinations
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
    return messages

# def prepare_input(messages):
#     return ';'.join([msg['delex_msg'] for msg in messages])


def train(trainset):
    trainstruct = {}
    for unit in trainset:
        messages = prepare_input(unit['messages'])

        # set index
        for idx, msg in enumerate(messages):
            messages[idx]['idx'] = idx

        struct = []
        for pidx in sorted(set([w['paragraph'] for w in messages])):
            paragraph = []
            fparagraph = [w for w in messages if w['paragraph'] == pidx]
            for sidx in sorted(set([w['sentence'] for w in fparagraph])):
                sentence = sorted([w for w in fparagraph if w['sentence'] == sidx], key=lambda x: x['order'])
                paragraph.append([w['idx'] for w in sentence])
            struct.append(paragraph)

        for i, paragraph in enumerate(struct):
            for j, snt in enumerate(paragraph):
                paragraph[j] = tuple(snt)
            struct[i] = tuple(paragraph)
        struct = tuple(struct)

        src = ';'.join([msg['id'] for msg in messages])
        if src not in trainstruct:
            trainstruct[src] = {}
        if struct not in trainstruct[src]:
            trainstruct[src][struct] = 0
        trainstruct[src][struct] += 1

    for src in trainstruct:
        trainstruct[src] = [{ 'struct': k, 'frequency': v } for k, v in trainstruct[src].items()]
    return trainstruct


def generate_old(messages, grammar, strategy='random'):
    messages = prepare_input(messages)
    src = ';'.join([msg['id'] for msg in messages])

    structs = grammar[src]
    if strategy == 'random':
        struct = structs[randint(0, len(structs)-1)]['struct']
    else:
        struct = sorted(structs, key=lambda x: x['frequency'], reverse=True)[0]['struct']

    i, paragraphs = 0, []
    for p in struct:
        paragraph = []
        for snt in p:
            sentence = []
            for idx in snt:
                message = messages[idx]
                message['order'] = i
                sentence.append(message)
                i += 1
            paragraph.append(sentence)
        paragraphs.append(paragraph)
    return paragraphs


def generate(messages, grammar, strategy='random'):
    # while not struct and len(messages_) != 0:
    #     messages_ = prepare_input(messages_)
    #     src = ';'.join([msg['id'] for msg in messages_])
    #     if src in grammar:
    #         structs = grammar[src]
    #         if strategy == 'random':
    #             struct = structs[randint(0, len(structs)-1)]['struct']
    #         else:
    #             struct = sorted(structs, key=lambda x: x['frequency'], reverse=True)[0]['struct']
    #     else:
    #         messages_ = messages_[:-1]

    struct, messages_ = None, messages[:]
    size = len(messages)
    while size > 0:
        for candidate in combinations(messages, size):
            messages_ = prepare_input(candidate)
            src = ';'.join([msg['id'] for msg in messages_])
            if src in grammar:
                structs = grammar[src]
                if strategy == 'random':
                    struct = structs[randint(0, len(structs)-1)]['struct']
                else:
                    struct = sorted(structs, key=lambda x: x['frequency'], reverse=True)[0]['struct']
                break
        if struct:
            break

        size -= 1

    i, paragraphs = 0, []
    for p in struct:
        paragraph = []
        for snt in p:
            sentence = []
            for idx in snt:
                message = messages_[idx]
                message['order'] = i
                sentence.append(message)
                i += 1
            paragraph.append(sentence)
        paragraphs.append(paragraph)
    return paragraphs