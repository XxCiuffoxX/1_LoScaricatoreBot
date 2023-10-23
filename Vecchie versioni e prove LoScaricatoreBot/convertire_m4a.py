from moviepy.editor import VideoFileClip

# Percorso del file MP4 di input
input_file = "Questo me ne sbatto il cao Lello.mp4"

# Percorso del file M4A di output
output_file = "output.m4a"

# Carica il video
video_clip = VideoFileClip(input_file)

# Estrai l'audio dal video
audio_clip = video_clip.audio

# Salva l'audio come file M4A
audio_clip.write_audiofile(output_file, codec="aac")
