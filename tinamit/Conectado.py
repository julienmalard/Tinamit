import datetime as ft
import pickle
import threading
from copy import copy as copiar
from warnings import warn as avisar

import numpy as np

from tinamit.BF import EnvolturaBF, ModeloBF
from tinamit.EnvolturasMDS import generar_mds
from tinamit.Geog.Geog import Lugar
from tinamit.MDS import EnvolturaMDS
from tinamit.Modelo import Modelo
from tinamit.Unidades.conv import convertir
from tinamit.config import _


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

    def agregar_modelo(símismo, modelo):
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

    def desconectar_modelo(símismo, modelo):
        if isinstance(modelo, Modelo):
            modelo = modelo.nombre

        try:
            símismo.modelos.pop(modelo)
        except KeyError:
            raise ValueError(_('El modelo "{}" no estaba conectado.').format(modelo))

        for var in símismo.variables:
            if var.startswith(modelo + '_'):
                símismo.variables.pop(var)
        for conex in símismo.conexiones.copy():
            if conex['modelo_fuente'] == modelo or conex['modelo_recip'] == modelo:
                símismo.conexiones.remove(conex)

        símismo.unidad_tiempo()

    def _inic_dic_vars(símismo):
        """
        Esta función no es necesaria, porque :func:`~tinamit.Conectado.Conectado.agregar_modelo` ya llama las funciones
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
        try:
            if all(convertir(u, u_0) == 1 for u in d_unids.values()):
                for m in l_mods:
                    símismo.conv_tiempo[m] = 1

                return list(d_unids.values())[0]
        except ValueError:
            pass

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
        np.divide(factores_conv, factores_conv.min(), out=factores_conv)

        # Verificar que no tengamos factores de conversión fraccionales.
        verificar_entero(factores_conv, l_unids=list(d_unids))

        # Aplicar los factores calculados.
        for i, m in enumerate(l_mods):
            símismo.conv_tiempo[m] = int(factores_conv[i])

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
        for m, c in conv.items():
            símismo.conv_tiempo[m] = c

        # Y guardar el nombre del modelo de base.
        símismo.mod_base_tiempo = mod_base

        # Si había duda acerca de la conversión de tiempo, ya no hay.
        símismo.conv_tiempo_dudoso = False

    def _cambiar_vals_modelo_externo(símismo, valores):
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
            mod, var = símismo.resolver_nombre_var(var)

            # Ahora, pedimos a los submodelos de hacer los cambios en los modelos externos, si hay.
            símismo.modelos[mod].cambiar_vals(valores={var: val})

            for c in símismo.conexiones:
                if c['modelo_fuente'] == mod and c['var_fuente'] == var:
                    símismo.modelos[c['modelo_recip']].cambiar_vals(valores={c['var_recip']: val * c['conv']})

    def paralelizable(símismo):
        """
        Un modelo :class:`SuperConectado` es paralelizable si todos sus submodelos lo son.

        :return: Si todos los submodelos de este modelo son paralelizables.
        :rtype: bool
        """

        return all(mod.paralelizable() for mod in símismo.modelos.values())

    def simular(símismo, t_final=None, t_inic=None, paso=1, nombre_corrida='Corrida Tinamït',
                vals_inic=None, vals_extern=None, bd=None, lugar_clima=None, clima=None, vars_interés=None):
        """
        Simula el modelo :class:`~tinamit.Conectado.SuperConectado`.

        :param t_final: El tiempo final de la simulación.
        :type t_final: int

        :param paso: El paso (intervalo de intercambio de valores entre los dos submodelos).
        :type paso: int

        :param nombre_corrida: El nombre de la corrida.  El valor automático es ``Corrida Tinamit``.
        :type nombre_corrida: str

        :param t_inic: La fecha inicial de la simulación. Necesaria para simulaciones con cambios climáticos.
        :type t_inic: ft.datetime | ft.date | int | str

        :param lugar_clima: El lugares de la simulación.
        :type lugar_clima: Lugar

        :param tcr: El escenario climático según el sistema de la IPCC (``2.6``, ``4.5``, ``6.0``, o ``8.5``). ``0`` da
          el clima histórico.
        :type tcr: str | float | int

        :param recalc_clima: Si quieres recalcular los datos climáticos, si ya existen.
        :type recalc_clima: bool

        :param clima: Si es una simulación de cambios climáticos o no.
        :type clima: bool

        """

        vals_inic = símismo._frmt_dic_vars(vals_inic)

        # ¡No se puede simular con menos de un modelo!
        if len(símismo.modelos) < 1:
            raise ValueError(_('Hay que conectar submodelos antes de empezar una simulación.'))

        # Si no estamos seguro de la conversión de unidades de tiempo, decirlo aquí.
        if símismo.conv_tiempo_dudoso:
            l_unids = [m.unidad_tiempo() for m in símismo.modelos.values()]
            avisar(_('No se pudo inferir la conversión de unidades de tiempo entre {}.\n'
                     'Especificarla con la función .estab_conv_tiempo().\n'
                     'Por el momento pusimos el factor de conversión a 1, pero probablemente no es lo que quieres.')
                   .format(', '.join(l_unids)))

        # Todo el restode la simulación se hace como en la clase pariente
        return super().simular(
            t_final=t_final, t_inic=t_inic, paso=paso, nombre_corrida=nombre_corrida,
            vals_inic=vals_inic, vals_extern=vals_extern, bd=bd,
            lugar_clima=lugar_clima, clima=clima, vars_interés=vars_interés
        )

    def simular_grupo(
            símismo, t_final, t_inic=None, paso=1, nombre_corrida='', vals_inic=None, vals_extern=None,
            lugar_clima=None, clima=None, recalc_clima=True, combinar=True, dibujar=None,
            paralelo=None, vars_interés=None, guardar=False
    ):

        vals_inic = símismo._frmt_dic_vars(vals_inic)

        # Llamar la función correspondiente de la clase pariente.
        return super().simular_grupo(
            t_final=t_final, paso=paso, nombre_corrida=nombre_corrida, vals_inic=vals_inic,
            vals_extern=vals_extern,
            t_inic=t_inic, lugar_clima=lugar_clima, clima=clima, combinar=combinar, paralelo=paralelo,
            vars_interés=vars_interés, guardar=guardar
        )

    def _act_vals_dic_var(símismo, valores):
        valores = símismo._frmt_dic_vars(valores)
        for mod, d_vals in valores.items():
            símismo.modelos[mod]._act_vals_dic_var(d_vals)

    def _frmt_dic_vars(símismo, vals_inic):
        # Reformatear el diccionario de valores iniciales en el caso que se especificó con submodelos
        if isinstance(vals_inic, dict):
            if not any(isinstance(x, dict) for x in vals_inic.values()):
                procesado = {}
                for vr in vals_inic:
                    resueltos = símismo.resolver_nombre_var(vr, todos=True)
                    for mod, v in resueltos:
                        if mod not in procesado:
                            procesado[mod] = {}
                        procesado[mod][v] = vals_inic[vr]
            elif all(isinstance(x, dict) for x in vals_inic.values()):
                if all(x in símismo.modelos for x in vals_inic):
                    procesado = vals_inic
                elif all(x in símismo.modelos for d_corr in vals_inic.values() for x in d_corr):
                    procesado = vals_inic
                else:
                    procesado = {}
                    for corr, d_corr in vals_inic.items():
                        if corr not in procesado:
                            procesado[corr] = {}
                        for var, val in d_corr.items():
                            resueltos = símismo.resolver_nombre_var(var, todos=True)
                            for mod, v in resueltos:
                                if mod not in procesado[corr]:
                                    procesado[corr][mod] = {}
                                procesado[corr][mod][v] = val

            else:
                raise ValueError

            return procesado
        else:
            return vals_inic

    def _incrementar(símismo, paso, guardar_cada=None):
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
                raise ChildProcessError(_('Hubo error en el modelo "{}": {}').format(m, e))

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

    def _leer_vals_inic(símismo):
        pass  # Se hace en iniciar_modelo para los submodelos.

    def _leer_vals(símismo):
        """
        Leamos los valores de los variables de los dos submodelos. Por la conexión entre los diccionarios de variables
        de los submodelos y del :class:`~tinamit.Conectado.SuperConectado`, no hay necesidad de actualizar el
        diccionario del :class:`~tinamit.Modelo.SuperConectado` sí mismo.
        """

        for mod in símismo.modelos.values():
            mod.leer_vals()  # Leer los valores de los variables.

    def _iniciar_modelo(símismo, tiempo_final, nombre_corrida, vals_inic):
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

            # Especificar el variable como variable egreso para la simulación, de manera recursiva si es una
            # instancia de :class:`SuperConectado`.
            obj_mod = símismo.modelos[mod_fuente]
            if isinstance(obj_mod, SuperConectado):
                obj_mod.especificar_var_saliendo(var_fuente)
            else:
                obj_mod.vars_saliendo.add(var_fuente)

        # Iniciar los submodelos también.
        for nmbr, mod in símismo.modelos.items():
            try:
                vals_inic_mod = vals_inic[nmbr]
            except KeyError:
                vals_inic_mod = {}
            conv_tiempo = símismo.conv_tiempo[nmbr]
            mod.iniciar_modelo(
                tiempo_final=tiempo_final * conv_tiempo, nombre_corrida=nombre_corrida, vals_inic=vals_inic_mod
            )  # Iniciar el modelo

    def especificar_var_saliendo(símismo, var):

        mod, var_mod = símismo.resolver_nombre_var(var)
        obj_mod = símismo.modelos[mod]
        if isinstance(obj_mod, SuperConectado):
            obj_mod.especificar_var_saliendo(var_mod)
        else:
            símismo.modelos[mod].vars_saliendo.add(var_mod)

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
        if any(x['var_recip'] == var_recip and x['modelo_recip'] == modelo_recip for x in símismo.conexiones):
            avisar(_('El variable "{}" del modelo "{}" ya está conectado como variable recipiente. '
                     'Borraremos la conexión anterior.').format(var_recip, modelo_recip))

        # Identificar los nombres de los variables fuente y recipiente, tanto como sus unidades, dimensiones y límites.
        unid_fuente = símismo.modelos[modelo_fuente].obt_unidades_var(var_fuente)
        unid_recip = símismo.modelos[modelo_recip].obt_unidades_var(var_recip)

        dims_fuente = símismo.modelos[modelo_fuente].obt_dims_var(var_fuente)
        dims_recip = símismo.modelos[modelo_recip].obt_dims_var(var_recip)

        líms_fuente = símismo.modelos[modelo_fuente].obt_lims_var(var_fuente)
        líms_recip = símismo.modelos[modelo_recip].obt_lims_var(var_recip)

        # Verificar que las dimensiones sean compatibles
        if dims_fuente != dims_recip:
            raise ValueError(_('Las dimensiones de los dos variables ({}: {}; {}: {}) no son compatibles.')
                             .format(var_fuente, dims_fuente, var_recip, dims_recip))

        # Verificar que los límites sean compatibles
        if (líms_recip[0] is not None) and (líms_fuente[0] is None or líms_recip[0] > líms_fuente[0]):
            avisar(_('Pensamos bien avisarte que el límite inferior ({l_r}) del variable recipiente "{v_r}" '
                     'queda superior al límite inferior ({l_f}) del variable fuente "{v_f}" de la conexión.'
                     ).format(v_r=var_recip, v_f=var_fuente, l_r=líms_recip[0], l_f=líms_fuente[0]))
        if (líms_recip[1] is not None) and (líms_fuente[1] is None or líms_recip[1] < líms_fuente[1]):
            avisar(_('Pensamos bien avisarte que el límite superior ({l_r}) del variable recipiente "{v_r}" '
                     'queda inferior al límite superior ({l_f}) del variable fuente "{v_f}" de la conexión.'
                     ).format(v_r=var_recip, v_f=var_fuente, l_r=líms_recip[1], l_f=líms_fuente[1]))

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

    def estab_conv_unid_tiempo(símismo, unid_ref, factor):

        super().estab_conv_unid_tiempo(unid_ref, factor)

        for mod in símismo.modelos.values():
            mod.estab_conv_unid_tiempo(unid_ref, factor)

    def valid_var(símismo, var):
        if var in símismo.variables:
            return var
        else:
            try:
                m = next(d['modelo_fuente'] for d in símismo.conexiones if d['var_fuente'] == var)
                return '{}_{}'.format(m, var)
            except StopIteration:
                pass

            for m, obj_m in símismo.modelos.items():
                if var in obj_m.variables:
                    return '{}_{}'.format(m, var)

            raise ValueError(_('El variable "{}" no existe en el modelo "{}", ni siquiera en sus '
                               'submodelos.').format(var, símismo))

    def resolver_nombre_var(símismo, var, todos=False):
        """

        Parameters
        ----------
        var : str

        Returns
        -------

        """

        v = símismo.valid_var(var)
        if not todos:
            return v.split('_', maxsplit=1)

        else:
            if v == var:
                return [tuple(v.split('_', maxsplit=1))]
            v = v.split('_', maxsplit=1)[1]
            egrs = []
            for mod, obj_m in símismo.modelos.items():
                if v in obj_m.variables:
                    egrs.append((mod, v))

            return egrs

    def leer_resultados(símismo, var=None, corrida=None):
        if corrida is None:
            if símismo.corrida_activa is None:
                raise ValueError(_('Debes especificar una corrida.'))
            else:
                corrida = símismo.corrida_activa

        if var in símismo.variables:
            try:
                return super().leer_resultados(var=var, corrida=corrida)
            except ValueError:
                pass

            mod, v = símismo.resolver_nombre_var(var)

            if mod in símismo.modelos and v in símismo.modelos[mod].variables:
                try:
                    return símismo.modelos[mod].leer_resultados(var=v, corrida=corrida)
                except FileNotFoundError:
                    pass
        else:
            var_compl = next(
                ('{}_{}'.format(m, var) for m in símismo.modelos if '{}_{}'.format(m, var) in símismo.mem_vars),
                None)
            if var_compl is not None:
                return super().leer_resultados(var=var_compl, corrida=corrida)
            for obj_m in símismo.modelos.values():
                if var in obj_m.variables:
                    try:
                        return obj_m.leer_resultados(var=var, corrida=corrida)
                    except FileNotFoundError:
                        pass

        raise FileNotFoundError(_('Ningún de los submodelos pudieron leer los resultados de la corrida.'))

    def __getinitargs__(símismo):
        return símismo.nombre,

    def __copy__(símismo):
        copia = super().__copy__()
        for m in símismo.modelos.values():
            copia.agregar_modelo(copiar(m))
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
            símismo.agregar_modelo(pickle.loads(m))
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

    def __init__(símismo, bf=None, mds=None, nombre='Conectado'):
        """
        Inicializar el modelo :mod:`~tinamit.Conectado.Conectado`.
        """

        # Referencias rápidas a los submodelos.
        símismo.mds = None  # type: EnvolturaMDS
        símismo.bf = None  # type: EnvolturaBF

        # Inicializar este como su clase superior.
        super().__init__(nombre=nombre)

        # Conectar los submodelos, si ya se especificaron.
        if bf is not None:
            símismo.estab_bf(bf)
        if mds is not None:
            símismo.estab_mds(mds)

    def estab_mds(símismo, archivo_mds):
        """
        Establecemos el modelo de dinámicas de los sistemas (:class:`~tinamit.EnvolturasMDS.EnvolturasMDS`).

        :param archivo_mds: El fuente del modelo DS, o el modelo sí mismo.
        :type archivo_mds: str | EnvolturaMDS

        """

        # Generamos un objeto de modelo DS.
        if isinstance(archivo_mds, str):
            modelo_mds = generar_mds(archivo=archivo_mds)
        elif isinstance(archivo_mds, EnvolturaMDS):
            modelo_mds = archivo_mds
        else:
            raise TypeError(_('Debes dar o un modelo DS, o la dirección hacia el fuente de uno.'))

        # Conectamos el modelo DS.
        símismo.agregar_modelo(modelo=modelo_mds)

        # Y hacemos la referencia rápida.
        símismo.mds = modelo_mds

    def estab_bf(símismo, bf):
        """
        Establece el modelo biofísico (:class:`~tinamit.BF.EnvolturasBF`).

        :param bf: El fuente con la clase del modelo biofísico. **Debe** ser un fuente de Python.
        :type bf: str | EnvolturaBF

        """

        # Creamos una instancia de la Envoltura BF con este modelo.
        if isinstance(bf, str) or isinstance(bf, ModeloBF) or callable(bf):
            modelo_bf = EnvolturaBF(modelo=bf)
        elif isinstance(bf, EnvolturaBF):
            modelo_bf = bf
        else:
            raise TypeError(_('Debes dar o un modelo BF, o la dirección hacia el fuente de uno.'))

        # Conectamos el modelo biofísico.
        símismo.agregar_modelo(modelo=modelo_bf)

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
