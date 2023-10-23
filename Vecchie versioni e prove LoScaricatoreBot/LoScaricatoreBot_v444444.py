import os
import telebot
from telebot import types
from pytube import YouTube
from mutagen.mp4 import MP4
from moviepy.editor import *
import pickle
#from pydub import AudioSegment
#import ffmpeg
import re #per individuare il link


# save links in a txt file
def file_txt(video_link):
    with open('Video_Scaricati.txt', 'a') as text_file:
        text_file.write('Receive ->  ' + video_link + '\n')


# check the length of the video
def length_control(link):
    youtubeObject = YouTube(link)
    length_in_sec = youtubeObject.length
    print(f"Video length: {length_in_sec} seconds")

    # if the video takes too long send a message
    if length_in_sec > 480:
        print("The video is too long.")
        return 1
    else: 
        return 0


# download the video
def Download(link, format_num, call, session_data):
    # convert link into object
    youtubeObject = YouTube(link)
    youtubeObject = youtubeObject.streams.get_highest_resolution()
    print("il titolo è " + youtubeObject.default_filename)
    
    # download the video
    if youtubeObject.download() == None:
        print("There has been an error in downloading your youtube video")
        download_error(call)

    # store the downloaded file name in session_data
    session_data['file_name'] = youtubeObject.default_filename

    # global variable that contains the name of the file in mp4 format
    # global mp4_file_name
    # mp4_file_name = ""
    # mp4_file_name = youtubeObject.default_filename

    # check if there is a need to convert mp4 file to mp4 file
    # if (format_num == 1):
    #     # convert the video in mp3
    #     mp4_video = VideoFileClip(mp4_file_name)

    #     mp3_file = mp4_video.audio

    #     # global variable that contains the name of the file in mp3 format
    #     global mp3_file_name
    #     mp3_file_name = mp4_file_name.replace(".mp4", ".mp3")

    #     mp3_file.write_audiofile(mp3_file_name, codec = 'libmp3lame')

    #     # store the mp3 file name in session_data
    #     session_data['mp3_file_name'] = mp3_file_name

    #     mp4_video.close()

    print("\n**************************************")
    print("This download has completed!")
    print("**************************************\n")


