# -*- coding: UTF-8 -*-

import telebot
import feedparser
import re
import logging

# CONSTANTS
TOKEN = ""
CHATS_DB = "Chats.dat"

URL = "https://www.loteriasyapuestas.es/es/"

PRIMITIVA = ("La Primitiva", "la-primitiva")
EUROMILLONES = ("Euromillones", "euromillones")
BONOLOTO = ("Bonoloto", "bonoloto")
QUINIELA = ("La Quiniela", "la-quiniela")
QUINIGOL = ("El Quinigol", "el-quinigol")
LOTOTURF = ("Lototurf", "lototurf")

LOTERIAS = [PRIMITIVA, EUROMILLONES, BONOLOTO, QUINIELA, QUINIGOL, LOTOTURF]

def load_chats():
    """ Load chats' identifiers from a file. """
    try:
        with(open(CHATS_DB, 'r')) as f:
            chats = set(map(int, f.read().splitlines()))
    except Exception as error:
        logging.error("Error loading chats.\n%s" % error)
        chats = set()
    return chats

def save_chats(chats):
    """ Save chats' identifiers in a file. """
    try:
        with(open(CHATS_DB, 'w+')) as f:
            for c in chats:
                f.write("%s\n" % c)
    except Exception as error:
        logging.error("Error saving chats.\n%s" % error)

def get_bote(sorteo):
    """ Get the latest bote given a rss. """
    try:
        f = feedparser.parse(URL + sorteo + "/botes/.formatoRSS")
        e = f.entries[0]
        bote = int(re.match(r'.+\ (.+)€', e.title).group(1).replace('.', ''))
        proximo_sorteo = re.match(r'.+próximo (.+) pone.+', e.summary).group(1)
        return (bote, proximo_sorteo)
    except Exception as error:
        logging.error("Error requesting botes to RSS.\n%s" % error)
        return None

def get_botes():
    """ Obtain the botes for all loterias. """
    botes = {}
    for l in LOTERIAS:
        botes[l[0]]=get_bote(l[1])
    return botes

# def get_results():
#     f = feedparser.parse(URL + PRIMITIVA[1] + "/resultados/.formatoRSS")
#     premios = f.entries[0]
#     res = f.entries[1]
#     print(premios.published_parsed) # time.struct_time(tm_year=2018, tm_mon=12, tm_mday=29, tm_hour=21, tm_min=7, tm_sec=50, tm_wday=5, tm_yday=363, tm_isdst=0)
#     print("----------------------------")
#     print(premios.summary)
#     m = re.search(r'<b>(.+)</b>', premios.summary)
#     print("group: " + str(m.group(1)))

    #     e = f.entries[0]
    #     m = re.match(r'.+\ (.+€)', e.title)
    #     return m.group(1)
    # except Exception as error:
    #     print(error)
    #     return -1

def format_botes(botes):
    message = "Botes y sortes [LAE](https://www.loteriasyapuestas.es/es)\n"
    for b in botes:
        message += u"\u2022 " + "*" + b[0] + "*: " + format(b[1][0], ',d').replace(',', '.') + "€\n" + str(b[1][1]) + "\n"

    return message

if __name__ == '__main__':
    logging.basicConfig(filename='patonegro.log', filemode='a+', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s: %(message)s',)
    logging.info("El Pato Negro is starting...")

    bot = telebot.TeleBot(TOKEN)

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        logging.info(message)
        bot.send_message(message.chat.id, "Hola! Soy *El Pato Negro*.\nPídeme información sobre los sorteos de LAE con el comando\n/botes", parse_mode="Markdown")

    @bot.message_handler(commands=['botes'])
    def send_botes(message):
        logging.info(message)
        botes = get_botes()
        botes = sorted(botes.items(), key=lambda kv: kv[1][0], reverse=True) # Ordena por botes de mayor a menor.
        bot.send_message(chat_id = message.chat.id,
                         text = format_botes(botes),
                         parse_mode="Markdown")

    logging.info("El Pato Negro is running...")
    bot.polling()
