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
from tinamit.Calib.SA_algorithms.Salib_SA import SA
from tinamit.Calib.SA_algorithms import morris as morris2
import operator


class MorrisSA(SA):
    root_path = 'D:\\Thesis\\pythonProject\\local use\\Morris'
    #root_path = 'D:\\Gaby\\Tinamit\\tinamit\\Calib\\SA_algorithms\\Morris'

    # 0. Site geography

    def __init__(self, config, name):
        super().__init__('Morris')
        self.n_poly = config[0]
        self.n_sampling = config[2]
        self.n_paras = config[1]
        self.n_level = config[3]
        self.name = name
        self.n_season = config[4]

    def sampling2(self, problem):
        '''
        generate SAlib sampling output
        :type list: [[]]
        :param problem:
        :return: param_values # list [[]] two layer = Ns * 23
        '''
        param_values = sample(problem, self.n_sampling, num_levels=self.n_level, grid_jump=self.n_level / 2,
                              optimal_trajectories=None)

        with open(os.path.join(self.root_path, '{}_Sampling_{}.out'.format(self.sa_name,
                self.name)), 'w') as f1:

            f1.write('{}\n'.format(json.dumps(param_values.tolist())))  # json: list --> structurazation
            f1.flush()
        # parameters_set.append(fast_sampler.sample(p_s, N)) format is 215*Ns*n_parameters (Ns = N * n_parameters)
        f1.close()
        return param_values

    def analyze2(self, evals, parameters_set, problem):
        '''

        :param evals: [Ns*215*n_season]; evals = mor.simulation2(parameters_set)
        :param parameters_set: [Ns*23]
        :param problem: {var: , name: [], bounds: []}
        :return: duration_all_si [{'WTD': [{}]}], 20*215 dicts with key of mu, mu_star; and their values
        '''

        # SA_FAST: PORCESS & WRITE, process first and write the timestep data into the file
        # r+ --> write and read

        duration_all_si = []  # restore si for all seasons

        # var: 'WTD', res: 1200*215*20
        for var, res in evals.items():
            evals_transpose = np.asarray(res).transpose() #from 1200*215*20 to 20*215*1200
            print(evals_transpose.shape) #20*215*1200

            # fw = open(os.path.join(self.root_path, 'morris_ranking_coefficiency_{}_{}.out'.format(
            #     self.name, var)), 'w' )
            for j, duration in enumerate(evals_transpose):
                # for a, b in enumerate(list), give each of the inner layers[b] an index[a]
                # duration : j= n_seasons, [duration 215 * 1200]; eg., j=1, duration=215*1200

                #skip the first data in simulation since it is the initial data
                if j == 0:
                    continue

                duration_si = []

                for i, poly_data in enumerate(duration):
                    # poly_data : poly_data=1200=(23+1)*50 times of simulation
                    # i = (1, 215), poly_data=1200 vals in each i; i=1, polydata=215*1200
                    print('Conduct Sensitivity analysis for polygon', i, 'in season', j)
                    dict_Si = {} #dict_Si = {dict} {'Watertable depth Tinamit': {'names': ['Ptq - s1', 'Ptr - s1', 'Kaq - s1', 'Peq - s1', 'Pex - s1', 'Ptq - s2', 'Ptr - s2', 'Kaq - s2', 'Peq - s2', 'Pex - s2', 'Ptq - s3', 'Ptr - s3', 'Kaq - s3', 'Peq - s3', 'Pex - s3', 'Ptq - s4', 'Ptr - s4', 'Kaq - s4', … View
                    # parameters_set=model input=Ns*23, poly_data=model output=1200samples for each of 215s
                    Si = morris2.analyze(problem, parameters_set, poly_data, conf_level=0.95,
                                        print_to_console=False,
                                        num_levels=self.n_level, grid_jump=self.n_level / 2,
                                        num_resamples=None)

                    dict_Si_var = {} #return a dict with only lists, not nparray
                    for k, v in Si.items():
                        if isinstance(v, np.ndarray): # if the values in Si is nparray, if it's a nparray, tolist(),if not, return itself
                            n_v = v.tolist()
                            dict_Si_var[k] = n_v # match the list switched from the nparray to its key.
                        else:
                            dict_Si_var[k] = v

                    duration_si.append(dict_Si_var) #put all 215 dicts to a list as an output
                    #print('duration_si', duration_si)
                duration_all_si.append(duration_si) #return all 20 seasons*215poly ranking SA results into a dict
        with open(os.path.join(self.root_path, 'morris_sensitivity_{}.out'.format(
                self.name)), 'w') as f0:
            f0.write(('{}\n').format(json.dumps(duration_all_si)))
        # duration_all_si [each season[each polygon{name, mu, mu_star, sigma, mu_start_conf}]]
        return duration_all_si

    @staticmethod
    def load_segmented_data_from_file(self, root_path, start, end):
        '''
        load divisional simulated data from file
        :param self:
        :param root_path: path to restore those files
        :param start: start point
        :param end:
        :return: evals
        '''
        evals = []
        for i in range(start, end + 1):
            with open(os.path.join(root_path, 'morris_simulation_{}_{}.out'.format(self.name, i)), 'r') as fr:
                for line in fr:
                    print(line)
                    evals.append(json.loads(line))
        return evals

    def plot_result(self, poly_id, duration_all_si, savepath):
        '''
        integrate two X--mu_star to Y--sigma plots in two seasons into one plot for comparison
        :param poly_id: from 1 to 215
        :param duration_all_si: all Si after SA #20*215
        :param savepath: the path to save the plotting result (SA_algorithms\previous runs\morrisFigure)
        :return:
        '''
        figname = '{}-{}={}'.format(poly_id + 1, self.n_level, self.n_sampling) # self.n_sampling = base samping (25 or 50)
        plt.figure(figname)
        plt.suptitle('p={}, r={}, poly_n={}'.format(self.n_level, self.n_sampling, poly_id + 1))#suptitle is the name inside each plot
        name = ['Ptq',
                'Ptr',
                'Kaq1',
                'Kaq2',
                'Kaq3',
                'Kaq4',
                'Peq',
                'Pex']

        for i, duration in enumerate(duration_all_si):
            if i == len(duration_all_si) - 1: # i = (1, 20), duration = each of the 215s, before was 2 seasons
                continue
            plt.subplot('13{}'.format(i + 1))
            if i == 0:
                plt.ylabel('Sigma')
            plt.xlabel('Mu_star')
            plt.title('season {}'.format(i + 1))
            mu = duration[poly_id]['mu_star'] # take the mu_star value with selected poly_id
            sigma = duration[poly_id]['sigma']
            # ax = plt.gca() returns the current axes

            for k, txt in enumerate(name):
                plt.gca().annotate(txt, (mu[k], sigma[k]))
            plt.gca().scatter(mu, sigma)
        # plt.ylabel('Sigma')
        plt.savefig('{}/{}-{}-{}.png'.format(savepath, poly_id, self.n_level, self.n_sampling))
        plt.close(figname)

    def plot_map_4_parameter(self, duration, parameter_n, season_n, config_n):
        '''
        Plot 215 maps in one specified season
        :param duration: 215*23dicts (take one season from 20 seasons)
        :param parameter_n: 23 paramter names
        :param season_n: (0, 20)
        :param config_n:
        :return:
        :path: SA_algorithms\Morris\plot_map_4_parameter
        '''
        name = self.problem['names']
        if not isinstance(parameter_n, int) \
                or not isinstance(season_n, int) or not isinstance(config_n, int):
            return 'parameter type error!'

        mu_star_in_polys = [] # 215 mu_star values in one season
        for poly in duration: # duration = 215 * dict(23 dicts), poly=(1, 215)
            mu_stars = [] # append mu_star in each poly into a list
            for value in poly['mu_star']: # value is one mu_star value in each poly
                mu_stars.append(value) # append one mu_star tolist
            mu_star_in_polys.append(mu_stars) #append all 215 mu_star tolist

        mu_star_in_polys = np.asarray(mu_star_in_polys).transpose() # from 215*23 to 23*215
        values = mu_star_in_polys[parameter_n] # each of 23 params has 215 mu_star values, append thoes to the values list
        # print(values)

        nombre_archivo = os.path.join(self.root_path,
                                      'plot_map_4_parameter\\Morris-parameter-{}-season-{}-config-{}'.format(
                                          parameter_n + 1, season_n + 1, config_n + 1))
        var = "Morris \nSensitivity index <{}> in each polygon in season {} \n Configuration {}\n Morris".format(
            name[parameter_n], season_n + 1, config_n + 1)
        unid = 'Sensitivity Index'
        # this is to calculate the range for the array--values
        escala = np.min(values), np.max(values) #minim and maxi values of mu_star for each parameter among all polys
        # escala = np.int32(0), np.int32(7)

        geog = self.Rechna_Doab
        colores = ['#f6e6bf', '#eeff66', '##FFCC66', '#00CC66', '#66ecff', '#6669ff', '#e766ff', '#6920dd']
        geog.dibujar(archivo=nombre_archivo, valores=values, título=var, unidades=unid,
                     colores=colores, escala_num=escala)


    # for BREE 509
    def get_data(self, filename, num_poly, id_sample, name):
        '''
        from the specified polygons with 20 seasons from their segmented simulation files
        :param filename:
        :param num_poly:
        :param id_sample:
        :param name:
        :return:
        '''
        result = [] #{'WTD': [215[20 seaons]]}
        with open(os.path.join(self.root_path, 'morris_simulation_{}_{}.out'.format(self.name, filename)), 'r') as fr:
            for line in fr:
                result.append(json.loads(line))
        specified_poly = []
        specified_poly.append(result[0]['Watertable depth Tinamit'][19][6])
        specified_poly.append(result[0]['Watertable depth Tinamit'][19][79])
        specified_poly.append(result[0]['Watertable depth Tinamit'][19][142])
        specified_poly.append(result[0]['Watertable depth Tinamit'][19][214])
        print(specified_poly)
        return

