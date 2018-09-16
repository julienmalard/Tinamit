import os

from tinamit.Análisis.Sens.corridas import simul_sens
from tinamit.Análisis.Sens.muestr import cargar_mstr_paráms, gen_problema, muestrear_paráms
from tinamit.cositas import cargar_json
from tinamit.Análisis.Sens import behavior

import numpy as np
from SALib.analyze import morris
from SALib.analyze import fast

from tinamit.config import _


def _anlzr_salib(método, problema, mstr, simul, ops_método):
    '''
    Parameters
    ----------
    método: ['morris', 'fast']
    líms_paráms, mapa_paráms se usan para generar el problema.
    mstr: sampled data
    simul: simulated model output
    ops_método: dict
    #{'num_levels': 8, 'grid_jump': 4}

    Returns
    -------

    '''

    if isinstance(mstr, list):
        mstr = np.asarray(mstr)

    if método == 'morris':
        if isinstance(simul, list):
            simul = np.asarray(simul)
        ops = {'X': mstr, 'Y': simul, 'num_levels': 8, 'grid_jump': 4}
        ops.update(ops_método)

        mor = {}
        Si = morris.analyze(problema, **ops)

        mor.update(
            {'mu_star': {j: Si['mu_star'][i] for i, j in enumerate(problema['names'])},
             'sigma': {j: Si['sigma'][i] for i, j in enumerate(problema['names'])},
             'sum_sigma': np.sum(Si['sigma'])
             })
        return mor

    elif método == 'fast':
        ops = {'Y': simul}

        fa = {}
        Si = fast.analyze(problema, **ops)

        fa.update({'Si': {j: Si['S1'][i] for i, j in enumerate(problema['names'])},
                   'ST': {j: Si['ST'][i] for i, j in enumerate(problema['names'])},
                   'St-Si': {j: Si['ST'][i] - Si['S1'][i] for i, j in enumerate(problema['names'])},
                   'sum_s1': np.sum(Si['S1']),
                   'sum_st': np.sum(Si['ST']),
                   'sum_st-s1': np.absolute(np.sum(Si['ST']) - np.sum(Si['S1']))
                   })
        return fa

    else:
        raise ValueError(_('Algoritmo "{}" no reconocido.').format(método))


def format_sens_ind(si, método, problema, var_egr):
    # here the result should be
    # {var_egr: {important(mu*>0.1):{}, non-influential(mu* < 0.1):{}, sum_sigma:()}}
    # {var_egr: {important(Si>0.01):{}, non-influential(Si<0.01&St-Si < 0.1):{}, sum_si:[], sum_st:[]}}

    if método == 'morris':
        important = {'important':
                         {problema['names'][i]: si['mu_star'].tolist()[i] for i in np.where(si['mu_star'] > 0.1)[0]}
                     }

        non_influential = {'non_influential':
                               {problema['names'][i]: si['mu_star'].tolist()[i] for i in
                                np.where(si['mu_star'] < 0.1)[0]}
                           }

        if var_egr is None:
            mor_ff_fp = {var: {'sum_sigma': si['sum_sigma']} for var in var_egr}

            for var in var_egr:
                mor_ff_fp[var].update(important)
                mor_ff_fp[var].update(non_influential)
        else:
            mor_ff_fp = {var_egr: {'sum_sigma': si['sum_sigma']}}
            mor_ff_fp[var_egr].update(important)
            mor_ff_fp[var_egr].update(non_influential)
        return mor_ff_fp

    elif método == 'fast':
        important = {'important':
                         {problema['names'][i]: si['S1'][i] for i in np.where(np.asarray(si['S1']) > 0.01)[0]}
                     }

        non_influential = {'non_influential':
                               {problema['names'][j]: si['S1'][j] for j in
                                [i for i in np.where(np.asarray(si['ST-S1']) < 0.1)[0].tolist()
                                 if i in np.where(np.asarray(si['S1']) < 0.01)[0].tolist()]}
                           }
        interaction = {'interaction':
                           {problema['names'][i]: si['ST-S1'][i] for i in np.where(np.asarray(si['ST-S1']) > 0.1)[0]}}

        if var_egr is None:
            fa_ff_fp = {var: {'sum_s1': si['sum_s1'], 'sum_st': si['sum_st'],
                              'sum_st-s1': si['sum_st-s1']} for var in var_egr}

            for var in var_egr:
                fa_ff_fp[var].update(important)
                fa_ff_fp[var].update(non_influential)
                fa_ff_fp[var].update(interaction)
        else:
            fa_ff_fp = {var_egr: {'sum_s1': si['sum_s1'], 'sum_st': si['sum_st'], 'sum_st-s1': si['sum_st-s1']}}
            fa_ff_fp[var_egr].update(important)
            fa_ff_fp[var_egr].update(non_influential)
            fa_ff_fp[var_egr].update(interaction)

        return fa_ff_fp

    else:
        raise ValueError(_('Algoritmo "{}" no reconocido.').format(método))


