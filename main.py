# encoding: utf-8

import json
import logging
from urllib2 import urlopen
from urllib import urlencode
from datetime import datetime 

from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

TOKEN = open('bot.token').read()
BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'
BOT_NAME = 'tufilmbot'


# ================================
# Data store classes

class Subscriber(ndb.Model):
    chat_id = ndb.IntegerProperty()


class Movie(ndb.Model):
    title = ndb.StringProperty()
    date = ndb.DateTimeProperty()
    url = ndb.StringProperty()
    imdbLink = ndb.StringProperty()
    imdbRating = ndb.StringProperty()

class Going(ndb.Model):
    chat_id = ndb.IntegerProperty()
    date_created = ndb.DateTimeProperty()

class GoingAnswers(ndb.Model):
    user_id = ndb.IntegerProperty()
    answer = ndb.StringProperty()


# ================================
# Helper functions

def get_going_answers(c_id):
    today = datetime.now()
    check = Going.query(ndb.AND(Going.date_created >= today, Going.chat_id == c_id)).fetch()

    if check:
        return GoingAnswers.query(ancestor=check.key).fetch()
    else:
        return 0

def add_going_answer(c_id, user_id, answer):
    today = datetime.now()
    check = Going.query(ndb.AND(Going.date_created >= today, Going.chat_id == c_id)).fetch()

    if check:
        GoingAnswers(parent=check.key, user_id=user_id, answer=answer)
    else:
        going = Going(chat_id = c_id, date_created = today)
        GoingAnswers(parent=going.key, user_id=user_id, answer=answer)

def add_subscriber(c_id):
    check = Subscriber.query(Subscriber.chat_id == c_id).fetch()
    if check:
        return 0
    else:
        subscriber = Subscriber(chat_id=c_id)
        subscriber.put()
        return 1


def remove_subscriber(c_id):
    check = Subscriber.query(Subscriber.chat_id == c_id).fetch()
    if check:
        check[0].key.delete()
        return 1
    return 0


def add_movie(title, date, url, imdblink, imdbrating):
    Movie(title=title,
          date=datetime.strptime(date, '%Y-%m-%dT%H:%M'),
          url=url,
          imdbLink=imdblink,
          imdbRating=imdbrating).put()


def get_formatted_movie_list():
    today = datetime.now()
    all_movies = Movie.query(Movie.date >= today).fetch()
    all_movies.sort(key=lambda movie_element: movie_element.date)
    movie_list = ''
    for movie in all_movies:
        movie_list += (movie.date.strftime('%d.%m.%Y') + ': ' + movie.title + '\n')
    return movie_list


def get_next_movie():
    today = datetime.now()
    query_movies_sorted = Movie.query(Movie.date >= today).fetch()
    query_movies_sorted.sort(key=lambda movie: movie.date)
    return query_movies_sorted[0]


def get_formatted_short_reminder(next_movie):
    return 'Nicht vergessen, heute im TU Film: ' \
           + next_movie.title + '\nBeginn um ' \
           + next_movie.date.strftime('%H:%M Uhr')


def get_formatted_movie(head, title, date=None, url=None, imdblink=None, imdbrating=None):
    text = '<b>' + head + '</b>\n' + title
    if date:
        text += '\n' + date.strftime('%d.%m.%Y um %H:%M Uhr')
        if url:
            text += '\nInfos: <a href="' + url + '">Link</a>'
            if imdblink:
                text += '\nIMDb: <a href="' + imdblink + '">Link</a>'
                if imdbrating:
                    text += u'\nIMDb ★: ' + imdbrating
    return text


# Send a message from the Bot
# HTML encoded
def reply(chat_id, msg=None):
    if msg:
        resp = urlopen(BASE_URL + 'sendMessage', urlencode({
            'chat_id': str(chat_id),
            'text': msg.encode('utf-8'),
            'parse_mode': 'HTML',
            'disable_web_page_preview': 'true',
        })).read()
    else:
        logging.error('no message specified')
        resp = None

    logging.info('send response:')
    logging.info(resp)


# ================================
# Google App Request Handlers

# set the web hook for the Telegram API
class SetWebHookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urlopen(BASE_URL + 'setWebhook', urlencode({'url': url})))))


# triggered over cron job
class ReminderHandler(webapp2.RequestHandler):
    def get(self):
        next_movie = get_next_movie()
        if datetime.date(datetime.now()) == next_movie.date.date():
            all_subscriber = Subscriber.query(projection=["chat_id"], distinct=True)
            # send reminder message to every subscriber
            # care if to many subscribers -> limitations from telegram api
            msg = get_formatted_short_reminder(next_movie)
            for sub in all_subscriber:
                reply(sub.chat_id, msg)


# Handler for adding a new Movie over a URL
class MovieHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        title = self.request.get('title')
        date = self.request.get('date')
        url = self.request.get('url')
        imdblink = self.request.get('imdblink')
        imdbrating = self.request.get('imdbrating')
        add_movie(title, date, url, imdblink, imdbrating)


# Starts the crawler
# Does nothing currently because the crawler script ist not yet imported
class GetMoviesHandler(webapp2.RedirectHandler):
    # links = get_all_title_links()
    # movie_list = get_movie_details(links)
    movie_list = []
    for movie in movie_list:
        add_movie(movie[0], movie[1], movie[2], movie[3], movie[4])


# Handles messages from Telegram
class WebHookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        json_body = json.loads(self.request.body)

        # log request
        logging.info('request body:')
        logging.info(json_body)
        self.response.write(json.dumps(json_body))

        # get chat and message information
        message = json_body['message']
        text = message.get('text')
        chat = message['chat']
        chat_id = chat['id']

        if not text:
            logging.info('no text')
            return

        if text.startswith('/'):
            if text.find('@') > 0:
                if text.find(BOT_NAME) > 0:
                    text = text[0:text.find('@')]
                else:
                    return
            if text == '/subscribe':
                if add_subscriber(chat_id) == 1:
                    reply(chat_id, 'Subscribed to movie reminder!')
                else:
                    reply(chat_id, 'Already subscribed!')
            elif text == '/unsubscribe':
                if remove_subscriber(chat_id) == 1:
                    reply(chat_id, 'Unsubscribed from movie reminder!')
                else:
                    reply(chat_id, 'Not subscribed!')
            elif text == '/listall':
                reply(chat_id, get_formatted_movie_list())
            elif text == '/next':
                next_movie = get_next_movie()
                reply(chat_id, get_formatted_movie(u'Als nächstes im TU Film',
                                                   next_movie.title,
                                                   next_movie.date,
                                                   next_movie.url,
                                                   next_movie.imdbLink,
                                                   next_movie.imdbRating))
            elif text == '/whoisgoing':
                answers = get_going_answers(chat_id)
                if answers:
                    # display answers
                else:
                    # ask user to create new poll
            elif text == '/updategoingstatus':
                answers = get_going_answers(chat_id)
                if answers:
                    # display user going options
                else:
                    # ask user to create new poll
            else:
                reply(chat_id, "Command not known, use / to get an overview over possible commands.")

        else:
            # reply(chat_id, "Use /<command>. See possible commands with /? or /commands.")
            return


# The App
app = webapp2.WSGIApplication([
    ('/set_webhook', SetWebHookHandler),
    ('/webhook', WebHookHandler),
    ('/reminder', ReminderHandler),
    ('/add_movie', MovieHandler),
    ('/get_movies', GetMoviesHandler),
], debug=True)
