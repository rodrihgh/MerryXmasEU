"""
Tweet application.

Minimal script to post a tweet to the Twitter API using a given message.
"""
import os
from pathlib import Path
from datetime import datetime as dt, timedelta as td
from random import seed, shuffle, choice
import json
import urllib.request

import tweepy


CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')
ACCESS_KEY = os.environ.get('ACCESS_KEY')
ACCESS_SECRET = os.environ.get('ACCESS_SECRET')

ue_handles = {"EN": "EU_Commission", "ES": "ComisionEuropea", "DE": "EUinDE", "FR": "UEFrance"}
header = {"EN": f"Dear @{ue_handles['EN']},",
          "ES": f"Querida @{ue_handles['ES']},",
          "DE": f"Liebe @{ue_handles['DE']},",
          "FR": f"Chère @{ue_handles['FR']},"}

today_is = {"EN": "today is",
            "ES": "hoy es",
            "DE": "heute ist",
            "FR": "nous sommes aujourd'hui"}

weekdays = {"EN": ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"),
            "ES": ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"),
            "DE": ("Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"),
            "FR": ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche")}

ordinal_en = ["", "1st", "2nd", "3rd", "4th"]
ordinal_fr = ["", "1ère", "2ème", "3ème", "4ème"]
advent_week = {"EN": lambda d: f"of the {ordinal_en[d]} week of Advent.",
               "ES": lambda d: f"de la {d}ª semana de Adviento.",
               "DE": lambda d: f"der {d}. Adventswoche.",
               "FR": lambda d: f"de la {ordinal_fr[d]} semaine de l'Avent."}

remaining = {"EN": lambda d: f"Only {d} days left to wish you a #MerryChristmas",
             "ES": lambda d: f"Faltan {d} días para desearos una muy #FelizNavidad",
             "DE": lambda d: f"Es sind nur noch {d} Tage, um Ihnen #FroheWeihnachten zu wünschen.",
             "FR": lambda d: f"Plus que {d} jours pour vous souhaiter un #JoyeuxNoël"}


def early_months(date):
    return date.month < 3


now = dt.now()
today = now.date()
year = today.year
if early_months(today):
    year -= 1

christmas = dt(year=year, month=12, day=25).date()
xmas_weekday = christmas.weekday()

epiphany = dt(year=year+1, month=1, day=6).date()
baptism = epiphany  # TODO calculate next Sunday
candlemas = dt(year=year+1, month=2, day=2).date()

fourth_advent = christmas - td(days=(xmas_weekday+1))
third_advent = fourth_advent - td(days=7)
second_advent = third_advent - td(days=7)
first_advent = second_advent - td(days=7)

celebrations = {first_advent: {"ES": "feliz 1er domingo de Adviento!",
                               "EN": "happy 1st Sunday of Advent!",
                               "DE": "schönen 1. Advent!",
                               "FR": "bon 1er dimanche de l'Avent!"},
                second_advent: {"ES": "feliz 2º domingo de Adviento!",
                                "EN": "happy 2nd Sunday of Advent!",
                                "DE": "schönen 2. Advent!",
                                "FR": "bon 2ème dimanche de l'Avent!"},
                third_advent: {"ES": "feliz 3er domingo de Adviento!",
                               "EN": "happy 3rd Sunday of Advent!",
                               "DE": "schönen 3. Advent!",
                               "FR": "bon 3ème dimanche de l'Avent!"},
                fourth_advent: {"ES": "feliz 4º domingo de Adviento!",
                                "EN": "happy 4th Sunday of Advent!",
                                "DE": "schönen 4. Advent!",
                                "FR": "bon 4ème dimanche de l'Avent!"},
                dt(year=year, month=12, day=24).date(): {"ES": "Nochebuena.",
                                                         "EN": "Christmas Eve.",
                                                         "DE": "Heiligabend.",
                                                         "FR": "Réveillon de Noël."},
                christmas: {"ES": "Navidad"},
                epiphany: {"ES": "Epifanía, día de los Reyes Magos"},
                baptism: {"ES": "domingo, día del Bautizo del Señor"},
                candlemas: {"ES": "Fiesta de la Candelaria"}}   # TODO complete list
celeb_days = celebrations.keys()

special_pics = {christmas: "christmas"}  # TODO
special_pic_days = special_pics.keys()

scheduled_hours = (7, 11, 15, 19)
languages = ["EN", "ES", "DE", "FR"]
n_lang = len(languages)

assert len(scheduled_hours) == len(languages), "Scheduled hours and languages do not coincide in length"


def get_index():
    hour = now.hour
    try:
        return scheduled_hours.index(hour)
    except ValueError:
        print(f"Unexpected hour: {hour}. Scheduled hours are {scheduled_hours}")
        index = choice(range(n_lang))
        print(f"Index {index} was randomly chosen")
        return index


def get_language(lang_index):
    date_seed = today.year * 1e4 + today.month * 1e2 + today.day
    seed(date_seed)
    shuffle(languages)

    return languages[lang_index]


def setup_conn():
    """
    Return API connection object.
    """
    assert all((CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)), \
        "All credentials must be set"

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)

    return tweepy.API(auth)


