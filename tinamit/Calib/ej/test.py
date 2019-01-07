from tinamit.Calib.ej.sens_análisis import *


def process_constant(data):
    data['bp_params']['constant'] = np.add(data['bp_params']['constant'], data['bp_params']['constant_1'])
    del data['bp_params']['constant_1']
    return data


for i in range(625):
    complete_behav = np.load(
        f"D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\f_simul\\f_simul_no_ini\\f_simul_{i}.npy").tolist()
    b_param = {}
    b_param.update({'spp_oscil_aten_inverso': process_constant(complete_behav['spp_oscil_aten_inverso'])})
    b_param.update({'spp_oscil_aten_log': process_constant(complete_behav['spp_oscil_aten_log'])})
    print(f"finished {i}-th sample")
    np.save(f"D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\f_simul\\f_simul_no_ini\\fsim_const\\f_simul_cont_{i}", b_param)
