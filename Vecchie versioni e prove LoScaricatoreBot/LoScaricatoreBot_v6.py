'''
This is the code of the bot "LoScaricatoreBot". 
The bot allows you to download videos from YouTube in mp3 or mp4 format.
'''

# necessary libraries
import os
import telebot
from telebot import types
from pytube import YouTube
from mutagen.mp4 import MP4
from moviepy.editor import *
from urllib.parse import urlparse, parse_qs
import urllib.request
import pickle
import re


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
        print("The video is too long.")
        return 1
    else: 
        return 0


# function to download the video
def Download(link, format_num, call, session_data):

    # convert link into object
    youtubeObject = YouTube(link)

    # take the highest resolution
    youtubeObject = youtubeObject.streams.get_highest_resolution()
    
    # check if the download is successful
    if youtubeObject.download() is None:

        # if download fails call download_error function
        download_error(call)

    # assign "session_data" the file name
    session_data['mp4_file_name'] = youtubeObject.default_filename
    session_data['mp3_file_name'] = ""

    # store the mp4 file name in mp4_file_name
    mp4_file_name = youtubeObject.default_filename

    # check if there is a need to convert mp4 file to mp4 file
    if (format_num == 1):
        # open the video
        mp4_video = VideoFileClip(mp4_file_name)

        # convert the video in mp3
        mp3_file = mp4_video.audio

        # store the mpe file name in mp4_file_name with .mp3 extension
        mp3_file_name = mp4_file_name.replace(".mp4", ".mp3")

        # convert the video in mp3
        mp3_file.write_audiofile(mp3_file_name, codec = 'libmp3lame')

        # store the mp3 file name in session_data
        session_data['mp3_file_name'] = mp3_file_name

        mp4_video.close()


# function that sends an error message in case of failed download
def download_error(call):

    # send the error message to the user
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Sorry, download request failed.\nWe need some time to fix this.')


# function to send the file
def Send_file(chat_id, format_num, call, session_data, video_url):

    # assign the file name to mp4_file_name
    mp4_file_name = session_data.get('mp4_file_name')

    # assign the file name to mp3_file_name
    mp3_file_name = session_data.get('mp3_file_name')

    #check if there is a need to send an mp3 file to mp4 file
    if (format_num == 1):


        # open mp3 file
        mp3_file = open(mp3_file_name, 'rb')

        audio_file_input = telebot.types.InputFile(mp3_file)

        video_id = get_video_id(video_url)
        if(video_id is not None):
            thumbnail_url = f'https://img.youtube.com/vi/'+video_id+'/hqdefault.jpg'
            thumbnail_file_path = video_id + '.jpg'
            urllib.request.urlretrieve(thumbnail_url, thumbnail_file_path)

        

        # thumbnail_file_path = download_image(video_url)

        thumbnail_file_input = telebot.types.InputFile(thumbnail_file_path)

        # check if there are no errors while sending the file
        if bot.send_audio(chat_id=chat_id, audio=audio_file_input, thumb=thumbnail_file_input) is None:

            # if the file is not sent call the send_error function
            send_error(call)

        # close mp3 file
        mp3_file.close()

        # call the remove_file function
        remove_file(mp3_file_name)

        # call the remove_file function
        remove_file(mp4_file_name)

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
    bot.reply_to(message, "Hi, I'm LoScaricatoreBot.😉\nSend me a YT link for the magic.🪄\n sessione: " + str(user_id))
    
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
            if length_control(video_url) == 1:

                # if the video is too long send error message to user
                bot.reply_to(message, text = "Video duration too long.🤔\n(Choose a shorter video, maximum 8 minutes)")
                return
        
            # create buttons
            keyboard = types.InlineKeyboardMarkup()
            mp3_button = types.InlineKeyboardButton(text='🔊Only Audio', callback_data='mp3')
            mp4_button = types.InlineKeyboardButton(text='🎬Video (with sound)', callback_data='mp4')

            # add buttons in two separate rows
            keyboard.row(mp3_button)
            keyboard.row(mp4_button)

            # send the message to the user
            bot.reply_to(message, text = "Choose the format.\n👇", reply_markup = keyboard)
        
        else:
            # if the message is not a link send an error message to the user
            bot.reply_to(message, "This isn't a link!⚠️\nSend me a YT link, try again.😄\n" + str(user_id))
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

    # if the mp3 button was pressed
    if call.data == 'mp3':

        # assign "session_data" the chosen file format
        session_data['format'] = 'mp3'
        
        # notifies the user that the system has received the request
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, disable_web_page_preview= True, text='Request made.👍\nWe\'re trying to download it.💿')

        # call the Download function to download the file
        Download(video_url, 1, call, session_data)

        # notifies the user that the system has downloaded the file and is now trying to send it
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, disable_web_page_preview= True, text='The download is finished.👌\nWe are now trying to send you the file.📤')

        # call the Send_file function to send the file to the user
        Send_file(user_id, 1, call, session_data, video_url)
        
    # if the mp4 button was pressed
    elif call.data == 'mp4':

        # assign "session_data" the chosen file format
        session_data['format'] = 'mp4'
                
        # notifies the user that the system has received the request
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, disable_web_page_preview= True, text='Request made.👍\nWe\'re trying to download it.💿')
        
        # call the Download function to download the file
        Download(video_url, 0, call, session_data)

        # notifies the user that the system has downloaded the file and is now trying to send it
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, disable_web_page_preview= True, text='The download is finished.👌\nWe are now trying to send you the file.📤')
        
        # call the Send_file function to send the file to the user
        Send_file(user_id, 0, call, session_data, video_url)


# the bot is always active
bot.infinity_polling()