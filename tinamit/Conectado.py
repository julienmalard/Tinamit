import datetime as ft
import pickle
import threading
from copy import copy as copiar
from warnings import warn as avisar

import numpy as np
from dateutil.relativedelta import relativedelta as deltarelativo

from tinamit import _
from tinamit.BF import EnvolturaBF, ModeloBF
from tinamit.EnvolturaMDS import generar_mds
from tinamit.Geog.Geog import Lugar
from tinamit.MDS import EnvolturaMDS
from tinamit.Modelo import Modelo
from tinamit.Unidades.conv import convertir


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
        # {'nombre_modelo_2': factor_conv,
        # ...}
        # Al menos uno de los dos factores siempre será = a 1.
        símismo.conv_tiempo = {}
        símismo.conv_tiempo_dudoso = False  # Para acordarse si Tinamït tuvo que adivinar la conversión o no.
        símismo.mod_base_tiempo = None

        # Inicializamos el SuperConectado como todos los Modelos.
        super().__init__(nombre=nombre)

    def estab_modelo(símismo, modelo):
        """
        Esta función agrega un modelo al SuperConectado. Una vez que dos modelos estén agregados, se pueden conectar
        y simular juntos.

        :param modelo: El modelo para agregar.
        :type modelo: tinamit.Modelo.Modelo

        """

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

        # Actualizar la unidad de tiempo del modelo
        símismo.unidad_tiempo()

    def _inic_dic_vars(símismo):
        """
        Esta función no es necesaria, porque :func:`~tinamit.Conectado.Conectado.estab_modelo` ya llama las funciones
        necesarias, :func:`~tinamit.Modelo._inic_dic_vars` de los submodelos.

        """
        pass

    def unidad_tiempo(símismo):
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

        # Borrar información existente
        símismo.conv_tiempo_dudoso = False
        símismo.conv_tiempo.clear()

        # Si se especificó modelo de base de tiempo, usar éste.
        if símismo.mod_base_tiempo is not None:
            return símismo.modelos[símismo.mod_base_tiempo].unidad_tiempo()

        # Casos fáciles
        if not len(símismo.modelos):
            # Si todavía no se han conectado modelos, no hay nada que hacer.
            return None
        elif len(símismo.modelos) == 1:
            # Si solamente se contectó un modelo, devolver la unidad de tiempo de éste.
            m = list(símismo.modelos)[0]
            símismo.conv_tiempo[m] = 1

            return símismo.modelos[m].unidad_tiempo()

        # Identificar las unidades de los submodelos.
        l_mods = list(símismo.modelos)  # Una lista ordenada de los nombres de los submodelos.
        d_unids = {m: símismo.modelos[m].unidad_tiempo() for m in l_mods}

        # Una función auxiliar aquí para verificar si los factores de conversión son números enteros o no.
        def verificar_entero(factor, l_unids):

            if not np.array_equal(factor.astype(int), factor):
                # Si todos los factores no son números enteros, tendremos que aproximar.
                avisar('Las unidades de tiempo de los dos modelos ({}) no tienen denominator común. '
                       'Se aproximará la conversión.'.format(', '.join(l_unids)))

            np.round(factor, out=factor)

        # Tomar cualquier unidad del diccionario como referencia de base
        u_0 = d_unids[l_mods[0]]

        # Si las unidades son idénticas, ya tenemos nuestra respuesta.
        if all(convertir(u, u_0) == 1 for u in d_unids.values()):
            for m in l_mods:
                símismo.conv_tiempo[m] = 1

            return list(d_unids.values())[0]

        else:
            # Sino, intentemos convertir automáticamente

            factores_conv = np.empty(len(d_unids))
            for i, m in enumerate(l_mods):
                u = d_unids[m]
                try:
                    # Intentar convertir la unidad del submodelo a la unidad de base
                    factores_conv[i] = convertir(de=u_0, a=u)
                except ValueError:
                    # Si no lo logramos, hay un error, pero no querremos parar todo el programa por eso.
                    símismo.conv_tiempo_dudoso = True
                    factores_conv[i] = 1

            # El factor más pequeño debe ser 1.
            np.divide(factores_conv, factores_conv.min())

            # Verificar que no tengamos factores de conversión fraccionales.
            verificar_entero(factores_conv, l_unids=list(d_unids))

            # Aplicar los factores calculados.
            for i, m in enumerate(l_mods):
                símismo.conv_tiempo[m] = factores_conv[i]

            # La unidad de base para el SuperConectado es la que tiene factor de conversión de 1.
            unid_base = next(d_unids[m] for m, c in símismo.conv_tiempo.items() if c == 1)

            # Devolver la unidad de base
            return unid_base

    def estab_conv_tiempo(símismo, mod_base, conv):
        """
        Esta función establece la conversión de tiempo entre los modelos (útil para unidades que Tinamït
        no reconoce).

        :param mod_base: El modelo con la unidad de tiempo mayor.
        :type mod_base: str

        :param conv: El factor de conversión con la unidad de tiempo del otro modelo. Si hay más que 2 modelos
        conectados, *debe* ser un diccionario con los nombres de los modelos y sus factores de conversión.
        :type conv: int | dict[str, int]

        """

        # Veryficar que el modelo de base es un nombre de modelo válido.
        if mod_base not in símismo.modelos:
            raise ValueError(_('El modelo "{}" no existe en este modelo conectado.').format(mod_base))

        # Convertir `conv`, si necesario.
        if isinstance(conv, int):
            if len(símismo.modelos) == 2:
                # Si hay dos modelos conectados, convertir `conv` a un diccionario.
                otro = next(m for m in símismo.modelos if m != mod_base)
                conv = {otro: conv}
            else:
                raise TypeError(_('Debes especificar un diccionario de factores de conversión si tienes'
                                  'más que 2 modelos conectados.'))

        else:
            # Asegurarse que todos los modelos en `conv` existen en `símismo.modelos`.
            m_error = [m for m in conv if m not in símismo.modelos]
            if len(m_error):
                raise ValueError(_('Los modelos siguientes no existen en el modelo conectado: {}')
                                 .format(', '.join(m_error)))

            # Assegurarse que todos los modelos en `símismo.modelos` existen en `conv`.
            if not all(m in símismo.modelos for m in conv if m != mod_base):
                raise ValueError(_('`Conv` debe incluir todos los modelos en este modelo conectado.'))

        # Establecer las conversiones
        símismo.conv_tiempo[mod_base] = 1
        for m, c in conv:
            símismo.conv_tiempo[m] = c

        # Y guardar el nombre del modelo de base.
        símismo.mod_base_tiempo = mod_base

        # Si había duda acerca de la conversión de tiempo, ya no hay.
        símismo.conv_tiempo_dudoso = False

    def _cambiar_vals_modelo_interno(símismo, valores):
        """
        Esta función cambia los valores del modelo. A través de la función :func:`~tinamit.Conectado.cambiar_vals`, se
        vuelve recursiva.

        :param valores: El diccionario de nombres de variables para cambiar. Hay que prefijar cada nombre de variable
          con el nombre del submodelo en en cual se ubica (separados con un ``_``), para que Tinamit sepa en cuál
          submodelo se ubica cada variable.
        :type valores: dict

        """

        # Para cada nombre de variable...
        for var, val in valores.items():
            # Primero, vamos a sacar el nombre del variable y el nombre del submodelo.
            mod, var = símismo.descomponer_nombre_var(var)

            # Ahora, pedimos a los submodelos de hacer los cambios en los modelos externos, si hay.
            símismo.modelos[mod].cambiar_vals(valores={var: val})

    def _conectar_clima(símismo, n_pasos, lugar, fecha_inic, tcr, recalc):
        """
        Esta función conecta el clima de un lugar con el modelo Conectado.

        :param  n_pasos: El número de pasos para la simulación.
        :type n_pasos: int
        :param lugar: El lugar.
        :type lugar: Lugar
        :param fecha_inic: La fecha inicial de la simulación.
        :type fecha_inic: ft.date | ft.datetime | str | int
        :param tcr: El escenario climático según el sistema de la IPCC (2.6, 4.5, 6.0, o 8.5)
        :type tcr: str | float

        """

        # Conectar el lugar
        símismo.lugar = lugar
        for m in símismo.modelos.values():
            m.lugar = lugar

        # Calcular la fecha final
        fecha_final = None
        n_días = None
        try:
            n_días = convertir(de=símismo.unidad_tiempo(), a='días', val=n_pasos)
        except ValueError:
            for m in símismo.modelos.values():
                try:
                    n_días = convertir(de=m.unidad_tiempo(), a='días', val=símismo.conv_tiempo[m.nombre] * n_pasos)
                    continue
                except ValueError:
                    pass

        if n_días is not None:
            fecha_final = fecha_inic + ft.timedelta(int(n_días))

        else:
            n_meses = None
            try:
                n_meses = convertir(de=símismo.unidad_tiempo(), a='meses', val=n_pasos)
            except ValueError:
                for m in símismo.modelos.values():
                    try:
                        n_meses = convertir(de=m.unidad_tiempo(), a='meses',
                                            val=símismo.conv_tiempo[m.nombre] * n_pasos)
                        continue
                    except ValueError:
                        pass
            if n_meses is not None:
                fecha_final = fecha_inic + deltarelativo(months=int(n_meses) + 1)

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
                recalc=True, clima=False, vars_interés=None):
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

        # ¡No se puede simular con menos de un modelo!
        if len(símismo.modelos) < 1:
            raise ValueError(_('Hay que conectar submodelos antes de empezar una simulación.'))

        # Si no estamos seguro de la conversión de unidades de tiempo, decirlo aquí.
        if símismo.conv_tiempo_dudoso:
            l_unids = [m.unidad_tiempo() for m in símismo.modelos.values()]
            avisar(_('\nNo se pudo inferir la conversión de unidades de tiempo entre {} y {}.\n'
                     'Especificarla con la función .estab_conv_tiempo().\n'
                     'Por el momento pusimos el factor de conversión a 1, pero probablemente no es lo que quieres.')
                   .format(l_unids))

        # Verificar los nombres de los variables de interés
        if vars_interés is not None:
            if not isinstance(vars_interés, list):
                vars_interés = [vars_interés]
            for i, v in enumerate(vars_interés.copy()):
                vars_interés[i] = símismo.valid_var(v)

        # Pasar la corrida activa a todos los submodelos también
        def aplicar_nombre_corr(m, corr):
            m.corrida_activa = corr
            if isinstance(m, SuperConectado):
                for s_m in m.modelos.values():
                    aplicar_nombre_corr(s_m, corr=corr)

        aplicar_nombre_corr(símismo, corr=nombre_corrida)

        # Todo el restode la simulación se hace como en la clase pariente
        super().simular(tiempo_final=tiempo_final, paso=paso, nombre_corrida=nombre_corrida, fecha_inic=fecha_inic,
                        lugar=lugar, tcr=tcr, recalc=recalc, clima=clima, vars_interés=vars_interés)

    def inic_vals_vars(símismo, dic_vals):

        llaves = list(dic_vals)

        # Implementar los valores iniciales
        if all(ll in símismo.variables for ll in llaves):
            super().inic_vals_vars(dic_vals)  # Enlaces dinámicos deberían arreglar los diccionarios de los submodelos

        else:
            if all(ll in símismo.modelos for ll in llaves):
                for m, d_vals in dic_vals.items():  # type: str, dict[str, float]
                    # Para cada submodelo...

                    # Implementar sus valores iniciales.
                    símismo.modelos[m].inic_vals_vars(dic_vals=d_vals)
            else:
                for var, val in dic_vals:
                    encontrado = False
                    for mod in símismo.modelos.values():
                        if var in mod.variables:
                            mod.inic_val_var(var, val)
                            encontrado = True
                            break
                    if not encontrado:
                        raise ValueError('')

    def _incrementar(símismo, paso):
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
            except BaseException as e:
                d[nombre] = e
                raise

        # Un diccionario para comunicar errores
        dic_err = {x: False for x in símismo.modelos}

        # Un hilo para cada modelo
        l_hilo = [threading.Thread(name='hilo_%s' % nombre,
                                   target=incr_mod, args=(mod, nombre, dic_err, (símismo.conv_tiempo[nombre] * paso,)))
                  for nombre, mod in símismo.modelos.items()]

        # Empezar los hilos al mismo tiempo
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
        símismo.leer_vals()

        # Intercambiar variables
        for m_r, d_m_r in símismo.conex_rápida.items():
            dic_vals = {}
            for v_r, d_v_r in d_m_r.items():
                m_f = d_v_r['mod_fuente']  # El modelo fuente
                v_f = d_v_r['var_fuente']  # El variable fuente

                val = símismo.modelos[m_f].obt_val_actual_var(v_f)  # El valor del variable
                conv = d_v_r['conv']  # La conversión
                dic_vals[v_r] = val * conv  # Agregar el nuevo valor al diccionario

            # Aplicar los cambios
            símismo.modelos[m_r].cambiar_vals(valores=dic_vals)

    def _leer_vals(símismo):
        """
        Leamos los valores de los variables de los dos submodelos. Por la conexión entre los diccionarios de variables
        de los submodelos y del :class:`~tinamit.Conectado.SuperConectado`, no hay necesidad de actualizar el
        diccionario del :class:`~tinamit.Modelo.SuperConectado` sí mismo.

        """

        for mod in símismo.modelos.values():
            mod.leer_vals()  # Leer los valores de los variables.

    def iniciar_modelo(símismo, tiempo_final, nombre_corrida):
        """
        Inicia el modelo en preparación para una simulación.

        Actualizamos el diccionario de cconexiones rápidas para facilitar el intercambio eventual de valores entre los
        modelos.

        Se organiza este diccionario por modelo recipiente.

        """

        # Borrar lo que podría haber allí desde antes.
        símismo.conex_rápida.clear()

        for m in símismo.modelos.values():
            m.vars_saliendo.clear()

        for conex in símismo.conexiones:
            # Para cada conexión establecida...

            # Identificar el modelo fuente y el modelo recipiente de la conexión.
            mod_fuente = conex['modelo_fuente']
            mod_recip = conex['modelo_recip']

            # Identificar el variable fuente y el variable recipiente de la conexión.
            var_fuente = conex['var_fuente']
            var_recip = conex['var_recip']

            # Si el modelo recipiente todavía no existe en el diccionario, agregarlo.
            if mod_recip not in símismo.conex_rápida:
                símismo.conex_rápida[mod_recip] = {}

            # Si el variable recipiente todavia no existe en el diccionario del modelo recipiente, agregarlo también.
            if var_recip not in símismo.conex_rápida[mod_recip]:
                símismo.conex_rápida[mod_recip][var_recip] = {}

            # Agregar el diccionario de conexión rápida.
            símismo.conex_rápida[mod_recip][var_recip] = {
                'mod_fuente': mod_fuente, 'var_fuente': var_fuente, 'conv': conex['conv']
            }

            símismo.modelos[mod_fuente].especificar_var_saliendo(var_fuente)

        # Iniciar los submodelos también.
        for mod in símismo.modelos.values():
            conv_tiempo = símismo.conv_tiempo[str(mod)]
            mod.iniciar_modelo(tiempo_final=tiempo_final * conv_tiempo,
                               nombre_corrida=nombre_corrida)  # Iniciar el modelo

    def especificar_var_saliendo(símismo, var):

        mod, var_mod = símismo.descomponer_nombre_var(var)
        símismo.modelos[mod].especificar_var_saliendo(var_mod)

    def cerrar_modelo(símismo):
        """
        Termina la simulación.
        """

        # No hay nada que hacer para el SuperConectado, pero podemos cerrar los submodelos.
        for mod in símismo.modelos.values():
            mod.cerrar_modelo()

    def conectar_vars(símismo, var_fuente, modelo_fuente, var_recip, modelo_recip, conv=None):
        """
        Conecta variables entre los submodelos.

        :param var_fuente: El variable fuente de la conexión.
        :type var_fuente: str

        :param modelo_fuente: El nombre del modelo fuente.
        :type modelo_fuente: str

        :param var_recip: El variable recipiente de la conexión.
        :type var_recip: str

        :param modelo_recip: El nombre del modelo recipiente.
        :type modelo_recip: str

        :param conv: La conversión entre las unidades de los modelos. En el caso ``None``, se intentará adivinar la
        conversión con el módulo `~tinamit.Unidades`.

        :type conv: float | int

        """

        # Verificar que todos los modelos existan.
        for m in [modelo_fuente, modelo_recip]:
            if m not in símismo.modelos:
                raise ValueError(_('El submodelo "{}" no existe en este modelo.').format(m))

        # Verificar que todos los variables existan.
        for v, m in [(var_fuente, modelo_fuente), (var_recip, modelo_recip)]:
            mod = símismo.modelos[m]
            if v not in mod.variables:
                raise ValueError(_('El variable "{}" no existe en el modelo "{}".').format(v, m))

        # Y también asegurarse de que el variable no haya sido conectado como variable recipiente ya.
        if any(x['var_recip'] == var_recip and x['mod_recip'] == modelo_recip for x in símismo.conexiones):
            avisar(_('El variable "{}" del modelo "{}" ya está conectado como variable recipiente. '
                     'Borraremos la conexión anterior.').format(var_recip, modelo_recip))

        # Identificar los nombres de los variables fuente y recipiente, tanto como sus unidades y dimensiones.
        unid_fuente = símismo.modelos[modelo_fuente].obt_unidades_var(var_fuente)
        unid_recip = símismo.modelos[modelo_recip].obt_unidades_var(var_recip)

        dims_recip = símismo.modelos[modelo_recip].obt_unidades_var(var_recip)
        dims_fuente = símismo.modelos[modelo_fuente].obt_unidades_var(var_fuente)

        # Verificar que las dimensiones sean compatibles
        if dims_fuente != dims_recip:
            raise ValueError(_('Las dimensiones de los dos variables ({}: {}; {}: {}) no son compatibles.')
                             .format(var_fuente, dims_fuente, var_recip, dims_recip))

        if conv is None:
            # Si no se especificó factor de conversión...

            # Intentar hacer una conversión automática.
            try:
                conv = convertir(de=unid_fuente, a=unid_recip)
            except ValueError:
                # Si eso no funcionó, suponer una conversión de 1.
                avisar(_('No se pudo identificar una conversión automática para las unidades de los variables'
                         '"{}" (unidades: {}) y "{}" (unidades: {}). Se está suponiendo un factor de conversión de 1.')
                       .format(var_fuente, unid_fuente, var_recip, unid_recip))
                conv = 1

        # Crear el diccionario de conexión.
        dic_conex = {'modelo_fuente': modelo_fuente,
                     'modelo_recip': modelo_recip,
                     'var_fuente': var_fuente,
                     'var_recip': var_recip,
                     'conv': conv
                     }

        # Agregar el diccionario de conexión a la lista de conexiones.
        símismo.conexiones.append(dic_conex)

    def desconectar_vars(símismo, var_fuente, modelo_fuente, modelo_recip=None, var_recip=None):
        """
        Esta función desconecta variables.

        :param var_fuente: El variable fuente de la conexión.
        :type var_fuente: str

        :param modelo_fuente: El modelo fuente de la conexión.
        :type modelo_fuente: str

        """

        # Verificar parámetros
        if modelo_recip is None and var_recip is not None:
            avisar(_('`var_recip` sin `modelo_recip` será ignorado en la función '
                     '`SuperConectado.desconectar_vars()`.'))

        # Buscar la conexión correspondiente...
        for n, conex in enumerate(símismo.conexiones):
            # Para cada conexión existente...
            if conex['modelo_fuente'] == modelo_fuente and conex['var_fuente'] == var_fuente:
                # Si el modelo y variable fuente corresponden...

                # Identificar si el modelo recipiente corresponde también.
                quitar = False
                if modelo_recip is None:
                    quitar = True
                else:
                    if modelo_recip == conex['modelo_recip']:
                        if var_recip is None or var_recip == conex['var_recip']:
                            quitar = True

                # Si corresponde todo, quitar la conexión.
                if quitar:
                    símismo.conexiones.pop(n)

    def estab_conv_meses(símismo, conv):

        super().estab_conv_meses(conv)
        for mod in símismo.modelos.values():
            if mod.unidad_tiempo() == símismo.unidad_tiempo():
                mod.estab_conv_meses(conv)

    def valid_var(símismo, var):
        if var in símismo.variables:
            return var
        else:
            for m, obj_m in símismo.modelos.items():
                if var in obj_m.variables:
                    return '{}_{}'.format(m, var)

            raise ValueError(_('El variable "{}" no existe en el modelo "{}", ni siquieta en sus '
                               'submodelos.').format(var, símismo))

    def descomponer_nombre_var(símismo, var):
        """

        Parameters
        ----------
        var : str

        Returns
        -------

        """
        if '_' not in var:
            raise ValueError(_('Un variable sin "_" no se puede descomponer en submodelo y nombre de variable.'))

        mod, var = var.split('_', maxsplit=1)

        if mod not in símismo.modelos:
            raise ValueError(_('El submodelo "{}" no existe en este modelo.').format(mod))

        if var not in símismo.modelos[mod].variables:
            raise ValueError(_('El variable "{}" no existe en submodelo "{}".').format(var, mod))

        return mod, var

    def _leer_resultados(símismo, var, corrida):

        if var in símismo.variables:
            mod, v = símismo.descomponer_nombre_var(var)

            if mod in símismo.modelos and v in símismo.modelos[mod].variables:
                try:
                    return símismo.modelos[mod]._leer_resultados(v, corrida)
                except NotImplementedError:
                    pass

        for m, obj_m in símismo.modelos.items():
            if var in obj_m.variables:
                try:
                    return obj_m._leer_resultados(var, corrida)
                except NotImplementedError:
                    pass

        raise IOError(_('Ningún de los submodelos pudieron leer los resultados de la corrida.'))

    def __getinitargs__(símismo):
        return símismo.nombre,

    def __copy__(símismo):
        copia = super().__copy__()
        for m in símismo.modelos.values():
            copia.estab_modelo(copiar(m))
        for c in símismo.conexiones:
            copia.conectar_vars(**c)

        copia.conv_tiempo = símismo.conv_tiempo
        copia.conv_tiempo_dudoso = símismo.conv_tiempo_dudoso
        copia.vars_clima = símismo.vars_clima

        return copia

    def __getstate__(símismo):
        d = super().__getstate__()
        d.update(
            {
                'conv_tiempo': símismo.conv_tiempo,
                'conv_tiempo_dudoso': símismo.conv_tiempo_dudoso,
                'conexiones': símismo.conexiones,
                'modelos': [pickle.dumps(m) for m in símismo.modelos.values()]
            }
        )
        return d

    def __setstate__(símismo, estado):
        super().__setstate__(estado)

        for m in estado['modelos']:
            símismo.estab_modelo(pickle.loads(m))
        for c in estado['conexiones']:
            símismo.conectar_vars(**c)

        símismo.conv_tiempo.clear()
        símismo.conv_tiempo.update(estado['conv_tiempo'])
        símismo.conv_tiempo_dudoso = estado['conv_tiempo_dudoso']


