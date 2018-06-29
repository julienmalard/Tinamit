import csv
import datetime as ft
import json
import math
import os
import pickle
import re
from copy import deepcopy as copiar_profundo
from multiprocessing import Pool as Reserva
from warnings import warn as avisar

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta as deltarelativo
from lxml import etree as arbole

import tinamit.Geog.Geog as Geog
from tinamit import _, valid_nombre_arch, detectar_codif
from tinamit.Análisis.Calibs import CalibradorEc, CalibradorMod
from tinamit.Análisis.Datos import leer_fechas, SuperBD, Datos, DatosRegión
from tinamit.Análisis.Valids import validar_resultados
from tinamit.Análisis.sintaxis import Ecuación
from tinamit.Unidades.conv import convertir


class Modelo(object):
    """
    Todas las cosas en Tinamit son instancias de `Modelo`, que sea un modelo de dinámicas de los sistemas, un modelo de
    cultivos o de suelos o de clima, o un modelo conectado.
    Cada tipo de modelo se representa por subclases específicas. Por eso, la gran mayoría de los métodos definidos
    aquí se implementan de manera independiente en cada subclase de `Modelo`.
    """

    # Una opción para precisar si un modelo está instalado en la computadora o no. Se usa en el caso de modelos que
    # dependen de un programa externo que podría no estar disponible en todas las computadoras que tienen Tinamït.
    instalado = True

    leng_orig = 'es'

    def __init__(símismo, nombre):
        """
        La función de inicialización de todos modelos, conectados o no.

        :param nombre: El nombre del modelo. Sirve para identificar distintos modelos en un modelo conectado.
        :type nombre: str

        """

        # No se puede incluir nombres de modelos con "_" en el nombre (podría corrumpir el manejo de variables en
        # modelos jerarquizados).
        if "_" in nombre:
            avisar(_('No se pueden emplear nombres de modelos con "_", así que no puedes nombrar tu modelo "{}".\n'
                     'Sino, causaría problemas de conexión de variables por una razón muy compleja y oscura.\n'
                     'Vamos a renombrar tu modelo "{}". Lo siento.').format(nombre, nombre.replace('_', '.')))
            nombre = nombre.replace('_', '.')

        # El nombre del modelo (sirve como una referencia a este modelo en el modelo conectado).
        símismo.nombre = nombre

        # El diccionario de variables necesita la forma siguiente. Se llena con la función símismo._inic_dic_vars().
        # {var1: {'val': 13, 'unidades': cm, 'ingreso': True, 'egreso': True},
        #  var2: {...},
        #  ...}
        símismo.variables = {}
        símismo._inic_dic_vars()  # Iniciar los variables.

        #
        símismo.datos = None  # type: SuperBD
        símismo.calibs = {}
        símismo.info_calibs = {'calibs': {}, 'micro calibs': {}}
        símismo.conex_var_datos = {}
        símismo.combin_incrs = False

        # Memorio de valores de variables (para leer los resultados más rápidamente después de una simulación).
        símismo.mem_vars = {}

        # Referencia hacia el nombre de la corrida activa.
        símismo.corrida_activa = None

        # Una referncia para acordarse si los valores de los variables en el diccionario de variables están actualizados
        símismo.vals_actualizadas = False

        # Un diccionarior para guardar valores de variables iniciales hasta el momento que empezamos la simulación.
        # Es muy útil para modelos cuyos variables no podemos cambiar antes de empezar una simulación (como VENSIM).
        símismo.vals_inic = {}
        símismo.vars_clima = {}  # Formato: var_intern1: {'nombre_extrn': nombre_oficial, 'combin': 'prom' | 'total'}
        símismo.lugar = None  # type: Geog.Lugar
        símismo.geog = None

        # Listas de los nombres de los variables que sirven de conexión con otro modelo.
        símismo.vars_saliendo = set()

        # Para manejar unidades de tiempo y su correspondencia con fechas iniciales.
        símismo._conv_unid_tiempo = {'unid_ref': None, 'factor': 1}

    def _inic_dic_vars(símismo):
        """
        Esta función debe poblar el diccionario de variables del modelo, según la forma siguiente:
        {'var1': {'val': 13, 'unidades': 'cm', 'ingreso': True, dims: (1,), 'egreso': True, 'info': 'descripción'},
        'var2': ...}
        }

        """
        raise NotImplementedError

    def unidad_tiempo(símismo):
        """
        Esta función debe devolver la unidad de tiempo empleada por el modelo.

        :return: La unidad de tiempo (p. ejemplo, 'meses', 'مہینہ', etc.
        :rtype: str

        """
        raise NotImplementedError

    def _leer_vals_inic(símismo):
        raise NotImplementedError

    def iniciar_modelo(símismo, tiempo_final, nombre_corrida):

        símismo.corrida_activa = nombre_corrida

        símismo._iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida=nombre_corrida)

        símismo._leer_vals_inic()

        símismo._act_vals_dic_var(símismo.vals_inic)
        símismo._aplicar_cambios_vals_inic()

    def _act_vals_dic_var(símismo, valores):
        for var, val in valores.items():
            if isinstance(símismo.variables[var]['val'], np.ndarray):
                símismo.variables[var]['val'][:] = val
            else:
                símismo.variables[var]['val'] = val

    def _iniciar_modelo(símismo, tiempo_final, nombre_corrida):
        """
        Esta función llama cualquier acción necesaria para preparar el modelo para la simulación. Esto incluye aplicar
        valores iniciales. En general es muy fácil y se hace simplemente con "símismo.cambiar_vals(símismo.vals_inic)",
        pero para unos modelos (como Vensim) es un poco más delicado así que los dejamos a ti para implementar.

        :param tiempo_final: El tiempo final de la simulación.
        :type tiempo_final: int

        :param nombre_corrida: El nombre de la corrida (generalmente para guardar resultados).
        :type nombre_corrida: str

        """
        raise NotImplementedError

    def _aplicar_cambios_vals_inic(símismo):
        raise NotImplementedError

    def _conectar_clima(símismo, lugar, fecha_inic, fecha_final, escenario):
        """
        Esta función conecta el clima de un lugar con el modelo.

        :param  n_pasos: El número de pasos para la simulación.
        :type n_pasos: int
        :param lugar: El lugar.
        :type lugar: Lugar
        :param fecha_inic: La fecha inicial de la simulación.
        :type fecha_inic: ft.date
        :param escenario: El escenario climático según el sistema de la IPCC (2.6, 4.5, 6.0, o 8.5)
        :type escenario: str | float

        """

        # Obtener los datos de lugares
        lugar.prep_datos(fecha_inic=fecha_inic, fecha_final=fecha_final, tcr=escenario)

    def simular(símismo, tiempo_final, paso=1, nombre_corrida='Corrida Tinamït', tiempo_inic=None, lugar=None,
                clima=None, vars_interés=None, guardar=False):
        """

        Parameters
        ----------
        tiempo_final :
        paso :
        nombre_corrida :
        tiempo_inic : ft.date
        lugar : Geog.Lugar
        clima :
        vars_interés :
        guardar: bool

        Returns
        -------

        """

        # Conectar el lugar
        símismo.lugar = lugar

        # Calcular el número de pasos necesario
        if int(paso) != paso:
            raise ValueError(_('`paso` debe ser un número entero.'))
        if paso < 1:
            raise ValueError(_('El paso debe ser superior a 1.'))
        n_pasos = int(math.ceil(tiempo_final / paso))

        # Preparar las unidades de tiempo
        dic_trad_tiempo = {'año': 'year', 'mes': 'months', 'día': 'days'}
        fecha_act = tiempo_inic

        # Si hay fecha inicial, tenemos que guardar cuenta de donde estamos en el calendario
        if tiempo_inic is None:
            if clima is not None:
                raise ValueError(_('Hay que especificar la fecha inicial para simulaciones de clima.'))
            unid_ref_tiempo = None

        else:
            if isinstance(tiempo_inic, ft.datetime):
                # Formatear la fecha inicial
                tiempo_inic = tiempo_inic.date()
            elif isinstance(tiempo_inic, int):
                año = tiempo_inic
                día = mes = 1
                tiempo_inic = ft.date(year=año, month=mes, day=día)
            elif isinstance(tiempo_inic, str):
                tiempo_inic = leer_fechas(tiempo_inic)
            fecha_act = tiempo_inic
            unid_ref_tiempo = símismo._conv_unid_tiempo['unid_ref']
            if unid_ref_tiempo is None:
                unid_ref_tiempo = símismo.unidad_tiempo()
            for u in ['año', 'mes', 'día']:
                try:
                    factor = convertir(de=unid_ref_tiempo, a=u)
                    if factor == 1:
                        unid_ref_tiempo = u
                        break
                except ValueError:
                    pass
            if unid_ref_tiempo not in ['año', 'mes', 'día']:
                raise ValueError(_('La unidad de tiempo "{}" no se pudo convertir a años, meses o días.')
                                 .format(unid_ref_tiempo))
            fecha_final = tiempo_inic + deltarelativo(**{dic_trad_tiempo[unid_ref_tiempo]: n_pasos})  # type: ft.date

            if lugar is not None and clima is None:
                clima = 0

            # Conectar el clima, si necesario
            if clima is not None:
                if lugar is None:
                    raise ValueError(_('Hay que especificar un lugar para incorporar el clima.'))
                else:
                    símismo._conectar_clima(lugar=lugar, fecha_inic=tiempo_inic, fecha_final=fecha_final,
                                            escenario=clima)

        # Iniciamos el modelo.
        símismo.corrida_activa = nombre_corrida
        símismo.iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida=nombre_corrida)

        # Verificar los nombres de los variables de interés
        símismo.vars_saliendo.clear()
        if vars_interés is None:
            vars_interés = []
        else:
            if not isinstance(vars_interés, list):
                vars_interés = [vars_interés]
            for i, v in enumerate(vars_interés.copy()):
                var = símismo.valid_var(v)
                vars_interés[i] = var
                símismo.vars_saliendo.add(var)

        if tiempo_inic is not None:
            fecha_próx = fecha_act + deltarelativo(**{dic_trad_tiempo[unid_ref_tiempo]: paso})

            # Actualizar variables de clima, si necesario
            if clima is not None:
                símismo.act_vals_clima(fecha_act, fecha_próx)

            fecha_act = fecha_próx

        símismo.mem_vars.clear()
        for v in vars_interés:
            dims = símismo.obt_dims_var(v)
            if dims == (1,):
                símismo.mem_vars[v] = np.empty(n_pasos + 1)
            else:
                símismo.mem_vars[v] = np.empty((n_pasos + 1, *símismo.obt_dims_var(v)))
            símismo.mem_vars[v][:] = np.nan

            símismo.mem_vars[v][0] = símismo.obt_val_actual_var(v)

        if clima is None and símismo.combin_incrs:
            símismo.incrementar(paso=n_pasos * paso, guardar_cada=paso)
            # Después de la simulación, cerramos el modelo.
            símismo.cerrar_modelo()
            res = símismo.leer_arch_resultados(archivo=nombre_corrida, var=vars_interés)
            for var, val in símismo.mem_vars.items():
                if res[var].shape[0] == n_pasos + 1:
                    val[:] = res[var]
                else:
                    val[:] = res[var][::paso]

        else:
            # Hasta llegar al tiempo final, incrementamos el modelo.
            for i in range(n_pasos):

                # Incrementar el modelo
                símismo.incrementar(paso)

                # Guardar valores de variables de interés
                if len(vars_interés):
                    símismo.leer_vals()
                for v in vars_interés:
                    símismo.mem_vars[v][i + 1] = símismo.obt_val_actual_var(v)

                if i != (n_pasos - 1):
                    if tiempo_inic is not None:
                        fecha_próx = fecha_act + deltarelativo(**{dic_trad_tiempo[unid_ref_tiempo]: paso})

                        # Actualizar variables de clima, si necesario
                        if clima is not None:
                            símismo.act_vals_clima(fecha_act, fecha_próx)

                        fecha_act = fecha_próx

            # Después de la simulación, cerramos el modelo.
            símismo.cerrar_modelo()

        if vars_interés is not None:
            return copiar_profundo(símismo.mem_vars)

        if guardar:
            símismo.guardar_resultados()

    def simular_grupo(símismo, tiempo_final, paso=1, nombre_corrida='', vals_inic=None,
                      tiempo_inic=None, lugar=None, clima=None, combinar=True,
                      dibujar=None, paralelo=None, vars_interés=None, guardar=False):

        # Formatear los nombres de variables a devolver.
        if vars_interés is not None:
            if isinstance(vars_interés, str):
                vars_interés = [vars_interés]
            vars_interés = [símismo.valid_var(v) for v in vars_interés]
        else:
            if not guardar:
                avisar(_('No podremos guardar datos porque tienes `guardar=False` y no especificaste `vars_interés`.'))

        # Poner las opciones de simulación en un diccionario.
        opciones = {'paso': paso, 'tiempo_inic': tiempo_inic, 'lugar': lugar, 'vals_inic': vals_inic,
                    'clima': clima, 'tiempo_final': tiempo_final}

        # Entender el tipo de opciones (lista, diccionario, o valor único)
        tipos_ops = {
            nmb: dict if isinstance(op, dict) else list if isinstance(op, list) else 'val'
            for nmb, op in opciones.items()
        }
        # Una excepción para "vals_inic": si es un diccionario con nombres de variables como llaves, es valor único;
        # si tiene nombres de corridas como llaves y diccionarios de variables como valores, es de tipo diccionario.
        op_inic = opciones['vals_inic']
        if isinstance(op_inic, list):
            tipos_ops['vals_inic'] = list
        elif isinstance(op_inic, dict):
            if all(isinstance(v, dict) for v in op_inic.values()):
                tipos_ops['vals_inic'] = dict
            elif not any(isinstance(v, dict) for v in op_inic.values()):
                tipos_ops['vals_inic'] = 'val'
            else:
                raise ValueError(_('Error en `vals_inic`.'))

        # Generaremos el diccionario de corridas:
        corridas = _gen_dic_ops_corridas(
            nombre_corrida=nombre_corrida, combinar=combinar, tipos_ops=tipos_ops, opciones=opciones
        )

        # Sacar los valores iniciales del diccionario de opciones de corridas
        d_vals_inic = {ll: v.pop('vals_inic') for ll, v in corridas.items()}

        # Validar los nombres y evitar un problema con nombres de corridas con '.' en Vensim
        mapa_nombres = {corr: valid_nombre_arch(corr.replace('.', '_')) for corr in corridas}
        for ant, nv in mapa_nombres.items():
            corridas[nv] = corridas.pop(ant)

        # Ahora, hacemos las simulaciones
        resultados = {}  # El diccionario de resultados

        # Verificar si vale la pena hacer corridas paralelas o no
        if paralelo is None:
            antes = ft.datetime.now()
            corr0 = list(corridas)[0]
            d_corr0 = corridas.pop(corr0)

            símismo.inic_vals_vars(dic_vals=d_vals_inic[corr0])

            d_corr0['vars_interés'] = vars_interés

            # Después, simular el modelo.
            res = símismo.simular(**d_corr0, nombre_corrida=corr0)

            if res is not None:
                resultados[mapa_nombres[corr0]] = res

            tiempo_simul = (ft.datetime.now() - antes).total_seconds()
            paralelo = tiempo_simul > 15

        # Efectuar las corridas
        if paralelo and símismo.paralelizable():
            # ...si el modelo y todos sus submodelos son paralelizables...

            # Este código un poco ridículo queda necesario para la paralelización en Windows. Si no estuviera aquí,
            # el programa se travaría para siempre a este punto.

            # Un variable MUY largo, que NO DEBE EXISTIR en cualquier otra parte del programa. Por eso tomamos un
            # nombre de variable muy, muy largo que estoy seguro no encontraremos en otro lugar.
            global ejecutando_simulación_paralela_por_primera_vez

            # Si no existía antes, es la primera vez que estamos ejecutando este código
            if 'ejecutando_simulación_paralela_por_primera_vez' not in globals():
                ejecutando_simulación_paralela_por_primera_vez = True

            # Si no es la primera vez, no querremos correr la simulación. (Sino, creerá ramas infinitas del proceso
            # Python).
            if not ejecutando_simulación_paralela_por_primera_vez:
                avisar(_('Parece que estés corriendo simulaciones en paralelo en Windows o alguna cosa parecida '
                         '\nsin poner tu código principal en "if __name__ == "__main__"". Probablemente funcionará'
                         '\nel código de todo modo, pero de verdad no es buena idea.'))
                return

            # Si era la primera vez, ahora ya no lo es.
            ejecutando_simulación_paralela_por_primera_vez = False

            # Empezar las simulaciones en paralelo
            l_trabajos = []  # type: list[tuple]

            copia_mod = pickle.dumps(símismo)  # Una copia de este modelo.

            # Crear la lista de información necesaria para las simulaciones en paralelo...
            for corr, d_prms_corr in corridas.items():
                d_args = {ll: copiar_profundo(v) for ll, v in d_prms_corr.items()}
                d_args['nombre_corrida'] = corr
                d_args['vars_interés'] = vars_interés

                l_trabajos.append((copia_mod, copiar_profundo(d_vals_inic[corr]), d_args))

            # Hacer las corridas en paralelo
            with Reserva() as r:
                res_paralelo = r.map(_correr_modelo, l_trabajos)

            # Ya terminamos la parte difícil. Desde ahora, sí permitiremos otras ejecuciones de esta función.
            ejecutando_simulación_paralela_por_primera_vez = True

            # Formatear los resultados, si hay.
            if res_paralelo is not None:
                resultados.update(
                    {mapa_nombres[corr]: res for corr, res in zip(corridas, res_paralelo)}
                )

        else:
            # Sino simplemente correrlas una tras otra con `Modelo.simular()`
            if paralelo:
                avisar(_('No todos los submodelos del modelo conectado "{}" son paralelizable. Para evitar el riesgo'
                         'de errores de paralelización, correremos las corridas como simulaciones secuenciales '
                         'normales. '
                         'Si tus modelos sí son paralelizables, crear un método nombrado `.paralelizable()` '
                         'que devuelve ``True`` en tu clase de modelo para activar la paralelización.'
                         ).format(símismo.nombre))

            # Para cada corrida...
            for corr, d_prms_corr in corridas.items():
                símismo.inic_vals_vars(dic_vals=d_vals_inic[corr])

                d_prms_corr['vars_interés'] = vars_interés

                # Después, simular el modelo.
                res = símismo.simular(**d_prms_corr, nombre_corrida=corr)

                if res is not None:
                    resultados[mapa_nombres[corr]] = res

        if guardar:
            for corr, res in resultados:
                símismo.guardar_resultados(dic_res=res, nombre=corr)

        return resultados

    def guardar_resultados(símismo, dic_res=None, nombre=None, frmt='json', var=None):
        """

        Parameters
        ----------
        dic_res: dict[str, np.ndarray]
        nombre
        frmt

        Returns
        -------

        """
        if dic_res is None:
            dic_res = símismo.mem_vars
        if not len(dic_res):
            raise ValueError(_('No hay datos de simulación disponibles para guardar. :('))
        if nombre is None:
            nombre = símismo.corrida_activa
        if var is None:
            l_vars = list(dic_res)
        elif isinstance(var, str):
            l_vars = [var]
        else:
            l_vars = var

        faltan = [x for x in l_vars if x not in dic_res]
        if len(faltan):
            raise ValueError(_('Los variables siguientes no existen en los datos:'
                               '\n{}').format(', '.join(faltan)))

        n_pasos = list(dic_res.values())[0].shape[0]
        if not all((val.shape[0] == n_pasos for val in dic_res.values())):
            raise ValueError(_('No todos los variables tienen el mismo número de datos.'))

        if 'tiempo' not in dic_res:
            dic_res['tiempo'] = np.arange(n_pasos)

        if frmt[0] != '.':
            frmt = '.' + frmt
        arch = valid_nombre_arch(nombre + frmt)
        if frmt == '.json':
            contenido = {ll: v.tolist() for ll, v in dic_res.items() if ll in l_vars}
            with open(arch, 'w', encoding='UTF-8') as a:
                json.dump(contenido, a)
        elif frmt == '.csv':

            with open(arch, 'w', encoding='UTF-8', newline='') as a:
                escr = csv.writer(a)

                escr.writerow(['tiempo'] + dic_res['tiempo'].tolist())
                for var, vals in dic_res.items():
                    if var not in l_vars:
                        continue
                    if len(vals.shape) == 1:
                        escr.writerow([var] + vals.tolist())
                    else:
                        for í in range(vals.shape[1]):
                            escr.writerow(['{}[{}]'.format(var, í)] + vals[:, í].tolist())

        else:
            raise ValueError(_('Formato de resultados "{}" no reconocido.').format(frmt))

    def _incrementar(símismo, paso, guardar_cada=None):
        """
        Esta función debe avanzar el modelo por un periodo de tiempo especificado.

        :param paso: El paso.
        :type paso: int

        """
        raise NotImplementedError

    def incrementar(símismo, paso, guardar_cada=None):
        símismo.vals_actualizadas = False
        símismo._incrementar(paso=paso, guardar_cada=guardar_cada)

    def leer_vals(símismo):

        if not símismo.vals_actualizadas:
            símismo._leer_vals()

            símismo.vals_actualizadas = True

    def _leer_vals(símismo):
        """
        Esta función debe leer los valores del modelo y escribirlos en el diccionario interno de variables. Se
        implementa frequentement con modelos externos de cuyos egresos hay que leer los resultados de una corrida.

        """

        raise NotImplementedError

    def inic_val_var(símismo, var, val):
        """
        Est método cambia el valor inicial de un variable (antes de empezar la simulación). Se emplea principalmente
        para activar y desactivar políticas y para establecer parámetros y valores iniciales para simulaciones.

        :param var: El nombre del variable para cambiar.
        :type var: str

        :param val: El nuevo valor del variable.
        :type val: float | np.ndarray

        """

        # Primero, asegurarse que el variable existe.
        var = símismo.valid_var(var)

        # Guardamos el valor en el diccionario `vals_inic`. Se aplicarán los valores iniciales únicamente al momento
        # de empezar la simulación.
        símismo.vals_inic[var] = val

        # Aplicar los valores iniciales al diccionario de valores actuales también.
        símismo._act_vals_dic_var({var: val})

    def inic_vals_vars(símismo, dic_vals):
        """
        Una función más cómoda para inicializar muchos variables al mismo tiempo.

        :param dic_vals:
        :type dic_vals: dict[str, float | int | np.ndarray]

        """

        for var, val in dic_vals.items():
            símismo.inic_val_var(var=var, val=val)

    def limp_vals_inic(símismo, var=None):
        """
        Esta función limpa los valores iniciales especificados anteriormente.
        """

        # Limpiar el diccionario.
        if var is None:
            símismo.vals_inic.clear()
        else:
            var = símismo.valid_var(var)
            try:
                símismo.vals_inic.pop(var)
            except KeyError:
                pass

    def conectar_var_clima(símismo, var, var_clima, conv, combin=None):
        """
        Conecta un variable climático.

        :param var: El nombre interno del variable en el modelo.
        :type var: str
        :param var_clima: El nombre oficial del variable climático.
        :type var_clima: str
        :param conv: La conversión entre el variable clima en Tinamït y el variable correspondiente en el modelo.
        :type conv: int | float
        :param combin: Si este variable se debe adicionar o tomar el promedio entre varios pasos.
        :type combin: str

        """
        var = símismo.valid_var(var)

        if var_clima not in Geog.conv_vars:
            raise ValueError(_('El variable climático "{}" no es una posibilidad. Debe ser uno de:\n'
                               '\t{}').format(var_clima, ', '.join(Geog.conv_vars)))

        if combin not in ['prom', 'total', None]:
            raise ValueError(_('"Combin" debe ser "prom", "total", o None, no "{}".').format(combin))

        símismo.vars_clima[var] = {'nombre_extrn': var_clima,
                                   'combin': combin,
                                   'conv': conv}

    def desconectar_var_clima(símismo, var):
        """
        Esta función desconecta un variable climático.

        :param var: El nombre interno del variable en el modelo.
        :type var: str

        """

        símismo.vars_clima.pop(var)

    def cambiar_vals(símismo, valores):
        """
        Esta función cambia el valor de uno o más variables del modelo. Cambia primero el valor en el diccionario
        interno del :class:`Modelo`, y después llama la función :func:`~Modelo.Modelo.cambiar_vals_modelo` para cambiar,
        si necesario, los valores de los variables en el modelo externo.

        :param valores: Un diccionario de variables y sus valores para cambiar.
        :type valores: dict

        """

        símismo._act_vals_dic_var(valores=valores)

        símismo._cambiar_vals_modelo_interno(valores=valores)

    def _cambiar_vals_modelo_interno(símismo, valores):
        """
        Esta función debe cambia el valor de variables en el :class:`Modelo`, incluso tomar acciones para asegurarse
        de que el cambio se hizo en el modelo externo, si aplica.

        :param valores: Un diccionario de variables y sus valores para cambiar.
        :type valores: dict

        """
        raise NotImplementedError

    def cerrar_modelo(símismo):
        """
        Esta función debe tomar las acciones necesarias para terminar la simulación y cerrar el modelo, si aplica.
        Si no aplica, usar ``pass``.
        """
        raise NotImplementedError

    def act_vals_clima(símismo, f_0, f_1):
        """
        Actualiza los variables climáticos. Esta función es la automática para cada modelo. Si necesitas algo más
        complicado (como, por ejemplo, predicciones por estación), la puedes cambiar en tu subclase.

        :param n_paso: El número de pasos para avanzar
        :type n_paso: int
        :param f: La fecha actual.
        :type f: ft.datetime | ft.date
        """

        if not len(símismo.vars_clima):
            return

        # Avisar si arriesgamos perder presición por combinar datos climáticos.
        n_días = (f_1 - f_0).days
        if n_días > 1:
            avisar('El paso es de {} días. Puede ser que las predicciones climáticas pierdan '
                   'en precisión.'.format(n_días))

        f_1 = f_1 - deltarelativo(days=1)

        # La lista de variables climáticos
        vars_clima = list(símismo.vars_clima)
        nombres_extrn = [d['nombre_extrn'] for d in símismo.vars_clima.values()]

        # La lista de maneras de combinar los valores diarios
        combins = [d['combin'] for d in símismo.vars_clima.values()]

        # La lista de factores de conversión
        convs = [d['conv'] for d in símismo.vars_clima.values()]

        # Calcular los datos
        datos = símismo.lugar.comb_datos(vars_clima=nombres_extrn, combin=combins,
                                         f_inic=f_0, f_final=f_1)

        # Aplicar los valores de variables calculados
        for i, var in enumerate(vars_clima):
            # Para cada variable en la lista de clima...

            # El nombre oficial del variable de clima
            var_clima = nombres_extrn[i]

            # El factor de conversión de unidades
            conv = convs[i]

            # Aplicar el cambio
            símismo.cambiar_vals(valores={var: datos[var_clima] * conv})

    def estab_conv_unid_tiempo(símismo, unid_ref, factor):
        """
        Establece, manualmente, el factor de conversión para convertir la unidad de tiempo del modelo a meses.
        Únicamente necesario si Tinamït no logra inferir este factor por sí mismo.

        :param conv: El factor de conversión entre la unidad de tiempo del modelo y un mes.
        :type: float | int

        """

        símismo._conv_unid_tiempo['unid_ref'] = unid_ref
        símismo._conv_unid_tiempo['factor'] = factor

    def dibujar_mapa(símismo, geog, var, directorio, corrida=None, i_paso=None, colores=None, escala=None):
        """
        Dibuja mapas espaciales de los valores de un variable.

        :param geog: La geografía del lugares.
        :type geog: Geografía
        :param var: El variable para dibujar.
        :type var: str
        :param corrida: El nombre de la corrida para dibujar.
        :type corrida: str
        :param directorio: El directorio, relativo al archivo EnvolturasMDS, donde hay que poner los dibujos.
        :type directorio: str
        :param i_paso: Los pasos a los cuales quieres dibujar los egresos.
        :type i_paso: list | tuple | int
        :param colores: La escala de colores para representar los valores del variable.
        :type colores: tuple | list | int
        :param escala: La escala de valores para el dibujo. Si ``None``, será el rango del variable.
        :type escala: list | np.ndarray
        """

        # Validar el nombre del variable.
        var = símismo.valid_var(var)

        # Preparar el nombre del variable para uso en el nombre del archivo.
        nombre_var = valid_nombre_arch(var)

        bd = símismo.leer_resultados(var=var, corrida=corrida)

        if isinstance(i_paso, tuple):
            i_paso = list(i_paso)
        if i_paso is None:
            i_paso = [0, bd.shape[-1]]
        if isinstance(i_paso, int):
            i_paso = [i_paso, i_paso + 1]
        if i_paso[0] is None:
            i_paso[0] = 0
        if i_paso[1] is None:
            i_paso[1] = bd.shape[-1]

        unid = símismo.obt_unidades_var(var)
        if escala is None:
            escala = np.min(bd), np.max(bd)

        # Incluir el nombre de la corrida en el directorio, si no es que ya esté allí.
        if os.path.split(directorio)[1] != corrida:
            dir_corrida = valid_nombre_arch(corrida)
            directorio = os.path.join(directorio, dir_corrida)

        # Crear el directorio, si no existe ya.
        if not os.path.isdir(directorio):
            os.makedirs(directorio)
        else:
            # Si ya existía el directorio, borrar dibujos ya existentes con este nombre (de corridas anteriores).
            for arch in os.listdir(directorio):
                if re.match(valid_nombre_arch(nombre_var), arch):
                    os.remove(os.path.join(directorio, arch))

        for i in range(*i_paso):
            valores = bd[..., i]
            nombre_archivo = os.path.join(directorio, '{}, {}'.format(nombre_var, i))
            geog.dibujar(archivo=nombre_archivo, valores=valores, título=var, unidades=unid,
                         colores=colores, escala_num=escala)

    def valid_var(símismo, var):
        if var in símismo.variables:
            return var
        else:
            raise ValueError(_('El variable "{}" no existe en el modelo "{}". Pero antes de quejarte '
                               'al gerente, sería buena idea verificar '
                               'si lo escrbiste bien.')  # Sí, lo "escrbí" así por propósito. :)
                             .format(var, símismo))

    def obt_info_var(símismo, var):
        var = símismo.valid_var(var)
        return símismo.variables[var]['info']

    def obt_unidades_var(símismo, var):
        var = símismo.valid_var(var)
        return símismo.variables[var]['unidades']

    def obt_val_actual_var(símismo, var):
        var = símismo.valid_var(var)
        return símismo.variables[var]['val']

    def obt_lims_var(símismo, var):
        var = símismo.valid_var(var)
        return símismo.variables[var]['líms']

    def obt_dims_var(símismo, var):
        var = símismo.valid_var(var)
        return símismo.variables[var]['dims']

    def obt_ec_var(símismo, var):
        var = símismo.valid_var(var)
        try:
            return símismo.variables[var]['ec']
        except KeyError:
            return

    def egresos(símismo):
        return [v for v, d_v in símismo.variables.items() if d_v['egreso']]

    def ingresos(símismo):
        return [v for v, d_v in símismo.variables.items() if d_v['ingreso']]

    def paráms(símismo):
        seguros = [v for v, d_v in símismo.variables.items() if d_v['parám']]

        potenciales = [v for v, d_v in símismo.variables.items()
                       if v not in seguros and d_v['ingreso'] is True and not d_v['estado_inicial']]

        return {'seguros': seguros, 'potenciales': potenciales}

    def vars_estado_inicial(símismo):
        return [v for v, d_v in símismo.variables.items() if d_v['estado_inicial']]

    def leer_resultados(símismo, var=None, corrida=None):
        """

        Parameters
        ----------
        var: str | list[str]
        corrida: str

        Returns
        -------

        """

        if isinstance(var, str):
            l_vars = [var]
        else:
            l_vars = var

        # Verificar que existe el variable en este modelo.
        l_vars = [símismo.valid_var(v) for v in l_vars]

        # Si no se especificó corrida especial, tomaremos la corrida más recién.
        if corrida is None:
            if símismo.corrida_activa is None:
                raise ValueError(_('Debes especificar una corrida.'))
            else:
                corrida = símismo.corrida_activa

        res = None
        # Leer de la memoria temporaria, si estamos interesadas en la corrida más recién
        if corrida == símismo.corrida_activa:
            try:
                res = {v: símismo.mem_vars[v] for v in l_vars}
            except KeyError:
                pass
        if res is None:
            res = símismo.leer_arch_resultados(archivo=corrida, var=l_vars)

        if isinstance(var, str):
            return res[var]
        else:
            return res

    @classmethod
    def leer_arch_resultados(cls, archivo, var=None):

        if isinstance(var, str):
            l_vars = [var]
        else:
            l_vars = var

        corr, ext = os.path.splitext(archivo)
        if len(ext):
            ext_potenciales = [ext]
        else:
            ext_potenciales = ['.json', '.csv']
        res = None
        for ex in ext_potenciales:
            arch = corr + ex
            if not os.path.isfile(arch):
                continue
            codif = detectar_codif(arch)
            if ex == '.json':
                with open(arch, 'r', encoding=codif) as d:
                    res = json.load(d)
                res = {ll: np.array(v) for ll, v in res.items() if ll in l_vars}
                break
            elif ex == '.csv':
                res = {}
                with open(arch, encoding=codif) as d:
                    lector = csv.reader(d)
                    for f in lector:
                        grp = re.match('(.*)(\[.*\])$', f[0])
                        if grp:
                            v = grp.group(1)
                            if v in res:
                                res[v].append(f[1:])
                            else:
                                res[v] = [f[1:]]
                        else:
                            if f[0] in l_vars:
                                res[f[0]] = np.array(f[1:], dtype=float)
                for vr, val in res.items():
                    if isinstance(val, list):
                        res[vr] = np.array(val, dtype=float).swapaxes(0, -1)  # eje 0: tiempo, ejes 1+: dims
                res = {ll: np.array(v, dtype=float) for ll, v in res.items()}
                break
            else:
                raise ValueError(_('El formato de datos "{}" no se puede leer al momento.').format(ext))

        if res is None:
            raise FileNotFoundError(_('No se encontró archivo de resultados para "{}".').format(archivo))

        if isinstance(var, str):
            return res[var]
        else:
            return res

    def paralelizable(símismo):
        """
        Indica si el modelo actual se puede paralelizar de manera segura o no. Si implementas una subclase
        paralelizable, reimplementar esta función para devolver ``True``.

        :return: Si el modelo se puede paralelizar (con corridas de nombres distintos) sin encontrar dificultades
          técnicas (por ejemplo, si hay riesgo que las corridas paralelas terminen escribiendo en los mismos
          archivos de egreso).
        :rtype: bool
        """
        return False

    def actualizar_trads(símismo, auto_llenar=True):
        raíz = arbole.Element('xliff', version='1.2')
        arch = arbole.SubElement(raíz, 'file', datatype='Modelo Tinamït', original=símismo.nombre)
        arch.set('source-language', símismo.leng_orig)
        cuerpo = arbole.SubElement(arch, 'body')

        for v, d_v in símismo.variables.items():
            grupo = arbole.SubElement(cuerpo, 'group', id=v)

            trans_nombre = arbole.SubElement(grupo, 'trans-unit')
            fnt = arbole.SubElement(trans_nombre, 'source', lang=símismo.leng_orig)
            fnt.text = v

            trans_info = arbole.SubElement(grupo, 'trans-unit')
            fnt = arbole.SubElement(trans_info, 'source', lang=símismo.leng_orig)
            fnt.text = d_v['info']

            trans_unids = arbole.SubElement(grupo, 'trans-unit')
            fnt = arbole.SubElement(trans_unids, 'source', lang=símismo.leng_orig)
            fnt.text = d_v['unidades']

    def cambiar_lengua(símismo, lengua):
        pass

    def agregar_lengua(símismo, lengua):
        pass

    def especificar_micro_calib(símismo, var, método=None, paráms=None, líms_paráms=None, escala=None,
                                ops_método=None):

        # Verificar el variable
        var = símismo.valid_var(var)

        if 'ec' not in símismo.variables[var]:
            raise ValueError(_('El variable "{}" no tiene ecuación asociada.').format(var))

        # Especificar la micro calibración.
        símismo.info_calibs['micro calibs'][var] = {
            'escala': escala,
            'método': método,
            'ops_método': ops_método,
            'paráms': paráms,
            'líms_paráms': líms_paráms
        }

    def verificar_micro_calib(símismo, var, en=None, escala=None):
        """
        Comprueba una microcalibración a pequeña (o grande) escala. Útil para comprobar calibraciones sin perder
        mucho tiempo calculándolas para toda la región de interés.

        Parameters
        ----------
        var : str
            El variable de interés.

        en : str
            Dónde hay que calibrar. Por ejemplo, calibrar en el departamento de Tz'olöj Ya'. Si no se especifica,
            se tomará la región geográfica en su totalidad. Solamente aplica si la base de datos vinculada tiene
            geografía asociada.

        escala : str
            La escala a la cual calibrar. Por ejemplo, calibrar al nivel municipal en el departamento de Tz'olöj Ya'.
            Si no se especifica, se tomará la escala correspondiendo a `en`. Solamente aplica si la base de datos
            vinculada tiene geografía asociada.

        Returns
        -------
        dict[str, dict]
            La calibración completada.

        """

        # Efectuar la calibración del variable.
        return símismo._calibrar_var(var=var, en=en, escala=escala)

    def efectuar_micro_calibs(símismo, en=None, escala=None):
        """

        Parameters
        ----------
        en : str
            Dónde hay que calibrar. Por ejemplo, calibrar en el departamento de Tz'olöj Ya'. Si no se especifica,
            se tomará la región geográfica en su totalidad. Solamente aplica si la base de datos vinculada tiene
            geografía asociada.

        escala : str
            La escala a la cual calibrar. Por ejemplo, calibrar al nivel municipal en el departamento de Tz'olöj Ya'.
            Si no se especifica, se tomará la escala correspondiendo a `en`. Solamente aplica si la base de datos
            vinculada tiene geografía asociada.

        Returns
        -------
        dict
            La calibración.
        """

        # Borramos calibraciones existentes
        símismo.calibs.clear()

        # Para cada microcalibración...
        for var, d_c in símismo.info_calibs['micro calibs'].items():

            # Si todavía no se ha calibrado este variable...
            if var not in símismo.calibs:

                # Efectuar la calibración
                calib = símismo._calibrar_var(var=var, en=en, escala=escala, hermanos=True)

                # Guardar las calibraciones para este variable y todos los otros variables que potencialmente
                # fueron calibrados al mismo tiempo.
                for v in calib:
                    símismo.calibs[v] = calib[v]

    def conectar_geog(símismo, geog):
        símismo.geog = geog

    def desconectar_geog(símismo):
        símismo.geog = None

    def conectar_datos(símismo, datos, corresp_vars=None):
        if isinstance(datos, SuperBD):
            símismo.datos = datos
        elif isinstance(datos, Datos):
            símismo.datos = SuperBD('Autogen', bds=datos)
        elif isinstance(datos, pd.DataFrame):
            símismo.datos = SuperBD('Autogen', bds=DatosRegión('Autogen', datos))
        elif isinstance(datos, dict):
            símismo.datos = SuperBD('Autogen', bds=DatosRegión('Autogen', pd.DataFrame(datos)))
        else:
            raise TypeError

        if corresp_vars is not None:
            for var, var_bd in corresp_vars.items():
                símismo.conectar_var_a_datos(var=var, var_bd=var_bd)

    def conectar_var_a_datos(símismo, var, var_bd=None):
        if var_bd is None:
            var_bd = var
        var = símismo.valid_var(var)
        símismo.conex_var_datos[var] = var_bd

    def desconectar_var_datos(símismo, var):
        var = símismo.valid_var(var)
        símismo.conex_var_datos.pop(var)

    def desconectar_datos(símismo):
        símismo.datos = None

    def _calibrar_var(símismo, var, en=None, escala=None, hermanos=False):

        if símismo.datos is None:
            raise ValueError()

        # La lista de variables que hay que calibrar con este.
        # l_vars = símismo._obt_vars_asociados(var, enforzar_datos=True, incluir_hermanos=hermanos)
        l_vars = {}  # para hacer: arreglar problemas de determinar paráms vs. otras ecuaciones

        # Preparar la ecuación
        ec = símismo.variables[var]['ec']
        if not len(Ecuación(ec).variables()):
            raise NotImplementedError  # Falta implementar el caso de un constante

        # El objeto de calibración.
        mod_calib = CalibradorEc(
            ec=ec, var_y=var, otras_ecs={v: símismo.variables[v]['ec'] for v in l_vars},
            nombres_equiv=símismo.conex_var_datos
        )

        # El método de calibración
        método = símismo.info_calibs['micro calibs'][var]['método']
        líms_paráms = símismo.info_calibs['micro calibs'][var]['líms_paráms']
        paráms = símismo.info_calibs['micro calibs'][var]['paráms']
        ops = símismo.info_calibs['micro calibs'][var]['ops_método']

        # Aplicar límites automáticos
        if líms_paráms is None:
            if paráms is not None:
                líms_paráms = {p: símismo.variables[p]['líms'] for p in paráms}
            else:
                líms_paráms = {p: símismo.variables[p]['líms'] for p in símismo.variables}

        # Efectuar la calibración.
        calib = mod_calib.calibrar(
            paráms=paráms, líms_paráms=líms_paráms, método=método, bd_datos=símismo.datos, geog=símismo.geog,
            en=en, escala=escala, ops_método=ops
        )

        # Reformatear los resultados
        resultado = {}
        for lg, d_lg in calib.items():
            if d_lg is None:
                continue
            for p in d_lg:
                if p not in resultado:
                    resultado[p] = {}
                resultado[p][lg] = d_lg[p]

        return resultado

    def _obt_vars_asociados(símismo, var, enforzar_datos=False, incluir_hermanos=False):
        """
        Obtiene los variables asociados con un variable de interés.

        Parameters
        ----------
        var : str
            El variable de interés.
        enforzar_datos : bool
            Si buscamos únicamente variables que tienen datos en la base de datos vinculada.
        incluir_hermanos :
            Si incluyemos los hermanos del variable (es decir, otros variables que se computan a base de los parientes
            del variable de interés.

        Returns
        -------
        set
            El conjunto de todos los variables vinculados.

        Raises
        ------
        ValueError
            Si no todos los variables asociados tienen ecuación especificada.
        RecursionError
            Si `enforzar_datos == True` y no hay suficientemente datos disponibles para encontrar parientes con datos
            para todos los variables asociados con el variable de interés.
        """

        # La base de datos
        bd_datos = símismo.datos if enforzar_datos else None

        # El diccionario de variables
        d_vars = símismo.variables

        # Una función recursiva queda muy útil en casos así.
        def _sacar_vars_recurs(v, c_v=None, sn_dts=None):
            """
            Una función recursiva para sacar variables asociados con un variable de interés.
            Parameters
            ----------
            v : str
                El variable de interés.
            c_v : set
                El conjunto de variables asociados (parámetro de recursión).

            Returns
            -------
            set
                El conjunto de variables asociados.

            """

            # Para evitar problemas de recursión en Python.
            if c_v is None:
                c_v = set()
            if sn_dts is None:
                sn_dts = set()

            # Verificar que el variable tenga ecuación
            if 'ec' not in d_vars[v]:
                raise ValueError(_('El variable "{}" no tiene ecuación.').format(v))

            # Los parientes del variable
            parientes = d_vars[v]['parientes']

            # Agregar los parientes al conjunto de variables vinculados
            c_v.update(parientes)

            for p in parientes:
                # Para cada pariente...

                p_bd = símismo.conex_var_datos[p] if p in símismo.conex_var_datos else p
                if bd_datos is not None and p_bd not in bd_datos:
                    # Si tenemos datos y este variable pariente no existe, tendremos que buscar sus parientes también.

                    # ...pero si ya encontramos este variable en otra recursión, quiere decir que no tenemos
                    # suficientemente datos y que estamos andando en círculos.
                    if p in sn_dts:
                        raise RecursionError(
                            _('Estamos andando en círculos buscando variables con datos disponibles. Debes '
                              'especificar más datos. Puedes empezar con uno de estos variables: {}'
                              ).format(', '.join(sn_dts))
                        )

                    # Acordarse que ya intentamos buscar parientes con datos para este variable
                    sn_dts.add(p)

                    # Seguir con la recursión
                    _sacar_vars_recurs(v=p, c_v=c_v, sn_dts=sn_dts)

                if incluir_hermanos:
                    # Si incluyemos a los hermanos, agregarlos y sus parientes aquí.
                    hijos = d_vars[p]['hijos']
                    c_v.update(hijos)
                    for h in hijos:
                        if h not in c_v:
                            _sacar_vars_recurs(v=h, c_v=c_v, sn_dts=sn_dts)

            # Devolver el conjunto de variables asociados
            return c_v

        return _sacar_vars_recurs(var)

    def borrar_micro_calib(símismo, var):
        try:
            símismo.info_calibs['micro calibs'].pop(var)
        except KeyError:
            raise ValueError(_('El variable "{}" no está asociado con una microcalibración.').format(var))

    def borrar_info_calibs(símismo):
        símismo.info_calibs['micro calibs'].clear()
        símismo.info_calibs['calibs'].clear()

    def borrar_calibs_calc(símismo):
        símismo.calibs.clear()

    def calibrar(símismo, paráms, líms_paráms=None, var=None, n_iter=500, método='mle'):

        if var is None:
            l_vars = None
        elif isinstance(var, str):
            l_vars = [símismo.valid_var(var)]
        else:
            l_vars = [símismo.valid_var(v) for v in var]

        if líms_paráms is None:
            líms_paráms = {}
        for p in paráms:
            if p not in líms_paráms:
                líms_paráms[p] = símismo.obt_lims_var(p)
        líms_paráms = {ll: v for ll, v in líms_paráms.items() if ll in paráms}

        calibrador = CalibradorMod(símismo)
        d_calibs = calibrador.calibrar(
            paráms=paráms, método=método, líms_paráms=líms_paráms, n_iter=n_iter, l_vars=l_vars
        )
        símismo.calibs.update(d_calibs)

    def validar(símismo, var=None, t_final=None):

        if var is None:
            l_vars = [v for v in símismo.datos.vars if v in símismo.variables or v in símismo.conex_var_datos.values()]
        elif isinstance(var, str):
            l_vars = [var]
        else:
            l_vars = var
        l_vars = [símismo.valid_var(v) for v in l_vars]

        obs = símismo.datos.obt_datos(l_vars, tipo='regional')[l_vars]
        if t_final is None:
            t_final = len(obs) - 1
        d_vals_prms = {p: d_p['dist'] for p, d_p in símismo.calibs.items()}
        n_vals = len(list(d_vals_prms.values())[0])
        vals_inic = [{p: v[í] for p, v in d_vals_prms.items()} for í in range(n_vals)]
        res_simul = símismo.simular_grupo(
            t_final, vals_inic=vals_inic, vars_interés=l_vars, combinar=False, paralelo=False
        )

        matrs_simul = {vr: np.array([d[vr] for d in res_simul.values()]) for vr in l_vars}

        resultados = validar_resultados(obs=obs, matrs_simul=matrs_simul)
        return resultados

    def __str__(símismo):
        return símismo.nombre

    def __getinitargs__(símismo):
        return símismo.nombre,

    def __copy__(símismo):
        copia = símismo.__class__(*símismo.__getinitargs__())
        copia.vals_inic = símismo.vals_inic
        copia.vars_clima = símismo.vars_clima
        copia._conv_unid_tiempo = símismo._conv_unid_tiempo

        return copia

    def __getstate__(símismo):
        d = {
            'args_inic': símismo.__getinitargs__(),
            'vals_inic': símismo.vals_inic,
            'vars_clima': símismo.vars_clima,
            '_conv_unid_tiempo': símismo._conv_unid_tiempo
        }
        return d

    def __setstate__(símismo, estado):
        símismo.__init__(*estado['args_inic'])
        símismo.vals_inic = estado['vals_inic']
        símismo.vars_clima = estado['vars_clima']
        símismo._conv_unid_tiempo = estado['_conv_unid_tiempo']


