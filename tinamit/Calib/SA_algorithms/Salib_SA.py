import os
from tinamit.Calib.ej import soil_class as SC

from tinamit.Calib import gaby_simulation as GS
# from tinamit.Ejemplos.en.Ejemplo_SAHYSMOD import "Coupling script2" as cs2
from tinamit.Calib.SA_algorithms import parameters_sa as P
import time
import numpy as np
import json
import matplotlib.pyplot as plt
from scipy import optimize
import scipy.stats as sp

class SA(object):
    # root_path = 'D:\\Thesis\\pythonProject\\Tinamit\\tinamit\\Calib\\SA_algorithms\\Morris'
    # root_path = 'D:\\Thesis\\pythonProject\\Tinamit\\tinamit\\Calib\\SA_algorithms\\Fast'
    root_path = ''

    # 0. Site geography
    def __init__(self, sa_name=None):
        self.sa_name = sa_name
        Rechna_Doab = Geografía(nombre='Rechna Doab')

        base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Shape_files')
        Rechna_Doab.agregar_frm_regiones(os.path.join(base_dir, 'Internal_Polygon.shp'), col_id="Polygon_ID")

        Rechna_Doab.agregar_forma(os.path.join(base_dir, 'External_Polygon.shp'), color='#edf4da')
        Rechna_Doab.agregar_forma(os.path.join(base_dir, 'RIVR.shp'), tipo='agua')
        # Rechna_Doab.agregar_forma(os.path.join(base_dir, 'Forst_polygon.shp'), tipo='bosque')
        Rechna_Doab.agregar_forma(os.path.join(base_dir, 'CNL_Arc.shp'), tipo='agua', color='#1ba4c6', llenar=False)
        # Rechna_Doab.agregar_forma(os.path.join(base_dir, 'buildup_Polygon.shp'), tipo='ciudad')
        # Rechna_Doab.agregar_forma(os.path.join(base_dir, 'road.shp'), tipo='calle')

        self.Rechna_Doab = Rechna_Doab

    def problems_setup2(self):
        '''
        Based on SALib requirement setup a problem for 1)number of params, 2)name of the params, 3)bounds
        :return: problem
        '''
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
                       [26, 103],  # Kaq_s1
                       [0.054, 0.302],
                       [0.065, 0.39],
                       [0.44, 0.50],
                       [0.44, 0.46],
                       [26, 120],  # Kaq_s2
                       [0.054, 0.302],
                       [0.065, 0.39],
                       [0.45, 0.53],
                       [0.45, 0.53],
                       [26, 158],  # Kaq_s3
                       [0.054, 0.302],
                       [0.065, 0.39],
                       [0.43, 0.55],
                       [0.42, 0.52],
                       [26, 52],  # Kaq_s4
                       [0.054, 0.302],
                       [0.065, 0.39],
                       [355, 450],
                       [235, 300],
                       [100.8, 201.6]
                       ]}
        self.problem = problem
        return problem

    def problems_setup_plus_dummy(self):
        '''
        According SALib requirement setup a problem for 1)number of params, 2)name of the params, 3)bounds
        :return: problem
        '''
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
                'Capacity per tubewell',
                'Dummy parameter'],
            'bounds': [[0.45, 0.55],
                       [0.45, 0.47],
                       [26, 103],  # Kaq_s1
                       [0.054, 0.302],
                       [0.065, 0.39],
                       [0.44, 0.50],
                       [0.44, 0.46],
                       [26, 120],  # Kaq_s2
                       [0.054, 0.302],
                       [0.065, 0.39],
                       [0.45, 0.53],
                       [0.45, 0.53],
                       [26, 158],  # Kaq_s3
                       [0.054, 0.302],
                       [0.065, 0.39],
                       [0.43, 0.55],
                       [0.42, 0.52],
                       [26, 52],  # Kaq_s4
                       [0.054, 0.302],
                       [0.065, 0.39],
                       [355, 450],
                       [235, 300],
                       [100.8, 201.6],
                       [0, 1]
                       ]}
        self.problem = problem
        return problem

    def sampling2(self, problem):
        return None

    def simulation2(self, parameters_set=None, is_dummy=False):
        '''
        Conduct Tinamit simulation
        :param parameters_set: Ns * number of parameters [e.g. Ns*23 = param_values]
        :return: sampling_parameters_set [{'var':[215],}], Ns*11*215, Tinamit Format
        '''

        def data_prepare(parameters_set):
            '''
            this function is to transform sampled data into format of Tinamit
            :param parameters_set: Ns * 23
            :sam: (), sam is 23 sample values in each of total Ns
            :return:
            '''
            if parameters_set is None:
                parameters_set = []
            # from 23 to 11 * 215
            sampling_parameters_set = []  # Ns*11*215 Tinamit format as Tinamit only consider Kaq1234
            if is_dummy:
                parameters = P.parametersNew_dummy
            else:
                parameters = P.parametersNew
            # for each sample from Ns
            for sam in parameters_set:  # sam: each 23 of the Ns
                sampling = {}  # each param iterate 215 times, 11*215; eg.,{'kaq1': [215 vals]}
                for i, name in enumerate(P.parameters):  # give index to 11 param names

                    if name.startswith('Kaq'):
                        if name.endswith('1'):
                            sampling[name] = [(sam[(SC.get_soil_type(j, 0) - 1) * 5 + parameters.index(
                                'Kaq - Horizontal hydraulic conductivity')] +
                                               sam[(SC.get_soil_type(j) - 1) * 5 + parameters.index(
                                                   'Kaq - Horizontal hydraulic conductivity')] / 2) for j in
                                              range(self.n_poly)]

                        if name.endswith('2'):
                            sampling[name] = [
                                (sam[(SC.get_soil_type(j, 1) - 1) * 5 + parameters.index(
                                    'Kaq - Horizontal hydraulic conductivity')] +
                                 sam[(SC.get_soil_type(j) - 1) * 5 + parameters.index(
                                     'Kaq - Horizontal hydraulic conductivity')] / 2) for j in
                                range(self.n_poly)]

                        if name.endswith('3'):
                            sampling[name] = [
                                (sam[(SC.get_soil_type(j, 2) - 1) * 5 + parameters.index(
                                    'Kaq - Horizontal hydraulic conductivity')] +
                                 sam[(SC.get_soil_type(j) - 1) * 5 + parameters.index(
                                     'Kaq - Horizontal hydraulic conductivity')] / 2) for j in
                                range(self.n_poly)]

                        if name.endswith('4'):
                            sampling[name] = [
                                (sam[(SC.get_soil_type(j, 3) - 1) * 5 + parameters.index(
                                    'Kaq - Horizontal hydraulic conductivity')] +
                                 sam[(SC.get_soil_type(j) - 1) * 5 + parameters.index(
                                     'Kaq - Horizontal hydraulic conductivity')] / 2) for j in
                                range(self.n_poly)]
                    else:
                        if parameters.index(name) <= 4:  # 4 means the first 5 BF params
                            sampling[name] = [
                                sam[(SC.get_soil_type(j) - 1) * 5 + parameters.index(name)] for j in
                                range(self.n_poly)]
                        elif parameters.index(name) <= 7 and parameters.index(name) > 4:
                            sampling[name] = [
                                sam[15 + parameters.index(name)] for j in
                                range(self.n_poly)]
                        else:
                            pass
                sampling_parameters_set.append(sampling)

            lista_mds = ['POH Kharif Tinamit', 'POH rabi Tinamit', 'Capacity per tubewell']
            list_dic_set = [{'bf': {ll: v for ll, v in s.items() if ll not in lista_mds},
                             'mds': {ll: v for ll, v in s.items() if ll in lista_mds}} for s in sampling_parameters_set]
            # list_dic_set [8*215 + 3*215]

            # split list_dic_set into n groups according to the base sample size;
            # e.g., n=50, number of tmp_list_dict_set=48
            tmp_list_dict_set = []  # tmp = temporary
            intercep = 25
            n_group = int(list_dic_set.__len__() / intercep)  # group the Ns into Ns/25 groups
            last_group = list_dic_set.__len__() % intercep  # 取余 add the residue to the last intergal group

            # define the same number of simulated data and saved in group form, in case of crush
            # ith group
            for i in range(n_group):
                tmp_list_dict_set.append(
                    list_dic_set[i * intercep: (i * intercep + intercep)])  # 0-99； 100-199; 200-299 etc.
            if last_group != 0:
                tmp_list_dict_set.append(list_dic_set[(n_group - 1) * intercep: ((n_group - 1) * intercep +
                                                                                 last_group)])

            for i, data in enumerate(tmp_list_dict_set):
                with open(os.path.join(self.root_path, '{}_temp_list_data_{}_{}.out'.format(self.sa_name,
                                                                                            self.name, i)), 'w') as f0:
                    f0.write(('{}\n').format(json.dumps(data)))
                f0.close()
            return tmp_list_dict_set

        # filename --> 'Morris_temp_list_data_{}_{}.out' OR 'Fast_temp_list_data_{}_{}.out'
        def read_data_from_file(filename):
            list_dic_set = []
            with open(os.path.join(self.root_path, filename),
                      'r') as fr:
                for line in fr:
                    list_dic_set.append(json.loads(line))
                    # print(json.loads(line)) # everything in the file is 'str' type --> 'dict'
            fr.close()
            return list_dic_set

        # def read_data_from_file(group_id):
        #     list_dic_set = []
        #     with open(os.path.join(self.root_path, '{}_temp_list_data_{}_{}.out'.format(self.sa_name,
        #                                                                                 self.name, group_id)),
        #               'r') as fr:
        #         for line in fr:
        #             list_dic_set.append(json.loads(line))
        #     fr.close()
        #     return list_dic_set
        #
        start_time = time.time()  # return current time for recoding current runtime
        list_dic_set = data_prepare(parameters_set)
        print('Start to preparing data for simulation')
        print(len(list_dic_set))

        # for i, set in enumerate(list_dic_set):
        #     print('{} iterations'.format(i))
        #     for p, v in set['bf'].items():
        #         print(p, v)
        # list_dic_set = [{'bf': {x: s[j] for j, x in enumerate(P.parameters)}} for s in sampling_parameters_set]

        result = {'Watertable depth Tinamit': []}  # {'WTD': [215[20 seaons]]}
        for i, list in enumerate(list_dic_set):  # intercept*11*215, list = each 11*215
            print("This is group {} of total {}".format(i, list_dic_set.__len__()))

            try:
                list_result = GS.simulation(list, self.n_season, nombre=self.sa_name)
                # list_result =
            except Exception as inst:
                print(inst)
                print('this is {} run'.format(i), list)
                # return

            # result['Watertable depth Tinamit'] += list_result['Watertable depth Tinamit']
            result['Watertable depth Tinamit'] += list_result

            print("--- %s seconds ---" % (time.time() - start_time))
            print('result', result)

            # results_json = {ll: [].append(p.tolist()) for ll, v in result.items() for p in v}
            results_json = {ll: [p.tolist() for p in v] for ll, v in list_result.items()}
            print(results_json)
            with open(os.path.join(self.root_path, '{}_simulation_{}_{}.out'.format(self.sa_name, self.name, i)),
                      'w') as f:
                # print(len()) # len() would be the first layer of the component
                f.write(json.dumps(results_json) + '\n')

        print("--- %s total seconds ---" % (time.time() - start_time))  # will only show once at the end
        return result

    def analyze2(self, evals, parameters_set, problem):
        # evals : [90*215*3], parameters_set: [215*90*8], problems_t: [215]
        # SA_FAST: PORCESS & WRITE, process first and write the timestep data into the file
        # write the results into the 'sensitivity.out'
        return None

    def get_last_and_ave_simulation_value(self, polys, evals, skip_firt_season=False):
        last_and_ave = []

        tmp_sum = 0
        tmp_last = 0
        for poly in polys:
            sum = 0
            for i, season in enumerate(evals[poly]):
                if skip_firt_season:
                    if i == 0:
                        continue
                sum += season
            tmp_sum += sum / (len(evals[poly]) if skip_firt_season else len(evals[poly]) - 1)
            tmp_last += evals[poly][-1]

        last_and_ave.append(tmp_sum / len(polys))
        last_and_ave.append(tmp_last / len(polys))
        return last_and_ave

    def compute_average_simuluation_value_4_polys(self, polys, evals):
        '''
        Average values for each of the class
        :param polys: refers to a list of polygons, e.g. [1, 2, 3, 4]
        :param evals:
        :return:
        compute_average_simuluation_value_4_polys(H1, evals)
        '''
        if len(polys) == 0:
            print('The length of list of polygons is null!')
            return None
        if not isinstance(polys, np.ndarray):
            polys = np.asarray(polys)
        average = 0
        for poly in polys:
            average += evals[poly]
        return (average / (len(polys))).tolist()

    @staticmethod
    def load_data_from_file(SA, filename):
        # IF ALREADY had simulation data, run here
        # if have existed simulation data, just for evaluation
        evals = []  # Ns × 215
        # with open('D:\\Thesis\\pythonProject\\Tinamit\\tinamit\\Calib\\SA_algorithms\\previous runs\\7timestep_simulation - Copy.out', 'r') as fr:
        with open(os.path.join(SA.root_path, filename),
                  'r') as fr:
            for line in fr:
                evals.append(json.loads(line))
                # print(json.loads(line)) # everything in the file is 'str' type --> 'dict'
        fr.close()
        return evals[0]

    @staticmethod
    def load_segmented_data_from_file(self, root_path, start, end):
        '''
        load divisional simulated data from file
        :param self:
        :param root_path: path to restore those files
        :param start: start point
        :param end:
        :return:
        '''
        evals = []
        for i in range(start, end + 1):
            with open(os.path.join(root_path, 'morris_simulation_{}_{}.out'.format(self.name, i)), 'r') as fr:
                for line in fr:
                    print(line)
                    evals.append(json.loads(line))
        return evals

    def load_sensitivity_data(self, filename):
        sensitivity_data = []
        with open(filename, 'r') as f:
            for line in f:
                sensitivity_data.append(json.loads(line))
                # print(json.loads(line))
                # dict_str = ast.literal_eval(line)
        # print(len(sensitivity_data))  # 11 (optimize it later>>>>>> Should be 10 --> use updated codes
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
        return parameters_set[0]

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

    def plot_map(self, duration, config, season, name='Morris'):
        if not isinstance(config, int) or not isinstance(season, int):
            return 'parameter type error!'
        # categs = self.problem['names']
        categs = [
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
            'Capacity per tubewell']

        parameter_mapping = {'Ptq - s1': 'Ptq',  # the most important for the water table depth (saturated zone)
                             'Ptr - s1': 'Ptr',  # unsaturated zone, important for the sanility
                             'Kaq - s1': 'Kaq',
                             'Peq - s1': 'Peq',
                             'Pex - s1': 'Pex',
                             'Ptq - s2': 'Ptq',  # the most important for the water table depth (saturated zone)
                             'Ptr - s2': 'Ptr',  # unsaturated zone, important for the sanility
                             'Kaq - s2': 'Kaq',
                             'Peq - s2': 'Peq',
                             'Pex - s2': 'Pex',
                             'Ptq - s3': 'Ptq',  # the most important for the water table depth (saturated zone)
                             'Ptr - s3': 'Ptr',  # unsaturated zone, important for the sanility
                             'Kaq - s3': 'Kaq',
                             'Peq - s3': 'Peq',
                             'Pex - s3': 'Pex',
                             'Ptq - s4': 'Ptq',  # the most important for the water table depth (saturated zone)
                             'Ptr - s4': 'Ptr',  # unsaturated zone, important for the sanility
                             'Kaq - s4': 'Kaq',
                             'Peq - s4': 'Peq',
                             'Pex - s4': 'Pex',
                             'POH Kharif': 'POH Kharif',
                             'POH rabi': 'POH rabi',
                             'Capacity per tubewell': 'Capacity per \ntubewell'}

        values = []  # contain 215 values, each value represents the paramater index of the biggest mu_star
        # parameters_2_value_dict = [
        #
        # ]
        for poly in duration:
            # the index of list is set as the index of parameters
            parameter_index = P.parametersName4Plot.index(
                parameter_mapping[categs[poly['mu_star'].index(max(poly['mu_star']))]])
            # parameter_index = poly['mu_star'].index(max(poly['mu_star']))
            # print(parameter_index)
            # print('len', len(poly['mu_star']))

            values.append(parameter_index)
            # print(parameter_index)
        # print(np.asarray(values))

        nombre_archivo = os.path.join(self.root_path,
                                      'Plot_Map\\{}-season-{}-config-{}'.format(name, season + 1, config + 1))
        parameter_name = ['Slope measure', 'Intercept measure']
        var = '{} \nMost sensitive parameter to watertable depth behavior pattern \n({})'.format(name,
                                                                                                 parameter_name[season])
        unid = 'Parameter'
        # this is to calculate the range for the array--values==
        # escala = np.min(values), np.max(values) (0 - 7 are the index for the 8 parameters)
        escala = np.int32(0), np.int32(7)

        geog = self.Rechna_Doab
        geog.dibujar(archivo=nombre_archivo, valores=values, título=var, unidades=unid,
                     escala_num=escala, categs=P.parametersName4Plot,
                     colores=['#f4f0ed', '#edd712', '#d16f25', '#f6e6bf', '#eeff66', '##FFCC66', '#00CC66', '#66ecff'])

    def plot_map_4_parameter(self, duration, parameter_n, season_n, config_n):
        return None

    @staticmethod
    def compute_linear_trend(SA, evals, poly_id=None):
        trend_result = {'Trend parameters': []}

        poly = poly_id
        print(f'Poly: {poly} is under processing ...')
        for id, sample in enumerate(evals['Watertable depth Tinamit']):
            # if id != 392:
            #     continue
            t_sample = []

            if poly_id is not None:
                n_poly = 1  # for FAST
            else:
                n_poly = SA.n_poly
            for poly_id in range(n_poly):

                # Specific for FAST to make up the vals
                if len(sample[poly_id]) != SA.n_season + 1:
                    new_season_data = []
                    new_season_data.extend(sample[poly_id])
                    new_season_data.extend(evals['Watertable depth Tinamit'][id - 1][poly_id][len(sample[poly_id]):])
                    y_data = new_season_data[3:]
                    # print('y_data', len(y_data))
                else:
                    y_data = sample[poly_id][3:]
                # if poly_id != 199:
                #     continue
                x_data = [i for i in range(18)]

                # print(len(y_data))
                # print(y_data)
                t_sample.append(SA.curve_fit(SA, poly_id, id, x_data, y_data).tolist())
            trend_result['Trend parameters'].append(t_sample)

        with open(os.path.join(SA.root_path, '{}_trend_{}_{}.out'.format(SA.sa_name, SA.name, poly)), 'w') as f:
            # print(len()) # len() would be the first layer of the component
            f.write(json.dumps(trend_result) + '\n')
        return trend_result

    @staticmethod
    def curve_fit(SA, ploy_id, sample_id=0, x_data=None, y_data=None):
        def function(x, a, b):
            return a * x + b

        np.random.seed(0)
        # x_data = np.linspace(-5, 5, num=50)
        # y_data = 2.9 * np.sin(1.5 * x_data) + np.random.normal(size=50)
        params, params_covariance = optimize.curve_fit(function, x_data, y_data, p0=[2.0, 2.0])
        # print(params)
        # SA.plot_trend(x_data, y_data, params, os.path.join(SA.root_path, 'plot_trend/selected poly/poly_{}_in_sample_{}.png'.format(ploy_id, sample_id)))
        return params

    @staticmethod
    def plot_trend(x_data, y_data, params, file_name):
        plt.figure(figsize=(6, 4))
        plt.scatter(x_data, y_data)
        plt.ylabel("Water Table Depth, m")
        plt.xlabel("Simulated Period")
        labels = ['1991 summer', '1992 winter', '1992 summer', '1993 winter', '1993 summer', '1994 winter',
                  '1994 summer',
                  '1995 winter', '1995 summer', '1996 winter', '1996 summer', '1997 winter', '1997 summer',
                  '1998 winter',
                  '1998 summer', '1999 winter', '1999 summer']

        plt.plot(x_data, [(params[0] * i + params[1]) for i in x_data], label='Fitted Regression Line')
        plt.xticks(x_data, labels, rotation='vertical')
        plt.margins(0.01)
        # Tweak spacing to prevent clipping of tick-labels
        plt.subplots_adjust(bottom=0.33)
        plt.legend(loc='best')
        plt.savefig(file_name)
        plt.close()

    @staticmethod
    def plot_ranking_coefficiency(coefficient, file_path, name, cur_season, cur_poly):
        '''plot convergence plot by using rank correlation coefficient.
        :param coefficient:
        :param file_path:
        :param name:
        :param cur_season:
        :param cur_poly:
        :return: plot with x-numbers of BS, y-coefficient
        '''
        plt.plot(coefficient, 'bo-')
        plt.ylabel('Adjusted rank correlation coefficient')
        plt.xlabel('Pairs of bootstrap resamples')
        plt.savefig('{}/{}-{}-{}.png'.format(file_path, name, cur_season, cur_poly))
        plt.close()

    @staticmethod
    def get_top_parameters(p_overlap, p_sensitivity, n_top_p):
        top_parameters = []
        for i in range(n_top_p):
            tmp_i = []
            for j in range(len(p_overlap)):
                t_i = sorted(range(len(p_sensitivity[p_overlap[j]]['mu_star'])),
                             key=lambda i: p_sensitivity[p_overlap[j]]['mu_star'][i], reverse=True)[i]
                # ordered_list = sorted(p_sensitivity[p_overlap[j]]['mu_star'], reverse=True)
                # print(t_i)
                # tmp_i.append(P.parameter_mapping[p_sensitivity[p_overlap[j]]['names'][t_i]])
                tmp_i.append(p_sensitivity[p_overlap[j]]['names'][t_i])
            # print(tmp_i)
            top_parameters.append(SA.find_frequent_string(tmp_i))
        print(top_parameters)

    @staticmethod
    def find_frequent_string(L):
        dict_l = {}
        for e in L:
            if dict_l.keys().__contains__(e):
                dict_l[e] += 1
            else:
                dict_l[e] = 1
        a1_sorted_keys = sorted(dict_l, key=dict_l.get, reverse=True)
        return (a1_sorted_keys[0], dict_l[a1_sorted_keys[0]])

    @staticmethod
    def plot_trend_4_overlap(p_overlap, evals):
        sum_a = 0
        sum_b = 0
        count = 0
        for sample in evals['Trend parameters']:
            for p in p_overlap:
                count += 1
                sum_a += sample[p][0]
                sum_b += sample[p][1]
        a_bar = sum_a / count
        b_bar = sum_b / count
        print(a_bar, b_bar)

        x_data = range(20)
        plt.plot(x_data, [(a_bar * i + b_bar) for i in x_data], label='Fitted Regression Line')
        plt.ylabel("Water Table Depth, m")
        plt.xlabel("Simulated Period")
        plt.show()

    @staticmethod
    def plot_residuals(y_data, x_data=None):
        return sp.residual_plot(y_data, x_data)

    @staticmethod
    def idealregression():
        '''
        idealregression()
        '''
        result = []  # [[{'r2':[], 'residuals':[], }, {}, ...{}]]
        with open(
                'D:\\Thesis\\pythonProject\\Tinamit\\tinamit\\Calib\\SA_algorithms\\Fast\\fa_residual_result_4_polys_winter.out') \
                as f:
            for line in f:
                result.append(json.loads(line))
        f.close()
        good_r2 = []
        for i in range(215):
            count = len([v for v in result[0][i]['R2'] if v > 0.6])  # all season is 'r2'
            print(f'count{i}: ', round(count / 115000, 2))  # / 1200 in Morris
            good_r2.append({'goodr2': count})
        print(good_r2)