class Conectado(SuperConectado):
    """
    Esta clase representa un tipo especial de modelo :class:`~tinamit.Conectado.SuperConectado`: la conexión entre un
    modelo biofísico y un modelo DS.
    """

    def __init__(símismo, nombre='Conectado'):
        """
        Inicializar el modelo :mod:`~tinamit.Conectado.Conectado`.
        """

        # Referencias rápidas a los submodelos.
        símismo.mds = None  # type: EnvolturaMDS
        símismo.bf = None  # type: EnvolturaBF

        # Inicializar este como su clase superior.
        super().__init__(nombre=nombre)

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

    def estab_bf(símismo, bf):
        """
        Establece el modelo biofísico (:class:`~tinamit.BF.EnvolturaBF`).

        :param bf: El archivo con la clase del modelo biofísico. **Debe** ser un archivo de Python.
        :type bf: str | EnvolturaBF

        """

        # Creamos una instancia de la Envoltura BF con este modelo.
        if isinstance(bf, str) or isinstance(bf, ModeloBF) or callable(bf):
            modelo_bf = EnvolturaBF(modelo=bf)
        elif isinstance(bf, EnvolturaBF):
            modelo_bf = bf
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

        # Establecer los variables y modelos fuentes y recipientes.
        if mds_fuente:
            modelo_fuente = símismo.mds.nombre
            var_fuente = var_mds

            modelo_recip = símismo.bf.nombre
            var_recip = var_bf

        else:
            modelo_fuente = símismo.bf.nombre
            var_fuente = var_bf

            modelo_recip = símismo.mds.nombre
            var_recip = var_mds

        # Llamar la función apropiada de la clase superior.
        símismo.conectar_vars(var_fuente=var_fuente, modelo_fuente=modelo_fuente,
                              var_recip=var_recip, modelo_recip=modelo_recip, conv=conv)

    def desconectar(símismo, var_mds):
        """
        Esta función deshacer una conexión entre el modelo biofísico y el modelo DS. Se especifica la conexión por
        el nombre del variable en el modelo DS.

        :param var_mds: El nombre del variable conectado en el modelo DS.
        :type var_mds: str

        """

        # Llamar la función apropiada de la clase superior.
        símismo.desconectar_vars(var_fuente=var_mds, modelo_fuente='mds')

    def __getinitargs__(símismo):
        return tuple()

    def __copy__(símismo):

        copia = super().__copy__()

        copia.bf = símismo.modelos['bf']
        copia.mds = símismo.modelos['mds']

        return copia

    def __setstate__(símismo, estado):
        super().__setstate__(estado)
        símismo.bf = símismo.modelos['bf']
        símismo.mds = símismo.modelos['mds']
