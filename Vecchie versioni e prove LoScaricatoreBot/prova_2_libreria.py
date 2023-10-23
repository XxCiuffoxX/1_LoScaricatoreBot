import requests
from bs4 import BeautifulSoup

# URL del sito web contenente il video da scaricare
url = "https://youtu.be/kLfkhY3IxpU"

# Effettua la richiesta HTTP al sito web
response = requests.get(url)

# Analizza l'HTML della pagina con Beautiful Soup
soup = BeautifulSoup(response.content, "html.parser")

# Trova il tag del video
video_tag = soup.find("video")

# Trova l'URL del video nel tag
video_url = video_tag["src"]

# Scarica il contenuto del video
video_content = requests.get(video_url).content

# Salva il contenuto del video in un file locale
with open("video.mp4", "wb") as f:
    f.write(video_content)