from flask import Flask, Response, render_template, url_for, request, jsonify
import requests
from openai import OpenAI
import json
import time