# send the download error message
def download_error(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Sorry, download request failed.\nWe need some time to fix this.')


# send file
def Send_file(chat_id, format_num, call, session_data):
    #check if there is a need to send an mp3 file to mp4 file

    # assegna a video_url l'url dell'utente
    mp4_file_name = session_data.get('file_name')

    if (format_num == 1):

        # send mp3 file
        mp3_file = open(mp4_file_name, 'rb')

        if bot.send_audio(chat_id, mp3_file) != "On success, the sent Message is returned.":
            send_error(call)

        mp3_file.close()
        remove_file(mp4_file_name)

    else: 
        
        # send mp4 file
        mp4_file = open(mp4_file_name, 'rb')

        if bot.send_video(chat_id, mp4_file) == None:
            send_error(call)
        
        mp4_file.close()
        remove_file(mp4_file_name)


# send the send error message
def send_error(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Sorry, request to send failed.\nWe need some time to fix this.')


# remove downloaded files
def remove_file(file_name):
    file_path = file_path = "C:\\Users\\matte\\Desktop\\1_LoScaricatoreBot\\" + file_name
    try:
        os.remove(file_path)
        print("\n\nSuccessfully deleted file.\n")
    except OSError as e:
        print(f"\n\nError deleting file: {e}\n")


# API 
API_TOKEN = '5962251803:AAEnIFI7Z_VwR4x7Nnnjn4FMR4MsCveJpC8'
bot = telebot.TeleBot(API_TOKEN)

# file in cui sono presenti le sessioni
SESSIONS_FILE = "user_sessions.pkl"

# Carica le sessioni da file (se presente)
def load_sessions():
    try:
        with open(SESSIONS_FILE, "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return {}
    
# Salva le sessioni su file
def save_sessions(sessions):
    with open(SESSIONS_FILE, "wb") as file:
        pickle.dump(sessions, file)

# Carica le sessioni all'avvio del bot
user_sessions = load_sessions()


# Dizionario per mantenere le informazioni di sessione degli utenti
# user_sessions = {}


# Handle '/start'
@bot.message_handler(commands=['start'])
def send_welcome(message):

    # Identifica l'utente
    user_id = message.from_user.id

    # Verifica se l'utente ha una sessione attiva
    if user_id in user_sessions:
        user_sessions[user_id] = {}
    else:
        # Avvia una nuova sessione per l'utente
        user_sessions[user_id] = {}

    bot.reply_to(message, "Hi, I'm LoScaricatoreBot.😉\nSend me a YT link for the magic.🪄\n sessione: " + str(user_id))
    
    # Salva le sessioni su file
    save_sessions(user_sessions)


@bot.message_handler(commands=['end'])
def end(message):
    # Identifica l'utente
    user_id = message.from_user.id
    
    # Verifica se l'utente ha una sessione attiva
    if user_id in user_sessions:
        # Termina la sessione dell'utente
        del user_sessions[user_id]
    #     bot.reply_to(message, "Session ended.")
    # else:
    #     bot.reply_to(message, "No active session.")
    

# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):

    # Identifica l'utente
    user_id = message.from_user.id
    
     # Verifica se l'utente ha una sessione attiva
    if user_id in user_sessions:
        # Esegui le operazioni della sessione dell'utente
        session_data = user_sessions[user_id]
        # print(session_data)
        pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        
        if re.search(pattern, message.text):

            # assegno a video_url l'url mandato dall'utente
            video_url = message.text

            # salvo in session_data l'url richiesto
            session_data['video_url'] = message.text

            # salvo l'url nel file txt
            file_txt(video_url)

            # controllo la lunghezza del video
            if length_control(video_url) == 1:
                bot.reply_to(message, text = "Video duration too long.🤔\n(Choose a shorter video, maximum 8 minutes)")
                return
        
            # create and print the buttons
            keyboard = types.InlineKeyboardMarkup()
            mp3_button = types.InlineKeyboardButton(text='🔊Only Audio', callback_data='mp3')
            mp4_button = types.InlineKeyboardButton(text='🎬Video (with sound)', callback_data='mp4')

            # Aggiungi i pulsanti in due righe separate
            keyboard.row(mp3_button)
            keyboard.row(mp4_button)
            bot.reply_to(message, text = "Choose the format.\n👇", reply_markup = keyboard)
        
        else:
            # se il messaggio non è un link mostra errore
            bot.reply_to(message, "This isn't a link!⚠️\nSend me a YT link, try again.😄\n" + str(user_id))
            return


#buttons
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):

    # ricava l'id dell'utente
    user_id = call.from_user.id
    # video_url = user_id.video_url
    
    
    # if user_id not in user_sessions:
    #     user_sessions[user_id] = {}

    # assegna a session data la sessione dell'utente
    session_data = user_sessions[user_id]

    # assegna a video_url l'url dell'utente
    video_url = session_data.get('video_url')

    if call.data == 'mp3':
        session_data['format'] = 'mp3'
        
        # Handle MP3 button press
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, disable_web_page_preview= True, text='Request made.👍\nWe\'re trying to download it.💿\n' + str(user_id) + "\n" + video_url + session_data['format'])

        Download(video_url, 1, call, session_data)

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, disable_web_page_preview= True, text='The download is finished.👌\nWe are now trying to send you the file.📤' + str(user_id)+ "\n" + video_url + "\n" + session_data['format'])

        Send_file(user_id, 1, call, session_data)
        

    elif call.data == 'mp4':
        session_data['format'] = 'mp4'
                
        # Handle MP4 button press
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, disable_web_page_preview= True, text='Request made.👍\nWe\'re trying to download it.💿'+ str(user_id) + "\n" + video_url)
        
        Download(video_url, 0, call, session_data)

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, disable_web_page_preview= True, text='The download is finished.👌\nWe are now trying to send you the file.📤'+ str(user_id)+ "\n" + video_url)
        
        Send_file(user_id, 0, call, session_data)



bot.infinity_polling()