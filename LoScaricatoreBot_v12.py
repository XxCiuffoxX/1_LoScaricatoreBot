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


# function to get the video id
def get_video_id(video_url):

    # splits the URL
    parsed_url = urlparse(video_url)
    
    if parsed_url.netloc == 'youtu.be':

        # Extract the video ID from "youtu.be" URLs
        video_id = parsed_url.path.lstrip('/')
        return video_id
    
    elif parsed_url.netloc == 'www.youtube.com':

        # Extract the video ID from "youtube.com" URLs
        query_parameters = parse_qs(parsed_url.query)
        video_id = query_parameters.get('v', [None])[0]
        return video_id
    else:

        # the URL is not recognized as a YouTube link
        return None


# function to check the playing time of the video
def length_control(link):

    # convert link into object
    youtubeObject = YouTube(link)

    # check the video playing time
    length_in_sec = youtubeObject.length

    # if the video takes too long send a message
    if length_in_sec > 480:
        return True
    else: 
        return False


# function to download the video
def Download(link, format_num, call, user_session):

    # convert link into object
    yt = YouTube(link)

    # save video info
    author = yt.author
    date = str(yt.publish_date.year)

    # take the highest resolution
    youtubeObject = yt.streams.get_highest_resolution()
    
    # check if the download is successful
    if youtubeObject.download() is None:

        # if download fails call download_error function
        download_error(call, user_session)

    # store the mp4 file name in mp4_file_name
    mp4_file_name = youtubeObject.default_filename

    # assign "user_session" the file name
    user_session['mp4_file_name'] = mp4_file_name
    user_session['m4a_file_name'] = ""

    # check if there is a need to convert mp4 file to mp4 file
    if (format_num == 0):

        # open the video
        mp4_video = VideoFileClip(mp4_file_name)

        # take the mp4 file's audio
        m4a_file = mp4_video.audio

        # store the m4a file name in mp4_file_name with .m4a extension
        m4a_file_name = mp4_file_name.replace(".mp4", ".m4a")

        # convert the video in m4a
        m4a_file.write_audiofile(m4a_file_name, codec="aac")

        # store the m4a file name in user_session
        user_session['m4a_file_name'] = m4a_file_name

        mp4_video.close()

        try:
            add_metadata(m4a_file_name, author, date, link, user_session)
        except:
            print("add metadata failed")  


# function to add metadata to the file
def add_metadata(m4a_file_name, author, date, video_url, user_session):

    # get the video id
    video_id = get_video_id(video_url)

    # check if video_is is not null
    if(video_id is not None):

        # gets and downloads the video cover
        thumbnail_url = f'https://img.youtube.com/vi/'+video_id+'/hqdefault.jpg'
        cover_image = video_id + '.jpg'
        cover_image_path = cover_image
        urllib.request.urlretrieve(thumbnail_url, cover_image)

    # store the cover_image path in user_session
    user_session['cover_image_path'] = str(cover_image_path)

    # upload the M4A file
    audio = MP4(m4a_file_name)

    # adds metadata
    audio["\xa9nam"] = m4a_file_name.replace(".m4a", "") # Nome della traccia
    audio["\xa9ART"] = author  # Artista
    audio["\xa9day"] = date # Anno di pubblicazione
    audio["\xa9cmt"] = "@LoScaricatoreBot"  # Commento

    # add your cover photo
    with open(cover_image_path, "rb") as cover_image:
        cover_data = cover_image.read()
        audio["covr"] = [MP4Cover(cover_data, imageformat=MP4Cover.FORMAT_JPEG)]

    # save the M4A file with metadata
    audio.save(m4a_file_name)     

    user_session['cover_image_path'] = cover_image_path


# function that sends an error message in case of failed download
def download_error(call, user_session):
        
    # gets the user's language
    user_language = user_session.get('language', None)

    # send the error message to the user
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=translations[user_language]["download_error"])


