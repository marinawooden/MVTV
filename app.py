from flask import Flask, Response, stream_with_context, render_template, jsonify
from flask_socketio import SocketIO, emit
import time
import subprocess

app = Flask(__name__)
socketio = SocketIO(app)

video_dict = [
    {
        "path": "streamer_scripts/vids/jQyazt4RDTM-resized.mp4",
        "info": {
            "title": "Head Over Heels",
            "year": 1984,
            "label": "Columbia Records",
            "artist": "The Go-Gos",
            "youtube_url": "https://www.youtube.com/watch?v=jQyazt4RDTM"
        }
    },
    {
        "path": "streamer_scripts/vids/jMsOH16tkaY-resized.mp4",
        "info": {
          "title": "Billy Joel Live",
          "year": 1985,
          "label": "Billy Joel",
          "artist": "Billy Joel",
          "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
    },
    {
        "path": "streamer_scripts/vids/J2jRuh1bAxw-resized.mp4",
        "info": {
          "title": "Radioshack Color Computer",
          "year": 1985,
          "label": "Radioshack",
          "artist": "Radioshack",
          "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
    },
    {
        "path": "streamer_scripts/vids/4yibaObVKgI-resized.mp4",
        "info": {
          "title": "Fig Newtons",
          "year": 1985,
          "label": "Fig Newtons",
          "artist": "Fig Newtons",
          "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
    },
    {
      "path": "streamer_scripts/vids/5T2aZrOgDak-resized.mp4",
      "info": {
        "title": "Uncertain Smile (Live)",
        "year": 1983,
        "label": "4AD",
        "artist": "The the",
        "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
      }
    }
]

current_video_index = 0
video_start_time = time.time()

def generate_video_stream(start_time, video_path):
    ffmpeg_command = [
        'ffmpeg',
        '-ss', str(start_time),  # start time
        '-i', video_path,
        '-f', 'mp4',
        '-movflags', 'frag_keyframe+empty_moov',
        '-c:v', 'copy',
        '-c:a', 'copy',
        '-reset_timestamps', '1',
        '-f', 'mp4',
        'pipe:1'
    ]
    process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process.stdout

@app.route("/")
def home():
    return render_template('index.html') 

@app.route('/video_feed')
def video_feed():
    global video_start_time, current_video_index
    current_time = time.time() - video_start_time
    video_path = video_dict[current_video_index]["path"]
    return Response(stream_with_context(generate_video_stream(current_time, video_path)), mimetype='video/mp4')

@socketio.on('connect')
def handle_connect():
    global current_video_index
    emit('video_info', video_dict[current_video_index]['info'])

@socketio.on('video_ended')
def handle_video_ended():
    global current_video_index, video_start_time
    current_video_index = (current_video_index + 1) % len(video_dict)
    video_start_time = time.time()
    emit('video_info', video_dict[current_video_index]['info'], broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080, debug=True)
