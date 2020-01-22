import requests
import json

# Easiest implementation I can imagine

with open("credential.json", "r") as file:
    KEY = json.load(file)['KEY']

parameters = {}
parameters['key'] = KEY


response = requests.get("https://www.rescuetime.com/anapi/data.json", params=parameters)
print(response.json())
