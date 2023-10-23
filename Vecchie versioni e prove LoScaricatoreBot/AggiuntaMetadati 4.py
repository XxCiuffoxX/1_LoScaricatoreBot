# Aggiunta metadati 4
import eyed3
from eyed3.id3.frames import ImageFrame

mp3_file_name = "Luche - Estate dimmerda 2.mp3"

audiofile = eyed3.load(mp3_file_name)

audiofile.tag.title = mp3_file_name.replace(".mp3", "")
audiofile.tag.artist = "Luchè"
audiofile.tag.year = "2000"
audiofile.tag.comments.set(str("@LoScaricatoreBot"))

# Legge il contenuto dell'immagine JPG come bytes
#with open("HZoB_0htpgY.jpg", "rb") as image_file:
#    image_data = image_file.read()

image_data = open("HZoB_0htpgY.jpg","rb").read()

audiofile.tag.images.set(3, image_data, 'image/jpeg', u"Description")

# Salva le modifiche
audiofile.tag.save()   