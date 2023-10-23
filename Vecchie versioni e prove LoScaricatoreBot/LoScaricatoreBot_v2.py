import os
import telebot
from pytube import YouTube
from mutagen.mp4 import MP4
from pydub import AudioSegment
import ffmpeg
import re #per individuare il link


def Download(link):
  #converte il link in 'oggetto'
  youtubeObject = YouTube(link)
  youtubeObject = youtubeObject.streams.get_highest_resolution()
  
  try:
      #effettua il download
      youtubeObject.download()
  except:
    print("There has been an error in downloading your youtube video")

  global file_name_2
  file_name_2 = youtubeObject.default_filename

  print("\n**************************************")
  print("This download has completed! Yahooooo!")
  print("**************************************\n")


def Send_video(chat_id):
    video = open(file_name_2, 'rb')
    bot.send_video(chat_id, video)
    bot.send_video(chat_id, "FILEID")


API_TOKEN = '5962251803:AAEnIFI7Z_VwR4x7Nnnjn4FMR4MsCveJpC8'
bot = telebot.TeleBot(API_TOKEN)


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, """\
Ciao sono er bot supremo.
Inviami il link per la magia.\
""")


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    link = re.search(pattern, message.text)

    if link:
        bot.reply_to(message, "I'm trying to download it...\n")
        chat_id = message.chat.id
        video_url = message.text

        Download(video_url)

        Send_video(chat_id)
    else:
       bot.reply_to(message, "This isn't a link, send me a yt link\n")


bot.infinity_polling()
