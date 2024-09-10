# SEVT Weather Infrastructure

There is a weather infrastructure is currently in use!
Keep in mind we can use two APIs:
1. solcast
- server_solcast.py
- server_client.py
- returns irradiance (W/m^2)
- limited API location calls per day
2. weather
- weather_client.py
- weather_server.py
- returns cloud cover (decimal from 0-1)
- unlimited API calls, but final answer may be less accurate

## Install:
- python 3.10
- numpy (array)
- solarpy
- datetime
- time
- scipy.interpolate
- pandas
- json
- requests
- socket
- io
- shapely
- pickle

### Running ```server_solcast.py``` or ```weather_server.py```
- if internet is good, make dataframe on local and skip pickling steps below

1. specify PICKLE_FILE_PATH, location where pandas df is stored
2. within start_server function, specify route_file_name (csv to read from)
3. run the main function and wait for dataframe creation (can be stored by pickling)
4. in terminal, run ```python3 server_solcast.py``` or ```python3 weather_server.py```
5. once updated pickle file is created, run scp command in terminal:
```scp jjz300@athena.dialup.mit.edu:~/GeminiStrategy/strategee/weather/PICKLE_FILE_PATH ~/documents```

- instead of ~/documents, file input location can be somewhere else on local
- I ran this command from local home dir
- will need to input kerb password to scp from my locker (jjz300 in this case, for whoever's locker is being pulled from)


### Using interpolation function
- optimizer will take care of interpolating
- weather only needs to create/store/send a dataframe of raw data

### bugs bugs bugs
- Make sure the plug future unix timestamps, as the APIs forecast into the future but do not look at the present

Solcast bugs:
- 200 OK	A successful response.
- 202 Accepted The request was accepted but does not include any data in the response. Refer to the message returned in the body of the response for more information.
- 400 Bad Request	The request may have included invalid parameters. Refer to the message returned in the body of the response for more information.
- 401 Unauthorized The request did not correctly include a valid API Key. Check the API Key used in the request is correct, active, and properly added to the request using one of the available authentication methods.
- 402 Payment Required You may have exceeded the available transaction limit or the requested endpoint is not available on your current plan.
- 403 Forbidden	The request includes parameter(s) not available at your current subscription level.
- 429 Too Many Requests	The request exceeds the available rate limit at your current subscription level.
- 500 Internal Server Error	An internal error has prevented the request from processing.
