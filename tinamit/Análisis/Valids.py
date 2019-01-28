import numpy as np
import pandas as pd
import scipy.optimize as optim
import scipy.stats as estad

from tinamit.Análisis.Calibs import aplastar, patro_proces, gen_gof


def validar_resultados(obs, matrs_simul, tol=0.75, tipo_proc=None, máx_prob=None, obj_func=None):
    """

    Parameters
    ----------
    obs : pd.DataFrame
    matrs_simul : dict[str, np.ndarray]

    Returns
    -------

    """
    l_vars = list(obs.data_vars)

    if tipo_proc is None:
        mu_obs = obs.mean()
        sg_obs = obs.std()
        mu_obs_matr = mu_obs.to_array().values  # array[3] for ['y'] should be --> array[1]
        sg_obs_matr = sg_obs.to_array().values  # [3]
        sims_norm = {vr: (matrs_simul[vr] - mu_obs_matr[í]) / sg_obs_matr[í] for í, vr in
                     enumerate(l_vars)}  # {'y': 50*21}
        obs_norm = {vr: ((obs - mu_obs) / sg_obs)[vr].values for vr in l_vars}  # {'y': 21}
        todas_sims = np.concatenate([x for x in sims_norm.values()], axis=1)  # 50*63 (63=21*3), 100*26*6,
        todas_obs = np.concatenate([x for x in obs_norm.values()])  # [63]
    else:
        mu_obs_matr, sg_obs_matr, obs_norm = aplastar(obs, l_vars)  # 6, 6, 6*21, obs_norm: dict {'y': 6*21}
        obs_norm = {va: obs_norm for va in l_vars}  # 63, 21*6, [nparray[38, 61]]
        sims_norm = {vr: (matrs - mu_obs_matr) / sg_obs_matr for vr, matrs in matrs_simul.items()}  # {'y': 100*21*6}

    if tipo_proc is None:
        egr = {
            'total': _valid(obs=todas_obs, sim=todas_sims, comport=False),
            'vars': {vr: _valid(obs=obs_norm[vr], sim=sims_norm[vr]) for vr in l_vars},
        }

        egr['éxito'] = all(v >= tol for ll, v in egr['total'].items() if 'ens' in ll) and \
                       all(v >= tol for vr in l_vars for ll, v in egr['vars'][vr].items() if 'ens' in ll)
        return egr
    elif tipo_proc == 'multidim':
        egr = {'vars': {vr: _valid(obs=obs_norm[vr].T, sim=sims_norm[vr], tipo_proc=tipo_proc, comport=False) for vr in
                        l_vars}}

        egr['éxito'] = all(v >= tol for vr in l_vars for v in egr['vars'][vr]['ens'])
        return egr
    else:
        sims_norm_T = {vr: np.array([sims_norm[vr][d, :].T for d in range(len(sims_norm[vr]))]) for vr in
                       l_vars}  # {'y': 100*6*21}
        if obj_func == 'AIC':
            obj_func = ['AIC', 'NSE']
            # eval (matriz_vacía.T, length_params), #6*21, []
            egr = {
                'vars': {vr:
                             {obj:
                                  gen_gof(tipo_proc, sim=sims_norm_T[vr], obj_func=obj,
                                          eval=patro_proces(tipo_proc, obs, obs_norm[vr], l_vars)) if obj == 'AIC'
                                  else gen_gof('multidim', sim=sims_norm_T[vr], obj_func=obj, eval=obs_norm[vr])
                              for obj in obj_func}
                         for vr in l_vars}
            }  # 100*62*38
            egr['éxito_nse'] = all(v >= tol for vr in l_vars for v in egr['vars'][vr]['NSE'])
            # egr['éxito_aic'] = all((egr['vars'][vr]['AIC'] - máx_prob) >= 2 for vr in l_vars)
            egr['éxito_aic'] = all((np.max(egr['vars'][vr]['AIC']) - máx_prob) >= 2 for vr in l_vars)
        else:
            egr = {
                'vars': {vr:
                             {obj_func: gen_gof('multidim', sim=sims_norm_T[vr], obj_func=obj_func, eval=obs_norm[vr])}
                         for vr in l_vars}
            }
            egr['éxito_nse'] = all(v >= tol for vr in l_vars for v in egr['vars'][vr]['NSE'])
    return egr


def _valid(obs, sim, comport=True, tipo_proc=None):  # obs63, sim 50*63//100*21*6
    if tipo_proc is None:
        ic_teor, ic_sim = _anlz_ic(obs, sim)
        egr = {
            'rcem': _rcem(obs, np.nanmean(sim, axis=0)),
            'ens': _ens(obs, np.nanmean(sim, axis=0)),
            'rcem_ic': _rcem(obs=ic_teor, sim=ic_sim),
            'ens_ic': _ens(obs=ic_teor, sim=ic_sim),
        }
    else:
        egr = {
            'rcem': np.array([_rcem(obs, sim[i, :]) for i in range(len(sim))]),
            'ens': np.array([_ens(obs, sim[i, :]) for i in range(len(sim))])
        }
    if comport:
        egr.update({
            'forma': _anlz_forma(obs=obs, sim=sim),
            'tendencia': _anlz_tendencia(obs=obs, sim=sim)
        })

    return egr


def _rcem(obs, sim):
    return np.sqrt(np.nanmean((obs - sim) ** 2))


def _ens(obs, sim):
    return 1 - np.nansum((obs - sim) ** 2) / np.nansum((obs - np.nanmean(obs)) ** 2)


def _anlz_ic(obs, sim):
    n_sims = sim.shape[0]  # 50
    prcnts_act = np.array(
        [np.nanmean(np.less(obs, np.percentile(sim, i / n_sims * 100))) for i in range(n_sims)]
    )  # sim 100*21*6
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
    return np.nanmean(ajusto_sims)


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
