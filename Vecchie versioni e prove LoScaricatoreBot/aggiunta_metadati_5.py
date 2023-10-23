from mutagen.mp4 import MP4, MP4Cover

# Percorso del file M4A di input
input_file = "output.m4a"

# Percorso del file M4A di output con i metadati e la copertina
output_file = "output.m4a"

# Carica il file M4A
audio = MP4(input_file)

# Aggiungi i metadati
audio["\xa9nam"] = "Titolo della traccia"  # Nome della traccia
audio["\xa9ART"] = "Artista"  # Artista
audio["\xa9alb"] = "Album"  # Album
audio["\xa9day"] = "Anno"  # Anno di pubblicazione
audio["\xa9cmt"] = "Commento"  # Commento

# Aggiungi l'immagine di copertina
cover_image_path = "HZoB_0htpgY.jpg"
with open(cover_image_path, "rb") as cover_image:
    cover_data = cover_image.read()
    audio["covr"] = [MP4Cover(cover_data, imageformat=MP4Cover.FORMAT_JPEG)]

# Salva il file M4A con i metadati
audio.save(output_file)
