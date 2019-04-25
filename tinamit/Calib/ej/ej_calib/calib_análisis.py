import operator
from matplotlib import pyplot
import numpy as np
from matplotlib_venn import venn3

# gard = "D:\Thesis\pythonProject\localuse\Dt\Calib\\cali_res\\original\\"

def load_path(cls, type, method):
    gard_point = "D:\Thesis\pythonProject\localuse\Dt\Calib\cali_res\\nse\\"
    calib_point=np.load(gard_point+'calib-fscabc_class_nse.npy').tolist()
    point_ind = np.argsort(calib_point['prob'])[-20:]
    # valid_point=np.load(gard_point+'fscabc-nse.npy').tolist()

    gard = f"D:\Thesis\pythonProject\localuse\Dt\Calib\\cali_res\\{cls}\\"
    # calib_abc = np.load(gard+f'calib_cluster.npy').tolist()
    calib_abc = np.load(gard + f'calib-{method}_class.npy').tolist()
    all_tests = np.load(gard +f"{type}21-{method}-aic.npy").tolist()  #
    calib_ind = np.argsort(calib_abc['prob'])[-20:]
    vr = 'mds_Watertable depth Tinamit'
    # sim_eq_obs = "D:\Thesis\pythonProject\localuse\Dt\Calib\cali_res\\reverse\\t_sim_all\\all\\all_sim_eq_obs.npy"
    d_trend = np.load(gard + f'{type}7-{method}-detrend.npy').tolist()
    trend_multi = np.load(gard + f'{type}21-{method}-trend.npy').tolist()
    trend_barlas = np.load(gard + f'{type}7-{method}-trend.npy').tolist()
    #agreement = np.load(gard + f'rev_agreemt-fscabc-coeffienct of agreement.npy').tolist()
    agreement = np.load(gard + f'agreemt-{method}-coeffienct of agreement.npy').tolist()
    return all_tests, vr, calib_ind, trend_multi, trend_barlas, d_trend, agreement, calib_abc, gard

def detect_21(calib_abc, all_tests, vr, obj_func, calib_ind, relate, threshold):
    obj = {}
    if obj_func == 'aic_21':
        aic = {i: calib_abc['prob'][i] for i in calib_ind}
    for p, vec in all_tests[vr][f'{obj_func}'].items():
        if obj_func == 'aic_21':
            if p not in obj:
                obj[p] = []
            # obj[p].extend([(key, value) for (key, value) in sorted(vec.items(), key=lambda x: x[1])][-threshold:])
            obj[p].extend([(key, value) for (key, value) in
                           sorted({n: v for n, v in vec.items() if n in [f'n{i}' for i in np.sort(calib_ind)]
                                   and v - aic[int(n[1:])] > 2}.items(), key=lambda x: x[1])])

        else:
            for n, v in vec.items():
                if obj_func == 'kappa':
                    if all(i == threshold for i in list(v.values())):
                        if p not in obj:
                            obj[p] = []
                        obj[p].append(int(n[1:]))
                elif relate(v, threshold):
                    if p not in obj:
                        obj[p] = []
                    obj[p].append((n, v))
    obj['n'] = []
    if obj_func == 'kappa':
        for i in np.asarray(list(set([n for p in obj for n in obj[p]]))):  # 69n, all=1
            if i in calib_ind:
                obj['n'].append(i)
    else:
        for i in [int(n[0][1:]) for p in obj for n in obj[p]]:
            if i in calib_ind:
                obj['n'].append(i)
    obj['n'] = set(obj['n'])
    if obj_func == 'aic_21':
        return aic, obj
    else:
        return obj

