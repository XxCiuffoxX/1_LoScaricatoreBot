'''
This is the code of the bot "LoScaricatoreBot". 
The bot allows you to download videos from YouTube in m4a or mp4 format.
'''

# necessary libraries
import os
import telebot
import json
import urllib.request
import pickle
import re
from telebot import types
from pytube import YouTube
from moviepy.editor import *
from urllib.parse import urlparse, parse_qs
from eyed3.id3.frames import ImageFrame
from mutagen.mp4 import MP4, MP4Cover


# function to get the video id
def get_video_id(video_url):
    parsed_url = urlparse(video_url)
    
    if parsed_url.netloc == 'youtu.be':
        # Estrai l'ID del video dagli URL youtu.be
        video_id = parsed_url.path.lstrip('/')
        return video_id
    elif parsed_url.netloc == 'www.youtube.com':
        # Estrai l'ID del video dagli URL completi di YouTube
        query_parameters = parse_qs(parsed_url.query)
        video_id = query_parameters.get('v', [None])[0]
        return video_id
    else:
        return None  # L'URL non è riconosciuto come link di YouTube


# function to save the received links in a txt file
def file_txt(video_link):

    with open('Video_Scaricati.txt', 'a') as text_file:
        text_file.write('Receive ->  ' + video_link + '\n')


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
def Download(link, format_num, call, session_data):

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
        download_error(call)

    # store the mp4 file name in mp4_file_name
    mp4_file_name = youtubeObject.default_filename

    # assign "session_data" the file name
    session_data['mp4_file_name'] = mp4_file_name
    session_data['m4a_file_name'] = ""

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

        # store the m4a file name in session_data
        session_data['m4a_file_name'] = m4a_file_name

        mp4_video.close()

        try:
            add_metadata(m4a_file_name, author, date, link, session_data)
        except:
            print("add metadata failed")  


def add_metadata(m4a_file_name, author, date, video_url, session_data):

    video_id = get_video_id(video_url)

    if(video_id is not None):
        thumbnail_url = f'https://img.youtube.com/vi/'+video_id+'/hqdefault.jpg'
        cover_image = video_id + '.jpg'
        cover_image_path = cover_image
        urllib.request.urlretrieve(thumbnail_url, cover_image)

    session_data['cover_image_path'] = str(cover_image_path)

    # Carica il file M4A
    audio = MP4(m4a_file_name)

    # Aggiungi i metadati
    audio["\xa9nam"] = m4a_file_name.replace(".m4a", "") # Nome della traccia
    audio["\xa9ART"] = author  # Artista
    audio["\xa9day"] = date # Anno di pubblicazione
    audio["\xa9cmt"] = "@LoScaricatoreBot"  # Commento

    # Aggiungi l'immagine di copertina
    with open(cover_image_path, "rb") as cover_image:
        cover_data = cover_image.read()
        audio["covr"] = [MP4Cover(cover_data, imageformat=MP4Cover.FORMAT_JPEG)]

    # Salva il file M4A con i metadati
    audio.save(m4a_file_name)     

    session_data['cover_image_path'] = cover_image_path
    # remove_file(cover_image_path) 


# function that sends an error message in case of failed download
def download_error(call):

    # send the error message to the user
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Sorry, download request failed.\nWe need some time to fix this.')


# function to send the file
def Send_file(chat_id, format_num, call, session_data):

    # assign the file name to mp4_file_name
    mp4_file_name = session_data.get('mp4_file_name')

    # assign the file name to m4a_file_name
    m4a_file_name = session_data.get('m4a_file_name')
    
    # thumbnail_file_input = telebot.types.InputFile(session_data.get('cover_image_path'))
    

    #check if there is a need to send an m4a file or mp4 file
    if (format_num == 0):

        cover_image = open(session_data.get('cover_image_path'), "rb")

        # open m4a file
        m4a_file = open(m4a_file_name, 'rb')

        audio_file_input = telebot.types.InputFile(m4a_file)

        # check if there are no errors while sending the file
        if bot.send_audio(chat_id=chat_id, audio=audio_file_input, title=m4a_file_name.replace(".m4a", ""), thumb=cover_image) is None:

            # if the file is not sent call the send_error function
            send_error(call)

        # close m4a file
        m4a_file.close()

        cover_image.close()

        # call the remove_file function
        remove_file(m4a_file_name)

        # call the remove_file function
        remove_file(mp4_file_name)

        remove_file(str(session_data.get('cover_image_path')))

    else: 
        
        # send mp4 file
        mp4_file = open(mp4_file_name, 'rb')

        # check if there are no errors while sending the file
        if bot.send_video(chat_id, mp4_file) is not None:

            # if the file is not sent call the send_error function
            send_error(call)
        
        # close mp4 file
        mp4_file.close()

        # call the remove_file function
        remove_file(mp4_file_name)


# function that sends an error message in case of failed sending
def send_error(call):

    # send the error message to the user
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Sorry, request to send failed.\nWe need some time to fix this.')


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
API_TOKEN = '5962251803:AAEnIFI7Z_VwR4x7Nnnjn4FMR4MsCveJpC8'
bot = telebot.TeleBot(API_TOKEN)

# file where the sessions exist
SESSIONS_FILE = "user_sessions.pkl"

translations = {}

languages = ["italiano", "inglese"]

