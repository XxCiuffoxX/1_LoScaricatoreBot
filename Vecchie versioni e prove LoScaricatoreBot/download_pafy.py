import pafy

# Ottenere l'oggetto video da YouTube
url = "https://youtu.be/EltoaN4U4Oc"
video = pafy.new(url)

# Ottenere la migliore qualità disponibile
best = video.getbest()

# Scaricare il video
best.download()
