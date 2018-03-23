import sys
import os
from SALib.analyze import morris
from SALib.sample.morris import sample
from tinamit.Calib.SA_algorithms import soil_class as SC
from tinamit.Calib import gaby_simulation as GS
from tinamit.Calib.SA_algorithms import parameters_sa as P
import time
import numpy as np
import json
import matplotlib.pyplot as plt
from tinamit.Geog.Geog import Geografía
from scipy import optimize
from warnings import warn


class MorrisSA(object):
    root_path = 'D:\\Thesis\\pythonProject\\Tinamit\\tinamit\\Calib\\SA_algorithms\\Morris'
    #root_path = 'D:\\Gaby\\Tinamit\\tinamit\\Calib\\SA_algorithms\\Morris'

    # 0. Site geography

    def __init__(self, config, name):
        self.n_poly = config[0]
        self.n_sampling = config[2]
        self.n_paras = config[1]
        self.n_level = config[3]
        self.name = name
        self.n_season = config[4]

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

        # 215 problems_tinamit, bounds are different with regards to polygons
        problems_t = []  # 215 problems
        for i in range(self.n_poly):
            problems_t.append({'num_vars': self.n_paras,
                               'names': P.parameters,
                               'bounds': set_bounds_4_paras(i)})
            # print(problems_t[-1])
        return problems_t

    def problems_setup2(self):

        problem = {
            'num_vars': self.n_paras,
            'names': [
                'Ptq - s1',  # the most important for the water table depth (saturated zone)
                'Ptr - s1',  # unsaturated zone, important for the sanility
                'Kaq - s1',
                'Peq - s1',
                'Pex - s1',
                'Ptq - s2',  # the most important for the water table depth (saturated zone)
                'Ptr - s2',  # unsaturated zone, important for the sanility
                'Kaq - s2',
                'Peq - s2',
                'Pex - s2',
                'Ptq - s3',  # the most important for the water table depth (saturated zone)
                'Ptr - s3',  # unsaturated zone, important for the sanility
                'Kaq - s3',
                'Peq - s3',
                'Pex - s3',
                'Ptq - s4',  # the most important for the water table depth (saturated zone)
                'Ptr - s4',  # unsaturated zone, important for the sanility
                'Kaq - s4',
                'Peq - s4',
                'Pex - s4',
                'POH Kharif',
                'POH rabi',
                'Capacity per tubewell'],
            'bounds': [[0.45, 0.55],
                       [0.45, 0.47],
                       [26, 103], #Kaq_s1
                       [0.054, 0.302],
                       [0.065, 0.39],
                       [0.44, 0.50],
                       [0.44, 0.46],
                       [26, 120], #Kaq_s2
                       [0.054, 0.302],
                       [0.065, 0.39],
                       [0.45, 0.53],
                       [0.45, 0.53],
                       [26, 158], #Kaq_s3
                       [0.054, 0.302],
                       [0.065, 0.39],
                       [0.43, 0.55],
                       [0.42, 0.52],
                       [26, 52], #Kaq_s4
                       [0.054, 0.302],
                       [0.065, 0.39],
                       [355, 450],
                       [235, 300],
                       [100.8, 201.6]
                       ]}

        return problem

    def sampling(self, problems_t=[]):
        parameters_set = []
        with open(os.path.join(self.root_path, 'morris_parameters_{}.out'.format(
                self.name)), 'w') as f1:
            for problem in problems_t:
                # SAlib sampling output --> list
                param_values = sample(problem, self.n_sampling, num_levels=self.n_level, grid_jump=self.n_level / 2,
                                      optimal_trajectories=None)
                # print(param_values)
                parameters_set.append(param_values)  # 215*90*8
                f1.write('{}\n'.format(json.dumps(param_values.tolist())))  # json: list --> structurazation [为了写文件]
                f1.flush()
        # parameters_set.append(fast_sampler.sample(p_s, N)) format is 215*Ns*n_parameters (Ns = N * n_parameters)
        f1.close()
        return parameters_set

    def sampling2(self, problem):
        # SAlib sampling output --> list
        param_values = sample(problem, self.n_sampling, num_levels=self.n_level, grid_jump=self.n_level / 2,
                              optimal_trajectories=None)
        #print(param_values) = # Ns*n_parameter = 600 * 23 --> [[]] only two layers.

        with open(os.path.join(self.root_path, 'Morris_Sampling_{}.out'.format(
                self.name +1)), 'w') as f1:

            f1.write('{}\n'.format(json.dumps(param_values.tolist())))  # json: list --> structurazation
            f1.flush()
        # parameters_set.append(fast_sampler.sample(p_s, N)) format is 215*Ns*n_parameters (Ns = N * n_parameters)
        f1.close()
        return param_values

    def simulation(self, parameters_set=None):
        if parameters_set is None:
            parameters_set = []

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

        # switch format 215*Ns*n_parameters to Ns*n_parameters*215 (to match Tinamit)
        # Ns = len(parameters_set)
        sampling_parameters_set = []  # 90*8*215, tinamit format
        for i in range(len(parameters_set[0])):  # 90
            sampling = []  # 8
            for j in range(self.n_paras):  # 8
                parameters = []  # 215
                for k in range(self.n_poly):  # 215
                    parameters.append(parameters_set[k][i][j])
                sampling.append(parameters)
                # print(min(parameters), max(parameters))
            sampling_parameters_set.append(sampling)

        # evals = []  # Ns × 215
        start_time = time.time()  # return current time for recoding current runtime

        # SIMULATION (if uses ALREADY data, comment this)
        # after each run of Tinamit, write the results into the 'Simulation.out', 'as f' -->Instance of operating file.
        worked = {x: [] for x in P.parameters}
        bad = {x: [] for x in P.parameters}
        list_dic_set = [{'bf': {x: s[j] for j, x in enumerate(P.parameters)}} for s in sampling_parameters_set]
        result = GS.simulation(list_dic_set, self.n_season, nombre='Morris')
        # print('Finished sampling ', ' ', result)
        print("--- %s seconds ---" % (time.time() - start_time))
        for var, val in result.items():
            print(var)  # total values of the results
            val = np.array(val)
            print(val.size)
            print(val.shape)
        # print(result.shape)
        results_json = {ll: [p.tolist()] for ll, v in result.items() for p in v}
        print(type(results_json))
        print(results_json)
        with open(os.path.join(self.root_path, 'morris_simulation_{}.out'.format(self.name)), 'w') as f:
            # print(len()) # len() would be the first layer of the component
            f.write(json.dumps(results_json) + '\n')

        # with open(os.path.join(self.root_path, 'morris_simulation_{}.out'.format(
        #         self.name)), 'w') as f:
        #     for i, set_ in enumerate(sampling_parameters_set):
        #         dict_set = {x: set_[j] for j, x in enumerate(P.parameters)}
        #         try:
        #             result = GS.simulation(dict_set, self.n_season)
        #             for x in worked:
        #                 worked[x].append(dict_set[x])
        #         except ChildProcessError:
        #             for x in bad:
        #                 warn('MISTAKE IN RUN')
        #                 bad[x].append(dict_set[x])
        #             continue
        #         except OSError as ose:
        #             print(ose)
        #             result = 0  # if exception then set value 0 to the result
        #         evals.append(result) # 90 simulations * n_seasons
        #         print('Sampling ', i, ' ', result)
        #         print("--- %s seconds ---" % (time.time() - start_time))
        #         print(result.size) # total values of the results
        #         print(result.shape)
        #         # print(len()) # len() would be the first layer of the component
        #         f.write(json.dumps(result.tolist()) + '\n')
        #         f.flush()  # in time writing

        print("--- %s total seconds ---" % (time.time() - start_time))  # will only show once at the end
        return result

    def simulation2(self, parameters_set=None):
        '''
        Function:
        :param parameters_set: Ns * number of parameters [= 600*23 = param_values]
        :return:
        '''
        def data_prepare(parameters_set):
            '''
            This function is to transform sampled data into Tinamit format
            :param parameters_set: list, [Ns*n_param]
            :return:
            '''
            if parameters_set is None:
                parameters_set = []
            # parameters_set size = Ns * 20 = param_values
            # from 23 to 11 * 215;
            sampling_parameters_set = [] # Ns*8*215; Tinamit
            # for each sample from Ns
            for sam in parameters_set: # 600*23
                sampling = {} #
                for i, name in enumerate(P.parameters):

                    if name.startswith('Kaq'):
                        if name.endswith('1'):
                            sampling[name] = [sam[(SC.get_soil_type(j, 0) - 1) * 5 + P.parametersNew.index(
                                'Kaq - Horizontal hydraulic conductivity')] for j in
                                              range(self.n_poly)]
                        if name.endswith('2'):
                            sampling[name] = [
                                sam[(SC.get_soil_type(j, 1) - 1) * 5 + P.parametersNew.index(
                                    'Kaq - Horizontal hydraulic conductivity')] for j in
                                range(self.n_poly)]
                        if name.endswith('3'):
                            sampling[name] = [
                                sam[(SC.get_soil_type(j, 2) - 1) * 5 + P.parametersNew.index(
                                    'Kaq - Horizontal hydraulic conductivity')] for j in
                                range(self.n_poly)]
                        if name.endswith('4'):
                            sampling[name] = [
                                sam[(SC.get_soil_type(j, 3) - 1) * 5 + P.parametersNew.index(
                                    'Kaq - Horizontal hydraulic conductivity')] for j in
                                range(self.n_poly)]
                    else:
                        if P.parametersNew.index(name) <= 4:
                            sampling[name] = [
                                sam[(SC.get_soil_type(j) - 1) * 5 + P.parametersNew.index(name)] for j in
                                range(self.n_poly)]
                        else:
                            sampling[name] = [
                                sam[15 + P.parametersNew.index(name)] for j in
                                range(self.n_poly)]
                sampling_parameters_set.append(sampling)

            # print(sampling_parameters_set)

            lista_mds = ['POH Kharif Tinamit', 'POH rabi Tinamit', 'Capacity per tubewell']
            list_dic_set = [{'bf': {ll: v for ll, v in s.items() if ll not in lista_mds},
                             'mds': {ll: v for ll, v in s.items() if ll in lista_mds}} for s in sampling_parameters_set]
            # Ns dictionary [8*215 + 3*215]

            # separete list_dic_set into groups with 50 size
            tmp_list_dict_set = [] #tmp = temporary
            intercep = 25
            n_group = int(list_dic_set.__len__()/intercep)
            last_group = list_dic_set.__len__()%intercep #取余

            for i in range(n_group):
                tmp_list_dict_set.append(list_dic_set[i*intercep: (i*intercep + intercep - 1)])#0-99； 100-199; 200-299 etc.
            if last_group != 0:
                tmp_list_dict_set.append(list_dic_set[(n_group - 1) * intercep: ((n_group - 1) * intercep +
                                                                                 last_group - 1)])

            for i, data in enumerate(tmp_list_dict_set):
                with open(os.path.join(self.root_path, 'Morris_temp_list_data_{}_{}.out'.format(
                    self.name, i)), 'w') as f0:
                    f0.write(('{}\n').format(json.dumps(data)))
                f0.close()
            return tmp_list_dict_set

        # filename --> 'Morris_temp_list_data_{}_{}.out'
        def read_data_from_file(filename):
            list_dic_set = []
            with open(os.path.join(self.root_path, filename),
                      'r') as fr:
                for line in fr:
                    list_dic_set.append(json.loads(line))
                    # print(json.loads(line)) # everything in the file is 'str' type --> 'dict'
            fr.close()
            return list_dic_set

        start_time = time.time()  # return current time for recoding current runtime
        list_dic_set = data_prepare(parameters_set)
        print(len(list_dic_set))
        # for i, set in enumerate(list_dic_set):
        #     print('{} iterations'.format(i))
        #     for p, v in set['bf'].items():
        #         print(p, v)
        #list_dic_set = [{'bf': {x: s[j] for j, x in enumerate(P.parameters)}} for s in sampling_parameters_set]

        for i, list in enumerate(list_dic_set):
            result = GS.simulation(list, self.n_season, nombre='Morris')
            # print('Finished sampling ', ' ', result)
            print("--- %s seconds ---" % (time.time() - start_time))
            print('result', result)

            # results_json = {ll: [].append(p.tolist()) for ll, v in result.items() for p in v}
            results_json = {ll: [p.tolist() for p in v] for ll, v in result.items()}
            print(results_json)
            with open(os.path.join(self.root_path, 'morris_simulation_{}_{}.out'.format(self.name), i), 'w') as f:
                # print(len()) # len() would be the first layer of the component
                f.write(json.dumps(results_json) + '\n')


        print("--- %s total seconds ---" % (time.time() - start_time))  # will only show once at the end
        return result

    def analyze(self, evals, parameters_set, problems_t):
        # evals : [90*215*3], parameters_set: [215*90*8], problems_t: [215]
        # SA_FAST: PORCESS & WRITE, process first and write the timestep data into the file
        # write the results into the 'sensitivity.out'
        # r+ --> write and read

        duration_all_si = []  # restore the result of all si
        dict_Si = {}

        for var, res in evals.items():

            evals_transpose = np.asarray(res).transpose()  # from 90*215*3 to 3*215*90

            for j, duration in enumerate(evals_transpose):
                # duration : [215*90]
                if j == 0:
                    continue

                duration_si = []
                for i, problem in enumerate(problems_t):
                    # Si = fast.analyze(p, duration[i], print_to_console=True)
                    # print(len(parameters_set[i]))
                    # para_set = np.asarray([parameters_set[i][x] for x in range(522)])
                    # evals_set = np.asarray([duration[i][x] for x in range(522)])
                    Si = morris.analyze(problem, parameters_set[i], duration[i], conf_level=0.95,
                                        print_to_console=False,
                                        num_levels=self.n_level, grid_jump=self.n_level / 2,
                                        num_resamples=self.n_sampling)
                    # print(Si)

                    # fig, (ax1, ax2) = plt.subplots(1, 2)
                    # horizontal_bar_plot(ax1, Si, {}, sortby='mu_star', unit=r"tCO$_2$/year")
                    # covariance_plot(ax2, Si, {}, unit=r"tCO$_2$/year")
                    #
                    # fig2 = plt.figure()
                    # sample_histograms(fig2, param_values, problem, {'color': 'y'})
                    # plt.show()
                    dict_Si_var = dict_Si[var] = {}
                    for k, v in Si.items():
                        if isinstance(v, np.ndarray):
                            n_v = v.tolist()
                            dict_Si_var[k] = n_v
                        else:
                            dict_Si_var[k] = v

                    duration_si.append(dict_Si)
                duration_all_si.append(duration_si)

        with open(os.path.join(self.root_path, 'morris_sensitivity_{}.out'.format(
                self.name)), 'w') as f0, \
                open(os.path.join(self.root_path,
                                  'morris_max_sensitivity_{}.out'.format(
                                      self.name)),
                     'w') as f1:
            f0.write(('{}\n').format(json.dumps(dict_Si)))
            f1.write('\nThis is the duration {}: \n\n'.format(j))

        return duration_all_si

    def analyze2(self, evals, parameters_set, problem):
        # evals : [23*215*10], parameters_set: [210*11], problem
        # SA_FAST: PORCESS & WRITE, process first and write the timestep data into the file
        # write the results into the 'sensitivity.out'
        # r+ --> write and read

        duration_all_si = []  # restore the result of all si
        dict_Si = {}
        for var, res in evals.items():
            evals_transpose = np.asarray(res).transpose()  # from 90*215*10 to 10*215*90
            print(evals_transpose.shape)

            for j, duration in enumerate(evals_transpose):
                # duration : [215*90]
                if j == 0:
                    continue

                duration_si = []

                Si = morris.analyze(problem, parameters_set, duration[i], conf_level=0.95,
                                    print_to_console=False,
                                    num_levels=self.n_level, grid_jump=self.n_level / 2,
                                    num_resamples=self.n_sampling)
                dict_Si_var = dict_Si[var] = {}
                for k, v in Si.items():
                    if isinstance(v, np.ndarray):
                        n_v = v.tolist()
                        dict_Si_var[k] = n_v
                    else:
                        dict_Si_var[k] = v

                duration_si.append(dict_Si)
                duration_all_si.append(duration_si)

        with open(os.path.join(self.root_path, 'morris_sensitivity_{}.out'.format(
                self.name)), 'w') as f0, \
                open(os.path.join(self.root_path,
                                  'morris_max_sensitivity_{}.out'.format(
                                      self.name)),
                     'w') as f1:
            f0.write(('{}\n').format(json.dumps(dict_Si)))
            f1.write('\nThis is the duration {}: \n\n'.format(j))

        return duration_all_si

    @staticmethod
    def load_data_from_file(self, filename):
        # IF ALREADY had simulation data, run here
        # if have existed simulation data, just for evaluation
        evals = []  # Ns × 215
        # with open('D:\\Thesis\\pythonProject\\Tinamit\\tinamit\\Calib\\SA_algorithms\\previous runs\\7timestep_simulation - Copy.out', 'r') as fr:
        with open(os.path.join(self.root_path, filename),
                  'r') as fr:
            for line in fr:
                evals.append(json.loads(line))
                # print(json.loads(line)) # everything in the file is 'str' type --> 'dict'
        fr.close()
        return evals

    def load_sensitivity_data(self, filename):
        sensitivity_data = []
        with open(filename, 'r') as f:
            for line in f:
                sensitivity_data.append(json.loads(line))
                # print(json.loads(line))
                # dict_str = ast.literal_eval(line)
        print(len(sensitivity_data))  # 11 (optimize it later>>>>>> Should be 10 --> use updated codes
        return sensitivity_data

    def load_parameters_sampling(self, filename):
        parameters_set = []
        with open(filename, 'r') as f:
            for line in f:
                ps = line.replace(']]', ']]\n')
                pss = ps.split('\n')
                for p in pss:
                    if len(p) == 0:
                        continue
                    parameters_set.append(json.loads(p))
        return parameters_set

    def plot_result(self, poly_id, duration_all_si, savepath):
        figname = '{}-{}={}'.format(poly_id + 1, self.n_level, self.n_sampling)
        plt.figure(figname)
        plt.suptitle('p={}, r={}, poly_n={}'.format(self.n_level, self.n_sampling, poly_id + 1))
        name = ['Ptq',
                'Ptr',
                'Kaq1',  # need to consider all four
                'Kaq2',
                'Kaq3',
                'Kaq4',
                'Peq',
                'Pex']

        for i, duration in enumerate(duration_all_si):
            if i == len(duration_all_si) - 1:
                continue
            plt.subplot('13{}'.format(i + 1))
            if i == 0:
                plt.ylabel('Sigma')
            plt.xlabel('Mu_star')
            plt.title('season {}'.format(i + 1))
            mu = duration[poly_id]['mu_star']
            sigma = duration[poly_id]['sigma']
            # ax = plt.gca()

            for k, txt in enumerate(name):
                plt.gca().annotate(txt, (mu[k], sigma[k]))
            plt.gca().scatter(mu, sigma)
        # plt.ylabel('Sigma')
        plt.savefig('{}/{}-{}-{}.png'.format(savepath, poly_id, self.n_level, self.n_sampling))
        plt.close(figname)

    def plot_map(self, duration, config, season):
        if not isinstance(config, int) or not isinstance(season, int):
            return 'parameter type error!'
        values = []  # contain 215 values, each value represents the paramater index of the biggest mu_star
        # parameters_2_value_dict = [
        #
        # ]
        for poly in duration:
            # the index of list is set as the index of parameters
            parameter_index = poly['mu_star'].index(max(poly['mu_star']))
            # print(parameter_index)
            # print('len', len(poly['mu_star']))

            values.append(parameter_index)
            # print(parameter_index)
        # print(np.asarray(values))

        nombre_archivo = os.path.join(self.root_path,
                                      'Plot_Map\\Morris-season-{}-config-{}'.format(season + 1, config + 1))
        var = 'Morris \nMost sensitive parameter of each polygon in season {}\n Configuration {}'.format(season + 1,
                                                                                                         config + 1)
        unid = 'Parameter'
        # this is to calculate the range for the array--values==
        # escala = np.min(values), np.max(values) (0 - 7 are the index for the 8 parameters)
        escala = np.int32(0), np.int32(7)

        geog = self.Rechna_Doab
        geog.dibujar(archivo=nombre_archivo, valores=values, título=var, unidades=unid,
                     escala_num=escala, categs=('Ptq', 'Ptr', 'Kaq1', 'Kaq2', 'Kaq3', 'Kaq4', 'Peq', 'Pex'),
                     colores=['#302311', '#eeff66', '##FFCC66', '#00CC66', '#66ecff', '#6669ff', '#e766ff', '#ff6685'])

    def plot_map_4_parameter(self, duration, parameter_n, season_n, config_n):
        name = ['Ptq',
                'Ptr',
                'Kaq1',  # need to consider all four
                'Kaq2',
                'Kaq3',
                'Kaq4',
                'Peq',
                'Pex']
        if not isinstance(parameter_n, int) \
                or not isinstance(season_n, int) or not isinstance(config_n, int):
            return 'parameter type error!'
        values = []
        # parameters_2_value_dict = [
        #
        # ]
        mu_star_in_polys = []
        for poly in duration:
            mu_stars = []
            for value in poly['mu_star']:
                mu_stars.append(value)
            mu_star_in_polys.append(mu_stars)

        mu_star_in_polys = np.asarray(mu_star_in_polys).transpose()
        values = mu_star_in_polys[parameter_n]
        # print(values)

        nombre_archivo = os.path.join(self.root_path,
                                      'plot_map_4_parameter\\Morris-parameter-{}-season-{}-config-{}'.format(
                                          parameter_n + 1, season_n + 1, config_n + 1))
        var = "Morris \nSensitivity index <{}> in each polygon in season {} \n Configuration {}\n Morris".format(
            name[parameter_n], season_n + 1, config_n + 1)
        unid = 'Sensitivity Index'
        # this is to calculate the range for the array--values==
        escala = np.min(values), np.max(values)
        # escala = np.int32(0), np.int32(7)

        geog = self.Rechna_Doab
        colores = ['#f6e6bf', '#eeff66', '##FFCC66', '#00CC66', '#66ecff', '#6669ff', '#e766ff', '#6920dd']
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
        # plt.show()

