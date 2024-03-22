import numpy as np
from numpy import array
from solarpy import solar_panel
import csv
import json
import requests                   #set base to conda 3.11.5 to install package
import socket
from datetime import datetime
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from scipy.interpolate import LinearNDInterpolator
import pickle


class SolarInterpolator:

    def __init__(self, route_file_name):
        self.route_file_name = route_file_name
        self.bounds_list = [[0, 0], [1, 0], [0, 1], [1, 1], [0, 0]] # useless initial bounds list
        self.cloud_dict = {}

    def clear_sky_radiance(self, lat, lon, elev, year, month, day, hour, minute):
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
        # panel = solar_panel(3.986327, 0.203)  # efficiency changed based on temp - have other members experienced this?

        panel.set_orientation(array([0, 0, -1]))  # upwards
        panel.set_position(lat, lon, elev)
        panel.set_datetime(datetime(year, month, day, hour, minute))
        return panel.power()


    def adj_radiance(self, radiance, cloud_cover):
        '''
        Input:
        radiance: original solar radiance on a clear day in W/m^2
        cloud cover: decimal cloud cover range from 0.0-1.0, from weather api

        Return:
        float, adjusted radiance based on cloud cover, in W/m^2

        clear_sky_radiance and adj_radiance may differ in units (panel power vs solar radiance)
        - hopefully general trend is ok
        '''
        #check cloud cover value:
        if cloud_cover >= 0.0 and cloud_cover <= 1.0:
            return radiance * (1 - 0.75*(cloud_cover)**3.4)
        else:
            print("Please enter valid cloud cover value")


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

        # Open the file in read mode
        with open(file_path, 'r') as json_file:
            # Load the JSON data into a dictionary
            data_dict = json.load(json_file)

        new_link = data_dict['properties']["forecastGridData"] # link directs you to json with sky cover data

        sky_cover_content = self.fetch_webpage_content(new_link)

        if sky_cover_content:
            filename = 'sky_cover.json'
            self.save_json_to_file(sky_cover_content, filename)
            # print(f"Webpage content saved to {filename}")

        #Step 3: Read final json file

        # Assuming you have a JSON file named 'example.json' in the same directory as your Python script
        new_file_path = 'sky_cover.json'

        # Open the file in read mode
        with open(new_file_path, 'r') as json_file:
            # Load the JSON data into a dictionary
            sky_cover_dict = json.load(json_file)

        sky_cover_time_list = sky_cover_dict["properties"]["skyCover"]["values"]
        self.bounds_list = sky_cover_dict["geometry"]["coordinates"][0]
        self.cloud_dict.clear() #empty dict

        for i in range(len(sky_cover_time_list)):    # may not need to generate entire dictionary to improve efficiency
            key = sky_cover_time_list[i]["validTime"][:13]
            value = int(sky_cover_time_list[i]["value"])/100  #cloud cover as decimal 0.0-1.0
            self.cloud_dict[key] = value


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


    def create_data_interpolator(self):
        '''
        Input file name of route
        Writes lat, lon, timestamps, radiance data to list
        Interpolates four lists creating an interpolation function
        Returns interpolation function

        Interpolation function: input lat, lon, target timestamp//3600 (to get hours)
        '''
        lats = []   # initialize lists
        lons = []
        timestamps = []
        radiances = []

        with open(self.route_file_name, 'r', newline='') as csvfile:   #open route csv
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:  # for lat, lon coord
                lat, lon, elev = row[:3]
                lat = float(lat)
                lon = float(lon)
                elev = float(elev)
                self.run_this_file(lat, lon)   # ensures cloud_dict is ready for next steps

                # for this_datetime, cloud_cover in some dict.items():
                for this_datetime, cloud_cover in self.cloud_dict.items():

                    # parse my_datetime:
                    year = int(this_datetime[:4])
                    month = int(this_datetime[5:7])
                    day = int(this_datetime[8:10])
                    hour = int(this_datetime[11:])
                    this_datetime_obj = datetime(year, month, day, hour)
                    this_timestamp = this_datetime_obj.timestamp()/3600  #seconds into hours

                    # calculate radiance
                    clear_radiance = self.clear_sky_radiance(lat, lon, elev, year, month, day, hour, minute=0)
                    cloud_cover = float(cloud_cover)
                    final_radiance = self.adj_radiance(clear_radiance, cloud_cover)   #float or numpy float

                    # write data into lists
                    lats.append(lat)
                    lons.append(lon)
                    timestamps.append(this_timestamp)
                    radiances.append(final_radiance)

        # make interpolator:
        increment = 60 # prevent interp errors
        inc_lats = lats[::increment]
        inc_lons = lons[::increment]
        inc_timestamps = timestamps[::increment]
        inc_radiances = radiances[::increment]

        points = np.column_stack((inc_lats, inc_lons, inc_timestamps))
        interp_func = LinearNDInterpolator(points, inc_radiances)
        return interp_func


def start_server():
    # Set up the server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 8888))
    server.listen(1)
    print("Server listening on port 8888...")

    route_file_name = "2022_C_tester.csv"  #make constant or change as needed?
    # route_file_name = "FULL_race_tester.csv"
    interp_obj = SolarInterpolator(route_file_name)

    while True:
        # Wait for a connection from the client
        client_socket, client_address = server.accept()
        print(f"Accepted connection from {client_address}")

        function = interp_obj.create_data_interpolator()
        serialized_function = pickle.dumps(function)

        client_socket.sendall(serialized_function)

        # Close the connection
        client_socket.close()
        print("Socket closed")


if __name__ == "__main__":
    # route_file_name = "2022_C_tester.csv"  #make into constant? or change as needed?
    # route_file_name = "FULL_race_tester.csv"
    start_server()

    # testing:
    # lat = 42.3
    # lon = -71.1
    # route_file_name = "2022_C_tester.csv"  #make into constant? or change as needed?
    # # route_file_name = "FULL_race_tester.csv"
    # interp_obj = SolarInterpolator(route_file_name)
    # data, bounds  = interp_obj.write_data_to_dict(lat, lon)

    # for key, val in data.items():
    #     print(key, val)

    # print(bounds)


'''
goal of the server:
1. input: csv with lat, lon, elev
2. for every hour over next 7 days, write to multiple lists (csv may not be needed)
data in order for lat, lon, timestamp - consider using numpy arrays
3. interpolate over the lists to get an interpolation function
4. write interpolation function to a file
5. repeat on a __ timely basis <-- HOW OFTEN TO REPEAT? OR ONLY RUN WHEN REQUESTED
6. if client requests it, send this file to the client (don't forget - client changes datetime into timestamp // 3600)

Issues: q hull issues
'''