def analy_by_file(método, líms_paráms, mapa_paráms, mstr_path, simulation_path, t_final, var_egr,
                  ops_método=None, tipo_egr=None, ficticia=True):
    """

    :param método:
    :param líms_paráms:
    :param mapa_paráms:
    :param mstr_path:
    :param simulation_path: {'arch_simular': str, 'num_samples': int}
    :param t_final:
    :param var_egr:
    :param ops_método:
    :param tipo_egr:
    :param ficticia:
    :return:
    """
    método = método.lower()
    if tipo_egr:
        tipo_egr = tipo_egr.lower()

    if ops_método is None:
        ops_método = {}

    mstr = cargar_mstr_paráms(mstr_path)
    simulation = read_simulation_data(simulation_path['arch_simular'], simulation_path['num_samples'], var_egr)

    return anlzr_simul(
        método=método, líms_paráms=líms_paráms, mstr=mstr, mapa_paráms=mapa_paráms, ficticia=ficticia,
        simulation=simulation, var_egr=var_egr, ops_método=ops_método, tipo_egr=tipo_egr
    )


def anlzr_sens(mod, método, líms_paráms, mapa_paráms, t_final, var_egr,
               ops_método=None, tipo_egr=None, ficticia=True, shape=None):
    método = método.lower()
    if tipo_egr:
        tipo_egr = tipo_egr.lower()

    if ops_método is None:
        ops_método = {}

    mstr = muestrear_paráms(líms_paráms, método, mapa_paráms=mapa_paráms, ficticia=ficticia)

    simulation = simul_sens(mod, mstr_paráms=mstr, mapa_paráms=mapa_paráms, t_final=t_final, var_egr=var_egr,
                            guardar=False)
    # import matplotlib.pyplot as ppt
    # for i in range(len(simulation)):
    #     ppt.plot(simulation[str(i)]['y'].values)
    #     ppt.savefig(f"D:\\Thesis\\pythonProject\\png\\{i}.png")
    #     ppt.close()

    # sample_size*xarray --> 100*
    return anlzr_simul(
        método=método, líms_paráms=líms_paráms, mstr=mstr, mapa_paráms=mapa_paráms, ficticia=ficticia,
        simulation=simulation, var_egr=var_egr, ops_método=ops_método, tipo_egr=tipo_egr
    )


def anlzr_simul(método, líms_paráms, mstr, mapa_paráms, ficticia, simulation, var_egr, ops_método,
                tipo_egr="promedio"):
    if isinstance(tipo_egr, str):
        tipo_egr = [tipo_egr]

    problema = gen_problema(líms_paráms, mapa_paráms, ficticia)[0]
    egr = {tp: {v: {} for v in var_egr} for tp in tipo_egr}
    f_mstr = [[mstr[para][i] for para in problema['names']] for i in range(len(list(mstr.values())[0]))]

    for tp in tipo_egr:
        d_tp = egr[tp]

        for vr in var_egr:
            if isinstance(list(simulation.values())[0], list):
                p_f_simul = format_simulation_data(simulation, vr, tp)
                d_var = {}
                for poly, f_simul in p_f_simul.items():
                    d_var[poly] = anlzr_simul_stepwise(problema, f_simul, método, f_mstr, ops_método)
            else:
                f_simul = format_simul(simulation=simulation, vr=vr, tipo_egr=tp)
                d_var = anlzr_simul_stepwise(problema, f_simul, método, f_mstr, ops_método)

            d_tp[vr] = d_var
    return egr


