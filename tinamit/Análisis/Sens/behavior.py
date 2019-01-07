import numpy as np
from scipy import optimize


def predict(x_data, parameters, pattern):
    if pattern == 'linear':
        return parameters['slope'] * x_data + parameters['intercept']
    elif pattern == 'exponencial':
        return parameters['y_intercept'] * (parameters['g_d'] ** x_data) + parameters['constant']
    elif pattern == 'logístico':
        return parameters['maxi_val'] / (1 + np.exp(-parameters['g_d'] * x_data + parameters['mid_point'])) + \
               parameters['constant']
    elif pattern == 'inverso':
        return parameters['g_d'] / (x_data + parameters['phi']) + parameters['constant']
    elif pattern == 'log':
        return parameters['g_d'] * np.log(x_data + parameters['phi']) + parameters['constant']
    elif pattern == 'oscilación':
        return parameters['amplitude'] * np.sin(parameters['period'] * x_data + parameters['phi']) + parameters[
            'constant']
    elif pattern == 'oscilación_aten':
        return np.exp(parameters['g_d'] * x_data) * parameters['amplitude'] * \
               np.sin(parameters['period'] * x_data + parameters['phi']) + parameters['constant']
    elif pattern == 'spp_oscil_aten_oscilación_aten':
        return np.exp(parameters['g_d'] * x_data) * parameters['amplitude'] * \
               np.sin(parameters['period'] * x_data + parameters['phi']) + parameters['constant'] + \
               np.exp(parameters['g_d_1'] * x_data) * parameters['amplitude_1'] * \
               np.sin(parameters['period_1'] * x_data + parameters['phi_1']) + parameters['constant_1']
    elif pattern == 'spp_oscil_aten_inverso':
        return np.exp(parameters['g_d'] * x_data) * parameters['amplitude'] * \
               np.sin(parameters['period'] * x_data + parameters['phi']) + parameters['constant'] + \
               parameters['g_d_1'] * np.log(x_data + parameters['phi_1']) + parameters['constant_1']


def linear(x, x_data):  # x is an np.array
    return x[0] * x_data + x[1]


def exponencial(x, x_data):
    return x[0] * (x[1] ** x_data) + x[2]


def logístico(x, x_data):
    return (x[0] / (1 + np.exp(-x[1] * x_data + x[2]))) + x[3]


def inverso(x, x_data):
    return (x[0] / (x_data + x[1])) + x[2]


def log(x, x_data):
    return x[0] * np.log(x_data + x[1]) + x[2]


def oscilación(x, x_data):
    return x[0] * np.sin(x[1] * x_data + x[2]) + x[3]


def oscilación_aten(x, x_data):
    return np.exp(x[0] * x_data) * x[1] * np.sin(x[2] * x_data + x[3]) + x[4]


