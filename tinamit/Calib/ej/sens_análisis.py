import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from collections import Counter

from matplotlib.colors import LinearSegmentedColormap
import matplotlib.colors as colors
from mpl_toolkits.axes_grid1 import make_axes_locatable

from tinamit.Análisis.Sens.behavior import find_best_behavior
from tinamit.Geog.Geog import _gen_clrbar_dic, _gen_d_mapacolores
from tinamit.Calib.ej.info_paráms import mapa_paráms
from tinamit.Calib.ej.soil_class import p_soil_class
from tinamit.Calib.ej.info_analr import *
from tinamit.Geog.Geog import Geografía, _hex_a_rva
from tinamit.Conectado import Conectado
from tinamit.Ejemplos.en.Ejemplo_SAHYSMOD.SAHYSMOD import Envoltura

import multiprocessing as mp


def gen_mod():
    # Create a coupled model instance
    modelo = Conectado()

    # Establish SDM and Biofisical model paths. The Biofisical model path must point to the Python wrapper for the model
    modelo.estab_mds('../../../tinamit/Ejemplos/en/Ejemplo_SAHYSMOD/Vensim/Tinamit_Rechna.vpm')

    modelo.estab_bf(Envoltura)
    modelo.estab_conv_tiempo(mod_base='mds', conv=6)

    # Couple models(Change variable names as needed)
    modelo.conectar(var_mds='Soil salinity Tinamit CropA', mds_fuente=False, var_bf="CrA - Root zone salinity crop A")
    modelo.conectar(var_mds='Soil salinity Tinamit CropB', mds_fuente=False, var_bf="CrB - Root zone salinity crop B")
    modelo.conectar(var_mds='Area fraction Tinamit CropA', mds_fuente=False,
                    var_bf="Area A - Seasonal fraction area crop A")
    modelo.conectar(var_mds='Area fraction Tinamit CropB', mds_fuente=False,
                    var_bf="Area B - Seasonal fraction area crop B")
    modelo.conectar(var_mds='Watertable depth Tinamit', mds_fuente=False, var_bf="Dw - Groundwater depth")
    modelo.conectar(var_mds='ECdw Tinamit', mds_fuente=False, var_bf='Cqf - Aquifer salinity')  ###
    modelo.conectar(var_mds='Final Rainfall', mds_fuente=True, var_bf='Pp - Rainfall')  # True-coming from Vensim
    modelo.conectar(var_mds='Lc', mds_fuente=True, var_bf='Lc - Canal percolation')
    modelo.conectar(var_mds='Ia CropA', mds_fuente=True, var_bf='IaA - Crop A field irrigation')
    modelo.conectar(var_mds='Ia CropB', mds_fuente=True, var_bf='IaB - Crop B field irrigation')
    modelo.conectar(var_mds='Gw', mds_fuente=True, var_bf='Gw - Groundwater extraction')
    modelo.conectar(var_mds='EpA', mds_fuente=True, var_bf='EpA - Potential ET crop A')
    modelo.conectar(var_mds='EpB', mds_fuente=True, var_bf='EpB - Potential ET crop B')
    modelo.conectar(var_mds='Irrigation efficiency', mds_fuente=True, var_bf='FsA - Water storage efficiency crop A')
    modelo.conectar(var_mds='Fw', mds_fuente=True, var_bf='Fw - Fraction well water to irrigation')
    # 'Policy RH' = 1, Fw = 1, Policy Irrigation improvement = 1, Policy Canal lining=1, Capacity per tubewell =(100.8, 201.6),
    return modelo


def gen_geog():
    Rechna_Doab = Geografía(nombre='Rechna Doab')

    base_dir = os.path.join("D:\Thesis\pythonProject\Tinamit\\tinamit\Ejemplos\en\Ejemplo_SAHYSMOD", 'Shape_files')
    Rechna_Doab.agregar_frm_regiones(os.path.join(base_dir, 'Internal_Polygon.shp'), col_id="Polygon_ID")

    Rechna_Doab.agregar_forma(os.path.join(base_dir, 'External_Polygon.shp'), color='#edf4da')
    Rechna_Doab.agregar_forma(os.path.join(base_dir, 'RIVR.shp'), tipo='agua')
    # Rechna_Doab.agregar_forma(os.path.join(base_dir, 'Forst_polygon.shp'), tipo='bosque')
    Rechna_Doab.agregar_forma(os.path.join(base_dir, 'CNL_Arc.shp'), tipo='agua', color='#1ba4c6', llenar=False)
    # Rechna_Doab.agregar_forma(os.path.join(base_dir, 'buildup_Polygon.shp'), tipo='ciudad')
    # Rechna_Doab.agregar_forma(os.path.join(base_dir, 'road.shp'), tipo='calle')

    return Rechna_Doab


devolver = ['Watertable depth Tinamit', 'Soil salinity Tinamit CropA']