for lang in languages:
    with open(f"{lang}.json", "r", encoding="utf-8") as file:
        translations[lang] = json.load(file)


# call the load_session function and assign the content to user_session
user_sessions = load_sessions()


# Handle '/start'
@bot.message_handler(commands=['start'])
def send_welcome(message):

    # identify the user
    user_id = message.from_user.id

    # check if the user has an active session
    if user_id in user_sessions:

        # create user_sessions
        user_sessions[user_id] = {}

    else:

        # start a new session for the user
        user_sessions[user_id] = {}

    # send the welcome message
    # bot.send_message(user_id, "Hi, I'm LoScaricatoreBot.😉\nSend me a YT link for the magic.🪄\nBut first, select a language\n\nCiao, sono LoScaricatoreBot.😉\nInviami un link di YT per la magia.🪄\nMa prima, scegli la lingua")
    first_message = "Hi, I'm LoScaricatoreBot.😉\nSend me a YT link for the magic.🪄\nBut first, select a language\n\nCiao, sono LoScaricatoreBot.😉\nInviami un link di YT per la magia.🪄\nMa prima, scegli la lingua"
    
    # create buttons
    keyboard = types.InlineKeyboardMarkup()
    m4a_button = types.InlineKeyboardButton(text=f'🇮🇹 Italiano', callback_data='it')
    mp4_button = types.InlineKeyboardButton(text=f'🇬🇧 English', callback_data='gb   ')

    # add buttons in two separate rows
    keyboard.row(m4a_button)
    keyboard.row(mp4_button)

    # send the message to the user
    bot.send_message(user_id, first_message, reply_markup = keyboard)
    
    # call the save_session function
    save_sessions(user_sessions)


# Handle '/end'
@bot.message_handler(commands=['end'])
def end(message):

    # identify the user
    user_id = message.from_user.id
    
    # check if the user has an active session
    if user_id in user_sessions:

        # end the user's session
        del user_sessions[user_id]

# Handle '/help'
@bot.message_handler(commands=['help'])
def help(message):

    # send the welcome message
    bot.reply_to(message, "Send me a YouTube link, choose the format you want, and I will send you the audio format (.m4a) than in video format (.mp4).\n\n" + 
                "Ways to send me the URL:\n" + 
                "1 Share the video link directly from the YouTube app.\n" +
                "2 Copy and paste the link from your browser " +
                "3 Use Telegram's inline bot by typing @vid titleVideo")
    

# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):

    # identify the user
    user_id = message.from_user.id
    
    # check if the user has an active session
    if user_id in user_sessions:

        # assigns the user's session to "session_data"
        session_data = user_sessions[user_id]

        # pattern for links
        pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        
        # if the message is a link
        if re.search(pattern, message.text):

            # assign to video_url the url sent by the user
            video_url = message.text

            # assigns the received url to "session_data".
            session_data['video_url'] = message.text

            # call the file_txt function
            file_txt(video_url)

            # call the length_control function
            if length_control(video_url):

                # if the video is too long send error message to user
                bot.reply_to(message, text = "Video duration too long.🤔\n(Choose a shorter video, maximum 8 minutes)")
                return
        
            # create buttons
            keyboard = types.InlineKeyboardMarkup()
            m4a_button = types.InlineKeyboardButton(text='🔊Only Audio', callback_data='m4a')
            mp4_button = types.InlineKeyboardButton(text='🎬Video (with sound)', callback_data='mp4')

            # add buttons in two separate rows
            keyboard.row(m4a_button)
            keyboard.row(mp4_button)

            # send the message to the user
            bot.reply_to(message, text = "Choose the format.\n👇", reply_markup = keyboard)
        
        else:
            # if the message is not a link send an error message to the user
            bot.reply_to(message, "This isn't a link!⚠️\nSend me a YT link, try again.😄\n")
            return


# buttons
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):

    # get the user id
    user_id = call.from_user.id

    # assigns the user's session to "session_data"
    session_data = user_sessions[user_id]

    # assign video_url the user's url
    video_url = session_data.get('video_url')

    # if the m4a button was pressed
    if call.data == 'm4a':

        # assign "session_data" the chosen file format
        session_data['format'] = 'm4a'
        
        # notifies the user that the system has received the request
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, disable_web_page_preview= True, text='Request made.👍\nWe\'re trying to download it.💿')

        # call the Download function to download the file
        # try:
        #     
        # except:
        #     print("errore nel download")
        
        Download(video_url, 0, call, session_data)

        # notifies the user that the system has downloaded the file and is now trying to send it
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, disable_web_page_preview= True, text='The download is finished.👌\nWe are now trying to send you the file.📤')

        # call the Send_file function to send the file to the user
        Send_file(user_id, 0, call, session_data)
        
    # if the mp4 button was pressed
    elif call.data == 'mp4':

        # assign "session_data" the chosen file format
        session_data['format'] = 'mp4'
                
        # notifies the user that the system has received the request
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, disable_web_page_preview= True, text='Request made.👍\nWe\'re trying to download it.💿')
        
        # call the Download function to download the file
        Download(video_url, 1, call, session_data)

        # notifies the user that the system has downloaded the file and is now trying to send it
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, disable_web_page_preview= True, text='The download is finished.👌\nWe are now trying to send you the file.📤')
        
        # call the Send_file function to send the file to the user
        Send_file(user_id, 1, call, session_data)
        


# the bot is always active
bot.infinity_polling()