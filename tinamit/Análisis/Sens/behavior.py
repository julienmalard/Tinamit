import numpy as np
import pylab as plt
from scipy import optimize
import scipy.stats as estad


def curve_fit(x_data=None, y_data=None, tipo_egr='linear'):

    def exponential(x, a, b):
        return a * (b ** x)

    def logistic(x, a, b, c):
        # a=1 for transition
        return a / (1 + np.exp(-b * x + c))

    def inverse(x, a, b):
        return a/(x + b)

    def log(x, a, b):
        return a * np.log(x + b)

    def ocilación(x, a, b, c):
        return a * np.sin(b * x + c)

    def ocilación_aten(x, a, b, c, d):
        # , b>0 larger amplitude, a<o ocilation decay, c=1 horizontal ocilation
        # larger e smaller the curve cycle
        # b is eseential, when b is (0, 1), larger b, tend to growth faster and approach to X-axis more (no slope)
        # b=1 on the X-axis
        # b(-1, 0) ocilation decay when b<0, ocillation growth when b>0
        return np.exp(a * x) * b * np.sin(c * x + d)

    def superposition(ocilación, func2):
        return ocilación + eval(function[func2])

    if tipo_egr == 'linear':
        slope, intercept, r_value, p_value, std_err = estad.linregress(x_data, y_data)
        b_params = {'slope': slope, 'intercept': intercept}
    elif tipo_egr == 'exponential':
        params, params_covariance = optimize.curve_fit(exponential, x_data, y_data, p0=[1.0, 1.0])
        b_params = {'y_intercept':params[0], 'g_d':params[1]}
    elif tipo_egr == 'logistic':
        params, params_covariance = optimize.curve_fit(logistic, x_data, y_data, p0=[3.0, 2.0, 0.0])
        b_params = {'maxi_val': params[0], 'g_d': params[1], 'mid_point': params[2]}
    elif tipo_egr == 'inverse':
        params, params_covariance = optimize.curve_fit(inverse, x_data, y_data, p0=[2.0, 2.0])
        b_params = {'g_d': params[0], 'phi': params[1]}
    elif tipo_egr == 'log':
        params, params_covariance = optimize.curve_fit(log, x_data, y_data, p0=[1.0, 1.0])
        b_params = {'g_d': params[0], 'phi': params[1]}
    elif tipo_egr == 'ocilación':
        params, params_covariance = optimize.curve_fit(ocilación, x_data, y_data, p0=[1.0, 1.0, 1.0])
        b_params = {'amplitude': params[0], 'period': params[1], 'phi': params[2]}
    elif tipo_egr == 'ocilación_aten':
        params, params_covariance = optimize.curve_fit(ocilación_aten, x_data, y_data, p0=[1.0, 1.0, 1.0, 1.0])
        b_params = {'g_d': params[0], 'amplitude': params[1], 'period': params[2], 'phi':params[3]}
    # elif tipo_egr == 'superposition':
        # for func in functions:
        # params, params_covariance = optimize.curve_fit(ocil_aten, x_data, y_data, p0=[1.0, 1.0, -0.2, 0, 10, 0, 0])
    else:
        raise ValueError(tipo_egr)

    return b_params

# def transition(n_trans=2):
#     def wt(x, b, c):
#         # a=1 of logistic for transition
#         return 1 / (1 + np.exp(-b * x + c))

def superposition(ocilación, func2):
    '''
    maybe this func should write inside the curve fit?
    Returns
    -------
    '''
    return ocilación + eval(function[func2])

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

def aic(k, y_predict, y_obs, *args):
    # https://www.researchgate.net/post/What_is_the_AIC_formula
    #deltaAIC = AICm - AIC* <2(great); (4, 7)less support; (>10)no support
    n = len(y_obs)
    resid = y_obs - y_predict
    sse = np.sum(resid ** 2)
    # k = of variables, small Ns is no/k<40 20/2 or 20/3
    #[2*k+(2*k+1)/(n-k-1)-2*np.log(np.exp(2*np.pi*sse/n))]
    return 2*k - n*np.log(np.exp(2*np.pi*sse/n)+1) #2*k - 2*np.log(np.exp(2*np.pi*sse/n))

def bic(y_predict, y_obs):
    #lowest BIC is preferred.
    np = len(y_predict)
    no = len(y_obs)
    resid = y_obs - y_predict
    sse = np.sum(resid ** 2)
    #no = number of observations
    return no * np.log(np.exp(sse / no)) + np * np.log(np.exp(no)) #

def plot(X, Y1, Y2):
    def superimpose_plt(X, Y1, Y2):
        plt.scatter(X, Y1, color='k')
        plt.scatter(X, Y2, color='g')
        plt.show()
    pass