def _integrate_egr(egr_arch, dim, si, mapa_paráms, tipo_egr):
    def _gen_egr_tmp(tipo_egr, egr, si, egr_tmp=None, dim=None):
        if egr_tmp is None:
            for egr_var, patt in egr[tipo_egr].items():
                if tipo_egr == 'paso_tiempo':
                    for para, val in patt[si].items():
                        for paso in val:
                            if para in mapa_paráms:
                                val[paso] = np.empty([4, dim])
                            else:
                                val[paso] = np.empty([dim])
                elif tipo_egr == "promedio":
                    for para in patt[si]:
                        if para in mapa_paráms:
                            patt[si][para] = np.empty([4, dim])
                        else:
                            patt[si][para] = np.empty([dim])
                else:
                    for p_name, bg_name in patt.items():
                        for b_g, d_si in bg_name.items():
                            for para_name, d_bp_gof in d_si[si].items():
                                for bp_gof_name in d_bp_gof:
                                    if para_name in mapa_paráms:
                                        d_bp_gof[bp_gof_name] = np.empty([4, dim])
                                    else:
                                        d_bp_gof[bp_gof_name] = np.empty([dim])
        else:
            for egr_var, patt in egr[tipo_egr].items():
                if tipo_egr == 'paso_tiempo':
                    for para, val in patt[si].items():
                        for paso in val:
                            if para in mapa_paráms:
                                egr_tmp[tipo_egr][egr_var][si][para][paso][:, dim] = val[paso][:, 0]
                            else:
                                egr_tmp[tipo_egr][egr_var][si][para][paso][dim] = val[paso]

                elif tipo_egr == "promedio":
                    for para in patt[si]:
                        if para in mapa_paráms:
                            egr_tmp[tipo_egr][egr_var][si][para][:, dim] = patt[si][para][:, 0]
                        else:
                            egr_tmp[tipo_egr][egr_var][si][para][dim] = patt[si][para]

                else:
                    for p_name, bg_name in patt.items():
                        for b_g, d_si in bg_name.items():
                            for para_name, d_bp_gof in d_si[si].items():
                                for bp_gof_name in d_bp_gof:
                                    if para_name in mapa_paráms:
                                        egr_tmp[tipo_egr][egr_var][p_name][b_g][si][para_name][bp_gof_name][:, dim] = \
                                            d_bp_gof[bp_gof_name][:, 0]
                                    else:
                                        egr_tmp[tipo_egr][egr_var][p_name][b_g][si][para_name][bp_gof_name][dim] = \
                                            d_bp_gof[
                                                bp_gof_name]

    egr_tmp = {}
    egr0 = np.load(egr_arch + f'egr-{0}.npy').tolist()
    _gen_egr_tmp(tipo_egr=tipo_egr, egr=egr0, si=si, dim=dim)
    egr_tmp.update(egr0)

    for i in range(dim):
        _gen_egr_tmp(tipo_egr=tipo_egr, egr=np.load(egr_arch + f'egr-{i}.npy').tolist(), si='Si', egr_tmp=egr_tmp,
                     dim=i)

    return egr_tmp


def verif_sens(método, tipo_egr, mapa_paráms, p_soil_class, si, dim=None, egr=None, egr_arch=None):
    if método == 'fast':
        egr = _integrate_egr(egr_arch, dim, si, mapa_paráms, tipo_egr)

    if tipo_egr == "forma" or tipo_egr == 'superposition':
        final_sens = {método: {tipo_egr: {p_name: {b_name: {bp_gof: {para: {f_name: np.asarray([f_val[id][i]
                                                                                                for i, id in enumerate(
                p_soil_class)])
                                                                            for f_name, f_val in
                                                                            val.items()} if para in mapa_paráms else val
                                                                     for para, val in bp_gof_val[si].items()}
                                                            for bp_gof, bp_gof_val in b_val.items()}
                                                   for b_name, b_val in p_val.items()}
                                          for p_name, p_val in egr[tipo_egr].items()}}}


    elif tipo_egr == "paso_tiempo":
        final_sens = {método: {tipo_egr: {p_name: {para: {paso: np.asarray([paso_val[id][i]
                                                                            for i, id in enumerate(p_soil_class)])
                                                          for paso, paso_val in
                                                          val.items()} if para in mapa_paráms else val
                                                   for para, val in p_val[si].items()}
                                          for p_name, p_val in egr[tipo_egr].items()}}}
    elif tipo_egr == "promedio":
        final_sens = {método: {tipo_egr: {p_name: {para: np.asarray([val[id][i]
                                                                     for i, id in enumerate(
                p_soil_class)]) if para in mapa_paráms else val
                                                   for para, val in p_val[si].items()}
                                          for p_name, p_val in egr[tipo_egr].items()}}}
    else:
        raise Exception('Not defined type!')

    return final_sens


def _single_poly(samples, i, f_simul_arch, gaurdar):
    fited_behav = {i: {j: {} for j in range(samples)}}
    for j in range(samples):
        print(f'this is {j}-th sample')
        behav = np.load(f_simul_arch + f"f_simul_{j}.npy").tolist()
        fited_behav[i][j] = find_best_behavior(behav, trans_shape=i)
    if gaurdar is not None:
        np.save(gaurdar + f'fit_beh_poly-{i}', fited_behav)


def _compute_single(i, method, dim_arch, samples, f_simul_arch):
    count_fited_behav_by_poly = []
    if method == 'morris':
        polynal_fited_behav = np.load(dim_arch).tolist()[i]
    elif method == 'fast':
        polynal_fited_behav = np.load(dim_arch + f'fit_beh_poly-{i}.npy').tolist()[i]

    for j in range(samples):
        count_fited_behav_by_poly.extend([key for key, val in polynal_fited_behav[j]])

    count_fited_behav_by_poly = [k for k, v in Counter(count_fited_behav_by_poly).items() if
                                 v / len(count_fited_behav_by_poly) > 0.1]
    # fited_behav.update({i: count_fited_behav_by_poly})

    aic_poly = {k: [] for k in count_fited_behav_by_poly}
    for j in range(samples):
        behav = np.load(f_simul_arch + f"f_simul_{j}.npy").tolist()
        for k in count_fited_behav_by_poly:
            aic_poly[k].append(behav[k]['gof']['aic'][0, i])
        print(f'Processing sample-{j} for poly-{i}')
    # aic_behav.update({i: {k: np.average(v) for k, v in aic_poly.items()}})
    return i, count_fited_behav_by_poly, {k: np.average(v) for k, v in aic_poly.items()}


