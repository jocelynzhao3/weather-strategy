'''
Check resolution with respect to TIME and DISTANCE

Time resolution: 5 min is signifigantly slower... 10 min performs similarly to larger increments
 - decrease time resolution from 10 if size is an issue
 - decrease time resolution if data isn't heavily impacted

Distance resolution: not much choice here... just maximizing higher resolution calls with algebra
 - solve: x + 2(1450-x) = 2500, where x = #1km calls; 1450 - x = #2km calls; 2500 = total_dist

'''

import pandas as pd
from math import radians, sin, cos, sqrt, atan2
import requests
from datetime import datetime, timezone
import time
from scipy.interpolate import PchipInterpolator, CubicSpline
import pickle

#likely need to be conservative with API calls here

API_KEY = "xr5Nz8p6rYXN_yslBSewP1Q-qeW19PO1" #expires 2024-07-30 20:00 UTC
# PICKLE_FILE_PATH = "solcast_interp_func.pickle"
# DICT_FUNC_PATH = "solcast_dict_of_funcs.pickle"
OUTPUT_PATH = "test_solcast_df.pickle"

class SolcastInterpolator:

    def __init__(self, route_file_path, days_in_advance=1):
        '''
        route_file_path: csv to read from
        days_in_advance: int days in advance to collect data for
        dict_func_path: pickle file name where dictionary is stored
        '''
        self.route_file_path = route_file_path

        self.hours_in_advance = days_in_advance*24
        self.forcasts = {}
        self.lat_called = 0 # far away starting point
        self.lon_called = 0
        self.frequency = 10
        # self.frequency = 5, 10, 15, 20, 30 are other options

    def fetch_website_content(self, url):
        '''
        Return url content as list of dictionaries
        If error, returns None
        '''
        response = requests.get(url)
        # Check if the response status code indicates success (200)
        if response.status_code == 200:
            # Convert the JSON response into a Python dictionary
            data = response.json()
            # print(data)
            return data['forecasts']  # {'pv_power_rooftop': 0, 'period_end': '2024-04-19T09:00:00.0000000Z', 'period': 'PT1H'}

        else:
            print("Error:", response.status_code)

    def parse_datetime_string(self, datetime_string):
        '''
        Given datetime string, return timestamp // 3600
        as a float, should be UTC time
        ex. "2024-04-25T02:00:00.0000000Z"
        '''
        year = int(datetime_string[:4])
        month = int(datetime_string[5:7])
        day = int(datetime_string[8:10])
        hour = int(datetime_string[11:13])
        minute = int(datetime_string[14:16])
        this_datetime_obj = datetime(year, month, day, hour, minute, 0, tzinfo=timezone.utc)
        return this_datetime_obj.timestamp()/3600  #seconds into hours

    def haversine(self, lat1, lon1, lat2, lon2):
        '''
        Given 4 coordinates, determines distance between in km
        '''
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        radius_earth = 6371  # Radius of the Earth in kilometers
        distance = radius_earth * c
        return distance

    def create_func_dict(self, return_df = True):
        '''
        Create data dict of (lat, lon): interpolation function
        The interpolation function: f(x) = y
        where x = timestamp/3600
        and y = global horizontal irridance (W/m^2)

        Returns a pandas dataframe of ['latitude', 'longitude', 'timestamp', 'irradiance']
        '''
        num_api_calls = 0
        func_dict = {}
        df = pd.read_csv(self.route_file_path)

        all_lats = []
        all_lons = []
        all_timestamps = []
        all_irradiances =  []

        for _ , row in df.iterrows():
            lon = row['longitude']
            lat = row['latitude']
            # url = f"https://api.solcast.com.au/data/forecast/rooftop_pv_power?latitude={lat}&longitude={lon}&output_parameters=pv_power_rooftop&capacity=1&format=json&terrain_shading=true&loss_factor={self.loss_factor}&period=PT60M&hours={self.days_in_advance*24}&api_key={API_KEY}"
            url = f"https://api.solcast.com.au/data/forecast/radiation_and_weather?latitude={lat}&longitude={lon}&output_parameters=ghi&format=json&period=PT{self.frequency}M&hours={self.hours_in_advance}&terrain_shading=True&api_key={API_KEY}"

            # check if lat, lon is within 1 km of most recent call - if so, don't call
            if self.haversine(lat, lon, self.lat_called, self.lon_called) > 2:
                a = time.time()
                self.forecasts = self.fetch_website_content(url)
                num_api_calls += 1
                b = time.time()

                print(f'fetch website took {b-a} seconds')

                if not self.forecasts:   #error
                    print("error occurred")
                    return None

                self.lat_called = lat
                self.lon_called = lon

                powers = []
                timestamps = []

                for forecast in self.forecasts: # {'pv_power_rooftop': 0, 'period_end': '2024-04-19T09:00:00.0000000Z', 'period': 'PT1H'}
                    all_lats.append(lat)
                    all_lons.append(lon)
                    timestamps.append(self.parse_datetime_string(forecast['period_end']))
                    powers.append(forecast['ghi']) # global horizontal irridance

                all_timestamps.extend(timestamps)
                all_irradiances.extend(powers)

                interpolated_func = PchipInterpolator(timestamps, powers)
                func_dict[(lat, lon)] = interpolated_func  #only add data with new API pull

        print(f'num_api_calls: {num_api_calls}')

        data = {'latitude': all_lats,
                'longitude': all_lons,
                'time': all_timestamps,
                'irradiance': all_irradiances}

        solcast_df = pd.DataFrame(data)

        if return_df:
            return solcast_df
            # Write DataFrame to a CSV file
            # df.to_csv('output.csv', index=False)  # Set index=False if you don't want to write row indices

        return func_dict


if __name__ == "__main__":

#    # Read the two CSV files
#     csv1 = pd.read_csv('routes/route-to.csv')
#     csv2 = pd.read_csv('routes/route-back.csv')

#     # Concatenate them
#     concatenated = pd.concat([csv1, csv2], ignore_index=True)

#     # Write the concatenated data to a new CSV file
#     concatenated.to_csv('routes/concatenated.csv', index=False)

    a = time.time()
    solcast_inst = SolcastInterpolator("routes/A--short.csv")
    func_dict = solcast_inst.create_func_dict(return_df=True)
    b = time.time()

    with open(OUTPUT_PATH, 'wb') as file:
        # Dump the dictionary into the file
        pickle.dump(func_dict, file)

    # to print to dataframe:

    with open(OUTPUT_PATH, 'rb') as file:
        loaded_df = pickle.load(file)

    from IPython.display import display

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    display(loaded_df)
    print(f'time: {b-a} seconds')
