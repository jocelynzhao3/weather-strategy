from server import SolarInterpolator
import socket
import pickle
from datetime import datetime
from scipy.interpolate import LinearNDInterpolator  #likely still need this

pickle_file_path = 'interp_func.pickle'

def receive_func_from_server():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 8888))

    received_data = b''  # Initialize an empty byte string to store received data
    buffer_size = 1024   # Set a smaller buffer size

    # Loop to receive data until no more data is available
    while True:
        chunk = client.recv(buffer_size)  # Receive a chunk of data
        if not chunk:
            break  # Break the loop when no more data is received
        received_data += chunk  # Append the received chunk to the data buffer

    # Deserialize the function
    received_function = pickle.loads(received_data)

    # Save the received function to a pickle file
    try:
        with open(pickle_file_path, 'wb') as file:
            pickle.dump(received_function, file)
        print(f"Function saved to '{pickle_file_path}'")
    except FileNotFoundError:
        print(f"Error: File '{pickle_file_path}' not found.")

    client.close()  # Close the socket


def interpolate(lats, lons, datetimes, update_func=False): #could also be timestamps
    '''
    lists should all be the same length
    lats: list of floats
    lons: list of floats
    datetimes: list of datetime objects
    update_func: optional bool to regenerate interpolation function

    return list of corresponding interpolated radiances
    '''
    timestamps = []
    for datetime in datetimes:
        timestamps.append(datetime.timestamp()//3600)  #seconds into hours

    if update_func:
        interp = receive_func_from_server()   #store stuff into a pickle file

    try:
        with open(pickle_file_path, 'rb') as file:
            loaded_function = pickle.load(file)
    except FileNotFoundError:
        print(f"Error: File '{pickle_file_path}' not found, set update_func as True!")
        return None

    # need to save interp function
    requested_rads = []
    for i in range(len(lats)):
        requested_rads.append(loaded_function(lats[i], lons[i], timestamps[i]))

    return requested_rads


if __name__ == "__main__":

    datetime_list = [datetime(2024, 3, 21, 18, 56, 19, 273221),
                     datetime(2024, 3, 22, 18, 56, 19, 273221),
                     datetime(2024, 3, 23, 18, 56, 19, 273221),
                     datetime(2024, 3, 24, 18, 56, 19, 273221)]

    timestamps = []
    for datetime in datetime_list:
        timestamps.append(datetime.timestamp()//3600)  #seconds into hours

    print(timestamps)
    pass

'''
client notes:
1. will have interp function stored as pickle on local
2. don't forget to add some no-internet intepolation funcs as well
'''
