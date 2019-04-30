import numpy as np
from tinamit.Calib.ej.cor_patrón import ori_valid, ori_calib

guardar_class = "D:\Thesis\pythonProject\localuse\Dt\Calib\cali_res\class\\"
guardar_class_rev = "D:\Thesis\pythonProject\localuse\Dt\Calib\cali_res\class_rev\\"

guardar_original = "D:\Thesis\pythonProject\localuse\Dt\Calib\\cali_res\\original\\"
guardar_reverse = "D:\Thesis\pythonProject\localuse\Dt\Calib\\cali_res\\reverse\\"

guardar_dream = "D:\Thesis\pythonProject\localuse\Dt\Calib\cali_res\dream\\"
guardar_dream_rev = "D:\Thesis\pythonProject\localuse\Dt\Calib\cali_res\dream_rev\\"
guardar_dream_nse = "D:\Thesis\pythonProject\localuse\Dt\Calib\cali_res\dream_nse\\"
guardar_dream_nse_rev = "D:\Thesis\pythonProject\localuse\Dt\Calib\cali_res\dream_nse_rev\\"

plot_dream = "D:\Thesis\pythonProject\localuse\Dt\Calib\plot\dream\\aic\\"
plot_dream_rev = "D:\Thesis\pythonProject\localuse\Dt\Calib\plot\dream\\aic_rev\\"
plot_dream_nse = "D:\Thesis\pythonProject\localuse\Dt\Calib\plot\dream\\nse\\"
plot_dream_nse_rev = "D:\Thesis\pythonProject\localuse\Dt\Calib\plot\dream\\nse_rev\\"

sim_dream = "D:\Thesis\pythonProject\localuse\Dt\Calib\\simular\\dream\\"
sim_dream_rev = "D:\Thesis\pythonProject\localuse\Dt\Calib\\simular\\\dream_rev\\"
sim_dream_nse = "D:\Thesis\pythonProject\localuse\Dt\Calib\\simular\\dream_nse\\"
sim_dream_nse_rev = "D:\Thesis\pythonProject\localuse\Dt\Calib\\simular\\dream_nse_rev\\"

sim_class = "D:\Thesis\pythonProject\localuse\Dt\Calib\\simular\\class\\"
sim_class_rev = "D:\Thesis\pythonProject\localuse\Dt\Calib\\simular\\\class_rev\\"

sim_original = "D:\Thesis\pythonProject\localuse\Dt\Calib\\simular\\original\\"
sim_rev = "D:\Thesis\pythonProject\localuse\Dt\Calib\\simular\\reverse\\"

sim_nse_rev = "D:\Thesis\pythonProject\localuse\Dt\Calib\simular\\nse_rev\\"
nse_rev = "D:\Thesis\pythonProject\localuse\Dt\Calib\cali_res\\nse_rev\\"


