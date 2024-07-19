# from moviepy.editor import VideoFileClip, ColorClip, concatenate_videoclips
# import moviepy.video.fx.all as vfx
import random
import json
import os
import yt_dlp
import subprocess
import time
from datetime import datetime
import threading

class Streamer():
    def __init__(self):
      self.videos = [] # options for videos
      self.ads = [] # options for ads

      self.q = [] # queue to play from (elem at 0th index is current)
      self.history = [] # history of already played videos
      self.last_start = time.time() # start time for calculating how far in to go
      
      with open('streamer_scripts/data/clips.json') as opts:
        data = json.load(opts)
        self.videos = data

      with open('streamer_scripts/data/clips-ads.json') as opts:
        data = json.load(opts)
        self.ads = data
      
      # init queue
      self.queue_video(save=False)
      self.queue_video(save=False)

      self.play()

    def play(self):
      """
      Called when a new video starts, keeps track of queue state
      """
      print("PLAYING VIDEO! QUEUE IS THIS:")
      print(", ".join([vid["title"] for vid in self.q]))

      if len(self.q) > 0:
        # get playing video
        curr_vid = self.q[0]
        # pop off current video from the queue
        self.q.pop(0)
        # add to history
        # self.history.append(curr_vid)
        # set new start time
        self.last_start = time.time()

        print(f"SETTING TIMER TO QUEUE VIDEO IN {curr_vid['duration']}")
        # set timer for when current video starts
        timer = threading.Timer(curr_vid['duration'] - 1, self.play)
        timer.start()

        # queue another video
        self.queue_video(save=False)
      else:
        print("NO VIDEOS IN QUEUE")
        self.q.append({"id": "1O0yazhqaxs", "video": "https://www.youtube.com/watch?v=1O0yazhqaxs", "title": "3 second video", "artist": "3 second video", "label": "Youtube", "year": 2024, "video_title": "3 Second Video", "duration": 3, "tags": ["3 second video", "three second video"]})

    def stream(self):
      isAd = True;
      while (True):
        start_time = time.time()
        self.queue_segment(isAd=isAd)
        print(f"Generated segment in {time.time() - start_time} seconds")
        isAd = not isAd
        
    
    def queue_video(self, save = True, isAd = False):
      print("ADDING TO QUEUE")
      # select new vid
      new_vid = self.__selectnewvid(set(), isAd=isAd)

      if not new_vid:
        return None

      if not os.path.isfile(f"streamer_scripts/vids/{new_vid['id']}-resized.mp4"):
        # download video
        self.__download_video(new_vid['video'], f"streamer_scripts/vids/{new_vid['id']}")

        # resize video
        self.__process_vid(new_vid['id'])
      else:
        print("ALREADY PROCESSED - SKIPPING!")

      # add new vid to queue
      self.q.append(new_vid)

      if save:
        self.__save_queue(isAd)

      return new_vid

    # TODO: DEPRECATED - remove
    def queue_segment(self, save = True, isAd = False):
      duration = 0 # accumulate duration
      max_duration = 300 if isAd else 1800 # current max: 30 minutes music, 5 minutes ads

      while duration < max_duration: 
        newvid = self.queue_video(save=False, isAd=isAd)

        if not newvid:
          break
          
        duration += newvid['duration']
        
      if save:
        self.__save_queue(isAd)

    def generate_video_stream(self):
      start_time = time.time() - self.last_start

      ffmpeg_command = [
          'ffmpeg',
          '-ss', str(start_time),  # start time
          '-i', "streamer_scripts/vids/" + self.q[0]['id'] + "-resized.mp4",
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
  
    def current_info(self):
      return self.q[0]
    
    def __download_video(self, url, output_path):
      ydl_opts = {
        'outtmpl': f'{output_path}',  # Save the video with this name
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4'  # Get the best quality video and audio
      }

      with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    def __save_queue(self, isAd):
      # TODO: combine this with lower line
      vidlist = [f"../vids/{vid['id']}-resized.mp4" for vid in self.q]

      # save vidlist to file for ffmpeg
      with open("streamer_scripts/data/queue.txt", "w") as txt_file:
        for vid in vidlist:
            txt_file.write(f"file {vid}\n")

      base_filename = f"../output/{datetime.today().strftime('%Y%m%d-%H%M%S')}"
      filename = f"{base_filename}{'ADS' if isAd else ''}.mp4"

      # Run the ffmpeg command with arguments as a list
      subprocess.run([
          "ffmpeg",
          "-y",  # Overwrite output file if it exists
          "-f", "concat",
          "-safe", "0",
          "-i", "streamer_scripts/data/queue.txt",
          "-c", "copy",
          filename
      ], check=True)

      self.q = []

    def __selectnewvid(self, chosen_ids, isAd):
      if len(chosen_ids) == len(self.videos):
        return None

      options = self.ads if isAd else self.videos 
      vid = random.choice(options) # get random option
      q = [v['id'] for v in self.q + self.history]

      if vid['id'] in q:
        chosen_ids.add(vid['id'])
        return self.__selectnewvid(chosen_ids, isAd=isAd)
      
      return vid

    def __process_vid(self, vidpath):
      target_height = 1080
      target_width = 1920

      input_path = f"streamer_scripts/vids/{vidpath}.mp4"
      output_path = f"streamer_scripts/vids/{vidpath}-resized.mp4"

      scale_filter = f'scale={target_width}:{target_height}:force_original_aspect_ratio=decrease'
      pad_filter = f'pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2'
      frame_filter = f'fps=30'
      filter_complex = f'{scale_filter},{pad_filter},{frame_filter}'

      command = [
          'ffmpeg',
          '-i', input_path,  # Input file
          '-vf', filter_complex,  # Video filter for scaling and padding
          # '-r', "29.97",  # Set the desired framerate
          # '-speed', '18',
          '-preset', 'ultrafast',
          output_path  # Output file
      ]

      subprocess.run(command, check=True)
      # remove the original file
      os.remove(input_path)
