"""Quick test to see buffer status right now"""
import requests

response = requests.get('http://localhost:8000/video/buffer/status')
print(response.json())