def get_client():

    assert all((CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)), \
        "All credentials must be set"

    return tweepy.Client(consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET,
                         access_token=ACCESS_KEY, access_token_secret=ACCESS_SECRET)


def write_tweet(lang="ES"):
    if first_advent <= today < christmas:
        if today in celeb_days:
            day_text = celebrations[today][lang]
        else:
            weekday = weekdays[lang][today.weekday()]
            adv_week = (today - first_advent).days // 7 + 1
            day_text = " ".join([today_is[lang], weekday, advent_week[lang](adv_week)])
        rem_days = (christmas - today).days
        return " ".join([header[lang], day_text, remaining[lang](rem_days)])
    elif christmas <= today <= candlemas:
        pass  # TODO
    else:
        print("Christmas Season is over :(")


def get_pic(index, reverse=False):
    if today in special_pic_days:
        pic_pool = Path.cwd()/"pics"/special_pics[today]
    else:
        pic_pool = Path.cwd()/"pics"/"normal.json"
    with open(pic_pool, "r") as rf:
        pic_list = json.load(rf)

    pic_len = len(pic_list)

    seed(year)
    shuffle(pic_list)

    pic_index = ((today - first_advent).days * n_lang + index) % pic_len
    if reverse:
        pic_index = pic_len - 1 - pic_index
    return pic_list[pic_index]


def download_pic(url):
    ext = Path(url).suffix
    pic_fname = f"pic{ext}"
    r = urllib.request.urlopen(url)
    with open(pic_fname, 'wb') as f:
        f.write(r.read())
    return pic_fname


def main(lang=None, index=0, reply=False, write=True):
    """
    Command-line entrypoint to post a tweet message to Twitter.
    """

    print("The date is:")
    print(now)

    if lang is None:
        lang = get_language(index)
    print(f"Writing tweet in {lang}")

    msg = write_tweet(lang)
    pic_url = get_pic(index, reverse=reply)

    print("Trying to download the following image:")
    print(pic_url)
    pic_fname = download_pic(pic_url)

    print(f"Tweeting message:")
    print(msg)

    if write:
        api = setup_conn()
        # client = get_client()

        print("uploading pic...")
        media = api.simple_upload(pic_fname)
        print(media)

        tweet_kwargs = {"media_ids": [media.media_id]}
        if reply:
            ue_statuses = api.user_timeline(screen_name=ue_handles[lang], include_rts=False)
            reply_id = ue_statuses[0].id
            tweet_kwargs["in_reply_to_status_id"] = reply_id
            tweet_kwargs["auto_populate_reply_metadata"] = False
        tweet = api.update_status(msg, **tweet_kwargs)
        # tweet = client.create_tweet(text=msg)
        print(tweet)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Just a subversive Christmas bot.')

    parser.add_argument("language", type=str, default=None, nargs="?", choices=languages,
                        help="Language to write the tweet in.")
    parser.add_argument("--day", "-d", type=str, default=None, help="Input the day as DD-MM")
    parser.add_argument("--index", "-i", type=int, default=0, choices=range(n_lang),
                        help=f"Index to select pic (and language if not set)")
    parser.add_argument("--fake", "-f", action='store_true', help="Set to skip the actual tweet posting.")
    parser.add_argument("--reply", "-r", action='store_true', help="Set to reply to UE Commissions' latest tweet.")

    args = parser.parse_args()

    if args.day is not None:
        year = dt.now().year
        day = dt.strptime(args.day, "%d-%m")
        if early_months(day):
            year -= 1
        today = dt(year, day.month, day.day).date()

    main(lang=args.language, index=args.index, reply=args.reply, write=not args.fake)
