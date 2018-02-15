import datetime as ft
import os
import pickle
import re
import threading
from copy import copy as copiar
from warnings import warn as avisar

import numpy as np
from dateutil.relativedelta import relativedelta

from tinamit import _
from tinamit.BF import EnvolturaBF
from tinamit.EnvolturaMDS import generar_mds
from tinamit.Geog.Geog import Lugar
from tinamit.MDS import EnvolturaMDS
from tinamit.Modelo import Modelo
from tinamit.Unidades.Unidades import convertir


class SuperConectado(Modelo):
    """
    Esta clase representa el más alto nivel posible de modelo conectado. Tiene la función muy útil de poder conectar
    instancias de sí misma, así permitiendo la conexión de números arbitrarios de modelos.
    """

    def __init__(símismo, nombre="SuperConectado"):
        """
        El nombre automático para este modelo es "SuperConectado". Si vas a conectar más que un modelo
        :class:`.SuperConectado` en un modelo jerárquico, asegúrate de darle un nombre distinto al menos a un de ellos.

        :param nombre: El nombre del modelo :class:`.SuperConectado`.
        :type nombre: str

        """

        # Un diccionario de los modelos que se van a conectar en este modelo. Tiene la forma general
        # {'nombre_modelo': objecto_modelo,
        #  'nombre_modelo_2': objecto_modelo_2}
        símismo.modelos = {}  # type: dict[str, Modelo]

        # Una lista de las conexiones entre los modelos.
        símismo.conexiones = []

        # Un diccionario para aceder rápidamente a las conexiones.
        símismo.conex_rápida = {}

        # Un diccionario con la información de conversiones de unidades de tiempo entre los dos modelos conectados.
        # Tiene la forma general:
        # {'nombre_modelo_1': factor_conv,
        # {'nombre_modelo_2': factor_conv}
        # Al menos uno de los dos factores siempre será = a 1.
        símismo.conv_tiempo = {}
        símismo.conv_tiempo_dudoso = False  # Para acordarse si Tinamït tuvo que adivinar la conversión o no.

        # Inicializamos el SuperConectado como todos los Modelos.
        super().__init__(nombre=nombre)

    def estab_modelo(símismo, modelo):
        """
        Esta función agrega un modelo al SuperConectado. Una vez que dos modelos estén agregados, se pueden conectar
        y simular juntos.

        :param modelo: El modelo para agregar.
        :type modelo: tinamit.Modelo.Modelo

        """

        # Si ya hay dos modelos conectados, no podemos conectar un modelo más.
        if len(símismo.modelos) >= 2:
            raise ValueError(_('Ya hay dos modelo conectados. Desconecta uno primero o emplea una instancia de'
                               'SuperConectado para conectar más que 2 modelos.'))

        # Si ya se conectó otro modelo con el mismo nombre, avisarlo al usuario.
        if modelo.nombre in símismo.modelos:
            avisar(_('El modelo {} ya existe. El nuevo modelo reemplazará el modelo anterior.').format(modelo.nombre))

        # Agregar el nuevo modelo al diccionario de modelos.
        símismo.modelos[modelo.nombre] = modelo

        # Ahora, tenemos que agregar los variables del modelo agregado al diccionaro de variables de este modelo
        # también. Se prefija el nombre del modelo al nombre de su variable para evitar posibilidades de nombres
        # desduplicados.
        for var in modelo.variables:
            nombre_var = '{mod}_{var}'.format(var=var, mod=modelo.nombre)
            símismo.variables[nombre_var] = modelo.variables[var]

        # Establecemos las unidades de tiempo del modelo SuperConectado según las unidades de tiempo de sus submodelos.
        símismo.unidad_tiempo = símismo.obt_unidad_tiempo()

    def inic_vars(símismo):
        """
        Esta función no es necesaria, porque :func:`~tinamit.Conectado.Conectado.estab_modelo` ya llama las funciones
        necesarias, :func:`~tinamit.Modelo.inic_vars` de los submodelos.

        """
        pass

    def obt_unidad_tiempo(símismo):
        """
        Esta función devolverá las unidades de tiempo del modelo conectado. Dependerá de los submodelos.
        Si los dos submodelos tienen las mismas unidades, esta será la unidad del modelo conectado también.
        Si los dos tienen unidades distintas, intentaremos encontrar la conversión entre los dos y después se
        considerará como unidad de tiempo de base la más grande de los dos. Por ejemplo, si se conecta un modelo
        con una unidad de tiempo de meses con un modelo de unidad de año, se aplicará una unidad de tiempo de سال
        al modelo conectado.

        Después se actualiza el variable símismo.conv_tiempo para guardar en memoria la conversión necesaria entre
        los pasos de los dos submodelos.

        Se emplea las clase `~tinamit.Unidades.Unidades` para convertir unidades.

        :return: El tiempo de paso del modelo SuperConectado.
        :rtype: str

        """

        # Si todavía no se han conectado 2 modelos, no hay nada que hacer.
        if len(símismo.modelos) < 2:
            return None

        # Identificar las unidades de los dos submodelos.
        l_mods = list(símismo.modelos)

        unid_mod_1 = símismo.modelos[l_mods[0]].unidad_tiempo
        unid_mod_2 = símismo.modelos[l_mods[1]].unidad_tiempo

        # Una función auxiliar aquí para verificar si el factor de conversión es un nombre entero o no.
        def verificar_entero(factor):

            if int(factor) != factor:
                # Si el factor no es un número entero, avisar antes de redondearlo.
                avisar('Las unidades de tiempo de los dos modelos ({} y {}) no tienen denominator común.'
                       'Se aproximará la conversión.'.format(unid_mod_1, unid_mod_2))

            # Devolver la mejor aproximación entera
            return round(factor)

        if unid_mod_1 == unid_mod_2:
            # Si las unidades son idénticas, ya tenemos nuestra respuesta.
            símismo.conv_tiempo[l_mods[0]] = 1
            símismo.conv_tiempo[l_mods[1]] = 1

            return unid_mod_1

        else:
            # Sino, intentemos convertir automáticamente
            try:
                factor_conv = convertir(de=unid_mod_1, a=unid_mod_2)

            except ValueError:
                # Si no lo logramos, hay un error.
                símismo.conv_tiempo_dudoso = True
                factor_conv = 1

            if factor_conv > 1:
                # Si la unidad de tiempo del primer modelo es más grande que la del otro...

                # Verificar que sea un factor entero
                factor_conv = verificar_entero(factor_conv)

                # ...y usar esta como unidad de tiempo y guardar el factor de conversión.
                símismo.conv_tiempo[l_mods[0]] = 1
                símismo.conv_tiempo[l_mods[1]] = factor_conv

                return unid_mod_1

            else:
                # Si la unidad de tiempo del segundo modelo es la más grande...

                # Tomar el recíproco de la conversión
                factor_conv = 1 / factor_conv

                # Verificar que sea un factor entero
                factor_conv = verificar_entero(factor_conv)

                # ...y usar las unidades del segundo modelo como referencia.
                símismo.conv_tiempo[l_mods[1]] = 1
                símismo.conv_tiempo[l_mods[0]] = factor_conv

                return unid_mod_2

    def estab_conv_tiempo(símismo, mod_base, conv):
        """
        Esta función establece la conversión de tiempo entre los dos modelos (útil para unidades que Tinamit
        no reconoce).

        :param mod_base: El modelo con la unidad de tiempo mayor.
        :type mod_base: str

        :param conv: El factor de conversión con la unidad de tiempo del otro modelo.
        :type conv: int

        """

        # Veryficar que el modelo de base es un nombre de modelo válido.
        if mod_base not in símismo.modelos:
            raise ValueError(_('El modelo "{}" no existe en este modelo conectado.').format(mod_base))

        # Identificar el modelo que no sirve de referencia para la unidad de tiempo
        l_mod = list(símismo.modelos)
        mod_otro = l_mod[(l_mod.index(mod_base) + 1) % 2]

        # Establecer las conversiones
        símismo.conv_tiempo[mod_base] = 1
        símismo.conv_tiempo[mod_otro] = conv

        # Y guardar la unidad de tiempo.
        símismo.unidad_tiempo = símismo.modelos[mod_base].unidad_tiempo

        # Si había duda acerca de la conversión de tiempo, ya no hay.
        símismo.conv_tiempo_dudoso = False

    def cambiar_vals_modelo_interno(símismo, valores):
        """
        Esta función cambia los valores del modelo. A través de la función :func:`~tinamit.Conectado.cambiar_vals`, se
        vuelve recursiva.

        :param valores: El diccionario de nombres de variables para cambiar. Hay que prefijar cada nombre de variable
          con el nombre del submodelo en en cual se ubica (separados con un ``_``), para que Tinamit sepa en cuál
          submodelo se ubica cada variable.
        :type valores: dict

        """

        # Para cada nombre de variable...
        for nombre_var, val in valores.items():
            # Primero, vamos a sacar el nombre del variable y el nombre del submodelo.
            nombre_mod, var = nombre_var.split('_', 1)

            # Ahora, pedimos a los submodelos de hacer los cambios en los modelos externos, si hay.
            símismo.modelos[nombre_mod].cambiar_vals(valores={var: val})

    def _conectar_clima(símismo, n_pasos, lugar, fecha_inic, tcr, recalc):
        """
        Esta función conecta el clima de un lugares con el modelo Conectado.

        :param  n_pasos: El número de pasos para la simulación.
        :type n_pasos: int
        :param lugar: El lugares.
        :type lugar: Lugar
        :param fecha_inic: La fecha inicial de la simulación.
        :type fecha_inic: ft.date | ft.datetime | str | int
        :param tcr: El escenario climático según el sistema de la IPCC (2.6, 4.5, 6.0, o 8.5)
        :type tcr: str | float

        """

        # Conectar el lugares
        símismo.lugar = lugar
        for m in símismo.modelos.values():
            m.lugar = lugar

        # Calcular la fecha final
        fecha_final = None
        n_días = None
        try:
            n_días = convertir(de=símismo.unidad_tiempo, a='días', val=n_pasos)
        except ValueError:
            for m in símismo.modelos.values():
                try:
                    n_días = convertir(de=m.unidad_tiempo, a='días', val=símismo.conv_tiempo[m.nombre] * n_pasos)
                    continue
                except ValueError:
                    pass

        if n_días is not None:
            fecha_final = fecha_inic + ft.timedelta(int(n_días))

        else:
            n_meses = None
            try:
                n_meses = convertir(de=símismo.unidad_tiempo, a='meses', val=n_pasos)
            except ValueError:
                for m in símismo.modelos.values():
                    try:
                        n_meses = convertir(de=m.unidad_tiempo, a='meses', val=símismo.conv_tiempo[m.nombre] * n_pasos)
                        continue
                    except ValueError:
                        pass
            if n_meses is not None:
                fecha_final = fecha_inic + relativedelta(months=int(n_meses) + 1)

        if fecha_final is None:
            raise ValueError

        # Obtener los datos de lugares
        lugar.prep_datos(fecha_inic=fecha_inic, fecha_final=fecha_final, tcr=tcr, regenerar=recalc)

    def act_vals_clima(símismo, n_paso, f):
        """
        Actualiza los variables climáticos según la fecha.

        :param n_paso: El número de pasos en adelante para cuales tenemos que obtener predicciones.
        :type n_paso: int
        :param f: La fecha actual.
        :type f: ft.datetime | ft.date

        """

        for nombre, mod in símismo.modelos.items():
            mod.act_vals_clima(n_paso=símismo.conv_tiempo[nombre] * n_paso, f=f)

    def paralelizable(símismo):
        """
        Un modelo :class:`SuperConectado` es paralelizable si todos sus submodelos lo son.

        :return: Si todos los submodelos de este modelo son paralelizables.
        :rtype: bool
        """

        return all(mod.paralelizable() for mod in símismo.modelos.values())

    def simular(símismo, tiempo_final, paso=1, nombre_corrida='Corrida Tinamït', fecha_inic=None, lugar=None, tcr=None,
                recalc=True, clima=False):
        """
        Simula el modelo :class:`~tinamit.Conectado.SuperConectado`.

        :param tiempo_final: El tiempo final de la simulación.
        :type tiempo_final: int

        :param paso: El paso (intervalo de intercambio de valores entre los dos submodelos).
        :type paso: int

        :param nombre_corrida: El nombre de la corrida.  El valor automático es ``Corrida Tinamit``.
        :type nombre_corrida: str

        :param fecha_inic: La fecha inicial de la simulación. Necesaria para simulaciones con cambios climáticos.
        :type fecha_inic: ft.datetime | ft.date | int | str

        :param lugar: El lugares de la simulación.
        :type lugar: Lugar

        :param tcr: El escenario climático según el sistema de la IPCC (``2.6``, ``4.5``, ``6.0``, o ``8.5``). ``0`` da
          el clima histórico.
        :type tcr: str | float | int

        :param recalc: Si quieres recalcular los datos climáticos, si ya existen.
        :type recalc: bool

        :param clima: Si es una simulación de cambios climáticos o no.
        :type clima: bool

        """

        # ¡No se puede simular con menos (o más) de dos modelos!
        if len(símismo.modelos) < 2:
            raise ValueError(_('Hay que conectar dos modelos antes de empezar una simulación.'))

        # Si no hay conversión de tiempo entre los dos modelos, no se puede simular nada.
        if not len(símismo.conv_tiempo):
            raise ValueError(_('Hay que especificar la conversión de unidades de tiempo con '
                               '.estab_conv_tiempo() antes de correr la simulación.'))

        # Si no estamos seguro de la conversión de unidades de tiempo, decirlo aquí.
        if símismo.conv_tiempo_dudoso:
            l_mods = list(símismo.modelos)
            unid_mod_1 = símismo.modelos[l_mods[0]].unidad_tiempo
            unid_mod_2 = símismo.modelos[l_mods[1]].unidad_tiempo
            avisar(_('\nNo se pudo inferir la conversión de unidades de tiempo entre {} y {}.\n'
                     'Especificarla con la función .estab_conv_tiempo().\n'
                     'Por el momento pusimos el factor de conversión a 1, pero probablemente no es lo que quieres.')
                   .format(unid_mod_1, unid_mod_2))

        # Calcular el número de pasos necesario
        n_pasos = int(tiempo_final / paso)

        # Conectar el clima, si necesario
        if clima:
            if lugar is None:
                raise ValueError(_('Hay que especificar un lugares para incorporar el clima.'))
            else:
                if fecha_inic is None:
                    raise ValueError(_('Hay que especificar la fecha inicial para simulaciones de clima'))
                elif isinstance(fecha_inic, ft.date):
                    # Formatear la fecha inicial
                    pass
                elif isinstance(fecha_inic, ft.datetime):
                    fecha_inic = fecha_inic.date()
                elif isinstance(fecha_inic, int):
                    año = fecha_inic
                    día = mes = 1
                    fecha_inic = ft.date(year=año, month=mes, day=día)
                elif isinstance(fecha_inic, str):
                    try:
                        fecha_inic = ft.datetime.strptime(fecha_inic, '%d/%m/%Y').date()
                    except ValueError:
                        raise ValueError(_('La fecha inicial debe ser en formato "día/mes/año", por ejemplo '
                                           '"24/12/2017".'))

                if tcr is None:
                    tcr = 8.5
                símismo._conectar_clima(n_pasos=n_pasos, lugar=lugar, fecha_inic=fecha_inic, tcr=tcr, recalc=recalc)

        # Iniciamos el modelo.
        símismo.iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida=nombre_corrida)

        # Si hay fecha inicial, tenemos que guardar cuenta de donde estamos en el calendario
        if fecha_inic is not None:
            fecha_act = fecha_inic
        else:
            fecha_act = None

        # Hasta llegar al tiempo final, incrementamos el modelo.
        for i in range(n_pasos):

            # Actualizar variables de clima, si necesario
            if clima:
                símismo.act_vals_clima(n_paso=paso, f=fecha_act)
                fecha_act += ft.timedelta(paso)  # Avanzar la fecha

            # Incrementar el modelo
            símismo.incrementar(paso)

        # Después de la simulación, cerramos el modelo.
        símismo.cerrar_modelo()

    def simular_paralelo(símismo, tiempo_final, paso=1, nombre_corrida='Corrida Tinamït', vals_inic=None,
                         fecha_inic=None, lugar=None, tcr=None, recalc=True, clima=False, combinar=True):

        #
        if isinstance(vals_inic, dict):
            if all(x in símismo.modelos for x in vals_inic):
                vals_inic = [vals_inic]

        # Poner las opciones de simulación en un diccionario.
        opciones = {'paso': paso, 'fecha_inic': fecha_inic, 'lugar': lugar, 'vals_inic': vals_inic,
                    'tcr': tcr, 'recalc': recalc, 'clima': clima}

        # Verificar llaves consistentes
        for op in opciones.values():
            lls_dics = next((d.keys() for d in opciones.values() if isinstance(d, dict)), None)  # Las llaves
            if isinstance(op, dict) and op.keys() != lls_dics:
                raise ValueError(_('Las llaves de diccionario de cada opción deben ser iguales.'))

        # Generar el diccionario de corridas
        l_n_ops = np.array([len(x) for x in opciones.values() if isinstance(x, list) or isinstance(x, dict)
                            and len(x) > 1])
        l_nmbs_ops_var = [ll for ll, v in opciones.items() if isinstance(v, list) or isinstance(v, dict)
                          and len(v) > 1]
        if combinar:
            n_corridas = int(np.prod(l_n_ops))

            if isinstance(nombre_corrida, list):
                raise TypeError('')

            dic_ops = {}  # Un diccionario de nombres de simulación y sus opciones de corrida

            # Poblar el diccionario de opciones iniciales
            ops = {}
            nombre = []
            for ll, op in opciones.items():
                if not isinstance(op, dict) and not isinstance(op, list):
                    ops[ll] = op
                else:
                    if isinstance(op, dict):

                        id_op = list(op)[0]
                        ops[ll] = op[id_op]

                        if len(op) > 1:
                            nombre.append(id_op)
                    else:
                        ops[ll] = op[0]

                        if len(op) > 1:
                            nombre.append(str(op[0]))
            l_n_ops_cum = np.roll(l_n_ops.cumprod(), 1)
            l_n_ops_cum[0] = 1

            for i in range(n_corridas):
                í_ops = [int(np.floor(i / l_n_ops_cum[n]) % l_n_ops[n]) for n in range(l_n_ops.shape[0])]
                for í, n in enumerate(í_ops):
                    nmb_op = l_nmbs_ops_var[í]
                    op = opciones[nmb_op]

                    if isinstance(op, list):
                        ops[nmb_op] = op[n]
                        nombre[í] = str(op[n])
                    elif isinstance(op, dict):
                        id_op = list(op)[n]
                        ops[nmb_op] = op[id_op]
                        nombre[í] = id_op
                    else:
                        raise TypeError(_('Tipo de variable "{}" erróneo. Debería ser imposible llegar hasta este '
                                          'error.'.format(type(op))))
                dic_ops[' '.join(nombre)] = ops.copy()

            corridas = {'{}{}'.format('nombre_corrida' + '_' if nombre_corrida else '', ll): ops
                        for ll, ops in dic_ops.items()}

        else:
            # Si no estamos haciendo todas las combinaciones posibles de opciones, es un poco más fácil.

            n_corridas = np.max(l_n_ops)  # El número de corridas

            # Asegurarse de que todas las opciones tengan el mismo número de opciones.
            if np.any(np.not_equal(l_n_ops, n_corridas)):
                raise ValueError(_('Si combinar == False, todas las opciones en forma de lista deben tener el mismo '
                                   'número de opciones.'))

            # Convertir diccionarios a listas
            for ll, op in opciones.items():
                if isinstance(op, dict):
                    opciones[ll] = [op[x] for x in sorted(op)]

            #
            if isinstance(nombre_corrida, str):
                if any(isinstance(op, dict) for op in opciones.values()):
                    l_nombres = next(isinstance(op, dict) for op in opciones.values())
                else:
                    l_nombres = range(n_corridas)
                l_nombres = sorted(l_nombres)

                corridas = {'{}_{}'.format(nombre_corrida, l_nombres[i]): {
                    ll: op[i] if isinstance(op, list) else op for ll, op in opciones.items()
                } for i in range(n_corridas)}

            else:
                corridas = {nmb: {
                    ll: op[i] if isinstance(op, list) else op for ll, op in opciones.items()
                } for i, nmb in enumerate(nombre_corrida)}

        # Sacar los valores iniciales del diccionario de opciones de corridas
        d_vals_inic = {ll: v.pop('vals_inic') for ll, v in corridas.items()}

        # Detectar si el modelo y todos sus submodelos son paralelizables
        if símismo.paralelizable():
            # ...si lo son...

            # Empezar las simulaciones en paralelo
            l_hilos = []  # type: list[threading.Thread]

            for corr, d_prms_corr in corridas.items():

                def correr_modelo(mod, vls_inic, d_args):
                    """
                    Función para inicializar y correr un modelo :class:`SuperConectado`.

                    :param mod: El modelo.
                    :type mod: SuperConectado

                    :param vls_inic: Diccionario de valores iniciales. El primer nivel de llaves es el nombre del
                      submodelo y el segundo los nombres de los variables con sus valores iniciales.
                    :type vls_inic: dict[str, dict[str, float | int | np.ndarray]]

                    :param d_args: Diccionario de argumentos para pasar al modelo.
                    :type d_args: dict
                    """

                    mod = copiar(mod)

                    # Inicializar los variables y valores iniciales. Esto debe ser adentro de la función llamada por
                    # Proceso, para que los valores iniciales se apliquen en su propio proceso (y no en el modelo
                    # original).
                    for m, d_inic in vls_inic:
                        # Para cada submodelo...

                        # Iniciar los valores iniciales
                        mod.modelos[m].inic_vals(dic_vals=d_inic)

                    # Después, simular el modelo
                    mod.simular(**d_args)

                l_hilos.append(
                    threading.Thread(name=corr, target=correr_modelo,
                                     kwargs={
                                         'mod': símismo, 'vls_inic': d_vals_inic[corr],
                                         'd_args': d_prms_corr
                                     })
                )

            # Empezar los procesos al mismo tiempo
            for hilo in l_hilos:
                hilo.start()

            # Esperar que todos los procesos hayan terminado
            for hilo in l_hilos:
                hilo.join()

        else:
            # Sino simplemente correrlas una tras otra con símismo.simular()

            avisar(_('No todos los submodelos del modelo conectado "{}" son paralelizable. Para evitar el riesgo'
                     'de errores de paralelización, correremos las corridas como simulaciones secuenciales normales. '
                     'Si tus modelos sí son paralelizable, poner el atributo ".paralelizable = True" para activar la '
                     'paralelización.').format(símismo.nombre))

            # Para cada corrida...
            for corr, d_prms_corr in corridas.items():

                # Implementar los valores iniciales
                for m, d_vals in d_vals_inic[corr].items():
                    # Para cada submodelo...

                    # Implementar sus valores iniciales.
                    símismo.inic_vals(dic_vals=d_vals)

                # Después, simular el modelo.
                símismo.simular(**d_prms_corr)

    def incrementar(símismo, paso):
        """
        Esta función avanza los dos submodelos conectados de intervalo de tiempo ``paso``. Emplea el módulo
        :py:mod:`threading` para correr los dos submodelos en paralelo, así ahorando tiempo.

        :param paso: El intervalo de tiempo.
        :type paso: int

        """

        # Una función independiente para controlar cada modelo
        def incr_mod(mod, nombre, d, args):
            """
            Esta función intenta incrementar un modelo y nos dice si hubo un error.

            :param mod: El modelo para incrementar
            :type mod: Modelo
            :param nombre: El nombre del modelo (para el diccionario de errores).
            :type nombre: str
            :param d: El diccionario en el cual cuardar información de errores.
            :type d: dict
            :param args: Los argumentos para el modelo
            :type args: tuple
            """
            try:
                mod.incrementar(*args)
            except:
                d[nombre] = True
                raise

        # Un diccionario para comunicar errores
        dic_err = {x: False for x in símismo.modelos}

        # Un hilo para cada modelo
        l_hilo = [threading.Thread(name='hilo_%s' % nombre,
                                   target=incr_mod, args=(mod, nombre, dic_err, (símismo.conv_tiempo[nombre] * paso,)))
                  for nombre, mod in símismo.modelos.items()]

        # Empezar los dos hilos al mismo tiempo
        for hilo in l_hilo:
            hilo.start()

        # Esperar que los dos hilos hayan terminado
        for hilo in l_hilo:
            hilo.join()

        # Verificar si hubo error
        for m, e in dic_err.items():
            if e:
                raise ChildProcessError(_('Hubo error en el modelo "{}".').format(m))

        # Leer egresos
        for mod in símismo.modelos.values():
            mod.leer_vals()

        # Intercambiar variables
        l_mods = [m for m in símismo.modelos.items()]  # Una lista de los submodelos.

        vars_egr = [dict([(símismo.conex_rápida[nombre][v]['var'],
                           m.variables[v]['val'] * símismo.conex_rápida[nombre][v]['conv'])
                          for v in m.vars_saliendo]) for nombre, m in l_mods]

        for n, tup in enumerate(l_mods):
            tup[1].cambiar_vals(valores=vars_egr[(n + 1) % 2])

    def leer_vals(símismo):
        """
        Leamos los valores de los variables de los dos submodelos. Por la conexión entre los diccionarios de variables
        de los submodelos y del :class:`~tinamit.Conectado.SuperConectado`, no hay necesidad de actualizar el
        diccionario del :class:`~tinamit.Modelo.SuperConectado` sí mismo.
        """

        for mod in símismo.modelos.values():
            mod.leer_vals()  # Leer los valores de los variables.

    def iniciar_modelo(símismo, **kwargs):
        """
        Inicia el modelo en preparación para una simulación.

        Actualizamos el diccionario de cconexiones rápidas para facilitar el intercambio eventual de valores entre los
        modelos.

        Se organiza este diccionario por modelo fuente. Tendrá la forma general:

        { modelo1: {var_fuente: {'var': var_recipiente_del_otro_modelo, 'conv': factor_conversión}, ...}, ...}

        """

        # Borrar lo que podría haber allí desde antes.
        símismo.conex_rápida.clear()

        # Una lista de los submodelos
        l_mod = list(símismo.modelos)

        for conex in símismo.conexiones:
            # Para cada conexión establecida...

            # Identificar el modelo fuente y el modelo recipiente de la conexión.
            mod_fuente = conex['modelo_fuente']
            mod_recip = l_mod[(l_mod.index(mod_fuente) + 1) % 2]

            # Identificar el variable fuente y el variable recipiente de la conexión.
            var_fuente = conex['dic_vars'][mod_fuente]
            var_recip = conex['dic_vars'][mod_recip]

            # Si el modelo fuente todavía no existe en el diccionario, agregarlo.
            if mod_fuente not in símismo.conex_rápida:
                símismo.conex_rápida[mod_fuente] = {}

            # Agregar el diccionario de conexión rápida.
            símismo.conex_rápida[mod_fuente][var_fuente] = {'var': var_recip, 'conv': conex['conv']}

        # Iniciar los submodelos también.
        for mod in símismo.modelos.values():
            mod.iniciar_modelo(**kwargs)  # Iniciar el modelo

    def cerrar_modelo(símismo):
        """
        Termina la simulación.
        """

        # No hay nada que hacer para el SuperConectado, pero podemos cerrar los submodelos.
        for mod in símismo.modelos.values():
            mod.cerrar_modelo()

    def conectar_vars(símismo, dic_vars, modelo_fuente, conv=None):
        """
        Conecta variables entre los submodelos.

        :param dic_vars: Un diccionario especificando los variables de cada modelo en el formato {mod1: var, mod2: var}.
        :type dic_vars: dict

        :param modelo_fuente: El nombre del modelo fuente.
        :type modelo_fuente: str

        :param conv: La conversión entre las unidades de ambos modelos. En el caso ``None``, se intentará adivinar la
          conversión con el módulo `~tinamit.Unidades`.

        :type conv: float

        """

        # Una lista de los submodelos.
        l_mods = list(símismo.modelos)

        # Asegurarse de que modelos y variables especificados sí existan.
        for nombre_mod in dic_vars:
            if nombre_mod not in símismo.modelos:
                raise ValueError(_('Nombre de modelo "{}" erróneo.').format(nombre_mod))

            mod = símismo.modelos[nombre_mod]
            var = dic_vars[nombre_mod]

            if var not in mod.variables:
                raise ValueError(_('El variable "{}" no existe en el modelo "{}".').format(var, nombre_mod))

            # Y también asegurarse de que el variable no a sido conectado ya.
            if var in mod.vars_saliendo or var in mod.vars_entrando:
                raise ValueError(_('El variable "{}" del modelo "{}" ya está conectado. '
                                   'Desconéctalo primero con .desconectar_vars().').format(var, nombre_mod))

        # Identificar el nombre del modelo recipiente también.
        n_mod_fuente = l_mods.index(modelo_fuente)
        modelo_recip = l_mods[(n_mod_fuente + 1) % 2]

        # Identificar los nombres de los variables fuente y recipiente, tanto como sus unidades y dimensiones.
        var_fuente = dic_vars[modelo_fuente]
        var_recip = dic_vars[modelo_recip]
        unid_fuente = símismo.modelos[modelo_fuente].variables[var_fuente]['unidades']
        unid_recip = símismo.modelos[modelo_recip].variables[var_recip]['unidades']

        dims_recip = símismo.modelos[modelo_recip].variables[var_recip]['dims']
        dims_fuente = símismo.modelos[modelo_fuente].variables[var_fuente]['dims']

        # Verificar que las dimensiones sean compatibles
        if dims_fuente != dims_recip:
            raise ValueError(_('Las dimensiones de los dos variables ({}: {}; {}: {}) no son compatibles.')
                             .format(var_fuente, dims_fuente, var_recip, dims_recip))

        if conv is None:
            # Si no se especificó factor de conversión...

            try:
                # Intentar hacer una conversión automática.
                conv = convertir(de=unid_fuente, a=unid_recip)
            except ValueError:
                # Si eso no funcionó, suponer una conversión de 1.
                avisar(_('No se pudo identificar una conversión automática para las unidades de los variables'
                         '"{}" (unidades: {}) y "{}" (unidades: {}). Se está suponiendo un factor de conversión de 1.')
                       .format(var_fuente, unid_fuente, var_recip, unid_recip))
                conv = 1

        # Crear el diccionario de conexión.
        dic_conex = {'modelo_fuente': modelo_fuente,
                     'dic_vars': dic_vars,
                     'conv': conv
                     }

        # Agregar el diccionario de conexión a la lista de conexiones.
        símismo.conexiones.append(dic_conex)

        # Para hacer: el siguiente debe ser recursivo.
        símismo.modelos[modelo_fuente].vars_saliendo.append(var_fuente)
        símismo.modelos[modelo_recip].vars_entrando.append(var_recip)

    def desconectar_vars(símismo, var_fuente, modelo_fuente):
        """
        Esta función desconecta variables.

        :param var_fuente: El variable fuente de la conexión.
        :type var_fuente: str

        :param modelo_fuente: El modelo fuente de la conexión.
        :type modelo_fuente: str

        """

        # Una lisat de los submodelos.
        l_mod = list(símismo.modelos)

        # Buscar la conexión correspondiente...
        for n, conex in enumerate(símismo.conexiones):
            # Para cada conexión existente...

            if conex['modelo_fuente'] == modelo_fuente and conex['dic_vars'][modelo_fuente] == var_fuente:
                # Si el modelo y variable fuente corresponden...

                # Identificar el modelo recipiente.
                mod_recip = l_mod[(l_mod.index(modelo_fuente) + 1) % 2]
                var_recipiente = conex['dic_vars'][mod_recip]

                # Quitar la conexión.
                símismo.conexiones.pop(n)

                # Quitar los variables desconectados de las listas de variables entrando y saliendo de los
                # submodelos.
                símismo.modelos[modelo_fuente].vars_saliendo.remove(var_fuente)
                símismo.modelos[mod_recip].vars_entrando.remove(var_recipiente)

                # Si ya encontramos la conexión, podemos parar aquí.
                return

        # Si no encontramos la conexión, hay un error.
        raise ValueError(_('La conexión especificada no existe.'))

    def estab_conv_meses(símismo, conv):

        super().estab_conv_meses(conv)
        for mod in símismo.modelos.values():
            if mod.unidad_tiempo == símismo.unidad_tiempo:
                mod.estab_conv_meses(conv)

    def __copy__(símismo):
        copia = símismo.__class__(símismo.nombre)


    def __getstate__(símismo):
        d = {
            'modelos': {n: pickle.dumps(m) for n, m in símismo.modelos.items()},
            'conexiones': símismo.conexiones,
            'conv_tiempo': símismo.conv_tiempo,
            'conv_tiempo_dudoso': símismo.conv_tiempo_dudoso,


        }

        d.update(super().__getstate__())

        return d

    def __setstate__(símismo, estado):

        super().__setstate__(estado)

        for m in estado['modelos']:
            símismo.estab_modelo(pickle.loads(m))
        for c in símismo.conexiones:
            símismo.conectar_vars(**c)
        símismo.conv_tiempo = estado['conv_tiempo']
        símismo.conv_tiempo_dudoso = estado['conv_tiempo_dudoso']
        símismo.vars_clima = estado['vars_clima']


