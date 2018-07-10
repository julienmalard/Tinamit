import os
import re
import time

import numpy as np

from tinamit import _
from tinamit.Análisis.Sens.muestr import cargar_mstr_paráms
import json


def gen_vals_inic(mstr, mapa_paráms):
    if mapa_paráms is None:
        mapa_paráms = {}
    ej_mstr = list(mstr.values())[0]

    if isinstance(ej_mstr, np.ndarray):
        iters = range(ej_mstr.size)
    elif isinstance(ej_mstr, list):
        iters = range(len(ej_mstr))
    else:
        iters = ej_mstr.keys()

    vals_inic = {í: {p: v[í] for p, v in mstr.items()
                     if not any(re.match(r'{}(_[0-9]*)?$'.format(p2), p) for p2 in mapa_paráms)
                     }
                 for í in iters}

    for p, mapa in mapa_paráms.items():
        if isinstance(mapa, list):
            mapa = np.array(mapa)
        if isinstance(mapa, np.ndarray):
            for í in iters:
                val_var = [
                    mstr[f'{p}_{í_p}'][í] for í_p in mapa_paráms[p]
                ]
                vals_inic[í][p] = np.array(val_var)

        elif isinstance(mapa, dict):
            transf = mapa['transf'].lower()

            for í in iters:
                for var, mp_var in mapa['mapa'].items():
                    if transf == 'prom':
                        val_var = [
                            (mstr['{}_{}'.format(p, t_índ[0])][í] + mstr['{}_{}'.format(p, t_índ[1])][í]) / 2
                            for t_índ in mp_var
                        ]
                    else:
                        raise ValueError(_('Transformación "{}" no reconocida.').format(transf))

                    vals_inic[í][var] = np.array(val_var)

    return vals_inic


def gen_índices_grupos(n_iter, tmñ_grupos):
    n_grupos_completos = int(n_iter / tmñ_grupos)
    resto = n_iter % tmñ_grupos
    tmñs = [tmñ_grupos] * n_grupos_completos + [resto] * (resto != 0)
    cums = np.cumsum(tmñs)
    índs_grupos = [list(range(cums[í - 1], cums[í])) if í > 0 else list(range(cums[í])) for í in range(cums.size)]
    return índs_grupos


def simul_faltan(mod, arch_mstr, dir, mapa_paráms, var_egr, índ_mstrs=None):
    faltan = buscar_simuls_faltan(arch_mstr, dir)

    # simul_sens_de_dic(mod=mod, mstr_paráms=faltan, mapa_paráms=mapa_paráms, var_egr=var_egr)


def simul_sens_por_grupo(mod, mstr_paráms, mapa_paráms, var_egr, direc, tiempo_final, tmñ_grupos,
                         í_grupos, guardar=True, paralelo=False):
    if isinstance(í_grupos, int):
        í_grupos = [í_grupos]
    n_iter = len(list(mstr_paráms.values())[0])
    índs_grupos = gen_índices_grupos(n_iter=n_iter, tmñ_grupos=tmñ_grupos)
    índices_mstrs = np.array([índs_grupos[í] for í in í_grupos]).ravel()
    return simul_sens(
        mod=mod, mstr_paráms=mstr_paráms, mapa_paráms=mapa_paráms, var_egr=var_egr, direc=direc,
        tiempo_final=tiempo_final, guardar=guardar, índices_mstrs=índices_mstrs, paralelo=paralelo
    )


def simul_sens(mod, mstr_paráms, mapa_paráms, var_egr, direc, tiempo_final, guardar=True, índices_mstrs=None,
               paralelo=True):
    if índices_mstrs is None:
        índices_mstrs = range(len(list(mstr_paráms.values())[0]))
    if isinstance(índices_mstrs, tuple):
        índices_mstrs = range(*índices_mstrs)

    mstrs_escogidas = {p: {í: mstr_paráms[p][í] for í in índices_mstrs} for p in mstr_paráms}
    #chosen samples

    vals_inic = gen_vals_inic(mstrs_escogidas, mapa_paráms)

    res_corridas = mod.simular_paralelo(tiempo_final=tiempo_final, vals_inic=vals_inic, vars_interés=var_egr,
                                        paralelo=paralelo)

    if guardar:
        for índ, res in res_corridas.items():
            guardar_json(dic=res, arch=os.path.join(direc, f'{índ}.json'))

    return res_corridas


def _jsonificar(dic, egr=None):
    if egr is None:
        egr = {}
    for ll, v in dic.items():
        if isinstance(v, np.ndarray):
            egr[ll] = v.tolist()
        elif isinstance(v, dict):
            _jsonificar(dic=v, egr=egr)
        else:
            egr[ll] = v

    return egr


def _numpyficar(dic, egr=None):
    if egr is None:
        egr = {}
    for ll, v in dic.items():
        if isinstance(v, list):
            egr[ll] = np.array(v)
        elif isinstance(v, dict):
            _jsonificar(dic=v, egr=egr)
        else:
            egr[ll] = v

    return egr


def guardar_json(dic, arch):
    dir, nmbr_arch = os.path.split(arch)
    if not os.path.isdir(dir):
        os.makedirs(dir)
    with open(arch, 'w', encoding='UTF-8') as d:
        json.dump(_jsonificar(dic), d, ensure_ascii=False)


