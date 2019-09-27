
import numpy as np

from eduscripts import normalize_cost

from scipy.io import loadmat
mat = loadmat('course_numeric_info.mat')
stars = mat['stars']
print(np.nanmin(stars))
print(normalize_cost(stars,0))
