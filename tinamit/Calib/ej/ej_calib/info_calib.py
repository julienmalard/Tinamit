import numpy as np
from tinamit.Calib.ej.cor_patrón import ori_valid, ori_calib

def load_calib_info(method, type_sim, t_trend=True, calib=False, rev=False, egr_spotpy=False, obj_func=None):
    guardar_original = "D:\Thesis\pythonProject\localuse\Dt\Calib\\cali_res\\original\\"
    guardar_reverse = "D:\Thesis\pythonProject\localuse\Dt\Calib\\cali_res\\reverse\\"
    sim_original = "D:\Thesis\pythonProject\localuse\Dt\Calib\\simular\\original\\"
    sim_rev = "D:\Thesis\pythonProject\localuse\Dt\Calib\\simular\\reverse\\"

    if not calib:
        lg_original = np.load(guardar_original + f'calib_pat-fscabc.npy').tolist()
        lg_reverse = np.load(guardar_reverse + f'calib_reverse-fscabc.npy').tolist()

    if t_trend:
        t_trend_original21 = guardar_original + "origina21-fscabc-trend.npy"
        t_trend_reverse21 = guardar_reverse + "reverse21-fscabc-trend.npy"
    if type_sim == 'nse':
        guardar_nse = "D:\Thesis\pythonProject\localuse\Dt\Calib\\cali_res\\nse\\"
        guardar_nse_rev = "D:\Thesis\pythonProject\localuse\Dt\Calib\\cali_res\\nse_rev\\"
        sim_nse = "D:\Thesis\pythonProject\localuse\Dt\Calib\\simular\\nse\\"
        sim_nse_rev = "D:\Thesis\pythonProject\localuse\Dt\Calib\\simular\\nse_rev\\"
        if not calib:
            lg_nse = np.load(guardar_nse + f'calib-fscabc.npy').tolist()
            return ori_valid,'multidim', 'NSE', guardar_nse + f'nse-{m}', lg_nse, 624 # bd, tipo_proc, obj_func, guardar, lg, n_sim, valid_sim,
        else:
            tipo_proc = 'multidim'
            obj_func = 'NSE',
            método = method
            egr_spotpy = False
            if rev:
                bd = ori_valid
                guardar = guardar_nse_rev + f'calib-{método}'
                guar_sim = sim_nse_rev
            else:
                bd = ori_calib
                guardar = guardar_nse + f'calib-{método}'
                guar_sim = sim_nse
            return bd, tipo_proc, obj_func, método, guardar, guar_sim, egr_spotpy

    elif type_sim == 'agreement':
        t_sim_agree_ori = {'t_obs': guardar_original + 'linear\\', 't_sim': guardar_original + 'linear\\t_sim',
                           'tipo': 'coeff_linear', 'trend_icc': t_trend_original21,
                           'linear_trend': guardar_original + 'linear\\trend.npy'}

        t_sim_agree_rev = {'t_obs': guardar_reverse + 'linear\\', 't_sim': guardar_reverse + 'linear\\t_sim',
                           'tipo': 'coeff_linear', 'trend_icc': t_trend_reverse21,
                           'linear_trend': guardar_reverse + 'linear\\trend.npy'}
        tipo_proc = 'patrón'
        obj_func = 'coeffienct of agreement'
        sim_eq_obs = False
        save_plot = None
        if rev:
            bd = ori_calib
            guardar = guardar_reverse + f'rev_agreemt-{method}'
            lg = lg_reverse
            valid_sim = sim_rev
            n_sim = 624
            t_sim_gard = t_sim_agree_rev
        else:
            bd = ori_valid
            guardar = guardar_original + f'agreemt-{method}'
            lg = lg_original
            valid_sim = sim_original
            n_sim = 144
            t_sim_gard = t_sim_agree_ori
        return bd, guardar, lg, valid_sim, n_sim, t_sim_gard, tipo_proc, obj_func, sim_eq_obs, save_plot


    elif type_sim == 'original':
        plot = "D:\Thesis\pythonProject\localuse\Dt\Calib\plot\\"
        n_sim = 144
        if calib:
            if egr_spotpy:
                egr_spotpy = egr_spotpy
            else:
                egr_spotpy = False
            bd = ori_calib
            tipo_proc = 'patrón'
            obj_func = 'AIC'
            guardar=guardar_original + f'calib-{method}'
            método= method
            guar_sim= sim_original
            egr_spotpy= egr_spotpy
            return bd, tipo_proc, obj_func, método, guardar, guar_sim, egr_spotpy, n_sim

        else:
            t_sim_gard_original7 = {'t_obs': guardar_original + '7\\t_obs7', 't_sim': guardar_original + '7\\t_sim',
                                   'tipo': 'valid_multi_tests'}
            t_sim_gard_original21 = {'t_obs': guardar_original + '21\\t_obs21', 't_sim': guardar_original + '21\\t_sim',
                                    'tipo': 'valid_others'}
            método = method
            bd = ori_valid
            tipo_proc = 'patrón'
            sim_eq_obs = False
            guar_sim = sim_original
            if obj_func == 'barlas':
                obj_func = 'multi_behavior_tests'
                save_plot = plot + 'original\\7\\'
                guardar = guardar_original + f'original7-{method}'
                t_sim_gard = t_sim_gard_original7
            else:
                obj_func = 'aic'
                save_plot = plot + 'original\\21\\'
                guardar = guardar_original + f'origina21-{method}'
                t_sim_gard = t_sim_gard_original21
            return bd, tipo_proc, obj_func, guardar, método, guar_sim, save_plot, t_sim_gard, sim_eq_obs

    elif type_sim == 'reverse':
        plot = "D:\Thesis\pythonProject\localuse\Dt\Calib\plot\\"
        n_sim = 624
        if calib:
            if egr_spotpy:
                egr_spotpy = egr_spotpy
            else:
                egr_spotpy = False
            bd = ori_valid
            tipo_proc = 'patrón'
            obj_func = 'AIC'
            guardar = guardar_reverse + f'calib-{method}'
            método = method
            guar_sim = sim_rev
            egr_spotpy = egr_spotpy
            return bd, tipo_proc, obj_func, método, guardar, guar_sim, egr_spotpy, n_sim

        else:
            t_sim_gard_reverse7 = {'t_obs': guardar_reverse + '7\\t_obs7', 't_sim': guardar_reverse + '7\\t_sim',
                                   'tipo': 'valid_multi_tests'}
            t_sim_gard_reverse21 = {'t_obs': guardar_reverse + '21\\t_obs21', 't_sim': guardar_reverse + '21\\t_sim',
                                    'tipo': 'valid_others'}
            método = method
            bd = ori_calib
            tipo_proc = 'patrón'
            sim_eq_obs = False
            guar_sim = sim_rev
            if obj_func == 'barlas':
                obj_func = 'multi_behavior_tests'
                save_plot = plot + 'reverse\\7\\'
                guardar = guardar_reverse + f'reverse7-{method}'
                t_sim_gard = t_sim_gard_reverse7
            else:
                obj_func = 'aic'
                save_plot = plot + 'reverse\\21\\'
                guardar = guardar_reverse + f'reverse21-{method}'
                t_sim_gard = t_sim_gard_reverse21
            return bd, tipo_proc, obj_func, guardar, método, guar_sim, save_plot, t_sim_gard, sim_eq_obs, n_sim

    elif type_sim == 'clutering':
        t_trendall = "D:\Thesis\pythonProject\localuse\Dt\Calib\cali_res\\reverse\\t_sim_all\\all\\all-fscabc-trend.npy"


