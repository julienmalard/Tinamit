import datetime as ft
import pickle
from multiprocessing import Pool as Reserva
from warnings import warn as avisar

import numpy as np

from tinamit.config import _, conf_mods
from .corrida import Corrida, Rebanada
from .extern import gen_extern
from .res import ResultadosGrupo, ResultadosSimul
from .vars_mod import VariablesMod
from ..tiempo.tiempo import EspecTiempo


class Modelo(object):
    """
    Todas las cosas en Tinamit son instancias de `Modelo`, que sea un modelo de dinámicas de los sistemas, un modelo de
    cultivos o de suelos o de clima, o un modelo conectado.
    Cada tipo de modelo se representa por subclases específicas. Por eso, la gran mayoría de los métodos definidos
    aquí se implementan de manera independiente en cada subclase de `Modelo`.
    """

    idioma_orig = 'es'  # Cambiar en tu modelo si el idioma de sus variables, etc. no es el castellano

    def __init__(símismo, variables, nombre):
        """
        La función de inicialización de todos modelos, conectados o no.

        Parameters
        ----------
        variables : VariablesMod
            Los variables del modelo.
        nombre : str
            El nombre del modelo.

        """

        símismo.nombre = nombre
        símismo.variables = variables
        símismo.corrida = None
        símismo.vars_clima = {}

    def unidad_tiempo(símismo):
        """
        Esta función debe devolver la unidad de tiempo empleada por el modelo.

        Returns
        -------
        str
            La unidad de tiempo (p. ej., 'meses', 'مہینہ', etc.)
        """

        raise NotImplementedError

    def simular(símismo, t, nombre='Tinamït', extern=None, clima=None, vars_interés=None):
        """
        
        Parameters
        ----------
        t: int or EspecTiempo
            La especificación del eje de tiempo. Si es ``int``, significará el número de pasos.
        nombre: str
            El nombre de la corrida.
        extern: Extern or pd.DataFrame or xr.Dataset or dict
            Valores externos para la simulación.
        clima: Clima
            El clima de la simulación.
        vars_interés: list
            Los variables para incluir en los resultados

        Returns
        -------
        ResultadosSimul

        """

        t = t if isinstance(t, EspecTiempo) else EspecTiempo(t)

        corrida = Corrida(
            nombre, t=t.gen_tiempo(símismo.unidad_tiempo()),
            extern=gen_extern(extern),
            vars_mod=símismo.variables,
            vars_interés=vars_interés,
            clima=clima
        )

        símismo.iniciar_modelo(corrida)
        símismo.correr()
        símismo.cerrar()

        return corrida.resultados

    def simular_grupo(símismo, ops_grupo, nombre='Tinamït', paralelo=False):
        """
        Efectua un grupo de simulaciones. Muy útil para accelerar corridas múltiples.

        Parameters
        ----------
        ops_grupo: PlantillaOpsSimulGrupo
            Las opciones de simulación en grupo.
        nombre: str
            El nombre de la simulación.
        paralelo: bool
            Si se simula en paralelo o no. Si el modelo no soporte corridas en paralelo, se ignorará este argumento.

        Returns
        -------
        ResultadosGrupo
        """

        if paralelo and not símismo.paralelizable():
            avisar(_(
                '\nEl modelo no se identifica como paralelizable. Para evitar el riesgo'
                '\nde errores de paralelización, correremos las corridas como simulaciones secuenciales '
                '\nnormales. '
                '\nSi tu modelo sí es paralelizable, crear un método nombrado `.paralelizable()` '
                '\nque devuelve ``True`` en tu clase de modelo para activar la paralelización.'
            ))
            paralelo = False

        res_grupo = ResultadosGrupo(nombre)
        if paralelo:
            l_trabajos = []
            copia_mod = pickle.dumps(símismo)  # Una copia de este modelo.

            # Crear la lista de información necesaria para las simulaciones en paralelo...
            for ops in ops_grupo:
                l_trabajos.append((copia_mod, ops))

            # Hacer las corridas en paralelo
            with Reserva() as r:
                res_paralelo = r.map(_correr_modelo, l_trabajos)
            for res in res_paralelo:
                res_grupo[str(res)] = res

        else:
            for ops in ops_grupo:
                res = símismo.simular(**ops)
                res_grupo[str(res)] = res

        return res_grupo

    def iniciar_modelo(símismo, corrida):
        """
        Inicia la simulación. En general no llamarías esta función directamente.
        
        No se te olvide una llamada al ``super`` cuando reimplementas esta función.
        
        Parameters
        ----------
        corrida: Corrida
            La corrida.

        """
        símismo.corrida = corrida
        corrida.variables.reinic()

        if corrida.extern:
            símismo.cambiar_vals(
                {vr: vl for vr, vl in corrida.obt_extern_act().items() if vr in símismo.variables}
            )
        if corrida.clima and símismo.vars_clima:
            t = símismo.corrida.t
            corrida.clima.inicializar(t)
            símismo._act_vals_clima(
                t.fecha(), t.fecha_próxima() - 1 * t.fecha().freq
            )
        corrida.actualizar_res()

    def correr(símismo):
        """
        Efectuar una simulación ya inicializada. En general, no llamarías esta función directamente.
        """

        intento = símismo._correr_hasta_final()
        if intento is not None:
            símismo.corrida.resultados.poner_vals_t(intento)
        else:
            while símismo.corrida.t.avanzar():
                símismo.incrementar(
                    Rebanada(
                        símismo.corrida.t.pasos_avanzados(símismo.unidad_tiempo()),
                        resultados=símismo.corrida.resultados
                    )
                )
                símismo.corrida.actualizar_res()

    def _correr_hasta_final(símismo):
        """
        Implementar si tu modelo puede correr de una vez hasta el final de la simulación, y después devolver los 
        resultados a cada paso de tiempo. Sirve a accelerar simulaciones no conectadas.
        
        Returns
        -------
        dict
            Un diccionario con matrices de los variables de egreso. Eje 0 debe ser el eje de tiempo.

        """
        return None

    def incrementar(símismo, rebanada):
        """
        Incrementa el modelo. En general, no llamarías esta función directamente.
        
        No se te olvide una llamada al ``super`` cuando reimplementas esta función.
        
        Parameters
        ----------
        rebanada: Rebanada
            La rebanada del incremento.

        """
        if símismo.corrida.extern:
            símismo.cambiar_vals(símismo.corrida.obt_extern_act())

        if símismo.corrida.clima and símismo.vars_clima:
            t = símismo.corrida.t
            símismo._act_vals_clima(t.fecha(), t.fecha_próxima() - 1 * t.fecha().freq)

    def cerrar(símismo):
        """
        Esta función toma acciones necesarias para terminar la simulación y cerrar el modelo, si aplica.
        """
        pass

    def cambiar_vals(símismo, valores):
        """
        Esta función cambia el valor de uno o más variables del modelo.

        Parameters
        ----------
        valores : dict
            Un diccionario de variables y sus valores para cambiar.
        """

        # Cambia primero el valor en el diccionario interno del Modelo
        símismo.variables.cambiar_vals(valores=valores)

    @classmethod
    def obt_conf(cls, llave, auto=None, cond=None, mnsj_err=None):
        """
        Obtiene un valor de configuración de la subclase de modelo.
        
        Parameters
        ----------
        llave: str
            El parámetro de configuración.
        auto: str or int or float or list or bool or dict
            Un valor automático a aplicar si no se encuentra en el diccionario de configuración.
        cond:
            Una condición para validar el valor; si no pasa la condición, se tratará como valor que falta.
        mnsj_err:
            Un mensaje de aviso para devolver al usuario si no se encuentra el valor.

        Returns
        -------
        str, int, float, list, bool, dict
            El valor de configuración
        """

        auto = auto or []
        if isinstance(auto, str):
            auto = [auto]

        try:
            op = conf_mods[cls.__name__][llave]
            if cond is None or cond(op):
                return op
        except KeyError:
            pass

        for op in auto:
            if cond is None or cond(op):
                conf_mods[cls.__name__, llave] = op
                return op

        if mnsj_err:
            avisar(mnsj_err)

    @classmethod
    def estab_conf(cls, llave, valor):
        """
        Establece un valor de configuración.
        
        Parameters
        ----------
        llave: str
            El parámetro de configuración.
        valor: str or int or float or list or bool or dict
            El valor del parámetro.

        """
        conf_mods[cls.__name__, llave] = valor

    @classmethod
    def instalado(cls):
        """
        Si tu modelo depiende en una instalación de otro programa externo a Tinamït, puedes reimplementar esta función
        para devolver ``True`` si el modelo está instalado y ``False`` sino.

        Returns
        -------
        bool
            Si el modelo está instalado completamente o no.
        """

        return True

    def paralelizable(símismo):
        """
        Indica si el modelo actual se puede paralelizar de manera segura o no. Si implementas una subclase
        paralelizable, reimplementar esta función para devolver ``True``.
        
        ¿No sabes si es paralelizable tu modelo?
        
        **Respuesta larga**: Si el modelo se puede paralelizar (con corridas de nombres distintos) sin encontrar 
        dificultades técnicas (sin riesgo que las corridas paralelas terminen escribiendo en los mismos archivos de 
        egreso), entonces sí es paralelizable tu modelo.
        
        **Respuesta rápida**: 95% seguro que sí.
        
        Returns
        -------
        bool:
            Si el modelo es paralelizable o no.
        """

        return False

    def conectar_var_clima(símismo, var, var_clima, conv, combin='prom'):
        """
        Conecta un variable climático.

        Parameters
        ----------
        var : str
            El nombre interno del variable en el modelo.
        var_clima : str
            El nombre oficial del variable climático.
        conv : number
            La conversión entre el variable clima en Tinamït y el variable correspondiente en el modelo.
        combin : str or function or None
            Si este variable se debe adicionar o tomar el promedio entre varios pasos. Puede ser ``prom``, ``total``,
            o una función. Si es ``None``, se tomará el último día en el caso de pasos de más de 1 día.
        """

        combins = {
            'prom': np.mean,
            'total': np.sum
        }
        if isinstance(combin, str):
            combin = combins[combin.lower()]

        símismo.vars_clima[var] = {
            'nombre_tqdr': var_clima,
            'combin': combin,
            'conv': conv
        }

    def _act_vals_clima(símismo, f_0, f_1, vars_clima=None):
        """
        Actualiza los variables climáticos. Esta función es la automática para cada modelo. Si necesitas algo más
        complicado (como, por ejemplo, predicciones por estación), la puedes cambiar en tu subclase.

        Parameters
        ----------
        f_0 : ft.date | ft.datetime
            La fecha actual.
        f_1 : ft.date | ft.datetime
            La próxima fecha.
        vars_clima : dict
        """
        vars_clima = vars_clima or símismo.vars_clima
        datos = símismo.corrida.clima.combin_datos(vars_clima=vars_clima, f_inic=f_0, f_final=f_1)

        símismo.cambiar_vals(valores=datos)

    def __str__(símismo):
        return símismo.nombre


def _correr_modelo(x):
    """
    Función para inicializar y correr un modelo en paralelo.

    Parameters
    ----------
    x : tuple[Modelo, dict]
        Los parámetros. El primero es el modelo, el segundo el diccionario de parámetros para la simulación.

    Returns
    -------
    dict
        Los resultados de la simulación.
    """

    estado_mod, d_args = x

    mod = pickle.loads(estado_mod)

    # Después, simular el modelo y devolver los resultados, si hay.
    return mod.simular(**d_args)
