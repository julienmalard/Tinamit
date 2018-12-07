import numpy as np

#morris
simu_guar_arch_mor = "D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\simular\\625_mor"
rank_arch_mor = "D:\Thesis\pythonProject\localuse\Dt\Mor\map\\final_plot\\"
no_ini_mor = "D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\f_simul\\f_simul_no_ini\\fited_behav_noini.npy"

paso_data_mor = np.load("D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\anlzr\\625\\mor_625_paso.npy").tolist()

mean_data_mor = np.load("D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\anlzr\\625\\mor_625_promedio.npy").tolist()

behav_data_mor = np.load("D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\anlzr\\625\\mor_625_spp_no_ini.npy").tolist()

#fast
no_ini_fast ="D:\Thesis\pythonProject\localuse\Dt\Fast\post_f_simul\\fited_behav.npy"
paso_data_fast = np.load("D:\Thesis\pythonProject\localuse\Dt\Fast\\anlzr\egr_paso\\egr-0.npy").tolist()
paso_arch_fast = "D:\Thesis\pythonProject\localuse\Dt\Fast\\anlzr\egr_paso\\"


mean_data_fast = np.load("D:\Thesis\pythonProject\localuse\Dt\Fast\\anlzr\\egr_mean\\egr-0.npy").tolist()
mean_arch_fast = "D:\Thesis\pythonProject\localuse\Dt\Fast\\anlzr\\egr_mean\\"


behav_data_fast = np.load("D:\Thesis\pythonProject\localuse\Dt\Fast\\anlzr\\egr_behav\\egr-0.npy").tolist()
behav_arch_fast = "D:\Thesis\pythonProject\localuse\Dt\Fast\\anlzr\\egr_behav\\"
