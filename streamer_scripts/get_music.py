#!/usr/bin/env python
import json
import yt_dlp
import re

def main():
  ydl_opts = {
    'quiet': True,
    'skip_download': True,  # We don't want to download the video
  }

  urls = []
  meta = []

  with open('./data/urls.json') as opts:
    urls = json.load(opts)
    
  for i in range(len(urls)):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      video_meta = ydl.extract_info(urls[i], download=False)

    pattern = r"(?<=v=).*"
    vid_id = re.search(pattern, urls[i]).group(0) 
    
    new_obj = {
      "id": vid_id,
      "video": urls[i],
      "title": video_meta['title'],
      "duration": video_meta['duration'],
      "tags": video_meta['tags'],
    }

    meta.append(new_obj)

  with open('./data/clips.json', 'w') as f:
    json.dump(meta, f)

  

if __name__ == '__main__':
  main()