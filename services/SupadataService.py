import requests
import os
from dotenv import load_dotenv

load_dotenv()

class SupadataService:
    def __init__(self):
        self.base_url = 'https://api.supadata.ai/v1'
        self.api_token = os.getenv('SUPADATA_API_KEY')
        self.headers = {
            'x-api-key': self.api_token
        } 

    def getTranscript(self, video_id):
        url = f"{self.base_url}/transcript?url=https://youtu.be/{video_id}"

        try:
            response = requests.get(url, headers=self.headers)            
            return response.json()

        except requests.RequestException as e:
            print(f"[GET] Error calling {url}: {e}")
            return None        