class Conectado(SuperConectado):
    """
    Esta clase representa un tipo especial de modelo :class:`~tinamit.Conectado.SuperConectado`: la conexión entre un
    modelo biofísico y un modelo DS.
    """

    def __init__(símismo):
        """
        Inicializar el modelo :mod:`~tinamit.Conectado.Conectado`.
        """

        # Referencias rápidas a los submodelos.
        símismo.mds = None
        símismo.bf = None

        # Inicializar este como su clase superior.
        super().__init__()

    def estab_mds(símismo, archivo_mds):
        """
        Establecemos el modelo de dinámicas de los sistemas (:class:`~tinamit.EnvolturaMDS.EnvolturaMDS`).

        :param archivo_mds: El archivo del modelo DS, o el modelo sí mismo.
        :type archivo_mds: str | EnvolturaMDS

        """

        # Generamos un objeto de modelo DS.
        if isinstance(archivo_mds, str):
            modelo_mds = generar_mds(archivo=archivo_mds)
        elif isinstance(archivo_mds, EnvolturaMDS):
            modelo_mds = archivo_mds
        else:
            raise TypeError(_('Debes dar o un modelo DS, o la dirección hacia el archivo de uno.'))

        # Conectamos el modelo DS.
        símismo.estab_modelo(modelo=modelo_mds)

        # Y hacemos la referencia rápida.
        símismo.mds = modelo_mds

    def estab_bf(símismo, archivo_bf):
        """
        Establece el modelo biofísico (:class:`~tinamit.BF.EnvolturaBF`).

        :param archivo_bf: El archivo con la clase del modelo biofísico. **Debe** ser un archivo de Python.
        :type archivo_bf: str

        """

        # Creamos una instancia de la Envoltura BF con este modelo.
        if isinstance(archivo_bf, str):
            modelo_bf = EnvolturaBF(archivo=archivo_bf)
        elif isinstance(archivo_bf, EnvolturaBF):
            modelo_bf = archivo_bf
        else:
            raise TypeError(_('Debes dar o un modelo BF, o la dirección hacia el archivo de uno.'))

        # Conectamos el modelo biofísico.
        símismo.estab_modelo(modelo=modelo_bf)

        # Y guardamos la referencia rápida.
        símismo.bf = modelo_bf

    def conectar(símismo, var_mds, var_bf, mds_fuente, conv=None):
        """
        Una función para conectar variables entre el modelo biofísico y el modelo DS.

        :param var_mds: El nombre del variable en el modelo DS.
        :type var_mds: str

        :param var_bf: El nombre del variable correspondiente en el modelo biofísico.
        :type var_bf: str

        :param mds_fuente: Si ``True``, el modelo DS es el modelo fuente para la conexión. Sino, será el modelo
          biofísico.
        :type mds_fuente: bool

        :param conv: El factor de conversión entre los variables.
        :type conv: float

        """

        # Hacer el diccionario necesario para especificar la conexión.
        dic_vars = {'mds': var_mds, 'bf': var_bf}

        # Establecer el modelo fuente.
        if mds_fuente:
            fuente = 'mds'
        else:
            fuente = 'bf'

        # Llamar la función apropiada de la clase superior.
        símismo.conectar_vars(dic_vars=dic_vars, modelo_fuente=fuente, conv=conv)

    def desconectar(símismo, var_mds):
        """
        Esta función deshacer una conexión entre el modelo biofísico y el modelo DS. Se especifica la conexión por
        el nombre del variable en el modelo DS.

        :param var_mds: El nombre del variable conectado en el modelo DS.
        :type var_mds: str

        """

        # Llamar la función apropiada de la clase superior.
        símismo.desconectar_vars(var_fuente=var_mds, modelo_fuente='mds')

    def dibujar(símismo, geog, var, corrida, directorio, i_paso=None, colores=None, escala=None):
        """
        Dibuja mapas espaciales de los valores de un variable.

        :param geog: La geografía del lugares.
        :type geog: Geografía
        :param var: El variable para dibujar.
        :type var: str
        :param corrida: El nombre de la corrida para dibujar.
        :type corrida: str
        :param directorio: El directorio, relativo al archivo EnvolturaMDS, donde hay que poner los dibujos.
        :type directorio: str
        :param i_paso: Los pasos a los cuales quieres dibujar los egresos.
        :type i_paso: list | tuple | int
        :param colores: La escala de colores para representar los valores del variable.
        :type colores: tuple | list | int
        :param escala: La escala de valores para el dibujo. Si ``None``, será el rango del variable.
        :type escala: list | np.ndarray
        """

        def valid_nombre_arch(nombre):
            """
            Una función para validar un nombre de archivo.

            :param nombre: El nombre propuesto para el archivo.
            :type nombre: str
            :return: Un nombre válido.
            :rtype: str
            """
            for x in ['\\', '/', '\|', ':' '*', '?', '"', '>', '<']:
                nombre = nombre.replace(x, '_')

            return nombre

        # Incluir el nombre de la corrida en el directorio, si no es que ya esté allí.
        if os.path.split(directorio)[1] != corrida:
            dir_corrida = valid_nombre_arch(corrida)
            directorio = os.path.join(directorio, dir_corrida)

        # Preparar el nombre del variable para uso en el nombre del archivo.
        nombre_var = valid_nombre_arch(var)

        # Crear el directorio, si no existe ya.
        if not os.path.isdir(directorio):
            os.makedirs(directorio)
        else:
            # Si ya existía el directorio, borrar dibujos ya existentes con este nombre (de corridas anteriores).
            for arch in os.listdir(directorio):
                if re.match(r'{}, [0-9]+'.format(nombre_var), arch):
                    os.remove(os.path.join(directorio, arch))

        bd = símismo.mds.leer_resultados_mds(corrida, var)

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

        unid = símismo.mds.variables[var]['unidades']
        if escala is None:
            escala = np.min(bd), np.max(bd)

        for i in range(*i_paso):
            valores = bd[..., i]
            nombre_archivo = os.path.join(directorio, '{}, {}'.format(nombre_var, i))
            geog.dibujar(archivo=nombre_archivo, valores=valores, título=var, unidades=unid,
                         colores=colores, escala_num=escala)

    def __setstate__(símismo, estado):

        super().__setstate__(estado)

        símismo.bf = símismo.modelos['bf']
        símismo.mds = símismo.modelos['mds']
