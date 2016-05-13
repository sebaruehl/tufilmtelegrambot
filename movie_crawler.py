# encoding: utf-8
# NOTICE
# This will probably not work in Google App Engine because it does not know the BeautifulSoup package
# Need to install BeautifulSoup locally into the project folder.
# More information: https://cloud.google.com/appengine/docs/python/tools/using-libraries-python-27

from bs4 import BeautifulSoup
import urllib
import re

BASIS_URL = "http://www.tu-film.de"


def get_all_title_links():
    url = BASIS_URL + "/programm"
    req = urllib.urlopen(url)
    page = req.read()
    scraping = BeautifulSoup(page, "lxml")
    ret_list = []
    for movie in scraping.find_all(attrs={"class": "title"}):
        ret_list.append(movie.find('a')['href'])
    return ret_list


def get_movie_details(url_list):
    ret_list = []
    for url_fragment in url_list:
        url = BASIS_URL + url_fragment
        req = urllib.urlopen(url)
        page = req.read()
        scraping = BeautifulSoup(page, "lxml")
        title = scraping.find_all('h1')[0].text
        title = title[title.find(':') + 1:]
        title = title.strip()
        datum = scraping.find_all(attrs={"class": "widget right info programm"})[0].text
        index_vorstellung = datum.find('Vorstellung')
        index_um = datum.find('um')
        datum = get_formatted_date(datum[index_vorstellung + 12:index_um - 2] + datum[index_um + 2:index_um + 8])
        imdblink = scraping.find_all(attrs={"class": "title"})[0].find('a')['href']
        req = urllib.urlopen(imdblink)
        page = req.read()
        scraping = BeautifulSoup(page, "lxml")
        imdbrating = scraping.find_all(attrs={"itemprop": "ratingValue"})[0].text
        ret_list.append([title, datum, url, imdblink, imdbrating])
    return ret_list


def get_formatted_date(date_string):
    day = date_string[4:6]
    if '.' in day:
        day = '0' + day[0]

    pattern_month = re.compile('(?:\.\s)([\w]*)', re.U)
    month = get_month_as_numberstring(pattern_month.search(date_string).group(1))

    pattern_year = re.compile('(20[0-9][0-9])')
    year = pattern_year.search(date_string).group(1)

    pattern_time = re.compile('([0-9]*[0-9]:[0-9][0-9])')
    time = pattern_time.search(date_string).group(1)

    res = year + '-' + month + '-' + day + 'T' + time

    return res


def get_month_as_numberstring(month_string):
    return {
        'Januar': '01',
        'Februar': '02',
        u'März': '03',
        'April': '04',
        'Mai': '05',
        'Juni': '06',
        'Juli': '07',
        'August': '08',
        'September': '09',
        'Oktober': '10',
        'November': '11',
        'Dezember': '12',
    }[month_string]

