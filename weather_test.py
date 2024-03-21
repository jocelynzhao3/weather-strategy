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
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Next steps:
# clean up print statements?
# how to get stuff into MIT SEVT github?
# try a server-client with another machine

class SolarInterpolator:

    def __init__(self, input_coordinate_csv, output_radiance_csv, start_hour, start_day, start_month, start_year=2024):
        '''
        Param:
        input and output file path strings
        Starting datetime values (whole ints - round any decimals)
        '''

        self.input_file_path = input_coordinate_csv   #  "2022_C_tester.csv"
        self.output_file_path = output_radiance_csv   #  "final_radiance.csv"
        self.start_hour = start_hour
        self.start_day = start_day
        self.start_month = start_month
        self.start_year = start_year


    def clear_sky_radiance(self, lat, lon, elev, year, month, day, hour, minute):
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

    def adj_radiance(self, radiance, cloud_cover):
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

    def find_item(self, csv_file, target_item):
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

    def find_radiance(self, lat, lon, elev, year, month, day, hour, minute=0):
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
        clear_radiance = self.clear_sky_radiance(lat, lon, elev, year, month, day, hour, minute)
        year = str(year)
        month = str(month)
        day = str(day)
        hour = str(hour)
        input_key = year.zfill(2) + "-" + month.zfill(2) + "-" + day.zfill(2) + "T" + hour.zfill(2)

        cloud_cover = self.find_item("local_cloud_cover.csv", input_key)
        if cloud_cover != None:  #datetime was found
            cloud_cover = float(self.find_item("local_cloud_cover.csv", input_key))
            return self.adj_radiance(clear_radiance, cloud_cover)
        else:
            # print("This time is unavaliable")    #may be asked to interpolate here
            return "This time is unavaliable"  #means that given the constant datetime in the 2.5*2.5 km square, no cloud cover data
            # should not matter if we interpolate over all avaliable hours of the day
            # return None


    ######## The code below takes 1 csv and returns radiance for every point for ONE specified datetime and writes to csv ########

    def one_time_csv(self, year= 2024, month= 2, day= 18, hour=12):
        '''
        Input csv to use and time
        '''
        file_path=self.input_file_path
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
                rad = self.find_radiance(lat, lon, elev, year, month, day, hour, minute=0)  # may be a string
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
            writer = csv.writer(file) # Create a CSV writer object
            writer.writerow(labels)  # Write the header

            # Write the data rows
            writer.writerows(rad_list)   #CHANGE THIS - SEEMS INEFFICIENT

        print(f"CSV file '{radiance_csv_path}' created successfully.")

    ######## The code below takes 1 csv and returns radiance for EVERY datetime on cloud csv and writes to new csv ########

    def write_all_to_csv(self):
        '''
        Writes lat, lon, hours_since_start, radiance data from input_file_path to out_file_path
        Returns nothing
        '''
        file_path = self.input_file_path
        cloud_path = "local_cloud_cover.csv"
        final_csv = self.output_file_path   #we will interpolate on this csv, "final_radiance.csv"

        # Specify the column headers
        final_column_headers = ['Lat', 'Lon', 'Hours since start', 'Radiance']  #DEFINE START

        # Writing to CSV file
        with open(final_csv, mode='w', newline='') as file:
            csv_writer = csv.writer(file)      # Create a CSV writer object
            csv_writer.writerow(final_column_headers)         # Write the column headers in the first line

        print(f'CSV file "{final_csv}" inital creation.')

        data_row=[]

        year = str(self.start_year)
        month = str(self.start_month)
        day = str(self.start_day)
        hour = str(self.start_hour)
        start_time_string = year + "-" + month.zfill(2) + "-" + day.zfill(2) + " " + hour.zfill(2) + ":00:00"

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

                        given_time_string = my_datetime[:10] + " " + my_datetime[11:] + ":00:00"
                        hours_since_start = self.hours_between_dates(start_time_string, given_time_string)

                        # calculate radiance - clear_sky_radiance and adj_radiance may differ in units (panel power vs solar radiance) - hopefully general trend is ok
                        clear_radiance = self.clear_sky_radiance(lat, lon, elev, year, month, day, hour, minute=0)
                        cloud_cover = float(cloud_cover)
                        final_radiance = self.adj_radiance(clear_radiance, cloud_cover)   #float or numpy float

                        # write data into final csv
                        data_row = [lat, lon, hours_since_start, final_radiance]
                        with open(final_csv, 'a', newline='') as final_file:   # I choose to open/close/reopen final_csv because it gets very large
                            final_csv_writer = csv.writer(final_file)
                            final_csv_writer.writerow(data_row)
        b = time.time()

        print(f'CSV file "{final_csv}" completed.')
        print(f"Time to run: {b-a} seconds.")

    def make_solar_interpolator(self):
        '''
        Write docstring pls, define HOURS_SINCE_START, keep print statements?
        Option to update csv we use - may be useful as race gets shorter or hours have passed and
        we can get mroe accurate weather data

        Returns nothing
        '''
        # Read CSV file
        csv_file_path = self.output_file_path
        data = pd.read_csv(csv_file_path)

        # Extract every nth row of data, can be changed
        data_subset = data.iloc[::10, :]  # the larger to value, to faster and potentially more inaccurate
        self.points = data_subset.iloc[:, :3].values
        self.output_values = data_subset.iloc[:, 3].values
        b = time.time()
        # Create the LinearNDInterpolator
        self.interp = LinearNDInterpolator(self.points, self.output_values) # self.interp must be made BEFORE get_solar_interpolator
        c = time.time()
        print("Interp time: " + str(c-b))

    def graph_interpolation(self):
        '''
        plots and shows graph
        return nothing
        '''
        csv_file_path = self.output_file_path
        data = pd.read_csv(csv_file_path)

        # Extract every nth row of data, can be changed
        data_subset = data.iloc[::10, :]  # the larger to value, to faster and potentially more inaccurate
        self.points = data_subset.iloc[:, :3].values
        self.output_values = data_subset.iloc[:, 3].values

        fig = plt.figure()           # Create a 3D scatter plot
        ax = fig.add_subplot(111, projection='3d')

        # Scatter plot of the original data points
        scatter = ax.scatter(self.points[:, 0], self.points[:, 1], self.points[:, 2], c=self.output_values, cmap='viridis', marker='o')

        # Set labels and title
        ax.set_xlabel('Lat')
        ax.set_ylabel('Lon')
        ax.set_zlabel('Hours from start')
        ax.set_title('Solar slice of cake')

        cbar = fig.colorbar(scatter, ax=ax, orientation='vertical', label='Output Values')         # Add a colorbar
        plt.show()

    def hours_between_dates(self, date1, date2):
        '''
        return number of hours between 2 dates, as an whole int
        '''
        date1 = datetime.strptime(date1, '%Y-%m-%d %H:%M:%S')         # Convert string dates to datetime objects
        date2 = datetime.strptime(date2, '%Y-%m-%d %H:%M:%S')

        time_difference = date2 - date1          # Calculate the time difference
        hours = round(time_difference.total_seconds() / 3600)         # Extract the total number of hours
        return hours

    def get_solar_interpolator(self, lat, lon, hour_since_start):
        '''
        Given target lat, lon, hours_since_start, return target interp value
        Option to update_interpolator - make new interpolator if we bring in updated data - IDK if this is needed????
        '''

        point_to_interpolate = [lat, lon, hour_since_start]   # Define the point to interpolate
        c = time.time()
        interpolated_value = self.interp(point_to_interpolate)  # Perform linear interpolation
        d = time.time()
        print("time to interpolate one point: " + str(d-c))

        return interpolated_value

    def interpolate_radiance(self, lats, lons, hours_since_start, write_csv=True):
        '''
        MAIN FUNCTION
        Input: list of lats, lon, hours_since_start with corresponding with index and all of the same length
                make_csv bool, can skip remaking csv if there would be not signifigant changes/save time
        Return: 1-d list of radiances with coressponding index, again same length
        IDEA: HAVE USER SPECIFY START TIME!! (modify write_all_to_csv as needed)
        '''
        if len(lats) != len(lons) or len(lons) != len(hours_since_start):
            print("Unequal length not permitted")
            return None
        if write_csv:
            self.write_all_to_csv()

        self.make_solar_interpolator()
        radiance_list = []  # length equal
        for i in range(len(lats)):
            radiance_list.extend(self.get_solar_interpolator(lats[i], lons[i], hours_since_start[i]))
        return radiance_list


