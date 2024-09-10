import requests
import pvlib
import pandas as pd
import numpy as np
import pickle
import time

API_KEY = "xr5Nz8p6rYXN_yslBSewP1Q-qeW19PO1" #expires 2024-07-30 20:00 UTC
OUTPUT_PATH = "solcast_charging_df.pickle"
days_in_advance = 7

def fetch_website_content(url):
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


def model_charging(latitude, longitude, altitude, start_charging_time, end_charging_time, temp = 24):
    '''
    charging location: lat, lon in degrees and altitude in m
    start_charging_time: unix timestamp (in seconds)
    end_charging_time: unix timestamp (in seconds)
    temp: optional with defult = 24C or 75F, in C

    return: pandas df of: timestamp, irradiance (GTI - W/m^2), 'optimal' azimuth, 'optimal' zenith

    ** This uses solcast!

    In theory:
    - the angle of the solar panels "face" (aka the sun) = azimuth angle, where north = 0, east = -90, west = 90
    - the angle the solar panel is raised (from flat position) = zenith angle (unless it is cloudy, in which case the solar panels may lay flat)
    '''
    beginning, ending = pd.to_datetime([start_charging_time, end_charging_time], unit='s')  # converts unix back to dt string
    angle_dict = {}
    num_api_calls = 0

    times = pd.date_range(start=beginning, end=ending, freq='10min', tz='UTC')
    for time in times:
        solar_position = pvlib.solarposition.get_solarposition(time, latitude, longitude, altitude, temp)
        if np.array(solar_position['azimuth'])[0] > 180:
            converted_azimuth = 360 - np.array(solar_position['azimuth'])[0]
        else:
            converted_azimuth = -1*np.array(solar_position['azimuth'])[0]
        # azimuth, zenith
        angle_dict[time] = (converted_azimuth, np.array(solar_position['apparent_zenith'])[0])

    # return angle_dict - how to only get the largest for a time??

    all_times = []
    all_irr = []
    all_azi = []
    all_zeni = []

    for sometime in angle_dict:  # not very time efficient...
        optimal_azimuth, optimal_zenith = angle_dict[sometime]
        url_start = f"https://api.solcast.com.au/data/forecast/radiation_and_weather?latitude={latitude}&longitude={longitude}"
        url_custom = f"output_parameters=gti,zenith,azimuth&format=json&period=PT{10}M&hours={24*days_in_advance}&array_type=fixed&tilt={optimal_zenith}&azimuth={optimal_azimuth}&api_key={API_KEY}"
        outputs = fetch_website_content(url_start + '&' + url_custom)
        num_api_calls += 1

        # only grab useful output:
        for output in outputs: # 2024-05-11T15:5 vs 2024-05-11 15:5
            output_time = output['period_end']

            if (output_time[:10] + " " + output_time[11:15]) == str(sometime)[:15]: # found the right time
                all_times.append(pd.to_datetime(sometime).timestamp()/3600)
                all_irr.append(int(output['gti']))
                all_azi.append(optimal_azimuth)
                all_zeni.append(optimal_zenith)
                break

    data = {'time': all_times,
            'irradiance': all_irr,
            'azimuth': all_azi,
            'zenith': all_zeni}

    df = pd.DataFrame(data)
    # df.to_csv('charging_example.csv')  # to test
    # print(f'num api calls: {num_api_calls}')
    return df


if __name__ == "__main__":

    # WATCH TIME ZONES: EST = UTC-4 in summer
    start_datetime_string = '2024-07-03 14:00:00' # in UTC
    end_datetime_string = '2024-07-03 16:00:00' # in UTC

    start_unix = pd.to_datetime(start_datetime_string).timestamp()
    end_unix = pd.to_datetime(end_datetime_string).timestamp()


    # sample_urls = [
    # f"https://api.solcast.com.au/data/forecast/radiation_and_weather?latitude=36.099763&longitude=-112.112485&output_parameters=gti,dhi,dni,ghi,zenith,azimuth&format=json&period=PT60M&hours=24&array_type=fixed&api_key={API_KEY}",
    # f"https://api.solcast.com.au/data/forecast/radiation_and_weather?latitude=36.099763&longitude=-112.112485&output_parameters=gti,dhi,dni,ghi,zenith,azimuth&format=json&period=PT60M&hours=24&array_type=fixed&tilt=80&azimuth=-90&api_key={API_KEY}"
    # ]

    a = time.time()
    angle_df = model_charging(36.099763, -112.112485, 2000, start_unix, end_unix)
    b = time.time()
    print(f'{b-a} seconds to run') # around 13 sec?

    with open(OUTPUT_PATH, 'wb') as file:
        # Dump the dictionary into the file
        pickle.dump(angle_df, file)

    from IPython.display import display

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    display(angle_df)




'''
How to model solar coming in while stationary? (From Stephen)

Accurately modeling the irradiance while you are stationary charging is similar to determining the "Plane of Array Irradiance" or Global Tilted Irradiance.
This page has a lot of info about it (and other modeling topics): https://pvpmc.sandia.gov/modeling-guide/1-weather-design-inputs/plane-of-array-poa-irradiance/.
Basically, there are 3 components: the DNI, the ground diffuse irradiance, and the sky diffuse irradiance.
I would say you can start with DNI as a rough estimate. You can then adjust for the sky diffuse irradiance using the models on the page I linked.
You'll want to make sure your tilt angle corresponds to the angle such that the panel is normal to the sun (meaning it will change over time).
The ground one is tricky since you will be charging at different locations.
If you want to be really accurate you would need to adjust the formula based on the surface of where you are charging.

Solcast model:
Need to calculate zenith and azimuth for any lat, lon, elev?, time
We can then use Solcast

Hand model:
Read https://pvpmc.sandia.gov/modeling-guide/1-weather-design-inputs/irradiance-insolation/

Concerns:
We may not know where we stop - optimizer decides where we stop
We need to keep track of timezone/timimg when accounting for charging time - use unix time

UTC-5 = EST
UTC = EST+5
'''
