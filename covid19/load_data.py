__author__='thiagocastroferreira'

import sys
sys.path.append('../')
from db.operations import save_corona
from db.model import CoronaVirus
from datetime import datetime, timedelta
from lxml import html
import requests

def history():
    URL = 'https://corona.lmao.ninja/v2/historical'

    r = requests.get(URL, timeout=10)
    r.encoding = "utf-8"

    data, cases, deaths, recovered = [], [], [], []
    if r.status_code == 200:
        items = r.json()
        for item in items:
            if item['country'].lower() == 'brazil':
                cases = item['timeline']['cases']
                deaths = item['timeline']['deaths']
                recovered = item['timeline']['recovered']

        for date_ in cases:
            month, day, year = date_.split('/')
            year = int(year) + 2000
            date = datetime(year, int(month), int(day))

            data.append({
                'date': date,
                'cases': cases[date_],
                'deaths': deaths[date_],
                'recovered': recovered[date_]
            })

            save_corona(date=date, cases=cases[date_], deaths=deaths[date_], recovered=recovered[date_])
    return data


def previous_day():
    date = datetime.now() - timedelta(days=1)
    date = datetime(date.year, date.month, date.day)
    items = CoronaVirus.objects(date=date)
    item = items[0]
    return item.cases, item.deaths, item.recovered


def last(country):
    url = 'https://www.worldometers.info/coronavirus/country/' + str(country)

    cases, deaths, recovered = 0.0, 0.0, 0.0
    r = requests.get(url)

    if r.status_code == 200:
        tree = html.fromstring(r.text)
        container = tree.xpath("//div[@id='maincounter-wrap']")

        for item in container:
            h1 = item.xpath('h1')[0].text
            number = int(item.xpath('div/span')[0].text.replace(',', ''))
            if 'Cases' in h1:
                cases = number
            elif 'Deaths' in h1:
                deaths = number
            else:
                recovered = number

        date = datetime.now() - timedelta(hours=3)
        date = datetime(date.year, date.month, date.day)
        save_corona(date=date, cases=cases, deaths=deaths, recovered=recovered)
    return cases, deaths, recovered


if __name__ == '__main__':
    # history()
    last('Brazil')