print("Welcome to interpolation!")

from scipy.interpolate import LinearNDInterpolator
import numpy as np
import pandas as pd
import time

# Next steps:
# do interpolation (try linear interpolation and grid data) - will take a long time
# make interpolation function
# try graphing them for pretty images??
# how to get stuff into MIT SEVT github?

# Read CSV file
csv_file_path = 'final_radiance.csv'
data = pd.read_csv(csv_file_path)

a = time.time()
points = data.iloc[:, :4].values
values = data.iloc[:, 4].values
b = time.time()
print(b-a)
# Create the LinearNDInterpolator
interp = LinearNDInterpolator(points, values)  #likely have to cut values to make code run faster
c = time.time()
print(c-b)
lat = 40.88278
lon = -98.37418
hour = 8
day = 19

# Example of linear interpolation
example_point = np.array([lat, lon, hour, day])  # Replace with your desired coordinates
interpolated_value = interp(*example_point)
d = time.time()
print(d-c)

print(f"Interpolated value at {example_point}: {interpolated_value}")




'''
In my case, points = [lat, lon, hour, day (of the month)]   (for pratical purposes, there should be no need to consider month and year)
'''
