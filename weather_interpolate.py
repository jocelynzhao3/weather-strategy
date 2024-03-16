from weather_test import SolarInterpolator
import pandas as pd
import numpy as np
from numpy import array
from solarpy import solar_panel
from datetime import datetime
from scipy.interpolate import LinearNDInterpolator


PANEL_AREA = 3.986327  #numbers based off of Nimbus
PANEL_EFF = 0.24 #may change under high temps

#User POV:
lat_list = [40.8, 40.7, 41.0, 41.8]
lon_list = [-98.3, -99.1,-100.4, -103.7]
hours_passed_list = [2, 20, 12, 24]
hour = 16
day = 24
month = 2
year = 2024

datetime_list = [
    datetime(2024, 3, 6, 10, 30, 0),  # Year, Month, Day, Hour, Minute, Second
    datetime(2024, 3, 7, 15, 45, 0),
    datetime(2024, 3, 8, 8, 0, 0),
    datetime(2024, 3, 9, 18, 20, 0),
]

#use datetime objects to generate an hours passed list

def get_radiance_list(lat_list, lon_list, hours_passed_list, hour, day, month, year, write_csv=False):
    '''
    Input lat, lon, hours_passed lists (of the same length)
    Input defined "start time": hour, day, month, year
    Input write_csv = True if we want to update radiance csv,
            remember to activate conda and weather_server.py

    Output: list of power values, may return nulls if extrapolating
    '''
    instance = SolarInterpolator("FULL_race_tester.csv", "final_radiance.csv", hour, day, month, year)
    radiance_list = instance.interpolate_radiance(lat_list, lon_list, hours_passed_list, write_csv=False)

    return radiance_list


# Functions for no internet connection:

def clear_radiance_list(lat_list, lon_list, datetime_list, guessed_cloud_cover=0):
    '''
    Input lat_list, lon_list, datetime_list - list of datetime instances
    (all of the same length)
    Input human estimate cloud coverage, ranging from 0 to 1

    Output: list of power values (same len)
    '''
    # Read CSV file
    data = pd.read_csv("FULL_race_tester.csv",)

    points = data.iloc[:, :2].values
    output_values = data.iloc[:, 2].values
    interp = LinearNDInterpolator(points, output_values) # create interpolator

    power_list = []
    for i, lat in enumerate(lat_list):
        lon = lon_list[i]
        interp_elev = interp([lat, lon])[0]
        # print(interp_elev)  #sanity check

        datetime_instance = datetime_list[i]
        year = datetime_instance.year
        month = datetime_instance.month
        day = datetime_instance.day
        hour = datetime_instance.hour
        power = clear_sky_radiance(lat, lon, interp_elev, year, month, day, hour, minute=0)

        if guessed_cloud_cover != 0 and guessed_cloud_cover <= 1:
            adj_power = power * (1 - 0.75*(guessed_cloud_cover)**3.4)
            power_list.append(adj_power)
        else:
            power_list.append(power)

    return power_list

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
        panel = solar_panel(PANEL_AREA, PANEL_EFF)  # surface (m^2), efficiency

        panel.set_orientation(array([0, 0, -1]))  # upwards
        panel.set_position(lat, lon, elev)
        panel.set_datetime(datetime(year, month, day, hour, minute))
        return panel.power()


if __name__ == "__main__":
    print(clear_radiance_list(lat_list, lon_list, datetime_list))
