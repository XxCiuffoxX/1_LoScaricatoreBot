import youtube_dl

# Definisci le opzioni per il download
options = {
    'format': 'bestvideo+bestaudio',
}

# Crea un'istanza di youtube-dl
ydl = youtube_dl.YoutubeDL(options)

# Scarica il video
video_url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
with ydl:
    result = ydl.extract_info(
        video_url,
        download=True # scarica il video
    )