def get_existing_simulated_result(morris, start_group):
    '''
    Load simulated data from existing files from group 0 to start_group
    :param start_group:
    :return: simulated data
    '''
    result = {'Watertable depth Tinamit': []}
    for i in range(start_group):
        with open(os.path.join(morris.root_path, 'Morris_simulation_{}_{}.out'.format(4, i)), 'r') as f:
            for line in f:
                print(len(json.loads(line)['Watertable depth Tinamit'])) # len=25
                result['Watertable depth Tinamit'] += json.loads(line)['Watertable depth Tinamit']
        print('result', i, len(result['Watertable depth Tinamit']))
    return result

def load_unsimulated_list(morris, n_group):
    '''
    load un-simulated sampling data from group 0 to n_group
    :param n_group:
    :return: sampling data
    '''
    list_dic_set = []
    for i in range(n_group + 1):
        with open(os.path.join(morris.root_path, 'Morris_temp_list_data_{}_{}.out'.format(morris.name, i)),
                  'r') as f:
            for line in f:
                list_dic_set.append(json.loads(line))
    return list_dic_set

def restart_sa_from_file(morris, start_group, n_group):
    '''
    restart the morris according to the last cash group
    :param morris:
    :param start_group:
    :param n_group:
    :return:
    '''
    result = get_existing_simulated_result(morris, start_group)
    list_dic_set = load_unsimulated_list(morris, n_group)
    start_time = time.time()

    for i, list in enumerate(list_dic_set):
        if i < start_group:
            continue
        print("This is group {} of total {}".format(i, list_dic_set.__len__()))
        try:
            list_result = GS.simulation(list, morris.n_season, nombre=morris.sa_name)
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
        with open(os.path.join(morris.root_path, '{}_simulation_{}_{}.out'.format(morris.sa_name, morris.name, i)), 'w') as f:
            # print(len()) # len() would be the first layer of the component
            f.write(json.dumps(results_json) + '\n')

    print("--- %s total seconds ---" % (time.time() - start_time))  # will only show once at the end
    return result

