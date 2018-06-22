import sys
import os
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
from tinamit.Calib.SA_algorithms.Salib_SA import SA
from tinamit.Calib.SA_algorithms import fast

class FastSa(SA):
    root_path = 'D:\\Thesis\\pythonProject\\Tinamit\\tinamit\\Calib\\SA_algorithms\\FAST'
    #root_path = 'D:\\Gaby\\Tinamit\\tinamit\\Calib\\SA_algorithms\\FAST'

    def __init__(self, config, name):
        super().__init__('Fast')
        self.n_poly = config[0]
        self.n_sampling = config[1]
        self.n_paras = config[2]
        self.n_season = config[3]
        self.name = name

    def sampling2(self, problem):
        '''
        Conduct EFast sampling for the simulation: list
        :param problem: 
        :return: param_values [[23]215]
        '''
        param_values = fast_sampler.sample(problem, self.n_sampling)
        print(len(param_values))
        #print(param_values) = 600 * 23 --> [[]] only two.

        with open(os.path.join(self.root_path, 'Fast_Sampling_{}.out'.format(
                self.name)), 'w') as f1:

            f1.write('{}\n'.format(json.dumps(param_values.tolist())))  # json: list --> structurazation
            f1.flush()
        # parameters_set.append(fast_sampler.sample(p_s, N)) format is 215*Ns*n_parameters (Ns = N * n_parameters)
        f1.close()
        return param_values

    def start_simulation_from_file(self):
        def read_data_from_file(group_id):
            list_dic_set = []
            with open(os.path.join(self.root_path, '{}_temp_list_data_{}_{}.out'.format(self.sa_name,
                                                                                        self.name, group_id)),
                      'r') as fr:
                for line in fr:
                    list_dic_set.append(json.loads(line))
                    # print(json.loads(line)) # everything in the file is 'str' type --> 'dict'
            fr.close()
            return list_dic_set

        start_time = time.time()  # return current time for recoding current runtime
        print('Start to preparing data for simulation')
        group_count = 575

        result = {'Watertable depth Tinamit': []}
        for i in range(group_count):
            if i == 0:
                continue
            print("This is group {} of total {}".format(i, group_count - 1))
            # list_result = GS.simulation(list, self.n_season, nombre=self.sa_name)
            data = read_data_from_file(i)[0]

            try:
                list_result = GS.simulation(data, self.n_season, nombre=self.sa_name)
            except Exception as inst:
                print(inst)
                print('this is {} run'.format(i), list)
                #     # return

                #result['Watertable depth Tinamit'] += list_result['Watertable depth Tinamit']

            # print('Finished sampling ', ' ', result)
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


    def analyze2(self, evals, problem, poly_id=None, is_trend_analysis=False):
        # evals : [90*215*3], parameters_set: [215*90*8], problems_t: [215]
        # SA_FAST: PORCESS & WRITE, process first and write the timestep data into the file
        # write the results into the 'sensitivity.out'
        # r+ --> write and read

        duration_all_si = []  # restore the result of si for all seasons

        for var, res in evals.items():
            # evals_transpose = np.asarray(res).transpose()  # from 90*215*10 to 10*215*90
            # print(evals_transpose.shape)
            if not is_trend_analysis:
                evals_transpose = []
                count = 0

                for i in range(self.n_season + 1):
                    sampling = []
                    if poly_id is not None:
                        number_of_poly = 1
                    else:
                        number_of_poly = self.n_poly
                    for j in range(number_of_poly):
                        parameters = []
                        for k in range(len(res)):

                            if len(res[k][j]) != self.n_season + 1 and len(res[k][j]) != 2:
                                count += 1
                                # print('Error count', count)
                                # print('season =', i, 'poly =', j, 'sample id =', k)
                                # print(res[k][j])
                                new_season_data = []
                                new_season_data.extend(res[k][j])
                                new_season_data.extend(res[k - 1][j][len(res[k][j]):])
                                # print('Completed season data:', new_season_data)
                                # parameters.append(new_season_data)
                                parameters.append(new_season_data[i])
                            else:
                                parameters.append(res[k][j][i])
                        sampling.append(parameters)
                    evals_transpose.append(sampling)

                evals_transpose = np.asarray(evals_transpose)
            else:
                evals_transpose = np.asarray(res).transpose()
            print(evals_transpose.shape)

            for j, duration in enumerate(evals_transpose):
                # duration : [215*90]
                # skip the first data in simulation since it is the initial data
                if not is_trend_analysis:
                    if j == 0:
                        continue

                duration_si = []
                for i, poly_data in enumerate(duration):
                    dict_Si = {}
                    Si = fast.analyze(problem, duration[i], print_to_console=False)

                    dict_Si_var = dict_Si[var] = {} #dict_Si = {dict} {'Watertable depth Tinamit': {'names': ['Ptq - s1', 'Ptr - s1', 'Kaq - s1', 'Peq - s1', 'Pex - s1', 'Ptq - s2', 'Ptr - s2', 'Kaq - s2', 'Peq - s2', 'Pex - s2', 'Ptq - s3', 'Ptr - s3', 'Kaq - s3', 'Peq - s3', 'Pex - s3', 'Ptq - s4', 'Ptr - s4', 'Kaq - s4', … View
                    for k, v in Si.items():
                        if isinstance(v, np.ndarray):
                            n_v = v.tolist()
                            dict_Si_var[k] = n_v
                        else:
                            dict_Si_var[k] = v

                    duration_si.append(dict_Si_var)
                    #print('duration_si', duration_si)
                duration_all_si.append(duration_si)
        if poly_id is not None:
            filename = '{}_sensitivity_{}_{}.out'.format(self.sa_name,
                self.name, poly_id)
        else:
            filename = filename = '{}_sensitivity_{}.out'.format(self.sa_name,
                self.name)

        with open(os.path.join(self.root_path, filename), 'w') as f0, \
                open(os.path.join(self.root_path,
                                  '{}_max_sensitivity_{}.out'.format(self.sa_name,
                                      self.name)),
                     'w') as f1:
            f0.write(('{}\n').format(json.dumps(duration_all_si)))
            f1.write('\nThis is the duration {}: \n\n'.format(j))
        # duration_all_si [each season[each polygon{name, mu, mu_star, sigma, mu_start_conf}]]
        return duration_all_si

    def plot_SI(self, ploy_id, duration_all_si, savepath):
        '''
        can delete
        :param ploy_id:
        :param duration_all_si:
        :param savepath:
        :return:
        '''
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

