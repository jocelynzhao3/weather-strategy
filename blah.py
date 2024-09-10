'''
COMMAND: scp jjz300@athena.dialup.mit.edu:~/GeminiStrategy/strategee/weather/my_interp_func.pickle ~/documents
    - instead of ~/documents, file input location can be somewhere else on local
    - I ran this command from local home dir

Check locker space: du -sk * .??* | sort -nr | more
To see percent space used: fs lq .

UTC-5 = EST
UTC = EST+5
'''

# tester file
import time

import numpy as np
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt
x = np.arange(10)
y = np.sin(x)
a = time.time()
cs = CubicSpline(x, y)
print(2, cs(2))
b = time.time()
print(b-a)

from scipy.interpolate import PchipInterpolator
x = np.arange(10)
y = np.sin(x)
a = time.time()
pc = PchipInterpolator(x, y)
print(2, pc(2))
b = time.time()
print(b-a)


import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

# Generate some random noisy data
x = np.linspace(0, 10, 10)
y = np.sin(x) + np.random.normal(0, 0.1, size=x.shape)

# Create an interpolation function
interp_func = interp1d(x, y, kind='linear')

import pandas as pd
from datetime import datetime

# Define the list of Python datetime objects
datetime_list = [
    datetime(2024, 4, 27, 0, 56, 19, 273221),
    datetime(2024, 4, 27, 6, 56, 19, 273221),
    datetime(2024, 4, 27, 12, 56, 19, 273221),
    datetime(2024, 4, 27, 18, 56, 19, 273221)
]


# s = '345x100'
# x = s.split('x')
# print(float(x[0]) * int(x[1]))

# s = "9:30:00 AM"
# curr_time = s.split(':')[:2]
# print(curr_time)


# import pandas as pd

# # Example DataFrame
# data = {'Name': ['John', 'Anna', 'Peter', 'Linda'],
#         'Age': [28, 35, 42, 29],
#         'City': ['New York', 'Paris', 'London', 'Sydney']}

# df = pd.DataFrame(data)

# # Write DataFrame to a CSV file
# df.to_csv('output.csv', index=True)  # Set index=False if you don't want to write row indices


import time
from datetime import datetime

# Get the current datetime
current_datetime = datetime.now().timestamp()


print("Current datetime:", current_datetime)

# Get the current Unix time
current_unix_time = int(time.time())

print("Current Unix time:", current_unix_time)

from datetime import datetime

# Assuming you have a Unix timestamp
unix_timestamp = 1620122873  # Example timestamp

# Convert Unix timestamp to datetime object
dt = datetime.fromtimestamp(unix_timestamp)
print("Datetime object:", dt)
print(dt.year)


from datetime import datetime, timezone

# Create a datetime object for a specific date and time in UTC
specific_utc_time = datetime(2024, 5, 4, 12, 30, 0, tzinfo=timezone.utc)

print("Specific UTC time:", specific_utc_time)

print(specific_utc_time.timestamp())

print('here')
times = pd.date_range(start='2024-05-05 00:00:00', end='2024-05-05 1:00:00', freq='10min', tz='UTC')
for sometime in times:
    print(sometime)

import pytz
tz = pytz.timezone('UTC')
dt = datetime(1970, 1, 1, 0, 0, 0, tzinfo = tz)  # specify timezone just in case
x = dt.timestamp() # timestamps given in seconds

tz = pytz.timezone('EST')
curr_dt = datetime(1969, 12, 31, 19, 0, 0, tzinfo=tz)  # edit datetime here!
y = curr_dt.timestamp()

diff = x -y
print(x) # UTC time
print(y) # est time

# to get the utc time from the est:
print(y + 18000) # gives you

# import pickle

# file_path = 'weather_df.pickle'
# with open(file_path, 'rb') as file:
#     loaded_dictionary = pickle.load(file)

# print(loaded_dictionary)


my_list = np.arange(0, 360, 1)
for angle in my_list:
    if angle > 180:
        converted_azimuth = 360 - angle
    else:
        converted_azimuth = -1*angle
    print(angle, converted_azimuth)


print(f'four: {4}')

current_datetime = datetime.now()
s_timestamp = current_datetime.timestamp()

beginning, ending = pd.to_datetime([s_timestamp, s_timestamp+ 10800], unit='s')
print(pd.date_range(start=beginning, end=ending, freq='10min', tz='UTC'))


x = "2024-05-12T11:00:00.0000000Z"
print(x[:10] + " " + x[11:15])


# Convert datetime string to timestamp
print(pd.to_datetime(x))
timestamp = pd.to_datetime(x).timestamp()

print(timestamp + 7200)
print(timestamp/3600)


# import time
# a = time.time()
# time.sleep(2)
# b = time.time()
# print(b-a)

# WATCH TIME ZONES: EST = UTC-5
start_datetime_string = '2024-07-03 14:00:00' # in UTC
end_datetime_string = '2024-07-03 16:00:00' # in UTC

start_unix = pd.to_datetime(start_datetime_string).timestamp()
end_unix = pd.to_datetime(end_datetime_string).timestamp()
beginning, ending = pd.to_datetime([start_unix, end_unix], unit='s')
print('here')
print(beginning)
print(ending)
times = pd.date_range(start=beginning, end=ending, freq='10min', tz='UTC')
print(times)

import pvlib
latitude = 42.3601
longitude = -71.0589

location = pvlib.location.Location(latitude, longitude)
clear_sky_irradiances = location.get_clearsky(times) # get the right item
# print(clear_sky_irradiances['ghi'])
# print(type(clear_sky_irradiances['ghi']))

for i, irr in enumerate(clear_sky_irradiances['ghi']):
    print(times[i], irr)


'''
Make a time table to compare UTC time vs EST, CST, MST
'''


# import pickle
# with open("test_asc.pickle", 'rb') as file:
#     loaded_df = pickle.load(file)
#     loaded_df.to_parquet("better_asc.parquet")

# print(pd.read_parquet("better_asc.parquet"))  # pretty cool lol

# x = pd.read_parquet("palmer.parquet")
# x.to_csv('palmer.csv')



print(time.time())
print(pd.to_datetime('2024-07-21T00').timestamp()/3600)



# l = [1, 1, 1, 1, 1, 2, 2, 2, 2]
# d = [5, 5, 5, 5, 5, 7, 7, 8, 8]

# x = set(zip(l, d))
# print(x)
