"""
Tweet application.

Minimal script to post a tweet to the Twitter API using a given message.
"""
import os
import sys
from datetime import datetime as dt, timedelta as td

import tweepy


CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')
ACCESS_KEY = os.environ.get('ACCESS_KEY')
ACCESS_SECRET = os.environ.get('ACCESS_SECRET')

header = {"ES": "Querida _CE_, hoy es"}

weekdays = {"ES": ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")}

advent_week = {"ES": lambda d: f"de la {d}ª semana de Adviento."}

remaining = {"ES": lambda d: f"Faltan {d} días para desearos una muy _FelizNavidad"}

today = dt.date(dt.now())
year = today.year
if today.month < 3:
    year -= 1

christmas = dt.date(dt(year=year, month=12, day=25))
xmas_weekday = christmas.weekday()

epiphany = dt.date(dt(year=year+1, month=1, day=6))
baptism = epiphany # TODO calculate next Sunday
candlemas = dt.date(dt(year=year+1, month=2, day=2))

fourth_advent = christmas - td(days=(xmas_weekday+1))
third_advent = fourth_advent - td(days=7)
second_advent = third_advent - td(days=7)
first_advent = second_advent - td(days=7)

celebrations = {first_advent: {"ES": "1er domingo de Adviento."},
                second_advent: {"ES": "2º domingo de Adviento."},
                third_advent: {"ES": "3er domingo de Adviento."},
                fourth_advent: {"ES": "4º domingo de Adviento."},
                dt.date(dt(year=year, month=12, day=24)): {"ES": "Nochebuena."},
                christmas: {"ES": "Navidad"},
                epiphany: {"ES": "Epifanía, día de los Reyes Magos"},
                baptism: {"ES": "domingo, día del Bautizo del Señor"},
                candlemas: {"ES": "Fiesta de la Candelaria"}}
celeb_days = celebrations.keys()


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
    
    return tweepy.Client(consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET, access_token=ACCESS_KEY, access_token_secret=ACCESS_SECRET)


def write_tweet(lang="ES"):
    if first_advent <= today < christmas:
        if today in celeb_days:
            day_text = celebrations[today][lang]
        else:
            weekday = weekdays[lang][today.weekday()]
            adv_week = (today - first_advent).days // 7 + 1
            day_text = " ".join([weekday, advent_week[lang](adv_week)])
        rem_days = (christmas - today).days
        return " ".join([header[lang], day_text, remaining[lang](rem_days)])
    elif christmas <= today <= candlemas:
        pass  # TODO
    else:
        print("Christmas Season is over :(")


def main(args):
    """
    Command-line entrypoint to post a tweet message to Twitter.
    """
    if not args:
        print("Provide a message on the CLI as the first argument.")
        print("It must be a single string. Multiple lines are allowed.")

        sys.exit(1)

    msg = write_tweet()

    # api = setup_conn()
    client = get_client()

    print(f"Tweeting message:")
    print(msg)

    # tweet = api.update_status(msg)
    tweet = client.create_tweet(text=msg)
    print(tweet)


if __name__ == "__main__":
    main(sys.argv[1:])
