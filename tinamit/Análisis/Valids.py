import numpy as np
import pandas as pd


def validar_resultados(obs, matrs_simul):
    """

    Parameters
    ----------
    obs : pd.DataFrame
    matrs_simul : dict[str, np.ndarray]

    Returns
    -------

    """
    tol = 0.80

    l_vars = list(obs)
    mu_obs = obs.mean().values
    sg_obs = obs.std().values
    sims_norm = {vr: (matrs_simul[vr] - mu_obs[í]) / sg_obs[í] for í, vr in enumerate(l_vars)}
    obs_norm = {vr: ((obs - mu_obs) / sg_obs)[vr].values for vr in l_vars}

    todas_sims = np.concatenate([x for x in sims_norm.values()], axis=1)
    todas_obs = np.concatenate([x for x in obs_norm.values()])
    egr = {
        'total': _valid(obs=todas_obs, sim=todas_sims),
        'vars': {vr: _valid(obs=obs_norm[vr], sim=sims_norm[vr]) for vr in l_vars},
    }
    egr['éxito'] = all(v >= tol for ll, v in egr['total'].items() if 'ens' in ll) and \
                   all(v >= tol for vr in l_vars for ll, v in egr['vars'][vr].items() if 'ens' in ll)

    return egr


def _valid(obs, sim):
    ic_teor, ic_sim = _anal_ic(obs, sim)

    egr = {
        'rcem': _rcem(obs, np.mean(sim, axis=0)),
        'ens': _ens(obs, np.mean(sim, axis=0)),
        'rcem_ic': _rcem(obs=ic_teor, sim=ic_sim),
        'ens_ic': _ens(obs=ic_teor, sim=ic_sim)
    }
    return egr


def _rcem(obs, sim):
    return np.sqrt(np.mean(np.square(obs - sim)))


def _ens(obs, sim):
    return 1 - np.sum(np.square(obs - sim)) / np.sum(np.square(obs - np.mean(obs)))


def _anal_ic(obs, sim):
    n_sims = sim.shape[0]
    prcnts_act = np.array([np.mean(np.less(obs, np.percentile(sim, i / n_sims * 100))) for i in range(n_sims)])
    prcnts_teor = np.arange(0, 1, 1 / n_sims)
    return prcnts_act, prcnts_teor
