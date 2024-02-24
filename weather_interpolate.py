from weather_test import SolarInterpolator

#User POV:
instance = SolarInterpolator("FULL_race_tester.csv", "final_radiance.csv", 16, 24, 2, 2024)   #hour, day, month, year
instance.graph_interpolation()
lat_list = [40.8, 40.7, 41.0, 41.8]
lon_list = [-98.3, -99.1,-100.4, -103.7]
hours_passed_list = [2, 20, 12, 24]
# if write_csv is true, remember to activate conda and weather_server.py
# radiance_list = instance.interpolate_radiance(lat_list, lon_list, hours_passed_list, write_csv=False)
# print(radiance_list)



'''
Notes:
1. interp list of points seems pretty fast (first query ~ 3 sec, after that <<0.01 sec)
2. creating interpolator takes ~10 sec (done once)
3. writing csv takes multiple minutes (1 segment ~ 8 minutes)
4. points outside of interpolation WILL RETURN NAN - user needs to expect that or I take care of it

Full race csv stats: (interp every 5 points)
1. interp list of points is pretty fast (first query ~ 15 sec, after that << 0.01 sec)
2. creating interpolator takes ~ 2 minutes
3. writing csv takes around 32.5 minutes, ~ 4.7M lines!

'''
