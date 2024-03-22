from scipy.interpolate import LinearNDInterpolator
import numpy as np
import pickle

lat_list = [40.8, 40.7, 41.0, 41.8]
lon_list = [-98.3, -99.1,-100.4, -103.7]
times = [1, 1, 2, 3]
rads = [30, 40, 20, 10]

points = np.column_stack((lat_list, lon_list, times))

interp_func = LinearNDInterpolator(points, rads)
print(interp_func)
print(interp_func(40.8, -99.1, 1))

serialized_function = pickle.dumps(interp_func)

received_function = pickle.loads(serialized_function)
print(received_function)
print(received_function(40.8, -99.1, 1))