def analy_behav_by_dims(method, samples, dims, f_simul_arch, dim_arch=None, gaurdar=None):
    if dim_arch is None:
        if method == 'morris':
            fited_behav = {i: {j: {} for j in range(samples)} for i in range(dims)}
            for j in range(samples):
                print(f'this is {j}-th sample')
                behav = np.load(f_simul_arch + f"f_simul_{j}.npy").tolist()
                for i in range(dims):
                    fited_behav[i][j] = find_best_behavior(behav, trans_shape=i)
                    print(f'processing {i} poly')
            if gaurdar is not None:
                np.save(gaurdar + 'fited_behav', fited_behav)

        elif method == 'fast':
            pool = mp.Pool(processes=10)

            results = []
            for i in range(dims):
                # if i not in [34, 144, 176, 186]:
                #     continue
                print(f'Processing {i} poly')
                results.append(pool.apply_async(_single_poly, args=(samples, i, f_simul_arch, gaurdar,)))

            [result.wait() for result in results]
            # output = [p.get() for p in results]
            print("finished")


    else:
        fited_behav = {}
        aic_behav = {}
        results = []
        pool = mp.Pool(processes=10)
        for i in range(dims):
            results.append(pool.apply_async(_compute_single, args=(i, method, dim_arch, samples, f_simul_arch,)))

        for result in results:
            re = result.get()
            fited_behav.update({re[0]: re[1]})
            aic_behav.update({re[0]: re[2]})

        if gaurdar is not None:
            np.save(gaurdar + 'fited_behav', fited_behav)
            np.save(gaurdar + 'aic_behav', aic_behav)


def gen_counted_behavior(fited_behav_arch, gaurdar=None):
    fited_behaviors = np.load(fited_behav_arch).tolist()
    counted_all_behaviors = []
    for i in range(len(fited_behaviors)):
        counted_all_behaviors.extend(fited_behaviors[i])
    counted_all_behaviors = set(counted_all_behaviors)
    if gaurdar is not None:
        np.save(gaurdar + 'counted_all_behaviors', counted_all_behaviors)
    else:
        return counted_all_behaviors


def gen_alpha(fited_behav_arch, patt):
    fited_behav = np.load(fited_behav_arch).tolist()
    d_alpha = {i: [] for i in fited_behav}
    for poly, behavs in fited_behav.items():
        if patt in behavs:
            d_alpha[poly] = 1.0
        else:
            d_alpha[poly] = 0.0
    return np.asarray([a for p, a in d_alpha.items()])


def _read_dt_4_map(method):
    method.capitalize()
    if method == 'Morris':
        pasos = \
            verif_sens('morris', 'paso_tiempo', mapa_paráms, p_soil_class, egr=paso_data_mor, si='mu_star')['morris'][
                'paso_tiempo']['mds_Watertable depth Tinamit']

        means = \
            verif_sens('morris', list(mean_data_mor.keys())[0], mapa_paráms, p_soil_class, egr=mean_data_mor,
                       si='mu_star')[
                'morris'][
                list(mean_data_mor.keys())[0]]['mds_Watertable depth Tinamit']

        behaviors = verif_sens('morris', list(behav_data_mor.keys())[0], mapa_paráms, p_soil_class, egr=behav_data_mor,
                               si='mu_star')['morris'][list(behav_data_mor.keys())[0]]['mds_Watertable depth Tinamit']

        no_ini = no_ini_mor

        ps = [0, 5, 10, 15, 20]

        return {'pasos': pasos, 'means': means, 'behaviors': behaviors, 'no_ini': no_ini, 'ps': ps}

    else:
        pasos = \
            verif_sens('fast', list(paso_data_fast.keys())[0], mapa_paráms, p_soil_class, egr_arch=paso_arch_fast,
                       si='Si',
                       dim=215)[
                'fast'][list(paso_data_fast.keys())[0]]['mds_Watertable depth Tinamit']  # 9prms * 215polys

        means = \
            verif_sens('fast', list(mean_data_fast.keys())[0], mapa_paráms, p_soil_class, egr_arch=mean_arch_fast,
                       si='Si',
                       dim=215)[
                'fast'][list(mean_data_fast.keys())[0]]['mds_Watertable depth Tinamit']

        behaviors = \
            verif_sens('fast', list(behav_data_fast.keys())[0], mapa_paráms, p_soil_class, egr_arch=behav_arch_fast,
                       si='Si',
                       dim=215)['fast'][list(behav_data_fast.keys())[0]]['mds_Watertable depth Tinamit']

        no_ini = no_ini_fast
        ps = [0, 1, 2, 3, 4]

        return {'pasos': pasos, 'means': means, 'behaviors': behaviors, 'no_ini': no_ini, 'ps': ps}


def gen_row_col(behaviors):
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
    row_labels = ['Ptq', 'Ptr', 'Kaq', 'Peq', 'Pex', 'POH, Summer', 'POH, Winter', 'CTW', 'Dummy']

    return row_labels, col, col_labels


