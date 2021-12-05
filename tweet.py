"""
Tweet application.

Minimal script to post a tweet to the Twitter API using a given message.
"""
import os
from pathlib import Path
from datetime import datetime as dt, timedelta as td
from random import seed, shuffle
import json
import urllib.request
import re

import tweepy


CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')
ACCESS_KEY = os.environ.get('ACCESS_KEY')
ACCESS_SECRET = os.environ.get('ACCESS_SECRET')

languages = ["EN", "ES", "DE", "FR"]
n_lang = len(languages)

ue_handles = {"EN": "EU_Commission", "ES": "ComisionEuropea", "DE": "EUinDE", "FR": "UEFrance"}
header = {"EN": f"Dear @{ue_handles['EN']},",
          "ES": f"Querida @{ue_handles['ES']},",
          "DE": f"Liebe @{ue_handles['DE']},",
          "FR": f"Chère @{ue_handles['FR']},"}

today_is = {"EN": "today is",
            "ES": "hoy es",
            "DE": "heute ist",
            "FR": "aujourd'hui c'est"}

weekdays = ({'EN': 'Monday', 'ES': 'lunes', 'DE': 'Montag', 'FR': 'lundi'},
            {'EN': 'Tuesday', 'ES': 'martes', 'DE': 'Dienstag', 'FR': 'mardi'},
            {'EN': 'Wednesday', 'ES': 'miércoles', 'DE': 'Mittwoch', 'FR': 'mercredi'},
            {'EN': 'Thursday', 'ES': 'jueves', 'DE': 'Donnerstag', 'FR': 'jeudi'},
            {'EN': 'Friday', 'ES': 'viernes', 'DE': 'Freitag', 'FR': 'vendredi'},
            {'EN': 'Saturday', 'ES': 'sábado', 'DE': 'Samstag', 'FR': 'samedi'},
            {'EN': 'Sunday', 'ES': 'domingo', 'DE': 'Sonntag', 'FR': 'dimanche'})


def ordinal(num, lang, feminine=False):
    if type(num) is not int or num < 1:
        raise ValueError(f"Invalid ordinal number {num}")
    if lang == "EN":
        if num == 1:
            return "1st"
        elif num == 2:
            return "2nd"
        elif num == 3:
            return "3rd"
        else:
            return f"{num}th"
    elif lang == "ES":
        return f"{num}ª" if feminine else f"{num}º"
    elif lang == "FR":
        if num == 1:
            return f"{num}ère" if feminine else f"{num}er"
        else:
            return f"{num}ème"
    elif lang == "DE":
        return f"{num}."


advent_week = {"EN": lambda d: f"of the {ordinal(d, 'EN')} week of Advent.",
               "ES": lambda d: f"de la {ordinal(d, 'ES', feminine=True)} semana de Adviento.",
               "DE": lambda d: f"der {ordinal(d, 'DE')}. Adventswoche.",
               "FR": lambda d: f"de la {ordinal(d, 'FR', feminine=True)} semaine de l'Avent."}

remaining = {"EN": lambda d: f"Only {d} days left to wish you a #MerryChristmas",
             "ES": lambda d: f"Faltan {d} días para desearos una muy #FelizNavidad",
             "DE": lambda d: f"Es sind nur noch {d} Tage, um Ihnen #FroheWeihnachten zu wünschen.",
             "FR": lambda d: f"Plus que {d} jours pour vous souhaiter un #JoyeuxNoël"}

xmas_days = {"EN": lambda d: f"the {ordinal(d, 'EN')} Christmas day.",
             "ES": lambda d: f"{ordinal(d, 'ES')} día de Navidad.",
             "DE": lambda d: f"{ordinal(d, 'DE')} Weihnachtstag.",
             "FR": lambda d: f"le {ordinal(d, 'FR')} jour de Noël."}

merry_xmas = {"EN": "#MerryChristmas to the European nation!",
              "ES": "#FelizNavidad a la nación europea!",
              "DE": "#FroheWeihnachten der europäischen Nation!",
              "FR": "#JoyeuxNoël à la nation européenne !"}

