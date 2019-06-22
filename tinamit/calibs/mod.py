import re
import tempfile

import numpy as np
import pandas as pd
import spotpy
import xarray as xr

from ._utils import _calc_máx_trz


class CalibradorMod(object):
    def __init__(símismo, mod):
        símismo.mod = mod

    def calibrar(símismo, líms_paráms, método, n_iter, bd, vars_obs=None, corresp_vars=None):
        vars_obs = vars_obs or bd.variables
        corresp_vars = corresp_vars or {}
        vars_obs = [corresp_vars[v] if v in corresp_vars else v for v in vars_obs]

        obs = bd.obt_datos(vars_obs, tipo='datos')[vars_obs]
        símismo._efec_calib(líms_paráms=líms_paráms, método=método, n_iter=n_iter, obs=obs)

    def _efec_calib(símismo, líms_paráms, método, n_iter, obs):
        raise NotImplementedError


class CalibradorModSpotPy(CalibradorMod):

    def _efec_calib(símismo, líms_paráms, método, n_iter, obs):

        temp = tempfile.NamedTemporaryFile('w', encoding='UTF-8', prefix='CalibTinamït_')

        mod_spotpy = _ModSpotPy(mod=símismo.mod, líms_paráms=líms_paráms, obs=obs)

        alg = _algs_spotpy[método.lower()] if isinstance(método, str) else método
        muestreador = alg(mod_spotpy, dbname=temp.name, dbformat='csv')
        if método is spotpy.algorithms.dream:
            muestreador.sample(repetitions=n_iter, runs_after_convergence=200)
        else:
            muestreador.sample(n_iter)
        egr_spotpy = pd.read_csv(temp.name + '.csv')

        cols_prm = [c for c in egr_spotpy.obt_nombres_cols() if c.startswith('par')]
        trzs = egr_spotpy.obt_datos(cols_prm)
        probs = egr_spotpy.obt_datos('like1')['like1']

        if método is spotpy.algorithms.dream:
            trzs = {p: trzs[p][-200:] for p in cols_prm}
        elif método is not spotpy.algorithms.mcmc:
            buenas = (probs >= 0.80)
            trzs = {p: trzs[p][buenas] for p in cols_prm}

        res = {}
        for p in líms_paráms:
            col_p = ('par' + p).replace(' ', '_')
            res[p] = {'dist': trzs[col_p], 'val': _calc_máx_trz(trzs[col_p])}

        return res


class _ModSpotPy(object):
    def __init__(símismo, mod, líms_paráms, obs):
        """

        Parameters
        ----------
        mod : Modelo.Modelo
        líms_paráms : dict
        obs: xr.Dataset
        """

        símismo.paráms = [
            spotpy.parameter.Uniform(re.sub('\W|^(?=\d)', '_', p), low=d[0], high=d[1], optguess=(d[0] + d[1]) / 2)
            for p, d in líms_paráms.items()
        ]
        símismo.nombres_paráms = list(líms_paráms)
        símismo.mod = mod
        símismo.vars_interés = sorted(list(obs.data_vars))
        símismo.t_final = len(obs['n']) - 1

        símismo.mu_obs = símismo._aplastar(obs.mean())
        símismo.sg_obs = símismo._aplastar(obs.std())
        símismo.obs_norm = símismo._aplastar((obs - obs.mean()) / obs.std())

    def parameters(símismo):
        return spotpy.parameter.generate(símismo.paráms)

    def simulation(símismo, x):
        res = símismo.mod.simular(
            t_final=símismo.t_final, vars_interés=símismo.vars_interés, vals_inic=dict(zip(símismo.nombres_paráms, x))
        )
        m_res = np.array([res[v].values for v in símismo.vars_interés]).T

        return ((m_res - símismo.mu_obs) / símismo.sg_obs).T.ravel()

    def evaluation(símismo):
        return símismo.obs_norm

    def objectivefunction(símismo, simulation, evaluation, params=None):
        # like = spotpy.likelihoods.gaussianLikelihoodMeasErrorOut(evaluation,simulation)
        like = spotpy.objectivefunctions.nashsutcliffe(evaluation, simulation)

        return like

    def _aplastar(símismo, datos):
        if isinstance(datos, xr.Dataset):
            return np.array([datos[v].values.ravel() for v in símismo.vars_interés]).ravel()
        elif isinstance(datos, dict):
            return np.array([datos[v].ravel() for v in sorted(datos)]).ravel()


_algs_spotpy = {
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