def gen_geog_map(gaurd_arch, measure='paso_tiempo', patt=None, method='Morris', param=None, fst_cut=0.1, snd_cut=8):
    read_dt = _read_dt_4_map(method)

    if measure == 'paso_tiempo':
        for prm, paso in read_dt['pasos'].items():
            map_sens(gen_geog(), method, 'paso_tiempo', prm,
                     paso, fst_cut=fst_cut, snd_cut=snd_cut, ids=[str(i) for i in range(1, 216)],
                     path=gaurd_arch)

    elif measure == 'promedio':
        for prmm, m_aray in read_dt['means'].items():
            map_sens(gen_geog(), method, 'promedio', prmm,
                     m_aray, fst_cut=fst_cut, snd_cut=snd_cut, ids=[str(i) for i in range(1, 216)],
                     path=gaurd_arch)

    elif measure == 'behavior_gof':
        for patt, b_g in read_dt['behaviors'].items():
            alpha = gen_alpha(read_dt['no_ini'], patt)
            if Counter(alpha)[0] == 215:
                alpha = np.zeros([215])
            gof_prm = b_g['gof']
            for prm, bpprm in gof_prm.items():
                map_sens(gen_geog(), method, 'superposition', prm,
                         bpprm, fst_cut=fst_cut, snd_cut=snd_cut, behav=patt, ids=[str(i) for i in range(1, 216)],
                         alpha=alpha, path=gaurd_arch)

    elif measure == 'behavior_param':
        for patt, b_g in read_dt['behaviors'].items():
            alpha = gen_alpha(read_dt['no_ini'], patt)
            if Counter(alpha)[0] == 215:
                alpha = np.zeros([215])
            bpp_prm = b_g['bp_params']
            for prm, bpprm in bpp_prm.items():
                map_sens(gen_geog(), method, 'superposition', prm,
                         bpprm, fst_cut=fst_cut, snd_cut=snd_cut, behav=patt, ids=[str(i) for i in range(1, 216)],
                         alpha=alpha, path=gaurd_arch)

    elif measure == 'test':
        alpha = gen_alpha(read_dt['no_ini'], patt)
        b_g = read_dt['behaviors'][patt]
        bpp_prm = b_g['bp_params']
        gof_prm = b_g['gof']
        for prm, bpprm in bpp_prm.items():
            if prm != param:
                continue
            map_sens(gen_geog(), method, 'superposition', prm,
                     bpprm, fst_cut=fst_cut, snd_cut=snd_cut, behav=patt, ids=[str(i) for i in range(1, 216)],
                     alpha=alpha, path=gaurd_arch)