# function to send the file
def Send_file(chat_id, format_num, call, user_session):

    # assign the file name to mp4_file_name
    mp4_file_name = user_session.get('mp4_file_name')

    # assign the file name to m4a_file_name
    m4a_file_name = user_session.get('m4a_file_name')

    #check if there is a need to send an m4a file or mp4 file
    if (format_num == 0):

        cover_image = open(user_session.get('cover_image_path'), "rb")

        # open m4a file
        m4a_file = open(m4a_file_name, 'rb')

        audio_file_input = telebot.types.InputFile(m4a_file)

        # check if there are no errors while sending the file
        if bot.send_audio(chat_id=chat_id, audio=audio_file_input, title=m4a_file_name.replace(".m4a", ""), thumb=cover_image) is None:

            # if the file is not sent call the send_error function
            send_error(call, user_session)

        # close m4a file
        m4a_file.close()

        # close cover_image file
        cover_image.close()

        # call the remove_file function
        remove_file(m4a_file_name)

        # call the remove_file function
        remove_file(mp4_file_name)

        remove_file(str(user_session.get('cover_image_path')))

    else: 
        
        # send mp4 file
        mp4_file = open(mp4_file_name, 'rb')

        # check if there are no errors while sending the file
        if bot.send_video(chat_id, mp4_file) is not None:

            # if the file is not sent call the send_error function
            send_error(call, user_session)
        
        # close mp4 file
        mp4_file.close()

        # call the remove_file function
        remove_file(mp4_file_name)


# function that sends an error message in case of failed sending
def send_error(call, user_session):

    # gets the user's language
    user_language = user_session.get('language', None)

    # send the error message to the user
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=translations[user_language]['send_error'])


# function to remove the downloaded file
def remove_file(file_name):

    # create the path
    file_path = file_path = "C:\\Users\\matte\\Desktop\\Progetti\\1_LoScaricatoreBot\\" + file_name

    # try deleting the file
    try:
        os.remove(file_path)
        print("\n\nSuccessfully deleted file.\n")
    except OSError as e:
        print(f"\n\nError deleting file: {e}\n")


# function to load sessions from file (if present)
def load_sessions():

    # try opening the file
    try:
        with open(SESSIONS_FILE, "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return {}
    

# function to save sessions to file
def save_sessions(sessions):

    # try opening the file
    with open(SESSIONS_FILE, "wb") as file:
        pickle.dump(sessions, file)


# API 
#-API_TOKEN = '6298767518:AAEl_6YTb6s_rk0BGvNbl0B5V6EnEftnuug'
API_TOKEN = '5962251803:AAEnIFI7Z_VwR4x7Nnnjn4FMR4MsCveJpC8'
bot = telebot.TeleBot(API_TOKEN)

# file where the sessions exist
SESSIONS_FILE = "all_sessions.pkl"

translations = {}

languages = ["it", "en"]

for lang in languages:
    with open(f"{lang}.json", "r", encoding="utf-8") as file:
        translations[lang] = json.load(file)


# call the load_session function and assign the content to user_session
all_sessions = load_sessions()


# Handle '/start'
@bot.message_handler(commands=['start'])
def send_welcome(message):

    # identify the user
    user_id = message.from_user.id

    # check if the user has an active session
    if user_id in all_sessions:

        user_session = all_sessions[user_id]
        
        # gets the user's language
        user_language = user_session.get('language', None)

        if user_language in translations:
            bot.send_message(user_id, text=translations[user_language]['welcome'])
        else:
            bot.send_message(user_id, "Hi, I'm LoScaricatoreBot.😉\nSend me a YT link for the magic.🪄\n\nCiao, sono LoScaricatoreBot.😉\nInviami un link di YT per la magia.🪄")

    else:

        # start a new session for the user
        all_sessions[user_id] = {}
        save_sessions(all_sessions)
        user_session = all_sessions[user_id]
        language(message)
        

# Handle '/end'
@bot.message_handler(commands=['end'])
def end(message):

    # identify the user
    user_id = message.from_user.id
    
    # check if the user has an active session
    if user_id in all_sessions:

        # end the user's session
        del all_sessions[user_id]

    save_sessions(all_sessions)

# Handle '/help'
@bot.message_handler(commands=['help'])
def help(message):

    # identify the user
    user_id = message.from_user.id
    
    user_session = all_sessions[user_id]
        
    # gets the user's language
    user_language = user_session.get('language', None)

    if user_language in translations:
        bot.send_message(user_id, text=translations[user_language]['help'])
    else:
        bot.send_message(user_id, text=translations['en']['help'])


# Handle '/language' or '/lingua'
@bot.message_handler(commands=['language'])
@bot.message_handler(commands=['lingua'])
def language(message):

    # identify the user
    user_id = message.from_user.id

    # create buttons
    keyboard = types.InlineKeyboardMarkup()
    it_button = types.InlineKeyboardButton(text=f'🇮🇹 Italiano', callback_data='it')
    en_button = types.InlineKeyboardButton(text=f'🇬🇧 English', callback_data='en')

    # add buttons in two separate rows
    keyboard.row(it_button)
    keyboard.row(en_button)

    # send the message to the user
    bot.send_message(user_id, text="Hi, I'm LoScaricatoreBot.😉\nSend me a YT link for the magic.🪄\nBut first select a language:\n\nCiao, sono LoScaricatoreBot.😉\nInviami un link di YT per la magia.🪄\nMa prima scegli una lingua:", reply_markup = keyboard)   


def set_language(user_id, language_code):

    user_session = all_sessions[user_id]

    # Imposta il valore dell'attributo "lingua"
    user_session['language'] = str(language_code)

    save_sessions(all_sessions)


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):

    # identify the user
    user_id = message.from_user.id
    
    # check if the user has an active session
    if user_id in all_sessions:

        # assigns the user's session to "user_session"
        user_session = all_sessions[user_id]
        
        user_language = user_session.get('language', None)

        # pattern for links
        pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        
        # if the message is a link
        if re.search(pattern, message.text):

            # assign to video_url the url sent by the user
            video_url = message.text

            # assigns the received url to "user_session".
            user_session['video_url'] = message.text

            # call the length_control function
            if length_control(video_url):

                # if the video is too long send error message to user
                bot.reply_to(message, text = translations[user_language]['video_too_long'])
                return
        
            # create buttons
            keyboard = types.InlineKeyboardMarkup()
            m4a_button = types.InlineKeyboardButton(text=translations[user_language]['audio_button'], callback_data='m4a')
            mp4_button = types.InlineKeyboardButton(text=translations[user_language]['video_button'], callback_data='mp4')

            # add buttons in two separate rows
            keyboard.row(m4a_button)
            keyboard.row(mp4_button)

            # send the message to the user
            bot.reply_to(message, text = translations[user_language]['choose_format'], reply_markup = keyboard)
        
        else:
            # if the message is not a link send an error message to the user
            bot.reply_to(message, text=translations[user_language]["not_a_link"])
            return


