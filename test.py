from loaders.youtube_channel_loader import load_youtube_channel_transcripts
from splitters.recursive_splitter import split_recursive_docs
from extractors.youtube_video_extractor import youtube_video_extractor
from utils.load_and_split_docs import load_and_split_docs

# channel_id = "UCI5d0aR9R0AWgTRUkQ-K3UA"
channel_id = "UCLOzkJ9W9fntCGyYfUwMPew"

video_ids = []

# videos = load_youtube_channel_transcripts(channel_id)

meta = [
    "source",
    "video_id",
    "title",
    "date",
    "channel_id"
]
tags = {}

load_and_split_docs(
        channel_id,                       #Arg: parent_id
        "YoutubeVideo",                   #Arg: document_type
        load_youtube_channel_transcripts, #Arg: load_fn
        [channel_id, video_ids],          #Arg: load_params
        split_recursive_docs,             #Arg: split_fn
        youtube_video_extractor,          #Arg: extract_fn
        meta,                             #Arg: meta
        tags                              #Arg: tags
)

# print(videos)