def coa(vr, calib_ind, agreement):
    kap = { }
    icc1 = { }
    kappa = agreement[vr]['kappa']
    icc = agreement[vr]['icc']
    for p in kappa:
        for n, v in kappa[p].items():
            if v['ka_slope'] == 1 and int(n[1:]) in calib_ind:
                if p not in kap:
                    kap[p] = []
                kap[p].append(n)
    kap['n'] = set([n for p in kap for n in kap[p]])
    kap['slope']  = all(v['ka_slope'] for p in kappa if p != 'n' for n , v in kappa[p].items() if int(n[1:]) in calib_ind and v['ka_slope']==1)

    for p in icc:
        for n in icc[p]:
            if icc[p][n] > 0.75 and int(n[1:]) in calib_ind:
                if p not in icc1:
                    icc1[p] = []
                icc1[p].append(n)
    icc1['n'] = set([n for p in icc1 for n in icc1[p]])
    icc1['all>0'] = all(v for p in icc if p != 'n' for n, v in icc[p].items() if int(n[1:]) in calib_ind and v>0.4)
    return kap, icc1

def point_based(obj_fun, all_tests, top_n, calib_ind):
    vr = 'mds_Watertable depth Tinamit'
    obj = {'n': {}}
    if obj_fun == 'RMSE':
        for i in np.argsort(all_tests[vr][obj_fun])[top_n:]:
            if i in calib_ind:
                obj['n'].update({i: all_tests[vr][obj_fun][i]})
    else:
        for i in np.argsort(all_tests[vr][obj_fun])[-top_n:]:
            if i in calib_ind:
                obj['n'].update({i: all_tests[vr][obj_fun][i]})
    return obj


def barlas(path, calib_ind, key=False, trend=False, vr=False, plot=False):
    out = np.load(path).tolist()
    if trend:
        n = [n for n in out[key] if int(n[1:]) in calib_ind]
        p = set(p for n1 in n for p in out[key][n1])
        pout = out[key]
    elif key == 'corr_sim':
        p = list(set(p for p in out[key] for n in out[key][p] if int(n[1:]) in calib_ind))  # 9
        n = set(n for p in out[key] for n in out[key][p] if int(n[1:]) in calib_ind)  # 63
        pout = out[key]
    elif key == 'multi_behavior_tests':
        n = set(n for p in out[vr][key] for n in out[vr][key][p] if n[-1] != '|' and int(n[1:]) in calib_ind)  # 10
        p = list(set(p for p in out[vr][key] for n in out[vr][key][p] if n[-1] != '|' and int(n[1:]) in calib_ind))
        pout = out[vr][key]
    else:
        n = set(n for p in out for n in out[p] if n[-1] != '|' and int(n[1:]) in calib_ind)  # 10
        p = list(set(p for p in out for n in out[p] if n[-1] != '|' and int(n[1:]) in calib_ind))
        pout = out
    if plot:
        p_n = [(pp, int(nn[1:])) for pp in pout for nn in list(n) if nn in pout[pp]]
        return p_n
    else:
        return n, p


