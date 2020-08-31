__author__='thiagocastroferreira'
import sys
sys.path.append('../')

import paths
import db.operations as dbop

import copy
import load_data
import schedule
import twitter
import time

from covid19.content import content
from datetime import datetime, timedelta
from nlg.generation import Generation

twitter_api = twitter.Api(consumer_key=paths.CONSUMER_KEY,
                          consumer_secret=paths.CONSUMER_SECRET,
                          access_token_key=paths.ACCESS_TOKEN,
                          access_token_secret=paths.ACCESS_SECRET)

gen = Generation(structuring_path=paths.COVID19_STRUCTURING_GRAMMAR,
                 lexicalization_path=paths.COVID19_LEXICALIZATION_GRAMMAR,
                 references_path=paths.COVID19_REFERENCES_GRAMMAR,
                 lexicon_path=paths.LEXICON_PATH)

def run():
    cases, deaths, recovered = load_data.last('Brazil')

    now = datetime.now() - timedelta(hours=3)
    date = datetime(now.year, now.month, now.day)
    messages = content(date)
    try:
        entry, template, paragraphs = gen.generate(messages, strategy='random')
        tweet = []
        for paragraph in paragraphs:
            tweet.append(' '.join(paragraph))
        tweet = '\n'.join(tweet)

        if dbop.save_corona_tweet(now, cases, deaths, recovered, tweet):
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
    except:
        print('ERROR')
        print('\n'.join([msg['str_msg'] for msg in messages]))
        print()

if __name__ == '__main__':
    run()
    schedule.every().day.at("12:00").do(run)
    schedule.every().day.at("13:00").do(run)
    schedule.every().day.at("14:00").do(run)
    schedule.every().day.at("15:00").do(run)
    schedule.every().day.at("16:00").do(run)
    schedule.every().day.at("17:00").do(run)
    schedule.every().day.at("18:00").do(run)
    schedule.every().day.at("19:00").do(run)
    schedule.every().day.at("20:00").do(run)
    schedule.every().day.at("20:30").do(run)
    schedule.every().day.at("21:00").do(run)
    schedule.every().day.at("21:30").do(run)
    schedule.every().day.at("22:00").do(run)
    schedule.every().day.at("22:30").do(run)
    schedule.every().day.at("23:00").do(run)
    schedule.every().day.at("23:30").do(run)
    schedule.every().day.at("00:00").do(run)
    schedule.every().day.at("01:00").do(run)
    schedule.every().day.at("02:00").do(run)
    schedule.every().day.at("02:58").do(run)

    while True:
        schedule.run_pending()
        time.sleep(30)