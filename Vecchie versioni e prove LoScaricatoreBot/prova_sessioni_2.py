'''
This is the code of the bot "LoScaricatoreBot". 
The bot allows you to download videos from YouTube in m4a or mp4 format.
'''

# necessary libraries
import os
import telebot
import json
from telebot import types
from pytube import YouTube
from moviepy.editor import *
from urllib.parse import urlparse, parse_qs
from eyed3.id3.frames import ImageFrame
from mutagen.mp4 import MP4, MP4Cover
import urllib.request
import pickle
import re

def load_sessions():

    try:
        with open(SESSIONS_FILE, "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return {}
    
def save_sessions(sessions):

    with open(SESSIONS_FILE, "wb") as file:
        pickle.dump(sessions, file)


API_TOKEN = '6298767518:AAEl_6YTb6s_rk0BGvNbl0B5V6EnEftnuug'
bot = telebot.TeleBot(API_TOKEN)

SESSIONS_FILE = "all_sessions.pkl"

translations = {}

languages = ["it", "en"]

for lang in languages:
    with open(f"{lang}.json", "r", encoding="utf-8") as file:
        translations[lang] = json.load(file)

all_sessions = load_sessions()


# Handle '/start'
@bot.message_handler(commands=['start'])
def send_welcome(message):

    user_id = message.from_user.id

    if user_id in all_sessions:

        user_session = all_sessions[user_id]
        user_language = user_session.get('language', None)

        if user_language in translations:
            bot.send_message(user_id, text=translations[user_language]['welcome'])
        else:
            print("Nessuna lingua")

    else:

        all_sessions[user_id] = {'language': '', 'nome':'Mario'}
        save_sessions(all_sessions)

    save_sessions(all_sessions)


# Handle '/end'
@bot.message_handler(commands=['end'])
def end(message):

    # identify the user
    user_id = message.from_user.id
    
    # check if the user has an active session
    if user_id in all_sessions:

        # end the user's session
        del all_sessions[user_id]

# the bot is always active
bot.infinity_polling()