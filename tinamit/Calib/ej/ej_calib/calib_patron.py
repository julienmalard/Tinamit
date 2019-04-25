import numpy as np

from tinamit.Calib.ej.ej_calib.info_calib import sim_dream, guardar_dream, sim_dream_rev, \
    guardar_dream_rev, guardar_dream_nse, sim_dream_nse, sim_dream_nse_rev, guardar_dream_nse_rev
from tinamit.Calib.ej.sens_análisis import gen_mod
from tinamit.Análisis.Sens.muestr import gen_problema
from tinamit.Calib.ej.info_paráms import calib_líms_paráms, calib_mapa_paráms
from tinamit.Calib.ej.cor_patrón import ori_valid, ori_calib

líms_paráms_final = []
líms_paráms_final.append(
    gen_problema(líms_paráms=calib_líms_paráms, mapa_paráms=calib_mapa_paráms, ficticia=False)[1])

mod = gen_mod()

method = ['dream', 'fscabc']

def _calib(bd, tipo_proc, obj_func, guardar, método, guar_sim, egr_spotpy):
    calib_res = mod.calibrar(paráms=list(líms_paráms_final), bd=bd, líms_paráms=calib_líms_paráms,
                             vars_obs='mds_Watertable depth Tinamit', final_líms_paráms=líms_paráms_final[0],
                             mapa_paráms=calib_mapa_paráms, tipo_proc=tipo_proc, obj_func=obj_func,
                             guardar=guardar, método=método, n_iter=500, guar_sim=guar_sim, egr_spotpy=egr_spotpy)
    return calib_res


def _valid(bd, tipo_proc, obj_func, guardar, valid_sim, n_sim, save_plot, t_sim_gard, sim_eq_obs, lg):
    valid_res = mod.validar(bd=bd, var='mds_Watertable depth Tinamit', tipo_proc=tipo_proc,
                            obj_func=obj_func, guardar=guardar, lg=lg, paralelo=True, valid_sim=valid_sim,
                            n_sim=n_sim, save_plot=save_plot, t_sim_gard=t_sim_gard, sim_eq_obs=sim_eq_obs)
    return valid_res


if __name__ == "__main__":
    for m in method:
        # if m == 'fscabc':
        if m == 'dream':

            _calib(bd=ori_calib, tipo_proc='patrón', obj_func='AIC', guardar=guardar_dream, método=m,
                   guar_sim=sim_dream, egr_spotpy=False)

            _calib(bd=ori_valid, tipo_proc='patrón', obj_func='AIC', guardar=guardar_dream_rev, método=m,
                   guar_sim=sim_dream_rev, egr_spotpy=False)

            _calib(bd=ori_calib, tipo_proc='multidim', obj_func='NSE', guardar=guardar_dream_nse, método=m,
                   guar_sim=sim_dream_nse, egr_spotpy=False)

            _calib(bd=ori_valid, tipo_proc='multidim', obj_func='NSE', guardar=guardar_dream_nse_rev, método=m,
                   guar_sim=sim_dream_nse_rev, egr_spotpy=False)

            # bd, tipo_proc, obj_func, método, guardar, guar_sim, egr_spotpy, n_sim = load_calib_info(
            #     m, 'reverse', t_trend=False, calib=True, rev=True, egr_spotpy=False, obj_func='NSE', tipo_proc='multidim')
            # _calib(bd, tipo_proc, obj_func, guardar, método, guar_sim, egr_spotpy)

            # bd, tipo_proc, obj_func, método, guardar, guar_sim, egr_spotpy, n_sim = load_calib_info(
            #     m, 'original', t_trend=False, calib=True, rev=False, egr_spotpy=False, obj_func='AIC',
            #     tipo_proc='patrón')
            # _calib(bd, tipo_proc, obj_func, guardar, método, guar_sim, egr_spotpy)

            # bd, tipo_proc, obj_func, método, guardar, guar_sim, egr_spotpy, n_sim = load_calib_info(
            #     m, 'reverse', t_trend=False, calib=True, rev=True, egr_spotpy=False, obj_func='AIC',
            #     tipo_proc='patrón')
            # _calib(bd, tipo_proc, obj_func, guardar, método, guar_sim, egr_spotpy)

            # bd, tipo_proc, obj_func, método, guardar, guar_sim, egr_spotpy = load_calib_info(
            #     m, 'nse', t_trend=False, calib=True, rev=True, egr_spotpy=False, obj_func='nse',
            #     tipo_proc='multidim')
            # _calib(bd, tipo_proc, obj_func, guardar, método, guar_sim, egr_spotpy)

            # bd, tipo_proc, obj_func, guardar, método, valid_sim, save_plot, t_sim_gard, sim_eq_obs, n_sim, lg = load_calib_info(
            #     m, 'original', t_trend=True, calib=False, rev=False, egr_spotpy=False, obj_func='aic')
            # _valid(bd, tipo_proc, obj_func, guardar, valid_sim, n_sim, save_plot, t_sim_gard, sim_eq_obs, lg)
            # bd, tipo_proc, obj_func, guardar, método, valid_sim, save_plot, t_sim_gard, sim_eq_obs, n_sim, lg = load_calib_info(
            #     m, 'original', t_trend=False, calib=False, rev=False, egr_spotpy=False, obj_func='barlas')
            # _valid(bd, tipo_proc, obj_func, guardar, valid_sim, n_sim, save_plot, t_sim_gard, sim_eq_obs, lg)

            # bd, guardar, lg, valid_sim, n_sim, t_sim_gard, tipo_proc, obj_func, sim_eq_obs, save_plot = load_calib_info(
            #     m, 'agreement', t_trend=False, calib=False, rev=False, egr_spotpy=False, obj_func='coeffienct of agreement')
            # _valid(bd, tipo_proc, obj_func, guardar, valid_sim, n_sim, save_plot, t_sim_gard, sim_eq_obs, lg)

            # bd, tipo_proc, obj_func, guardar, método, valid_sim, save_plot, t_sim_gard, sim_eq_obs, n_sim, lg = load_calib_info(
            #     m, 'reverse', t_trend=False, calib=False, rev=True, egr_spotpy=False, obj_func='aic')
            # _valid(bd, tipo_proc, obj_func, guardar, valid_sim, n_sim, save_plot, t_sim_gard, sim_eq_obs, lg)

            # bd, tipo_proc, obj_func, guardar, método, valid_sim, save_plot, t_sim_gard, sim_eq_obs, n_sim, lg = load_calib_info(
            #     m, 'reverse', t_trend=False, calib=False, rev=True, egr_spotpy=False, obj_func='barlas')
            # _valid(bd, tipo_proc, obj_func, guardar, valid_sim, n_sim, save_plot, t_sim_gard, sim_eq_obs, lg)

            # bd, guardar, lg, valid_sim, n_sim, t_sim_gard, tipo_proc, obj_func, sim_eq_obs, save_plot = load_calib_info(
            #     m, 'agreement', t_trend=False, calib=False, rev=True, egr_spotpy=False, obj_func='coeffienct of agreement')
            # _valid(bd, tipo_proc, obj_func, guardar, valid_sim, n_sim, save_plot, t_sim_gard, sim_eq_obs, lg)