def _correr_modelo(x):
    """
    Función para inicializar y correr un modelo :class:`SuperConectado`.

    :param x: Los parámetros. El primero es el modelo, el segundo el diccionario de valores iniciales (El primer
      nivel de llaves es el nombre del submodelo y el segundo los nombres de los variables con sus valores
      iniciales), y el tercero es el diccionario de argumentos para pasar al modelo.
    :type x: tuple[SuperConectado, dict[str, dict[str, float | int | np.ndarray]], dict]

    """
    estado_mod, vls_inic, d_args = x

    mod = pickle.loads(estado_mod)

    # Inicializar los variables y valores iniciales. Esto debe ser adentro de la función llamada por
    # Proceso, para que los valores iniciales se apliquen en su propio proceso (y no en el modelo
    # original).
    if vls_inic is not None:
        mod.inic_vals_vars(vls_inic)

    # Después, simular el modelo y devolver los resultados, si hay.
    return mod.simular(**d_args)


def _gen_dic_ops_corridas(nombre_corrida, combinar, tipos_ops, opciones):
    # Una matriz con el número de valores distintos para cada opción, guardando únicamente las opciones con valores
    # múltiples.
    l_n_ops = np.array(
        [
            len(v) for ll, v in opciones.items()  # El número de opciones
            if tipos_ops[ll] in [list, dict]  # Si no es de valor único
        ]
    )
    # Una lista con el nombre de cada opción (p. ej., "paso", etc.) con valores múltiples.
    l_nmbs_ops_var = [
        ll for ll, v in opciones.items()  # El nombre de la opción
        if tipos_ops[ll] in [list, dict]  # Si no es de valor único
    ]

    # Crear el diccionario de corridas
    if combinar:
        # Si estamos combinando las opciones...

        # El nombre de corrida no puede ser una lista si estamos combinando las opciones
        if isinstance(nombre_corrida, list):
            raise TypeError(_('No puedes especificar una lista de nombres de corridas si estás'
                              ' simulando todas las combinaciones posibles de las opciones.'))

        # El número de corridas es el producto del número de valores por opción.
        n_corridas = int(np.prod(l_n_ops))

        dic_ops = {}  # Un diccionario de nombres de simulación y sus opciones de corrida

        # Poblar el diccionario de opciones iniciales
        ops = {}  # Las opciones iniciales
        nombre = []  # Una lista que se convertirá en el nombre de la opción
        for ll, op in opciones.items():
            # Para cada opción...

            if tipos_ops[ll] == 'val':
                # Si no hay valores múltiples, su único valor será su valor permanente.
                ops[ll] = op

            else:
                # Pero si tenemos valores múltiples, damos el primero de la lista o diccionario para empezar.
                if tipos_ops[ll] == dict:
                    # Si es un diccionario...

                    # Tomar el nombre de la primera corrida especificada en el diccionario
                    id_op = list(op)[0]

                    # ...y el valor para esta corrida
                    ops[ll] = op[id_op]

                    # Guardar el nombre también.
                    nombre.append(id_op)

                else:
                    # Si es una lista...

                    ops[ll] = op[0]  # Empezar con el primer valor de la lista

                    # Convertir el índice del valor a un nombre para las corridas
                    nombre.append(f'{ll}0')

        # Una matriz con el número cumulativo de combinaciones de opciones
        l_n_ops_cum = np.roll(l_n_ops.cumprod(), 1)  # Pasamos el número final al principio
        if len(l_n_ops_cum):
            l_n_ops_cum[0] = 1  # ... y reemplazamos el número ahora inicial con ``1``.
        else:
            l_n_ops_cum = [1]  # ... si no tenemos combinaciones que hacer, darle ``1``

        # Crear la lista de diccionarios de opciones para cada corrida.
        for í_c in range(n_corridas):
            # Para cada corrida...

            # Calcular el índice del valor actual para cada opción que tiene valores múltiples
            í_ops = [int(np.floor(í_c / l_n_ops_cum[n]) % l_n_ops[n]) for n in range(l_n_ops.shape[0])]

            # Para cada opción...
            for í_op, n in enumerate(í_ops):

                # Sacamos el nombre de la opción actual
                nmbr_op = l_nmbs_ops_var[í_op]
                op = opciones[nmbr_op]  # El valor de la opción

                # Aplicar los cambios al diccionario transitorio de opciones
                if tipos_ops[nmbr_op] == list:
                    # Si la opción está en formato de lista...

                    # Guardar su valor
                    ops[nmbr_op] = op[n]

                    # Y cambiar su nombre
                    nombre[í_op] = f'{nmbr_op}{n}'

                elif tipos_ops[nmbr_op] == dict:
                    # Sino, es un diccionario

                    # Guardar nu nombre y valor
                    id_op = list(op)[n]
                    ops[nmbr_op] = op[id_op]
                    nombre[í_op] = id_op

                else:
                    raise TypeError(_('Tipo de variable "{}" erróneo. Debería ser imposible llegar hasta este '
                                      'error.'.format(type(op))))

            # Concatenar el nombre y guardar una copia del diccionario transitorio de opciones.
            dic_ops[' '.join(nombre)] = ops.copy()

        # Formatear las corridas con sus nombres de corridas.
        corridas = {
            '{}{}'.format(nombre_corrida + ('_' if nombre_corrida and ll else ''), ll): ops
            for ll, ops in dic_ops.items()
        }  # type: dict[str, dict]

        # Y, por fin, si solamente tenemos una corrida que hacer, asegurarse que tenga un nombre.
        if len(corridas) == 1 and list(corridas)[0] == '':
            corridas['Corrida Tinamït'] = corridas.pop('')

    else:
        # Si no estamos haciendo todas las combinaciones posibles de opciones, es un poco más fácil.

        # Asegurarse de que todas las opciones múltiples sean o diccionarios, o listas
        if any(t is dict for t in tipos_ops.values()):
            if any(t is list for t in tipos_ops.values()):
                raise TypeError(
                    _('Si no estás haciendo combinaciones, no puedes combinar diccionarios con listas.'))
            frmt = dict
        elif any(t is list for t in tipos_ops.values()):
            frmt = list
        else:
            frmt = 'val'

        if frmt is dict:
            # Verificar que las llaves sean consistentes
            lls_dics = next((op.keys() for nmb, op in opciones.items() if tipos_ops[nmb] == dict), None)  # Las llaves
            for nmb, op in opciones.items():
                # Asegurarse que las llaves de esta opción sean iguales al estándar.
                if tipos_ops[nmb] == dict and op.keys() != lls_dics:
                    raise ValueError(_('Las llaves de diccionario de cada opción deben ser iguales.'))

        # Asegurarse de que todas las opciones tengan el mismo número de opciones.
        tmñs_únicos = np.unique(l_n_ops)
        if tmñs_únicos.size == 1:
            n_corridas = tmñs_únicos[0]  # El número de corridas
        else:
            raise ValueError(_('Si `combinar` == ``False``, todas las opciones en forma de lista o diccionario '
                               'deben tener el mismo número de opciones.'))

        # Preparar la lista de nombres de corridas
        if isinstance(nombre_corrida, str):
            # Si el nombre especificado para la corrida queda en formato texto...

            # ...tenemos que agregarle algo para distinguir entre las varias corridas.
            if frmt is dict:
                # Si hay diccionarios de opciones con nombres de corridas, utilizar éstas.
                l_nombres = next(list(opciones[nmb]) for nmb, t in tipos_ops.items() if t is dict)

                # Generar el diccionario de nombres de corridas con sus valores de simulación correspondientes.
                corridas = {
                    '{}_{}'.format(nombre_corrida, nmb_corr):
                        {
                            ll: op[nmb_corr] if tipos_ops[ll] is dict else op for ll, op in opciones.items()
                        }
                    for nmb_corr in l_nombres
                }
            else:
                # Sino, las daremos nombres según números consecutivos
                corridas = {
                    '{}_{}'.format(nombre_corrida, i):
                        {
                            nmb: op[i] if tipos_ops[nmb] is list else op for nmb, op in opciones.items()
                        }
                    for i in range(n_corridas)
                }

        elif isinstance(nombre_corrida, list):
            # Si tenemos una lista de nombres de corridas...

            # Asegurarse que tenga el tamaño necesario
            if len(nombre_corrida) != n_corridas:
                raise ValueError(
                    _('Una lista de nombres de corrida debe tener el mismo número de nombres ("{}") que hay '
                      'valores de opciones en la simulación ("{}").').format(len(nombre_corrida), n_corridas)
                )

            if frmt is dict:
                raise ValueError(
                    _('No puedes especificar una lista de nombres de corridas si tienes opciones en '
                      'formato de diccionario.')
                )

            # Generar el diccionario de corridas
            corridas = {
                nmb: {ll: op[i] if tipos_ops[ll] is list else op for ll, op in opciones.items()}
                for i, nmb in enumerate(nombre_corrida)
            }

        else:
            raise TypeError(_('El nombre de corrida debe ser o una cadena de texto, o una lista de cadenas '
                              'de texto.'))

    return corridas
