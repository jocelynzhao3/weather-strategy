print("Welcome to solar flux testing!")

import numpy as np
from numpy import array
from solarpy import solar_panel
from datetime import datetime
import matplotlib

#find units of all inputs to the panel!

panel = solar_panel(2.1, 0.2, id_name='NYC_xmas')  # surface (m^2), efficiency and name
panel.set_orientation(array([0, 0, -1]))  # upwards
panel.set_position(40.73, -73.93, 0)  # NYC latitude (-90 to +90 degrees), longitude (-179 to 180 degrees), altitude (0 to 24k meters)
panel.set_datetime(datetime(2019, 12, 25, 16, 15))  #number seems about right
x = panel.power()   #returns in units of W/m^2*m^2*units of efficiency?

#print(x)

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
    # panel = solar_panel(3.986327, 0.24)  # surface (m^2), efficiency, numbers based off of Nimbus
    panel = solar_panel(3.986327, 0.203)  # surface (m^2), efficiency changed based on temp

    panel.set_orientation(array([0, 0, -1]))  # upwards
    panel.set_position(lat, lon, elev)
    panel.set_datetime(datetime(year, month, day, hour, minute))
    return panel.power()

x = clear_sky_radiance(40.832, -98.338, 78.56, 2022, 7, 10, 15, 0)
print(x)

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

print(adj_radiance(x, 0))
