import re
import time

import numpy as np

from tinamit import _
from tinamit.Análisis.Sens.muestr import cargar_mstr_paráms
import json


def gen_vals_inic(mstr, mapa_paráms):
    if mapa_paráms is None:
        mapa_paráms = {}
    n_iter = len(list(mstr.values())[0])

    vals_inic = {í: {p: v[í] for p, v in mstr.items()
                     if not any(re.match(r'{}(_[0-9]*)?$'.format(p2), p) for p2 in mapa_paráms)
                     }
                 for í in range(n_iter)}

    for p, mapa in mapa_paráms.items():
        if isinstance(mapa, list):
            mapa = np.array(mapa)
        if isinstance(mapa, np.ndarray):
            for í in range(n_iter):
                val_var = [
                    mstr[f'{p}_{í_p}'][í] for í_p in mapa_paráms[p]
                ]
                vals_inic[í][p] = np.array(val_var)

        elif isinstance(mapa, dict):
            transf = mapa['transf'].lower()

            for í in range(n_iter):
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


def simul_sens_faltan(mod, arch_mstr, dir, mapa_paráms, var_egr, índ_mstrs=None):
    faltan = buscar_simuls_faltan(arch_mstr, dir)
    if índ_mstrs is not None:
        faltan = {ll: v for ll, v in faltan.items() if índ_mstrs[0] <= ll < índ_mstrs[1]}

    # simul_sens_de_dic(mod=mod, mstr_paráms=faltan, mapa_paráms=mapa_paráms, var_egr=var_egr)

def simul_sens(mod, mstr_paráms, var_egr, método, tiempo_final=None, indices_mstrs=None, guardar=False, archivo=None):
    evals = []
    if indices_mstrs is not None: # tuple((tuple), ())
        for ind in indices_mstrs:
            evals.append(simul_sens_ind(mod, mstr_paráms, var_egr, método, tiempo_final=tiempo_final, ind_mstrs=ind,
                           guardar=guardar, archivo=archivo))
    else:
        evals.append(simul_sens_ind(mod, mstr_paráms, var_egr, método=método, tiempo_final=tiempo_final, guardar=guardar,
                                    archivo=archivo))
    return np.asarray(evals)


def simul_sens_ind(mod, mstr_paráms, var_egr, método=None, tiempo_final=None, ind_mstrs=None, guardar=False, archivo=None):

    if ind_mstrs is not None:
        vals_inic = [v for ll, v in enumerate(mstr_paráms) if ind_mstrs[0] <= ll <= ind_mstrs[1]] ####
    res = mod.simular_paralelo(vals_inic=vals_inic, vars_interés=var_egr, tiempo_final=tiempo_final, método=método)

    if guardar: #save
        with open(archivo, 'w', encoding='UTF-8') as d:
            json.dump(res, d)

    return res

def buscar_simuls_faltan(arch_mstr, dir):
    mstr = cargar_mstr_paráms(arch_mstr)
    n_mstr = len(mstr)

    faltan = {}
    ###
    return faltan


# def mstrs_group(mapa_paráms, intercep=None, archivo=None, guardar=False):
#     if intercep is None:
#         return mapa_paráms
#     else:
#         mstrs_groups = []
#         n_group = int(mapa_paráms.__len__() / intercep)  # group the Ns into Ns/25 groups
#         last_group = mapa_paráms.__len__() % intercep  # 取余 add the residue to the last intergal group
#
#         # define the same number of simulated data and saved in group form, in case of crush
#         # ith group
#         for i in range(n_group):
#             mstrs_groups.append(
#                 mapa_paráms[i * intercep: (i * intercep + intercep)])  # 0-99； 100-199; 200-299 etc.
#         if last_group != 0:
#             mstrs_groups.append(mapa_paráms[(n_group - 1) * intercep: ((n_group - 1) * intercep +
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
#                 intercep=None, índ_mstrs=None):
#     # groups
#     mstrs_groups = mstrs_group(mapa_paráms, intercep, archivo_m, guardar)
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



