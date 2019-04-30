import numpy as np

from tinamit.Calib.ej.ej_calib.info_calib import *
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


def _valid(bd, tipo_proc, obj_func, guardar, valid_sim, n_sim, save_plot, lg):
    valid_res = mod.validar(bd=bd, var='mds_Watertable depth Tinamit', tipo_proc=tipo_proc,
                            obj_func=obj_func, guardar=guardar, lg=lg, paralelo=True, valid_sim=valid_sim,
                            n_sim=n_sim, save_plot=save_plot)
    return valid_res


if __name__ == "__main__":
    for m in method:
        # if m == 'fscabc':
        if m == 'dream':

            # _calib(bd=ori_calib, tipo_proc='patrón', obj_func='AIC', guardar=guardar_dream, método=m,
            #        guar_sim=sim_dream, egr_spotpy=False)
            #
            # _calib(bd=ori_valid, tipo_proc='patrón', obj_func='AIC', guardar=guardar_dream_rev, método=m,
            #        guar_sim=sim_dream_rev, egr_spotpy=False)
            #
            # _calib(bd=ori_calib, tipo_proc='multidim', obj_func='NSE', guardar=guardar_dream_nse, método=m,
            #        guar_sim=sim_dream_nse, egr_spotpy=False)
            #
            # _calib(bd=ori_valid, tipo_proc='multidim', obj_func='NSE', guardar=guardar_dream_nse_rev, método=m,
            #        guar_sim=sim_dream_nse_rev, egr_spotpy=False)

        #valid_dream

            # original nse
            # _valid(bd=ori_valid, tipo_proc='multidim', obj_func='NSE', guardar=guardar_dream+'valid_nse', valid_sim=sim_dream_nse,
            #        n_sim=495, save_plot=plot_dream_nse, lg=np.load(guardar_dream+"nse.npy").tolist())

            #rev nse
            # _valid(bd=ori_calib, tipo_proc='multidim', obj_func='NSE', guardar=guardar_dream + 'valid_nse_rev',
            #        valid_sim=sim_dream_nse_rev,
            #        n_sim=495, save_plot=plot_dream_nse_rev, lg=np.load(guardar_dream + "nse_rev.npy").tolist())

            #ori aic
            _valid(bd=ori_valid, tipo_proc='patrón', obj_func='multi_behavior_tests', guardar=guardar_dream + 'valid_aic',
                   valid_sim=sim_dream,
                   n_sim=495, save_plot=plot_dream, lg=np.load(guardar_dream + "dream.npy").tolist())

            #rev aic
            _valid(bd=ori_calib, tipo_proc='patrón', obj_func='multi_behavior_tests',
                   guardar=guardar_dream + 'valid_aic_rev',
                   valid_sim=sim_dream_rev,
                   n_sim=495, save_plot=plot_dream_rev, lg=np.load(guardar_dream + "dream_rev.npy").tolist())