def load_calib_info(method, type_sim, t_trend=True, calib=False, rev=False, egr_spotpy=False, obj_func=None,
                    tipo_proc='patrón'):
    guardar_class = "D:\Thesis\pythonProject\localuse\Dt\Calib\cali_res\class\\"
    guardar_class_rev = "D:\Thesis\pythonProject\localuse\Dt\Calib\cali_res\class_rev\\"

    guardar_original = "D:\Thesis\pythonProject\localuse\Dt\Calib\\cali_res\\original\\"
    guardar_reverse = "D:\Thesis\pythonProject\localuse\Dt\Calib\\cali_res\\reverse\\"

    sim_class = "D:\Thesis\pythonProject\localuse\Dt\Calib\\simular\\class\\"
    sim_class_rev = "D:\Thesis\pythonProject\localuse\Dt\Calib\\simular\\\class_rev\\"

    sim_original = "D:\Thesis\pythonProject\localuse\Dt\Calib\\simular\\original\\"
    sim_rev = "D:\Thesis\pythonProject\localuse\Dt\Calib\\simular\\reverse\\"

    sim_nse_rev = "D:\Thesis\pythonProject\localuse\Dt\Calib\simular\\nse_rev\\"
    nse_rev = "D:\Thesis\pythonProject\localuse\Dt\Calib\cali_res\\nse_rev\\"

    if not calib:
        lg_original = np.load(guardar_original + f'calib_pat-fscabc.npy').tolist()
        lg_reverse = np.load(guardar_reverse + f'calib-fscabc.npy').tolist()

    if t_trend:
        t_trend_original7 = guardar_original + "original7-fscabc-trend.npy"
        t_trend_original21 = guardar_original + "original21-fscabc-trend.npy"
        t_trend_reverse7 = guardar_reverse + "reverse7-fscabc-trend.npy"
        t_trend_reverse21 = guardar_reverse + "reverse21-fscabc-trend.npy"
    if type_sim == 'nse':
        guardar_nse = "D:\Thesis\pythonProject\localuse\Dt\Calib\\cali_res\\nse\\"
        guardar_nse_rev = "D:\Thesis\pythonProject\localuse\Dt\Calib\\cali_res\\nse_rev\\"
        sim_nse = "D:\Thesis\pythonProject\localuse\Dt\Calib\\simular\\nse\\"
        sim_nse_rev = "D:\Thesis\pythonProject\localuse\Dt\Calib\\simular\\nse_rev\\"
        if not calib:
            lg_nse = np.load(guardar_nse + f'calib-fscabc.npy').tolist()
            return ori_valid, 'multidim', 'NSE', guardar_nse + f'nse-{m}', lg_nse, 624  # bd, tipo_proc, obj_func, guardar, lg, n_sim, valid_sim,
        else:
            tipo_proc = 'multidim'
            obj_func = 'NSE'
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
        t_sim_agree_ori = {'t_obs': guardar_class + 'linear\\', 't_sim': guardar_class + 'linear\\t_sim',
                           'tipo': 'coeff_linear', 'trend_icc': guardar_class + 'original21-fscabc-trend.npy',
                           'linear_trend': None}  # guardar_original + 'linear\\trend.npy'}

        t_sim_agree_rev = {'t_obs': guardar_class_rev + 'linear\\', 't_sim': guardar_class_rev + 'linear\\t_sim',
                           'tipo': 'coeff_linear', 'trend_icc': guardar_class_rev + "reverse21-fscabc-trend.npy",
                           'linear_trend': None}  # guardar_reverse + 'linear\\trend.npy'}
        tipo_proc = 'patrón'
        obj_func = 'coeffienct of agreement'
        save_plot = None
        if rev:
            bd = ori_calib
            guardar = guardar_class_rev + f'rev_agreemt-{method}'
            lg = np.load(
                "D:\Thesis\pythonProject\localuse\Dt\Calib\cali_res\class_rev\\calib-fscabc_class_rev.npy").tolist()
            valid_sim = sim_class_rev
            n_sim = 144
            t_sim_gard = t_sim_agree_rev
        else:
            bd = ori_valid
            guardar = guardar_class + f'agreemt-{method}'
            lg = np.load("D:\Thesis\pythonProject\localuse\Dt\Calib\cali_res\class\\calib-fscabc_class.npy").tolist()
            valid_sim = sim_class
            n_sim = 144
            t_sim_gard = t_sim_agree_ori
        return bd, guardar, lg, valid_sim, n_sim, t_sim_gard, tipo_proc, obj_func, save_plot


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
            guardar = guardar_class + f'calib-{method}'
            método = method
            guar_sim = sim_class
            egr_spotpy = egr_spotpy
            return bd, tipo_proc, obj_func, método, guardar, guar_sim, egr_spotpy, n_sim

        else:
            if not t_trend:
                t_sim_gard_original7 = {'t_obs': guardar_class + '7\\t_obs7', 't_sim': guardar_class + '7\\t_sim',
                                        'tipo': 'valid_multi_tests'}
                t_sim_gard_original21 = {'t_obs': guardar_class + '21\\t_obs21', 't_sim': guardar_class + '21\\t_sim',
                                         'tipo': 'valid_others'}
            else:
                t_sim_gard_original7 = ""
                t_sim_gard_original21 = "D:\Thesis\pythonProject\localuse\Dt\Calib\cali_res\class\\origina21-fscabc-trend.npy"
            lg = np.load("D:\Thesis\pythonProject\localuse\Dt\Calib\cali_res\class\\calib-fscabc_class.npy").tolist()
            método = method
            bd = ori_valid
            tipo_proc = 'patrón'
            valid_sim = sim_class
            if obj_func == 'barlas':
                obj_func = 'multi_behavior_tests'
                save_plot = plot + 'class\\7\\'
                guardar = guardar_class + f'original7-{method}'
                t_sim_gard = t_sim_gard_original7
            else:
                obj_func = 'aic'
                save_plot = plot + 'class\\21\\'
                guardar = guardar_class + f'origina21-{method}'
                t_sim_gard = t_sim_gard_original21
            return bd, tipo_proc, obj_func, guardar, método, valid_sim, save_plot, t_sim_gard, n_sim, lg

    elif type_sim == 'reverse':
        plot = "D:\Thesis\pythonProject\localuse\Dt\Calib\plot\\"
        n_sim = 144
        if calib:
            if egr_spotpy:
                egr_spotpy = egr_spotpy
            else:
                egr_spotpy = False
            bd = ori_valid
            tipo_proc = tipo_proc
            obj_func = obj_func
            guardar = guardar_class_rev + f'calib-{method}'
            método = method
            guar_sim = sim_class_rev
            egr_spotpy = egr_spotpy
            return bd, tipo_proc, obj_func, método, guardar, guar_sim, egr_spotpy, 500

        else:
            if not t_trend:
                t_sim_gard_reverse7 = {'t_obs': guardar_class_rev + '7\\t_obs7',
                                       't_sim': guardar_class_rev + '7\\t_sim',
                                       'tipo': 'valid_multi_tests'}
                t_sim_gard_reverse21 = {'t_obs': guardar_class_rev + '21\\t_obs21',
                                        't_sim': guardar_class_rev + '21\\t_sim',
                                        'tipo': 'valid_others'}
            else:
                t_sim_gard_reverse7 = t_trend_reverse7
                t_sim_gard_reverse21 = t_trend_reverse21
            lg = np.load(
                "D:\Thesis\pythonProject\localuse\Dt\Calib\cali_res\class_rev\\calib-fscabc_class_rev.npy").tolist()
            método = method
            bd = ori_calib
            tipo_proc = 'patrón'
            valid_sim = sim_class_rev
            if obj_func == 'barlas':
                obj_func = 'multi_behavior_tests'
                save_plot = plot + 'class_rev\\7\\'
                guardar = guardar_reverse + f'reverse7-{method}'
                t_sim_gard = t_sim_gard_reverse7
            else:
                obj_func = 'aic'
                save_plot = plot + 'class_rev\\21\\'
                guardar = guardar_class_rev + f'reverse21-{method}'
                t_sim_gard = t_sim_gard_reverse21
            return bd, tipo_proc, obj_func, guardar, método, valid_sim, save_plot, t_sim_gard, n_sim, lg

    elif type_sim == 'clutering':
        t_trendall = "D:\Thesis\pythonProject\localuse\Dt\Calib\cali_res\\reverse\\t_sim_all\\all\\all-fscabc-trend.npy"
