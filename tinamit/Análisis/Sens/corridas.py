import time

from tinamit.Análisis.Sens.muestr import cargar_mstr_paráms
import json

def simul_sens_faltan(mod, arch_mstr, dir, mapa_paráms, var_egr, índ_mstrs=None):
    faltan = buscar_simuls_faltan(arch_mstr, dir)
    if índ_mstrs is not None:
        faltan = {ll: v for ll, v in faltan.items() if índ_mstrs[0] <= ll < índ_mstrs[1]}

    # simul_sens_de_dic(mod=mod, mstr_paráms=faltan, mapa_paráms=mapa_paráms, var_egr=var_egr)

def mstrs_group(mapa_paráms, intercep=None, archivo=None, guardar=False):
    if intercep is None:
        return mapa_paráms
    else:
        mstrs_groups  = []
        n_group = int(mapa_paráms.__len__() / intercep)  # group the Ns into Ns/25 groups
        last_group = mapa_paráms.__len__() % intercep  # 取余 add the residue to the last intergal group

        # define the same number of simulated data and saved in group form, in case of crush
        # ith group
        for i in range(n_group):
            mstrs_groups.append(
                mapa_paráms[i * intercep: (i * intercep + intercep)])  # 0-99； 100-199; 200-299 etc.
        if last_group != 0:
            mstrs_groups.append(mapa_paráms[(n_group - 1) * intercep: ((n_group - 1) * intercep +
                                                                             last_group)])
        if guardar and archivo:  # save
            for i, data in enumerate(mstrs_groups):
                with open(f'{archivo}-{i}.out', 'w', encoding='UTF-8') as f0:
                    json.dump(data, f0)

        return mstrs_groups

def cargar_mapa_groups(archivos):
    groups_data = []
    for archivo in archivos:
        with open(archivo, encoding='UTF-8') as d:
            groups_data.append(json.load(d))
    return groups_data


def simul_mstrs(mod, mapa_paráms, tiempo_final, var_egr, método, archivo_m=None, archivo_r=None, guardar=False, \
                intercep=None, índ_mstrs=None):
    # groups
    mstrs_groups = mstrs_group(mapa_paráms, intercep, archivo_m, guardar)
    evals = []
    # for each group
    start_time = time.time()
    for ee in mstrs_groups:
        evals.append(simul_sens(mod, ee, tiempo_final, var_egr, método, archivo_r, guardar, índ_mstrs))
    print("--- %s total seconds ---" % (time.time() - start_time))
    return evals


def simul_sens(mod, mapa_paráms, tiempo_final, var_egr, método, archivo=None, guardar=False, índ_mstrs=None):
    start_time = time.time()
    if índ_mstrs is not None:
        mapa_paráms = [data for ll, data in enumerate(mapa_paráms) if índ_mstrs[0] <= ll < índ_mstrs[1]]

    res = mod.simular_paralelo(tiempo_final, vars_interés=var_egr, nombre_corrida=método, vals_inic=mapa_paráms)

    # try:
    #     res = mod.simular_paralelo(tiempo_final, vars_interés=var_egr, nombre_corrida=método, vals_inic=mapa_paráms)
    # except Exception as isnt:
    #     print(isnt)

    if guardar and archivo:  # save
        #print(archivo)
        with open(archivo, 'w', encoding='UTF-8') as d:
            json.dump(res, d)
    print("--- %s seconds ---" % (time.time() - start_time))
    return res

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


def buscar_simuls_faltan(arch_mstr, dir):
    mstr = cargar_mstr_paráms(arch_mstr)
    n_mstr = len(mstr)

    faltan = {}
    ###
    return faltan