from __future__ import division
from __future__ import print_function

import math
from sys import exit

import numpy as np


def analyze(problem, Y, M=4, print_to_console=False, num_resamples=None):
    """Performs the Fourier Amplitude Sensitivity Test (FAST) on model outputs.

    Returns a dictionary with keys 'S1' and 'ST', where each entry is a list of
    size D (the number of parameters) containing the indices in the same order
    as the parameter file.

    Parameters
    ----------
    problem : dict
        The problem definition
    Y : numpy.array
        A NumPy array containing the model outputs
    M : int
        The interference parameter, i.e., the number of harmonics to sum in
        the Fourier series decomposition (default 4)
    print_to_console : bool
        Print results directly to console (default False)

    References
    ----------
    .. [1] Cukier, R. I., C. M. Fortuin, K. E. Shuler, A. G. Petschek, and J. H.
           Schaibly (1973).  "Study of the sensitivity of coupled reaction
           systems to uncertainties in rate coefficients."  J. Chem. Phys.,
           59(8):3873-3878, doi:10.1063/1.1680571.

    .. [2] Saltelli, A., S. Tarantola, and K. P.-S. Chan (1999).  "A
          Quantitative Model-Independent Method for Global Sensitivity
          Analysis of Model Output."  Technometrics, 41(1):39-56,
          doi:10.1080/00401706.1999.10485594.

    Examples
    --------
    >>> X = fast_sampler.sample(problem, 1000)
    >>> Y = Ishigami.evaluate(X)
    >>> Si = fast.analyze(problem, Y, print_to_console=False)
    """

    D = problem['num_vars']

    if Y.size % (D) == 0:
        N = int(Y.size / D)  # Y.size = 115000 (K-dimensional hybercube)
    else:
        print("""
            Error: Number of samples in model output file must be a multiple of D, 
            where D is the number of parameters in your parameter file.
          """)
        exit()

    # Recreate the vector omega used in the sampling
    omega = np.zeros([D])
    omega[0] = math.floor((N - 1) / (2 * M))  # 624
    m = math.floor(omega[0] / (2 * M))  # 78

    if m >= (D - 1):
        omega[1:] = np.floor(np.linspace(1, m, D - 1))  # (1, 78, 22), from 1 to 78 evenly spaced to 22 intervals

    else:
        omega[1:] = np.arange(D - 1) % m + 1

    # Calculate and Output the First and Total Order Values
    if print_to_console:
        print("Parameter First Total")
    Si = dict((k, [None] * D) for k in ['S1', 'ST'])
    for i in range(D):  # 23

        l = np.arange(i * N, (i + 1) * N)
        Si['S1'][i] = compute_first_order(Y[l], N, M, omega[0])
        Si['ST'][i] = compute_total_order(Y[l], N, omega[0])
        if print_to_console:
            print("%s %f %f" %
                  (problem['names'][i], Si['S1'][i], Si['ST'][i]))

    # compute bootstrapping ADDED
    if num_resamples is not None:
        rank_j_k = []
        for i in range(D):  # 23

            l = np.arange(i * N, (i + 1) * N)  #
            rank_j_k.append(get_resampled_Si(
                Y[l], N, num_resamples, N, M, omega[0], conf_level=0.95))
        rank_j_k = np.asarray(rank_j_k)
        rank_j_k = rank_j_k.transpose()

        # compute sum of max index
        sum = 0
        for i in range(D):
            for j in range(num_resamples):
                for k in range(j, num_resamples):
                    sum += np.power(max(rank_j_k[j][i], rank_j_k[k][i]), 2)

        # compute rank corelation coefficient:
        coefficient = []
        for j in range(num_resamples):
            for k in range(j + 1, num_resamples):
                co_sum = 0
                sum = 0
                for i in range(D):
                    sum += np.power(max(rank_j_k[j][i], rank_j_k[k][i]), 2)
                for i in range(D):
                    s = sorted(rank_j_k[j], reverse=True)
                    ri_j = s.index(rank_j_k[j][i])
                    s = sorted(rank_j_k[k], reverse=True)
                    ri_k = s.index(rank_j_k[k][i])

                    co_sum += np.abs(ri_j - ri_k) * np.power(max(rank_j_k[j][i], rank_j_k[k][i]), 2) / sum
                coefficient.append(co_sum)
                # print('sum:', sum, 'co_sum:', co_sum)
        # print(coefficient)

        coefficient.sort()
        # print(coefficient)


        if coefficient[int(0.95 * coefficient.__len__())] < 1:
            Si['S_convergence'] = 1
        else:
            Si['S_convergence'] = 0
        print(Si['S_convergence'])
    return Si


# ADDED Bootstrap resampling
def get_resampled_Si(Si, num_samples, num_resamples, N, M, omega,
                     conf_level=0.95):
    data_resampled = np.zeros([num_samples])
    Si_resampled = np.zeros([num_resamples])

    if not 0 < conf_level < 1:
        raise ValueError("Confidence level must be between 0-1.")

    resample_index = np.random.randint(
        len(Si), size=(num_resamples, num_samples))
    data_resampled = Si[resample_index]
    # Compute average of the absolute values over each of the resamples
    # Si_resampled =
    i = 0
    for sample in data_resampled:
        # Si_resampled[i] = compute_first_order(sample, N, M, omega)

        Si_resampled[i] = compute_total_order(sample, N, omega)
        i += 1
    return Si_resampled


def compute_first_order(outputs, N, M, omega):
    f = np.fft.fft(outputs)
    Sp = np.power(np.absolute(f[np.arange(1, int((N + 1) / 2))]) / N, 2)
    V = 2 * np.sum(Sp)
    D1 = 2 * np.sum(Sp[np.arange(1, M + 1) * int(omega) - 1])
    return D1 / V

def compute_total_order(outputs, N, omega):
    f = np.fft.fft(outputs)
    Sp = np.power(np.absolute(f[np.arange(1, int((N + 1) / 2))]) / N, 2)
    V = 2 * np.sum(Sp)
    Dt = 2 * sum(Sp[np.arange(int(omega / 2))])
    return (1 - Dt / V)
