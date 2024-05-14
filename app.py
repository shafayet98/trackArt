from flask import Flask, Response, render_template, url_for, request, jsonify
import requests
from openai import OpenAI
import json
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
API_KEY = open("API_KEY", 'r').read()


client = OpenAI(api_key=API_KEY)

@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == "POST":
        data = request.json
        
        lyrics = data['lyrics']
        suggestion = data['suggestion']
        response = client.images.generate(
            model="dall-e-3",
            prompt= "You are an album cover artist." + lyrics + "Create an album cover based on the lyrics given to you. Analyze the meaning of it and generate the cover." 
            + "Here is some sugguestion on how the cover should be: " + suggestion + " Follow these suggestion and let your imagination flow.",
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url


        # find the artist name if exist
        query = [{
                "role": "user",
                "content": 
                
                """You're a search engine to find songs. What is the name of the song and the artist of the given lyrics? Return me the result in JSON format. 
                   The return format should be like this:

                   {
                    "artist_name" : Name of the arist,
                    "track_name" : Name of the song
                   } 
                
                Here is the lyrics for you:
                """ + lyrics
            }]

            # Make a request to GPT API with stream=True
        chat_completion_response = client.chat.completions.create(
                messages=query,
                model="gpt-3.5-turbo",
                stream=False
        )
        print(chat_completion_response.choices[0])

        
        return jsonify({'message': 'Form received!', 'result': image_url})

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8081)