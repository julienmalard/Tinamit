import numpy as np
from scipy.stats import gaussian_kde


def _calc_máx_trz(trz):
    if len(trz) == 1:
        return trz[0]

    # Ajustar el rango, si es muy grande (necesario para las funciones que siguen)
    escl = np.max(trz)
    rango = escl - np.min(trz)
    if escl < 10e10:
        escl = 1  # Si no es muy grande, no hay necesidad de ajustar

    # Intentar calcular la densidad máxima.
    try:
        # Se me olvidó cómo funciona esta parte.
        fdp = gaussian_kde(trz / escl)
        x = np.linspace(trz.min() / escl - 1 * rango, trz.max() / escl + 1 * rango, 1000)
        máx = x[np.argmax(fdp.evaluate(x))] * escl
        return máx

    except BaseException:
        return np.nan
