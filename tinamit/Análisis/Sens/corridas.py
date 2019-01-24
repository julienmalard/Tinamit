import os
import re
import time
from datetime import datetime

import numpy as np

from tinamit.Análisis.Sens.muestr import cargar_mstr_paráms
from tinamit.config import _
from tinamit.cositas import guardar_json, cargar_json


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

    # mapa_paráms_final = {}
    # for p, mapa in mapa_paráms.items():
    #     if isinstance(mapa, dict):
    #         if len(mapa) > 1:
    #             mapa_paráms_final.update({k: v for k, v in mapa['mapa'].items()})
    #     else:
    #         mapa_paráms_final.update({p: mapa})

    # vals_inic = {í: {p: v[í] for p, v in mstr.items()
    #                  if not any(re.match(r'{}(_[0-9]*)?$'.format(p2), p) for p2 in mapa_paráms_final) and p != 'Ficticia'
    #                  }
    #              for í in iters}

    vals_inic = {í: {p: v[í] for p, v in mstr.items()
                     if
                     not any(re.match(r'{}(_[0-9]*)?$'.format(p2), p) for p2 in mapa_paráms) and p != 'Ficticia'
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
            # if len(mapa['mapa'])>1:
            #     for í in iters:
            #         for var, mp_var in mapa['mapa'].items():
            #             if transf == 'prom':
            #                 val_var = [
            #                     (mstr['{}_{}'.format(var, t_índ[0])][í] + mstr['{}_{}'.format(var, t_índ[1])][í]) / 2
            #                     for t_índ in mp_var
            #                 ]
            #
            #             vals_inic[í][var] = np.array(val_var)
            # else:
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


def simul_faltan(mod, arch_mstr, direc, mapa_paráms, var_egr, t_final, índices_mstrs=None, paralelo=None):
    faltan = buscar_simuls_faltan(arch_mstr, direc)
    if índices_mstrs is not None:
        faltan = [í for í in índices_mstrs if í in faltan]
    mstr_paráms = cargar_mstr_paráms(arch_mstr)
    simul_sens(mod=mod, mstr_paráms=mstr_paráms, mapa_paráms=mapa_paráms, var_egr=var_egr,
               t_final=t_final, guardar=direc, índices_mstrs=faltan, paralelo=paralelo)


def simul_sens_por_grupo(mod, mstr_paráms, mapa_paráms, var_egr, t_final, tmñ_grupos,
                         í_grupos, guardar=True, paralelo=None):
    if isinstance(í_grupos, int):
        í_grupos = [í_grupos]
    n_iter = len(list(mstr_paráms.values())[0])
    índs_grupos = gen_índices_grupos(n_iter=n_iter, tmñ_grupos=tmñ_grupos)
    índices_mstrs = np.array([índs_grupos[í] for í in í_grupos]).ravel()
    return simul_sens(
        mod=mod, mstr_paráms=mstr_paráms, mapa_paráms=mapa_paráms, var_egr=var_egr,
        t_final=t_final, guardar=guardar, índices_mstrs=índices_mstrs, paralelo=paralelo
    )


def simul_sens(mod, mstr_paráms, mapa_paráms, var_egr, t_final, guardar=True, índices_mstrs=None,
               paralelo=None):
    if índices_mstrs is None:
        índices_mstrs = range(len(list(mstr_paráms.values())[0]))
    if isinstance(índices_mstrs, tuple):
        índices_mstrs = range(*índices_mstrs)

    mstrs_escogidas = {p: {í: mstr_paráms[p][í] for í in índices_mstrs} for p in mstr_paráms}
    # chosen samples 23*625

    vals_inic = gen_vals_inic(mstrs_escogidas, mapa_paráms)
    start_time = datetime.now().strftime("%H:%M:%S")
    FMT = '%H:%M:%S'
    print(f"Initializing simulation {start_time} ")
    res_corridas = mod.simular_grupo(
        t_final=t_final, vals_inic=vals_inic, vars_interés=var_egr, paralelo=paralelo, guardar=guardar
    )
    print(
        f"Simulation elapse {datetime.strptime(datetime.now().strftime('%H:%M:%S'), FMT) - datetime.strptime(start_time, FMT)}")
    return res_corridas


def buscar_simuls_faltan(mstr, direc):
    if isinstance(mstr, str):
        mstr = cargar_mstr_paráms(mstr)
    n_mstr = len(list(mstr.values())[0])

    faltan = [i for i in range(n_mstr) if not os.path.isfile(os.path.join(direc, f'{i}.json'))]

    return faltan
