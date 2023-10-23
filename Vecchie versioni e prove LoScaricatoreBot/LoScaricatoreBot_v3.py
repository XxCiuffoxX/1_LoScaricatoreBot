import os
import telebot
from telebot import types
from pytube import YouTube
from mutagen.mp4 import MP4
from moviepy.editor import *
#from pydub import AudioSegment
import ffmpeg
import re #per individuare il link

def file_txt(video_link):
    with open('Video_Scaricati.txt', 'a') as text_file:
        text_file.write('Receive ->  ' + video_link + '\n')


def length_control(link):
    youtubeObject = YouTube(link)
    length_in_sec = youtubeObject.length
    print(f"Durata del video: {length_in_sec} secondi")
    if length_in_sec > 480:
        print("Troppo lungo")
        return 1
    else: 
        return 0


def Download(link, format_num):
    #convert link into object
    youtubeObject = YouTube(link)
    youtubeObject = youtubeObject.streams.get_highest_resolution()

    try:
        #download the video
        youtubeObject.download()
    except:
        print("There has been an error in downloading your youtube video")

    #global variable that contains the name of the file in mp4 format
    global mp4_file_name
    mp4_file_name = youtubeObject.default_filename

    #check if there is a need to convert mp4 file to mp4 file
    if (format_num == 1):
        #convert the video in mp3
        mp4_video = VideoFileClip(mp4_file_name)

        mp3_file = mp4_video.audio

        #global variable that contains the name of the file in mp3 format
        global mp3_file_name
        mp3_file_name = mp4_file_name.replace(".mp4", ".mp3")

        mp3_file.write_audiofile(mp3_file_name, codec = 'libmp3lame')

        mp4_video.close()

    print("\n**************************************")
    print("This download has completed!")
    print("**************************************\n")


def Send_video(chat_id, format_num):
        #check if there is a need to send an mp3 file to mp4 file
        #if format_num == 1 is an mp3 file
        if (format_num == 1):
            mp3_file = open(mp3_file_name, 'rb')
            try:
                bot.send_audio(chat_id, mp3_file)

                mp3_file.close()
                remove_file(mp3_file_name)

            except:
                mp3_file.close()
                remove_file(mp3_file_name)
                return 0
        else: 
            mp4_file = open(mp4_file_name, 'rb')
            try:
                bot.send_video(chat_id, mp4_file)
                mp4_file.close()
            except:
                mp4_file.close()
                remove_file(mp4_file_name)
                return 0
        
        remove_file(mp4_file_name)

    #out of if couse ther's alway an mp4 file
    #call remove_file function
    #remove_file(mp4_file_name)


def remove_file(file_name):
    file_path = file_path = "C:\\Users\\matte\\Desktop\\Bot_Telegram\\" + file_name
    try:
        os.remove(file_path)
        print("\n\nFile eliminato con successo.\n")
    except OSError as e:
        print(f"\n\nErrore durante l'eliminazione del file: {e}\n")




API_TOKEN = '5962251803:AAEnIFI7Z_VwR4x7Nnnjn4FMR4MsCveJpC8'
bot = telebot.TeleBot(API_TOKEN)


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, """\
Hi, I'm LoScaricatoreBot.
Send me a YT link for the magic.\
""")
    


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    link = re.search(pattern, message.text)

    if link:

        global chat_id
        chat_id = message.chat.id
        #global video_url
        video_url = message.text

        file_txt(video_link=video_url)

        #if length_control(video_url) == 1:
        #    bot.send_message(chat_id = message.chat.id, text = "Video duration too long. \n(Choose a shorter video, maximum 8 minutes)")
        #    return
        
        

        #create and print the buttons
        keyboard = types.InlineKeyboardMarkup()
        mp3_button = types.InlineKeyboardButton(text='MP3', callback_data='mp3')
        mp4_button = types.InlineKeyboardButton(text='MP4', callback_data='mp4')
        keyboard.add(mp3_button, mp4_button)
        bot.send_message(chat_id = message.chat.id, text = "Choose the format.", reply_markup = keyboard)
        

        #buttons
        @bot.callback_query_handler(func=lambda call: True)
        def callback_query(call):

            if call.data == 'mp3':
                
                # Handle MP3 button press
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Request made.')

                Download(video_url, 1)

                Send_video(chat_id, 1)
                #bot.answer_callback_query(callback_query_id=call.id, text="Hai scelto MP3")

            elif call.data == 'mp4':
                        
                # Handle MP4 button press
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Request made.')

                Download(video_url, 0)

                Send_video(chat_id, 0)

                #bot.answer_callback_query(callback_query_id=call.id, text="Hai scelto MP4")

        #bot.reply_to(message, "I'm trying to download it...\n")

    else:
       bot.reply_to(message, "This isn't a link, send me a YT link, try again.\n")
       return


bot.infinity_polling()
