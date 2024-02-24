print("Welcome to client-server weather testing, where the magic happens!")

from weather_client import run_this_file
import numpy as np
from numpy import array
from solarpy import solar_panel
from datetime import datetime
import csv
import time
from scipy.interpolate import LinearNDInterpolator
import pandas as pd


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

# test solarpy library works:
# print(clear_sky_radiance(46, -80, 200, 2024, 2, 3, 12, 0))


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

    Note: this function is not nessessary if we use interpolation, it is only useful for a specific date/time w/o interpolation
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
        # print("This time is unavaliable")    #may be asked to interpolate here
        return "This time is unavaliable"  #means that given the constant datetime in the 2.5*2.5 km square, no cloud cover data
        # should not matter if we interpolate over all avaliable hours of the day
        # return None


######## The code below takes 1 csv and returns radiance for every point for ONE specified datetime and writes to csv ########

def one_time_csv(file_path="2022_C_tester.csv", year= 2024, month= 2, day= 18, hour=12):
    '''
    Input csv to use and time
    '''
    rad_list = []
    a = time.time()
    with open(file_path, 'r', newline='') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            lat, lon, elev = row[:3]
            # print(lat + " " + lon)
            lat = float(lat)
            lon = float(lon)
            elev = float(elev)
            run_this_file(lat, lon)
            rad = find_radiance(lat, lon, elev, year, month, day, hour, minute=0)  # may be a string
            rad_list.append([lat, lon, rad])
    b = time.time()

    print("complete")
    print("time: " + str(b-a))  #50s

    # Your list data
    labels = ["Lat", "Lon", "Adjusted Rad"]  #ADD TIME TO THIS

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

######## The code below takes 1 csv and returns radiance for EVERY datetime on cloud csv and writes to new csv ########


def write_all_to_csv(file_path = "2022_C_tester.csv"):
    '''
    MAIN FUNCTION
    Input the route csv to use
    '''
    cloud_path = "local_cloud_cover.csv"
    final_csv = "final_radiance.csv"    #we will interpolate on this csv

    # Specify the column headers
    final_column_headers = ['Lat', 'Lon', 'Hours since start', 'Radiance']  #DEFINE START

    # Writing to CSV file
    with open(final_csv, mode='w', newline='') as file:
        csv_writer = csv.writer(file)      # Create a CSV writer object
        csv_writer.writerow(final_column_headers)         # Write the column headers in the first line

    print(f'CSV file "{final_csv}" inital creation.')

    data_row=[]

    # Get the current date and time
    current_datetime = datetime.now()   #START = current datetime?

    # Extract individual components
    current_month = current_datetime.month
    current_day = current_datetime.day
    current_hour = current_datetime.hour

    a = time.time()
    with open(file_path, 'r', newline='') as csvfile:   #open route csv
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:  # for lat, lon coord
            lat, lon, elev = row[:3]
            # print(lat + " " + lon)
            lat = float(lat)
            lon = float(lon)
            elev = float(elev)
            run_this_file(lat, lon)   # ensures local_cloud_cover csv is ready for next steps

            with open(cloud_path, 'r', newline='') as cloud_csvfile:   #open cloud csv
                cloud_csv_reader = csv.reader(cloud_csvfile)
                next(cloud_csv_reader)    # Skip the first line, which is boundary list
                for cloud_row in cloud_csv_reader:  # for each avaliable date/time

                    my_datetime = cloud_row[0]
                    cloud_cover = cloud_row[1]

                    #parse my_datetime:
                    year = int(my_datetime[:4])   #likely the same - 2024
                    month = int(my_datetime[5:7])  #likely the same (for the race)
                    day = int(my_datetime[8:10])
                    hour = int(my_datetime[11:])


                    hours_since_start = (day - current_day)*24 + hour - current_hour

                    # calculate radiance - clear_sky_radiance and adj_radiance may differ in units (panel power vs solar radiance) - hopefully general trend is ok
                    clear_radiance = clear_sky_radiance(lat, lon, elev, year, month, day, hour, minute=0)
                    cloud_cover = float(cloud_cover)
                    final_radiance = adj_radiance(clear_radiance, cloud_cover)   #float or numpy float

                    # write data into final csv
                    data_row = [lat, lon, hours_since_start, final_radiance]
                    with open(final_csv, 'a', newline='') as final_file:   # I choose to open/close/reopen final_csv because it gets very large
                        final_csv_writer = csv.writer(final_file)
                        final_csv_writer.writerow(data_row)
    b = time.time()

    print(f'CSV file "{final_csv}" completed.')
    print(f"Time to run: {b-a} seconds.")



if __name__ == "__main__":
    write_all_to_csv(file_path = "2022_C_tester.csv")
    # pass


'''
Many potential/current bugs:
1. server must be OPENED BEFORE anything runs (maybe client too?) - activate conda, python weather_server.py, etc.
2. server must close before used again (how to open server when needed?)
3. How to catch errors.....
4. We update the cloud csv when we update lat/lon, not when we update time!! (crude fix is the make cloud cover a far away point,
then plug in desired point and current cloud data will update)

Next steps:
1. This may be very very very inaccurate - check up on that
2. clean up repetitive functions

Note: this is a client-side function (for now)
'''
