import sys

sys.path.append('../..')
from tinamit.Calib.ej import soil_class as SC
from tinamit.Calib import gaby_simulation as GS
from tinamit.Calib.SA_algorithms import parameters_sa as P
import time
import numpy as np
import json
from SALib.analyze import sobol
from SALib.sample import saltelli


class SobolSa:

    def __init__(self, config, name):
        self.n_poly = config[0]
        self.n_sampling = config[1]
        self.n_paras = config[2]
        self.name = name

    def problems_setup(self):
        '''

        :param n_sampling: # sampling number N
        :param n_parameters: # number of parameters p_n
        :param n_poly: # polygon number poly_n
        :return:
        '''

        def set_bounds_4_paras(poly_id):
            bounds = []
            for para in P.parameters:
                if para.startswith('Kaq'):
                    if para.endswith('1'):
                        bounds.append(SC.get_p_soil_class(poly_id, 0)['Kaq'])
                    if para.endswith('2'):
                        bounds.append(SC.get_p_soil_class(poly_id, 1)['Kaq'])
                    if para.endswith('3'):
                        bounds.append(SC.get_p_soil_class(poly_id, 2)['Kaq'])
                    if para.endswith('4'):
                        bounds.append(SC.get_p_soil_class(poly_id, 3)['Kaq'])
                else:
                    bounds.append(SC.get_p_soil_class(poly_id)[para])
            return bounds

        # 215 problems_tinamit,bounds are different with regards to polygons
        problems_t = []  # 215 problems
        for i in range(self.n_poly):
            problems_t.append({'num_vars': self.n_paras,
                               'names': P.parameters,
                               'bounds': set_bounds_4_paras(i)})
            # print()
        return problems_t

    def sampling(self, problems_t=[]):
        parameters_set = []
        with open('D:\\Thesis\\pythonProject\\Tinamit\\tinamit\\Calib\\SA_algorithms\\sobol_parameters_{}.out'.format(
                self.name), 'w') as f1:
            for problem in problems_t:
                # print(fast_sampler.sample(p_s, N)) (num_level--> P level grid)
                param_values = saltelli.sample(problem, self.n_sampling, calc_second_order=True)
                # print(param_values.shape)
                parameters_set.append(param_values)  # N*9*8
                f1.write(json.dumps(param_values.tolist()))
                f1.flush()
        # parameters_set.append(fast_sampler.sample(p_s, N)) format is 215*Ns*n_parameters (Ns = N * n_parameters)
        f1.close()
        return parameters_set

    def simulation(self, parameters_set=[]):
        def plotting():
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

        # initialization
        # start simulation i=index, outer layer is Ns (inner is 215), take out the Ns layer, therefore n_parameter*215
        # to substite the old (n_parameters * 215)

        # switch format to Ns*n_parameters*215 (to match Tinamit)
        # Ns = len(parameters_set)
        sampling_parameters_set = []
        for i in range(len(parameters_set[0])):
            sampling = []
            for j in range(self.n_paras):
                parameters = []
                for k in range(self.n_poly):
                    parameters.append(parameters_set[k][i][j])
                sampling.append(parameters)
            sampling_parameters_set.append(sampling)

        evals = []  # Ns × 215
        start_time = time.time()  # return current time for recoding current runtime

        # SIMULATION (if uses ALREADY data, comment this)
        # after each run of Tinamit, write the results into the 'Simulation.out', 'as f' -->Instance of operating file.
        worked = {x: [] for x in P.parameters}
        bad = {x: [] for x in P.parameters}
        with open('D:\\Thesis\\pythonProject\\Tinamit\\tinamit\\Calib\\SA_algorithms\\sobol_simulation_{}.out'.format(
                self.name), 'w') as f:
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
                # print(len())
                f.write(json.dumps(result.tolist()) + '\n')
                f.flush()  # in time writing

        f.close()

        # plotting()
        print("--- %s total seconds ---" % (time.time() - start_time))
        return evals

    def analyze(self, evals=[], parameters_set=[], problems_t=[]):
        # SA_FAST: PORCESS & WRITE, process first and write the timestep data into the file
        # write the results into the 'sensitivity.out'
        # r+ --> write and read
        evals_transpose = np.asarray(evals).transpose()
        with open('D:\\Thesis\\pythonProject\\Tinamit\\tinamit\\Calib\\SA_algorithms\\sobol_sensitivity_{}.out'.format(
                self.name),
                'w') as f0, \
                open(
                    'D:\\Thesis\\pythonProject\\Tinamit\\tinamit\\Calib\\SA_algorithms\\sobol_max_sensitivity_{}.out'.format(
                        self.name),
                    'w') as f1:
            for j, duration in enumerate(evals_transpose):
                if j == 0:
                    continue
                f1.write('\nThis is the duration {}: \n\n'.format(j))
                f1.flush()
                for i, problem in enumerate(problems_t):
                    # Si = fast.analyze(p, duration[i], print_to_console=True)
                    # print(len(parameters_set[i]))
                    # para_set = np.asarray([parameters_set[i][x] for x in range(522)])
                    # evals_set = np.asarray([duration[i][x] for x in range(522)])
                    Si = sobol.analyze(problem, duration[i], calc_second_order=True, conf_level=0.95,
                                       print_to_console=True)
                    # print(Si)

                    # fig, (ax1, ax2) = plt.subplots(1, 2)
                    # horizontal_bar_plot(ax1, Si, {}, sortby='mu_star', unit=r"tCO$_2$/year")
                    # covariance_plot(ax2, Si, {}, unit=r"tCO$_2$/year")
                    #
                    # fig2 = plt.figure()
                    # sample_histograms(fig2, param_values, problem, {'color': 'y'})
                    # plt.show()
                    f0.write(('{}\n').format(Si))
                    f0.flush()
        f0.close()
        f1.close()

    def load_data_from_file(self):
        # IF ALREADY had simulation data, run here
        # if have existed simulation data, just for evaluation
        evals = []  # Ns × 215
        # with open('D:\\Thesis\\pythonProject\\Tinamit\\tinamit\\Calib\\SA_algorithms\\previous runs\\7timestep_simulation - Copy.out', 'r') as fr:
        with open('D:\\Thesis\\pythonProject\\Tinamit\\tinamit\\Calib\\SA_algorithms\\sobol_simulation.out',
                  'r') as fr:
            for line in fr:
                evals.append(json.loads(line))
                # print(json.loads(line)) # everything in the file is 'str' type --> 'dict'
        fr.close()
        return evals


config = [
    [215, 1000, 8]
]

for i, conf in enumerate(config):
    mor = SobolSa(conf, i)
    problems = mor.problems_setup()
    parameters_set = mor.sampling(problems)
    evals = mor.simulation(parameters_set)
    mor.analyze(evals, parameters_set, problems)
