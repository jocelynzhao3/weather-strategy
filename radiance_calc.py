import requests   #set base to conda 3.11.5 to install package
import json
import os
import numpy as np
from numpy import array
from solarpy import solar_panel
from datetime import datetime
import matplotlib
import time

def find_radiance(lat, lon, elev, year, month, day, hour, minute=0):
    '''
    Param:
    lat - latitude (-90 to +90 degrees)
    lon - longitude (-179 to 180 degrees)
    elev - altitude (0 to 24k meters)
    int type: year, month, day, hour(local time, 24 hour format), minute

    Return:
    Power of panel - units of W
    '''
    clear_radiance = clear_sky_radiance(lat, lon, elev, year, month, day, hour, minute)

    # Step 1: Read first json file for link (used in step 2)
    #for boston, will have to change with car

    link = "https://api.weather.gov/points/" + str(lat) + "," + str(lon)
    #example: link = "https://api.weather.gov/points/42.36,-71.06"

    json_content = fetch_webpage_content(link)

    if json_content:
        filename = 'weather_points.json'
        save_json_to_file(json_content, filename)
        # print(f"Webpage content saved to {filename}")

    #Step 2: Read just-created json file to get link to sky cover data

    # Assuming you have a JSON file named 'example.json' in the same directory as your Python script
    file_path = 'weather_points.json'

    # Open the file in read mode
    with open(file_path, 'r') as json_file:
        # Load the JSON data into a dictionary
        data_dict = json.load(json_file)

    new_link = data_dict['properties']["forecastGridData"] # link directs you to json with sky cover data

    sky_cover_content = fetch_webpage_content(new_link)

    if sky_cover_content:
        filename = 'sky_cover.json'
        save_json_to_file(sky_cover_content, filename)
        # print(f"Webpage content saved to {filename}")

    #Step 3: Read final json file

    # Assuming you have a JSON file named 'example.json' in the same directory as your Python script
    new_file_path = 'sky_cover.json'

    # Open the file in read mode
    with open(new_file_path, 'r') as json_file:
        # Load the JSON data into a dictionary
        sky_cover_dict = json.load(json_file)

    sky_cover_time_list = sky_cover_dict["properties"]["skyCover"]["values"]
    bounds_list = sky_cover_dict["geometry"]["coordinates"][0]
    print(bounds_list)

    sky_cover_time_dict = {}

    for i in range(len(sky_cover_time_list)):    # may not need to generate entire dictionary to improve efficiency
        key = sky_cover_dict["properties"]["skyCover"]["values"][i]["validTime"][:13]
        value = int(sky_cover_dict["properties"]["skyCover"]["values"][i]["value"])/100  #cloud cover as decimal 0.0-1.0
        sky_cover_time_dict[key] = value

    year = str(year)
    month = str(month)
    day = str(day)
    hour = str(hour)

    # Specify the file path

    input_key = year.zfill(2) + "-" + month.zfill(2) + "-" + day.zfill(2) + "T" + hour.zfill(2)
    try:
        cloud_cover = sky_cover_time_dict[input_key]

        # Delete the file after reading from it - optional functionality
        # if os.path.exists(new_file_path):
        #     os.remove(new_file_path)
        #     print(f'{new_file_path} deleted successfully')
        # else:
        #     print(f'{new_file_path} does not exist')

        return adj_radiance(clear_radiance, cloud_cover)
    except KeyError:
        print("This time is unavaliable")    #may be asked to interpolate here, returns None for now


def clear_sky_radiance(lat, lon, elev, year, month, day, hour, minute):
    '''
    Param:
    lat - latitude (-90 to +90 degrees),
    lon - longitude (-179 to 180 degrees)
    elev - altitude (0 to 24k meters)
    year, month, day, hour(24 hour format), minute

    Return:
    Power of panel - units of W/m^2*m^2*units of efficiency?


    '''
    panel = solar_panel(3.986327, 0.24)  # surface (m^2), efficiency, numbers based off of Nimbus
    # panel = solar_panel(3.986327, 0.203)  # surface (m^2), efficiency changed based on temp - have other members experienced this?

    panel.set_orientation(array([0, 0, -1]))  # upwards
    panel.set_position(lat, lon, elev)
    panel.set_datetime(datetime(year, month, day, hour, minute))
    return panel.power()

# x = clear_sky_radiance(40.832, -98.338, 78.56, 2022, 7, 10, 15, 0)
# print(x)

def adj_radiance(radiance, cloud_cover):
    '''
    Input:
    radiance: original solar radiance on a clear day in W/m^2
    cloud cover: decimal cloud cover range from 0.0-1.0, from weather api

    Return:
    float, adjusted radiance based on cloud cover, in W/m^2
    '''

    #check cloud cover value:
    if cloud_cover >= 0.0 and cloud_cover <= 1.0:
        return radiance * (1 - 0.75*(cloud_cover)**3.4)
    else:
        print("Please enter valid cloud cover value")

# print(adj_radiance(x, 0))

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

a = time.time()
x = (find_radiance(42.36, -71.06, 5.8, 2024, 2, 2, 14, minute=0))  #date should be within next 7 days - some times are unavaliable or give errors
# keep visual crossing pulls as a backup????
b = time.time()
print(x)
print(b-a)

# c = time.time()
# data = fetch_webpage_content("https://api.weather.gov/gridpoints/BOX/71,90")
# save_json_to_file(data, "test_time.json")
# d = time.time()
# print(d-c)   #timing seems to be similar
