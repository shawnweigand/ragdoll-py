from services.YoutubeService import YoutubeService
from loaders.youtube_video_loader import load_youtube_video_transcript
from typing import List, Optional

def load_youtube_channel_transcripts(channel_id: str, video_ids: Optional[List[str]] = None):
    """
    Load transcripts from a Youtube Channel's Videos.
    
    Args:
        channel_id (str): The ID of the youtube channel.
        
    Returns:
        transcripts (Document[]): A list of video transcript documents.
    """

    yt = YoutubeService()

    videos = yt.getChannelVideos('UCLOzkJ9W9fntCGyYfUwMPew')

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

    print(vids)

    transcripts = []

    for vid in vids:
        doc = load_youtube_video_transcript(vid["video_id"])
        if doc:
            doc[0].metadata = doc[0].metadata | vid
            transcripts.append(doc[0])

    print(transcripts)

    return transcripts