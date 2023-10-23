from pytube import YouTube
import moviepy.editor as mp
import eyed3
import os

# URL del video di YouTube da scaricare
video_url = 'http://www.youtube.com/watch?v=N3qxFptQbVA'

# Directory di lavoro
working_dir = 'C:/Users/matte/Desktop/Progetti/1_LoScaricatoreBot'
os.chdir(working_dir)

# Scarica il video da YouTube
yt = YouTube(video_url)
video_stream = yt.streams.get_highest_resolution()
video_stream.download()

# Ottieni le informazioni sul video
titolo = yt.title
artista = yt.author
anno = yt.publish_date.year

# Converti il video in MP3
video_filename = os.path.splitext(yt.title)[0] + ".mp4"
mp4_file_path = os.path.join(working_dir, video_filename)
mp3_file_path = os.path.join(working_dir, f"{titolo}.mp3")

clip = mp.VideoFileClip(mp4_file_path)
clip.audio.write_audiofile(mp3_file_path)

# Aggiungi i metadati al file MP3
audiofile = eyed3.load(mp3_file_path)
audiofile.tag.title = titolo
audiofile.tag.artist = artista
audiofile.tag.year = str(anno)

# Aggiungi la copertina dell'album
copertina_youtube = yt.thumbnail_url
copertina_filename = os.path.join(working_dir, f"{titolo}.jpg")
os.system(f'wget "{copertina_youtube}" -O "{copertina_filename}"')
with open(copertina_filename, 'rb') as cover_image:
    audiofile.tag.images.set(3, cover_image.read(), 'image/jpeg', u"Description")

# Aggiungi i commenti
audiofile.tag.comments.set(str("Ciao a tutti"))

# Salva le modifiche
audiofile.tag.save()

# Rimuovi il file video MP4
os.remove(mp4_file_path)

print("Conversione completata con successo.")
