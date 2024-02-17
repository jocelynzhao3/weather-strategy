print("welcome to interpolation practice!")

from scipy.interpolate import LinearNDInterpolator
import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
# rng = np.random.default_rng()
# x = rng.random(10) - 0.5
# y = rng.random(10) - 0.5
# z = np.hypot(x, y)
# X = np.linspace(min(x), max(x))
# Y = np.linspace(min(y), max(y))
# X, Y = np.meshgrid(X, Y)  # 2D grid for interpolation
# print(len(list(zip(x, y))))
# print(len(z))
# interp = LinearNDInterpolator(list(zip(x, y)), z)
# Z = interp(X, Y)
# plt.pcolormesh(X, Y, Z, shading='auto')
# plt.plot(x, y, "ok", label="input point")
# plt.legend()
# plt.colorbar()
# plt.axis("equal")
# plt.show()

# Example data
points_3d = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 0], [1, 0, 1], [0, 1, 1], [1, 1, 1]])
values_3d = np.array([0, 1, 2, 3, 4, 5, 6, 7])

# Create a LinearNDInterpolator for 3D data
interp_3d = LinearNDInterpolator(points_3d, values_3d)

# Test the interpolation at a new 3D point
new_point_3d = np.array([0.5, 0.5, 0.5])   # will return nan if you have to extrapolate
result_3d = interp_3d(new_point_3d)
print(result_3d)
