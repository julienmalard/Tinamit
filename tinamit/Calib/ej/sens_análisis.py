import numpy as np



def verif_sens(método, tipo_egr, egr, mapa_paráms, p_soil_class):

    if tipo_egr == "forma" or  tipo_egr == 'superposition':
        final_sens = {método: {tipo_egr: {p_name: {b_name: {bp_gof: {para:{f_name: np.asarray([f_val[id][i]
                                                                          for i, id in enumerate(p_soil_class)])
                                                                 for f_name, f_val in val.items()} if para in mapa_paráms else val
                                                           for para, val in bp_gof_val['mu_star'].items()}
                                                  for bp_gof, bp_gof_val in b_val.items()}
                                         for b_name, b_val in p_val.items()}
                                for p_name, p_val in egr[tipo_egr].items()}}}


    elif tipo_egr == "paso_tiempo":
        final_sens = {método: {tipo_egr: {p_name: {para: {paso: np.asarray([paso_val[id][i]
                                                                for i, id in enumerate(p_soil_class)])
                                                        for paso, paso_val in val.items()} if para in mapa_paráms else val
                                                for para, val in p_val['mu_star'].items()}
                                for p_name, p_val in egr[tipo_egr].items()}}}
    elif tipo_egr == "promedio":
        final_sens = {método: {tipo_egr: {p_name: {para: np.asarray([val[id][i]
                                                    for i, id in enumerate(p_soil_class)]) if para in mapa_paráms else val
                                               for para, val in p_val['mu_star'].items()}
                                      for p_name, p_val in egr[tipo_egr].items()}}}
    else:
        raise Exception('Not defined type!')


    '''simulation, vars_egr = carg_simul_dt(simul_arch['arch_simular'], simul_arch['num_samples'])

    if not isinstance(vars_egr, list):
        vars_egr = [vars_egr]

    f_simul = np.load(f_simul_arch).tolist()

    def _gen_matr_i_sens(líms_prm, mapa_prm, t_final, tipo_egr):
        if not isinstance(mapa_prm, dict):  # the orther mapa_matrix
            if tipo_egr == 'paso_tiempo':
                matr_i_sens = np.zeros([len(líms_prm), t_final + 1, len(mapa_prm)])
                for t in range(t_final + 1):
                    for y in range(len(mapa_prm)):
                        matr_i_sens[mapa_prm[y], t, y] = 1
            else:
                matr_i_sens = np.zeros([len(líms_prm), len(mapa_prm)])  # 4*215
                for y in range(len(mapa_prm)):  # y-215
                    matr_i_sens[mapa_prm[y], y] = 1
        else:  # only kaq
            l_y = list(mapa_prm['mapa'].values())  # take kaq_1,2,3,4
            if tipo_egr == 'paso_tiempo':
                matr_i_sens = np.zeros([len(líms_prm), t_final + 1, len(l_y[0])])
                for t in range(t_final + 1):
                    for y in range(len(l_y)):
                        matr_i_sens[l_y[y], t, y] = 1
            else:
                matr_i_sens = np.zeros([len(líms_prm), len(l_y[0])])  # 4*215
                for kaq_i in range(len(l_y)):
                    for y in range(len(l_y[0])):
                        matr_i_sens[l_y[kaq_i][y], y] = 1

        return np.greater(matr_i_sens, 0)

    if tipo_egr == 'forma':
        final_sens = {mtds: {tipo_egr: {bp: {bpp_aic: np.empty([11, 215])
                                             for i, bpp_aic in enumerate(bg.values())} for bp, bg in f_simul.items()}}}
    elif tipo_egr == 'promedio':
        final_sens = {mtds: {tipo_egr: {np.empty([11, 215])}}}
    else:
        final_sens = {mtds: {tipo_egr: {bpp: np.empty([11, 215]) for bpp in f_simul}}

    for prm in líms_paráms:
        if prm not in mapa_paráms: # prm is sdm var
            dims_p = (1,)
            dims_y = (215,)

            final_sens[mtds][tipo_egr].update(_proc_res_sens(tipo_egr, vars_egr, prm, egr, mtds, dims_p, dims_y,
                                                             t_final, mapa_paráms, sens=True, i_sens=None))
        else: # prm is bf var
            for p, val in mapa_paráms:
                if isinstance(val, dict):
                    for i in range(len(val['mapa'])):
                        líms_paráms.update({list(val['mapa'].keys())[i]: líms_paráms[p]})
                    del líms_paráms[p]

            mask = _gen_matr_i_sens(líms_paráms[prm], mapa_paráms[prm], t_final, tipo_egr)
            dims_p = (len(líms_paráms[prm]),) #4
            dims_y = (215,)

            final_sens[mtds][tipo_egr].update(_proc_res_sens(
                tipo_egr, vars_egr, prm, egr, mtds, dims_p, dims_y, t_final, mapa_paráms, sens=True, i_sens=mask
            ))'''
    return final_sens

