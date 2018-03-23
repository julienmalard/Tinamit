import sys

sys.path.append('../..')

from SALib.analyze import fast
from SALib.sample import fast_sampler
from SALib.test_functions import Ishigami
from SALib.util import read_param_file
from tinamit.Calib.SA_algorithms import soil_class
from tinamit.Calib import gaby_simulation as GS
from tinamit.Calib.SA_algorithms import parameters_sa as P
import time
import numpy as np
from tinamit.Calib import read_xl
import json

# sampling number N
N = 66
# Sample size N > 4M^2 is required. M=4 by default. N = 4*(4)^2= 64, N = 66 > 64)

# number of parameters p_n
p_n = len(P.parameters)
# polygon number poly_n
poly_n = 215

# Read the parameter range file and generate samples
problem_t = {
    'num_vars': p_n,
    'names': P.parameters,
    'groups': None
}

problems_t = [] # 215 problems
for i in range(poly_n):
    problems_t.append({'num_vars': problem_t['num_vars'],
                       'names': problem_t['names'],
                       'bounds': soil_class.soil_class[str(soil_class.p_soil_class[i])]})
    #print(problems_t[i])

# sampling number = 66 * 11
parameters_set = []
for p_s in problems_t:
    #print(fast_sampler.sample(p_s, N))
    parameters_set.append(fast_sampler.sample(p_s, N))
#parameters_set.append(fast_sampler.sample(p_s, N)) format is 215*Ns*n_parameters (Ns = N * n_parameters)

# print(len(parameters_set))
# print(len(parameters_set[214]))
# print(len(parameters_set[0][724]))
# print(parameters_set[0][724])
# print(parameters_set)

sampling_parameters_set = []
for i in range(N*p_n):
    sampling = []
    for j in range(p_n):
        parameters = []
        for k in range(poly_n):
            parameters.append(parameters_set[k][i][j])
        sampling.append(parameters)
    sampling_parameters_set.append(sampling)
# switch format to Ns*n_parameters*215 (to match Tinamit)

# [(4*4^2*11)=726] * 11 * 215

# print(len(sampling_parameters_set))
# print(len(sampling_parameters_set[0]))
# print(len(sampling_parameters_set[0][0]))
# print(sampling_parameters_set[0])
# #print(GS.simulation(sampling_parameters_set[0]))


# start simulation i=index, outer layer is Ns (inner is 215), take out the Ns layer, therefore n_parameter*215
# to substite the old (n_parameters * 215)
evals = [] # Ns × 215
start_time = time.time() # return current time for recoding current runtime

# after each run of Tinamit, write the results into the 'Simulation.out', 'as f' -->Instance of operating file.
with open('D:\\Thesis\\pythonProject\\Tinamit\\tinamit\\Calib\\SA_algorithms\\simulation.out', 'r+') as f:
    for i, set in enumerate(sampling_parameters_set):
        result = GS.simulation(set)
        evals.append(result)
        print('Sampling ', i, ' ', result)
        print("--- %s seconds ---" % (time.time() - start_time))
        f.write(json.dumps(result.tolist()) + '\n')
        f.flush() # in time writing
f.close()

print("--- %s total seconds ---" % (time.time() - start_time))

#read_xl.read_xl_file()
# change evals to 215 × Ns
evals_transpose = np.asarray(evals).transpose()
evals_transpose = evals_transpose.tolist()

# write the results into the 'sensitivity.out'
with open('D:\\Thesis\\pythonProject\\Tinamit\\tinamit\\Calib\\SA_algorithms\\sensitivity.out', 'r+') as f:
    #S_T = []
    for i, p in enumerate(problems_t):
        Si = fast.analyze(p, evals_transpose[i], print_to_console=True)
        #S_T.append(Si)
        f.write(json.dumps(Si) + '\n')
        f.flush()
f.close()

'''
# print(problem['names'])
# print(problem['bounds'])
# print(problem['num_vars'])
# print(problem['groups'])
# print(problem['dists'])

# Generate samples
param_values = fast_sampler.sample(problem, 66)

print(param_values[9])
print(param_values.__len__())

# Run the "model" and save the output in a text file
# This will happen offline for external models
Y = Ishigami.evaluate(param_values)

print(Y)
print(Y.__class__)
print(Y.__len__())

# Perform the sensitivity analysis using the model output
# Specify which column of the output file to analyze (zero-indexed)
Si = fast.analyze(problem, Y, print_to_console=True)
# for key in Si:

# Returns a dictionary with keys 'S1' and 'ST'
# e.g. Si['S1'] contains the first-order index for each parameter, in the
# same order as the parameter file
# S1->(Di/D) D=variance// Si,j->(Di,j/D)
'''

