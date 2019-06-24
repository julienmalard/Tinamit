import numpy as np
import scipy.stats as estad
import spotpy
from spotpy import objectivefunctions as spt_f, likelihoods as spt_l


def calc_máx_trz(trz):
    if len(trz) == 1:
        return trz[0]

    # Normalizar el rango (necesario para las funciones que siguen, si es muy grande)
    sig = np.std(trz)
    mu = np.mean(trz)
    trz_norm = (trz - mu) / sig

    # Intentar calcular la densidad máxima.
    try:
        # Se me olvidó cómo funciona esta parte.
        fdp = estad.gaussian_kde(trz)
        x = np.linspace(trz_norm.min(), trz_norm.max(), 1000)
        máx = x[np.argmax(fdp.evaluate(x))]

        # De-normalizar
        return máx * sig + mu

    except BaseException:
        return np.nan


def _anlz_tendencia(o, s):
    x = np.arange(len(o))
    pend_obs = estad.linregress(x, o)[0]
    pend_sim = estad.linregress(x, s)[0]

    return (pend_obs > 0) is (pend_sim > 0)


algs_spotpy = {
    'fast': spotpy.algorithms.fast,
    'dream': spotpy.algorithms.dream,
    'cm': spotpy.algorithms.mc,
    'cmmc': spotpy.algorithms.mcmc,
    'epm': spotpy.algorithms.mle,
    'mhl': spotpy.algorithms.lhs,
    'as': spotpy.algorithms.sa,
    'sceua': spotpy.algorithms.sceua,
    'erop': spotpy.algorithms.rope,
    'caa': spotpy.algorithms.abc,
    'fscabc': spotpy.algorithms.fscabc,
    'bdd': spotpy.algorithms.dds
}

eval_funcs = {
    'ens': spt_f.nashsutcliffe,
    'rcep': lambda o, s: -spt_f.rmse(o, s),
    'corresp': spt_f.agreementindex,
    'ekg': spt_f.kge,
    'r2': spt_f.rsquared,
    'rcnep': lambda o, s: -spt_f.rrmse(o, s),
    'log p': spt_f.log_p,
    'verosimil_gaus': spt_l.gaussianLikelihoodMeasErrorOut,
    'tendencia': _anlz_tendencia
}