def simple_shape(x_data=None, y_data=None, tipo_egr='linear', gof=False):
    def f_opt(x, x_data, y_data, f):
        return compute_rmse(f(x, x_data), y_data)

    norm_y_data = (y_data - np.average(y_data)) / np.std(y_data)
    # norm_y_data = y_data

    if tipo_egr == 'linear':
        params = optimize.minimize(f_opt, x0=[1, 1], method='Nelder-Mead',
                                   args=(x_data, norm_y_data, linear)).x
        b_params = {'bp_params': de_normalize(params, y_data, tipo_egr)}
        # slope, intercept, r_value, p_value, std_err = estad.linregress(x_data, norm_y_data)
        # b_params = {'bp_params': de_normalize(np.asarray([slope, intercept]), y_data, tipo_egr)}
        if gof:
            b_params.update({'gof': {'aic': aic(len(b_params['bp_params']),
                                                linear(np.asarray(list(b_params['bp_params'].values())), x_data),
                                                y_data)}})
    elif tipo_egr == 'exponencial':
        params = optimize.minimize(f_opt, x0=[0.1, 1.1, 0], method='Powell',
                                   args=(x_data, norm_y_data, exponencial)).x
        b_params = {'bp_params': de_normalize(params, y_data, tipo_egr)}
        if gof:
            b_params.update({'gof': {'aic': aic(len(b_params['bp_params']),
                                                exponencial(np.asarray(list(b_params['bp_params'].values())), x_data),
                                                y_data)}})
    elif tipo_egr == 'logístico':
        params = optimize.minimize(f_opt, x0=[5.0, 0.85, 3.0, 0], method='Powell',
                                   args=(x_data, norm_y_data, logístico)).x
        b_params = {'bp_params': de_normalize(params, y_data, tipo_egr)}
        if gof:
            b_params.update({'gof': {'aic': aic(len(b_params['bp_params']),
                                                logístico(np.asarray(list(b_params['bp_params'].values())), x_data),
                                                y_data)}})
    elif tipo_egr == 'inverso':
        params = optimize.minimize(f_opt, x0=[3.0, 0.4, 0], method='Nelder-Mead', args=(x_data, norm_y_data, inverso)).x
        b_params = {'bp_params': de_normalize(params, y_data, tipo_egr)}
        if gof:
            b_params.update({'gof': {'aic': aic(len(b_params['bp_params']),
                                                inverso(np.asarray(list(b_params['bp_params'].values())), x_data),
                                                y_data)}})
    elif tipo_egr == 'log':
        params = optimize.minimize(f_opt, x0=[0.3, 0.1, 0], method='Nelder-Mead', args=(x_data, norm_y_data, log)).x
        b_params = {'bp_params': de_normalize(params, y_data, tipo_egr)}
        if gof:
            b_params.update({'gof': {'aic': aic(len(b_params['bp_params']),
                                                log(np.asarray(list(b_params['bp_params'].values())), x_data),
                                                y_data)}})
    elif tipo_egr == 'oscilación':
        params = optimize.minimize(f_opt, x0=[2, 1.35, 0, 0], method='Powell',  # for wtd 7, 1.6, 0, 0
                                   args=(x_data, norm_y_data, oscilación)).x
        b_params = {'bp_params': de_normalize(params, y_data, tipo_egr)}
        if gof:
            b_params.update({'gof': {'aic': aic(len(b_params['bp_params']),
                                                oscilación(np.asarray(list(b_params['bp_params'].values())), x_data),
                                                y_data)}})
    elif tipo_egr == 'oscilación_aten':
        # x0 assignment is very tricky, the period (3rd arg should always>= real period)
        params = optimize.minimize(f_opt, x0=[0.1, 2, 2, 0, 0], method='SLSQP',  # 0.1, 1, 2, 0.01, 0, SLSQP, Powell
                                   args=(x_data, norm_y_data, oscilación_aten)).x
        b_params = {'bp_params': de_normalize(params, y_data, tipo_egr)}
        if gof:
            b_params.update({'gof': {'aic': aic(len(b_params['bp_params']),
                                                oscilación_aten(np.asarray(list(b_params['bp_params'].values())),
                                                                x_data), y_data)}})
    else:
        raise ValueError(tipo_egr)

    return b_params


def forma(x_data, y_data):
    behaviors_aics = {'linear': {},
                      'exponencial': {},
                      'logístico': {},
                      'inverso': {},
                      'log': {},
                      'oscilación': {},
                      'oscilación_aten': {}}

    for behavior in behaviors_aics.keys():
        behaviors_aics[behavior] = simple_shape(x_data, y_data, behavior, gof=True)

    return behaviors_aics


def find_best_behavior(all_beh_dt, trans_shape=None):
    fited_behaviors = []

    if trans_shape is None:
        gof_dict = {key: val['gof']['aic'] for key, val in all_beh_dt.items()}
    else:
        gof_dict = {key: val['gof']['aic'][:, trans_shape] for key, val in all_beh_dt.items()}

    gof_dict = sorted(gof_dict.items(), key=lambda x: x[1])  # list of tuple [('ocsi', -492),()]

    fited_behaviors.append(gof_dict[0])
    m = 1
    while m < len(gof_dict):
        if gof_dict[m][1] - gof_dict[0][1] > 2:
            break
        else:
            fited_behaviors.append(gof_dict[m])
        m += 1

    return fited_behaviors, gof_dict


