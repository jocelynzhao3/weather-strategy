print("welcome to client-server weather testing")
#belongs on client side, clean up repetitive functions

from weather_client import run_this_file
import numpy as np
from numpy import array
from solarpy import solar_panel
from datetime import datetime
import csv
import time

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

def find_item(csv_file, target_item):
    '''
    find desired cloud coverage with appropriate target date and time
    '''
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            # Assuming the first column contains the item you're searching for
            if row and row[0] == target_item:
                return row[1]  # Return the corresponding value from the second column

    # If the target item is not found, return None or handle it as needed
    return None

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
    year = str(year)
    month = str(month)
    day = str(day)
    hour = str(hour)
    input_key = year.zfill(2) + "-" + month.zfill(2) + "-" + day.zfill(2) + "T" + hour.zfill(2)

    cloud_cover = find_item("local_cloud_cover.csv", input_key)
    if cloud_cover != None:  #datetime was found
        cloud_cover = float(find_item("local_cloud_cover.csv", input_key))
        return adj_radiance(clear_radiance, cloud_cover)
    else:
        # print("This time is unavaliable")    #may be asked to interpolate here, returns None for now
        return "This time is unavaliable"
        # return None

def write_radiance_csv(file_name, file_path):
    find_radiance(lat, lon, elev, year, month, day, hour, minute=0)
    pass

file_path = "2022_C-checker.csv"
#current date:
year= 2024
month= 2
day= 9
hour=12
rad_list = []

a = time.time()
with open(file_path, 'r', newline='') as csvfile:
    csv_reader = csv.reader(csvfile)
    for row in csv_reader:
        lat, lon, elev = row[:3]
        print(lat + " " + lon)
        lat = float(lat)
        lon = float(lon)
        elev = float(elev)
        run_this_file(lat, lon)
        rad = find_radiance(lat, lon, elev, year, month, day, hour, minute=0)
        rad_list.append([lat, lon, rad])
b = time.time()

print("complete")
print("time: " + str(b-a))  #50s

# Your list data
labels = ["Lat", "Lon", "Adjusted Rad"]

# Specify the CSV file path
radiance_csv_path = "my_radiance.csv"

# Open the CSV file in write mode
with open(radiance_csv_path, mode='w', newline='') as file:
    # Create a CSV writer object
    writer = csv.writer(file)

    # Write the header
    writer.writerow(labels)

    # Write the data rows
    writer.writerows(rad_list)   #CHANGE THIS - SEEMS INEFFICIENT

print(f"CSV file '{radiance_csv_path}' created successfully.")
