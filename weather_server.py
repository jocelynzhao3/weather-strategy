import json
import requests    #set base to conda 3.11.5 to install package
import csv
import socket
from io import StringIO

def fetch_webpage_content(url):
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        return response.json()  # Assume the content is in JSON format
    else:
        print(f"Failed to fetch content. Status code: {response.status_code}")
        return None

def save_json_to_file(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def write_data_to_dict(lat, lon):
    link = "https://api.weather.gov/points/" + str(lat) + "," + str(lon)
    #example: link = "https://api.weather.gov/points/42.36,-71.06"

    json_content = fetch_webpage_content(link)

    if json_content:
        filename = 'weather_points.json'
        save_json_to_file(json_content, filename)
        # print(f"Webpage content saved to {filename}")

    #Step 2: Read just-created json file to get link to sky cover data

    # Assuming you have a JSON file named 'example.json' in the same directory as your Python script
    file_path = 'weather_points.json'

    # Open the file in read mode
    with open(file_path, 'r') as json_file:
        # Load the JSON data into a dictionary
        data_dict = json.load(json_file)

    new_link = data_dict['properties']["forecastGridData"] # link directs you to json with sky cover data

    sky_cover_content = fetch_webpage_content(new_link)

    if sky_cover_content:
        filename = 'sky_cover.json'
        save_json_to_file(sky_cover_content, filename)
        # print(f"Webpage content saved to {filename}")

    #Step 3: Read final json file

    # Assuming you have a JSON file named 'example.json' in the same directory as your Python script
    new_file_path = 'sky_cover.json'

    # Open the file in read mode
    with open(new_file_path, 'r') as json_file:
        # Load the JSON data into a dictionary
        sky_cover_dict = json.load(json_file)

    sky_cover_time_list = sky_cover_dict["properties"]["skyCover"]["values"]
    bounds_list = sky_cover_dict["geometry"]["coordinates"][0]
    # print(bounds_list)
    data = {"bounds" : bounds_list} #write the first line as the bounds

    for i in range(len(sky_cover_time_list)):    # may not need to generate entire dictionary to improve efficiency
        key = sky_cover_dict["properties"]["skyCover"]["values"][i]["validTime"][:13]   #abtract away year
        value = int(sky_cover_dict["properties"]["skyCover"]["values"][i]["value"])/100  #cloud cover as decimal 0.0-1.0
        data[key] = value

    # print("data :" + str(data))
    return data   # data dict



#lat, lon values will be given by the client
lat = 42.36
lon = -71.06
# write_data_to_dict(lat, lon)   #length < 160, find way to send csv to client

# Online code:

def get_response(data):   #make dictionary from lat/lon points
    lat, lon = data.rsplit(", ")
    lat = float(lat)
    lon = float(lon)
    return write_data_to_dict(lat, lon)

def handle_client(client_socket):
    # Receive data from the client (assuming it's a string)
    data = client_socket.recv(1024).decode('utf-8')    #lat, lon
    # print(f"Received data from client: {data}")
    print("Received data from client")

    # Process the received string (You can replace this logic with your specific use case)
    response_dict = get_response(data)
    # print(response_dict)

    # Convert the dictionary to a JSON string
    json_response = json.dumps(response_dict)

    # Send the JSON string to the client
    client_socket.send(json_response.encode('utf-8'))

    # Close the connection
    client_socket.close()
    print("Socket closed")

def start_server():
    # Set up the server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 8888))
    server.listen(1)
    print("Server listening on port 8888...")

    while True:
        # Wait for a connection from the client
        client_socket, client_address = server.accept()
        print(f"Accepted connection from {client_address}")

        # Handle the client in a separate thread
        handle_client(client_socket)

if __name__ == "__main__":
    start_server()