def superposition(x_data, y_data):
    behaviors_aics = forma(x_data, y_data)

    b_param = {}
    for behavior in behaviors_aics:
        y_predict = predict(x_data, behaviors_aics[behavior]['bp_params'], behavior)  ## how to use linear(x, x_data) ??
        resid = y_data - y_predict

        osci = simple_shape(x_data=x_data, y_data=resid, tipo_egr='oscilación', gof=True)

        osci_atan = simple_shape(x_data=x_data, y_data=resid, tipo_egr='oscilación_aten', gof=True)

        y_spp_osci = predict(x_data, osci['bp_params'], 'oscilación') + y_predict
        y_spp_osci_atan = predict(x_data, osci_atan['bp_params'], 'oscilación_aten') + y_predict

        spp_osci_aic = aic(len(y_predict), y_spp_osci, y_data)
        spp_osci_aic_atan = aic(len(y_predict), y_spp_osci_atan, y_data)

        b_param.update({behavior: behaviors_aics[behavior]})

        if 'constant' in behaviors_aics[behavior]['bp_params']:
            osci['bp_params']['constant'] = behaviors_aics[behavior]['bp_params']['constant'] + osci['bp_params'][
                'constant']
            osci_atan['bp_params']['constant'] = behaviors_aics[behavior]['bp_params']['constant'] + osci_atan['bp_params'][
                'constant']

            osci['bp_params'].update(
                {k + "_1": v for k, v in behaviors_aics[behavior]['bp_params'].items() if k != 'constant'})
            osci_atan['bp_params'].update(
                {k + "_1": v for k, v in behaviors_aics[behavior]['bp_params'].items() if k != 'constant'})
        else:
            osci['bp_params'].update(
                {k + "_1": v for k, v in behaviors_aics[behavior]['bp_params'].items()})
            osci_atan['bp_params'].update(
                {k + "_1": v for k, v in behaviors_aics[behavior]['bp_params'].items()})

        b_param.update({f'spp_oscil_{behavior}':
                            {'bp_params': osci['bp_params'],
                             'gof': {'aic': spp_osci_aic}}})
        b_param.update({f'spp_oscil_aten_{behavior}':
                            {'bp_params': osci_atan['bp_params'],
                             'gof': {'aic': spp_osci_aic_atan}}})

    return b_param, behaviors_aics


def de_normalize(norm_b_param, y_data, tipo_egr):
    if tipo_egr == 'linear':
        return {'slope': norm_b_param[0] * np.std(y_data),
                'intercept': norm_b_param[1] * np.std(y_data) + np.average(y_data)}
        # return {'slope': norm_b_param[0],
        #         'intercept': norm_b_param[1]}
    elif tipo_egr == 'exponencial':
        return {'y_intercept': norm_b_param[0] * np.std(y_data),
                'g_d': norm_b_param[1],
                'constant': norm_b_param[2] * np.std(y_data) + np.average(y_data)}
        # return {'y_intercept': norm_b_param[0],
        #         'g_d': norm_b_param[1],
        #         'constant': norm_b_param[2]}
    elif tipo_egr == 'logístico':
        return {'maxi_val': norm_b_param[0] * np.std(y_data),
                'g_d': norm_b_param[1],
                'mid_point': norm_b_param[2],
                'constant': norm_b_param[3] * np.std(y_data) + np.average(y_data)}
        # return {'maxi_val': norm_b_param[0],
        #         'g_d': norm_b_param[1],
        #         'mid_point': norm_b_param[2],
        #         'constant': norm_b_param[3]}
    elif tipo_egr == 'inverso':
        return {'g_d': norm_b_param[0] * np.std(y_data),
                'phi': norm_b_param[1],
                'constant': norm_b_param[2] * np.std(y_data) + np.average(y_data)}
        # return {'g_d': norm_b_param[0],
        #         'phi': norm_b_param[1],
        #         'constant': norm_b_param[2]}
    elif tipo_egr == 'log':
        return {'g_d': norm_b_param[0] * np.std(y_data),
                'phi': norm_b_param[1],
                'constant': norm_b_param[2] * np.std(y_data) + np.average(y_data)}
        # return {'g_d': norm_b_param[0],
        #         'phi': norm_b_param[1],
        #         'constant': norm_b_param[2]}
    elif tipo_egr == 'oscilación':
        return {'amplitude': norm_b_param[0] * np.std(y_data),
                'period': abs(norm_b_param[1]),
                'phi': norm_b_param[2],
                'constant': norm_b_param[3] * np.std(y_data) + np.average(y_data)}
        # return {'amplitude': norm_b_param[0],
        #         'period': abs(norm_b_param[1]),
        #         'phi': norm_b_param[2],
        #         'constant': norm_b_param[3]}
    elif tipo_egr == 'oscilación_aten':
        return {'g_d': norm_b_param[0],
                'amplitude': norm_b_param[1] * np.std(y_data),
                'period': abs(norm_b_param[2]),
                'phi': norm_b_param[3],
                'constant': norm_b_param[4] * np.std(y_data) + np.average(y_data)}
        # return {'g_d': norm_b_param[0],
        #         'amplitude': norm_b_param[1],
        #         'period': abs(norm_b_param[2]),
        #         'phi': norm_b_param[3],
        #         'constant': norm_b_param[4]}