if __name__ == '__main__':

    config = [
        # n_poly, n_paras, n_sampling, n_level, n_season
        # [215, 23, 25, 8, 3],
        # [215, 23, 25, 8, 10],
        # [215, 23, 25, 8, 10],
        [215, 23, 25, 8, 20],#24*25*20=12,000(6000)
        # [215, 23, 25, 16, 10],
        # [215, 20, 25, 16, 20]
        # [215, 20, 10, 16, 10],
        # [215, 20, 20, 8, 10],
        # [215, 20, 20, 16, 10],
        # [215, 20, 50, 8, 10],
        # [215, 20, 50, 16, 10]
    ]

    # SIMULATION on problem
    for i, conf in enumerate(config):
        # if crash
        if i != 0:
            continue
        mor = MorrisSA(conf, i)
        problem = mor.problems_setup2()
        parameters_set = mor.sampling2(problem)
        evals = mor.simulation2(parameters_set)
        mor.analyze2(evals, parameters_set, problem)

    # config = [
    #     # n_poly, n_paras, n_sampling, n_level, n_season   #     [215, 8, 10, 8, 2],  # 90 = (N + 1) * config[2]
    #     [215, 8, 10, 16, 10],
    #     # [215, 8, 10, 32, 10],
    #     [215, 8, 20, 8, 10],
    #     [215, 8, 20, 16, 10],
    #     # [215, 8, 20, 32, 11],
    #     [215, 8, 50, 8, 10],
    #     [215, 8, 50, 16, 10],
    #     # [215, 8, 50, 32, 11],
    # ]

    # # SIMULATION
    # for i, conf in enumerate(config):
    #     # if crash
    #     if i != 0:
    #         continue
    #     mor = MorrisSA(conf, i)
    #     problems = mor.problems_setup()
    #     parameters_set = mor.sampling(problems)
    #     evals = mor.simulation(parameters_set)
    #     mor.analyze(evals, parameters_set, problems)

    # PLOTTING
    # for i, conf in enumerate(config):
    #     if i != 0:
    #         continue
    #     mor = MorrisSA(conf, i)
    #     problems = mor.problems_setup()
    #     # sensitivity_data = mor.load_sensitivity_data('D:\\Gaby\\Tinamit\\tinamit\\Calib\\SA_algorithms\\previous runs\\Morris Runs\\morris_sensitivity_0.out')
    #     parameters_set = np.asarray(mor.load_parameters_sampling(
    #         os.path.join(mor.root_path, 'morris_parameters_{}.out'.format(i))))
    #
    #     sampling_parameters_set = []
    #     for l in range(len(parameters_set[0])):
    #         sampling = []
    #         for j in range(mor.n_paras):
    #             parameters = []
    #             for k in range(mor.n_poly):
    #                 parameters.append(parameters_set[k][l][j])
    #             sampling.append(parameters)
    #             # print(min(parameters), max(parameters))
    #         sampling_parameters_set.append(sampling)
    #
    #     print(len(sampling_parameters_set))
    #     print(sampling_parameters_set[0])
    #     print(sampling_parameters_set[1])
    #     # evals is size of (n_paras + 1)*n_sampling*n_poly*n_season 3-D matrix
    #     evals = mor.load_data_from_file(mor, 'morris_simulation_{}.out'.format(i))
    #     print(len(evals))
    #     print(evals[0])
    #     print(evals[1])
    #     duration_all_si = mor.analyze(evals, parameters_set, problems)

    # print(len(duration_all_si))
    # # mor.plot_map(duration_all_si[1], i, 1)
    # for j in range(mor.n_poly):
    #     mor.plot_result(j, duration_all_si,
    #       'D:\\Thesis\\pythonProject\\Tinamit\\tinamit\\Calib\\SA_algorithms\\previous runs\\morrisFigure')

    # for season in range(conf[4]):
    #     mor.plot_map(duration_all_si[season], i, season)

    # for season in range(conf[4] - 1):
    #     for p in range(conf[1]):
    #         mor.plot_map_4_parameter(duration_all_si[season], p, season, i)

    # mor.plot_result(63, sensitivity_data)
    # mor.plot_result(73, sensitivity_data)
    # mor.plot_result(74, sensitivity_data)

    # CURVE FITTING
    # evals = MorrisSA.load_data_from_file(MorrisSA,'Simulation\\morris_simulation_{}.out'.format(0))
    # print(len(evals))
    # print(len(evals[0]))
    # print(len(evals[0][0]))
    # for sample in evals:
    #     poly_id = 0
    #     x_data = [i for i in range(12)]
    #     y_data = sample[poly_id]
    #     # print(len(y_data))
    #     # print(y_data)
    #     MorrisSA.curve_fit(x_data, y_data)
    # plt.show()
