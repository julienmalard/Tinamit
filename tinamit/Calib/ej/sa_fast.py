from tinamit.Análisis.Sens.corridas import *
from tinamit.Calib.ej.info_analr import *
from tinamit.Calib.ej.info_paráms import mapa_paráms, líms_paráms
from tinamit.Calib.ej.soil_class import p_soil_class

from tinamit.Calib.ej.sens_análisis import analy_behav_by_dims, map_rank, gen_rank_map, _gen_poly_dt_for_geog, \
    gen_geog_map, _read_dt_4_map
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

    #
    # for result in results:
    #     re = result.get()
    #     np.save(gaurdar + f'egr-{re[0]}', re[1])

    # _gen_poly_dt_for_geog('fast', fit_beh_poly_fast, geog_simul_pct_fast, 120000)
    # gen_geog_map(geog_simul_pct_fast, measure='behavior_param', method='Fast', param=None,
    #              fst_cut=0.01, snd_cut=1)

    '''
    map
    '''
    # simulation_data, var_egr = carg_simul_dt(os.path.abspath('D:\Thesis\pythonProject\localuse\Dt\Fast\simular\\'), 1,
    #                   var_egr='mds_Soil salinity Tinamit CropA')
    #
    #
    # map_sens(gen_geog(), 'fast', 'paso_0', 'SS',
    #          simulation_data['1000'][var_egr].values, 0.1,
    #          "D:\Thesis\pythonProject\localuse\Dt\Fast\map\\paso_")

    gen_rank_map(geog_save_fast, 'Fast', 0.01, 1, 'num_poly_rank', cluster=True, cls=6)
    # _read_dt_4_map('Fast')