__author__='thiagocastroferreira'
import sys
sys.path.append('../')

import copy
import paths
import db.operations as dbop
from db.model import DeforestationDeterINPE

import inpe_deter.daily_content as daily_content
import inpe_deter.load_data as inpe
import schedule
import twitter
import time

from datetime import datetime, timedelta
from inpe_deter.content import content
from nlg.generation import Generation

twitter_api = twitter.Api(consumer_key=paths.CONSUMER_KEY,
                          consumer_secret=paths.CONSUMER_SECRET,
                          access_token_key=paths.ACCESS_TOKEN,
                          access_token_secret=paths.ACCESS_SECRET)

def run():
    dados, estados, municipios, UCs, causas = inpe.setting_dados_deter()

    last_month_day, same_month = False, False
    # Always remove the data from the last 6 months and add it again to avoid duplication
    limit = datetime.now() - timedelta(days=180)
    limit = datetime(limit.year, limit.month, 1)
    DeforestationDeterINPE.objects(date__gte=limit).delete()

    now = datetime.now()
    prev_month = datetime(now.year-1, 12, 1) if now.month == 1 else datetime(now.year, now.month-1, 1)
    for row in dados['features']:
        docid = str(row['properties']['a'])
        state = row['properties']['h']
        city = row['properties']['i']
        uc = row['properties']['j']

        city_area = row['properties']['e']
        uc_area = row['properties']['f']
        cause = row['properties']['c']

        year, month, day = row['properties']['g']
        date = datetime(int(year), int(month), int(day))

        if date >= limit:
            next_day = date + timedelta(days=1)
            if now.month == int(month) and now.year == int(year):
                same_month = True
                last_month_day = False
            if prev_month.month == date.month and next_day.month != date.month and not same_month:
                last_month_day = True

            dbop.save_deter(docid=docid, date=date, cause=cause,
                            state=state, city=city, uc=uc, location='deter-amz',
                            city_area=city_area, uc_area=uc_area)
            print(row['properties'])

    if last_month_day:
        month_report(prev_month.month, prev_month.year)
    daily_report()


def tweeting(paragraphs):
    tweet = None
    for paragraph in paragraphs:
        start, end = 0, len(paragraph)
        while start < len(paragraph):
            publishing = ' '.join(paragraph[start:end])
            if len(publishing) > 280:
                end = end - 1
                if start == end:
                    start += 1
                    end = len(paragraph)
            else:
                tweet = twitter_api.PostUpdate(publishing) if not tweet else twitter_api.PostUpdate(publishing, in_reply_to_status_id=tweet.id)
                start = copy.copy(end)
                end = len(paragraph)

def daily_report():
    gen = Generation(structuring_path=paths.DETER_STRUCTURING_DAILYGRAMMAR,
                     lexicalization_path=paths.DETER_LEXICALIZATION_DAILYGRAMMAR,
                     references_path=paths.DETER_REFERENCES_DAILYGRAMMAR,
                     lexicon_path=paths.LEXICON_PATH)


    date = datetime.now() - timedelta(days=30)
    last_days = sorted(DeforestationDeterINPE.objects(date__gte=date).distinct('date'))

    cities, ucs = {}, {}
    for last_day in last_days:
        cases = DeforestationDeterINPE.objects(date=last_day)
        for case in cases:
            if case.cause in ['DESMATAMENTO_CR', 'DESMATAMENTO_VEG', 'MINERACAO']:
                if case.UC:
                    if (last_day, case.state, case.city, case.UC) not in ucs:
                        ucs[(last_day, case.state, case.city, case.UC)] = 0
                    ucs[(last_day, case.state, case.city, case.UC)] += case.uc_area
                else:
                    if (last_day, case.state, case.city, None) not in cities:
                        cities[(last_day, case.state, case.city, None)] = 0
                    cities[(last_day, case.state, case.city, None)] += case.city_area

    # SELECT THE CITIES AND UCS WITH THE HIGHEST DEFORESTED AREA IN THE LAST DAY IN THE DATABASE
    cities = sorted(cities.items(), key=lambda x:x[1], reverse=True)
    ucs = sorted(ucs.items(), key=lambda x:x[1], reverse=True)

    # COMPILE CITY ALERTS TO BE VERBALIZED
    alerts = []
    for city in cities:
        alerts.append(city[0])
    posts = 0
    for alert in alerts:
        # 3 city verbalizations per day
        if posts == 1:
            break
        date, state, city, uc = alert
        messages, _ = daily_content.content(date, state, city, uc)

        try:
            entry, template, paragraphs = gen.generate(messages, strategy='random')
            tweet = []
            for paragraph in paragraphs:
                tweet.append(' '.join(paragraph))
            tweet = '\n'.join(tweet)

            if dbop.save_deforestation_tweet(date=date, is_daily=True, tweet=tweet, state=state, city=city, uc=uc):
                tweeting(paragraphs)
                posts += 1
        except:
            print('ERROR')
            print('\n'.join([msg['str_msg'] for msg in messages]))
            print()

    # COMPILE UC ALERTS TO BE VERBALIZED
    alerts = []
    for uc in ucs:
        alerts.append(uc[0])
    posts = 0
    for alert in alerts:
        # 3 uc verbalizations per day
        if posts == 1:
            break
        date, state, city, uc = alert
        messages, _ = daily_content.content(date, state, city, uc)

        try:
            entry, template, paragraphs = gen.generate(messages, strategy='random')
            tweet = []
            for paragraph in paragraphs:
                tweet.append(' '.join(paragraph))
            tweet = '\n'.join(tweet)

            if dbop.save_deforestation_tweet(date=date, is_daily=True, tweet=tweet, state=state, city=city, uc=uc):
                tweeting(paragraphs)
                posts += 1
        except:
            print('ERROR')
            print('\n'.join([msg['str_msg'] for msg in messages]))
            print()


def month_report(month, year):
    gen = Generation(structuring_path=paths.DETER_STRUCTURING_GRAMMAR,
                     lexicalization_path=paths.DETER_LEXICALIZATION_GRAMMAR,
                     references_path=paths.DETER_REFERENCES_GRAMMAR,
                     lexicon_path=paths.LEXICON_PATH)

    messages, date = content(month=month, year=year)

    date = datetime(year, month, 1)
    try:
        entry, template, paragraphs = gen.generate(messages, strategy='random')
        tweet = []
        for paragraph in paragraphs:
            tweet.append(' '.join(paragraph))
        tweet = '\n'.join(tweet)

        if dbop.save_deforestation_tweet(date, False, tweet):
            tweeting(paragraphs)
    except:
        print('ERROR')
        print('\n'.join([msg['str_msg'] for msg in messages]))
        print()

if __name__ == '__main__':
    # run()
    schedule.every().day.at("11:30").do(run)
    schedule.every().day.at("15:30").do(run)
    schedule.every().day.at("21:30").do(run)

    while True:
        schedule.run_pending()
        time.sleep(600)