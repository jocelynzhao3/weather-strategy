from datetime import datetime
import numpy as np
import time
import pickle
from math import radians, sin, cos, sqrt, atan2

# PICKLE_FUNC_DICT = "solcast_dict_of_funcs.pickle"
PICKLE_FUNC_DICT = "new_route_back.pickle"

def interpolate(lats, lons, unix_datetimes):
    '''
    lists should all be the same length
    lats: list of floats
    lons: list of floats
    unix_datetimes: list of unix_datetimes (floats)
    update_func: optional bool to regenerate interpolation function

    return list of corresponding interpolated insolations (W/m^2), may return nan values
    '''
    timestamps = [unix/3600 for unix in unix_datetimes]

    try:
        with open(PICKLE_FUNC_DICT, 'rb') as file:
            loaded_dictionary = pickle.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: File '{PICKLE_FUNC_DICT}' not found, set update_func as True or check folder!")

    requested_rads = []
    a = time.time()
    for i in range(len(lats)):
        loaded_function = dictionary_search(lats[i], lons[i], loaded_dictionary)
        requested_rads.append(loaded_function(timestamps[i]))
    b = time.time()

    print("search & interp time: " + str(b-a))
    return np.array(requested_rads)

def haversine(lat1, lon1, lat2, lon2):
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

def dictionary_search(lat, lon, dictionary):
    '''
    Input desired lat, lon, dictionary
    Return interpolation function for closest lat, lon point
    '''
    min_dist = float('inf')

    for coord in dictionary.keys():
        if haversine(lat, lon, coord[0], coord[1]) < min_dist:
            min_coord = coord

    return dictionary[min_coord]

if __name__ == "__main__":

    datetime_list = [datetime(2024, 5, 5, 0, 56, 19, 273221),  # year, month, day, hour, minute, second, microsecond,
                     datetime(2024, 5, 6, 6, 56, 19, 273221),
                     datetime(2024, 5, 6, 12, 56, 19, 273221),
                     datetime(2024, 5, 7, 18, 56, 19, 273221)] # must be UTC times....

    # lats = [36.239005, 36.539854, 36.878315, 36.804048]  # for nashville to paducah
    # lons = [-86.81887, -86.901317, -87.508044, -88.200973]

    lats = [42.35742, 42.4819, 42.71567, 42.8167]
    lons = [-71.09271, -71.11597, -71.21049, -71.28425]

    unix_datetimes = [my_dt.timestamp() for my_dt in datetime_list]

    x = interpolate(lats, lons, unix_datetimes)
