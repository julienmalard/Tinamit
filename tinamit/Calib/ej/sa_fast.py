from tinamit.Calib.ej.sa import gen_geog, gen_mod, devolver
from tinamit.Análisis.Sens.corridas import *
from tinamit.Calib.ej.info_paráms import mapa_paráms, líms_paráms
from tinamit.Calib.ej.soil_class import p_soil_class

from tinamit.Calib.ej.sens_análisis import analy_behav_by_dims, map_rank
from tinamit.Conectado import Conectado
from tinamit.Ejemplos.en.Ejemplo_SAHYSMOD.SAHYSMOD import Envoltura
from tinamit.Análisis.Sens.anlzr import anlzr_sens, analy_by_file, carg_simul_dt, anlzr_simul
from tinamit.Geog import Geografía
import multiprocessing as mp
import time


def _anlzr_simul(i, método, líms_paráms, mstr, mapa_paráms, ficticia, var_egr, f_simul_arch, dim, tipo_egr="promedio",
                 simulation=None, ops_método=None):
    return i, anlzr_simul(método, líms_paráms, mstr, mapa_paráms, ficticia, var_egr, f_simul_arch, dim, tipo_egr,
                          simulation, ops_método)


def _analy_by_file(i, método, líms_paráms, mapa_paráms, mstr_arch, simul_arch, var_egr=None,
                   ops_método=None, tipo_egr=None, ficticia=True, f_simul_arch=None, dim=None):
    return i, analy_by_file(método, líms_paráms, mapa_paráms, mstr_arch, simul_arch, var_egr,
                            ops_método, tipo_egr, ficticia, f_simul_arch, dim)


