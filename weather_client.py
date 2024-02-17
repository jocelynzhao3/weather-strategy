from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import json
import csv
import numpy as np
from numpy import array
from solarpy import solar_panel
from datetime import datetime
import socket

# Please add documentation ASAP (client & server)

def within_bounds(lat, lon, bounds_list):
    '''
    Determines if current (lat, lon) is within cloud_cover bounds (no need to query from server)
    '''
    point = Point(lon, lat)     #bounds list may reverse points
    polygon = Polygon(bounds_list)
    return polygon.contains(point)


def read_first_line(csv_file):
    '''
    The first line of local_cloud_cover contains the lat/lon bounds list
    '''
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        first_line = next(reader, None)[1]  # Use next() to get the first row
    first_line = first_line[2:-2]   #parsing the boundary string into correct format
    bounds_list = first_line.rsplit('], [')
    final = []
    for point in bounds_list:
        lat, lon = point.rsplit(', ')
        final.append([float(lat), float(lon)])
    # print(final)
    return final

# Online Code:

def receive_all_data(client_socket):    #need to split up into chunks as string is too big
    data = b''
    while True:
        chunk = client_socket.recv(1024)
        if not chunk:
            break
        data += chunk
    return data.decode('utf-8')

def receive_json_from_server(data):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 8888))

    # Send the string to the server
    client.send(data.encode('utf-8'))

    json_response = receive_all_data(client)

    response_dict = json.loads(json_response)

    #write dictionary into local csv:
    file_path = "local_cloud_cover.csv"
    with open(file_path, 'w', newline='') as csv_file:
        # Create a CSV writer
        csv_writer = csv.writer(csv_file)

        # Write header (optional)
        # header = ["Key", "Value"]
        # csv_writer.writerow(header)

        # Write data from the dictionary to the CSV file
        for key, value in response_dict.items():
            csv_writer.writerow([key, value])

    # print("Dictionary received from server:")
    # for key, value in response_dict.items():
    #     print(f"{key}: {value}")

    client.close()

def run_this_file(lat, lon):
    csv_file = "local_cloud_cover.csv"
    bounds_list = read_first_line(csv_file)

    if within_bounds(lat, lon, bounds_list):   #current csv contains needed information
        # print("current csv contains info - go ahead and calc radiance")
        pass
    else:
        # Example string to send to the server
        input_string = str(lat) + ", " + str(lon)  #lat, lon
        # print("need server input: " + input_string)

        # Send the string to the server and receive the dictionary response
        receive_json_from_server(input_string)

if __name__ == "__main__":
    # x = find_radiance(42.36, -71.06, 5.8, 2024, 2, 2, 14, minute=0)   #final testing, all other parts should be functions
    # print(x)
    # find_radiance(lat, lon, elev, year, month, day, hour, minute=0)

    #point should be in the US or API may have issues
    lat = float(input("Enter valid latitude: "))
    lon = float(input("Enter valid longitude: "))

    # lat = 42.36
    # lon = -71.06

    csv_file = "local_cloud_cover.csv"
    bounds_list = read_first_line(csv_file)

    if within_bounds(lat, lon, bounds_list):   #current csv contains needed information
        print("current csv contains info - go ahead and calc radiance")
    else:
        # Example string to send to the server
        input_string = str(lat) + ", " + str(lon)  #lat, lon
        print("need server input: " + input_string)

        # Send the string to the server and receive the dictionary response
        receive_json_from_server(input_string)

    # basic functionality works, next step: CALC RADIANCE FOR EACH POINT AND WRITE THIS (MORE USEFUL) DATA INTO CSV
