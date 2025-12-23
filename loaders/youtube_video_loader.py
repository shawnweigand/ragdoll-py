import requests
import re
import json
import xml.etree.ElementTree as ET
import html
from langchain_core.documents import Document

def load_youtube_video_transcript(video_id: str):
    """
    Load transcripts from a Youtube Video.
    
    Args:
        video_id (str): The ID of the youtube video.
        
    Returns:
        transcript (Document): A single video transcript.
    """

    url = f"https://www.youtube.com/watch?v={video_id}"

    metadata = {
        "source": url,
        "video_id": video_id,
    }

    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch video page, status code: {response.status_code}")

    html_content = response.text

    match = re.search(r'"captionTracks":(\[.*?\])', html_content)
    if not match:
        raise Exception("Could not find captionTracks in HTML")

    caption_tracks_json = match.group(1)
    caption_tracks = json.loads(caption_tracks_json)

    results = []
    for track in caption_tracks:
        language = track.get("languageCode", "unknown")
        name = track.get("name", {}).get("simpleText", "")
        url = track.get("baseUrl")
        results.append({
            "language": language,
            "name": name,
            "baseUrl": url
        })

    prinnt(results)
    base_url = results[0]['baseUrl']
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
    }

    response = requests.get(base_url, headers)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch transcript from {base_url}")

    try:
        xml_text = response.content.decode('utf-8', errors='ignore')
        root = ET.fromstring(xml_text)
        transcript = []
        full_transcript = ''
        for elem in root.findall('text'):
            start = float(elem.attrib['start'])
            dur = float(elem.attrib.get('dur', 0))
            text = html.unescape(elem.text or "")
            transcript.append({
                "start": start,
                "dur": dur,
                "text": text.replace('\n', ' ')
            })
            full_transcript += text.replace('\n', ' ') + ' '
        return [Document(
            page_content = full_transcript,
            metadata = metadata
        )]
    except ET.ParseError as e:
        print("Failed to parse XML:", e)
        print(response.text[:500])
        print ("Skipping video:", video_id)
        return None
        # raise Exception(f"Failed to parse XML: {e}")