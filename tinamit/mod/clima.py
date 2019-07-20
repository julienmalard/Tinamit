import pandas as pd
import xarray as xr
from tinamit.config import _
from تقدیر.مقام import مقام
from tinamit.tiempo.tiempo import TiempoCalendario


class Clima(object):
    def __init__(símismo, lat, long, elev=None, fuentes=None, escenario='8.5'):
        símismo._lugar = مقام(عرض=lat, طول=long, بلندی=elev)
        símismo.fuentes = fuentes
        símismo.escenario = escenario

        símismo.datos = None

    def inicializar(símismo, t):
        """
        Por hacer todas las pedidas a ``taqdir`` de una vez al principio, ahoramos mucho tiempo porque la pedida
        de datos de ``taqdir`` es bastante lenta.

        Parameters
        ----------
        t: TiempoCalendario
            El tiempo del cual querremos datos después.
        """

        f_inic = t.fecha()
        f_final = f_inic + t.delta_relativo(t.n_pasos + 1)

        if símismo.datos is None:
            símismo.datos = símismo._obt_datos_de_taqdir(f_inic, f_final)

        f_inic_datos = símismo.datos.index[0].to_timestamp()
        f_final_datos = símismo.datos.index[-1].to_timestamp()

        # En el caso que ya haya sido inicializado para otra corrida con datos distintos...
        if f_inic_datos > f_inic:
            nuevos = símismo._obt_datos_de_taqdir(f_inic, f_inic_datos - 1)
            símismo.datos = pd.concat([nuevos, símismo.datos])
        if f_final_datos < f_final:
            nuevos = símismo._obt_datos_de_taqdir(f_final_datos + 1, f_final)
            símismo.datos = pd.concat([símismo.datos, nuevos])

    def _obt_datos_de_taqdir(símismo, f_inic, f_final):
        return símismo._lugar.کوائف_پانا(
            f_inic, f_final, ذرائع=(símismo.fuentes,), خاکے=símismo.escenario
        ).روزانہ()

    def obt_datos(símismo, f_inic, f_final=None):

        f_final = f_final or f_inic
        dts = símismo.datos

        return dts[f_inic: f_final]

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
                    datos_vr[(datos_vr['date'] < f) & (datos_vr['date'] <= eje[i + 1])]
                ) if combin is not None else datos_vr[f] for i, f in enumerate(eje[:-1])
            ]

            vals[v] = xr.DataArray(datos_t * conv, coords={_('fecha'): t}, dims=[_('fecha')])
        return vals
