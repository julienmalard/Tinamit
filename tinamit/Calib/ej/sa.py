from tinamit.Análisis.Sens.corridas import *
from tinamit.Calib.ej.info_paráms import mapa_paráms, líms_paráms

from tinamit.Conectado import Conectado
from tinamit.Ejemplos.en.Ejemplo_SAHYSMOD.SAHYSMOD import Envoltura
from tinamit.Análisis.Sens.anlzr import anlzr_sens, analy_by_file


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

devolver = ['Watertable depth Tinamit']

# %% Buchiana 1
# %% Farida 2
# %% Jhang 3
# %% Chuharkana 4

if __name__ == "__main__":
    from tinamit.Calib.ej.muestrear import mstr, archivo_muestrea


    # direc = os.path.join(os.path.split(__file__)[0], "Morris_sim_")
    direc = os.path.join("D:\Thesis\pythonProject\localuse\Dt\Mor\simular")
    guardar = os.path.join("D:\Thesis\pythonProject\localuse\Dt\Mor\\anlzr\\anlzr_new_logístico")
    # direc = os.path.join("D:\Thesis\pythonProject\localuse\Dt\Fast\simular")
    # guardar = os.path.join("D:\Thesis\pythonProject\localuse\Dt\Fast\\anlzr\\anlzr_new")

    #direc = os.path.join("D:\Thesis\pythonProject\localuse\Dt\Fast\simular")
    #guardar = os.path.join("D:\Thesis\pythonProject\localuse\Dt\Fast\\anlzr\\anlzr")

    # simul_sens_por_grupo(
    #     gen_mod(), t_final=5, mstr_paráms=mstr, mapa_paráms=mapa_paráms, var_egr=devolver,
    #     tmñ_grupos=9, í_grupos=[2, 5], paralelo=True, guardar=direc
    # )

    # simul_faltan(
    #     gen_mod(), arch_mstr=archivo_muestrea, mapa_paráms=mapa_paráms, var_egr=devolver, direc=direc,
    #     t_final=10, índices_mstrs=None, paralelo=True
    # )

    # simul_sens(
    #     gen_mod(), mstr_paráms=mstr, mapa_paráms=mapa_paráms, var_egr=devolver, t_final=3, guardar=direc,
    #     índices_mstrs=None, paralelo=True
    # )

    # mstr_paráms = format_mstr(cargar_mstr_paráms(archivo_muestrea), problema['names']) #这里不行 参数格式需要是625＊24

    # anlzr_sens(archivo_muestrea, "morris", líms_paráms, mapa_paráms, direc, 625, guardar, var_egr='mds_Watertable depth Tinamit',
    #            tipo_egr='linear')

    # anlzr_sens(archivo_muestrea, "morris", problema_arch, direc, 625, guardar, var_egr='mds_Watertable depth Tinamit',
    #            cal_raw='paso_tiempo')

    res = analy_by_file('morris',líms_paráms=líms_paráms, mapa_paráms=mapa_paráms, mstr_path=archivo_muestrea,
                  simulation_path={'arch_simular': direc, 'num_samples': 625}, t_final=10, var_egr=['mds_Watertable depth Tinamit'],
                  tipo_egr='logístico')

    guardar_json(res, guardar)

    # Draw maps
    # modelo.dibujar_mapa(geog=Rechna_Doab, corrida=name, var='Watertable depth Tinamit', directorio='Maps')