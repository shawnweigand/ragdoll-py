import os
import time
from dotenv import load_dotenv
from services.YoutubeService import YoutubeService
from services.SupadataService import SupadataService
from loaders.youtube_video_loader import load_youtube_video_transcript
load_dotenv()

yt = YoutubeService()
sd = SupadataService()

# channel_id = "UCI5d0aR9R0AWgTRUkQ-K3UA"
channel_id = "UCLOzkJ9W9fntCGyYfUwMPew"

video_ids = []

videos = yt.getChannelVideos(channel_id)

vids = [
    {
        "video_id": video["id"]["videoId"],
        "title": video["snippet"]["title"],
        "date": video["snippet"]["publishTime"],
        "channel_id": channel_id
    }
    for video in videos[:10]
    # if video_ids is None or video["id"]["videoId"] in video_ids
]

print(len(vids))

transcripts = []
for vid in vids:
    print("Loading transcript for video ID:", vid["video_id"])
    transcript = sd.getTranscript(vid["video_id"])
    transcripts.append(transcript)

print(transcripts)