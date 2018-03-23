import sys
sys.path.append('../..')
from SALib.analyze import fast
from SALib.sample import fast_sampler
from tinamit.Calib.SA_algorithms import soil_class
from tinamit.Calib import gaby_simulation as GS
from tinamit.Calib.SA_algorithms import parameters_sa as P
import time
import numpy as np
import json

# sampling number N
N = 66
# Sample size N > 4M^2 is required. M=4 by default. N = 4*(4)^2= 64, N = 66 > 64)

# number of parameters p_n
p_n = len(P.parameters)
# polygon number poly_n
poly_n = 215

# Read the parameter range file and generate samples, single probem_tinamit
problem_t = {
    'num_vars': p_n,
    'names': P.parameters,
    'groups': None
}

# 215 problems_tinamit,bounds are different with regards to polygons
problems_t = []  # 215 problems
for i in range(poly_n):
    problems_t.append({'num_vars': problem_t['num_vars'],
                       'names': problem_t['names'],
                       'bounds': soil_class.soil_class[str(soil_class.p_soil_class[i])]})
    # print(problems_t[i])


# sampling number = 66 * n_parameters
parameters_set = []
for p_s in problems_t:
    #print(fast_sampler.sample(p_s, N))
    parameters_set.append(fast_sampler.sample(p_s, N)) # p_s = 215; N = 66
# parameters_set.append(fast_sampler.sample(p_s, N)) format is 215*Ns*n_parameters (Ns = N * n_parameters)

# switch format to Ns*n_parameters*215 (to match Tinamit)
sampling_parameters_set = []
for i in range(N*p_n):
    sampling = []
    for j in range(p_n):
        parameters = []
        for k in range(poly_n):
            parameters.append(parameters_set[k][i][j])
        sampling.append(parameters)
    sampling_parameters_set.append(sampling)

# initialization
# start simulation i=index, outer layer is Ns (inner is 215), take out the Ns layer, therefore n_parameter*215
# to substite the old (n_parameters * 215)
evals = [] # Ns × 215
start_time = time.time() # return current time for recoding current runtime

# SIMULATION (if uses ALREADY data, comment this)
# after each run of Tinamit, write the results into the 'Simulation.out', 'as f' -->Instance of operating file.
worked = {x: [] for x in P.parameters}
bad = {x: [] for x in P.parameters}
with open('D:\\Thesis\\pythonProject\\Tinamit\\tinamit\\Calib\\SA_algorithms\\simulation.out', 'w') as f:
    for i, set_ in enumerate(sampling_parameters_set):
        dict_set = {x: set_[i] for i, x in enumerate(P.parameters)}
        try:
            result = GS.simulation(dict_set)
            for x in worked:
                worked[x].append(dict_set[x])
        except ChildProcessError:
            for x in bad:
                bad[x].append(dict_set[x])
            continue
        evals.append(result)
        print('Sampling ', i, ' ', result)
        print("--- %s seconds ---" % (time.time() - start_time))
        print(result.size)
        print(result.shape)
        #print(len())
        f.write(json.dumps(result.tolist()) + '\n')
        f.flush() # in time writing
f.close()

print("--- %s total seconds ---" % (time.time() - start_time))

import matplotlib.pyplot as dib

for x in P.parameters:

    dib.clf()

    min_poly = [np.min(v) for v in worked[x]]
    max_poly = [np.max(v) for v in worked[x]]
    dib.plot(min_poly, label='Good, minimum')
    dib.plot(max_poly, label='Good, maximum')

    min_poly_bad = [np.min(v) for v in bad[x]]
    max_poly_bad = [np.max(v) for v in bad[x]]
    dib.plot(min_poly_bad, label='Bad, minimum')
    dib.plot(max_poly_bad, label='Bad, maximum')
    dib.legend()
    dib.title(x)
    dib.show()

# IF ALREADY had simulation data, run here
# if have existed simulation data, just for evaluation
# evals = []  # Ns × 215
# with open('D:\\Thesis\\pythonProject\\Tinamit\\tinamit\\Calib\\SA_algorithms\\previous runs\\7timestep_simulation - Copy.out', 'r') as fr:
#     for line in fr:
#         evals.append(json.loads(line))
#         # print(json.loads(line)) # everything in the file is 'str' type --> 'dict'
# fr.close()

# change evals to 215 × Ns
print(len(evals))
print(len(evals[0]))
evals_transpose = np.asarray(evals).transpose()
print(evals_transpose.size)
# print(evals_transpose)
# evals_transpose = evals_transpose.tolist()

# SA_FAST: PORCESS & WRITE, process first and write the timestep data into the file
# write the results into the 'sensitivity.out'
# r+ --> write and read
with open('D:\\Thesis\\pythonProject\\Tinamit\\tinamit\\Calib\\SA_algorithms\\sensitivity.out', 'w') as f0,\
        open('D:\\Thesis\\pythonProject\\Tinamit\\tinamit\\Calib\\SA_algorithms\\max_sensitivity.out', 'w') as f1:
    for j, duration in enumerate(evals_transpose):
        if j == 0:
            continue
        f1.write('\nThis is the duration {}: \n\n'.format(j))
        f1.flush()
        for i, p in enumerate(problems_t):
            Si = fast.analyze(p, duration[i], print_to_console=True)

            S1_list = Si['S1']
            St_list = Si['ST']
            #print('Max',  P.parameters[np.argmax(S1_list)])
            print(P.parameters[S1_list.index(max(S1_list))])
            print(P.parameters[St_list.index(max(St_list))])
            f1.write('Sensitivity analysis in polygon {} \n'.format(i))
            f1.write('Parameter with max S1: ({} -> {}), '.format(P.parameters[S1_list.index(max(S1_list))], max(S1_list)))
            f1.write('Parameter with max ST: ({} -> {}) \n'.format(P.parameters[St_list.index(max(St_list))], max(St_list)))

            f1.flush()
            #S_T.append(Si)
            f0.write(json.dumps(Si) + '\n')
            f0.flush()
f0.close()
f1.close()

# SA: get the result from BF and run SA (SA on the last one value)
# with open('D:\\Thesis\\pythonProject\\Tinamit\\tinamit\\Calib\\SA_algorithms\\sensitivity.out', 'w') as f0, \
#         open('D:\\Thesis\\pythonProject\\Tinamit\\tinamit\\Calib\\SA_algorithms\\max_sensitivity.out', 'w') as f1:
#     f1.write('\nThis is the duration 1: \n\n')
#     f1.flush()
#     for i, p in enumerate(problems_t):
#         Si = fast.analyze(p, evals_transpose[i], print_to_console=True)
#
#         S1_list = Si['S1']
#         St_list = Si['ST']
#         # print('Max',  P.parameters[np.argmax(S1_list)])
#         print(P.parameters[S1_list.index(max(S1_list))])
#         print(P.parameters[St_list.index(max(St_list))])
#         f1.write('Sensitivity analysis in polygon {} \n'.format(i))
#         f1.write('Parameter with max S1: ({} -> {}), '.format(P.parameters[S1_list.index(max(S1_list))], max(S1_list)))
#         f1.write('Parameter with max ST: ({} -> {}) \n'.format(P.parameters[St_list.index(max(St_list))], max(St_list)))
#
#         f1.flush()
#         # S_T.append(Si)
#         f0.write(json.dumps(Si) + '\n')
#         f0.flush()
# f0.close()
# f1.close()