class SensitivityOrder(Enum):
    S1 = 'S1'
    ST = 'ST'

def get_existing_simulated_result(fa, start_group, poly=None):
    '''
    load simulated data from existing files from group 0 to start_group
    :param start_group: Ns/intercept; eg., Ns=11500/200 = 575
    :return: simulated data of each polygon in the entire start_group; eg., poly_1 data of all 575 groups {'WTD':[[[]]]} 115000*1*20
    '''
    result = {'Watertable depth Tinamit': []}
    for i in range(start_group):
        with open(os.path.join(fa.root_path, 'Simulation\\5000_Fast simulation\\Fast_simulation_{}_{}.out'.format(0, i)), 'r') as f:
            # line=1 in each of 575 files f: {'WTD':[[[]]]};  200*215*20seasons,
            for line in f:
                print(len(json.loads(line)['Watertable depth Tinamit']))
                if poly is not None:
                    data = json.loads(line)['Watertable depth Tinamit'] #len(data)=200
                    result['Watertable depth Tinamit'] += [[samp[poly]] for samp in data] # samp is each of 200s, each samp=one 215
                    #result['Watertable depth Tinamit'] += [[[poly[poly]] for poly in samp] for samp in data ]
                else:
                    result['Watertable depth Tinamit'] += json.loads(line)['Watertable depth Tinamit']
        print('result', i, len(result['Watertable depth Tinamit']))
    if poly is not None:
        with open(os.path.join(fa.root_path, 'Fast_simulation_{}_poly_{}.out'.format(fa.name, poly)), 'w') as f:
            f.write(json.dumps(result))
        f.close()
    return result

