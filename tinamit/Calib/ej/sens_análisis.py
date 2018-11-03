from collections import Counter
from tinamit.Análisis.Sens.behavior import find_best_behavior

import numpy as np


def verif_sens(método, tipo_egr, egr, mapa_paráms, p_soil_class):
    if tipo_egr == "forma" or tipo_egr == 'superposition':
        final_sens = {método: {tipo_egr: {p_name: {b_name: {bp_gof: {para: {f_name: np.asarray([f_val[id][i]
                                                                                                for i, id in enumerate(
                p_soil_class)])
                                                                            for f_name, f_val in
                                                                            val.items()} if para in mapa_paráms else val
                                                                     for para, val in bp_gof_val['mu_star'].items()}
                                                            for bp_gof, bp_gof_val in b_val.items()}
                                                   for b_name, b_val in p_val.items()}
                                          for p_name, p_val in egr[tipo_egr].items()}}}


    elif tipo_egr == "paso_tiempo":
        final_sens = {método: {tipo_egr: {p_name: {para: {paso: np.asarray([paso_val[id][i]
                                                                            for i, id in enumerate(p_soil_class)])
                                                          for paso, paso_val in
                                                          val.items()} if para in mapa_paráms else val
                                                   for para, val in p_val['mu_star'].items()}
                                          for p_name, p_val in egr[tipo_egr].items()}}}
    elif tipo_egr == "promedio":
        final_sens = {método: {tipo_egr: {p_name: {para: np.asarray([val[id][i]
                                                                     for i, id in enumerate(
                p_soil_class)]) if para in mapa_paráms else val
                                                   for para, val in p_val['mu_star'].items()}
                                          for p_name, p_val in egr[tipo_egr].items()}}}
    else:
        raise Exception('Not defined type!')

    return final_sens


def analy_behav_by_dims(samples, dims, f_simul_arch, dim_arch=False, gaurdar=None):
    counted_all_behaviors_keys = []
    counted_all_behaviors = []
    if dim_arch is False:
        fited_behav = {i: {j: {} for j in range(samples)} for i in range(dims)}
        for j in range(samples):
            print(f'this is {j}-th sample')
            # behav = np.load(
            #         f"D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\f_simul\corrected_bf\\new_spp\\new_f_simul_sppf_simul_{j}.npy").tolist()
            behav = np.load(f_simul_arch + f"new_f_simul_sppf_simul_{j}.npy").tolist()
            fited_behaviors = []
            for i in range(dims):
                fited_behaviors.append(find_best_behavior(behav, trans_shape=i)[0])
                fited_behav[i][j] = find_best_behavior(behav, trans_shape=i)
                print(f'processing {i} poly')

            # counted_behaviors = Counter([k for k, v in fited_behaviors])
            # counted_all_behaviors.extend(counted_behaviors)
            # counted_all_behaviors_keys.extend(list(counted_behaviors.keys()))
        if gaurdar is not None:
            # np.save("D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\f_simul\\dict_fited_behav", fited_behav)
            # np.save("D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\f_simul\\best_behav_poly", fited_behaviors)

            np.save(gaurdar + 'fited_behav', fited_behav)
            np.save(gaurdar + 'fited_behaviors', fited_behaviors)
        else:
            print(f'the best shape for all dims are {fited_behaviors}')

    else:
        fited_behav = {}
        aic_behav = {}
        for i in range(dims):
            count_fited_behav_by_poly = []
            # polynal_fited_behav = np.load("D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\f_simul\\dict_fited_behav.npy")[i]
            polynal_fited_behav = np.load(dim_arch)[i]
            for j in range(samples):
                count_fited_behav_by_poly.extend([key for key, val in polynal_fited_behav[j]])

            count_fited_behav_by_poly = set(count_fited_behav_by_poly)
            fited_behav.update({i: count_fited_behav_by_poly})

            aic_poly = {k: [] for k in count_fited_behav_by_poly}
            for j in range(samples):
                # behav = np.load(
                #     f"D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\f_simul\corrected_bf\\new_spp\\new_f_simul_sppf_simul_{j}.npy").tolist()
                behav = np.load(f_simul_arch + f"new_f_simul_sppf_simul_{j}.npy").tolist()

                for k in count_fited_behav_by_poly:
                    aic_poly[k].append(behav[k]['gof']['aic'][i])
            aic_behav.update({i: aic_poly})

        if gaurdar is not None:
            np.save(gaurdar + 'fited_behav', fited_behav)
            np.save(gaurdar + 'aic_behav', aic_behav)


def map_sens(geog, metodo, tipo_egr, para_name, data, threshold, path, behav=None, paso=None, ids=None):
    vars_interés = {tipo_egr: {
        # 'col': ['#21bf13', '#FFCC66', '#eaa607', '#ea0707'],
        'col': ['#0f6607', '#278e1d', '#abed49', '#ccc80c', '#eaea07', '#eaa607', '#ea0707'],
        'escala_núm': [np.min(data), np.max(data)]}
    }

    unid = 'Mor Sensitivity Index'  # 'Soil salinity'
    # this is to calculate the range for the array--values
    # escala = np.int32(0), np.float(threshold)

    for v, d in vars_interés.items():

        # for j in [0, 5, 15, 20]:
        #     geog.dibujar(archivo=path + f'old-{j}', valores=data[j], título=f'Soil salinity old paso-{j}',
        #                  unidades='Soil salinity level',
        #                  colores=d['col'], ids=ids)  # for azahr

        # paso
        # ll = [0, 5, 15, 20]
        # for i in ll:
        #     geog.dibujar(archivo=path + f'{i}-{para_name}', valores=data[f'paso_{i}'],
        #                  título=f"Mor-{para_name[: 5]}-paso-{i} to WTD",
        #                  unidades=unid, colores=d['col'], ids=ids,
        #                  escala_num=(np.min(data[f'paso_{i}']), np.max(data[f'paso_{i}'])))

        # test
        for i in [0]:
            geog.dibujar(archivo=path + f'test_{i}-{para_name}', valores=data[f'paso_{i}'],
                         título=f"Mor-{para_name[: 5]}-paso-{i} to WTD",
                         unidades=unid, colores=d['col'], ids=ids,
                         escala_num=(np.min(data[f'paso_{i}']), np.max(data[f'paso_{i}'])))

        # mean val
        # geog.dibujar(archivo=path + f'prom-{para_name}', valores=data,
        #              título=f"{metodo}-{para_name}-to watertable-prom",
        #                  unidades=unid, colores=d['col'], ids=ids, escala_num=d['escala_núm'])

        # beahv
        # for bpprm in data: # "D:\Thesis\pythonProject\localuse\Dt\Mor\map\\spp\\aic\\{bpprm}-{behav}-{para_name}" #f"D:\Thesis\pythonProject\localuse\Dt\Mor\map\spp\\bppprm\\bpprm-{behav}-{para_name}"
        #     geog.dibujar(archivo=path + f"{para_name}-{behav}-{bpprm}",
        #                  valores=data[bpprm], título=f"Mor-{para_name[: 5]}-{bpprm}-{behav}",
        #                  unidades=unid, colores=d['col'], ids=ids, escala_num=(np.min(data[bpprm]), np.max(data[bpprm])))

        # geog.dibujar(archivo=path + f'{i}{para_name}', valores=data[:, 215],
        #              título=f"{metodo}-{para_name}-paso-{i} to SS", unidades='fast SI',
        #              colores=d['col'], ids=ids, escala_num=(np.min(data[:, 215]), np.max(data[:, 215])))