def anlzr_simul_stepwise(problema, f_simul, método, f_mstr, ops_método):
    if isinstance(f_simul, dict):
        if método == 'morris':
            d_var = {'mu_star': {name: {ll: {} for ll in f_simul} for name in problema['names']},
                     'sigma': {name: {ll: {} for ll in f_simul} for name in problema['names']},
                     'sum_sigma': {ll: {} for ll in f_simul}}
        elif método == 'fast':
            d_var = {'Si': {name: {ll: {} for ll in f_simul} for name in problema['names']},
                     'ST': {name: {ll: {} for ll in f_simul} for name in problema['names']},
                     'St-Si': {name: {ll: {} for ll in f_simul} for name in problema['names']},
                     'sum_s1': {ll: {} for ll in f_simul},
                     'sum_st': {ll: {} for ll in f_simul},
                     'sum_st-s1': {ll: {} for ll in f_simul}}

        else:
            raise ValueError(método)

        for ll, v in f_simul.items():
            res = _anlzr_salib(método=método, problema=problema,
                              mstr=f_mstr, simul=v, ops_método=ops_método)
            for si, val in res.items():
                if isinstance(val, dict):
                    for pa, p_var in val.items():
                        d_var[si][pa][ll] = p_var
                else:
                    d_var[si][ll] = val
    else:
        if len(f_simul.shape) > 1:
            tmñ = f_simul.shape[1:]
            if método == 'morris':
                d_var = {'mu_star': {name: np.empty(tmñ) for name in problema['names']},
                         'sigma': {name: np.empty(tmñ) for name in problema['names']},
                         'sum_sigma': np.empty(tmñ)}
            elif método == 'fast':
                d_var = {'Si': {name: np.empty(tmñ) for name in problema['names']},
                         'ST': {name: np.empty(tmñ) for name in problema['names']},
                         'St-Si': {name: np.empty(tmñ) for name in problema['names']},
                         'sum_s1': np.empty(tmñ),
                         'sum_st': np.empty(tmñ),
                         'sum_st-s1': np.empty(tmñ)}
            else:
                raise ValueError(método)

            for i in range(f_simul.shape[1]):
                res = _anlzr_salib(método=método, problema=problema,
                                  mstr=f_mstr, simul=f_simul[:, i], ops_método=ops_método)
                for name, val in res.items():
                    if isinstance(val, dict):
                        for pa, p_var in val.items():
                            d_var[name][pa][i] = p_var
                    else:
                        d_var[name][i] = val

        else:
            d_var = {}
            d_var.update(
                _anlzr_salib(método=método, problema=problema, mstr=f_mstr,
                             simul=f_simul, ops_método=ops_método))

    return d_var

def format_simul(simulation, vr, tipo_egr, n_dimension=None):
    """

    :param simulation: { 'sample_id': {'y': []}}
    :param vr:
    :param tipo_egr:
    :param n_dimension:
    :return: [] or {'p': []}
    """
    if tipo_egr == "promedio":
        f_simul = np.empty((len(simulation)))
        for i, val in enumerate(simulation.values()):
            f_simul[i] = np.average(val[vr].values[1:])

    elif tipo_egr == "final":
        f_simul = np.empty((len(simulation)))
        for i, val in enumerate(simulation.values()):
            f_simul[i] = val[vr].values[-1]

    elif tipo_egr == "paso_tiempo":
        f_simul = np.empty([len(simulation), simulation['0'][vr].values.size - 1])
        for i, val in enumerate(simulation.values()):
            f_simul[i] = val[vr].values[1:]

    elif tipo_egr == "linear":
        bf_simul = {'slope': np.empty((len(simulation))), 'intercept': np.empty((len(simulation)))}
        f_simul = behavior_anlzr(simulation, bf_simul, vr, tipo_egr, n_dimension=None)

    elif tipo_egr == "exponencial":
        bf_simul = {'y_intercept': np.empty((len(simulation))), 'g_d': np.empty((len(simulation)))}
        f_simul = behavior_anlzr(simulation, bf_simul, vr, tipo_egr, n_dimension=None)

    elif tipo_egr == "logístico":
        bf_simul = {'maxi_val': np.empty((len(simulation))), 'g_d': np.empty((len(simulation))),
                    'mid_point': np.empty((len(simulation)))}
        f_simul = behavior_anlzr(simulation, bf_simul, vr, tipo_egr, n_dimension=None)

    elif tipo_egr == "inverso":
        bf_simul = {'g_d': np.empty((len(simulation))), 'phi': np.empty((len(simulation)))}
        f_simul = behavior_anlzr(simulation, bf_simul, vr, tipo_egr, n_dimension=None)

    elif tipo_egr == "log":
        bf_simul = {'g_d': np.empty((len(simulation))), 'phi': np.empty((len(simulation)))}
        f_simul = behavior_anlzr(simulation, bf_simul, vr, tipo_egr, n_dimension=None)

    elif tipo_egr == "oscilación":
        bf_simul = {'amplitude': np.empty((len(simulation))), 'period': np.empty((len(simulation))),
                    'phi': np.empty((len(simulation)))}
        f_simul = behavior_anlzr(simulation, bf_simul, vr, tipo_egr, n_dimension=None)

    elif tipo_egr == "oscilación_aten":
        bf_simul = {'g_d': np.empty((len(simulation))), 'amplitude': np.empty((len(simulation))),
                    'period': np.empty((len(simulation))), 'phi': np.empty((len(simulation)))}
        f_simul = behavior_anlzr(simulation, bf_simul, vr, tipo_egr, n_dimension=None)

    else:
        raise ValueError(tipo_egr)

    return f_simul