light = {"EN": "May the birth of Our Lord Jesus Christ enlighten our peoples in peace and justice.",
         "ES": "Que el nacimiento de Nuestro Salvador Jesucristo ilumine a nuestros pueblos en paz y justicia.",
         "DE": "Möge die Geburt unseres Herrn Jesu Christi unsere Völker in Frieden und Gerechtigkeit erleuchten.",
         "FR": "Que la naissance de notre Sauveur Jésus-Christ éclaire nos peuples dans la paix et la justice."}

phrases = (ue_handles, header, today_is, advent_week, remaining, xmas_days, merry_xmas, light) + weekdays

assert all(set(languages) == set(ph.keys()) for ph in phrases), "Some language missing among phrases"


def early_months(month):
    return month < 3


now = dt.now()
today = now.date()
year = today.year
if early_months(today.month):
    year -= 1


def date(day, month):
    date_year = year
    if early_months(month):
        date_year += 1
    return dt(year=date_year, month=month, day=day).date()


christmas = date(25, 12)
xmas_weekday = christmas.weekday()

nikolaus = date(6, 12)
xmas_eve = date(24, 12)
st_stephen = date(26, 12)
innocent = date(28, 12)
new_years_eve = date(31, 12)
new_year = date(1, 1)

if xmas_weekday == 6:
    holy_family = date(30, 12)
else:
    holy_family = christmas + td(days=6-xmas_weekday)

epiphany_eve = date(5, 1)
epiphany = date(6, 1)

epiphany_weekday = epiphany.weekday()

baptism = epiphany + td(days=(5 - epiphany_weekday) % 7 + 1)  # Next Sunday

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
                xmas_eve: {"ES": "pasad una feliz Nochebuena.",
                           "EN": "I wish you a wonderful Christmas Eve.",
                           "DE": "meine beste Wünsche zu diesem Heiligabend.",
                           "FR": "je vous souhaite un bon Réveillon de Noël."},
                christmas: {"ES": "Navidad, al fin.",
                            "EN": "finally Christmas.",
                            "DE": "endlich Weihnachten.",
                            "FR": "la Fete de Noël, enfin."},
                st_stephen: {"ES": "26 de diciembre, día de San Esteban Protomártir.",
                             "EN": "December the 26th, Boxing Day. "
                                   "We also celebrate the Feast of St. Stephen Protomartyr.",
                             "DE": "der 2. Weihnachtstag. "
                                   "Die katholische Kirche feiert ebenso den Stefanstag, "
                                   "den Gedenktag des Erzmärtyrers.",
                             "FR": "le jour des boîtes et la Fête de la Saint-Étienne, "
                                   "protomartyr de l'Église."},
                innocent: {"ES": "28 de diciembre, día de los Santos Inocentes.",
                           "EN": "December the 28th, Feast of the Holy Innocents.",
                           "DE": "28. Dezember, das Fest der Unschuldigen Kinder.",
                           "FR": "le 28 décembre, le Jour des Saints Innocents."
                           },
                new_year: {"ES": "la Solemnidad de Santa María, Madre de Dios para la Iglesia Católica. "
                                 "La Iglesia Ortodoxa oriental y diversas confesiones protestantes celebran "
                                 "la Circuncisión de Cristo. Lo de Año Nuevo no me suena...",
                           "EN": "the Solemnity of Mary, Mother of God in the Catholic Church and "
                                 "the Feast of the Circumcision of Christ for the Orthodox, "
                                 "Lutheran and Anglican Churches, among others. New Year? Never heard of it.",
                           "DE": "das Hochfest der Gottesmutter laut der kath. Kirche."
                                 "Die orthodoxe, anglikanische und evangelische Kirchen feiern hingegen "
                                 "die Beschneidung des Herrn. Neujahr? Noch nie davon gehört.",
                           "FR": "la fête de Marie mère de Dieu pour l'Église catholique et "
                                 "la fête de la Circoncision de Jésus pour les Églises orthodoxe, anglicane "
                                 "et luthérienne. Nouvel an? Je n'en ai jamais entendu parler "
                           }

                # epiphany: {"ES": "Epifanía, día de los Reyes Magos"},
                # baptism: {"ES": "domingo, día del Bautizo del Señor"}} # TODO complete list
                }

