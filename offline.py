'''
Give clear sky irradiance values - use when we don't have internet

https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.location.Location.get_clearsky.html#pvlib.location.Location.get_clearsky
'''

import pandas as pd
import pvlib
import time
import pickle

input_csv = "routes/A--short.csv"
predicted_cloud_cover = 0 # decimal between 0 and 1
OUTPUT_PATH = "offline_data.pickle"

def adj_radiance(radiance, cloud_cover):
        '''
        Input:
        radiance: original solar radiance on a clear day in W/m^2
        cloud cover: decimal cloud cover range from 0.0-1.0, from weather api

        Return:
        float, adjusted radiance based on cloud cover, in W/m^2

        clear_sky_radiance and adj_radiance may differ in units (panel power vs solar radiance)
        - hopefully general trend is ok
        '''
        #check cloud cover value:
        if cloud_cover >= 0.0 and cloud_cover <= 1.0:
            return radiance * (1 - 0.75*(cloud_cover)**3.4)
        else:
            print("Please enter valid cloud cover value")

def offline_func_dict(input_csv, start_race_time, end_race_time, predicted_cloud_cover):
    '''
    input_csv: input file name as string, containing lat, lon points
    start_race_time: datetime string, ex. '2024-07-03 14:00:00' in UTC
    end_race_time: datetime string
    predicted_cloud_cover: decimal in [0, 1] range
    '''
    df = pd.read_csv(input_csv)

    all_lats = []
    all_lons = []
    all_times = []
    all_irradiances =  []

    times = pd.date_range(start=start_race_time, end=end_race_time, freq='10min', tz='UTC')  # list of times
    # print(times)

    for _ , row in df.iterrows():
        longitude = row['longitude']
        latitude = row['latitude']

        location = pvlib.location.Location(latitude, longitude)
        clear_sky_irradiances = location.get_clearsky(times) # get the right item
        # print(clear_sky_irradiances)

        for index, irr in enumerate(clear_sky_irradiances['ghi']): # only take ghi information

            final_irradiance = adj_radiance(irr, predicted_cloud_cover)

            all_lats.append(latitude)
            all_lons.append(longitude)
            all_times.append(pd.to_datetime(times[index]).timestamp()/3600)  # get unix/3600
            all_irradiances.append(final_irradiance)


    data = {'lats': all_lats,
            'lons': all_lons,
            'time': all_times,
            'irradiances': all_irradiances}

    df = pd.DataFrame(data)
    # df.to_csv('offline_example.csv')  # to test
    return df



if __name__ == "__main__":

    # WATCH TIME ZONES: EST = UTC-4 in summer
    start_datetime_string = '2024-07-04 10:00:00' # in UTC
    end_datetime_string = '2024-07-04 12:00:00' # in UTC


    # sample_urls = [
    # f"https://api.solcast.com.au/data/forecast/radiation_and_weather?latitude=36.099763&longitude=-112.112485&output_parameters=gti,dhi,dni,ghi,zenith,azimuth&format=json&period=PT60M&hours=24&array_type=fixed&api_key={API_KEY}",
    # f"https://api.solcast.com.au/data/forecast/radiation_and_weather?latitude=36.099763&longitude=-112.112485&output_parameters=gti,dhi,dni,ghi,zenith,azimuth&format=json&period=PT60M&hours=24&array_type=fixed&tilt=80&azimuth=-90&api_key={API_KEY}"
    # ]

    a = time.time()
    offline_df = offline_func_dict(input_csv, start_datetime_string, end_datetime_string, predicted_cloud_cover)
    b = time.time()
    print(f'{b-a} seconds to run')

    with open(OUTPUT_PATH, 'wb') as file:
        # Dump the dictionary into the file
        pickle.dump(offline_df, file)

    from IPython.display import display

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    display(offline_df)
