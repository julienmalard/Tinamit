import string

from tinamit.Análisis.Sens.anlzr import analy_by_file
from tinamit.Análisis.Sens.corridas import simul_sens
from tinamit.Calib.ej.info_paráms import mapa_paráms, líms_paráms
from tinamit.Conectado import Conectado
from tinamit.Ejemplos.en.Ejemplo_SAHYSMOD.SAHYSMOD import Envoltura
from tinamit.Geog.Geog import Geografía


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

# %% Buchiana 1
# %% Farida 2
# %% Jhang 3
# %% Chuharkana 4

if __name__ == "__main__":
    import os
    import numpy as np

    direc = os.path.join("D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\simular\\625_mor")
    '''
    Simul
    '''
    # simul_sens(
    #     gen_mod(), mstr_paráms=mstr_morris, mapa_paráms=mapa_paráms, var_egr=devolver, t_final=20, guardar=direc,
    #     índices_mstrs=None, paralelo=True
    # )

    '''
    Anlzr
    '''
    from tinamit.Calib.ej.sens_análisis import analy_behav_by_dims, gen_alpha, map_rank, gen_counted_behavior

    # guardar = os.path.join("D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\f_simul\\f_simul_new\\")
    # mstr_mor = os.path.join('D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\sampled_data\\muestra_morris_625.json')
    # egr = analy_by_file('morris', líms_paráms, mapa_paráms, mstr_mor, dim=214,
    #                     simul_arch={'arch_simular': direc, 'num_samples': 624}, tipo_egr='superposition',
    #                     var_egr='mds_Watertable depth Tinamit')
    #                     # f_simul_arch= {'arch': "D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\f_simul\corrected_bf\\new_spp\\new_f_simul_sppf_simul",
    #                     #                'num_sample': 625,
    #                     #                'counted_behaviors':
    #                     #                    "D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\f_simul\corrected_bf\counted_all\\counted_all_behav.npy"})
    #
    # np.save(guardar, egr)

    # behav_proc_from_file(simul_arch={'arch_simular': direc, 'num_samples': 625}, tipo_egr='superposition', dim=214,
    #                      var_egr='mds_Watertable depth Tinamit', guardar=guardar)

    '''
    post_processing Anlzr 
    '''
    from tinamit.Calib.ej.sens_análisis import verif_sens
    from tinamit.Calib.ej.soil_class import p_soil_class

    no_ini = "D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\f_simul\\f_simul_no_ini\\fited_behav_noini.npy"
    # ini = "D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\f_simul\\f_simul_ini\\fited_behav_ini.npy"
    # guardar = "D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\anlzr\\625\\"

    # analy_behav_by_dims(625, 215, "D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\f_simul\\f_simul_ini\\",
    #                     # dim_arch=ini,
    #                     gaurdar= "D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\f_simul\\f_simul_ini\\")

    # counted_all_behaviors = gen_counted_behavior(ini)

    # egr = analy_by_file('morris', líms_paráms, mapa_paráms, mstr_mor, dim=214,
    #                     simul_arch={'arch_simular': direc, 'num_samples': 624}, tipo_egr='superposition',
    #                     var_egr='mds_Watertable depth Tinamit',
    #                     f_simul_arch={
    #                         'arch': "D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\f_simul\\f_simul_ini\\f_simul",
    #                         'num_sample': 625,
    #                         'counted_behaviors':
    #                             "D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\f_simul\\f_simul_ini\\counted_all_behaviors_ini.npy"})
    #
    # np.save(guardar + 'mor_625_spp_ini', egr)

    '''
    Maping
    '''
    from tinamit.Calib.ej.sens_análisis import map_sens, verif_sens
    from collections import Counter

    paso_data = np.load("D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\anlzr\\625\\mor_625_paso.npy").tolist()
    pasos = verif_sens('morris', list(paso_data.keys())[0], paso_data, mapa_paráms, p_soil_class, si='mu_star')['morris'][
        list(paso_data.keys())[0]]['mds_Watertable depth Tinamit']  # 9prms * 215polys

    # mean_data = np.load("D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\anlzr\\625\\mor_625_promedio.npy").tolist()
    # means = verif_sens('morris', list(mean_data.keys())[0], mean_data, mapa_paráms, p_soil_class, si='mu_star')['morris'][
    #     list(mean_data.keys())[0]]['mds_Watertable depth Tinamit']
    #
    # behav_data = np.load(
    #     "D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\anlzr\\625\\mor_625_spp_no_ini.npy").tolist()
    # behaviors = verif_sens('morris', list(behav_data.keys())[0], behav_data, mapa_paráms, p_soil_class, si='mu_star')['morris'][
    #     list(behav_data.keys())[0]]['mds_Watertable depth Tinamit']
    #
    # # paso
    # # for prm, paso in pasos.items():
    # #     map_sens(gen_geog(), 'Morris', list(paso_data.keys())[0], prm,
    # #              paso, 0.1, ids=[str(i) for i in range(1, 216)],
    # #                               path="D:\Thesis\pythonProject\localuse\Dt\Mor\map\paso\\")
    #
    # # mean
    # # for prmm, m_aray in means.items():
    # #     map_sens(gen_geog(), 'Morris', list(mean_data.keys())[0], prmm,
    # #              m_aray, 0.1, ids=[str(i) for i in range(1, 216)],
    # #              path="D:\Thesis\pythonProject\localuse\Dt\Mor\map\prom\\")
    #
    # # for spp
    # # for patt, b_g in behaviors.items():
    # #     alpha = gen_alpha(no_ini, patt)  # ini/ no_ini
    # #     if Counter(alpha)[0] == 215:
    # #         alpha = np.zeros([215])
    # #     bpp_prm = b_g['bp_params']
    # #     gof_prm = b_g['gof']
    # #     for prm, bpprm in bpp_prm.items():
    # #         if prm == 'Ficticia':
    # #             alpha = np.zeros([215])
    # #         map_sens(gen_geog(), 'Morris', list(behav_data.keys())[0], prm,
    # #                  bpprm, 0.1, behav=patt, ids=[str(i) for i in range(1, 216)], alpha=alpha,
    # #                  path="D:\Thesis\pythonProject\localuse\Dt\Mor\map\\no_ini\\spp\\")  # non_ini
    # #
    # # # for test
    # # patt = 'linear'
    # # b_g = behaviors[patt]
    # # alpha = 1  # ini/ no_ini
    # # bpp_prm = b_g['bp_params']
    # # gof_prm = b_g['gof']
    # # for prm, bpprm in bpp_prm.items():
    # #     if prm == 'Ficticia':
    # #         alpha = np.zeros([215])
    # #     map_sens(gen_geog(), 'Morris', list(behav_data.keys())[0], prm,
    # #              bpprm, 0.1, behav=patt, ids=[str(i) for i in range(1, 216)], alpha=alpha,
    # #              path="D:\Thesis\pythonProject\localuse\Dt\Mor\map\\no_ini\\spp\\linear\\")
    #
    # # final plot
    # archivo = "D:\Thesis\pythonProject\localuse\Dt\Mor\map\\final_plot\\"
    #
    # col_labels = ['S_0', 'S_5', 'S_10', 'S_15', 'S_20', 'Mean']
    #
    # col_labels.extend([f"{behav}_{bpp}" for behav in behaviors for bpp in behaviors[behav]['bp_params']['Kaq']])
    # col_labels.extend([f"{behav}_gof" for behav in behaviors])
    # sig_l = [f'n_{l+1}' for l in range(6)]
    # sig_l.extend([f'b_{l+1}' for l in range(len(col_labels))])
    #
    # db_l = [f's_{l}' for l in range(20)]
    #
    # col = col_labels.copy()
    # col[:6] = sig_l[:6]
    # sl = 0
    # dl = 0
    # for j in col[6:]:
    #     if j[:3] == 'spp':
    #         col[col.index(j)] = db_l[dl]
    #         dl += 1
    #     elif col.index(j) < len(col):
    #         col[col.index(j)] = sig_l[sl + 6]
    #         sl += 1
    #
    # row_labels = list(pasos)
    # for i in range(215):
    #     data = np.empty([len(row_labels), len(col_labels)])
    #     # paso
    #     ps = [0, 5, 10, 15, 20]
    #     for prmp, d_paso in pasos.items():
    #         for p in ps:
    #             data[list(pasos).index(prmp), ps.index(p)] = d_paso[f'paso_{p}'][i]
    #
    #     # mean
    #     for prmm, m_aray in means.items():
    #         data[list(pasos).index(prmm), col_labels.index('Mean')] = m_aray[i]
    #
    #     # behavior
    #     for patt, d_bg in behaviors.items():
    #         alpha = gen_alpha(no_ini, patt)
    #         for pbpp, bpp in d_bg['bp_params'].items():
    #             if Counter(alpha)[0] == 215 or pbpp == 'Ficticia':
    #                 alpha = np.zeros([215])
    #             for bppm, va in bpp.items():
    #                 if alpha[i] == 0 and patt != 'linear':
    #                     data[list(pasos).index(pbpp), col_labels.index(f'{patt}_{bppm}')] = 0
    #                 else:
    #                     data[list(pasos).index(pbpp), col_labels.index(f'{patt}_{bppm}')] = va[i]
    #         for paic, aic in d_bg['gof'].items():
    #             if alpha[i] == 0 and patt != 'linear':
    #                 data[list(pasos).index(paic), col_labels.index(f'{patt}_gof')] = 0
    #             else:
    #                 data[list(pasos).index(paic), col_labels.index(f'{patt}_gof')] = aic['aic'][i]
    #
    #     map_rank(row_labels=row_labels, col_labels=col, data=np.round(data, 2),
    #              title='Morris Sensitivity Ranking Results', y_label='Parameters',
    #              archivo=archivo + f'poly{i+1}', fst_cut=0.1, snd_cut=10, maxi=np.round(data, 2).max(),
    #              cbarlabel="Sensitivity Index", cmap="magma_r")
    #
    #     print(f'finish the {i}-th poly, yeah!')

    # data = np.empty([len(row_labels), len(col_labels)])
    # # paso
    # ps = [0, 5, 10, 15, 20]
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
    #                 data[list(pasos).index(pbpp), col_labels.index(f'{patt}_{bppm}')] = max(va)
    #     for paic, aic in d_bg['gof'].items():
    #             data[list(pasos).index(paic), col_labels.index(f'{patt}_gof')] = max(aic['aic'])
    #
    # map_rank(row_labels=row_labels, col_labels=col, data=np.round(data, 2),
    #          title='Morris Sensitivity Ranking Results', y_label='Parameters',
    #          archivo=archivo + f'all_poly', fst_cut=0.1, snd_cut=10, maxi=np.round(data, 2).max(),
    #          cbarlabel="Sensitivity Index", cmap="magma_r")