def conduct_SA_from_configs(config, specific_config=None):
    '''

    :param config:
    :param specific_config:
    :return:
    '''
    # SIMULATION on problem
    for i, conf in enumerate(config):
        # if crash
        if specific_config != None:
            if i != specific_config:
                continue
        mor = MorrisSA(conf, i)
        problem = mor.problems_setup2()
        parameters_set = mor.sampling2(problem)
        evals = mor.simulation2(parameters_set)
        mor.analyze2(evals, parameters_set, problem)

def conduct_SA_dummy_from_configs(config, specific_config=None):
    '''

    :param config:
    :param specific_config: 4
    :return:
    '''
    # SIMULATION on problem
    # for i, conf in enumerate(config):
    #     # if crash
    #     if specific_config != None:
    #         if i != specific_config:
    #             continue
    #     mor = MorrisSA(conf, i)
    #     problem = mor.problems_setup_plus_dummy()
    #     parameters_set = mor.sampling2(problem)
    #     evals = mor.simulation2(parameters_set)
    #     mor.analyze2(evals, parameters_set, problem)

    mor = MorrisSA(config[specific_config], specific_config)
    problem = mor.problems_setup_plus_dummy()
    parameters_set = np.asarray(mor.load_parameters_sampling(os.path.join(mor.root_path, "Morris_Sampling_4.out")))
    evals = restart_sa_from_file(mor, 31, 49)

    mor.analyze2(evals, parameters_set, problem)


