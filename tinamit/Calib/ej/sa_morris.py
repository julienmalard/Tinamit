from tinamit.Análisis.Sens.anlzr import analy_by_file, behav_proc_from_file
from tinamit.Análisis.Sens.corridas import simul_sens
from tinamit.Calib.ej.info_analr import *
from tinamit.Calib.ej.info_paráms import mapa_paráms, líms_paráms
from tinamit.Calib.ej.sens_análisis import gen_row_col, gen_geog_map, gen_rank_map, _gen_poly_dt_for_geog, \
    _read_dt_4_map

if __name__ == "__main__":
    import numpy as np

    '''
    Simul
    '''
    # simul_sens(
    #     gen_mod(), mstr_paráms=mstr_morris, mapa_paráms=mapa_paráms, var_egr=devolver, t_final=20, guardar=simu_guar_arch,
    #     índices_mstrs=None, paralelo=True
    # )

    '''
    Anlzr
    '''
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

    behav_proc_from_file(simul_arch={'arch_simular': simu_guar_arch_mor, 'num_samples': 625}, tipo_egr='superposition', dim=214,
                         var_egr='mds_Watertable depth Tinamit', guardar=behav_const_dt)

    '''
    post_processing Anlzr 
    '''

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
    # _gen_poly_dt_for_geog('morris', geog_simul_pct_mor2, geog_simul_pct_mor)
    # gen_geog_map(geog_save_mor, measure='behavior_param', method='Morris', param=None,
    #              fst_cut=0.1, snd_cut=8)

    # final plot
    # gen_rank_map(rank_arch_mor, 'Morris', 0.1, 8, 'num_poly_rank') #, cluster=True, cls=6)

    # _read_dt_4_map('Morris')