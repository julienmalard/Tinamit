import datetime as ft
import numpy as np
import pandas as pd

from taqdir.مقامات import مقام


# Ofrecemos la oportunidad de utilizar تقدیر, taqdir, en español
conv_vars = {
    'Precipitación': 'بارش',
    'Radiación solar': 'شمسی_تابکاری',
    'Temperatura máxima': 'درجہ_حرارت_زیادہ',
    'Temperatura promedia': 'درجہ_حرارت_کم',
    'Temperatura mínima': 'درجہ_حرارت_اوسط'
}


# Una subclase traducida
class Lugar(مقام):
    def __init__(símismo, lat, long, elev):

        super().__init__(lat=lat, long=long, elev=elev)

    def observar(símismo, archivo, datos, fecha=None, mes=None, año=None):
        super().cargar_datos(archivo=archivo, cols_datos=datos, fecha=fecha, mes=mes, año=año)

    def prep_datos(símismo, primer_año, último_año, rcp, n_rep=1, diario=True, mensual=True,
                   postdict=None, predict=None, regenerar=True):
        super().prep_datos(primer_año, último_año, rcp, n_rep=1, diario=True, mensual=True,
                           postdict=None, predict=None, regenerar=True)

    def comb_datos(símismo, vars_clima, combin, f_inic, f_final):
        """

        :param vars_clima:
        :type vars_clima: list[str]
        :param combin:
        :type combin: list[str]
        :param f_inic:
        :type f_inic: ft.datetime
        :param f_final:
        :type f_final: ft.datetime
        :return:
        :rtype: dict[np.ndarray]
        """

        bd = símismo.datos['diario']  # type: pd.DataFrame
        datos_interés = bd[vars_clima][(bd['دن'] >= f_inic) & (bd['دن'] <= f_final)]

        resultados = {}
        for v, c in zip(vars_clima, combin):
            try:
                v_conv = conv_vars[v]
            except KeyError:
                raise ValueError('El variable "{}" está erróneo. Debe ser uno de:\n'
                                 '\t{}'.format(v, ', '.join(conv_vars)))
            if c is None:
                if v in ['درجہ_حرارت_زیادہ', 'درجہ_حرارت_کم', 'درجہ_حرارت_اوسط']:
                    c = 'prom'
                else:
                    c = 'total'

            if c == 'prom':
                resultados[v] = datos_interés[v_conv].mean()
            elif c == 'total':
                resultados[v] = datos_interés[v_conv].sum()
            else:
                raise ValueError

        return resultados