def conduct_SA_from_sampling_files(config, name, sampling_file_name):
    '''
    invoke model simualtion
    :param config:
    :param name:
    :param sampling_file_name:
    :return:
    '''
    mor = MorrisSA(config, name)
    problem = mor.problems_setup2()
    # os.path.join(mor.root_path, 'previous simulation//10 years//0407 run N=50 P=16//Morris_Sampling_{}.out'.format(0))
    parameters_set = np.asarray(mor.load_parameters_sampling(os.path.join(mor.root_path, sampling_file_name)))
    evals = mor.simulation2(parameters_set)
    mor.analyze2(evals, parameters_set, problem)

def conduct_analysis_from_files(config, name, sampling_file_name, n_similuated_result, is_dummy=False):
    '''
    Use exiting simulated data
    :param config: eg., config[3]
    :param name: number of config; eg., 3
    :param sampling_file_name: path
    :param n_similuated_result: n_similuated_result = Ns/intercept; eg., 1200/25 = 48
    :return:
    '''
    mor = MorrisSA(config, name)
    if is_dummy:
        problem = mor.problems_setup_plus_dummy()
    else:
        problem = mor.problems_setup2()
    # os.path.join(mor.root_path, 'previous simulation//10 years//0407 run N=50 P=16//Morris_Sampling_{}.out'.format(0))
    parameters_set = np.asarray(mor.load_parameters_sampling(os.path.join(mor.root_path, sampling_file_name)))
    evals = get_existing_simulated_result(mor, n_similuated_result)
    mor.analyze2(evals, parameters_set, problem)

def conduct_trend_analysis_from_files(config, name, sampling_file_name, n_similuated_result):
    '''

    :param config:
    :param name:
    :param sampling_file_name:
    :param n_similuated_result: n_similuated_result = 48, if base sample = 50
    :return:
    '''
    mor = MorrisSA(config, name)
    problem = mor.problems_setup2()
    # os.path.join(mor.root_path, 'previous simulation//10 years//0407 run N=50 P=16//Morris_Sampling_{}.out'.format(0))
    parameters_set = np.asarray(mor.load_parameters_sampling(os.path.join(mor.root_path, sampling_file_name)))
    evals = get_existing_simulated_result(mor, n_similuated_result)
    evals = mor.compute_linear_trend(mor, evals)
    mor.analyze2(evals, parameters_set, problem)

def plot_trend_4_overlap(config, name, poly_list, trend_data_filename):
    '''

    :param config:
    :param name:
    :param poly_list: e.g. [86, 54, 44] 针对list里面的值进行趋势分析
    :param trend_data_filename: D:\\Thesis\\pythonProject\\Tinamit\\tinamit\\Calib\\SA_algorithms\\Morris\\Morris_trend_3.out
    :return:
    '''
    mor = MorrisSA(config, name)
    evals = mor.load_data_from_file(mor, trend_data_filename)
    mor.plot_trend_4_overlap(poly_list, evals)

def poly_select_criteria(config, name, sensitivity_data_filename, n_top_params):
    '''

    :param config:
    :param name: 3
    :param sensitivity_data_filename: os.path.join(mor.root_path, 'morris_sensitivity_3.out')
    :param n_top_params: e.g. 4
    :return:
    '''
    mor = MorrisSA(config, name)
    duration_all_si = mor.load_sensitivity_data(sensitivity_data_filename)[0]
    for season in range(2):
        #mor.plot_map(duration_all_si[season], 0, season)
        mor.get_top_parameters(SC.M1, duration_all_si[season], n_top_params)
        mor.get_top_parameters(SC.M2, duration_all_si[season], n_top_params)
        mor.get_top_parameters(SC.M3, duration_all_si[season], n_top_params)
        mor.get_top_parameters(SC.H4, duration_all_si[season], n_top_params)
# poly_select_criteria(config[3], 3, os.path.join(mor.root_path, 'morris_sensitivity_3.out'), 4)

def convergence_rate(config, name, converge_data_filename):
    '''
    for all polygons in each season: e.g. 20 values for 20 seasons
    :param config:
    :param name:
    :param converge_data_filename: '\\previous simulation\\BS\\BS-50\\0422 Config 4\\morris_sensitivity_3.out'
    :return:
    '''
    mor = MorrisSA(config, name)
    sensitivity_data = mor.load_sensitivity_data(mor.root_path + converge_data_filename)
    convergence_percentage_4_seasons = []
    for season in sensitivity_data[0]:
        converged = 0
        for poly in season:
            if poly['convergence'] == 1:
                converged += 1
        convergence_percentage_4_seasons.append(converged / mor.n_poly)
    print(convergence_percentage_4_seasons)
