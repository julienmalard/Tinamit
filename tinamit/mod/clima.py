from datetime import date, datetime

from تقدیر.مقام import مقام

from tinamit.config import _
from tinamit.envolt.bf import EnvolturaBF
from . import Variable
from tinamit.mod import VariablesMod


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

    def variables(símismo):
        return {v for v in símismo._lugar.متاغیرات()}


class EnvoltClima(EnvolturaBF):

    def __init__(símismo, clima):
        símismo.clima = clima
        símismo.datos = None
        variables = VariablesMod(
            [Variable(v, unid=NotImplemented, ingr=False, egr=True) for v in símismo.clima.variables()]
        )
        super().__init__(variables=variables, nombre='clima')

    def iniciar_modelo(símismo, corrida):
        símismo.datos = símismo.clima.obt_datos()

    def incrementar(símismo, rebanada):
        símismo.variables.cambiar_vals({v: símismo.datos[str(v)][símismo.corrida.t.fecha()] for v in símismo.variables})

    def unidad_tiempo(símismo):
        return 'día'
