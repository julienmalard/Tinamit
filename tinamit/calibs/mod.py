import re
import tempfile

import numpy as np
import pandas as pd
import spotpy as sp
import xarray as xr
import platform

from tinamit.cositas import detectar_codif
from tinamit.datos.bd import BD

from ._utils import calc_máx_trz, algs_spotpy, eval_funcs


class CalibradorMod(object):
    """
    Clase pariente para cada calibrador de modelo.
    """

    def __init__(símismo, mod):
        símismo.mod = mod

    def calibrar(símismo, líms_paráms, datos, método='epm', n_iter=300, vars_obs=None):
        """
        Efectuar la calibración.

        Parameters
        ----------
        líms_paráms: dict
            Diccionario de cada parámetro con sus límites teoréticos.
        datos: xr.Dataset or xr.DataArray or str or pd.DataFrame or dict or Fuente or list or BD
            Los datos para la calibración.
        método
        n_iter
        vars_obs

        Returns
        -------

        """
        # Para hacer: limpiar comunicación de datos entre calibrador y CalibradorGeog, y también con validadores
        if isinstance(datos, xr.Dataset):
            obs = datos
        else:
            datos = datos if isinstance(datos, BD) else BD(datos)
            obs = datos.obt_vals(vars_obs)

        return símismo._efec_calib(líms_paráms=líms_paráms, método=método, n_iter=n_iter, obs=obs)

    def _efec_calib(símismo, líms_paráms, método, n_iter, obs):
        """
        Efectua la calibración.

        Parameters
        ----------
        líms_paráms: dict
            Diccionario de cada parámetro con sus límites teoréticos.
        método
        n_iter
        obs: xr.Dataset

        Returns
        -------

        """
        raise NotImplementedError


class CalibradorModSpotPy(CalibradorMod):

    def _efec_calib(símismo, líms_paráms, método, n_iter, obs):

        temp = tempfile.NamedTemporaryFile('w', encoding='UTF-8', prefix='CalibTinamït_')

        mod_spotpy = _ModSpotPy(mod=símismo.mod, líms_paráms=líms_paráms, obs=obs)

        alg = algs_spotpy[método.lower()] if isinstance(método, str) else método
        muestreador = alg(mod_spotpy, dbname=temp.name, dbformat='csv')
        if método is sp.algorithms.dream:
            muestreador.sample(repetitions=n_iter, runs_after_convergence=200)
        else:
            muestreador.sample(n_iter)

        codif = detectar_codif(temp.name + '.csv', máx_líneas=1) if platform.system() == 'Windows' else 'utf8'
        egr_spotpy = pd.read_csv(temp.name + '.csv', encoding=codif)

        cols_prm = [c for c in egr_spotpy.columns if c.startswith('par')]
        probs = egr_spotpy['like1']

        if método in (sp.algorithms.dream, sp.algorithms.mcmc):
            trzs = {p: egr_spotpy[p][-200:] for p in cols_prm}
        else:
            buenas = (probs >= 0.80)
            trzs = {p: egr_spotpy[p][buenas] for p in cols_prm}

        res = {}
        for p in líms_paráms:
            col_p = ('par' + p).replace(' ', '_')
            res[p] = {
                'dist': trzs[col_p], 'cumbre': calc_máx_trz(trzs[col_p]),
                'mejor': egr_spotpy[col_p][np.argmax(probs.values)]
            }

        return res


class _ModSpotPy(object):
    def __init__(símismo, mod, líms_paráms, obs, f_obj='ens'):
        """

        Parameters
        ----------
        mod : Modelo.Modelo
        líms_paráms : dict
        obs: xr.Dataset
        """

        símismo.paráms = [
            sp.parameter.Uniform(re.sub('\W|^(?=\d)', '_', p), low=d[0], high=d[1], optguess=(d[0] + d[1]) / 2)
            for p, d in líms_paráms.items()
        ]
        símismo.nombres_paráms = list(líms_paráms)
        símismo.mod = mod
        símismo.vars_interés = sorted(list(obs.data_vars))
        símismo.t_final = len(obs['n']) - 1  # para hacer: arreglar

        símismo.mu_obs = símismo._aplastar(obs.mean())
        símismo.sg_obs = símismo._aplastar(obs.std())
        símismo.obs_norm = símismo._aplastar((obs - obs.mean()) / obs.std())

        símismo.func = eval_funcs[f_obj.lower()]

    def parameters(símismo):
        return sp.parameter.generate(símismo.paráms)

    def simulation(símismo, x):
        res = símismo.mod.simular(
            t=símismo.t_final, vars_interés=símismo.vars_interés, extern=dict(zip(símismo.nombres_paráms, x))
        )
        m_res = np.array([res[v].vals for v in símismo.vars_interés]).T

        return ((m_res - símismo.mu_obs) / símismo.sg_obs).T.ravel()

    def evaluation(símismo):
        return símismo.obs_norm

    def objectivefunction(símismo, simulation, evaluation, params=None):
        return símismo.func(evaluation, simulation, f=None)

    def _aplastar(símismo, datos):
        if isinstance(datos, xr.Dataset):
            return np.array([datos[v].values.ravel() for v in símismo.vars_interés]).ravel()
        elif isinstance(datos, dict):
            return np.array([datos[v].ravel() for v in sorted(datos)]).ravel()