# convergence_rate(config[3],3, '\\previous simulation\\BS\\BS-50\\0422 Config 4\\morris_sensitivity_3.out')

def compute_avearage_simulate_values_4_classes(config, name, simulation_filename, sampling_file_name=None):
    '''
    Compute the mean value for each of 11 classes of trend (a, b)
    :param config:
    :param name:
    :param simulation_filename:
    :param sampling_file_name:
    :return:
    compute_avearage_simulate_values_4_classes(config[3], 3, 'Morris_trend_3.out',
                                               'previous simulation//10 years//0407 run N=50 P=16//Morris_Sampling_{}.out'.format(0))
    '''
    categories = [SC.H1, SC.H2, SC.H3, SC.M1, SC.M2, SC.M3, SC.M4, SC.T1, SC.T2, SC.T3, SC.T4]
    average_4_categories = []
    mor = MorrisSA(config, name)
    evals = np.asarray(mor.load_data_from_file(mor, simulation_filename)['Trend parameters'])
    for sample in evals:
        sample_ave = []
        for category in categories:
            sample_ave.append(mor.compute_average_simuluation_value_4_polys(category, sample))
        average_4_categories.append(sample_ave)

    average_4_categories = {'Average Class Sim for ab':average_4_categories}

    if sampling_file_name is not None:
        problem = mor.problems_setup2()
        # os.path.join(mor.root_path, 'previous simulation//10 years//0407 run N=50 P=16//Morris_Sampling_{}.out'.format(0))
        parameters_set = np.asarray(mor.load_parameters_sampling(os.path.join(mor.root_path, sampling_file_name)))
        mor.analyze2(average_4_categories, parameters_set, problem)

    with open(f'{mor.root_path}/{mor.sa_name}_average_class_sim_data_{mor.name}.out', 'w') as f:
        f.write(json.dumps(average_4_categories))
    # for i, ave in enumerate(average_4_categories):
    #     print(i + 1, ave)
    # return average_4_categories

def compute_last_n_ave_simulation(config, name, sampling_filename, n_similuated_result):
    '''
    Compute the last and mean seasonal values for each of the 11 classes
    :param config:
    :param name:
    :param sampling_filename:
    :param n_similuated_result:
    :return:
    compute_last_n_ave_simulation(config[3], 3,
                                  'previous simulation//10 years//0407 run N=50 P=16//Morris_Sampling_{}.out'.format(0),
                                  n_similuated_result=48)
    '''
    mor = MorrisSA(config, name)
    problem = mor.problems_setup2()
    parameter_sets = np.asarray(mor.load_parameters_sampling(os.path.join(mor.root_path, sampling_filename)))

    last_n_ave_data = []
    evals = get_existing_simulated_result(mor, n_similuated_result)['Watertable depth Tinamit']
    categories = [SC.H1, SC.H2, SC.H3, SC.M1, SC.M2, SC.M3, SC.M4, SC.T1, SC.T2, SC.T3, SC.T4]
    for sample in evals:
        sample_ave = []
        for category in categories:
            sample_ave.append(mor.get_last_and_ave_simulation_value(category, sample, skip_firt_season=True))
        last_n_ave_data.append(sample_ave)

    last_n_ave_data = {'Last and Average simulation data':last_n_ave_data}
    mor.analyze2(last_n_ave_data, parameter_sets, problem)

    with open(f'{mor.root_path}/{mor.sa_name}_last_and_average_sim_data_{mor.name}.out', 'w') as f:
        f.write(json.dumps(last_n_ave_data))

