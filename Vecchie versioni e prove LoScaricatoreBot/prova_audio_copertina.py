import telebot
import urllib.request
from urllib.parse import urlparse, parse_qs

API_TOKEN = '5962251803:AAEnIFI7Z_VwR4x7Nnnjn4FMR4MsCveJpC8'
bot = telebot.TeleBot(API_TOKEN)

def get_video_id_from_url(video_url):
    parsed_url = urlparse(video_url)
    
    if parsed_url.netloc == 'youtu.be':
        # Estrai l'ID del video dagli URL youtu.be
        video_id = parsed_url.path.lstrip('/')
        return video_id
    elif parsed_url.netloc == 'www.youtube.com':
        # Estrai l'ID del video dagli URL completi di YouTube
        query_parameters = dict(parse_qsl(parsed_url.query))
        video_id = query_parameters.get('v')
        return video_id
    else:
        return None

@bot.message_handler(commands=['send_audio'])
def send_audio(message):
    # Simulated audio file path, replace with the actual file path
    audio_file_path = 'C:\\Users\\matte\Desktop\\1_LoScaricatoreBot\\Dennis Lloyd - Leftovers  A COLORS SHOW.mp3'

    with open(audio_file_path, 'rb') as f:
        audio_file = f.read()

    audio_file_input = telebot.types.InputFile(audio_file_path)

    # Simulated YouTube thumbnail URL, replace with the actual URL
    # Estrai il video ID dall'URL
    video_url = 'https://youtu.be/s87L5XWGiwI?list=PLqBdnr7qQNNC9pzMJL8TB2DaJ-EQNxloH'
    video_url = 'https://youtu.be/SwFbIpwDpoM'
    
    # parsed_url = urlparse(video_url)
    # video_id = parse_qs(parsed_url.query).get('v')

    parsed_url = urlparse(video_url)
    video_id = parsed_url.path.lstrip('/')
    print(video_id)
    thumbnail_url = f'https://img.youtube.com/vi/'+video_id+'/hqdefault.jpg'
    thumbnail_file_path = 'thumbnail.jpg'
    urllib.request.urlretrieve(thumbnail_url, thumbnail_file_path)

    thumbnail_file_input = telebot.types.InputFile(thumbnail_file_path)

    bot.send_audio(
        chat_id=message.chat.id,
        audio=audio_file_input,
        thumb=thumbnail_file_input,
        # title='My Audio File',
        # performer='Performer Name',  # Optional: add performer name
        # caption='This is my audio file.',  # Optional: add a caption
        # parse_mode='HTML'  # Optional: parse the caption as HTML
    )

    # Clean up by deleting the downloaded thumbnail image
    import os
    os.remove(thumbnail_file_path)

bot.polling()
