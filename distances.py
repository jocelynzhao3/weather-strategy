import csv
from math import radians, sin, cos, sqrt, atan2
import time
import math
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

# max_dist = float('inf')
# min_dist = 0
# with open('routes/all_asc_2024.csv') as f:
#     reader = csv.reader(f)
#     row1 = next(reader)
#     row2 = next(reader)

#     prev_lat =36.146807
#     prev_lon =-86.77556

#     for row in reader:
#         new_lon, new_lat = row
#         new_lon = float(new_lon)
#         new_lat = float(new_lat)

#         new_dist = haversine(prev_lat, prev_lon, new_lat, new_lon)
#         if new_dist == 0:
#             print(f'zero at {row}')
#             break
#         if new_dist < max_dist:
#             max_dist = new_dist
#             print(f'new max at {row}')
#         if new_dist > min_dist:
#             min_dist = new_dist
#             print(f'new min at {row}')

#         prev_lat = new_lat
#         prev_lon = new_lon

# for all asc 2024:
# 0.00014111377750237268
# 2.133030406215289

'''
Given limited API calls, we want 1 km resolution for as long as possible,
but the cover the race with (at worst) 2 km resolution
'''

def find_total_dist(csv_name):

    total_dist = 0

    a = time.time()
    with open(csv_name) as f:
        reader = csv.reader(f)
        row1 = next(reader)
        row2 = next(reader)

        prev_lat =36.146807
        prev_lon =-86.77556

        for row in reader:
            new_lon, new_lat = row
            new_lon = float(new_lon)
            new_lat = float(new_lat)

            total_dist += haversine(prev_lat, prev_lon, new_lat, new_lon)

            prev_lat = new_lat
            prev_lon = new_lon
    b = time.time()

    print(f'Total distance: {total_dist} km in {b-a} seconds')
    return total_dist

# find_total_dist('full_asc.csv')

'''
max_api_calls = 1450
total_dist = 2500 #km
'''

def api_call_distribution(total_dist, num_api_calls, short_res=1, long_res=2):
    '''
    total_dist = total distance left to race in km
    num_api_calls = number of remaining avaliable API calls
    short_res = short resolution distance in km (maximized)
    long_res = longer resolution distance in km

    returns number of allowed short_res API calls (which we will apply to beginning of race)
    '''
    short_calls = (long_res*num_api_calls - total_dist)/(long_res-short_res)

    if short_calls < 0: # not enough API calls/total distance is too long
        return 0
    return short_calls

# print('high res')
# print(api_call_distribution(2501, 1450))


'''
148.92 Meters | 488.58 Feet
Coordinates: 38.7049, -90.6115

201.30 Meters | 660.43 Feet

Coordinates: 38.7109, -90.6145
'''
if __name__ == "__main__":
    lat1 = 38.7049  # 148.92 in m
    lon1 = -90.6115
    lat2 = 38.7109  # 201.30
    lon2 = -90.6145
    print(haversine(lat1, lon1, lat2, lon2)*1000) # km
    print(201.3 - 148.92)
    print(atan2(201.3 - 148.92, haversine(lat1, lon1, lat2, lon2)*1000)* 180/math.pi)

    print(find_total_dist('routes/extra-B.csv'))