def compute_gof(y_predict, y_obs):
    return compute_nsc(y_predict, y_obs), compute_rmse(y_predict, y_obs)


def compute_rmse(y_predict, y_obs):
    if not isinstance(y_predict, np.ndarray):
        y_predict = np.asarray(y_predict)
    if not isinstance(y_obs, np.ndarray):
        y_obs = np.asarray(y_obs)
    return np.linalg.norm(y_predict - y_obs) / np.sqrt(len(y_predict))


def compute_nsc(y_predict, y_obs):
    # Nash-Sutcliffe Coefficient
    return 1 - np.sum(((y_predict - y_obs) ** 2) / np.sum((y_obs - np.mean(y_obs)) ** 2))


def L(y_predict, y_obs, N=5):
    # likelihood function
    return np.exp(-N * np.sum((y_predict - y_obs) ** 2) / np.sum((y_obs - np.mean(y_obs)) ** 2))


def compute_rcc(y_predict, y_obs):
    n = len(y_predict)

    s_yy = s_ysys = s_yys = 0
    for i in range(n):
        s_yy += (y_obs[i] - np.average(y_obs)) ^ 2
        s_ysys += (y_predict[i] - np.average(y_predict)) ^ 2
        s_yys += (y_obs[i] - np.average(y_obs)) * (y_predict[i] - np.average(y_predict))

    s_yy_s = s_ybyb = s_yyb = 0
    for k in range(n):
        for i in range(k + 1, n):
            y_star = y_b = 0
            for j in range(k + 1, n):
                y_star += y_obs[j]
                y_b += y_obs[j - k]
            y_star = (1 / (n - k)) * y_star
            y_b = (1 / (n - k)) * y_b
            s_yy_s += (y_obs[i] - y_star) ^ 2
            s_ybyb += (y_obs[i - k] - y_b) ^ 2
            s_yyb += (y_obs[i] - y_star) * ((y_obs[i - k] - y_b))

    return (s_yys / np.sqrt(s_yy * s_ysys)) / (s_yyb / np.sqrt(s_yy_s * s_ybyb))


def aic(k, y_predict, y_obs):
    # https://www.researchgate.net/post/What_is_the_AIC_formula
    # deltaAIC = AICm - AIC* <2(great); (4, 7)less support; (>10)no support
    n = len(y_obs)
    resid = y_obs - y_predict
    sse = np.sum(resid ** 2)
    # k = of variables, small Ns is no/k<40 20/2 or 20/3
    # [2*k+(2*k+1)/(n-k-1)-2*np.log(np.exp(2*np.pi*sse/n))]
    # 2*k - 2*np.log(2*np.pi*sse/ n) +2*k*(k + 1)/(n-k-1)
    # return 2*k - 2*np.log(sse) + 2*k*(k + 1)/(n-k-1)
    return 2 * k + n * np.log(sse / n)
    # 2*k - n*np.log(np.exp(2 * np.pi * sse / n) + 1)


def bic(y_predict, y_obs):
    # lowest BIC is preferred.
    np = len(y_predict)
    no = len(y_obs)
    resid = y_obs - y_predict
    sse = np.sum(resid ** 2)
    # no = number of observations
    return no * np.log(np.exp(sse / no)) + np * np.log(np.exp(no))
