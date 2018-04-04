from subprocess import run as correr
from pkg_resources import resource_filename
import os
from datetime import datetime as ft

from tinamit.BF import ModeloBF

plantilla_wth = resource_filename('PLANTILLA.WTH', 'tinamit.EnvolturaBF.es.DSSAT')
arch_DSSAT_WTH = 'C:\\DSSAT46\\Weather\\TNMT0101.WTH'

class EnvoltDSSAT(ModeloBF):

    def __init__(símismo, archivo_ingr, exe_DSSAT='C:\\DSSAT46\\DSCSM046.EXE'):
        super().__init__()

        args = {'exe_DSSAT': exe_DSSAT, 'archivo_ingr': archivo_ingr}
        símismo.comanda = '{exe_DSSAT} B {archivo_ingr}'.format(**args)

        símismo.dic_egr = 'C:\\DSSAT46\\Maize\\OVERVIEW.OUT'

        símismo.día_act = 0  # El día actual de la simulación
        símismo.día_princ_últ_sim = 0  # El primer día de la última llamada a DSSAT

    def cambiar_vals_modelo_interno(símismo, valores):
        pass

    def incrementar(símismo, paso):
        correr(símismo.comanda)

    def act_vals_clima(símismo, n_paso, f):
        vars_clima = ['Precipitación', 'Radiación solar',
                      'Temperatura máxima', 'Temperatura mínima']
        datos = símismo.lugar.devolver_datos(vars_clima=vars_clima, f_inic=f, f_final=ft(year=f.year+1, month=1, day=1))

        with open(plantilla_wth, 'r') as d:
            líns = d.readlines()
        for í, f in datos.iterrows():
            dd = {'DATE': í, 'SRAD': f['Radiación solar'], 'RAIN': f['Precipitación'],
                  'TMAX': f['Temperatura máxima'], 'TMIN': f['Temperatura mínima']}
            líns.append('01{DATE:0>3}{SRAD:>6.1f}{TMAX:>6.1f}{TMIN:>6.1f}{RAIN:>6.1f}'.format(**dd))
        with open(arch_DSSAT_WTH, 'w') as d:
            d.writelines(líns)

    def leer_vals(símismo):
        if not os.path.isfile(símismo.dic_egr):
            raise OSError('Error en el programa DSSAT.')

        egr = {}
        corr = None
        with open(símismo.dic_egr) as d:
            for l in d:
                if '*RUN' in l:
                    corr = l.split(':')[1].strip()
                if 'Maize YIELD :' in l:
                    rend = float(l.split(':')[1].split('kg/ha')[0].strip())
                    egr[corr] = rend

        os.remove(símismo.dic_egr)

        return {NotImplementedError}

    def cerrar_modelo(símismo):
        pass

    def obt_unidad_tiempo(símismo):
        return 'año'

    def inic_vars(símismo):
        símismo.variables = {
            'Rendimiento':
                {'val': None,
                 'unidades': 'kg/año',
                 'ingreso': False,
                 'egreso': True,
                 'dims': (1,)
                 },
            'Irrigación':
                {'val': 0,
                 'unidades': None,
                 'ingreso': True,
                 'egreso': False,
                 'dims': (1,)
                 },
            'Orgánico':
                {'val': 0,
                 'unidades': None,
                 'ingreso': True,
                 'egreso': False,
                 'dims': (1,)
                 },
            'Químico':
                {'val': 1,
                 'unidades': None,
                 'ingreso': True,
                 'egreso': False,
                 'dims': (1,)
                 },
        }

    def leer_vals_inic(símismo):
        pass
