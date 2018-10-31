from tinamit.Análisis.Sens.anlzr import analy_by_file, carg_simul_dt, behav_proc_from_file, anlzr_simul
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
    #'Policy RH' = 1, Fw = 1, Policy Irrigation improvement = 1, Policy Canal lining=1, Capacity per tubewell =(100.8, 201.6),
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
    direc = os.path.join("D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\simular\\corrected_Mor")
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
    # guardar = os.path.join("D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\anlzr\\625\\mor_newbf_paso")
    # mstr_mor = os.path.join('D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\sampled_data\\muestra_morris_625_corrected_bf.json')
    # egr = analy_by_file('morris', líms_paráms, mapa_paráms, mstr_mor,
    #                     simul_arch={'arch_simular': direc, 'num_samples': 625}, tipo_egr='paso_tiempo',
    #                     var_egr='mds_Watertable depth Tinamit')
    #                     # f_simul_arch= {'arch': "D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\f_simul\corrected_bf\\new_spp\\new_f_simul_sppf_simul",
    #                     #                'num_sample': 625,
    #                     #                'counted_behaviors':
    #                     #                    "D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\f_simul\corrected_bf\counted_all\\counted_all_behav.npy"})
    #
    # np.save(guardar, egr)

    # behav_proc_from_file(simul_arch={'arch_simular': direc, 'num_samples': 625}, tipo_egr='superposition', dim=214,
    #                     var_egr='mds_Watertable depth Tinamit', guardar=guardar)

    '''
    post_processing Anlzr 
    '''
    from tinamit.Calib.ej.sens_análisis import verif_sens
    from tinamit.Calib.ej.soil_class import p_soil_class
    # egr = np.load("D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\anlzr\\625\\mor_625_forma.npy").tolist()
    # egr = np.load("D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\anlzr\\625\\mor_625_promedio.npy").tolist()
    # simulation_data = np.load("D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\anlzr\\625\\mor_625_paso.npy").tolist()
    # final_sens = verif_sens('morris', 'promedio', egr, mapa_paráms, p_soil_class)

    '''
    Maping
    '''
    from tinamit.Calib.ej.sens_análisis import map_sens, verif_sens

    simulation_data = np.load("D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\anlzr\\625\\mor_newbf_paso.npy").tolist()
    final_sens = verif_sens('morris', list(simulation_data.keys())[0], simulation_data, mapa_paráms, p_soil_class)
    pasos = final_sens['morris'][list(simulation_data.keys())[0]]['mds_Watertable depth Tinamit']
    for prm, paso in pasos.items():
        map_sens(gen_geog(), 'morris', list(simulation_data.keys())[0], prm,
                 paso, 0.1,
                 "D:\Thesis\pythonProject\localuse\Dt\Mor\map\\")
            # "C:\\Users\\gis_user\Downloads\\azhar shared\\azhar_plot\\paso_0_new222", ids=range(1, 216))

    # for spp
    # for patt, b_g in pasos.items():
    #     bpp_prm = b_g['bp_params']
    #     gof_prm = b_g['gof']
        # for prm, bpprm in bpp_prm.items():
            # map_sens(gen_geog(), 'morris', list(simulation_data.keys())[0], prm,
            #          bpprm, 0.1, behav=patt,
            #          path="D:\Thesis\pythonProject\localuse\Dt\Mor\map\spp_1\\bpp\\")

        # for prm, gof in gof_prm.items():
        #     map_sens(gen_geog(), 'morris', list(simulation_data.keys())[0], prm,
        #              gof, 0.1, behav=patt,
        #              path="D:\Thesis\pythonProject\localuse\Dt\Mor\map\\spp_1\\aic\\")

    # FOR AZHAR
    #D:\Thesis\pythonProject\localuse\Dt\Mor\mor_new_input  #D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\simular\\625_mor\\

    # simulation_data, var_egr = carg_simul_dt(os.path.abspath('D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\simular\\625_mor\\'), 1,
    #                   var_egr='mds_Soil salinity Tinamit CropA')
    # map_sens(gen_geog(), 'morris', 'paso_0', 'Soil salinity',
    #          simulation_data['100'][var_egr].values, 0.1,
    #          # "D:\Thesis\pythonProject\localuse\Dt\Mor\map\\paso_")
    #     "C:\\Users\\gis_user\Downloads\\azhar shared\\azhar_plot\\paso_0", ids=range(1, 216))