def load_simulation_poly_data(fast, filename):
    result = []
    with open(os.path.join(fast.root_path, filename), 'r') as f1:
        for line in f1:
            result.append(json.loads(line))
    f1.close()
    return result[0] if len(result) == 1 else result

def conduct_trend_analysis_from_files(config, name, sampling_file_name, n_similuated_result, poly_id=None):
    '''
    Conduct trend analysis from the simulated data
    :param name:
    :param sampling_file_name:
    :param n_similuated_result: 575 * 200
    :return:
    '''
    fa = FastSa(config, name)
    problem = fa.problems_setup2()
    # os.path.join(mor.root_path, 'p revious simulation//10 years//0407 run N=50 P=16//Morris_Sampling_{}.out'.format(0))
    #parameters_set = np.asarray(fa.load_parameters_sampling(os.path.join(fa.root_path, sampling_file_name)))
    #evals = get_existing_simulated_result(fa, os.path.join(fa.root_path, n_similuated_result))
    evals = load_simulation_poly_data(fa, os.path.join(fa.root_path, n_similuated_result))
    evals = fa.compute_linear_trend(fa, evals, poly_id)

    #fa.analyze2(evals, problem, poly_id, is_trend_analysis=True)

def compute_last_n_ave_simulate_values_4_classes(config, name, simulation_filename):
    '''
    use to compute the ave and last season among for 12 classes
    :param config:
    :param name:
    :param simulation_filename: (no use)
    :return:
    compute_last_n_ave_simulate_values_4_classes(config, 0, 'trend_SA\\ab\\Fast_trend_0.out')
    '''
    categories = [SC.H1, SC.H2, SC.H3, SC.M1, SC.M2, SC.M3, SC.M4, SC.T1, SC.T2, SC.T3, SC.T4]
    average_4_categories = []
    fa = FastSa(config, name)

    for category in categories:
        print(f'Working on category: {category.__str__()}')
        result = combine_last_n_ave_data(*category)
        if len(average_4_categories) == 0:
            average_4_categories = result
        else:
            for i in range(len(result)):
                average_4_categories[i].extend(result[i])


    average_4_categories = {'Average Class Sim for ave_n_last':average_4_categories}
    problem = fa.problems_setup2()
        # os.path.join(mor.root_path, 'previous simulation//10 years//0407 run N=50 P=16//Morris_Sampling_{}.out'.format(0))
    fa.analyze2(average_4_categories, problem, is_trend_analysis=True)

    with open(f'{fa.root_path}/{fa.sa_name}_average_class_sim_data_4_ave_n_last_{fa.name}.out', 'w') as f:
        f.write(json.dumps(average_4_categories))

def compute_avearage_simulate_values_4_classes(config, name, simulation_filename):
    '''
    Compute the mean value for each of 11 classes of trend (a, b)
    :param config:
    :param name:
    :param simulation_filename: (no use)
    :return:
    compute_avearage_simulate_values_4_classes(config, 0, 'trend_SA\\ab\\Fast_trend_0.out')
    '''
    categories = [SC.H1, SC.H2, SC.H3, SC.M1, SC.M2, SC.M3, SC.M4, SC.T1, SC.T2, SC.T3, SC.T4]
    average_4_categories = []
    fa = FastSa(config, name)

    for category in categories:
        print(f'Working on category: {category.__str__()}')
        result = combine_trend_ab_data_into_file(*category)
        if len(average_4_categories) == 0:
            average_4_categories = result
        else:
            for i in range(len(result)):
                average_4_categories[i].extend(result[i])


    average_4_categories = {'Average Class Sim for ab':average_4_categories}
    problem = fa.problems_setup2()
        # os.path.join(mor.root_path, 'previous simulation//10 years//0407 run N=50 P=16//Morris_Sampling_{}.out'.format(0))
    fa.analyze2(average_4_categories, problem, is_trend_analysis=True)

    with open(f'{fa.root_path}/{fa.sa_name}_average_class_sim_data_{fa.name}.out', 'w') as f:
        f.write(json.dumps(average_4_categories))


