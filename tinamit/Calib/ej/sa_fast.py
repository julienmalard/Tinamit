from tinamit.Análisis.Sens.corridas import *
from tinamit.Calib.ej.info_analr import *
from tinamit.Calib.ej.info_paráms import mapa_paráms, líms_paráms
from tinamit.Calib.ej.soil_class import p_soil_class

from tinamit.Calib.ej.sens_análisis import analy_behav_by_dims, map_rank, gen_rank_map
from tinamit.Conectado import Conectado
from tinamit.Ejemplos.en.Ejemplo_SAHYSMOD.SAHYSMOD import Envoltura
from tinamit.Análisis.Sens.anlzr import anlzr_sens, analy_by_file, carg_simul_dt, anlzr_simul
from tinamit.Geog import Geografía
import multiprocessing as mp
import time


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
    # # After finish the f_simul simulation SAlib for superposition (the best behavior for each poly)
    from tinamit.Calib.ej.sens_análisis import analy_behav_by_dims, map_rank

    f_simul_arch = 'D:\Thesis\pythonProject\localuse\Dt\Fast\\f_simul\\'
    fited_behav = "D:\Thesis\pythonProject\localuse\Dt\Fast\post_f_simul\\"

    # analy_behav_by_dims('fast', 120000, 215, f_simul_arch, gaurdar=fited_behav, dim_arch=fited_behav)
    #
    # gen_counted_behavior(fited_behav + 'fited_behav.npy', gaurdar=fited_behav)
    #
    # egr = anlzr_simul('fast', líms_paráms, mstr_fa, mapa_paráms, ficticia=True, var_egr='mds_Watertable depth Tinamit',
    #                   dim=215, tipo_egr="superposition",
    #                   f_simul_arch={
    #                       'arch': "D:\Thesis\pythonProject\localuse\Dt\Fast\\f_simul",
    #                       'num_sample': 120000,
    #                       'counted_behaviors': fited_behav + 'counted_all_behaviors.npy'}
    #                   )

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
    from tinamit.Calib.ej.sens_análisis import map_sens, verif_sens, gen_alpha, gen_counted_behavior
    from collections import Counter

    paso_data = np.load("D:\Gaby\Tinamit\Dt\Fast\\anlzr\egr_paso\\egr-0.npy").tolist()
    paso_arch = "D:\Gaby\Tinamit\Dt\Fast\\anlzr\egr_paso\\"
    pasos = \
        verif_sens('fast', list(paso_data.keys())[0], mapa_paráms, p_soil_class, egr_arch=paso_arch, si='Si', dim=215)[
            'fast'][list(paso_data.keys())[0]]['mds_Watertable depth Tinamit']  # 9prms * 215polys

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

    gen_rank_map(rank_arch_fast, 'Fast', 0.01, 1, 'total_poly')