# buttons
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):

    # get the user id
    user_id = call.from_user.id

    # assigns the user's session to "user_session"
    user_session = all_sessions[user_id]

    # gets the user's language
    user_language = user_session.get('language', None)

    # assign video_url the user's url
    video_url = user_session.get(('video_url'))

    # if the m4a button was pressed
    if call.data == 'm4a':

        # assign "user_session" the chosen file format
        user_session['format'] = 'm4a'
        
        # notifies the user that the system has received the request
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, disable_web_page_preview= True, text=translations[user_language]['download_request'])
        
        Download(video_url, 0, call, user_session)

        # notifies the user that the system has downloaded the file and is now trying to send it
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, disable_web_page_preview= True, text=translations[user_language]['send_request'])

        # call the Send_file function to send the file to the user
        Send_file(user_id, 0, call, user_session)
        
    # if the mp4 button was pressed
    elif call.data == 'mp4':

        # assign "user_session" the chosen file format
        user_session['format'] = 'mp4'
                
        # notifies the user that the system has received the request
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, disable_web_page_preview= True, text=translations[user_language]['download_request'])
        
        # call the Download function to download the file
        Download(video_url, 1, call, user_session)

        # notifies the user that the system has downloaded the file and is now trying to send it
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, disable_web_page_preview= True, text=translations[user_language]['send_request'])
        
        # call the Send_file function to send the file to the user
        Send_file(user_id, 1, call, user_session)

    elif call.data == 'it':
        set_language(user_id, language_code="it")

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, disable_web_page_preview= True, text=translations['it']['welcome'])
        

    elif call.data == 'en':
        set_language(user_id, language_code="en")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, disable_web_page_preview= True, text=translations['en']['welcome'])


# the bot is always active
bot.infinity_polling()