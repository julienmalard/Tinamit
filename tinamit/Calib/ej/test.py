# from tinamit.Análisis.Sens.anlzr import anlzr_simul
# from tinamit.Análisis.Sens.corridas import gen_vals_inic
# from tinamit.Calib.ej.sens_análisis import *
# from tinamit.Calib.ej.info_paráms import *
# from tinamit.Calib.ej.info_analr import *
# from tinamit.Análisis.Sens.muestr import gen_problema, muestrear_paráms
# from pandas.plotting import lag_plot

# def process_constant(data):
#     data['bp_params']['constant'] = np.add(data['bp_params']['constant'], data['bp_params']['constant_1'])
#     del data['bp_params']['constant_1']
#     return data
#
#
# for i in range(625):
#     complete_behav = np.load(
#         f"D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\f_simul\\f_simul_no_ini\\f_simul_{i}.npy").tolist()
#     b_param = {}
#     b_param.update({'spp_oscil_aten_inverso': process_constant(complete_behav['spp_oscil_aten_inverso'])})
#     b_param.update({'spp_oscil_aten_log': process_constant(complete_behav['spp_oscil_aten_log'])})
#     print(f"finished {i}-th sample")
#     np.save(f"D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\f_simul\\f_simul_no_ini\\fsim_const\\f_simul_cont_{i}", b_param)

# egr = anlzr_simul('morris', líms_paráms,
#                   "D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\sampled_data\\muestra_morris_625_corrected_bf.json",
#                   mapa_paráms, ficticia=True, var_egr='mds_Watertable depth Tinamit', f_simul_arch={
#         'arch': "D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\f_simul\\f_simul_no_ini\\fsim_const\\f_simul_cont",
#         'num_sample': 625,
#         'counted_behaviors': "D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\f_simul\\f_simul_no_ini\\fsim_const\\count_all.npy"},
#                   dim=215, tipo_egr="superposition", simulation=None, ops_método=None)
# np.save("D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\anlzr\\625\\mor_625_spp_const", egr)

# import numpy as np
# ga = "D:\Thesis\pythonProject\localuse\Dt\Calib\cali_res\\reverse_obs\\"
#
# abc_calib = np.load(ga + 'calib_reverse-fscabc.npy').tolist()
# abc_valid = np.load(ga + 'valid_reverse-fscabc.npy').tolist()
# # dream_calib = np.load(ga + 'calib_reverse-dream.npy').tolist()
# # dream_valid = np.load(ga + 'valid_reverse-dream.npy').tolist()
# print("")
# from tinamit.Análisis.Sens.anlzr import carg_simul_dt
# from tinamit.Calib.ej.obs_patrón import read_obs_csv
# gard_sim = "D:\Thesis\pythonProject\localuse\Dt\Calib\simular\\fscabc\\"
# data = read_obs_csv("D:\Thesis\data\\total_obs.csv")
import operator
from matplotlib import pyplot
import numpy as np



vr = 'mds_Watertable depth Tinamit'


# d_sample = carg_simul_dt(gard_sim, 144, var_egr='mds_Watertable depth Tinamit', dim=1, tipo_egr='paso_tiempo', método='Morris')
# poly = [poly-1 for poly in data[1]]
# new_d_simul={}
# for sam, vec in d_sample[0].items():
#     new_d_simul[sam] = vec[1:, poly]
# for sam, vec in new_d_simul.items():
#     for p in range(vec.shape[1]):
#         sim_series = pd.Series(vec[:, p], index=data[0])
#         lag_plot(sim_series)
#     pyplot.savefig(f"D:\Thesis\pythonProject\localuse\Dt\Calib\plot\Calib\\abc\\sim_{sam}")
# for poly in data[1]:
#     obs_series = pd.Series(data[1][poly], index=data[0])
#     lag_plot(obs_series)
# pyplot.savefig("D:\Thesis\pythonProject\localuse\Dt\Calib\plot\Calib\\abc\\obs_dt")
