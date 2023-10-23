from pytube import YouTube
import moviepy.editor as mp
from mutagen.mp4 import MP4
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TDRC, COMM
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

# Converti il video in M4A
video_filename = os.path.splitext(yt.title)[0] + ".mp4"
m4a_file_path = os.path.join(working_dir, f"{titolo}.m4a")

clip = mp.VideoFileClip(video_filename)
clip.audio.write_audiofile(m4a_file_path, codec='aac')

# Aggiungi i metadati al file M4A
audio = MP4(m4a_file_path)
audio['title'] = titolo
audio['artist'] = artista
audio['date'] = str(anno)

# Aggiungi la copertina dell'album
copertina_youtube = yt.thumbnail_url
copertina_filename = os.path.join(working_dir, f"{titolo}.jpg")
os.system(f'wget "{copertina_youtube}" -O "{copertina_filename}"')
with open(copertina_filename, 'rb') as cover_image:
    audio['covr'] = [APIC(3, 'image/jpeg', 3, '', cover_image.read())]

# Aggiungi i commenti
audio['comment'] = COMM(encoding=3, lang='eng', desc='Ciao a tutti', text='Ciao a tutti')

# Salva le modifiche
audio.save()

# Rimuovi il file video MP4 temporaneo
os.remove(video_filename)

print("Conversione completata con successo.")