def combine_last_n_ave_data(*polys):
    last_n_ave = []
    for poly in polys:
        result = []
        with open(f'D:\\Thesis\\pythonProject\\Tinamit\\tinamit\\Calib\\SA_algorithms\\Fast\\Simulation\\poly_data_Sim\\Fast_simulation_0_poly_{poly}.out') \
            as f:
            for line in f:
                result.append(json.loads(line))

        tmp_result = []
        result = result[0]['Watertable depth Tinamit']
        for sample in range(len(result)):
            sum = 0
            last = result[sample][0][-1]
            for season in range(1, 21):
                if len(result[sample][0]) < 21 and season >= len(result[sample][0]):
                    sum += result[sample-1][0][season]
                else:
                    sum += result[sample][0][season]
            tmp_result.append([[sum/20, last]])

        last_n_ave.append(tmp_result)
        #evals = np.asarray(load_data_from_file(fa, simulation_filename)['Trend parameters'])

    ave_n_last_class = []
    for sample in range(len(last_n_ave[0])):
        ave = 0
        last = 0
        for poly in range(len(polys)):
            ave += last_n_ave[poly][sample][0][0]
            last += last_n_ave[poly][sample][0][1]
        ave /= len(polys)
        last /= len(polys)
        ave_n_last_class.append([[ave, last]])

    return ave_n_last_class

def combine_trend_ab_data_into_file(*polys):
    trend_ab = []
    for poly in polys:
        result = []
        with open(f'D:\\Thesis\\pythonProject\\Tinamit\\tinamit\\Calib\\SA_algorithms\\Fast\\trend_SA\\ab\\trend_sim_ab\\Fast_trend_0_{poly}.out') \
            as f:
            for line in f:
                result.append(json.loads(line))

        trend_ab.append(result[0]['Trend parameters'])
        #evals = np.asarray(load_data_from_file(fa, simulation_filename)['Trend parameters'])

    ave_class_ab = []
    for sample in range(len(trend_ab[0])):
        ave_a = 0
        ave_b = 0
        for poly in range(len(polys)):
            ave_a += trend_ab[poly][sample][0][0]
            ave_b += trend_ab[poly][sample][0][1]
        ave_a /= len(polys)
        ave_b /= len(polys)
        ave_class_ab.append([[ave_a, ave_b]])

    return ave_class_ab