def behavior_anlzr(simulation, bf_simul, vr, tipo_egr, n_dimension):
    for i, val in enumerate(simulation.values()):
        y_data = val[vr].values
        b_param = behavior.minimize(np.asarray(range(val[vr].values.size)), y_data, tipo_egr)['parameters']
        for k, v in bf_simul.items():
            bf_simul[k][i] = b_param[k]
    return bf_simul


def read_simulation_data(arch_simular, num_samples, var_egr=None):
    """

    :param arch_simular:
    :param num_samples:
    :param var_egr:
    :return: {'para_name': [samples[time_step[ploy]]]}
    """
    if arch_simular is None:
        raise ValueError(_("la ruta de simulación es ninguna."))

    r = cargar_json(os.path.join(arch_simular, '0.json'))
    data = r['data_vars']

    if data is not None:
        var_nombre = [var for var in data]

    if var_egr is None:
        simulation_data = {var: [cargar_json(os.path.join(arch_simular, f'{i}.json'))['data_vars'][var]['data']
                                 for i in range(num_samples)] for var in var_nombre}
    else:
        # {para_name:[num_samples*time_step*num_polys]}
        simulation_data = {}
        for var in var_egr:
            simulation_data[var] = [cargar_json(os.path.join(arch_simular, f'{i}.json'))['data_vars'][var]['data']
                                    for i in range(num_samples)]

    return simulation_data


def format_simulation_data(simulation_data, vr, tipo_egr="paso_tiempo"):
    """

    :param simulation: {'para_name': [samples[time_step[ploy]]]}
    :param tipo_egr:
    :return: {para_name: {poly_id: {time_step: []}}}
    """
    if simulation_data is None:
        raise ValueError(_(""))

    num_samples = len(simulation_data[vr])
    time_step = len(simulation_data[vr][0])
    num_polys = len(simulation_data[vr][0][0])

    if tipo_egr == "promedio":

        # var: wtd, value=[625*21*215]
        samples = []
        for i in range(num_samples):
            polys = []
            for j in range(num_polys):
                sum = 0
                for k in range(1, time_step):
                    sum += simulation_data[vr][i][k][j]
                sum /= float(time_step - 1)
                polys.append(sum)
            samples.append([polys])

        formato_simular = {poly:
                               {step:
                                    [samples[sample][step][poly]
                                     for sample in range(num_samples)]
                                for step in [0]}
                           for poly in range(num_polys)}

        return formato_simular

    elif tipo_egr == "final":

        formato_simular = {poly:
                               {step:
                                    [simulation_data[vr][sample][step][poly]
                                     for sample in range(num_samples)]
                                for step in [time_step - 1]}
                           for poly in range(num_polys)}

        return formato_simular

    elif tipo_egr == "paso_tiempo":
        formato_simular = {poly:
                               {step:
                                    [simulation_data[vr][sample][step][poly]
                                     for sample in range(num_samples)]
                                for step in range(time_step) if step != 0}
                           for poly in range(num_polys)}
        return formato_simular

    elif tipo_egr == 'linear' or tipo_egr == 'oscilación' or tipo_egr == 'logístico' or tipo_egr == 'exponencial' \
            or tipo_egr == 'oscilación_aten':

        simulations = conduct_behavior_analysis(simulation_data[vr], num_samples, num_polys, time_step, tipo_egr)
        # {var: 625*215*[slope, intercept]}
        formato_simular = {poly:
                               {para:
                                    [simulations[sample][poly][para]
                                     for sample in range(num_samples)]
                                for para, val in simulations[0][poly].items()}
                           for poly in range(num_polys)}
        return formato_simular

    elif tipo_egr == 'forma':
        pass

    elif tipo_egr == 'trasiciones':
        pass

    elif tipo_egr == 'calibration':
        simulations = conduct_behavior_analysis(simulation_data[vr], num_samples, num_polys, time_step, tipo_egr)
        # {var: 625*215*[slope, intercept]}
        formato_simular = {poly:
                               {para:
                                    [simulations[sample][poly][para]
                                     for sample in range(num_samples)]
                                for para, val in simulations[0][poly].items()}
                           for poly in range(num_polys)}
        return formato_simular

    else:
        raise ValueError(_("el tipo de salidas ('tipo_egr') debe ser 'promedio', 'final',"
                           "'paso_tiempo', 'linear', 'forma', 'ocilación', 'trasiciones'. "))


def conduct_behavior_analysis(simulation_data, num_samples, num_polys, time_step, tipo_egr):
    samples = []
    for i in range(num_samples):
        polys = []
        for j in range(num_polys):
            step = [simulation_data[i][k][j] for k in range(1, time_step)]
            print(f"Conduct {tipo_egr} analysis to poly {j} on sample {i}")
            paras = behavior.minimize(range(len(step)), step, tipo_egr)
            polys.append(paras['parameters'])
        samples.append(polys)
    return samples
