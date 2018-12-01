from tinamit.Análisis.Sens.corridas import *
from tinamit.Calib.ej.info_paráms import mapa_paráms, líms_paráms

from tinamit.Conectado import Conectado
from tinamit.Ejemplos.en.Ejemplo_SAHYSMOD.SAHYSMOD import Envoltura
from tinamit.Análisis.Sens.anlzr import anlzr_sens, analy_by_file, behav_proc_from_file


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
    #'Policy RH' = 1, Fw = 1, Policy Irrigation improvement = 1, Policy Canal lining=1, Capacity per tubewell =(100.8, 201.6),
    return modelo

devolver = ['Watertable depth Tinamit', 'Soil salinity Tinamit CropA']

# %% Buchiana 1
# %% Farida 2
# %% Jhang 3
# %% Chuharkana 4

if __name__ == "__main__":
    # from tinamit.Calib.ej.muestrear import mstr_morris
    direc = os.path.join("D:\Gaby\Tinamit\Dt\Mor\simular\\625_mor")
    guardar = os.path.join("D:\Gaby\Tinamit\Dt\Mor\\f_simul\\f_simul\\")
    f_simul = os.path.join("D:\Gaby\Tinamit\Dt\Mor\\f_simul\\f_simul.npy")

    '''
       Simulation
    '''
    # simul_sens(
    #     gen_mod(), mstr_paráms=mstr_morris, mapa_paráms=mapa_paráms, var_egr=devolver, t_final=20, guardar=direc,
    #     índices_mstrs=None, paralelo=True
    # )


    '''
      Analysis
    '''
    # mstr_mor = os.path.join('D:\Gaby\Tinamit-master\Dt\Mor\sampled_data\\muestra_morris_625.json')
    # egr = analy_by_file('morris', líms_paráms, mapa_paráms, mstr_mor,
    #                     simul_arch={'arch_simular': direc, 'num_samples': 625}, tipo_egr='superposition',
    #                     f_simul_arch="D:\Gaby\Tinamit-master\Dt\Mor\\f_simul\\f_simul_spp_625.npy")
    #
    # np.save(guardar, egr)

    behav_proc_from_file(simul_arch={'arch_simular': direc, 'num_samples': 625}, tipo_egr='superposition', dim=214,
                         var_egr='mds_Watertable depth Tinamit', guardar=guardar)