def noninfluential_param_of_wtd(fa, sensitivity_output):
    '''GET the noninfluential param of WTD (Si < 0.01 & St < 0.1)
    :param fa:
    :return:
    '''
    for j in range(fa.n_poly):
        sensitivity_output = fa.load_sensitivity_data(
            os.path.join(fa.root_path, f'trend_SA\\ab\\Fast_sensitivity_{fa.name}_{j}.out'))

        # noninfluential_param_of_wtd = [
        #     [{fa.problem['names'][i]: st for i, st in enumerate(season[0]['ST']) if st < 0.1} for
        #     season in sensitivity_of_ab[0]]

        # noninfluential_param_of_wtd = [ [ {fa.problem['names']:(i['S1'][para], i['ST'][para]) for para in range(fa.n_paras)
        #                                    if i['S1'][para] < 0.01 and i['ST'][para] < 0.1} for i in season]
        #                                 for season in sensitivity_of_ab[0]]

        noninfluential_param_of_wtd = []
        for ab in sensitivity_output[0]:
            for i in ab: #i = 2 dict for a/b= 2(s1/st) * 23, i = a or b
                ab_trend = []
                for j in range(fa.n_paras): #j = 23
                    if i['S1'][j] < 0.01 and (i['ST'][j] - i['S1'][j])< 0.1:
                        #print(fa.problem['names'][j], (i['S1'][j], i['ST'][j] ))
        #                 ab_trend.append({fa.problem['names'][j]: (i['S1'][j], (i['ST'][j] - i['S1'][j])})
        #         noninfluential_param_of_wtd.append(ab_trend)
        # for i, param in enumerate(noninfluential_param_of_wtd):
        #     print(f'ab{i+1}', f'non:{len(param)},influential:{23 - len(param)}', param)
        print()

        # sensitivity_of_ab = fa.load_sensitivity_data(
        #     os.path.join(fa.root_path, f'trend_SA\\ab\\Fast_sensitivity_{fa.name}_{j}.out'))
        #
        # # noninfluential_param_of_wtd = [
        # #     [{fa.problem['names'][i]: st for i, st in enumerate(season[0]['ST']) if st < 0.1} for
        # #     season in sensitivity_of_ab[0]]
        #
        # # noninfluential_param_of_wtd = [ [ {fa.problem['names']:(i['S1'][para], i['ST'][para]) for para in range(fa.n_paras)
        # #                                    if i['S1'][para] < 0.01 and i['ST'][para] < 0.1} for i in season]
        # #                                 for season in sensitivity_of_ab[0]]
        #
        # noninfluential_param_of_wtd = []
        # for ab in sensitivity_of_ab[0]:
        #     for i in ab: #i = 2 dict for a/b= 2(s1/st) * 23, i = a or b
        #         ab_trend = []
        #         for j in range(fa.n_paras): #j = 23
        #             if i['S1'][j] < 0.01 and (i['ST'][j] - i['S1'][j])< 0.1:
        #                 #print(fa.problem['names'][j], (i['S1'][j], i['ST'][j] ))
        #                 ab_trend.append({fa.problem['names'][j]: (i['S1'][j], (i['ST'][j] - i['S1'][j])})
        #         noninfluential_param_of_wtd.append(ab_trend)
        # for i, param in enumerate(noninfluential_param_of_wtd):
        #     print(f'ab{i+1}', f'non:{len(param)},influential:{23 - len(param)}', param)
        #
        # print()


def  plot_residual(config, name, filename):
    def load_poly_data(fa, poly_id):
        filename = os.path.join(fa.root_path, f'Simulation\\poly_data_Sim\\Fast_simulation_0_poly_{poly_id}.out')
        data = []
        with open(filename, 'r') as fr:
            for line in fr:
                data.append(json.loads(line))
        fr.close()
        return data[0]["Watertable depth Tinamit"]

    def plot_all(fa):
        all_residuals = []
        for poly in range(fa.n_poly):
            print(f'\npolygon {poly}')
            poly_eval = load_poly_data(fa, poly)
            poly_eval = ([sample[0][3:] for sample in poly_eval])
            res = fa.plot_residuals(poly_eval, x_data=range(fa.n_poly))
            res['poly_id'] = poly
            all_residuals.append(res)

        # save the result to file
        with open(os.path.join(fa.root_path, 'fa_residual_result_4_polys_all.out'), 'w') as fw:
            fw.write(json.dumps(all_residuals))
        fw.close()

    def plot_summar_n_winter(fa):
        # all_residuals_s = []
        all_residuals_w = []
        for poly in range(fa.n_poly):
            print(f'\npolygon {poly}')
            eval = load_poly_data(fa, poly)

            # poly_eval_s = []
            poly_eval_w = []
            for sample in range(len(eval)):
                # s = []
                w = []
                for season in range(3, 21):
                    if len(eval[sample][0]) < 21 and season >= len(eval[sample][0]):
                        tmp = eval[sample - 1][0][season]
                    else:
                        tmp = eval[sample][0][season]
                    if season % 2 == 1:
                        # s.append(tmp)
                        pass
                    else:
                        w.append(tmp)
                # poly_eval_s.append(s)
                poly_eval_w.append(w)

            # print(poly_eval_s)
            # poly_eval = ([sample[poly][3:] for sample in eval])
            # res_s = fa.plot_residuals(poly_eval_s)
            res_w = fa.plot_residuals(poly_eval_w)
            # res['poly_id'] = poly
            # all_residuals.append(res)
            # res_s['poly_id'] = poly
            # res_w['poly_id'] = poly
            # all_residuals_s.append(res_s)
            # all_residuals_w.append(res_w)


        with open(os.path.join(fa.root_path, 'fa_residual_result_4_polys_winter.out'), 'w') as fw:
            fw.write(json.dumps(all_residuals_w))
        fw.close()

    fa = FastSa(config, name)
    plot_all(fa)
    # plot_summar_n_winter(fa)

