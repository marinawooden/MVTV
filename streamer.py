from moviepy.editor import VideoFileClip, ColorClip, concatenate_videoclips
import moviepy.video.fx.all as vfx
import random
import time
import json
import os

class Streamer():
    def __init__(self):
      self.videos = [
        {
          "id": 1,
          "video": "./vids/1",
          "title": "3 second video",
          "duration": 3,
          "offset": 0
        },
        {
          "id": 2,
          "video": "./vids/2",
          "title": "Green background for 3 seconds",
          "duration": 3,
          "offset": 0
        }
      ]

      self.history = []
      with open('./data/options.json') as opts:
        data = json.load(opts)
        self.options = data
      
      for vid in self.videos:
        print(vid)
        self.__resizevid(vid['video'])

      final_clip = concatenate_videoclips([VideoFileClip(f"{vid['video']}-tmp.mp4") for vid in self.videos], method='compose')
      final_clip.write_videofile("./output/stream.mp4")

    # def stream(self):
    #   final_clip = concatenate_videoclips([
    #     VideoFileClip("./output/stream.mp4"),
    #     VideoFileClip("./vids/1-tmp.mp4")
    #   ], method='compose')

    #   final_clip.write_videofile("./output/stream-copy.mp4")
    #   os.replace("./output/stream-copy.mp4", "./output/stream.mp4")


    def stream(self):
      print("START****************************************")
      count_vids_played = 0
      time.sleep(self.videos[0]['duration'])

      while(True):
        count_vids_played += 1
        print(f"Video {count_vids_played} played, with title {self.videos[0]['title']}")

        # store watched video in history
        curr_vid = self.videos[0]
        self.history.append(curr_vid)

        arrhis = ", ".join([vid['title'] for vid in self.history])
        print(f"Watch history is this: {arrhis}")

        # select new video that isn't in history
        newvid = self.__selectnewvid(set())

        if not newvid:
          print("Error: ran out of videos to choose from!")
          for vid in self.videos:
            self.__resizevid(vid['video'])
          
          # finish up
          final_clip = concatenate_videoclips([
            VideoFileClip("./output/stream.mp4")
          ] +
          [VideoFileClip(vid['video'] + "-tmp.mp4") for vid in self.videos], method='compose')
          watchis = [vid['title'] for vid in self.history]
          print(f"WHOLE WATCH HISTORY IS {watchis}")
          
          final_clip.write_videofile("./output/stream-copy.mp4")
          os.replace("./output/stream-copy.mp4", "./output/stream.mp4")
          break;
        
        self.__resizevid(newvid['video'])
        
        print(f"Selected new video: {newvid['title']}")

        # add that video to the current stream
        self.videos.append(newvid)
        final_clip = concatenate_videoclips([
          VideoFileClip("./output/stream.mp4"),
          VideoFileClip(f"{newvid['video']}-tmp.mp4")
        ], method='compose')

        final_clip.write_videofile("./output/stream-copy.mp4")
        os.replace("./output/stream-copy.mp4", "./output/stream.mp4")

        self.videos.pop(0)
        
        # TODO: trim history if the total duration is over 30 (minutes)

        print(f"Playing video {self.videos[0]['title']} with duration {self.videos[0]['duration']}")
        print("OVER*********************************")
        # set timeout to do the same thing once current video is over
        time.sleep(self.videos[0]['duration'])

    def __selectnewvid(self, chosen_ids):
      if len(chosen_ids) == len(self.options):
        return None

      vid = random.choice(self.options) # get random option
      q = [v['id'] for v in self.history + self.videos]

      if vid['id'] in q:
        chosen_ids.add(vid['id'])
        return self.__selectnewvid(chosen_ids)
      
      return vid


    def __resizevid(self, vidpath):
      clip = VideoFileClip(vidpath + ".mp4")
      (w, h) = clip.size

      clip_resized = clip.resize(height=720).crop(width=960, height=720, x_center=w/2, y_center=h/2)
      clip_resized.write_videofile(f"{vidpath}-tmp.mp4")


stream = Streamer()
stream.stream()