if __name__ == "__main__":
    import os
    import numpy as np

    '''
    Simul
    '''
    # from tinamit.Calib.ej.muestrear import mstr_fast

    # guardar = os.path.join("D:\Thesis\pythonProject\localuse\Dt\Fast\\anlzr\\anlzr_new_calib")

    # direc = os.path.join("D:\Thesis\pythonProject\localuse\Dt\Fast\simular")
    # guardar = os.path.join("D:\Thesis\pythonProject\localuse\Dt\Fast\\anlzr\\new_calib")

    # simul_sens(
    #     gen_mod(), mstr_paráms=mstr_fast, mapa_paráms=mapa_paráms, var_egr=devolver, t_final=20, guardar=direc,
    #     índices_mstrs=None, paralelo=True
    # )

    # simul_sens_por_grupo(gen_mod(), mstr_paráms=mstr_fast, mapa_paráms=mapa_paráms, var_egr=devolver, t_final=20,
    #                      tmñ_grupos=360, í_grupos=[0], guardar=direc, paralelo=True)

    # 360 groups size of each group = 500
    '''
    analysis
    '''
    # # After finish the f_simul simulation SAlib for superposition (the best behavior for each poly)
    # from tinamit.Calib.ej.sens_análisis import analy_behav_by_dims

    # fited_behav = "D:\Gaby\Tinamit\Dt\Fast\\f_simul_post\\"
    # analy_behav_by_dims('fast', 120000, 215, f_simul_arch, gaurdar=gaurdar, dim_arch=fited_behav)

    direc = 'D:\Gaby\Tinamit\Dt\Fast\simular\\12000_fa\\'
    f_simul_arch = 'D:\Gaby\Tinamit\Dt\Fast\\f_simul\\'
    gaurdar = 'D:\Gaby\Tinamit\Dt\Fast\\anlzr\egr_mean\\'
    no_ini = "D:\Gaby\Tinamit\Dt\Fast\guardar_po_fsim\\fited_behav.npy"

    # pool = mp.Pool(processes=11)
    # results = []
    #
    # for dim in range(11, 215):
    # Behavior process
    # results.append(pool.apply_async(_anlzr_simul, args=(
    #     dim, 'fast', líms_paráms, "D:\Gaby\Tinamit\Dt\Fast\sampled_dt\\muestra_fast_23params.json",
    #     mapa_paráms, True, 'mds_Watertable depth Tinamit',
    #     {'arch': f_simul_arch + 'f_simul',
    #      'num_sample': 120000,
    #      'counted_behaviors': gaurdar + 'counted_all_behaviors.npy'}, dim, "superposition", None, None,)))

    # Paso, Mean
    #     results.append(pool.apply_async(_analy_by_file, args=(
    #         dim, 'fast', líms_paráms, mapa_paráms, "D:\Gaby\Tinamit\Dt\Fast\sampled_dt\\muestra_fast_23params.json",
    #         {'arch_simular': direc, 'num_samples': 120000}, 'mds_Watertable depth Tinamit', None, 'promedio', True, #promedio, paso_tiempo
    #         None, dim)))
    #
    # for result in results:
    #     re = result.get()
    #     np.save(gaurdar + f'egr-{re[0]}', re[1])
    '''
    map
    '''
    from tinamit.Calib.ej.soil_class import p_soil_class
    from tinamit.Calib.ej.sens_análisis import map_sens, verif_sens, gen_alpha, gen_counted_behavior
    from collections import Counter

    paso_data = np.load("D:\Gaby\Tinamit\Dt\Fast\\anlzr\egr_paso\\egr-0.npy").tolist()
    paso_arch = "D:\Gaby\Tinamit\Dt\Fast\\anlzr\egr_paso\\"
    pasos = \
        verif_sens('fast', list(paso_data.keys())[0], mapa_paráms, p_soil_class, egr_arch=paso_arch, si='Si', dim=215)[
            'fast'][list(paso_data.keys())[0]]['mds_Watertable depth Tinamit']  # 9prms * 215polys

    mean_data = np.load("D:\Gaby\Tinamit\Dt\Fast\\anlzr\egr_mean\\egr-0.npy").tolist()
    mean_arch = "D:\Gaby\Tinamit\Dt\Fast\\anlzr\egr_mean\\"
    means = \
        verif_sens('fast', list(mean_data.keys())[0], mapa_paráms, p_soil_class, egr_arch=mean_arch, si='Si', dim=215)[
            'fast'][list(mean_data.keys())[0]]['mds_Watertable depth Tinamit']

    behav_data = np.load("D:\Gaby\Tinamit\Dt\Fast\\anlzr\egr_behav\\egr-0.npy").tolist()
    behav_arch = "D:\Gaby\Tinamit\Dt\Fast\\anlzr\egr_behav\\"
    behaviors = \
        verif_sens('fast', list(behav_data.keys())[0], mapa_paráms, p_soil_class, egr_arch=behav_arch, si='Si',
                   dim=215)['fast'][list(behav_data.keys())[0]]['mds_Watertable depth Tinamit']

    # paso
    # for prm, paso in pasos.items():
    #     map_sens(gen_geog(), 'Fast', list(paso_data.keys())[0], prm,
    #              paso, 0.01, ids=[str(i) for i in range(1, 216)],
    #              path="D:\Gaby\Tinamit\Dt\Fast\map\paso\\test\\")

    # mean
    # for prmm, m_aray in means.items():
    #     map_sens(gen_geog(), 'Fast', list(mean_data.keys())[0], prmm,
    #              m_aray, 0.01, ids=[str(i) for i in range(1, 216)],
    #              path="D:\Gaby\Tinamit\Dt\Fast\map\mean\\")

    # for spp
    # for patt, b_g in behaviors.items():
    #     alpha = gen_alpha(no_ini, patt)  # ini/ no_ini
    #     if Counter(alpha)[0] == 215:
    #         alpha = np.zeros([215])
    #     bpp_prm = b_g['bp_params']
    #     gof_prm = b_g['gof']
    #     for prm, bpprm in bpp_prm.items():
    #         # if prm == 'Ficticia':
    #         #     alpha = np.zeros([215])
    #         map_sens(gen_geog(), 'Fast', list(behav_data.keys())[0], prm,
    #                  bpprm, 0.01, behav=patt, ids=[str(i) for i in range(1, 216)], alpha=alpha,
    #                  path="D:\Gaby\Tinamit\Dt\Fast\map\\spp\\")

    # for Linear
    # patt = 'linear'
    # b_g = behaviors[patt]
    # alpha = 1  # ini/ no_ini
    # bpp_prm = b_g['bp_params']
    # gof_prm = b_g['gof']
    # for prm, bpprm in gof_prm.items():
    #     # if prm == 'Ficticia':
    #     #     alpha = np.zeros([215])
    #     map_sens(gen_geog(), 'Fast', list(behav_data.keys())[0], prm,
    #              bpprm, 0.01, behav=patt, ids=[str(i) for i in range(1, 216)], alpha=alpha,
    #              path="D:\Gaby\Tinamit\Dt\Fast\map\\aic\\linear\\")

    #test
    # patt = 'spp_oscil_aten_log'
    # b_g = behaviors[patt]
    # alpha = gen_alpha(no_ini, patt)
    # bpp_prm = b_g['bp_params']
    # gof_prm = b_g['gof']
    # for prm, bpprm in bpp_prm.items():
    #     if prm != 'POH Kharif Tinamit':
    #         continue
    #     map_sens(gen_geog(), 'Fast', list(behav_data.keys())[0], prm,
    #              bpprm, 0.01, behav=patt, ids=[str(i) for i in range(1, 216)], alpha=alpha,
    #              path="D:\Gaby\Tinamit\Dt\Fast\map\\spp\\")

    # final plot
    archivo = "D:\Gaby\Tinamit\Dt\Fast\map\\final_plot\\"

    col_labels = ['0', '5', '10', '15', '20', 'Mean']

    col_labels.extend([f"{behav}_{bpp}" for behav in behaviors for bpp in behaviors[behav]['bp_params']['Kaq']])
    col_labels.extend([f"{behav}_gof" for behav in behaviors])
    sig_l = [f'n_{l + 1}' for l in range(6)]
    sig_l.extend([f'b_{l + 1}' for l in range(len(col_labels))])

    db_l = [f's_{l}' for l in range(20)]

    col = col_labels.copy()
    col[:6] = sig_l[:6]
    sl = 0
    dl = 0
    for j in col[6:]:
        if j[:3] == 'spp':
            col[col.index(j)] = db_l[dl]
            dl += 1
        elif col.index(j) < len(col):
            col[col.index(j)] = sig_l[sl + 6]
            sl += 1

    row_labels=['Ptq', 'Ptr', 'Kaq', 'Peq', 'Pex', 'POH, Summer', 'POH, Winter', 'CTW', 'Dummy']
    for i in range(215):
        data = np.empty([len(list(pasos)), len(col_labels)])
        # paso
        ps = [0, 1, 2, 3, 4]
        for prmp, d_paso in pasos.items():
            for p in ps:
                data[list(pasos).index(prmp), ps.index(p)] = d_paso[f'paso_{p}'][i]

    #     mean
        for prmm, m_aray in means.items():
            data[list(pasos).index(prmm), col_labels.index('Mean')] = m_aray[i]

    #     behavior
        for patt, d_bg in behaviors.items():
            alpha = gen_alpha(no_ini, patt)
            for pbpp, bpp in d_bg['bp_params'].items():
                if Counter(alpha)[0] == 215: #or pbpp == 'Ficticia':  ###
                    alpha = np.zeros([215])
                for bppm, va in bpp.items():
                    if alpha[i] == 0 and patt != 'linear':
                        data[list(pasos).index(pbpp), col_labels.index(f'{patt}_{bppm}')] = 0
                    else:
                        data[list(pasos).index(pbpp), col_labels.index(f'{patt}_{bppm}')] = va[i]
            for paic, aic in d_bg['gof'].items():
                if alpha[i] == 0 and patt != 'linear':
                    data[list(pasos).index(paic), col_labels.index(f'{patt}_gof')] = 0
                else:
                    data[list(pasos).index(paic), col_labels.index(f'{patt}_gof')] = aic['aic'][i]
        if len(np.where(np.isnan(data))[1]) != 0:
            data[np.where(np.isnan(data))] = 0
        map_rank(row_labels=row_labels, col_labels=col, data=np.round(data, 2),
                 title='Fast Sensitivity Ranking Results', y_label='Parameters',
                 archivo=archivo + f'poly{i + 1}', fst_cut=0.01, snd_cut=10, maxi=np.round(data, 2).max(),
                 cbarlabel="Fast Sensitivity Index", cmap="magma_r")

        print(f'finish the {i}-th poly, yeah!')

    #  for the 215 total plt
    # data = np.empty([len(row_labels), len(col_labels)])
    # # paso
    # ps = [0, 1, 2, 3, 4]
    # for prmp, d_paso in pasos.items():
    #     for p in ps:
    #         data[list(pasos).index(prmp), ps.index(p)] = max(d_paso[f'paso_{p}'])
    #
    # # mean
    # for prmm, m_aray in means.items():
    #     data[list(pasos).index(prmm), col_labels.index('Mean')] = max(m_aray)
    #
    # # behavior
    # for patt, d_bg in behaviors.items():
    #     for pbpp, bpp in d_bg['bp_params'].items():
    #         for bppm, va in bpp.items():
    #             data[list(pasos).index(pbpp), col_labels.index(f'{patt}_{bppm}')] = max(va)
    #     for paic, aic in d_bg['gof'].items():
    #         data[list(pasos).index(paic), col_labels.index(f'{patt}_gof')] = max(aic['aic'])
    #
    # map_rank(row_labels=row_labels, col_labels=col, data=np.round(data, 2),
    #          title='Fast Sensitivity Ranking Results', y_label='Parameters',
    #          archivo=archivo + f'all_poly', fst_cut=0.01, snd_cut=10, maxi=np.round(data, 2).max(),
    #          cbarlabel="Fast Sensitivity Index", cmap="magma_r")