def cargar_json(arch):
    with open(arch, encoding='UTF-8') as d:
        dic = json.load(d)
    return _numpyficar(dic)


def buscar_simuls_faltan(mstr, direc):
    if isinstance(mstr, str):
        mstr = cargar_mstr_paráms(mstr)
    n_mstr = len(list(mstr.values())[0])

    faltan = [i for i in range(n_mstr) if
              not os.path.isfile(os.path.join(direc, f'{i}.json'))]

    return faltan

# def mstrs_group(mapa_paráms, tmñ_grupo=None, archivo=None, guardar=False):
#     if tmñ_grupo is None:
#         return mapa_paráms
#     else:
#         mstrs_groups = []
#         n_group = int(len(mapa_paráms) / tmñ_grupo)  # group the Ns into Ns/25 groups
#         last_group = mapa_paráms.__len__() % tmñ_grupo  # 取余 add the residue to the last intergal group
#
#         # define the same number of simulated data and saved in group form, in case of crush
#         # ith group
#         for i in range(n_group):
#             mstrs_groups.append(
#                 mapa_paráms[i * tmñ_grupo: (i * tmñ_grupo + tmñ_grupo)])  # 0-99； 100-199; 200-299 etc.
#         if last_group != 0:
#             mstrs_groups.append(mapa_paráms[(n_group - 1) * tmñ_grupo: ((n_group - 1) * tmñ_grupo +
#                                                                        last_group)])
#         if guardar and archivo:  # save
#             for i, data in enumerate(mstrs_groups):
#                 with open(f'{archivo}-{i}.out', 'w', encoding='UTF-8') as f0:
#                     json.dump(data, f0)
#
#         return mstrs_groups


# def cargar_mapa_groups(archivos):
#     groups_data = []
#     for archivo in archivos:
#         with open(archivo, encoding='UTF-8') as d:
#             groups_data.append(json.load(d))
#     return groups_data


# def simul_mstrs(mod, mapa_paráms, tiempo_final, var_egr, método, archivo_m=None, archivo_r=None, guardar=False, \
#                 tmñ_grupo=None, índ_mstrs=None):
#     # groups
#     mstrs_groups = mstrs_group(mapa_paráms, tmñ_grupo, archivo_m, guardar)
#     evals = []
#     # for each group
#     start_time = time.time()
#     for ee in mstrs_groups:
#         evals.append(simul_sens(mod, ee, tiempo_final, var_egr, método, archivo_r, guardar, índ_mstrs))
#     print("--- %s total seconds ---" % (time.time() - start_time))
#     return evals


# def simul_sens(mod, mapa_paráms, tiempo_final, var_egr, método, archivo=None, guardar=False, índ_mstrs=None):
#     start_time = time.time()
#     if índ_mstrs is not None:
#         mapa_paráms = [data for ll, data in enumerate(mapa_paráms) if índ_mstrs[0] <= ll < índ_mstrs[1]]
#
#     res = mod.simular_paralelo(tiempo_final, vars_interés=var_egr, nombre_corrida=método, vals_inic=mapa_paráms)
#
#     # try:
#     #     res = mod.simular_paralelo(tiempo_final, vars_interés=var_egr, nombre_corrida=método, vals_inic=mapa_paráms)
#     # except Exception as isnt:
#     #     print(isnt)
#
#     if guardar and archivo:  # save
#         # print(archivo)
#         with open(archivo, 'w', encoding='UTF-8') as d:
#             json.dump(res, d)
#     print("--- %s seconds ---" % (time.time() - start_time))
#     return res

# simul_sens_de_dic(mod=mod, mapa_paráms=mapa_paráms, var_egr=var_egr, tiempo_final=tiempo_final, método=método)


# def simul_sens_de_dic(mod, mapa_paráms, var_egr, tiempo_final, método, archivo=None, guardar=False):
#
#     res = mod.simular_paralelo(vals_inic=mapa_paráms, vars_interés=var_egr, tiempo_final=tiempo_final, método=método)
#
#     if guardar and archivo: #save
#         with open(archivo, encoding='UTF-8') as d:
#             json.dump(res, d)


# def simul_sens(mod, mstr_paráms, mapa_paráms, var_egr, índ_mstrs=None):
#
#     if isinstance(mstr_paráms, list):
#         mstr_paráms = {í: x for í, x in enumerate(mstr_paráms)}
#     if índ_mstrs is not None:
#         mstr_paráms = {ll: v for ll, v in mstr_paráms.items() if índ_mstrs[0] <= ll < índ_mstrs[1]}
#     simul_sens_de_dic(mod=mod, mstr_paráms=mstr_paráms, mapa_paráms=mapa_paráms, var_egr=var_egr)
#
#
# def simul_sens_de_dic(mod, mstr_paráms, mapa_paráms, var_egr, guardar=False):
#
#     vals_inic = mstr_paráms
#     if mapa_paráms is not None:
#         pass
#
#     res = mod.simular_paralelo(vals_inic=vals_inic, vars_interés=var_egr, tiempo_final=tiempo_final, método=método)
#
#     if guardar: #save
#         with open() as d:
#             json.dump(res, d)
