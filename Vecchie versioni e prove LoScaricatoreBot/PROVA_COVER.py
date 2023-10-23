import ffmpeg

input_image = ffmpeg.input('GOPR0016.jpg')
input_audio = ffmpeg.input('Dennis Lloyd - Leftovers  A COLORS SHOW.mp3')

(
    ffmpeg
    .concat(input_image, input_audio, v=1, a=1)
    .output('audio1.mp3').run()
)
