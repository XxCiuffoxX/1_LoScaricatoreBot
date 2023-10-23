import os
import telebot
from telebot import types
from pytube import YouTube
from moviepy.editor import *
from urllib.parse import urlparse, parse_qs
from eyed3.id3.frames import ImageFrame
from mutagen.mp4 import MP4, MP4Cover
import urllib.request
import pickle
import eyed3
import re

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


video_id = get_video_id("http://www.youtube.com/watch?v=47dtFZ8CFo8")

if(video_id is not None):
    thumbnail_url = f'https://img.youtube.com/vi/'+video_id+'/hqdefault.jpg'
    cover_image = video_id + '.jpg'
    cover_image_path = cover_image
    urllib.request.urlretrieve(thumbnail_url, cover_image)