if __name__ == '__main__':
    # n_poly, Ns(sampling size for each parameter), n_para, timestepss 24753
    config = [215, 5000, 23, 20]
    # convergence can be reached when the no. of evaluation is 10^5 in total for 20 param (10^5/24) = 4000
    #combine_trend_ab_data_into_file(*SC.H1)
    # combine_last_n_ave_data(*SC.H1)

    #plot residual
    plot_residual(config, 0, '')

    # good R2
    # FastSa.idealregression()

    # compute_last_n_ave_simulate_values_4_classes(config, 0, 'trend_SA\\ab\\Fast_trend_0.out')
#not 4000, 12500 instead. 12500*8 + 1 ~= 100,000
# 23*5000=115000
    # SIMULATION
    #fa = FastSa(config=config, name='0')
    # #fa.start_simulation_from_file()
    # problem = fa.problems_setup2()
    # for i in range(fa.n_poly):
        # if i < 122:
        #     continue
        # evals = get_existing_simulated_result(fa, 575, i)
    # for poly_data in range(fa.n_poly): # poly_data is 20 rankings of S1 and 20 rankings of
    #     evals = load_simulation_poly_data(fa, 'Fast_simulation_0_poly_{}.out'.format(poly_data))
    #     result = fa.analyze2(evals, problem, poly_id=poly_data)
    #print()
    # parameters_set = fa.sampling2(problem)
    # evals = fa.simulation2(parameters_set, 200)
    #result = fa.analyze2(evals, problem, n_poly=0)

    # for poly_data in range(config[0]):
    # # os.path.join(fa.root_path, 'previous simulation//10 years//0407 run N=50 P=16//Morris_Sampling_{}.out'.format(0))
    # #     parameters_set = np.asarray(fa.load_parameters_sampling(fa.root_path, 'Fast_simulation_0_poly_{}.out'.format(poly_data))
    # #     evals = load_simulation_poly_data(fa, 'Simulation\\5000_Fast simulation\\Fast_simulation_0_poly_{}.out'.format(poly_data))
    # #     evals = fa.compute_linear_trend(fa, evals)
    # #     result = fa.analyze2(evals, parameters_set, problem)
    #      conduct_trend_analysis_from_files(config, 0, 'Simulation\\0406 run 5000\\Fast_Sampling_0.out', 'Simulation\\poly_data_Sim\\Fast_simulation_0_poly_{}.out'.format(poly_data), poly_id=poly_data)


    # for poly_data in range(fa.n_poly): # poly_data is 20 rankings of S1 and 20 rankings of
    #     evals = load_simulation_poly_data(fa, 'Fast_simulation_0_poly_{}.out'.format(poly_data))
    #     result = fa.analyze2(evals, problem, poly_id=poly_data)