if nikolaus.weekday() != 6:
    celebrations[nikolaus] = {"ES": "feliz día de San Nicolás!",
                              "EN": "happy Saint Nicholas Day!",
                              "DE": "schönen Nikolaustag!",
                              "FR": "bonne Fête de Saint-Nicolas!"}
if holy_family not in celebrations.keys():
    celebrations[holy_family] = {"EN": f"the Feast of the Holy Family and",
                                 "ES": "el Día de la Sagrada Familia y",
                                 "DE": "das Fest der Heiligen Familie und",
                                 "FR": "le Jour de la Sainte Famille et"}
else:
    holy_family = None

assert all(set(languages) == set(cel.keys())
           for d, cel in celebrations.items()), "Some language missing among celebration days"

celeb_days = celebrations.keys()

special_pics = dict(
    nikolaus="nikolaus.json",
    xmas_eve="shepherds.json",
    christmas="shepherds.json",
    st_stephen="st_stephen.json",
    epiphany_eve="magi.json",
    epiphany="magi.json"
)  # {baptism: "baptism.json"}  # TODO

special_pics[holy_family] = "holy_family.json"
special_pics[innocent] = "innocents.json"

special_pic_days = special_pics.keys()


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


def fill_num(lang_dict, number):
    return {k: v(number) for k, v in lang_dict.items()}


def capitalize(lang_dict):
    return {k: v.capitalize() for k, v in lang_dict.items()}


def append(lang_dict, suffix):
    return {k: v + suffix for k, v in lang_dict.items()}


def join_message(parts, lang):
    return " ".join(part[lang] for part in parts)


def write_tweet(lang="ES"):
    weekday = weekdays[today.weekday()]
    if first_advent <= today < christmas:
        if today in celeb_days:
            day_text = [celebrations[today]]
        else:
            adv_week = (today - first_advent).days // 7 + 1
            day_text = [today_is, weekday, fill_num(advent_week, adv_week)]
        rem_days = (christmas - today).days
        return join_message([header] + day_text + [fill_num(remaining, rem_days)], lang)
    elif today == christmas:
        return join_message([header, merry_xmas, light, today_is, celebrations[today]], lang)
    elif today == new_year:
        return join_message([header, merry_xmas, today_is, celebrations[today]], lang)
    elif christmas <= today <= baptism:
        xmas_d = (today - christmas).days + 1
        if today in celeb_days:
            if today == holy_family:
                day_text = [append(weekday, ","), celebrations[today], fill_num(xmas_days, xmas_d)]
            else:
                day_text = [celebrations[today]]
        else:
            day_text = [append(weekday, ","), fill_num(xmas_days, xmas_d)]
        return join_message([header, merry_xmas, light, capitalize(today_is)] + day_text, lang)
    else:
        print("Christmas Season is over :(")


def get_pic(index, reverse=False):
    if today in special_pic_days:
        pic_pool = Path.cwd()/"pics"/special_pics[today]
    else:
        pic_pool = Path.cwd()/"pics"/"normal.json"
    with open(str(pic_pool), "r") as rf:
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


def original_pic_url(pic_url):
    regex = r"(\/[\da-d]{2}\/)(.*)(\/)"
    match = re.search(regex, pic_url)
    if match:
        return f"https://commons.wikimedia.org/wiki/File:{match.group(2)}"
    else:
        return pic_url


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

    if msg is None:
        return

    pic_url = get_pic(index, reverse=reply)

    print(f"Tweeting message with {len(msg)} characters:")
    print(msg)

    print("\nTrying to download the following image:")
    print(pic_url)

    if write:
        pic_fname = download_pic(pic_url)

        api = setup_conn()
        # client = get_client()

        print("uploading pic...")
        media = api.simple_upload(pic_fname)
        media_id = media.media_id
        api.create_media_metadata(media_id, alt_text=f"Image source: {original_pic_url(pic_url)}")
        print(media)

        tweet_kwargs = {"media_ids": [media_id]}
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
        day_month = dt.strptime(args.day, "%d-%m")
        today = date(day_month.day, day_month.month)

    main(lang=args.language, index=args.index, reply=args.reply, write=not args.fake)
