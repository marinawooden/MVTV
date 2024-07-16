# from moviepy.editor import VideoFileClip, ColorClip, concatenate_videoclips
# import moviepy.video.fx.all as vfx
import random
import json
import os
import yt_dlp
import subprocess
import time

class Streamer():
    def __init__(self):
      self.videos = []
      self.history = []
      
      with open('./data/clips.json') as opts:
        data = json.load(opts)
        self.options = data
    
    def queue_video(self, save = True):
      # select new vid
      new_vid = self.__selectnewvid(set())
        
      print(new_vid)

      if not new_vid:
        return None
      
      # download video
      self.__download_video(new_vid['video'], f"./vids/{new_vid['id']}")

      if not os.path.isfile(f"./vids/{new_vid['id']}-resized.mp4"):
        # resize video
        self.__process_vid(new_vid['id'])
      else:
        print("ALREADY PROCESSED - SKIPPING!")

      # add new vid to queue
      self.videos.append(new_vid)

      if save:
        self.__save_queue()

      return new_vid

    def queue_segment(self, save = True):
      duration = 0 # accumulate duration

      while duration < 1800: # current max: 30 minutes
        newvid = self.queue_video(save=False)

        if not newvid:
          break
          
        duration += newvid['duration']
        
      if save:
        self.__save_queue()
    
    def __download_video(self, url, output_path):
      ydl_opts = {
        'outtmpl': f'{output_path}',  # Save the video with this name
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4'  # Get the best quality video and audio
      }

      with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    def __save_queue(self):
      vidlist = [f"../vids/{vid['id']}-resized.mp4" for vid in self.videos]

      # save vidlist to file for ffmpeg
      with open("./data/queue.txt", "w") as txt_file:
        for vid in vidlist:
            txt_file.write(f"file {vid}\n")

      # subprocess.run("ffmpeg -y -f concat -safe 0 -i ./data/queue.txt -c copy ./output/stream.mp4")
      # Run the ffmpeg command with arguments as a list
      subprocess.run([
          "ffmpeg",
          "-y",  # Overwrite output file if it exists
          "-f", "concat",
          "-safe", "0",
          "-i", "./data/queue.txt",
          "-c", "copy",
          "./output/stream.mp4"
      ], check=True)

      self.history = self.videos
      self.videos = []

    def __selectnewvid(self, chosen_ids):
      if len(chosen_ids) == len(self.options):
        return None

      vid = random.choice(self.options) # get random option
      q = [v['id'] for v in self.videos]

      if vid['id'] in q:
        chosen_ids.add(vid['id'])
        return self.__selectnewvid(chosen_ids)
      
      return vid

    def __process_vid(self, vidpath):
      target_height = 1080
      target_width = 1920

      input_path = f"./vids/{vidpath}.mp4"
      output_path = f"./vids/{vidpath}-resized.mp4"

      scale_filter = f'scale={target_width}:{target_height}:force_original_aspect_ratio=decrease'
      pad_filter = f'pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2'
      filter_complex = f'{scale_filter},{pad_filter}'

      command = [
          'ffmpeg',
          '-i', input_path,  # Input file
          '-vf', filter_complex,  # Video filter for scaling and padding
          '-r', "29.97",  # Set the desired framerate
          '-speed', '18',
          output_path  # Output file
      ]

      subprocess.run(command, check=True)


stream = Streamer()

start_time = time.time()
stream.queue_segment()

# vid = {'id': 'bDMCwSP5nf0', 'video': 'https://www.youtube.com/watch?v=bDMCwSP5nf0', 'title': 'Pet Shop Boys - Always on my mind (Official Video) [4k Upgrade]', 'duration': 313, 'tags': []}
# vid = {'id': 'VAtGOESO7W8', 'video': 'https://www.youtube.com/watch?v=VAtGOESO7W8', 'title': 'Tears For Fears - Sowing The Seeds Of Love', 'duration': 332, 'tags': ['tears for fears seeds of love live', 'tears for fears seeds of love album', 'tears for fears seeds of love remastered', 'tears for fears seeds of love full album', 'tears for fears seeds of love lyrics', 'tears for fears seeds of love hq', 'TEARS FOR FEARS', 'TEARS FOR FEARS SOWING THE SEEDS OF LOVE', 'SOWING THE SEEDS OF LOVE', 'SOWING THE SEEDS OF LOVE TEARS FOR FEARS', 'SOWING THE SEEDS OF LOVE official music video', 'SOWING THE SEEDS OF LOVE remastered video']}
# stream.queue_video(vid=vid)
print(f"{time.time() - start_time} seconds")