if __name__ == "__main__":
    lat = 40.88278
    lon = -98.37418
    hours_since_start = 20

    # Creating an instance of the class and providing values for initialization
    solar_interp_instance = SolarInterpolator("2022_C_tester.csv", "final_radiance.csv", 15, 24, 2)
    # solar_interp_instance.write_all_to_csv()
    # solar_interp_instance.make_solar_interpolator()
    # # one lat, lon, time:
    # value = solar_interp_instance.get_solar_interpolator(lat, lon, hours_since_start)
    # print("Interpolated value: " + str(value))

    print(solar_interp_instance.clear_sky_radiance(lat, lon, 0, 2024, 3, 3, 16, 0))
    print(solar_interp_instance.clear_sky_radiance(lat, lon, 200, 2024, 3, 3, 16, 0))  #elevation kinda matters



'''
Many potential/current bugs - esp for write_all_to_csv:
1. server must be OPENED BEFORE anything runs (maybe client too?) - activate conda, python weather_server.py, etc.
2. server must close before used again (how to open server when needed?)
3. How to catch errors.....
4. We update the cloud csv when we update lat/lon, not when we update time!! (crude fix is the make cloud cover a far away point,
then plug in desired point and current cloud data will update)
5. Sometimes the hours_from_start returns a ridiculous number (account for month is tricky),
therefore it is best to run this at the beginning/middle of a month :)

Next steps:
1. This may be very very very inaccurate - check up on that

Note: this is a client-side function (for now)
'''