def plot_residual(config, name, filename):
    mor = MorrisSA(config, name)
    eval = get_existing_simulated_result(mor, 48)['Watertable depth Tinamit']

    all_residuals = []
    all_residuals_s = []
    all_residuals_w = []
    for poly in range(mor.n_poly):
        print(f'\npolygon {poly}')
        # summar data
        # poly_eval_s = []
        # for sample in eval:
        #     for i in range(3, mor.n_season):
        #         if i % 2 == 1:
        #             poly_eval_s.append()

        # poly_eval_s = [[sample[poly][i] for i in range(3, mor.n_season) if i % 2 == 1] for sample in eval] # summer
        # poly_eval_w = [[sample[poly][i] for i in range(3, mor.n_season) if i % 2 == 0] for sample in eval] # winter
        # print(poly_eval_s)
        poly_eval = ([sample[poly][3:] for sample in eval])
        res = mor.plot_residuals(poly_eval)
        # res_s = mor.plot_residuals(poly_eval_s)
        # res_w = mor.plot_residuals(poly_eval_w)
        res['poly_id'] = poly
        all_residuals.append(res)
        # res_s['poly_id'] = poly
        # res_w['poly_id'] = poly
        # all_residuals_s.append(res_s)
        # all_residuals_w.append(res_w)

    # with open(os.path.join(mor.root_path, 'residual_result_4_polys_summer.out'), 'w') as fw:
    #     fw.write(json.dumps(all_residuals_s))
    # fw.close()
    # with open(os.path.join(mor.root_path, 'residual_result_4_polys_winter.out'), 'w') as fw:
    #     fw.write(json.dumps(all_residuals_w))
    # fw.close()
    with open(os.path.join(mor.root_path, 'residual_result_4_polys_all.out'), 'w') as fw:
        fw.write(json.dumps(all_residuals))
    fw.close()

def compute_r2_analysis(config, name, sampling_file_name, r2_filename):
    def load_r2_data(r2_filename):
        r2_data = []
        with open(os.path.join(mor.root_path, r2_filename), 'r') as fr:
            for line in fr:
                r2_data.append(json.loads(line))
        fr.close()

        eval = {'R2_sa': []}
        for i in range(1200):
            tmp = []
            for j in range(215):
                tmp.append([r2_data[0][j]['R2'][i]])
                #eval[i][j][0] = r2_data[0][j]['R2'][i]
            eval['R2_sa'].append(tmp)
        #print(eval)
        return eval


    mor = MorrisSA(config, name)
    eval = load_r2_data(r2_filename)
    problem = mor.problems_setup2()
    # os.path.join(mor.root_path, 'previous simulation//10 years//0407 run N=50 P=16//Morris_Sampling_{}.out'.format(0))
    parameters_set = np.asarray(mor.load_parameters_sampling(os.path.join(mor.root_path, sampling_file_name)))
    mor.analyze2(eval, parameters_set, problem)


if __name__ == '__main__':

    config = [
        # n_poly, n_paras, n_sampling, n_level, n_season
        [215, 23, 25, 8, 20],
        [215, 23, 50, 8, 20],
        [215, 23, 25, 16, 20],
        [215, 23, 50, 16, 20],#24*25*20=12,000(6000)
        [215, 24, 50, 16, 20] #dummy
    ]

    #conduct_SA_dummy_from_configs(config, 4)
    #conduct_analysis_from_files(config[4], 4, 'Morris_Sampling_4.out', 50, is_dummy=True)
    # compute_r2_analysis(config[3], 0, 'previous simulation//10 years//0407 run N=50 P=16//Morris_Sampling_{}.out'.format(0),
    #                     'residual_result_4_polys_all.out')
    # compute_avearage_simulate_values_4_classes(config[3], 3, 'Morris_trend_3.out',
    #                                            'previous simulation//10 years//0407 run N=50 P=16//Morris_Sampling_{}.out'.format(0))

    # compute_last_n_ave_simulation(config[3], 3, 'previous simulation//10 years//0407 run N=50 P=16//Morris_Sampling_{}.out'.format(0),
    #                               n_similuated_result=48)


    # evals = mor.load_data_from_file(mor, 'Morris_trend_3.out')
    mor = MorrisSA(config[3], name=3)
    problem = mor.problems_setup2()
    sampling_set = mor.sampling2(problem)
    lol = mor.simulation2(parameters_set=sampling_set)


    # # os.path.join(mor.root_path, 'previous simulation//10 years//0407 run N=50 P=16//Morris_Sampling_{}.out'.format(0))
    # parameters_set = np.asarray(mor.load_parameters_sampling(os.path.join(mor.root_path, 'previous simulation//10 years//0407 run N=50 P=16//Morris_Sampling_{}.out'.format(0))))
    # mor.analyze2(evals, parameters_set, problem)
    # sensitivity_of_ab = mor.load_sensitivity_data(os.path.join(mor.root_path, 'morris_sensitivity_ab_3.out'))
    # influential_param_a = [ {poly['names'][i]:mu_star for i, mu_star in enumerate(poly['mu_star']) if mu_star > 0.1} for poly in sensitivity_of_ab[0][0]]
    # influential_param_b = sensitivity_of_ab[0][1]
    # print()

    # GET the influential param of WTD
    # mor = MorrisSA(config[3], name=3)
    # sensitivity_of_ab = mor.load_sensitivity_data(os.path.join(mor.root_path, 'morris_sensitivity_ab_3.out'))
    # influential_param_of_wtd = [{poly['names'][i]: mu_star for i, mu_star in enumerate(poly['mu_star']) if mu_star > 0.1} for
    #                        poly in sensitivity_of_ab[0][1]] #[0][0] for a; [0][1] for b
    # for i, param in enumerate(influential_param_of_wtd):
    #     print(f'trend_b_poly_id:{i + 1}', f'influential:{len(param)}, non:{23 - len(param)}', '\n', param)

    #Dummy variable
    # mor = MorrisSA(config[4], name=4)
    # sensitivity_of_dummy = mor.load_sensitivity_data(os.path.join(mor.root_path, 'morris_sensitivity_4.out'))[0]
    # influential_param_of_wtd = [[{'Dummy parameter': poly['mu_star'][23]} for poly in season] for season in sensitivity_of_dummy]
    # #influential_param_of_wtd = [{poly['names']['Dummy parameter']: mu_star for poly['mu_star'][23] in sensitivity_of_dummy[0][0]] #[0][0] for a; [0][1] for b
    # for i, param in enumerate(influential_param_of_wtd):
    #     print(f"dummy SI:{param}")
    # print()


    '''
    Get the influential param of R2
    Mor --> important factor: mean si > CT (0.1); non-influential: mean si < CT; inter: mustar>0.1, sigma>cone line(mustar*sqrt(50)/2)
    EFAST --> important factor: mean si > CT1; non-influential: mean si < CT1(0.01), St < CT2(0.1); [ct2 = st-s1] interaction 
    (mu_star Vs Si for FP, mu_star Vs St + sigma Vs St for FF )
    '''
