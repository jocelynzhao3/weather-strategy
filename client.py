import socket
import pickle
from scipy.interpolate import LinearNDInterpolator  #likely still need this


# IDK if you still need this - pickle for interp function is likely short
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
    client.send(data.encode('utf-8'))   # what is data> should be nothing

    json_response = receive_all_data(client)

    response_dict = json.loads(json_response) #load in pickle

    client.close()

    with open('interpolator.pkl', 'rb') as f:
        interpolator_loaded = pickle.load(f)


def interpolate(lats, lons, datetimes?, update_func=False): # list of datetimes can also be list of timestamps
    '''
    lists should all be the same length

    return list of corresponding interpolated radiances
    '''

    if update_func or no interpolator:
        receive_json_from_server()
    else:
        somehow grab interp function

    with open('interpolator.pkl', 'rb') as f:
        interpolator_loaded = pickle.load(f)


    requested_rads = []
    for i in range(len(lats)):
        requested_rads.append(requested_rads(lats[i], lons[i], timestamps[i]))

    return requested_rads
