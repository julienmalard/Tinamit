import sys
import os
from SALib.analyze import fast
from SALib.sample import fast_sampler
from tinamit.Calib.SA_algorithms import soil_class
from tinamit.Calib import gaby_simulation as GS
from tinamit.Calib.SA_algorithms import parameters_sa as P
import time
import numpy as np
import json
from tinamit.Calib.SA_algorithms import soil_class as SC
from matplotlib import pyplot as plt
from tinamit.Geog.Geog import Geografía
from enum import Enum
from scipy import optimize


class FastSa:
    root_path = 'D:\\Thesis\\pythonProject\\Tinamit\\tinamit\\Calib\\SA_algorithms\\Fast'
    #root_path = 'D:\\Gaby\\Tinamit\\tinamit\\Calib\\SA_algorithms'


    def __init__(self, config, name):
        self.n_poly = config[0]
        self.n_sampling = config[1]
        self.n_paras = config[2]
        self.n_season = config[3]
        self.name = name

        Rechna_Doab = Geografía(nombre='Rechna Doab')

        base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Shape_files')
        Rechna_Doab.agregar_frm_regiones(os.path.join(base_dir, 'Internal_Polygon.shp'), col_orden='Polygon_ID')

        Rechna_Doab.agregar_forma(os.path.join(base_dir, 'External_Polygon.shp'), color='#edf4da')
        Rechna_Doab.agregar_forma(os.path.join(base_dir, 'RIVR.shp'), tipo='agua')
        Rechna_Doab.agregar_forma(os.path.join(base_dir, 'Forst_polygon.shp'), tipo='bosque')
        Rechna_Doab.agregar_forma(os.path.join(base_dir, 'CNL_Arc.shp'), tipo='agua', llenar=False)
        Rechna_Doab.agregar_forma(os.path.join(base_dir, 'buildup_Polygon.shp'), tipo='ciudad')
        Rechna_Doab.agregar_forma(os.path.join(base_dir, 'road.shp'), tipo='calle')

        self.Rechna_Doab = Rechna_Doab

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
        with open(os.path.join(self.root_path, 'fast_parameters_{}.out'.format(
            self.name)), 'w') as f1:
            for problem in problems_t:
                # print(fast_sampler.sample(p_s, N)) (num_level--> P level grid)
                param_values = fast_sampler.sample(problem, self.n_sampling)
                # print(param_values.shape)
                parameters_set.append(param_values)  # N*9*8
                f1.write('{}\n'.format(json.dumps(param_values.tolist())))  # json: list --> structurazation
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
        with open(os.path.join(self.root_path, 'Simulation\\fast_simulation_{}.out'.format(self.name)), 'w') as f:
            for i, set_ in enumerate(sampling_parameters_set):
                dict_set = {x: set_[i] for i, x in enumerate(P.parameters)}
                try:
                    result = GS.simulation(dict_set, self.n_season)
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

    def analyze(self, evals=[], problems_t=[]):
        # SA_FAST: PORCESS & WRITE, process first and write the timestep data into the file
        # write the results into the 'sensitivity.out'
        # r+ --> write and read
        duration_all_si = []
        evals_transpose = np.asarray(evals).transpose()
        with open(os.path.join(self.root_path, '\\Simulation\\fast_sensitivity_{}.out'.format(self.name)), 'w') as f0, \
                open(os.path.join(self.root_path, '\\Simulation\\fast_max_sensitivity_{}.out'.format(self.name)), 'w') as f1:
            for j, duration in enumerate(evals_transpose):
                if j == 0:
                    continue
                f1.write('\nThis is the duration {}: \n\n'.format(j))
                f1.flush()
                duration_si = []
                for i, problem in enumerate(problems_t):
                    Si = fast.analyze(problem, duration[i], print_to_console=False)
                    duration_si.append(Si)
                    S1_list = Si['S1']
                    St_list = Si['ST']
                    # print('Max',  P.parameters[np.argmax(S1_list)])
                    # print(P.parameters[S1_list.index(max(S1_list))])
                    # print(P.parameters[St_list.index(max(St_list))])
                    f1.write('Sensitivity analysis in polygon {} \n'.format(i))
                    f1.write(
                        'Parameter with max S1: ({} -> {}), '.format(P.parameters[S1_list.index(max(S1_list))],
                                                                     max(S1_list)))
                    f1.write(
                        'Parameter with max ST: ({} -> {}) \n'.format(P.parameters[St_list.index(max(St_list))],
                                                                      max(St_list)))

                    f1.flush()
                    # S_T.append(Si)
                    f0.write(json.dumps(Si) + '\n')
                    f0.flush()
                duration_all_si.append(duration_si)
        f0.close()
        f1.close()
        return duration_all_si

    def analyze_total_samples(self, evals=[], problems_t=[]):
        '''
        treat all sampling data of polygons as sampling from one problem
        :param evals:
        :param problems_t:
        :return:
        '''
        evals_transpose = np.asarray(evals).transpose()
        # print(evals_transpose.shape)
        # print(evals_transpose[0][0][0])
        durations = []
        for duration in evals_transpose:
            total_samples = []
            for i in range(self.n_paras):
                for j in range(self.n_poly):
                    for k in range(i*100, i * 100 + 100):
                        total_samples.append(duration[j][k])
                    #total_samples.append(duration[j][i * 100:i * 100 + 99])
            durations.append(total_samples)
        durations = np.asanyarray(durations)
        print(durations.shape)
        # print(len(evals))
        # print(len(evals[0]))
        # evals_transpose = np.asarray(evals).transpose()
        with open(os.path.join(self.root_path, 'Simulation\\FAST_sensitivity_{}.out'.format(
                self.name)), 'w') as f0, \
                open(os.path.join(self.root_path, 'Simulation\\FAST_max_sensitivity_{}.out'.format(self.name)),
                    'w') as f1:
            for j, duration in enumerate(durations):
                if j == 0:
                    continue
                f1.write('\nThis is the duration {}: \n\n'.format(j))
                f1.flush()

                Si = fast.analyze(problems_t[0], duration, print_to_console=False)

                S1_list = Si['S1']
                St_list = Si['ST']  # print('Max',  P.parameters[np.argmax(S1_list)])
                # print(P.parameters[S1_list.index(max(S1_list))])
                # print(P.parameters[St_list.index(max(St_list))])
                # f1.write(
                #     'Parameter with max S1: ({} -> {}), '.format(P.parameters[S1_list.index(max(S1_list))],
                #                                                  max(S1_list)))
                f1.write(
                    'Parameter with max ST: ({} -> {}) \n'.format(P.parameters[St_list.index(max(St_list))],
                                                                  max(St_list)))

                f1.flush()
                # S_T.append(Si)
                f0.write(json.dumps(Si) + '\n')
                f0.flush()
        f0.close()
        f1.close()
        return

    @staticmethod
    def load_data_from_file(self, filename):
        # IF ALREADY had simulation data, run here
        # if have existed simulation data, just for evaluation
        evals = []  # Ns × 215
        # with open('D:\\Thesis\\pythonProject\\Tinamit\\tinamit\\Calib\\SA_algorithms\\previous runs\\7timestep_simulation - Copy.out', 'r') as fr:
        with open(filename, 'r') as fr:
            for line in fr:
                evals.append(json.loads(line))
                # print(json.loads(line)) # everything in the file is 'str' type --> 'dict'
        fr.close()
        return evals

    def load_sensitivity_data(self, filename):
        duration_sensitivities = []
        with open(filename, 'r') as f:
            content = f.readlines()
            for season in range(self.n_season - 1):
                duration = []
                for poly in range(self.n_poly):
                    duration.append(json.loads(content[season*215 + poly]))
                duration_sensitivities.append(duration)
        return duration_sensitivities


    def plot_SI(self, ploy_id, duration_all_si, savepath):
        X = []
        S1 = []
        ST = []
        name = ['Ptq',
              'Ptr',
              'Kaq1', #need to consider all four
              'Kaq2',
              'Kaq3',
              'Kaq4',
               'Peq',
               'Pex']

        for i, duration in enumerate(duration_all_si):
            if i == len(duration_all_si) - 1:
                continue
            # for s1 in duration[ploy_id]['S1']:
            #     X.append(i + 1)
            #     S1.append(s1)
            for st in duration[ploy_id]['ST']:
                ST.append(st)

        plt.figure(ploy_id)
        plt.suptitle('polygon number = {}'.format(ploy_id + 1))
        plt.subplot(211)
        plt.ylabel('S1')
        ax = plt.gca()
        ax.scatter(X, S1)

        for j in range(len(duration_all_si)):
            if j == len(duration_all_si) - 1:
                continue
            for i, txt in enumerate(name):
                ax.annotate(txt, (X[j*self.n_paras + i], S1[j*self.n_paras + i]))

        plt.subplot(212)
        ax2 = plt.gca()
        ax2.scatter(X, ST)

        for j in range(len(duration_all_si)):
            if j == len(duration_all_si) - 1:
                continue
            for i, txt in enumerate(name):
                ax2.annotate(txt, (X[j * self.n_paras + i], ST[j * self.n_paras + i]))

        plt.xlabel('Season')
        plt.ylabel('ST')
        plt.savefig('{}/{}.png'.format(savepath, ploy_id + 1))
        plt.close(ploy_id)

    def plot_map(self, duration, season, sensitivity_order):
        if not isinstance(season, int):
            return 'parameter type error!'
        if sensitivity_order == SensitivityOrder.S1:
            sensitivity_order = 'S1'
        elif sensitivity_order == SensitivityOrder.ST:
            sensitivity_order = 'ST'
        else:
            return 'Sensitivity order error!'

        values = []
        # parameters_2_value_dict = [
        #
        # ]
        for poly in duration:
            # the index of list is set as the index of parameters
            parameter_index = poly[sensitivity_order].index(max(poly[sensitivity_order]))
            #print(parameter_index)
            #print('len', len(poly['mu_star']))

            values.append(parameter_index)
            #print(parameter_index)
        #print(np.asarray(values))

        nombre_archivo = os.path.join(self.root_path, 'Plot_Map\\fast-{}-season-{}'.format(sensitivity_order, season + 1))
        var = 'FAST \n Most sensitive parameters in each polygon in season {}: {}'.format(season + 1, sensitivity_order)
        unid = 'Parameter'
        colores = None
        # this is to calculate the range for the array--values==
        #escala = np.min(values), np.max(values)
        escala = np.int32(0), np.int32(7)

        geog = self.Rechna_Doab
        geog.dibujar(archivo=nombre_archivo, valores=values, título=var, unidades=unid,
                     escala_num=escala, categs=('Ptq', 'Ptr', 'Kaq1', 'Kaq2', 'Kaq3', 'Kaq4', 'Peq', 'Pex'),
                     colores=['#302311', '#eeff66', '##FFCC66', '#00CC66', '#66ecff', '#6669ff', '#e766ff', '#ff6685'])

        # geog.dibujar_sensibilidad(archivo=nombre_archivo, valores=values, título=var, unidades=unid,
        #                           colores=colores, escala=escala)

    def plot_map_4_parameter(self, duration, parameter_n, season_n, sensitivity_order):

        if sensitivity_order == SensitivityOrder.S1:
            sensitivity_order = 'S1'
        elif sensitivity_order == SensitivityOrder.ST:
            sensitivity_order = 'ST'
        else:
            print('Sensitivity order error!')
            return

        name = ['Ptq',
                'Ptr',
                'Kaq1',  # need to consider all four
                'Kaq2',
                'Kaq3',
                'Kaq4',
                'Peq',
                'Pex']
        if not isinstance(parameter_n, int) \
                or not isinstance(season_n, int):
            return 'parameter type error!'
        values = []
        # parameters_2_value_dict = [
        #
        # ]
        mu_star_in_polys = []
        for poly in duration:
            mu_stars = []
            for value in poly[sensitivity_order]:
                mu_stars.append(value)
            mu_star_in_polys.append(mu_stars)

        mu_star_in_polys = np.asarray(mu_star_in_polys).transpose()
        values = mu_star_in_polys[parameter_n]
       # print(values)

        nombre_archivo = os.path.join(self.root_path, 'plot_map_4_parameter\\Fast-{}-parameter-{}-season-{}'.format(sensitivity_order, parameter_n + 1, season_n + 1))
        var = "FAST \n Sensitivity index <{}> in each polygon in season {}: {}".format(name[parameter_n], season_n + 1, sensitivity_order)
        unid = 'Sensitivity Index'
        colores = None
        # this is to calculate the range for the array--values==
        escala = np.min(values), np.max(values)
        #escala = np.int32(0), np.int32(7)

        geog = self.Rechna_Doab
        colores = ['#fffce0', '#fcf4ab', '#f4250e']
        geog.dibujar(archivo=nombre_archivo, valores=values, título=var, unidades=unid,
                     colores=colores, escala_num=escala)

    @staticmethod
    def curve_fit(x_data=None, y_data=None):
        def function(x, a, b):
            return a * x + b

        np.random.seed(0)
        # x_data = np.linspace(-5, 5, num=50)
        # y_data = 2.9 * np.sin(1.5 * x_data) + np.random.normal(size=50)
        params, params_covariance = optimize.curve_fit(function, x_data, y_data, p0=[2.0, 2.0])
        print(params)
        plt.figure(figsize=(6, 4))
        plt.scatter(x_data, y_data, label='Data')
        plt.plot(x_data, [(params[0] * i + params[1]) for i in x_data], label='Fitted function')
        plt.legend(loc='best')
        plt.show()

