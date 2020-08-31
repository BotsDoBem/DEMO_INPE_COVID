__author__ = 'thiagocastroferreira'

"""
Author: Thiago Castro Ferreira
Date: 01/01/2018
Description:
    IBGE Database structure
"""

from mongoengine import *
connect('DATABASE', username='USERNAME', password='PASSWORD', authentication_source='ROLE')


class CoronaVirus(Document):
    date = DateTimeField(required=True)
    cases = IntField(required=True)
    deaths = IntField(required=True)
    recovered = IntField(required=True)
    country = StringField()

    meta = {
        'indexes': [
            'date'
        ]
    }

class CoronaTweet(Document):
    date = DateTimeField(required=True)
    cases = IntField(required=True)
    deaths = IntField(required=True)
    recovered = IntField(required=True)
    country = StringField()

    tweet = StringField(required=True)

    meta = {
        'indexes': [
            'date'
        ]
    }

class DeforestationDeterINPE(Document):
    docid = StringField(required=True)
    date = DateTimeField(required=True)
    location = StringField(required=True)
    state = StringField(required=True)
    city = StringField(required=True)
    UC = StringField() # unidade conservadora
    cause = StringField(required=True)

    # deforested area
    city_area = FloatField(required=True)
    uc_area = FloatField(required=True)

    meta = {
        'indexes': [
            'docid', 'date', 'location', 'state', 'city', 'UC', 'cause'
        ]
    }

class DeforestationTweet(Document):
    date = DateTimeField(required=True)
    is_daily = BooleanField(required=True)

    state = StringField()
    city = StringField()
    uc = StringField()

    tweet = StringField(required=True)

    meta = {
        'indexes': [
            'date'
        ]
    }