#     mor = MorrisSA(config[3], name=3)
#     sensitivity_of_r2 = mor.load_sensitivity_data(os.path.join(mor.root_path, 'morris_sensitivity_gof_R2.out'))
#     influential_param_of_r2 = [{poly['names'][i]: mu_star for i, mu_star in enumerate(poly['mu_star']) if mu_star > 0.1} for
#                            poly in influential_param_of_r2[0][0]] #[0][0] for a; [0][1] for b
#     for i, param in enumerate(influential_param_of_r2):
#         print(f'trend_b_poly_id:{i + 1}', f'influential:{len(param)}, non:{23 - len(param)}', '\n', param)
#
#     interaction_r2_sigma = []
#         for r2 in sensitivity_of_r2[0][0]: #r2 = 215{'name':[], 'mustar':[]...}
#         cone_line = ['mu_star'] / 2 * math.sqrt(50)
#         interaction = []
#         for j in range(23):  # j = 23
#             if r2['mu_star'][j] > 0.1 and r2['sigma'][j] > r2['mu_star'] / 2 * math.sqrt(50):  # > cone_line?
#                 # print(fa.problem['names'][j], (i['mu_star'][j], i['ST'][j] ))
#                 interaction.append({fa.problem['names'][j]: (r2['mu_star'][j], r2['sigma'][j])})
# noninfluential_param_of_wtd.append(ab_trend)
#
#         for i, param in enumerate(noninfluential_param_of_wtd):
#             print(f'ab{i+1}', f'non:{len(param)},influential:{23 - len(param)}', param)
#
#         print()
#
#     print()


    #print(influential_param_of_wtd)

    # conduct_SA_from_sampling_files(config[3], 3, 'Morris_Sampling_{}.out'.format(0))
    # mor = MorrisSA(config[3], 3)
    # sensitivity_data = mor.load_sensitivity_data(mor.root_path +
    #     '\\morris_sensitivity_3.out')

    # conduct_trend_analysis_from_files(config[3], 3,
    #                                'previous simulation//10 years//0407 run N=50 P=16//Morris_Sampling_{}.out'.format(
    #                                    0),48)
    # mor = MorrisSA(config[3], 3)
    # sensitivity_data = mor.load_sensitivity_data(mor.root_path +
    #                                              '\\morris_sensitivity_ss_3.out')

    # conduct_analysis_from_files(config[3], 3, 'previous simulation//10 years//0407 run N=50 P=16//Morris_Sampling_{}.out'.format(0), 48)

    # all_mustar = []
    # for para in sensitivity_data[0]:
    #     mu_stat_for_slope = []
    #     print()
    #     for i, poly in enumerate(para):
    #         tmp_dict = {poly['names'][i]: poly['mu_star'][i] for i in range(mor.n_paras)}
    #         orderwed_dict = sorted(tmp_dict.items(), key=operator.itemgetter(1), reverse=True)
    #         str = []
    #         for i in range(len(orderwed_dict)):
    #             str.append(orderwed_dict[i][0])
    #             str.append(orderwed_dict[i][1])
    #         print(str)

            #print('polygon ', i, poly['mu_star'])
            # for value in poly['mu_star']:
            #     mu_stat_for_slope.append(value)
            #     print(mu_stat_for_slope)

    # for season in range(mor.n_season):
    #     for p in range(mor.n_paras):
    #         mor.plot_map_4_parameter(duration_all_si[season], p, season, 0)


    # PLOTTING
    # for i, conf in enumerate(config):
    #     if i != 0:
    #         continue
    #     mor = MorrisSA(conf, i)
    #     problems = mor.problems_setup2()
        # sensitivity_data = mor.load_sensitivity_data('D:\\Gaby\\Tinamit\\tinamit\\Calib\\SA_algorithms\\previous runs\\Morris Runs\\morris_sensitivity_0.out')
        # parameters_set = np.asarray(mor.load_parameters_sampling(
        #     os.path.join(mor.root_path, 'morris_simulation_{}_{}.out'.format(mor.name, i))))
    #
    #     sampling_parameters_set = []
    #     for l in range(len(parameters_set[0])):
    #         sampling2 = []
    #         for j in range(mor.n_paras):
    #             parameters = []
    #             for k in range(mor.n_poly):
    #                 parameters.append(parameters_set[k][l][j])
    #             sampling2.append(parameters)
    #             # print(min(parameters), max(parameters))
    #         sampling_parameters_set.append(sampling2)
        #
        # print(len(sampling_parameters_set))
        # print(sampling_parameters_set[0])
        # print(sampling_parameters_set[1])
        # evals is size of (n_paras + 1)*n_sampling*n_poly*n_season 3-D matrix
        # evals = mor.load_data_from_file(mor, 'morris_simulation_{}.out'.format(i))
        # print(len(evals))
        # print(evals[0])
        # print(evals[1])
        # duration_all_si = mor.analyze(evals, parameters_set, problems)

    # print(len(duration_all_si))
    # mor = MorrisSA(config(3), 3)
    # mor.plot_map(duration_all_si[1], i, 1)
    # for j in range(mor.n_poly): #j = 215
    #     mor.plot_result(j, duration_all_si,
    #       'D:\\Thesis\\pythonProject\\Tinamit\\tinamit\\Calib\\SA_algorithms\\previous runs\\morrisFigure')

    # mor = MorrisSA(config(3), 3)
    # duration_all_si = mor.load_sensitivity_data(os.path.join(mor.root_path, 'morris_sensitivity_3.out')[0]
    # for season in range(config[4]):
    #    mor.plot_map(duration_all_si[season], config(3)), season)

    # for season in range(conf[4] - 1):
    #     for p in range(conf[1]):
    #         mor.plot_map_4_parameter(duration_all_si[season], p, season, i)

    # mor.plot_result(63, sensitivity_data)
    # mor.plot_result(73, sensitivity_data)
    # mor.plot_result(74, sensitivity_data)

    # CURVE FITTING
    # mor = MorrisSA(config[0], 0)
    # evals = MorrisSA.load_segmented_data_from_file(mor, mor.root_path, 14, 14)[0]['Watertable depth Tinamit']
    # # [25,8]-->sim_14; [25,16]-->sim_15; [50,8]-->sim_30; [50,16]-->sim_46
    # evals = MorrisSA.load_data_from_file(MorrisSA,'Simulation\\morris_simulation_{}.out'.format(0))
    # evals = get_existing_simulated_result(mor, 48)['Watertable depth Tinamit'] # the same as line 558

    # trend HERE
    # print(len(evals))
    # print(len(evals[0]))
    # print(len(evals[0][0]))
    # for id, sample in enumerate(evals):
    #     # if id > 2:
    #     #     continue
    #     for poly_id in range(mor.n_poly):
    #         x_data = [i for i in range(21)]
    #         y_data = sample[poly_id]
    #         # print(len(y_data))
    #         # print(y_data)
    #         MorrisSA.curve_fit(mor, poly_id, id, x_data, y_data)
    # plt.show()