def _proc_res_sens(tipo_egr, vars_egr, prm, egr, m, dims_p, dims_y, t_final, mapa_paráms, sens, i_sens):
    d_vals = egr[tipo_egr][vars_egr[0]]

    def _sacar_val(nombre, tipo_egr):
        if tipo_egr == 'forma':
            behav_dict = {bp: {prm: {} , 'Ficticia': {}} for bp in d_vals}
            for bp, bp_dict in d_vals.items():
                for bg, si_dict in bp_dict.items():
                    behav_dict[bp][prm].update(si_dict[nombre][prm])
                    behav_dict[bp][prm].update(si_dict[nombre]['Ficticia'])

        else:
            behav_dict = {prm: {}}
            d_val = d_vals[nombre]
            behav_dict.update(d_val[prm])
            behav_dict.update(d_val['Ficticia'])

        return behav_dict

    def _verify_no_sig(behav_dict, sello, rtol=0.1):
        if i_sens is not None:
            inv_sens = np.invert(i_sens)
            no_sens = {'no_sig': {behav_dict[bp][prm]: {} for bp in d_vals}}
            for bp in d_vals:
                for bpp_aic in behav_dict[bp][prm]:
                    no_sens['no_sig'].update(behav_dict[bp][prm][bpp_aic][inv_sens])
                    val_fict = behav_dict[bp]['Ficticia'][bpp_aic][np.where(i_sens)[1]]

            # no_sens = val_prm[inv_sens]

            return i_sens, val_prm[inv_sens], val_fict[np.where(i_sens)[1]]
            # _no_sig(val_prm[inv_sens], sello, val_fict[np.where(i_sens)[1]], rtol)

        else:
            if behav_dict[prm].ndim < 2:
                _no_sig(behav_dict[prm], sello, behav_dict['Ficticia'], rtol)
            else:
                for y in range(dims_y[0]):
                    _no_sig(behav_dict[prm][:, y], sello, behav_dict['Ficticia'][:, y], rtol)

    def _no_sig(val_prm, sello, val_fict, rtol):
        #return every try
        try:
            np.less_equal(val_prm, sello)
        except AssertionError:
            try:
                np.less_equal(val_prm, val_fict)
            except AssertionError:
                raise NotImplementedError
               # np.(val_prm, val_fict, rtol=rtol)

    def _verificar_sig(behav_dict, sello, rtol=0.1):
        if i_sens is not None:
            # return val_prm[i_sens], val_fict[np.where(i_sens)[1]]
            _sig(val_prm[i_sens], sello, val_fict[np.where(i_sens)[1]], rtol)

        else:
            if val_prm.ndim < 2:
                _sig(val_prm, sello, val_fict, rtol)
            else:
                for y in range(dims_y[0]):
                    _sig(val_prm[:, y], sello, val_fict[:, y], rtol)

    def _sig(val_prm, sello, val_fict, rtol):
        np.less_equal(sello, val_prm)
        np.less_equal(val_fict, val_prm)
        np.less_equal(rtol, np.abs(val_fict - val_prm) / val_fict)

    if m == 'morris':
        mu_star_behav_dict = _sacar_val('mu_star', tipo_egr)

        # mu_star_prm, mu_star_fict = _sacar_val('mu_star', tipo_egr)

        if sens:
            _verificar_sig(mu_star_behav_dict, sello=0.1)

            _verify_no_sig(mu_star_behav_dict, sello=0.1)

    elif m == 'fast':
        si_behav_dict = _sacar_val('Si', tipo_egr)
        st_si_behav_dict = _sacar_val('St-Si', tipo_egr)

        if sens:
            _verificar_sig(si_behav_dict, sello=0.01)

            _verify_no_sig(st_si_behav_dict, sello=0.1)
            _verify_no_sig(st_si_behav_dict, sello=0.01)

    else:
        raise ValueError(m)


def map_sens(geog, metodo, tipo_egr, para_name, data, threshold, path, behav=None, paso=None, ids=None):
    vars_interés = {tipo_egr: {
        # 'col': ['#21bf13', '#FFCC66', '#eaa607', '#ea0707'],
        'col': ['#0f6607', '#278e1d', '#abed49', '#ccc80c', '#eaea07', '#eaa607', '#ea0707'],
        'categs': [prm for prm in para_name], #categs is not in dibujar anymore
        'escala_núm': [np.min(data), np.max(data)]}
                    }

    unid = 'Sensitivity Index' #'Soil salinity'
    # this is to calculate the range for the array--values
    # escala = (np.min(data), np.max(data))  # minim and maxi values of mu_star for each parameter among all polys
    escala = np.int32(0), np.float(threshold)


    for v, d in vars_interés.items():

        for j in [0, 5, 15, 20]:
            geog.dibujar(archivo=path + f'old-{j}', valores=data[j], título=f'Soil salinity old paso-{j}',
                         unidades='Soil salinity level',
                         colores=d['col'], ids=[str(i) for i in range(1, 216)]) # for azahr

        #paso
        # ll = [0, 5, 15, 20]
        # for i in ll:
        #     geog.dibujar(archivo=path + f'{i}{para_name}', valores=data[f'paso_{i}'], título=f"{metodo}-{para_name}-at paso-{i} to Watertable-depth",
        #                  unidades=unid, colores=d['col'], ids=[str(j) for j in range(1, 216)])


        #mean val
        # geog.dibujar(archivo=path + f'prom-{para_name}', valores=data,
        #              título=f"{metodo}-{para_name}-to watertable-prom",
        #                  unidades=unid, colores=d['col'], ids=[str(j) for j in range(1, 216)])

        #beahv
        # for bpprm in data: # "D:\Thesis\pythonProject\localuse\Dt\Mor\map\\spp\\aic\\{bpprm}-{behav}-{para_name}" #f"D:\Thesis\pythonProject\localuse\Dt\Mor\map\spp\\bppprm\\bpprm-{behav}-{para_name}"
        #     geog.dibujar(archivo=f"D:\Thesis\pythonProject\localuse\Dt\Mor\map\spp\\aic\\{para_name}-{behav}-{bpprm}",
        #                  valores=data[bpprm], título=f"Mor-{para_name[: 5]}-'{bpprm}'-{behav}",
        #                  unidades=unid, colores=d['col'], ids=[str(j) for j in range(1, 216)])

        # geog.dibujar(archivo="D:\Thesis\pythonProject\localuse\Dt\Mor\map\\test\\test", valores=data['paso_0'],
        #              título='test', unidades=unid,
        #              colores=d['col'], ids=[str(i) for i in range(1, 216)], escala_num=escala)