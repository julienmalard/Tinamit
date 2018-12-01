from tinamit.Análisis.Sens.corridas import *
from tinamit.Calib.ej.info_paráms import mapa_paráms, líms_paráms
from tinamit.Calib.ej.soil_class import p_soil_class

from tinamit.Conectado import Conectado
from tinamit.Ejemplos.en.Ejemplo_SAHYSMOD.SAHYSMOD import Envoltura
from tinamit.Análisis.Sens.anlzr import anlzr_sens, analy_by_file, carg_simul_dt, anlzr_simul
from tinamit.Geog import Geografía


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

if __name__ == "__main__":
    import os
    import numpy as np

    direc = os.path.join("D:\Thesis\pythonProject\localuse\Dt\Fast\simular")

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
    # For paso/mean val

    mstr_fa = os.path.join('D:\Thesis\pythonProject\localuse\Dt\Fast\sampled data\\muestra_fast_23params.json')
    # for dim in range(215):
        # egr = analy_by_file('fast', líms_paráms, mapa_paráms, mstr_fa,
        #                     simul_arch={'arch_simular': direc, 'num_samples': 120000}, tipo_egr='superposition',
        #                     var_egr='mds_Watertable depth Tinamit', dim=dim,
        #                     f_simul_arch={
        #                         'arch': "D:\Thesis\pythonProject\localuse\Dt\Fast\\f_simul", 'num_sample': 120000,
        #                         'counted_behaviors':
        #                             "D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\f_simul\corrected_bf\counted_all\\counted_all_behav.npy"})

    # After finish the f_simul simulation
    from tinamit.Calib.ej.sens_análisis import analy_behav_by_dims

    f_simul_arch = 'D:\Thesis\pythonProject\localuse\Dt\Fast\\f_simul'
    fited_behav = ''
    counted_all_beahviors = "D:\Thesis\pythonProject\localuse\Dt\Fast\\f_simul\\non_ini\counted_all"
    analy_behav_by_dims(120000, 215, f_simul_arch, gaurdar=counted_all_beahviors)

    # egr = anlzr_simul('fast', líms_paráms, mstr_fa, mapa_paráms,
    #                   ficticia=True, var_egr='mds_Watertable depth Tinamit', dim=dim, tipo_egr="superposition",
    #                   f_simul_arch={
    #                       'arch': "D:\Thesis\pythonProject\localuse\Dt\Fast\\f_simul", 'num_sample': 120000,
    #                       'counted_behaviors': counted_all_beahviors+ 'counted_all_behaviors.npy'
    #                           }
    #                   )

    '''
    post analysis 
    '''
    from tinamit.Calib.ej.sens_análisis import verif_sens, gen_counted_behavior
    from tinamit.Calib.ej.soil_class import p_soil_class

    '''
    map
    '''
    from tinamit.Calib.ej.sens_análisis import map_sens, verif_sens

    # simulation_data, var_egr = carg_simul_dt(os.path.abspath('D:\Thesis\pythonProject\localuse\Dt\Fast\simular\\'), 1,
    #                   var_egr='mds_Soil salinity Tinamit CropA')
    #
    #
    # map_sens(gen_geog(), 'fast', 'paso_0', 'SS',
    #          simulation_data['1000'][var_egr].values, 0.1,
    #          "D:\Thesis\pythonProject\localuse\Dt\Fast\map\\paso_")