class SensitivityOrder(Enum):
    S1 = 'S1'
    ST = 'ST'

#n_poly, Ns(sampling size for each parameter), n_para, timestepss
config = [215, 806, 8, 10]


# SIMULATION
fa = FastSa(config=config, name='0')
# problems = fa.problems_setup()
# parameters_set = fa.sampling(problems)
# evals = fa.simulation(parameters_set)
# result = fa.analyze(evals, problems)

# TRANSFORM SIMULATION RESULTS TO S1 AND ST
# evals = fa.load_data_from_file(os.path.join(fa.root_path, 'previous runs\\FAST RUNS\\fast_simulation_6462.out'))
# #fa.analyze_total_samples(evals, problems)
# evals = evals[0:6448]
# #print(len(evals))
# result = fa.analyze(evals, problems)

# plot original 2-dimentional graph
# for i in range(fa.n_poly):
#     fa.plot_SI(i, result, os.path.join(fa.root_path, 'previous runs\\fastFigure'))

duration_sensitivities = fa.load_sensitivity_data(os.path.join(fa.root_path, 'Simulation\\fast_sensitivity_0.out'))
print(duration_sensitivities[0].__len__())
print(duration_sensitivities[0])
for season in range(config[3] - 1):
    fa.plot_map(duration_sensitivities[season], season, SensitivityOrder.ST)
#     for p in range(fa.n_paras):
#         # fa.plot_map_4_parameter(duration_sensitivities[season], p, season, SensitivityOrder.S1)
#         fa.plot_map_4_parameter(duration_sensitivities[season], p, season, SensitivityOrder.ST)
