import threading
import os
import requests
import json
from flask import Flask, jsonify, request, Response
from dotenv import load_dotenv
from utils.load_and_split_docs import load_and_split_docs

# Loaders
from loaders.drive_loader import load_drive_folder_docs
from loaders.strong_csv_loader import load_strong_csv_docs
from loaders.youtube_video_loader import load_youtube_video_transcript
from loaders.youtube_channel_loader import load_youtube_channel_transcripts

# Splitters
from splitters.recursive_splitter import split_recursive_docs
from splitters.strong_csv_splitter import split_strong_csv_docs

# Extractors
from extractors.google_drive_extractor import google_drive_extractor
from extractors.strong_csv_extractor import strong_csv_extractor
from extractors.youtube_video_extractor import youtube_video_extractor

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Google Drive folder
@app.route('/api/drive/folder/<folder_id>', methods=['POST'])
def parse_drive_folder_docs(folder_id: str):
    """
    Parse documents from a Google Drive folder.
    
    Args:
        folder_id (str): The ID of the Google Drive folder.
        
    Returns:
        str: A message indicating the status of the operation.
    """
    # Extract meta and tags from the request
    data = request.get_json()
    meta = data.get("meta", [])
    tags = data.get("tags", {})
    
    # Load and split documents in a separate thread
    threading.Thread(target=load_and_split_docs, args=(
        folder_id,              #Arg: parent_id
        "GoogleDrive",          #Arg: document_type
        load_drive_folder_docs, #Arg: load_fn
        [folder_id],            #Arg: load_params
        split_recursive_docs,   #Arg: split_fn
        google_drive_extractor, #Arg: extract_fn
        meta,                   #Arg: meta
        tags                    #Arg: tags
    )).start()
    
    return jsonify({"message": "Documents are being processed."})

# Strong CSV file
@app.route('/api/strong/<csv_name>', methods=['POST'])
def parse_strong_docs(csv_name: str):
    """
    Parse documents from a Strong CSV file.
    
    Args:
        csv_name (str): The name of the Strong CSV file.
        
    Returns:
        str: A message indicating the status of the operation.
    """
    # Extract meta and tags from the request
    data = request.get_json()
    meta = data.get("meta", [])
    tags = data.get("tags", {})

    # Check if the CSV file exists
    csv = f"{csv_name}.csv"
    if not os.path.exists(f".csv/{csv}"):
        return jsonify({"error": f"File {csv_name}.csv not found."}), 404

    # Load and split documents in a separate thread
    threading.Thread(target=load_and_split_docs, args=(
        None,                       #Arg: parent_id
        "StrongCSV",                #Arg: document_type
        load_strong_csv_docs,       #Arg: load_fn
        [csv],                      #Arg: load_params
        split_strong_csv_docs,      #Arg: split_fn
        strong_csv_extractor,       #Arg: extract_fn
        meta,                       #Arg: meta
        tags                        #Arg: tags
    )).start()
    
    return jsonify({"message": "Documents are being processed."})


# YouTube Video
@app.route('/api/youtube/video/<video_id>', methods=['POST'])
def parse_youtube_video_transcript(video_id: str):
    # Extract meta and tags from the request
    data = request.get_json()
    meta = data.get("meta", [])
    tags = data.get("tags", {})
    
    # Load and split documents in a separate thread
    threading.Thread(target=load_and_split_docs, args=(
        None,                           #Arg: parent_id
        "YouTubeVideo",                 #Arg: document_type
        load_youtube_video_transcript,  #Arg: load_fn
        [video_id],                     #Arg: load_params
        split_recursive_docs,           #Arg: split_fn
        youtube_video_extractor,        #Arg: extract_fn
        meta,                           #Arg: meta
        tags                            #Arg: tags
    )).start()    
    
    return jsonify({"message": "Documents are being processed."})

# YouTube Channel
@app.route('/api/youtube/channel/<channel_id>', methods=['POST'])
def parse_youtube_video_channel(channel_id: str):
    # Extract meta and tags from the request
    data = request.get_json()
    meta = data.get("meta", [])
    tags = data.get("tags", {})


# # Root route
# @app.route('/')
# def hello_world():
#     return 'Hello, World!'

# # Example: Simple JSON API endpoint
# @app.route('/api/ping', methods=['GET'])
# def ping():
#     return jsonify({'message': 'pong'})

# Example: Echo back posted data
@app.route('/api/echo', methods=['POST'])
def echo():
    try:
        data = request.get_json()

        conversation_id = data.get('conversation_id', 'N/A')
        user_id = data.get('user_id', 'N/A')

        with (open(f".temp/log.log", "a")) as f:
            f.write(f"{request.headers}\n")
            f.write(f"Convo {conversation_id} for user {user_id}\n")

        query_data = data.get('query', [])
        if query_data:
            content = query_data[0].get('content', 'No content available')
        else:
            content = "No query data found."
        
        def generate_response():
            # Meta event
            yield f"event: meta\ndata: {json.dumps({'content_type': 'text/markdown', 'suggested_replies': False})}\n\n"

            # Text event: response to the user's query
            yield f"event: text\ndata: {json.dumps({'text': f'Hi there! You said: {content}'})}\n\n"

            # Optional suggested replies event (you can customize this based on your needs)
            yield f"event: suggested_reply\ndata: {json.dumps({'text': 'Can you tell me more?'})}\n\n"
            yield f"event: suggested_reply\ndata: {json.dumps({'text': 'What would you like to do next?'})}\n\n"

            # Done event (must be the last event)
            yield f"event: done\ndata: {json.dumps({})}\n\n"
        
        return Response(generate_response(), content_type='text/event-stream')

        return jsonify({
            'you_sent': data
        })
    except Exception as e:
        # If any error occurs, respond with an error event
        error_message = f"An error occurred: {str(e)}"

        with (open(f".temp/log.log", "a")) as f:
            # f.write(f"{request.headers}\n")
            f.write(f"{error_message}\n")

        return Response(
            f"event: error\ndata: {json.dumps({'text': error_message, 'allow_retry': True})}\n\n", 
            content_type='text/event-stream', 
            status=500
        )

# # Example: Dynamic URL parameter
# @app.route('/api/user/<username>', methods=['GET'])
# def get_user(username):
#     return jsonify({'user': username})

# # Example: Query parameters
# @app.route('/api/search', methods=['GET'])
# def search():
#     query = request.args.get('q')
#     return jsonify({'search_query': query})

# Main entry point
if __name__ == '__main__':
    app.run(debug=True)