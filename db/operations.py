__author__ = 'thiagocastroferreira'

"""
Author: Thiago Castro Ferreira
Date: 06/11/2019
Description:
    CRUD operations on the database
"""

from db.model import *

def update_translation(news, translation):
    response = news.modify(set__translation=translation)
    return response


def save_corona(date, cases, deaths, recovered, country='Brazil'):
    query = CoronaVirus.objects(date=date, country=country)
    if query.count() == 0:
        corona = CoronaVirus(date=date, cases=cases, deaths=deaths, recovered=recovered, country=country)
        corona.save()
    else:
        corona = query[0]
        corona.modify(set__date=date, set__cases=cases, set__deaths=deaths, set__recovered=recovered)


def save_deter(date, location, state, city, uc, cause, city_area, uc_area, docid=None):
    deforestation = DeforestationDeterINPE(docid=docid,
                                           date=date,
                                           location=location,
                                           state=state,
                                           city=city,
                                           UC=uc,
                                           cause=cause,
                                           city_area=city_area,
                                           uc_area=uc_area)
    deforestation.save()


def get_state_uc(uc):
    return DeforestationDeterINPE.objects(UC=uc).distinct('state')[0]

def get_state_city(city):
    return DeforestationDeterINPE.objects(city=city).distinct('state')[0]

def save_corona_tweet(date, cases, deaths, recovered, tweet, country='Brazil'):
    query = CoronaTweet.objects(cases=cases, deaths=deaths, recovered=recovered)
    if query.count() == 0:
        corona = CoronaTweet(date=date, cases=cases, deaths=deaths, recovered=recovered, tweet=tweet, country=country)
        corona.save()
        return True
    return False

def save_deforestation_tweet(date, is_daily, tweet, state="", city="", uc=""):
    query = DeforestationTweet.objects(date=date,
                                is_daily=is_daily,
                                state=state,
                                city=city,
                                uc=uc)
    if query.count() == 0:
        tweet = DeforestationTweet(date=date,
                                   is_daily=is_daily,
                                   tweet=tweet,
                                   state=state,
                                   city=city,
                                   uc=uc)
        tweet.save()
        return True
    return False


def save_category(docid, description, ctype, group=None, subgroup=None, item=None, subitem=None, index=None):
    category = Category(docid=docid,
                        description=description,
                        ctype=ctype,
                        group=group,
                        subgroup=subgroup,
                        item=item,
                        subitem=subitem,
                        index=index)

    query = Category.objects(docid=docid, ctype=ctype)
    if query.count() == 0:
        category.save()
    return category


def save_location(docid, name, level, state=None, region=None, country=None):
    uf = Location(docid=docid, name=name, level=level, state=state, region=region, country=country)
    query = Location.objects(docid=docid, level=level)
    if query.count() == 0:
        uf.save()
    else:
        query[0].docid = docid
        query[0].name = name
        query[0].level = level
        query[0].state = state
        query[0].region = region
        query[0].country = country
        query[0].save()
    return uf