# if __name__ == "__main__":
#     for m in method:
#         if m == 'fscabc':
# lg = np.load(guardar_nse + f'calib-{m}.npy').tolist()
# mod.validar(bd=ori_valid, var='mds_Watertable depth Tinamit', tipo_proc='multidim',
#             obj_func='NSE',
#             guardar=guardar_nse + f'nse-{m}', lg=lg, paralelo=True, valid_sim=nse_sim, n_sim=624,
#             save_plot=plot + 'nse\\')

# lg = np.load(guardar + f'calib_cluster.npy').tolist()
#             mod.validar(bd=cluster_valid, var='mds_Watertable depth Tinamit', tipo_proc='patrón',
#                         obj_func='multi_behavior_tests',
#                         guardar=guardar + f'cluster7-{m}', lg=lg, paralelo=True, valid_sim=fscabc_sim, n_sim=144,
#                         save_plot=plot+'cluster7\\', t_sim_gard=t_sim_gard_cluster7, sim_eq_obs=False)

#             mod.validar(bd=cluster_valid, var='mds_Watertable depth Tinamit', tipo_proc='patrón',
#                         obj_func='kappa',
#                         guardar=guardar + f'cluster21-{m}', lg=lg, paralelo=True, valid_sim=fscabc_sim, n_sim=144,
#                         save_plot=plot + 'cluster21\\', t_sim_gard=t_trend_cluster21, sim_eq_obs=False)
# sim_eq_obs is False used as all generated t_sim behaviour not need to be the same as obs.
# sim_eq_obs is True only save those detected pattern is the same as obs

# lg = lg_original
# mod.validar(bd=ori_valid, var='mds_Watertable depth Tinamit', tipo_proc='patrón',
#             obj_func='coeffienct of agreement',
#             guardar=guardar_original + f'agreemt-{m}', lg=lg, paralelo=True,
#             valid_sim=fscabc_sim, n_sim=144, t_sim_gard=t_sim_kappa_ori, sim_eq_obs=False)

# mod.validar(bd=ori_valid, var='mds_Watertable depth Tinamit', tipo_proc='patrón',
#             obj_func='multi_behavior_tests',
#             guardar=guardar_original + f'original7-{m}', lg=lg, paralelo=True,
#             valid_sim=fscabc_sim,
#             n_sim=144,
#             save_plot=plot + 'abc\\7\\', t_sim_gard=t_sim_gard_original7, sim_eq_obs=False)
#
# mod.validar(bd=ori_valid, var='mds_Watertable depth Tinamit', tipo_proc='patrón',
#             obj_func='kappa',
#             guardar=guardar_original + f'origina21-{m}', lg=lg, paralelo=True,
#             valid_sim=fscabc_sim,
#             n_sim=144,
#             save_plot=plot + 'abc\\21\\', t_sim_gard=t_sim_gard_original21, sim_eq_obs=False)

# lg = lg_reverse
# mod.validar(bd=ori_calib, var='mds_Watertable depth Tinamit', tipo_proc='patrón',
#             obj_func='coeffienct of agreement',
#             guardar=guardar_reverse + f'rev_agr-{m}', lg=lg, paralelo=True,
#             valid_sim=reverse_sim, n_sim=624, t_sim_gard=t_sim_kappa, sim_eq_obs=False)

# mod.validar(bd=ori_calib, var='mds_Watertable depth Tinamit', tipo_proc='patrón',
#             obj_func='multi_behavior_tests',
#             guardar=guardar_reverse + f'reverse17-{m}', lg=lg, paralelo=True, valid_sim=reverse_sim,
#             n_sim=624,
#             save_plot=plot + 'reverse\\7\\', t_sim_gard=t_sim_gard_reverse7, sim_eq_obs=False)
#
# mod.validar(bd=ori_calib, var='mds_Watertable depth Tinamit', tipo_proc='patrón',
#             obj_func='kappa',
#             guardar=guardar_reverse + f'reverse21-{m}', lg=lg, paralelo=True, valid_sim=reverse_sim,
#             n_sim=624,
#             save_plot=plot + 'reverse\\21\\', t_sim_gard=t_sim_gard_reverse21, sim_eq_obs=False)
