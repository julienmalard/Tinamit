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


def map_sens(geog, metodo, tipo_egr, para_name, data, threshold, path, behav=None, paso=None, ids=None):
    vars_interés = {tipo_egr: {
        # 'col': ['#21bf13', '#FFCC66', '#eaa607', '#ea0707'],
        'col': ['#0f6607', '#278e1d', '#abed49', '#ccc80c', '#eaea07', '#eaa607', '#ea0707'],
        'categs': [prm for prm in para_name],  # categs is not in dibujar anymore
        'escala_núm': [np.min(data), np.max(data)]}
    }

    unid = 'Sensitivity Index'  # 'Soil salinity'
    # this is to calculate the range for the array--values
    # escala = np.int32(0), np.float(threshold)

    for v, d in vars_interés.items():

        for j in [0, 5, 15, 20]:
            geog.dibujar(archivo=path + f'old-{j}', valores=data[j], título=f'Soil salinity old paso-{j}',
                         unidades='Soil salinity level',
                         colores=d['col'], ids=[str(i) for i in range(1, 216)])  # for azahr

        # paso
        ll = [0, 5, 15, 20]
        for i in ll:
            geog.dibujar(archivo=path + f'{i}{para_name}', valores=data[f'paso_{i}'], título=f"{metodo}-{para_name}-at paso-{i} to Watertable-depth",
                         unidades=unid, colores=d['col'], ids=[str(j) for j in range(1, 216)], escala_num=d['escala_núm'])

        # mean val
        # geog.dibujar(archivo=path + f'prom-{para_name}', valores=data,
        #              título=f"{metodo}-{para_name}-to watertable-prom",
        #                  unidades=unid, colores=d['col'], ids=[str(j) for j in range(1, 216)], escala_num=d['escala_núm'])

        # beahv
        # for bpprm in data: # "D:\Thesis\pythonProject\localuse\Dt\Mor\map\\spp\\aic\\{bpprm}-{behav}-{para_name}" #f"D:\Thesis\pythonProject\localuse\Dt\Mor\map\spp\\bppprm\\bpprm-{behav}-{para_name}"
        #     geog.dibujar(archivo=f"D:\Thesis\pythonProject\localuse\Dt\Mor\map\spp\\aic\\{para_name}-{behav}-{bpprm}",
        #                  valores=data[bpprm], título=f"Mor-{para_name[: 5]}-'{bpprm}'-{behav}",
        #                  unidades=unid, colores=d['col'], ids=[str(j) for j in range(1, 216)], escala_num=d['escala_núm'])

        # geog.dibujar(archivo="D:\Thesis\pythonProject\localuse\Dt\Mor\map\\test\\test", valores=data['paso_0'],
        #              título='test', unidades=unid,
        #              colores=d['col'], ids=[str(i) for i in range(1, 216)], escala_num=d['escala_núm'])
