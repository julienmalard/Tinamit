import numpy as np
from scipy import optimize, stats
from matplotlib import pyplot as plt

# def curve_fit(x_data=None, y_data=None):
#     def function(x, a, b):
#         return a * x + b
#
#     np.random.seed(0)
#     params, params_covariance = optimize.curve_fit(function, x_data, y_data, p0=[2.0, 2.0])
#     return params

def residual_plot(y_data, x_data=None):
    '''
R2 (0.7, 1); (0.6, 0.7); (0.5, 0.6), (0, 0.5)
    :param y_data: 1200 * 20
    :param x_data:
    :return:
    '''
    params = [stats.linregress(range(len(data)), data) for data in y_data]
    r2 = [p[2]**2 for p in params]

    #r2 = sorted([p[2]**2 for p in params], reverse=True)
    #print('R2', sorted([p[2]**2 for p in params], reverse=True))
    # print([p[2]**2 for p in params])
    # slope, intercept, r_value, p_value, std_error
    # params = [curve_fit(range(1, len(data) + 1), data) for data in y_data]
    #residuals = [params[j][0] + params[j][1]*i - data[i] for j, data in enumerate(y_data) for i in range(1, len(data))]

    #stats.probplot(residuals, plot=plt)
    #plt.show()
    r22 = [round(i, 2) if isinstance(i, float) else i for i in r2]
    # residuals2 = [round(i, 2) if isinstance(i, float) else i for i in residuals]
    # print(r22)
    # print(residuals2)
    return {'R2': r22}