def gen_rank_map(rank_arch, method, fst_cut, snd_cut, rank_method):
    read_dt = _read_dt_4_map(method)
    r_c = gen_row_col(read_dt['behaviors'])

    data = np.empty([len(r_c[0]), len(r_c[1])])

    if rank_method == 'polygons':
        for i in range(215):
            # paso
            for prmp, d_paso in read_dt['pasos'].items():
                for p in read_dt['ps']:
                    data[list(read_dt['pasos']).index(prmp), read_dt['ps'].index(p)] = d_paso[f'paso_{p}'][i]

            # mean
            for prmm, m_aray in read_dt['means'].items():
                data[list(read_dt['pasos']).index(prmm), gen_row_col(read_dt['behaviors'])[1].index('Mean')] = m_aray[i]

            # behavior
            for patt, d_bg in read_dt['behaviors'].items():
                alpha = gen_alpha(read_dt['no_ini'], patt)
                for pbpp, bpp in d_bg['bp_params'].items():
                    if Counter(alpha)[0] == 215 or pbpp == 'Ficticia':
                        alpha = np.zeros([215])
                    for bppm, va in bpp.items():
                        if alpha[i] == 0 and patt != 'linear':
                            data[list(read_dt['pasos']).index(pbpp), r_c[1].index(f'{patt}_{bppm}')] = 0
                        else:
                            data[list(read_dt['pasos']).index(pbpp), r_c[1].index(f'{patt}_{bppm}')] = va[i]
                for paic, aic in d_bg['gof'].items():
                    if alpha[i] == 0 and patt != 'linear':
                        data[list(read_dt['pasos']).index(paic), r_c[1].index(f'{patt}_gof')] = 0
                    else:
                        data[list(read_dt['pasos']).index(paic), r_c[1].index(f'{patt}_gof')] = aic['aic'][i]

            map_rank(row_labels=r_c[0], col_labels=r_c[2], data=np.round(data, 2),
                     title=f'{method} Sensitivity Ranking Results', y_label='Parameters',
                     archivo=rank_arch + f'poly{i + 1}', fst_cut=fst_cut, snd_cut=snd_cut, maxi=np.round(data, 2).max(),
                     cbarlabel=f"{method} Sensitivity Index", cmap="magma_r")
            print(f'finish the {i}-th poly, yeah!')

    elif rank_method == 'count_poly':
        param_lst = list(read_dt['pasos'])
        for p in read_dt['ps']:
            n_dt = {prmp: len(d_paso[f'paso_{p}'][np.where(d_paso[f'paso_{p}'] > fst_cut)[0]]) / 215 for prmp, d_paso in
                    read_dt['pasos'].items()}
            for prmp, v in n_dt.items():
                data[list(n_dt).index(prmp), read_dt['ps'].index(p)] = v

        n_dt2 = {prmm: len(m_aray[np.where(m_aray > fst_cut)[0]]) / 215 for prmm, m_aray in read_dt['means'].items()}
        for prmm, m_aray in n_dt2.items():
            data[list(n_dt2).index(prmm), r_c[2].index('Mean')] = m_aray

        col_ind = []
        for patt, d_bg in read_dt['behaviors'].items():
            for pbpp, bpp in d_bg['bp_params'].items():
                for bppm, va in bpp.items():
                    col_ind.append(r_c[2].index(f'{patt}_{bppm}'))
                    data[param_lst.index(pbpp), r_c[2].index(f'{patt}_{bppm}')] = len(
                        va[np.where(va > fst_cut)[0]]) / 215
            for paic, aic in d_bg['gof'].items():
                col_ind.append(r_c[2].index(f'{patt}_gof'))
                data[param_lst.index(paic), r_c[2].index(f'{patt}_gof')] = len(
                    aic['aic'][np.where(aic['aic'] > fst_cut)[0]]) / 215

        if len(np.where(np.isnan(data))[1]) != 0:
            data[np.where(np.isnan(data))] = 0
        cat_clr_bar = data.max()

        map_rank(row_labels=r_c[0], col_labels=r_c[1], data=np.round(data, 2),
                 title=f"{method} Sensitivity occurence polygonal map", y_label='Parameters',
                 archivo=rank_arch + f'{rank_method}', fst_cut=0.1, snd_cut=0.8, maxi=data.max(),
                 cbarlabel=f"{method} Sensitivity Rank", cmap="magma_r", cat_clr_bar=cat_clr_bar, bin=5)

    if rank_method == 'num_poly_rank':
        param_lst = list(read_dt['pasos'])
        for p in read_dt['ps']:
            dt = {prmp: max(d_paso[f'paso_{p}']) for prmp, d_paso in read_dt['pasos'].items()}
            r = {key: rank for rank, key in enumerate(sorted(set(dt.values()), reverse=True), 1)}
            n_dt = {k: r[v] if v > fst_cut else 0 for k, v in dt.items()}
            for prmp, v in n_dt.items():
                data[list(n_dt).index(prmp), read_dt['ps'].index(p)] = v

        dt2 = {prmm: max(m_aray) for prmm, m_aray in read_dt['means'].items()}
        r2 = {key: rank for rank, key in enumerate(sorted(set(dt2.values()), reverse=True), 1)}
        n_dt2 = {k: r2[v] if v > fst_cut else 0 for k, v in dt2.items()}
        for prmm, m_aray in n_dt2.items():
            data[list(n_dt2).index(prmm), r_c[2].index('Mean')] = m_aray
        col_ind = []
        for patt, d_bg in read_dt['behaviors'].items():
            for pbpp, bpp in d_bg['bp_params'].items():
                for bppm, va in bpp.items():
                    col_ind.append(r_c[2].index(f'{patt}_{bppm}'))
                    data[param_lst.index(pbpp), r_c[2].index(f'{patt}_{bppm}')] = max(va)
            for paic, aic in d_bg['gof'].items():
                col_ind.append(r_c[2].index(f'{patt}_gof'))
                data[param_lst.index(paic), r_c[2].index(f'{patt}_gof')] = max(aic['aic'])
        lst = list(set(col_ind))
        for c_i in lst:
            dt = {para: data[:, c_i][i] for i, para in enumerate(param_lst)}
            r = {key: rank for rank, key in enumerate(sorted(set(dt.values()), reverse=True), 1)}
            n_dt = {k: r[v] if v > fst_cut else 0 for k, v in dt.items()}
            for para, rk in n_dt.items():
                data[param_lst.index(para), c_i] = rk

        if len(np.where(np.isnan(data))[1]) != 0:
            data[np.where(np.isnan(data))] = 0
        cat_clr_bar = data.max()

        map_rank(row_labels=r_c[0], col_labels=r_c[1], data=np.round(data, 2),
                 title=f"{method} Sensitivity Ranking Map", y_label='Parameters',
                 archivo=rank_arch + f'{rank_method}', fst_cut=1, snd_cut=data.max(), maxi=data.max(),
                 cbarlabel=f"{method} Sensitivity Rank", cmap="magma_r", cat_clr_bar=cat_clr_bar, bin=9)

    if rank_method == 'total_poly':
        for prmp, d_paso in read_dt['pasos'].items():
            for p in read_dt['ps']:
                data[list(read_dt['pasos']).index(prmp), read_dt['ps'].index(p)] = max(d_paso[f'paso_{p}'])
        # mean
        for prmm, m_aray in read_dt['means'].items():
            data[list(read_dt['pasos']).index(prmm), r_c[2].index('Mean')] = max(m_aray)

        # behavior
        for patt, d_bg in read_dt['behaviors'].items():
            for pbpp, bpp in d_bg['bp_params'].items():
                for bppm, va in bpp.items():
                    data[list(read_dt['pasos']).index(pbpp), r_c[2].index(f'{patt}_{bppm}')] = max(va)
            for paic, aic in d_bg['gof'].items():
                data[list(read_dt['pasos']).index(paic), r_c[2].index(f'{patt}_gof')] = max(aic['aic'])

        if len(np.where(np.isnan(data))[1]) != 0:
            data[np.where(np.isnan(data))] = 0
        map_rank(row_labels=r_c[0], col_labels=r_c[2], data=np.round(data, 2),
                 title=f"{method} Sensitivity Ranking Results", y_label='Parameters',
                 archivo=rank_arch + f'{rank_method}', fst_cut=fst_cut, snd_cut=snd_cut, maxi=np.round(data, 2).max(),
                 cbarlabel=f"{method} Sensitivity Index", cmap="magma_r")


