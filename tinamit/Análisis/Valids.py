import numpy as np
import pandas as pd
import scipy.optimize as optim
import scipy.stats as estad


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
        'total': _valid(obs=todas_obs, sim=todas_sims, comport=False),
        'vars': {vr: _valid(obs=obs_norm[vr], sim=sims_norm[vr]) for vr in l_vars},
    }
    egr['éxito'] = all(v >= tol for ll, v in egr['total'].items() if 'ens' in ll) and \
                   all(v >= tol for vr in l_vars for ll, v in egr['vars'][vr].items() if 'ens' in ll)

    return egr


def _valid(obs, sim, comport=True):
    ic_teor, ic_sim = _anlz_ic(obs, sim)

    egr = {
        'rcem': _rcem(obs, np.mean(sim, axis=0)),
        'ens': _ens(obs, np.mean(sim, axis=0)),
        'rcem_ic': _rcem(obs=ic_teor, sim=ic_sim),
        'ens_ic': _ens(obs=ic_teor, sim=ic_sim),
    }

    if comport:
        egr.update({
            'forma': _anlz_forma(obs=obs, sim=sim),
            'tendencia': _anlz_tendencia(obs=obs, sim=sim)
        })

    return egr


def _rcem(obs, sim):
    return np.sqrt(np.mean(np.square(obs - sim)))


def _ens(obs, sim):
    return 1 - np.sum(np.square(obs - sim)) / np.sum(np.square(obs - np.mean(obs)))


def _anlz_ic(obs, sim):
    n_sims = sim.shape[0]
    prcnts_act = np.array([np.mean(np.less(obs, np.percentile(sim, i / n_sims * 100))) for i in range(n_sims)])
    prcnts_teor = np.arange(0, 1, 1 / n_sims)
    return prcnts_act, prcnts_teor


formas_potenciales = {
    'lin': {'f': lambda x, a, b: x * a + b},
    'expon': {'f': lambda x, a, b, c: a * c ** x + b},
    'logíst': {'f': lambda x, a, b, c, d: a / (1 + np.exp(-b * (x - c))) - a + d},
    'log': {'f': lambda x, a, b: a * np.log(x) + b},
    # 'gamma': {'f': lambda x, a, b, c, d: a * estad.gamma.pdf(x=x/c, a=b, scale=1) + d}
}


def _anlz_forma(obs, sim):
    dic_forma = _aprox_forma(obs)
    forma_obs = dic_forma['forma']
    ajusto_sims = np.array([_ajustar(s, forma=forma_obs)[0] for s in sim])
    return ajusto_sims.mean()


def _aprox_forma(vec):
    ajuste = {'forma': None, 'ens': -np.inf, 'paráms': {}}

    for frm in formas_potenciales:
        ajst, prms = _ajustar(vec, frm)
        if ajst > ajuste['ens']:
            ajuste['forma'] = frm
            ajuste['ens'] = ajst
            ajuste['paráms'] = prms

    return ajuste


def _ajustar(vec, forma):
    datos_x = np.arange(len(vec))
    f = formas_potenciales[forma]['f']
    try:
        prms = optim.curve_fit(f=f, xdata=datos_x, ydata=vec)[0]
        ajst = _ens(vec, f(datos_x, *prms))
    except RuntimeError:
        prms = None
        ajst = -np.inf
    return ajst, prms


def _anlz_tendencia(obs, sim):
    x = np.arange(len(obs))
    pend_obs = estad.linregress(x, obs)[0]
    pends_sim = [estad.linregress(x, s)[0] for s in sim]
    pend_obs_pos = pend_obs > 0
    if pend_obs_pos:
        correctos = np.greater(pends_sim, 0)
    else:
        correctos = np.less_equal(pends_sim, 0)

    return correctos.mean()
