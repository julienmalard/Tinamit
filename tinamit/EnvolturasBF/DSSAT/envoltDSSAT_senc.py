import os
from datetime import datetime as ft
from subprocess import run as correr

from pkg_resources import resource_filename

from tinamit.BF import ModeloBF

plantilla_wth = resource_filename('tinamit.EnvolturasBF.es.DSSAT', 'PLANTILLA.WTH')
arch_DSSAT_WTH = 'C:\\DSSAT46\\Weather\\TNMT0101.WTH'


class EnvoltDSSAT(ModeloBF):

    def __init__(símismo, archivo_ingr='DSSBatch.v46', exe_DSSAT='C:\\DSSAT46\\DSCSM046.EXE'):
        super().__init__()

        args = {'exe_DSSAT': exe_DSSAT, 'archivo_ingr': archivo_ingr}
        símismo.comanda = '{exe_DSSAT} MZIXM046 B {archivo_ingr}'.format(**args)

        símismo.dic_egr = 'C:\\DSSAT46\\Maize\\OVERVIEW.OUT'

        símismo.día_act = 0  # El día actual de la simulación
        símismo.día_princ_últ_sim = 0  # El primer día de la última llamada a DSSAT

    def _cambiar_vals_modelo_interno(símismo, valores):
        pass

    def _incrementar(símismo, paso):
        correr(símismo.comanda, cwd='C:\\DSSAT46\\maize')

    def act_vals_clima(símismo, n_paso, f):
        vars_clima = ['Precipitación', 'Radiación solar',
                      'Temperatura máxima', 'Temperatura mínima']
        datos = símismo.lugar.devolver_datos(vars_clima=vars_clima,
                                             f_inic=ft(year=f.year, month=1, day=1),
                                             f_final=ft(year=f.year, month=12, day=31))

        with open(plantilla_wth, 'r') as d:
            líns = d.readlines()
        for í, f in datos.iterrows():
            dd = {'DATE': í.timetuple().tm_yday, 'SRAD': f['شمسی_تابکاری'], 'RAIN': f['بارش'],
                  'TMAX': f['درجہ_حرارت_زیادہ'], 'TMIN': f['درجہ_حرارت_کم']}
            líns.append('01{DATE:0>3}{SRAD:>6.1f}{TMAX:>6.1f}{TMIN:>6.1f}{RAIN:>6.1f}\n'.format(**dd))
        with open(arch_DSSAT_WTH, 'w') as d:
            d.writelines(líns)

    def _leer_vals(símismo):
        if not os.path.isfile(símismo.dic_egr):
            raise OSError('Error en el programa DSSAT.')

        egr = {}
        corr = None
        with open(símismo.dic_egr) as d:
            for l in d:
                if '*RUN' in l:
                    corr = l.split(':')[1].split('MZIXM046')[0].strip()
                if 'Maize YIELD :' in l:
                    rend = float(l.split(':')[1].split('kg/ha')[0].strip())
                    egr[corr] = rend

        irr = símismo.variables['Irrigación']['val']
        org = símismo.variables['Orgánico']['val']
        quím = símismo.variables['Químico']['val']
        fert = org + quím
        if fert > 1:
            org /= fert
            quím /= fert
            nada = 0
        else:
            nada = 1 - fert

        rend_prom = egr['NADA'] * nada + egr['ORGANICO Y RIEGO'] * org * irr + egr['QUIMICO Y RIEGO'] * quím * irr + \
                    egr['ORGANICO'] * org * (1 - irr) + egr['QUIMICO'] * (1 - org) * (1 - irr)

        símismo.variables['Rendimiento']['val'] = rend_prom

        os.remove(símismo.dic_egr)

    def cerrar_modelo(símismo):
        pass

    def unidad_tiempo(símismo):
        return 'año'

    def _inic_dic_vars(símismo):
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

    def _leer_vals_inic(símismo):
        pass
