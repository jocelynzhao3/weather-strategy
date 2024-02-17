print("testing visual crossing")

import requests
import json
import time


def fetch_webpage_content(url):
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        return response.json()  # Assume the content is in JSON format
    else:
        print(f"Failed to fetch content. Status code: {response.status_code}")
        return None

def save_json_to_file(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)


lat = 42.3601  #Boston
lon = -71.0589
year = 2024
month = 1
day = 27
hour = 11
API_KEY = "BRZ9RR2P5L3VK38UE33UTX5WS"
# link = "https://api.weather.gov/points/" + str(lat) + "," + str(lon)
#example: link = "https://api.weather.gov/points/42.36,-71.06"
base = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
location = str(lat) + "," + str(lon)
date = str(year) + "-" + str(month) + "-" + str(day) + "T" + str(hour) + ":00:00"
key = "?key=" + API_KEY
# include=current
request = "&elements=cloudcover"
link = base + location + "/" + date + key + request

#method will query for the entire 24 hours, but costs 1 query

a = time.time()
json_content = fetch_webpage_content(link)

if json_content:
    filename = 'visual_crossing.json'
    save_json_to_file(json_content, filename)
    # print(f"Webpage content saved to {filename}")
b = time.time()

# print(b - a) one query take (0.1, 0.2) sec

#Step 2: Read just-created json file to get link to sky cover data

# Assuming you have a JSON file named 'example.json' in the same directory as your Python script
file_path = 'visual_crossing.json'

# Open the file in read mode
with open(file_path, 'r') as json_file:
    # Load the JSON data into a dictionary
    data_dict = json.load(json_file)

# print(data_dict)  #likely too expensive if we want 20k+ points
