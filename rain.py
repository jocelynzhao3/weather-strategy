'''
Run this occasionally to alert caravan of incoming rain
- running on 9200 rows in 235 seconds (~ 4 minutes)

- limit data stores (rain chance < 30 or time too far in future)
- how to organize CSV for easy use? - currrently sorted by lat/lon point
- test test test

Final data: CSV holding times and locations on potential chance of rain
'''

import pandas as pd
import json
import csv
import requests                   #set base to conda 3.11.5 to install package
from datetime import datetime, timezone
import time
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

# WATCH TIME ZONES: EST = UTC-4
OUTPUT_PATH = "rain.csv"

class SolarInterpolator:

    def __init__(self, stage_file_name, days_in_advance = 2):
        self.route_file_name = stage_file_name
        self.bounds_list = [[0, 0], [1, 0], [0, 1], [1, 1], [0, 0]] # useless initial bounds list
        self.rain_dict = {}
        self.increment = 5 # prevent interp errors
        self.days_in_advance = days_in_advance

    def fetch_webpage_content(self, url):
        # Send a GET request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            print("fetch worked")
            return response.json()  # Assume the content is in JSON format
        else:
            print(f"Failed to fetch content. Status code: {response.status_code}")

    def save_json_to_file(self, data, filename):
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)

    def write_data_to_dict(self, lat, lon):
        '''
        Given lat, lon, grabs hours cloud coverage forecast from internet and
        organizes into dictionary, along with bounds of this forecast

        Returns none (alters class variable)
        '''
        link = "https://api.weather.gov/points/" + str(lat) + "," + str(lon)
        #example: link = "https://api.weather.gov/points/42.36,-71.06"

        json_content = self.fetch_webpage_content(link)

        if json_content:
            filename = 'weather_points.json'
            self.save_json_to_file(json_content, filename)
            # print(f"Webpage content saved to {filename}")

        #Step 2: Read just-created json file to get link to sky cover data

        # Assuming you have a JSON file named 'example.json' in the same directory as your Python script
        file_path = 'weather_points.json'

        # Open the file in read modex
        with open(file_path, 'r') as json_file:
            # Load the JSON data into a dictionary
            data_dict = json.load(json_file)

        new_link = data_dict['properties']["forecastGridData"] # link directs you to json with sky cover data

        rain_content = self.fetch_webpage_content(new_link)

        if rain_content:
            filename = 'rain.json'
            self.save_json_to_file(rain_content, filename)
            # print(f"Webpage content saved to {filename}")

        #Step 3: Read final json file

        # Assuming you have a JSON file named 'example.json' in the same directory as your Python script
        new_file_path = 'rain.json'

        # Open the file in read mode
        with open(new_file_path, 'r') as json_file:
            # Load the JSON data into a dictionary
            rain_dict = json.load(json_file)

        rain_time_list = rain_dict["properties"]["probabilityOfPrecipitation"]["values"]
        self.bounds_list = rain_dict["geometry"]["coordinates"][0]
        self.rain_dict.clear() #empty dict

        for i in range(len(rain_time_list)):    # may not need to generate entire dictionary to improve efficiency
            key = rain_time_list[i]["validTime"][:13]
            value = int(rain_time_list[i]["value"])/100  #cloud cover as decimal 0.0-1.0
            self.rain_dict[key] = value


    def within_bounds(self, lat, lon, bounds_list):
        '''
        Determines if current (lat, lon) is within cloud_cover bounds (no need to query from server)
        '''
        point = Point(lon, lat)     #bounds list may reverse points
        polygon = Polygon(bounds_list)
        return polygon.contains(point)


    def run_this_file(self, lat, lon):
        '''
        Check is current cloud_dict class var holds correct info
        If not, updates class vars
        '''
        if not self.within_bounds(lat, lon, self.bounds_list):
           self.write_data_to_dict(lat, lon)
           return True
        return False


    def create_rain_data(self, threshold = -1, locations_only = False):
        '''
        Input file name of route
        Optionally input threshold value in range [0, 1] to only shows rain chance above given threshold
        Optionally input locations_only to see locations of rain, but not the times?
        Writes lat, lon, datetimes, rain_chances
        Returns a pandas dataframe
        '''
        df = pd.read_csv(self.route_file_name)
        current_time = time.time()

        all_lats = []
        all_lons = []
        all_datetimes = []
        all_rain_chances =  []
        all_warnings = []

        # Iterate through rows of the DataFrame
        for _, row in df.iterrows():
            lon = row['longitude']
            lat = row['latitude']
            if self.run_this_file(lat, lon):   # ensures cloud_dict is ready for next steps
                timestamps = []
                rain_chances = []

                for this_datetime, rain_chance in self.rain_dict.items():

                    new_time = pd.to_datetime(this_datetime).timestamp()  # limits data we store
                    if new_time - current_time > self.days_in_advance*86400:
                        break # we got enough data for now, can move on

                    if rain_chance >= threshold:  # limits data we store
                        timestamps.append(this_datetime)
                        rain_chances.append(float(rain_chance))
                        all_lats.append(lat)
                        all_lons.append(lon)

                        if rain_chance > 0.5:
                            all_warnings.append('HIGH')
                        else:
                            all_warnings.append('LOW')

                all_datetimes.extend(timestamps)
                all_rain_chances.extend(rain_chances)

        if locations_only:
            locations = set(zip(all_lats, all_lons))
            filename = 'rain_locations_only'
            with open(filename, 'w') as csvfile:
                csvwriter = csv.writer(csvfile)
                for location in locations:
                    csvwriter.writerow(location)

        data = {'latitude': all_lats,
                'longitude': all_lons,
                'time': all_datetimes, # in UTC
                'rain chance': all_rain_chances,
                'warnings': all_warnings}

        df = pd.DataFrame(data)
        return df



if __name__ == "__main__":

    # csv1 = pd.read_csv('routes/route-to-split-stops(npieces=10)-elev.csv')
    # csv2 = pd.read_csv('routes/route-back-split-stops(npieces=10)-elev.csv')
    # concatenated = pd.concat([csv1, csv2], ignore_index=True)
    # concatenated.to_csv('routes/concatenated_elev.csv', index=False)

    a = time.time()
    interp_inst = SolarInterpolator('strategee/weather_spline/weather_old/I--Gering-to-Casper.csv')
    weather_df = interp_inst.create_rain_data(threshold=0.1, locations_only=False)  # maybe plug into somewhere and visualize?
    print(weather_df)
    weather_df.to_csv('rain.csv')
    b = time.time()

    # weather_df.to_csv('rain_csv')
    print(f'runtime: {b-a} seconds')

    # Write DataFrame to a CSV file
    # df.to_csv('output.csv', index=False)  # Set index=False if you don't want to write row indices




print("hi there! ")
