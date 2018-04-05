from tinamit.Geog.Geog import Lugar
from tinamit.Conectado import Conectado
import os
import json
import numpy as np

mod = Conectado()
mod.estab_bf('DSSAT.py')
mod.estab_mds('Para Tinamït.de.verdad.vpm')

mod.conectar(var_mds='Rendimiento milpa', var_bf='Rendimiento', mds_fuente=False, conv=1/12)
mod.conectar(var_mds='Uso insumos químicos', var_bf='Químico', mds_fuente=True)
mod.conectar(var_mds='Uso insumos orgánicos', var_bf='Orgánico', mds_fuente=True)
mod.conectar(var_mds='Agua disponible', var_bf='Irrigación', mds_fuente=True)

mod.estab_conv_tiempo(mod_base='bf', conv=12)

dics_pol = {'Base': {'Política consumo de hortalizas': 0, 'Política riego': 0, 'Política acceso a crédito': 0,
                      'Política educación': 0, 'Política reforestación': 0},
            'Consumo': {'Política consumo de hortalizas': 1, 'Política riego': 0, 'Política acceso a crédito': 0, 'Política educación': 0, 'Política reforestación': 0},
            'Riego': {'Política riego': 1, 'Política consumo de hortalizas': 0, 'Política acceso a crédito': 0, 'Política educación': 0, 'Política reforestación': 0},
            'Crédito': {'Política acceso a crédito': 1, 'Política consumo de hortalizas': 0, 'Política riego': 0, 'Política educación': 0, 'Política reforestación': 0},
            'Educación': {'Política educación': 1, 'Política consumo de hortalizas': 0, 'Política riego': 0, 'Política acceso a crédito': 0, 'Política reforestación': 0},
            'Reforest': {'Política reforestación': 1, 'Política educación': 0, 'Política consumo de hortalizas': 0, 'Política riego': 0, 'Política acceso a crédito': 0},
            'Todas': {'Política consumo de hortalizas': 1, 'Política riego': 1, 'Política acceso a crédito': 1, 'Política educación': 1, 'Política reforestación': 1}
            }

Tz_Ya = Lugar(lat=14.673, long=-91.145, elev=2050)

res = mod.simular_paralelo(tiempo_final=40, nombre_corrida='Conec', fecha_inic=2020, tcr=[2.6, 4.5, 6.0, 8.5, 0],
                           devolver=['Seguridad alimentaria', 'Rendimiento milpa', 'Pobreza',
                                     'Tecnificación agrícola', 'Emigración permanente'],
                           lugar=Tz_Ya, vals_inic={x: {'mds': v} for x, v in dics_pol.items()}, clima=True,
                           combinar=True)


def np_a_lista(d, d_f=None):
    if d_f is None:
        d_f = {}

    for ll, v in d.items():
        if isinstance(v, dict):
            d_f[ll] = {}
            np_a_lista(d=v, d_f=d_f[ll])
        elif isinstance(v, np.ndarray):
            d_f[ll] = v.tolist()
        elif isinstance(v, str):
            d_f[ll] = v
        else:
            try:
                if v is None or np.any(np.isnan(v)):
                    d_f[ll] = 'None'
                else:
                    d_f[ll] = v
            except TypeError:
                d_f[ll] = 'None'

    return d_f

print(res)
with open(os.path.join(os.path.split(__file__)[0], 'calib.json'), 'w', encoding='UTF-8') as d:
    json.dump(np_a_lista(res), d, ensure_ascii=False, sort_keys=True, indent=2)