# sub_4_plot = [only_b, only_aic, both_b_aic, only_k, both_b_k, both_aic_k, all]
def plot_venn(top_val, save_path, set_labels=('Multi-step tests', 'AIC', 'KAPPA')):
    # top_val = [11, 51, 4, 47, 25, 4, 1]
    loc = ('100', '010', '110', '001', '101', '011', '111')
    new_sub = {}
    for i, val in enumerate(loc):
        new_sub[val] = top_val[i]

    pyplot.ioff()
    v = venn3(subsets=new_sub, set_labels=set_labels)
    # v.get_label_by_id(loc[0]).set_text('best is n123')
    # v.get_label_by_id(loc[1]).set_text('best is n564')
    # v.get_label_by_id(loc[2]).set_text(f'overlapped 5')
    # # v.get_label_by_id(loc[3]).set_text(' ')
    # v.get_label_by_id(loc[4]).set_text('overlapped 25 simulations')
    # v.get_label_by_id(loc[5]).set_text('overlapped 5(include n564)')
    # v.get_label_by_id(loc[6]).set_text('478')
    pyplot.annotate('69 simulations are equally the best',
                    xy=v.get_label_by_id(loc[3]).get_position() - np.array([0, 0.05]),
                    ha='center', xytext=(0.1, 0.0001), textcoords='axes fraction',
                    bbox=dict(boxstyle='round,pad=0.5', fc='gray', alpha=0.1),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.3', color='gray'))

    pyplot.annotate('485-th run', xy=v.get_label_by_id(loc[6]).get_position() - np.array([0, 0.05]),
                    ha='center', xytext=(0.8, 0.2), textcoords='axes fraction',
                    bbox=dict(boxstyle='round,pad=0.5', fc='gray', alpha=0.1),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.3', color='gray'))

    pyplot.annotate('485-th run', xy=v.get_label_by_id(loc[6]).get_position() - np.array([0, 0.05]),
                    ha='center', xytext=(0.8, 0.2), textcoords='axes fraction',
                    bbox=dict(boxstyle='round,pad=0.5', fc='gray', alpha=0.1),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.3', color='gray'))

    pyplot.savefig(save_path)


def plot_top_sim(obj_func, trend_multi, trend_barlas, save_plot, calib_ind, all_tests, gard, type, method):
    vr = 'mds_Watertable depth Tinamit'
    if obj_func == 'multi_behavior_tests':
        p_n = barlas(gard + f"{type}7-{method}-phase.npy", calib_ind, plot=True)
        obj_func = 'Muti-behaviour tests'
        trend = trend_barlas
    elif obj_func == 'AIC':
        AIC = point_based('AIC', all_tests, 20, calib_ind)
        p_n = [(p, n) for n in AIC['n'] for p in trend_multi['t_sim'][f'n{n}']]
        trend = trend_multi
    else:
        p_n = []
        if obj_func == 'aic_21':
            aic, obj_21 = detect_21(all_tests, vr, 'aic_21', calib_ind, operator.gt, 20)
        elif obj_func == 'kappa':
            obj_21 = detect_21(all_tests, vr, 'kappa', calib_ind, operator.eq, 1)
            p_n = [(p, n) for p in obj_21 if not isinstance(p, str) for n in obj_21['n'] if n in obj_21[p]]
        elif obj_func == 'rmse_21':
            obj_21 = detect_21(all_tests, vr, 'rmse_21', calib_ind, operator.lt, 0.4)
        elif obj_func == 'nse_21':
            obj_21 = detect_21(all_tests, vr, 'nse_21', calib_ind, operator.gt, 0.7)
        if not len(p_n):
            p_n = [(p, n) for p in obj_21 if not isinstance(p, str) for n in list(obj_21['n']) if
                   f'n{n}' in [i[0] for i in obj_21[p]]]
        obj_func = obj_func[:3]
        trend = trend_multi
    mismatch_sim = {obj_func: []}
    for pn in p_n:
        obs_yred = trend['t_obs'][pn[0]]['y_pred']
        if f'n{pn[1]}' in trend['t_sim']:
            sim_yred = trend['t_sim'][f'n{pn[1]}'][pn[0]]['y_pred']
        else:
            mismatch_sim[obj_func].append(pn)
        pyplot.ioff()
        pyplot.plot(obs_yred, 'g--', label=f"obs_poly{pn[0]}")
        pyplot.plot(sim_yred, 'r-.', label=f"sim_{pn[1]}")

        pyplot.legend()
        pyplot.title(f'{obj_func}-poly{pn[0]}-sim{pn[1]} Vs Obs{pn[0]}')
        pyplot.savefig(save_plot + f'{obj_func}_poly{pn[0]}_sim{pn[1]}')
        pyplot.close('all')
    return mismatch_sim



def prep_cluster_dt(obj_func, vr, sim_eq_obs):
    obj = sim_eq_obs[vr][obj_func]
    cluster = np.empty([len(obj), len(list(obj.values())[0])])
    for p in obj:
        if obj_func == 'kappa':
            cluster[list(obj).index(p), :] = np.asarray([list(v.values())[0] for v in list(obj[p].values())])
        else:
            cluster[list(obj).index(p), :] = np.asarray(list(obj[p].values()))
    return cluster


