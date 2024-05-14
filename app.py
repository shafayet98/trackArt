from flask import Flask, Response, render_template, url_for, request, jsonify
import requests
from openai import OpenAI
import json
import time

app = Flask(__name__)
API_KEY = open("API_KEY", 'r').read()


client = OpenAI(api_key=API_KEY)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', data="Hello World")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)