def map_sens(geog, metodo, tipo_egr, para_name, data, fst_cut, path, snd_cut=None, alpha=None, behav=None, paso=None,
             ids=None):
    vars_interés = {tipo_egr: {
        'col': ['#f8fef7', '#e7fde5', '#d6fcd2', '#c5fbc0', '#b4f9ad', '#b4f9ad', '#5ff352',
                '#5395a0', '#4a8590', '#42767f', '#39666e', '#30565d', '#28474c', '#1f373c',
                '#ffe6e6', '#ffcccc', '#ffb3b3', '#ff9999', '#ff8080', '#ff2f2f', '#ff0808'
                ],
        'escala_núm': [min(data), max(data)]}}

    # clr_bar_dic = {'green': ['#e6fff2', '#80ffbf'] , # '#33ff99', '#00cc66', '#006633'],
    #                'blue': ['#80dfff', '#00bfff', '#1ac6ff', '#00ace6', '#007399'],
    #                'red': ['#ff8000', '#ff8c1a', '#ff8000']}

    clr_bar_dic = {'green': ['#e6fff2', '#b3ffd9'],
                   'blue': ['#80ff9f', '#80ff80', '#9fff80', '#bfff80', '#dfff80', '#ffff80', '#ffdf80', '#ff8080'],
                   # '#ff8080']
                   'red': ['#ff0000', '#ff0000']}

    unid = f'{metodo} Sensitivity Index'

    for v, d in vars_interés.items():
        # for j in [0, 5, 15, 20]:
        #     geog.dibujar(archivo=path + f'old-{j}', valores=data[j], título=f'Soil salinity old paso-{j}',
        #                  unidades='Soil salinity level',
        #                  colores=d['col'], ids=ids)  # for azahr

        # paso
        # ll = [0, 5, 10, 15, 20]
        # # ll = [0, 1, 2, 3, 4]
        # for i in ll:
        #     max_val = max(data[f'paso_{i}'])
        #     if max_val > snd_cut:
        #         data[f'paso_{i}'][np.where(data[f'paso_{i}'] > snd_cut)] = snd_cut
        #         max_val = snd_cut
        #     geog.dibujar(archivo=path + f'{i*5}-{para_name}', valores=data[f'paso_{i}'],
        #                  título=f"{metodo}-{para_name[: 5]}-Timestep-{i*5} to WTD",
        #                  unidades=unid, colores=d['col'], ids=ids, midpoint=midpoint, clr_bar_dic=clr_bar_dic,
        #                  escala_num=(0, max_val))

        # mean val
        # max_val = max(data)
        # if max_val > snd_cut:
        #     data[np.where(data > snd_cut)] = snd_cut
        #     max_val = snd_cut
        # geog.dibujar(archivo=path + f'mean-{para_name}', valores=data,
        #              título=f"{metodo[:2]}-{para_name}-to WTD-Mean", midpoint=midpoint, clr_bar_dic=clr_bar_dic,
        #              unidades=unid, colores=d['col'], ids=ids, escala_num=(0, max_val))

        # beahv
        for bpprm in data:  # "D:\Thesis\pythonProject\localuse\Dt\Mor\map\\spp\\aic\\{bpprm}-{behav}-{para_name}" #f"D:\Thesis\pythonProject\localuse\Dt\Mor\map\spp\\bppprm\\bpprm-{behav}-{para_name}"
            # if bpprm != 'amplitude':
            #     continue
            # new_alpha = np.zeros([215])
            # new_alpha[np.where(data[bpprm])[0][np.isin(np.where(data[bpprm]), np.where(alpha > 0))[0]]] = 1
            if np.round(max(data[bpprm]), 4) == 0:
                max_val = 0
            # elif behav == 'linear':
            #     alpha = 1
            #     max_val = max(data[bpprm])
            elif len(np.where(data[bpprm])[0][np.isin(np.where(data[bpprm]), np.where(alpha > 0))[0]]) == 0:
                max_val = 0
            else:
                max_val = max(
                    data[bpprm][[np.where(data[bpprm])[0][np.isin(np.where(data[bpprm]), np.where(alpha > 0))[0]]]])
                # if max_val < max(data[bpprm]):
                #     data[bpprm][np.where(data[bpprm] > max_val)[0]] = max_val
            if max_val > snd_cut:
                data[bpprm][np.where(data[bpprm] > snd_cut)] = snd_cut
                data[np.where(data < fst_cut)] = 0 - snd_cut * 0.1
                max_val = snd_cut

            geog.dibujar(archivo=path + f"{metodo[:2]}-{para_name[: 5]}-{behav}-{bpprm}",  # midpoint=midpoint,
                         valores=data[bpprm],
                         título=f"{metodo[:2].capitalize()}-{para_name[0].capitalize() + para_name[1: 5]}-{behav[0].capitalize() + behav[1:]}-{bpprm}",
                         alpha=alpha, unidades=unid, colores=d['col'], ids=ids, fst_cut=fst_cut + snd_cut * 0.1,
                         snd_cut=snd_cut,
                         clr_bar_dic=clr_bar_dic,
                         escala_num=(0, max_val)
                         )


