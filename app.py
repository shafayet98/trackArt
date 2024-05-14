from flask import Flask, Response, render_template, url_for, request, jsonify
import requests
from openai import OpenAI
import json
import time
import base64
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

API_KEY = open("API_KEY", 'r').read()

# spotify api
# Your Spotify API credentials
client_id = open("SPOT_CID", 'r').read()
client_secret = open("SPOT_CS", 'r').read()


client = OpenAI(api_key=API_KEY)


# Step 1: Get Access Token
def get_access_token(client_id, client_secret):
    token_url = 'https://accounts.spotify.com/api/token'
    auth_header = base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode('ascii')
    token_data = {
        'grant_type': 'client_credentials'
    }
    token_headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    response = requests.post(token_url, data=token_data, headers=token_headers)
    token_response_data = response.json()
    return token_response_data['access_token']


def search_track(track_name, artist_name, access_token):
    search_url = 'https://api.spotify.com/v1/search'
    search_headers = {
        'Authorization': f'Bearer {access_token}',
    }
    search_params = {
        'q': f'track:{track_name} artist:{artist_name}',
        'type': 'track',
        'limit': 1,
    }
    response = requests.get(search_url, headers=search_headers, params=search_params)
    search_results = response.json()
    
    if search_results['tracks']['items']:
        track = search_results['tracks']['items'][0]
        track_name = track['name']
        track_id = track['id']
        artists = ', '.join(artist['name'] for artist in track['artists'])
        preview_url = track['preview_url']
        return track_name, artists, track_id, 
    else:
        return None, None, None


def get_preview_url(access_token, trackID):
    track_url = f'https://api.spotify.com/v1/tracks/{trackID}'
    track_headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(track_url, headers=track_headers)
    track_data = response.json()

    if 'error' not in track_data:
        track_name = track_data['name']
        artists = ', '.join(artist['name'] for artist in track_data['artists'])
        preview_url = track_data['preview_url']
        return track_name, artists, preview_url
    else:
        return None, None, None


@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == "POST":
        data = request.json
        
        lyrics = data['lyrics']
        suggestion = data['suggestion']
        artistName = data['artistName']
        trackName = data['trackName']

        # spotify search
        print(artistName, trackName)
        access_token = get_access_token(client_id, client_secret)
        print('Access token:', access_token)
        track_name, artists, track_id = search_track(trackName, artistName, access_token)
        track_name, artists, preview_url = get_preview_url(access_token, track_id)
        print(preview_url)
        
        # gpt reuqest
        response = client.images.generate(
            model="dall-e-3",
            prompt= "You are an album cover artist." + lyrics + "Create an album cover based on the lyrics given to you. Analyze the meaning of it and generate the cover." 
            + "Here is some sugguestion on how the cover should be: " + suggestion + " .Follow these suggestion and let your imagination flow.",
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url
        
        
        return jsonify({'message': 'Form received!', 'result': image_url, 'previewURL': preview_url})

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8081)