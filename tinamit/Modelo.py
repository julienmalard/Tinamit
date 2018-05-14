import datetime as ft
import math
import os
import pickle
import re
from warnings import warn as avisar

from copy import deepcopy as copiar_profundo
import numpy as np
from multiprocessing import Pool as Reserva
from dateutil.relativedelta import relativedelta as deltarelativo

import tinamit.Geog.Geog as Geog
from tinamit import _, valid_nombre_arch
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

    def __init__(símismo, nombre):
        """
        La función de inicialización de todos modelos, conectados o no.

        :param nombre: El nombre del modelo. Sirve para identificar distintos modelos en un modelo conectado.
        :type nombre: str

        """

        # No se puede incluir nombres de modelos con "_" en el nombre (podría corrumpir el manejo de variables en
        # modelos jerarquizados).
        if "_" in nombre:
            avisar(_('No se pueden emplear nombres de modelos con "_", así que no puedes nombrar tu modelo"{}".\n'
                   'Sino, causaría problemas de conexión de variables por una razón muy compleja y oscura.\n'
                   'Vamos a renombrar tu modelo "{}". Lo siento.').format(nombre, nombre.replace('_', '.')))

        # El nombre del modelo (sirve como una referencia a este modelo en el modelo conectado).
        símismo.nombre = nombre

        # El diccionario de variables necesita la forma siguiente. Se llena con la función símismo._inic_dic_vars().
        # {var1: {'val': 13, 'unidades': cm, 'ingreso': True, 'egreso': True},
        #  var2: {...},
        #  ...}
        símismo.variables = {}
        símismo._inic_dic_vars()  # Iniciar los variables.

        #
        símismo.calibs = {}

        # Memorio de valores de variables (para leer los resultados más rápidamente después de una simulación).
        símismo.mem_vars = {}

        # Un diccionarior para guardar valores de variables iniciales hasta el momento que empezamos la simulación.
        # Es muy útil para modelos cuyos variables no podemos cambiar antes de empezar una simulación (como VENSIM).
        símismo.vals_inic = {}
        símismo.vars_clima = {}  # Formato: var_intern1: {'nombre_extrn': nombre_oficial, 'combin': 'prom' | 'total'}
        símismo.lugar = None  # type: Geog.Lugar

        # Listas de los nombres de los variables que sirven de conexión con otro modelo.
        símismo.vars_saliendo = set()
        símismo.vars_entrando = set()

        # El factor de conversión entre la unidad de tiempo del modelo y meses. (P. ej., 6 quiere decir que
        # hay 6 meses en una unidad de tiempo del modelo.)
        símismo.unidad_tiempo_meses = None

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

    def iniciar_modelo(símismo, tiempo_final, nombre_corrida):
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

    def _conectar_clima(símismo, n_pasos, lugar, fecha_inic, tcr, recalc):
        """
        Esta función conecta el clima de un lugar con el modelo.

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

        # Calcular la fecha final
        fecha_final = None
        n_días = None
        try:
            n_días = convertir(de=símismo.unidad_tiempo(), a='días', val=n_pasos)
        except ValueError:
            pass

        if n_días is not None:
            fecha_final = fecha_inic + ft.timedelta(int(n_días))

        else:
            try:
                n_meses = convertir(de=símismo.unidad_tiempo(), a='meses', val=n_pasos)
                fecha_final = fecha_inic + deltarelativo(months=int(n_meses) + 1)
            except ValueError:
                pass

        if fecha_final is None:
            raise ValueError('')

        # Obtener los datos de lugares
        lugar.prep_datos(fecha_inic=fecha_inic, fecha_final=fecha_final, tcr=tcr, regenerar=recalc)

    def simular(símismo, tiempo_final, paso=1, nombre_corrida='Corrida Tinamït', fecha_inic=None, lugar=None, tcr=None,
                recalc=True, clima=False, vars_interés=None):

        # Calcular el número de pasos necesario
        n_pasos = int(math.ceil(tiempo_final / paso))

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

        if vars_interés is None:
            vars_interés = []
        else:
            if isinstance(vars_interés, str):
                vars_interés = [vars_interés]
            for v in vars_interés:
                if v not in símismo.variables:
                    raise ValueError(_('El variable "{}" no existe en el modelo "{}".').format(v, símismo))
                símismo.vars_saliendo.add(v)  # para hacer: limpiar

        símismo.mem_vars.clear()
        for v in vars_interés:
            símismo.mem_vars[v] = np.empty((n_pasos + 1, *símismo.variables[v]['dims']))
            símismo.mem_vars[v][0] = símismo.variables[v]['val']

        # Hasta llegar al tiempo final, incrementamos el modelo.
        for i in range(n_pasos):

            # Actualizar variables de clima, si necesario
            if clima:
                símismo.act_vals_clima(n_paso=paso, f=fecha_act)
                # arreglarme: mejor conversión de unidades de tiempo
                if símismo.unidad_tiempo() == 'año':
                    fecha_act = ft.datetime(year=fecha_act.year + 1, month=fecha_act.month,
                                            day=fecha_act.day)  # Avanzar la fecha
                elif símismo.unidad_tiempo() == 'mes':
                    fecha_act += ft.timedelta(paso * 30)  # Avanzar la fecha
                elif símismo.unidad_tiempo() == 'días':
                    fecha_act += ft.timedelta(paso)  # Avanzar la fecha
                else:
                    if símismo.unidad_tiempo_meses is not None:
                        fecha_act += ft.timedelta(paso * símismo.unidad_tiempo_meses * 30)  # Avanzar la fecha
                    else:
                        raise ValueError('')

            # Incrementar el modelo
            símismo.incrementar(paso)

            # Guardar valores de variables de interés
            if len(vars_interés):
                símismo.leer_vals()
            for v in vars_interés:
                símismo.mem_vars[v][i + 1] = símismo.variables[v]['val']

        # Después de la simulación, cerramos el modelo.
        símismo.cerrar_modelo()

        if vars_interés is not None:
            return símismo.mem_vars

    def simular_paralelo(símismo, tiempo_final, paso=1, nombre_corrida='Corrida Tinamït', vals_inic=None,
                         fecha_inic=None, lugar=None, tcr=None, recalc=True, clima=False, combinar=True,
                         dibujar=None, paralelo=True, devolver=None):
        #
        if isinstance(vals_inic, dict):
            if all(x in símismo.modelos for x in vals_inic):
                vals_inic = [vals_inic]

        if devolver is not None:
            if not isinstance(devolver, list) and not isinstance(devolver, tuple):
                devolver = [devolver]

        # Poner las opciones de simulación en un diccionario.
        opciones = {'paso': paso, 'fecha_inic': fecha_inic, 'lugar': lugar, 'vals_inic': vals_inic,
                    'tcr': tcr, 'recalc': recalc, 'clima': clima, 'tiempo_final': tiempo_final}

        # Verificar llaves consistentes
        for op in opciones.values():
            lls_dics = next((d.keys() for d in opciones.values() if isinstance(d, dict)), None)  # Las llaves
            if isinstance(op, dict) and op.keys() != lls_dics:
                raise ValueError(_('Las llaves de diccionario de cada opción deben ser iguales.'))

        # Generar el diccionario de corridas
        l_n_ops = np.array([len(x) for x in opciones.values() if ((isinstance(x, list) or isinstance(x, dict))
                                                                  and (len(x) > 1))])
        l_nmbs_ops_var = [ll for ll, v in opciones.items() if ((isinstance(v, list) or isinstance(v, dict))
                                                               and (len(v) > 1))]

        devolv_lista = True
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
                        devolv_lista = False

                        id_op = list(op)[0]
                        ops[ll] = op[id_op]

                        if len(op) > 1:
                            nombre.append(id_op)
                    else:
                        ops[ll] = op[0]

                        if len(op) > 1:
                            nombre.append(str(op[0]) if not (isinstance(op[0], list) or isinstance(op[0], dict))
                                          else str(0))
            l_n_ops_cum = np.roll(l_n_ops.cumprod(), 1)
            if len(l_n_ops_cum):
                l_n_ops_cum[0] = 1
            else:
                l_n_ops_cum = [1]

            for i in range(n_corridas):
                í_ops = [int(np.floor(i / l_n_ops_cum[n]) % l_n_ops[n]) for n in range(l_n_ops.shape[0])]
                for í, n in enumerate(í_ops):
                    nmb_op = l_nmbs_ops_var[í]
                    op = opciones[nmb_op]

                    if isinstance(op, list):
                        ops[nmb_op] = op[n]
                        nombre[í] = str(str(op[n]) if not (isinstance(op[n], list) or isinstance(op[n], dict))
                                        else str(n))
                    elif isinstance(op, dict):
                        id_op = list(op)[n]
                        ops[nmb_op] = op[id_op]
                        nombre[í] = id_op
                    else:
                        raise TypeError(_('Tipo de variable "{}" erróneo. Debería ser imposible llegar hasta este '
                                          'error.'.format(type(op))))
                dic_ops[' '.join(x.replace(',', '_') for x in nombre)] = ops.copy()

                corridas = {'{}{}'.format(nombre_corrida + '_' if nombre_corrida else '', ll): ops
                            for ll, ops in dic_ops.items()}

            if len(corridas) == 1 and list(corridas)[0] == '':
                corridas['Corrida Tinamït'] = corridas.pop('')

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

            if any(isinstance(op, dict) for op in opciones.values()):
                devolv_lista = False

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

        for nmb in list(corridas.keys()):
            corridas[nmb.replace('.', '_')] = corridas.pop(nmb)
        # Sacar los valores iniciales del diccionario de opciones de corridas
        d_vals_inic = {ll: v.pop('vals_inic') for ll, v in corridas.items()}

        # Detectar si el modelo y todos sus submodelos son paralelizables
        if símismo.paralelizable() and paralelo:
            # ...si lo son...

            # Empezar las simulaciones en paralelo
            l_trabajos = []  # type: list[tuple]

            copia_mod = pickle.dumps(símismo)

            for corr, d_prms_corr in corridas.items():
                d_args = {ll: copiar_profundo(v) for ll, v in d_prms_corr.items()}
                d_args['nombre_corrida'] = corr

                l_trabajos.append((copia_mod, copiar_profundo(d_vals_inic[corr]), d_args))

            with Reserva() as r:
                r.map(_correr_modelo, l_trabajos)

        else:
            # Sino simplemente correrlas una tras otra con símismo.simular()
            if paralelo:
                avisar(_('No todos los submodelos del modelo conectado "{}" son paralelizable. Para evitar el riesgo'
                         'de errores de paralelización, correremos las corridas como simulaciones secuenciales normales. '
                         'Si tus modelos sí son paralelizable, poner el atributo ".paralelizable = True" para activar la '
                         'paralelización.').format(símismo.nombre))

            # Para cada corrida...
            for corr, d_prms_corr in corridas.items():

                símismo.inic_vals_vars(d_prms_corr)

                # Después, simular el modelo.
                símismo.simular(**d_prms_corr, nombre_corrida=corr)

        if dibujar is not None:
            # Para hacer: formalizar para todos los modelos
            if símismo.__class__.__name__ == 'Conectado':
                if not isinstance(dibujar, list):
                    dibujar = [dibujar]

                for dib in dibujar:
                    for corr in corridas:
                        símismo.dibujar_mapa(corrida=corr, **dib)

        if devolver is not None:
            egresos = {}
            for var in devolver:
                if devolv_lista:
                    egresos[var] = [símismo.leer_resultados(corrida=x, var=var)
                                    for x in corridas.keys()]
                else:
                    egresos[var] = {x: símismo.leer_resultados(corrida=x, var=var)
                                    for x in corridas.keys()}

            return egresos

    def incrementar(símismo, paso):
        """
        Esta función debe avanzar el modelo por un periodo de tiempo especificado.

        :param paso: El paso.
        :type paso: int

        """
        raise NotImplementedError

    def leer_vals(símismo):
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
        if var not in símismo.variables:
            raise ValueError(_('El variable inicializado "{}" no existe en los variables del modelo.\n'
                               'Pero antes de quejarte al gerente, sería buena idea verificar '
                               'si lo escrbiste bien.').format(var))  # Sí, lo "escrbí" así por propósito. :)

        # Guardamos el valor en el diccionario `vals_inic`. Se aplicarán los valores iniciales únicamente al momento
        # de empezar la simulación.
        símismo.vals_inic[var] = val

    def inic_vals_vars(símismo, dic_vals):
        """
        Una función más cómoda para inicializar muchos variables al mismo tiempo.

        :param dic_vals:
        :type dic_vals: dict[str, float | int | np.ndarray]

        """

        for var, val in dic_vals.items():
            símismo.inic_val_var(var=var, val=val)

    def _limp_vals_inic(símismo):
        """
        Esta función limpa los valores iniciales especificados anteriormente.
        """

        # Limpiar el diccionario.
        for v in símismo.vals_inic.values():
            v.clear()

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
        if var not in símismo.variables:
            raise ValueError(_('El variable "{}" no existe en este modelo. ¿De pronto lo escribiste mal?').format(var))
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

        for var in valores:
            if isinstance(símismo.variables[var]['val'], np.ndarray):
                símismo.variables[var]['val'][:] = valores[var]
            else:
                símismo.variables[var]['val'] = valores[var]

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

    def act_vals_clima(símismo, n_paso, f):
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

        # La lista de variables climáticos
        vars_clima = list(símismo.vars_clima)
        nombres_extrn = [d['nombre_extrn'] for d in símismo.vars_clima.values()]

        # La lista de maneras de combinar los valores diarios
        combins = [d['combin'] for d in símismo.vars_clima.values()]

        # La lista de factores de conversión
        convs = [d['conv'] for d in símismo.vars_clima.values()]

        # La fecha final
        if símismo.unidad_tiempo() == 'Días':
            f_final = f + deltarelativo(days=+n_paso)
            n_meses = n_paso / 30
        else:
            if símismo.unidad_tiempo_meses is None:

                try:
                    símismo.unidad_tiempo_meses = convertir(de=símismo.unidad_tiempo(), a='Mes', val=1)

                except ValueError:
                    raise ValueError(_('La unidad de tiempo "{}" no se pudo convertir a meses. Tienes que especificar'
                                       'el factor de conversión manualmente con ".estab_conv_meses(conv)".'))

            n_meses = n_paso * símismo.unidad_tiempo_meses
            if int(n_meses) != n_meses:
                avisar('Tuvimos que redondear la unidad de tiempo, {} {}, a {} meses'.
                       format(n_meses, símismo.unidad_tiempo, int(n_meses)))

            f_final = f + deltarelativo(months=n_meses)

        if n_meses > 1:
            avisar('El paso ({} {}) es superior a 1 mes. Puede ser que las predicciones climáticas pierdan '
                   'en precisión.'
                   .format(n_paso, símismo.unidad_tiempo))

        # Calcular los datos
        datos = símismo.lugar.comb_datos(vars_clima=nombres_extrn, combin=combins,
                                         f_inic=f, f_final=f_final)

        # Aplicar los valores de variables calculados
        for i, var in enumerate(vars_clima):
            # Para cada variable en la lista de clima...

            # El nombre oficial del variable de clima
            var_clima = nombres_extrn[i]

            # El factor de conversión de unidades
            conv = convs[i]

            # Aplicar el cambio
            símismo.cambiar_vals(valores={var: datos[var_clima] * conv})

    def estab_conv_meses(símismo, conv):
        """
        Establece, manualmente, el factor de conversión para convertir la unidad de tiempo del modelo a meses.
        Únicamente necesario si Tinamït no logra inferir este factor por sí mismo.

        :param conv: El factor de conversión entre la unidad de tiempo del modelo y un mes.
        :type: float | int

        """

        símismo.unidad_tiempo_meses = conv

    def dibujar_mapa(símismo, geog, var, directorio, corrida=None, i_paso=None, colores=None, escala=None):
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

        # Validar el nombre del variable.
        var = símismo.valid_var(var)

        # Preparar el nombre del variable para uso en el nombre del archivo.
        nombre_var = valid_nombre_arch(var)

        bd = símismo.leer_resultados(corrida, var)

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

        unid = símismo.variables[var]['unidades']
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
            raise ValueError(_('El variable "{}" no existe en el modelo "{}".').format(var, símismo))

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

    def egresos(símismo):
        return [v for v, d_v in símismo.variables.items() if d_v['egreso']]

    def ingresos(símismo):
        return [v for v, d_v in símismo.variables.items() if d_v['ingreso']]

    def paráms(símismo):
        return [v for v, d_v in símismo.variables.items() if d_v['parám']]

    def vars_estado_inicial(símismo):
        return [v for v, d_v in símismo.variables.items() if d_v['estado_inicial']]

    def leer_resultados(símismo, var, corrida=None):
        if corrida is None:
            if var in símismo.mem_vars:
                return símismo.mem_vars[var]
            else:
                raise ValueError(_('El variable "{}" no está en la memoria temporaria, y no especificaste una corrida '
                                   'donde buscarlo. Debes o especificar una corrida en particular, o poner "{}" en'
                                   '"vars_interés" cuando corres una simulación').format(var, var))
        else:
            return símismo._leer_resultados(var, corrida)

    def _leer_resultados(símismo, var, corrida):
        raise NotImplementedError(_(
            'Modelos de tipo "{}" no pueden leer los resultados de una corrida después de terminar una simulación. '
            'Debes especificar "vars_interés" cuando corres la simulación para poder acceder a los resultados después. '
            'Si estás desarrollando esta envoltura y quieres agregar esta funcionalidad, debes implementar la '
            'función "._leer_resultados()" en tu envoltura.')
                                  .format(símismo.__class__))

    def paralelizable(símismo):
        """
        Indica si el modelo actual se puede paralelizar de manera segura o no. Si implementas una subclase
        paralelizable, reimplementar esta función para devolver ``True``.

        :return: Si el modelo se puede paralelizar (con corridas de nombres distintos) sin encontrar dificultades
          técnicas (por ejemplo, si hay riesgo que las corridas paralelas terminen escribiendo en los mismos
          documents de egresos).
        :rtype: bool
        """
        return False

    def __str__(símismo):
        return símismo.nombre

    def __getinitargs__(símismo):
        return símismo.nombre,

    def __copy__(símismo):
        copia = símismo.__class__(*símismo.__getinitargs__())
        copia.vals_inic = símismo.vals_inic
        copia.vars_clima = símismo.vars_clima
        copia.unidad_tiempo_meses = símismo.unidad_tiempo_meses

        return copia

    def __getstate__(símismo):
        d = {
            'args_inic': símismo.__getinitargs__(),
            'vals_inic': símismo.vals_inic,
            'vars_clima': símismo.vars_clima,
            'unidad_tiempo_meses': símismo.unidad_tiempo_meses
        }
        return d

    def __setstate__(símismo, estado):
        símismo.__init__(*estado['args_inic'])
        símismo.vals_inic = estado['vals_inic']
        símismo.vars_clima = estado['vars_clima']
        símismo.unidad_tiempo_meses = estado['unidad_tiempo_meses']


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
    mod.inic_vals_vars(vls_inic)

    # Después, simular el modelo
    mod.simular(**d_args)
