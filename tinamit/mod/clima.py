from datetime import date, datetime

import xarray as xr
from تقدیر.مقام import مقام

from tinamit.config import _


class Clima(object):
    def __init__(símismo, lat, long, elev=None, fuentes=None, escenario='8.5'):
        símismo._lugar = مقام(عرض=lat, طول=long, بلندی=elev)
        símismo.fuentes = fuentes
        símismo.escenario = escenario

    def obt_datos(símismo, f_inic, f_final):
        if not isinstance(f_inic, (date, datetime)):
            raise ValueError(
                _('Hay que especificar la fecha inicial para simulaciones de clima.'))  # para hacer: ¿no aquí?
        return símismo._lugar.کوائف_پانا(f_inic, f_final, ذرائع=símismo.fuentes, خاکے=símismo.escenario)

    def combin_datos(símismo, f_inic, f_final, vars_clima):
        vals = {}
        datos = símismo.obt_datos(f_inic, f_final)
        for v, d in vars_clima.items():
            combin = d['combin']
            datos_vr = datos[d['nombre_tqdr']]

            vals[v] = (combin(datos_vr) if combin is not None else datos_vr[-1]) * d['conv']
        return vals

    def obt_todos_vals(símismo, t, vars_clima):
        vals = {}
        datos = símismo.obt_datos(t[0], t[-1])
        for v, d in vars_clima.items():
            datos_vr = datos[d['nombre_tqdr']]
            combin = d['combin']
            conv = d['conv']
            eje = t.eje()
            datos_t = [
                combin(
                    datos_vr[(datos_vr['date'] < f) & (datos_vr['date'] <= eje[i+1])]
                ) if combin is not None else datos_vr[f] for i, f in enumerate(eje[:-1])
            ]

            vals[v] = xr.DataArray(datos_t * conv, coords={_('tiempo'): t}, dims=[_('tiempo')])
        return vals
