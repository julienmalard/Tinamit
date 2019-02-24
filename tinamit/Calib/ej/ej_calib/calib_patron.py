import numpy as np
from tinamit.Calib.ej.sens_análisis import gen_mod
from tinamit.Análisis.Sens.muestr import gen_problema
from tinamit.Calib.ej.info_paráms import calib_líms_paráms, calib_mapa_paráms
from tinamit.Calib.ej.cor_patrón import calib_obs_90, valid_obs_90, calib_obs_80, valid_obs_80

guardar = "D:\Thesis\pythonProject\localuse\Dt\Calib\\cali_res\\reverse_obs\\"
fscabc_sim = "D:\Thesis\pythonProject\localuse\Dt\Calib\\simular\\reverse_obs\\"
test = "D:\Thesis\pythonProject\localuse\Dt\Calib\\test_pgsdm\\"
FSCABC = "C:\\Users\\gis_user\\AppData\\Local\\Temp\\CalibTinamït_42bbykc6.csv"
# load original parameter names for the model simulation
líms_paráms_final = []
líms_paráms_final.append(gen_problema(líms_paráms=calib_líms_paráms, mapa_paráms=calib_mapa_paráms, ficticia=False)[1])

# process parameter names to fit the SPOTPY
# líms_paráms_final.append(
#     {f'{k[:3]}_{k[4]}' if not k.startswith('Peq') | k.startswith('Pex') and k.startswith(
#         'POH') else 'CTW' if k.startswith('Capacity') else f'{k[:3]}{k[-2:]}': limis for k, limis in
#      líms_paráms_final[0].items()})

# calibrate the model
mod = gen_mod()

método = [
    'mle',
    # 'demcz',
    # 'sceua',
    # 'dream',
    # 'mcmc',
    'rope',
    'abc',
    'fscabc',
]

parallel_método = [
    'mc',
    'dream',
    'sceua',
    'rope',
    'abc',
    'fscabc',
    'demcz'
]
method = ['dream', 'fscabc']

# if __name__ == "__main__":
#     for m in method:
#         if m == 'fscabc':
#             Calib_res = mod.calibrar(paráms=list(líms_paráms_final), bd=valid_obs_90, líms_paráms=calib_líms_paráms,
#                                      vars_obs='mds_Watertable depth Tinamit', final_líms_paráms=líms_paráms_final[0],
#                                      mapa_paráms=calib_mapa_paráms, tipo_proc='patrón', obj_func='AIC',
#                                      guardar=guardar + f'calib_pat-{m}', método=m, n_iter=500, guar_sim=fscabc_sim
#                                      )

if __name__ == "__main__":
    for m in method:
        if m == 'fscabc':
            lg = np.load(guardar + f'calib_pat-{m}.npy').tolist()
            mod.validar(bd=calib_obs_90, var='mds_Watertable depth Tinamit', tipo_proc='patrón', obj_func='AIC',
                        guardar=guardar + f'valid_reverse-{m}', lg=lg, paralelo=True, valid_sim=fscabc_sim, n_sim=624)
