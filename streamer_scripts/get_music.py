#!/usr/bin/env python
import json
import yt_dlp
import re

def main():
  parse_files('./data/urls.json', './data/clips.json')
  parse_files('./data/urls-ads.json', './data/clips-ads.json')
  

def parse_files(input, output):
  meta = []
  ydl_opts = {
    'quiet': True,
    'skip_download': True,  # We don't want to download the video
  }

  with open(input) as opts:
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

  with open(output, 'w') as f:
    json.dump(meta, f)

  

if __name__ == '__main__':
  main()