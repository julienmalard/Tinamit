from tinamit.Análisis.Sens.corridas import *
from tinamit.Calib.ej.info_paráms import mapa_paráms, líms_paráms
from tinamit.Calib.ej.soil_class import p_soil_class

from tinamit.Calib.ej.sens_análisis import analy_behav_by_dims
from tinamit.Conectado import Conectado
from tinamit.Ejemplos.en.Ejemplo_SAHYSMOD.SAHYSMOD import Envoltura
from tinamit.Análisis.Sens.anlzr import anlzr_sens, analy_by_file, carg_simul_dt, anlzr_simul
from tinamit.Geog import Geografía
import multiprocessing as mp
import time


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
    modelo.conectar(var_mds='Fw', mds_fuente=True, var_bf='Fw - Fraction well water to irrigation')  ##0 - 0.8
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
    post analysis 
    '''
    from tinamit.Calib.ej.sens_análisis import verif_sens, gen_counted_behavior
    from tinamit.Calib.ej.soil_class import p_soil_class

    '''
    map
    '''
    from tinamit.Calib.ej.sens_análisis import map_sens, verif_sens, gen_alpha
    from collections import Counter

    paso_data = np.load("D:\Gaby\Tinamit\Dt\Fast\\anlzr\egr_paso\\").tolist()
    pasos = \
        verif_sens('fast', list(paso_data.keys())[0], mapa_paráms, p_soil_class, egr_arch=paso_data, si='Si', dim=215)
    ['morris'][list(paso_data.keys())[0]]['mds_Watertable depth Tinamit']  # 9prms * 215polys

    mean_data = np.load("D:\Gaby\Tinamit\Dt\Fast\\anlzr\egr_mean\\").tolist()
    means = \
        verif_sens('fast', list(paso_data.keys())[0], mapa_paráms, p_soil_class, egr_arch=mean_data, si='Si', dim=215)
    ['morris'][list(paso_data.keys())[0]]['mds_Watertable depth Tinamit']

    behav_data = np.load("D:\Gaby\Tinamit\Dt\Fast\\anlzr\egr_behav\\").tolist()
    behaviors = \
        verif_sens('fast', list(paso_data.keys())[0], mapa_paráms, p_soil_class, egr_arch=behav_data, si='Si', dim=215)
    ['morris'][list(paso_data.keys())[0]]['mds_Watertable depth Tinamit']

    # paso
    for prm, paso in pasos.items():
        map_sens(gen_geog(), 'Morris', list(paso_data.keys())[0], prm,
                 paso, 0.01, ids=[str(i) for i in range(1, 216)],
                 path="D:\Gaby\Tinamit\Dt\Fast\map\paso\\")

    # mean
    for prmm, m_aray in means.items():
        map_sens(gen_geog(), 'Morris', list(mean_data.keys())[0], prmm,
                 m_aray, 0.1, ids=[str(i) for i in range(1, 216)],
                 path="D:\Gaby\Tinamit\Dt\Fast\map\mean\\")

    # for spp
    for patt, b_g in behaviors.items():
        alpha = gen_alpha(no_ini, patt)  # ini/ no_ini
        if Counter(alpha)[0] == 215:
            alpha = np.zeros([215])
        bpp_prm = b_g['bp_params']
        gof_prm = b_g['gof']
        for prm, bpprm in bpp_prm.items():
            if prm == 'Ficticia':
                alpha = np.zeros([215])
            map_sens(gen_geog(), 'Morris', list(behav_data.keys())[0], prm,
                     bpprm, 0.1, behav=patt, ids=[str(i) for i in range(1, 216)], alpha=alpha,
                     path="D:\Gaby\Tinamit\Dt\Fast\map\\spp\\")  # non_ini

    # for Linear
    patt = 'linear'
    b_g = behaviors[patt]
    alpha = 1  # ini/ no_ini
    bpp_prm = b_g['bp_params']
    gof_prm = b_g['gof']
    for prm, bpprm in bpp_prm.items():
        # if prm == 'Ficticia':
        #     alpha = np.zeros([215])
        map_sens(gen_geog(), 'Morris', list(behav_data.keys())[0], prm,
                 bpprm, 0.1, behav=patt, ids=[str(i) for i in range(1, 216)], alpha=alpha,
                 path="D:\Gaby\Tinamit\Dt\Fast\map\\spp\\linear\\")