from SALib.sample import saltelli
from SALib.analyze import sobol
from SALib.test_functions import Ishigami
import numpy as np

Y = np.zeros(8)
print(Y)
Y = np.zeros([8])
print([8].__class__)
print(Y)

problem = {
    'num_vars': 3,
    'names': ['x1', 'x2', 'x3'],
    'bounds': [[-np.pi, np.pi]] * 3

}

# Generate samples
param_values = saltelli.sample(problem, 1000)
'''
print(param_values)
print(param_values.__len__())
'''

# sampling method is saltelli -> 1000 sampling 8000 samples
# Run model (example)
Y = Ishigami.evaluate(param_values)

print(Y)
print(Y.__class__)
print(Y.__len__())

# Perform analysis
Si = sobol.analyze(problem, Y, print_to_console=True)
# Returns a dictionary with keys 'S1', 'S1_conf', 'ST', and 'ST_conf'
# (first and total-order indices with bootstrap confidence intervals)

