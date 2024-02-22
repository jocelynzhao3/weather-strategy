print("Welcome to interpolation!")

from scipy.interpolate import LinearNDInterpolator
import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


# Next steps:
# do interpolation (try linear interpolation and grid data) - will take a long time
# make interpolation function
# try graphing them for pretty images??
# how to get stuff into MIT SEVT github?

# Read CSV file
csv_file_path = 'final_radiance.csv'
data = pd.read_csv(csv_file_path)

a = time.time()
# Extract input points and output values

# Extract every 10th row of data
data_subset = data.iloc[::3, :]
points = data_subset.iloc[:, :3].values
output_values = data_subset.iloc[:, 3].values
b = time.time()
print(b-a)
# Create the LinearNDInterpolator
interp = LinearNDInterpolator(points, output_values)
c = time.time()
print("interp time: " + str(c-b))
# Define the point to interpolate
lat = 40.88278
lon = -98.37418
hours_since_start = 20
point_to_interpolate = [lat, lon, hours_since_start]

# Perform linear interpolation
interpolated_value = interp(point_to_interpolate)
d = time.time()
print(f"Interpolated value at {point_to_interpolate}: {interpolated_value}")
print("time to interpolate one point: " + str(d-c))

# Create a 3D scatter plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Scatter plot of the original data points
scatter = ax.scatter(points[:, 0], points[:, 1], points[:, 2], c=output_values, cmap='viridis', marker='o')

# Set labels and title
ax.set_xlabel('Lat')
ax.set_ylabel('Lon')
ax.set_zlabel('Hours from start')
ax.set_title('Solar slice of cake')

# Add a colorbar
cbar = fig.colorbar(scatter, ax=ax, orientation='vertical', label='Output Values')

plt.show()
