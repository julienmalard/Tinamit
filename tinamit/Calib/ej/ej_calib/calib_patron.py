from tinamit.Calib.ej.sens_análisis import gen_mod
from tinamit.Análisis.Sens.muestr import gen_problema
from tinamit.Calib.ej.info_paráms import calib_líms_paráms, calib_mapa_paráms
from tinamit.Calib.ej.cor_patrón import calib_obs, valid_obs

guardar = "D:\Thesis\pythonProject\localuse\Dt\Calib\\test_pgsdm\\"
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
        'mcmc',
        'sceua',
        'rope',
        'abc',
        'fscabc',
        'mle',
        'demcz',
        'dream',
]

for m in método:
    Calib_res = mod.calibrar(paráms=list(líms_paráms_final), bd=calib_obs, líms_paráms=calib_líms_paráms,
                             vars_obs='mds_Watertable depth Tinamit', final_líms_paráms=líms_paráms_final[0],
                             mapa_paráms=calib_mapa_paráms, tipo_proc='patrón', obj_func='AIC', guardar=guardar+f'calib_pat-{m}',
                             método=m)

    mod.validar(bd=valid_obs, var='mds_Watertable depth Tinamit', obj_func='AIC', guardar=guardar+f'valid_pat-{m}')
