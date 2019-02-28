from sklearn.metrics import cohen_kappa_score
import numpy as np
import scipy.optimize as optim
import scipy.stats as estad
from matplotlib import pyplot
from pandas.plotting import autocorrelation_plot

from tinamit.Análisis.Calibs import aplastar, patro_proces, gen_gof
from tinamit.Análisis.Sens.behavior import predict


def validar_resultados(obs, matrs_simul, tol=0.65, tipo_proc=None, máx_prob=None, obj_func=None, save_plot=None,
                       ind_simul=None, gard=None):
    """

    patt_vec['bp_params']
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
        sims_norm = {vr: np.empty(matrs_simul[vr].shape) for vr in l_vars}
        for vr, matrs in matrs_simul.items():
            for i in range(len(matrs)):
                sims_norm[vr][i] = (matrs[i] - mu_obs_matr) / sg_obs_matr
        # sims_norm = {vr: (matrs - mu_obs_matr) / sg_obs_matr for vr, matrs in matrs_simul.items()}  # {'y': 100*21*6}

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

    elif tipo_proc == 'patrón':
        sims_norm_T = {vr: np.array([sims_norm[vr][d, :].T for d in range(len(sims_norm[vr]))]) for vr in
                       l_vars}  # {'y': 100*6*21}; 144*18*41
        if obj_func == 'AIC':
            egr = {vr: {obj:
                            gen_gof(tipo_proc, sim=sims_norm_T[vr], obj_func=obj,
                                    eval=patro_proces(tipo_proc, obs, obs_norm[vr], l_vars)) if obj == 'AIC'
                            else gen_gof('multidim', sim=sims_norm_T[vr], obj_func=obj, eval=obs_norm[vr])
                        for obj in ['AIC', 'NSE']}
                   for vr in l_vars}

            egr['éxito_nse'] = all(v >= tol for vr in l_vars for v in egr[vr]['NSE'])
            egr['éxito_aic'] = all((v - máx_prob) > 2 for vr in l_vars for v in egr[vr]['AIC'])
            prom = np.array([v for vr in l_vars for v in egr[vr]['AIC']]).mean()
            egr['diff_aic'] = {'valid_prom': prom, 'calib_máx_prob': máx_prob, 'diff': prom - máx_prob}
            egr['ind_simul'] = ind_simul

        elif obj_func.lower() == 'multi_behavior_tests':
            patrón_valid = PatrónValidTest(obs, mu_obs_matr, obs_norm, tipo_proc, sims_norm, l_vars,
                                           save_plot=save_plot, gard=gard)
            pat_valid = patrón_valid.conduct_validate()
            egr = {vr: {obj_func.lower(): pat_valid} for vr in l_vars}

        elif obj_func.lower() == 'kappa':
            kappa = _kappa(obs, obs_norm, sims_norm, tipo_proc, l_vars)
            egr = {vr: {obj_func.lower(): kappa} for vr in l_vars}

        else:
            egr = {
                'vars': {vr:
                             {obj_func.lower(): gen_gof('multidim', sim=sims_norm_T[vr], obj_func=obj_func,
                                                        eval=obs_norm[vr])}
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


class PatrónValidTest(object):
    def __init__(símismo, obs, mu_obs_matr, obs_norm, tipo_proc, sims_norm, l_vars, save_plot, gard=None):
        símismo.obs = obs
        símismo.tipo_proc = tipo_proc
        símismo.vars_interés = l_vars
        símismo.obs_norm = obs_norm  # {wtd: t*18}
        símismo.mu_obs = mu_obs_matr
        símismo.sim_norm = sims_norm  # {wtd: N*t*18}
        símismo.save_plot = save_plot
        símismo.gard = gard

    @staticmethod
    def trend_compare(obs, obs_norm, sim_norm, tipo_proc, vars_interés, save_plot, gard=None):
        '''
        Returns
        -------
        trend = {'t_obs': {'best_patt': [],
                            poly: {'patt': 'bp_param':
                                            'y_pred':
                                   }
                            }

                't_sim': {'n1': {poly: {'patt': 'bp_param':
                                            'y_pred':
                                   }
                                    }
                            }
                }
        '''
        poly = obs['x0'].values
        for vr in vars_interés:
            trend = {'t_obs': {}, 't_sim': {f'n{n}': {} for n in range(sim_norm[vr].shape[0])}}
            print("\n\n****Start detecting observed data****\n\n")
            t_obs = patro_proces(tipo_proc, obs, obs_norm[vr],
                                 valid=True)  # eval={17:'inverso':{bp_param:xx, gof:xx}, 'y_pred':41}
            trend['t_obs'].update({'best_patt': [list(v.keys())[0] for i, v in t_obs.items()]})
            trend['t_obs'].update(t_obs)

            for n in range(sim_norm[vr].shape[0]):  # if the pattens are the same and the values with index are the same
                print(f"\nDetecting the {n}-th simulation\n")
                t_sim = patro_proces(tipo_proc, obs, sim_norm[vr][n, :].T,
                                     valid=True)  # {n1:  {17:'inverso':{bp_param:xx, gof:xx}, 'y_pred':41}
                for ind, patt in enumerate([list(v.keys())[0] for i, v in t_sim.items()]):
                    if patt == trend['t_obs']['best_patt'][ind]:
                        if np.count_nonzero(np.isnan(t_obs[poly[ind]]['y_pred']
                                                     [~np.isnan(t_sim[poly[ind]]['y_pred'])])) == 0:
                            trend['t_sim'][f'n{n}'][poly[ind]] = t_sim[poly[ind]]
            dele_sim = {}
            for sim, vec in trend['t_sim'].items():
                if len(vec):
                    dele_sim[sim] = vec
            dele_p_sim = {i: {} for i in dele_sim}
            for sim, p_vec in dele_sim.items():
                for p, v in p_vec.items():
                    if np.nanmax(dele_sim[sim][p]['y_pred']) > 0:
                        dele_p_sim[sim][p] = dele_sim[sim][p]

            trend['t_sim'] = dele_p_sim

            if save_plot is not None:
                for p in poly:
                    occr = []
                    for n, po_vec in trend['t_sim'].items():
                        if p in po_vec:
                            occr.append(po_vec[p]['y_pred'])
                    if len(occr):
                        pyplot.ioff()
                        pyplot.plot(trend['t_obs'][p]['y_pred'], 'g--', label="obs")
                        for aray in occr:
                            pyplot.plot(aray, 'r-.', label=f"sim")
                        pyplot.legend(bbox_to_anchor=(0.8, 0.8), loc=3, mode="expand", borderaxespad=0.)
                        pyplot.savefig(save_plot + f't_poly_{p}')
                        pyplot.close('all')
            if gard:
                np.save(gard + '-trend', trend)
            return poly, trend

    def detrend(símismo, poly, trend, obs_norm, sim_norm):
        '''

        Returns
        -------
        detrend = {'d_obs': {'best_patt': [],
                                    poly: { zi }
                                    }

                        'd_sim': {'poly': {n: {zi}
                                           }
                                            }
                        }
        '''

        def _d_trend(d_bparams, patt, dt_norm):
            x_data = np.arange(dt_norm.shape[0])
            return dt_norm - predict(x_data, d_bparams, patt)

        detrend = {'d_obs': {}, 'd_sim': {}}
        for vr, dt in obs_norm.items():
            for p in poly:
                for n, poly_vec in trend['t_sim'].items():
                    if p in poly_vec:
                        detrend['d_obs'][p] = _d_trend(list(trend['t_obs'][p].values())[0]['bp_params'],
                                                       trend['t_obs']['best_patt'][list(poly).index(p)],
                                                       obs_norm[vr][list(poly).index(p), :])  # 18*41

                        obs = list(list(trend['t_obs'][p].values())[0]['bp_params'].values())
                        sim = list(list(trend['t_sim'][n][p].values())[0]['bp_params'].values())
                        stat, alpha = estad.ttest_ind(obs, sim)
                        if alpha > 0.05:
                            if not len(detrend['d_sim']) or p not in detrend['d_sim']:
                                detrend['d_sim'][p] = {}
                            detrend['d_sim'][p].update({n: _d_trend(list(poly_vec[p].values())[0]['bp_params'],
                                                                    trend['t_obs']['best_patt'][list(poly).index(p)],
                                                                    sim_norm[vr][int(n[-1]), :].T[list(poly).index(p),
                                                                    :])})  # 2*41*18--18*41--41

            if símismo.save_plot is not None:
                pyplot.ioff()
                for p in detrend['d_sim']:
                    pyplot.plot(detrend['d_obs'][p], 'g--', label="d_obs")
                    for n in detrend['d_sim'][p]:
                        pyplot.plot(detrend['d_sim'][p][n], 'r-.', label=f"d_sim-{n}")
                    pyplot.legend(bbox_to_anchor=(0.8, 0.8), loc=3, mode="expand", borderaxespad=0.)
                    pyplot.savefig(símismo.save_plot + f'd_poly_{p}')
                    pyplot.close('all')
        if símismo.gard:
            np.save(símismo.gard + '-detrend', detrend)
        return detrend

    def period_compare(símismo, detrend):
        def _compute_var_rk(auto_corr):
            var_rk = []
            N = len(auto_corr) - 1
            for k in range(N):
                summ = []
                for i in range(1, N - 1):
                    if k + i > N:
                        break
                    summ.append((N - i) * (auto_corr[k - i] + auto_corr[k + i] -
                                           2 * auto_corr[k] * auto_corr[i]) ** 2)
                var_rk.append(np.nansum(summ) / (N * (N + 2)))
            return np.asarray(var_rk)

        def _se(var_rs, var_ra):
            se = []
            for k in range(len(var_ra)):
                se.append(np.sqrt(var_rs[k] - var_ra[k]))
            return np.asarray(se)

        def _rk(vec):
            N = len(vec) - 1
            cov = []
            for k in range(N):
                summ = []
                for i in range(1, N - k):
                    if i + k > N:
                        break
                    summ.append((vec[i] - np.nanmean(vec)) * (vec[i + k] - np.nanmean(vec)))
                cov.append((np.nansum(summ) / N) / np.nanvar(vec))
            return np.asarray(cov)

        autocorrelation = {'corr_obs': {}, 'corr_sim': {}}
        for p, v in detrend['d_obs'].items():
            s_obs = _rk(v)
            pyplot.ioff()
            autocorrelation_plot(s_obs, color='green', linestyle='dashed')
            autocorrelation['corr_obs'].update({p: s_obs})

            for n in detrend['d_sim'][p]:
                s_sim = _rk(detrend['d_sim'][p][n])
                pyplot.plot(s_sim, 'r-.', label=f"autocorr_sim-{n}")
                if not autocorrelation['corr_sim'] or p not in autocorrelation['corr_sim']:
                    autocorrelation['corr_sim'][p] = {}
                autocorrelation['corr_sim'][p].update({n: s_sim})
            pyplot.title("Autocorrelations of the time patterns (after trend removal)")
            pyplot.savefig(símismo.save_plot + f'autocorr_{p}')
            pyplot.close('all')

        autocorr_var = {'var_obs': {}, 'var_sim': {}, 'diff': {}, 'se': {}, 'pass_diff': {}}
        for p, vec_obs in autocorrelation['corr_obs'].items():
            autocorr_var['var_obs'].update({p: _compute_var_rk(vec_obs)})
            for n in autocorrelation['corr_sim'][p]:
                var_sim = _compute_var_rk(autocorrelation['corr_sim'][p][n])
                vec_sim = np.asarray(autocorrelation['corr_sim'][p][n])
                if not autocorr_var['var_sim'] or p not in autocorr_var['var_sim']:
                    autocorr_var['var_sim'][p] = {}
                    autocorr_var['diff'][p] = {}
                    autocorr_var['se'][p] = {}
                    autocorr_var['pass_diff'][p] = {}

                autocorr_var['var_sim'][p].update({n: var_sim})
                diff = vec_sim - vec_obs
                se = _se(vec_sim, vec_obs)
                autocorr_var['diff'][p].update({n: diff})
                autocorr_var['se'][p].update({n: se})
                autocorr_var['pass_diff'][p].update({n: []})
                for k in range(len(diff)):
                    if np.negative(se)[k] <= diff[k] <= se[k]:
                        autocorr_var['pass_diff'][p][n].append(diff[k])
                    else:
                        autocorr_var['pass_diff'][p][n].append(np.nan)

        if símismo.save_plot is not None:
            pyplot.ioff()
            for p in autocorr_var['diff']:
                for n in autocorr_var['diff'][p]:
                    autocorrelation_plot(autocorr_var['diff'][p][n], y_label='Differences', label='diff', color='green',
                                         linestyle='dashed')
                    pyplot.plot(autocorr_var['se'][p][n], 'r-.', label=f"2SE")
                    pyplot.plot(sorted(np.negative(autocorr_var['se'][p][n])), 'r-.')
                pyplot.title("Differences of ACFs, 2Se confidence band")
                pyplot.legend(bbox_to_anchor=(0.8, 0.8), loc=3, mode="expand", borderaxespad=0.)
                pyplot.savefig(símismo.save_plot + f'diff_{p}')
                pyplot.close('all')

        if símismo.gard:
            np.save(símismo.gard + '-Rk', autocorrelation)
            np.save(símismo.gard + '-autocorr_variables', autocorr_var)

        return autocorr_var

    def mean_compare(símismo, detrend, autocorr_var):
        l_sim = {}  # {p: [n1, n3, n4]}
        for p in autocorr_var['pass_diff']:
            for n in autocorr_var['pass_diff'][p]:
                if np.count_nonzero(~np.isnan(autocorr_var['pass_diff'][p][n])):
                    if not len(l_sim) or p not in l_sim:
                        l_sim[p] = []
                    l_sim[p].append(n)

        mu = { }
        for p, l_sim in l_sim.items():
            mu_obs = np.nanmean(detrend['d_obs'][p])
            for n in l_sim:
                mu_sim = np.nanmean(detrend['d_sim'][p][n])
                n_mu = abs(mu_sim - mu_obs) / mu_obs
                if n_mu > 0.05:
                    if not len(mu) or p not in mu:
                        mu[p] = { }
                    mu[p].update({n: n_mu})

        if símismo.gard:
            np.save(símismo.gard + '-Mean', mu)

        return mu

    def amplitude_compare(símismo, detrend, mu):
        std = { }
        for p, sim_vec in mu.items():
            std_obs = np.nanstd(detrend['d_obs'][p])
            for n in sim_vec:
                std_sim = np.nanstd(detrend['d_sim'][p][n])
                n_std = abs(std_sim - std_obs) / std_obs
                if n_std > 0.3:
                    if not len(std) or p not in std:
                        std[p] = { }
                    std[p].update({n: n_std})

        if símismo.gard:
            np.save(símismo.gard + '-Std', std)

        return std

    def phase_lag(símismo, detrend, amplitude):
        # Max-Min>0.8
        def _csa(ai, si, len_k):
            csa = []
            mu_s = np.nanmean(si)
            mu_a = np.nanmean(ai)
            std_s = np.nanstd(si)
            std_a = np.nanstd(ai)
            N = len(ai)
            for k in range(len_k):
                summ = []
                for i in range(k, N):
                    summ.append((si[i] - mu_s) * (ai[i - k] - mu_a))
                csa.append(np.nansum(summ) / (std_s * std_a * N))
            return np.asarray(csa)

        def _cas(ai, si, len_k):
            cas = []
            mu_s = np.nanmean(si)
            mu_a = np.nanmean(ai)
            std_s = np.nanstd(si)
            std_a = np.nanstd(ai)
            N = len(ai)
            for lag in range(len_k):
                neg_k = np.negative(lag)
                summ = []
                for i in range(lag, N):
                    summ.append((ai[i] - mu_a) * (si[i + neg_k] - mu_s))
                cas.append(np.nansum(summ) / (std_s * std_a * N))
            return np.asarray(cas)

        phase = { }
        for p in amplitude:
            for n in amplitude[p]:
                len_k = len(detrend['d_obs'][p]) - 1
                k = sorted([np.negative(i) for i in np.arange(len_k)])
                k.extend(np.arange(len_k))
                cas = _cas(detrend['d_sim'][p][n], detrend['d_obs'][p], len_k)
                csa = _csa(detrend['d_sim'][p][n], detrend['d_obs'][p], len_k)
                lag_v = np.concatenate([cas, csa])
                if np.nanmax(lag_v) - np.nanmin(lag_v) > 0.6:
                    if not len(phase) or p not in phase:
                        phase[p] = { }
                    phase[p].update({n: lag_v, '|max − min|': np.nanmax(lag_v) - np.nanmin(lag_v)})

                if símismo.save_plot is not None:
                    pyplot.ioff()
                    for p in phase:
                        for n in phase[p]:
                            if n != '|max − min|':
                                autocorrelation_plot(lag_v, y_label='Correlations', label='ccf',
                                                     # ax=pyplot.gca(xlim=(-n / 2, n / 2), ylim=(-1.0, 1.0)),
                                                     color='blue', linestyle='dashed')
                    pyplot.title(f"Cross-correlation between obs and sim patterns of poly-{n}")
                    pyplot.legend(bbox_to_anchor=(0.8, 0.8), loc=3, mode="expand", borderaxespad=0.)
                    pyplot.savefig(símismo.save_plot + f'ccf_{p}')
                    pyplot.close('all')

        if símismo.gard:
            np.save(símismo.gard + '-phase', phase)

        return phase

    def discrepancy(símismo, detrend, phase):
        def _sse(vec):
            sse_sum = np.nansum((vec - np.nanmean(vec)) ** 2)
            sse = np.sqrt(sse_sum)
            return sse

        u = { }
        for p in phase:
            si = detrend['d_obs'][p]
            for n in phase[p]:
                if n != '|max − min|':
                    ai = detrend['d_sim'][p][n]
                    si_ai = si - ai
                    n_u = _sse(si_ai) / (_sse(si) + _sse(ai))
                    if n_u < 0.7:
                        if not len(u) or p not in u:
                            u[p] = { }
                        u[p].update({n: n_u})
        if símismo.gard:
            np.save(símismo.gard + '-U', u)
        return u

    def conduct_validate(símismo):
        poly, trend = símismo.trend_compare(símismo.obs, símismo.obs_norm, símismo.sim_norm, símismo.tipo_proc,
                                            símismo.vars_interés, símismo.save_plot, símismo.gard)
        detrend = símismo.detrend(poly, trend, símismo.obs_norm, símismo.sim_norm)
        autocorr_var = símismo.period_compare(detrend)
        mu = símismo.mean_compare(detrend, autocorr_var)
        amplitude = símismo.amplitude_compare(detrend, mu)
        phase = símismo.phase_lag(detrend, amplitude)
        u = símismo.discrepancy(detrend, phase)
        return u


def _kappa(obs, obs_norm, sim_norm, tipo_proc, vars_interés):
    '''
    trend = {'t_obs': {'best_patt': [],
                            poly: {'patt': 'bp_param':
                                            'y_pred':
                                   }
                            }

                't_sim': {'n1': {poly: {'patt': 'bp_param':
                                            'y_pred':
                                   }
                                    }
                            }
                }


    '''
    poly, trend = PatrónValidTest.trend_compare(obs, obs_norm, sim_norm, tipo_proc, vars_interés, save_plot=None)
    kappa = {}
    for p in poly:
        for n, poly_vec in trend['t_sim'].items():
            if p in poly_vec:
                if not len(kappa) or p not in kappa:
                    kappa[p] = {}
                obs = list(list(trend['t_obs'][p].values())[0]['bp_params'].values())
                sim = list(list(trend['t_sim'][n][p].values())[0]['bp_params'].values())
                ka = cohen_kappa_score([sorted(obs).index(v) for i, v in enumerate(obs)],
                                       [sorted(sim).index(v) for i, v in enumerate(sim)])
                if ka > 0.6:
                    kappa[p].update({n: ka})

    return kappa
