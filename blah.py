from scipy.interpolate import LinearNDInterpolator
import numpy as np

class InterpolatorWithWeights(LinearNDInterpolator):
    def __call__(self, *args):
        result = super().__call__(*args)
        # Calculate weights
        weights = self._calc_weights(*args)
        return result, weights

    def _calc_weights(self, *args):
        # Calculate weights based on the distance from the test point to the vertices of the simplex
        distances = self._do_evaluate(self.points, *args)
        return 1 / np.sum(distances)

# Sample data
lat_list = [40.8, 40.7, 41.0, 41.8]
lon_list = [-98.3, -99.1, -100.4, -103.7]
times = [1, 1, 2, 3]
rads = [30, 40, 20, 10]

# Creating 3D linear interpolation function
interp_func = InterpolatorWithWeights(list(zip(lat_list, lon_list, times)), rads)

# Test point for interpolation
test_lat = 41.1
test_lon = -100.0
test_time = 2

# Interpolate at the test point and get the weights
interpolated_rad, weights = interp_func(test_lat, test_lon, test_time)  #weights give issue
print("Interpolated Radiance:", interpolated_rad)
print("Weights:", weights)
