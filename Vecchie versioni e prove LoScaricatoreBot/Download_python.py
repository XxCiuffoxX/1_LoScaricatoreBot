from pytube import YouTube

#link = input("Inserisci il link: ")
link = "https://youtu.be/EltoaN4U4Oc"

youtubeObject = YouTube(link)
#youtubeObject = youtubeObject.streams.get_highest_resolution()
youtubeObject = youtubeObject.streams.get_by_itag(22)

youtubeObject.download()