def map_rank(fst_cut, snd_cut, maxi, row_labels, col_labels, data, title, y_label, archivo, ax=None, cbar_kw={},
             cbarlabel="Sensitivity Index", cat_clr_bar=None, bin=None, **kwargs):
    '''

    Parameters
    ----------
    row_labels:  A list or array of length N with the labels for the rows
    ["cucumber", "tomato", "lettuce", "asparagus", "potato", "wheat", "barley"]
    col_labels: A list or array of length M with the labels for the columns
    ["Farmer Joe", "Upland Bros.", "Smith Gardening", "Agrifun", "Organiculture", "BioGoods Ltd.", "Cornylee Corp."]
    data: A 2D numpy array of shape (N,M)
    np.array([[0.8, 2.4, 2.5, 3.9, 0.0, 4.0, 0.0],
            [2.4, 0.0, 4.0, 1.0, 2.7, 0.0, 0.0],
            [1.1, 2.4, 0.8, 4.3, 1.9, 4.4, 0.0],
            [0.6, 0.0, 0.3, 0.0, 3.1, 0.0, 0.0],
            [0.7, 1.7, 0.6, 2.6, 2.2, 6.2, 0.0],
            [1.3, 1.2, 0.0, 0.0, 0.0, 3.2, 5.1],
            [0.1, 2.0, 0.0, 1.4, 0.0, 1.9, 6.3]])

    Optional arguments:
        ax         : A matplotlib.axes.Axes instance to which the heatmap
                     is plotted. If not provided, use current axes or
                     create a new one.
        cbar_kw    : A dictionary with arguments to
                     :meth:`matplotlib.Figure.colorbar`.
        cbarlabel  : The label for the colorbar
    All other arguments are directly passed on to the imshow call.

    cmap="Wistia", cmap="magma_r" , cmap=plt.get_cmap("PiYG", 7) yellow-black, cmap="PuOr" brown
    vmin=0, vmin=-1, vmax=1
    cbar_kw=dict(ticks=np.arange(-3, 4),

    Returns
    -------

    '''
    if not ax:
        fig, ax = plt.subplots()

    # clr_bar_dic = {'green': ['#e6fff2', '#80ffbf', '#33ff99', '#00cc66', '#006633'],
    #                'blue': ['#80dfff', '#00bfff', '#1ac6ff', '#00ace6', '#007399'],
    #                'red': ['#ff8000', '#ff8c1a', '#ff8000']}

    clr_bar_dic = {'green': ['#e6fff2', '#b3ffd9'],
                   'blue': ['#80ff9f', '#80ff80', '#9fff80', '#bfff80', '#dfff80', '#ffff80', '#ffdf80', '#ff8080'],
                   'red': ['#ff0000', '#ff0000']}

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="1.5%", pad=0.05)

    if cat_clr_bar is not None:
        if bin == 5:
            dic_c = _gen_d_mapacolores(
                ['#e6fff2', '#80ff9f', '#80ff80', '#9fff80', '#bfff80', '#dfff80', '#ffff80', '#ffdf80', '#ff8080'],
                maxi=None)
        elif bin == 9:
            dic_c = _gen_d_mapacolores(
                ['#e6fff2', '#ff8080', '#ffdf80', '#ffff80', '#dfff80', '#bfff80', '#9fff80', '#80ff80', '#80ff9f'],
                maxi=None)

        mapa_color = LinearSegmentedColormap('mapa_color', dic_c, N=bin)
        im = ax.imshow(data, mapa_color)
        if bin == 5:
            cbar = fig.colorbar(im, cax=cax, ticks=[0, 0.2, 0.4, 0.6, 0.8, 1])
            cbar.ax.set_yticklabels(['0', '~20%', '~40%', '~60%', '~80%', '~100%'], fontsize=6)
        elif bin == 9:
            cbar = fig.colorbar(im, cax=cax, ticks=[0, 8, 7, 6, 5, 4, 3, 2, 1])
            cbar.ax.set_yticklabels(['0', '8', '7', '6', '5', '4', '3', '2', '1'], fontsize=6)

    else:
        if data.max() > snd_cut:
            data[np.where(data > snd_cut)] = snd_cut + 0.1
            data[np.where(data < fst_cut)] = 0 - snd_cut * 0.1
            dic_c = _gen_clrbar_dic(fst_cut=fst_cut + snd_cut * 0.1, snd_cut=snd_cut - 0.1,
                                    maxi=snd_cut + 0.1 + snd_cut * 0.1,
                                    first_set=clr_bar_dic['green'],
                                    second_set=clr_bar_dic['blue'], third_set=clr_bar_dic['red'])
            mapa_color = LinearSegmentedColormap('mapa_color', dic_c)
            im = ax.imshow(data, mapa_color)

            cbar = fig.colorbar(im, cax=cax, ticks=[data.min(), fst_cut, snd_cut - 0.1])
            cbar.ax.set_yticklabels(
                ['0', f'Screnning threshold, {fst_cut}', f'+{snd_cut} High sensitivity zone'],
                fontsize=3)

        elif fst_cut < data.max() < snd_cut:
            data[np.where(data < fst_cut)] = 0 - maxi * 0.1
            dic_c = _gen_clrbar_dic(fst_cut=fst_cut + maxi * 0.1, snd_cut=None, maxi=maxi + maxi * 0.1,
                                    first_set=clr_bar_dic['green'], second_set=clr_bar_dic['blue'],
                                    third_set=clr_bar_dic['red'])
            mapa_color = LinearSegmentedColormap('mapa_color', dic_c)
            im = ax.imshow(data, mapa_color)
            cbar = fig.colorbar(im, cax=cax, ticks=[data.min(), fst_cut, data.max()])
            # cbar = ax.figure.colorbar(im, ax=cax, ticks=[0, fst_cut, data.max()], **cbar_kw)
            cbar.ax.set_yticklabels(['0', f'Screnning threshold, {fst_cut}', f'maximum val, {np.round(data.max(), 3)}'],
                                    fontsize=3)

        elif data.max() < fst_cut:
            dic_c = _gen_clrbar_dic(fst_cut=None, snd_cut=None, maxi=maxi, first_set=clr_bar_dic['green'],
                                    second_set=clr_bar_dic['blue'], third_set=clr_bar_dic['red'])
            mapa_color = LinearSegmentedColormap('mapa_color', dic_c)
            im = ax.imshow(data, mapa_color)
            cbar = fig.colorbar(im, cax=cax, ticks=[0, data.max()])
            # cbar = ax.figure.colorbar(im, ax=cax, ticks=[0, data.max()], **cbar_kw)
            cbar.ax.set_yticklabels(['0', f'maximum val, {data.max()}'], fontsize=3)

    cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom", fontsize=5)
    ax.tick_params(width=0.1)
    cbar.ax.tick_params(width=0.1)

    # We want to show all ticks...
    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_yticks(np.arange(data.shape[0]))
    # ... and label them with the respective list entries.
    ax.set_xticklabels(col_labels, fontsize=3)
    ax.set_yticklabels(row_labels, fontsize=4)

    # Let the horizontal axes labeling appear on top.
    ax.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=-30, ha="right",
             rotation_mode="anchor")

    # Turn spines off and create white grid.
    for edge, spine in ax.spines.items():
        spine.set_visible(False)

    ax.set_xticks(np.arange(data.shape[1] + 1) - .5, minor=True)
    ax.set_yticks(np.arange(data.shape[0] + 1) - .5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=0.5)
    ax.tick_params(which="minor", bottom=False, left=False)

    def func(x, pos):
        return "{:.2f}".format(x).replace("-0.80", "0").replace("8.10", "")

    def func2(x):
        return "{:}".format(x).replace("0", "")

    def _annotate_rankmap(fst_cut=fst_cut, snd_cut=snd_cut, im=im, valfmt='{:.2f}',
                          txtclr=["white", "black", ''],
                          **textkw):
        """
        A function to annotate a rankmap.

        Arguments:
            im         : The AxesImage to be labeled.
        Optional arguments:
            data       : Data used to annotate. If None, the image's data is used.
            valfmt     : The format of the annotations inside the heatmap.
                         This should either use the string format method, e.g.
                         "$ {x:.2f}", or be a :class:`matplotlib.ticker.Formatter`.
            textcolors : A list or array of two color specifications. The first is
                         used for values below a threshold, the second for those
                         above.
            threshold  : Value in data units according to which the colors from
                         textcolors are applied. If None (the default) uses the
                         middle of the colormap as separation.

        Further arguments are passed on to the created text labels.
        valfmt="{x:d}" (integer format), valfmt="{x:.1f}",
        **textkw: size=7, fontweight="bold",
        """

        # Normalize the threshold to the images color range.
        fst_cut = im.norm(fst_cut)
        snd_cut = im.norm(snd_cut)

        # Set default alignment to center, but allow it to be
        # overwritten by textkw.
        kw = dict(horizontalalignment="center",
                  verticalalignment="center")
        kw.update(textkw)

        # Get the formatter in case a string is supplied
        if isinstance(valfmt, str):
            valfmt = matplotlib.ticker.StrMethodFormatter(valfmt)

        # Loop over the data and create a `Text` for each "pixel".
        # Change the text's color depending on the data.
        texts = []
        if cat_clr_bar is None:
            for i in range(data.shape[0]):
                for j in range(data.shape[1]):
                    kw.update(color=txtclr[fst_cut < im.norm(data[i, j]) < snd_cut])
                    text = im.axes.text(j, i, matplotlib.ticker.FuncFormatter(func)(data[i, j], None), **kw)
                    texts.append(text)
        elif bin == 9:
            for i in range(data.shape[0]):
                for j in range(data.shape[1]):
                    texts.append(
                        ax.text(j, i, int(data[i, j]), ha="center", va="center", color=txtclr[0 < im.norm(data[i, j])],
                                size=2))
        elif bin == 5:
            for i in range(data.shape[0]):
                for j in range(data.shape[1]):
                    texts.append(
                        ax.text(j, i, f"{np.round(float(data[i, j])*100, 2)}%", ha="center", va="center", color='black',
                                size=1.5))

        return texts

    if cat_clr_bar is None:
        _annotate_rankmap(im=im, size=0.5)
    else:
        _annotate_rankmap(im=im, size=0.5, txtclr=["white", "black"], valfmt=matplotlib.ticker.FuncFormatter(func2))
    # matplotlib.ticker.FuncFormatter(
    #     "{:.2f}".format(data).replace("0.", ".").replace("0.00", "")))
    # Loop over data dimensions and create text annotations.

    ax.set_title(title, fontsize=10, y=1.5)
    ax.set_ylabel(y_label, fontsize=5)
    # plt.title(title, y=1.5)

    fig.tight_layout(h_pad=1)
    fig.savefig(archivo, dpi=1000)
    plt.close()
