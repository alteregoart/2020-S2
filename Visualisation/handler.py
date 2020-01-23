import requests
import json

# Easiest implementation I can imagine

with open("credential.json", "r") as file:
    KEY = json.load(file)['KEY']

start_date = '2020-01-22'
end_date = '2020-01-23'

parameters = {
    'key': KEY,
    'restric_begin': start_date,
    'restric_end': end_date,
    'format':'json', # JSON or csv
}


response = requests.get("https://www.rescuetime.com/anapi/data.json", params=parameters)
print(response.json())
