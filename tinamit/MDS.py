import ctypes
import os
import numpy as np
import struct

from tinamit.Modelo import Modelo


class EnvolturaMDS(Modelo):
    """
    Esta clase sirve para representar modelo de dinámicas de los sistemas (MDS). Se debe crear una subclase para cada
    tipo de MDS. Al moment, el único incluido es VENSIM.
    """

    def __init__(símismo):
        # Listas vacías para distintos tipos de variables.
        símismo.constantes = []
        símismo.niveles = []
        símismo.flujos = []

        # Modelos DS se identifican por el nombre 'mds'.
        super().__init__(nombre='mds')

    def inic_vars(símismo):
        """
        Este método se deja a las subclases de :class:`~tinamit.MDS.EnvolturaMDS` para implementar. Además de los
        diccionarios de variables normales, debe establecer `símismo.constantes`, `símismo.flujos`, y `símismo.niveles`.

        Ver :func:`Modelo.Modelo.inic_vars` para más información.
        """

        raise NotImplementedError

    def obt_unidad_tiempo(símismo):
        """
        Cada envoltura de programa DS debe implementar eset metodo para devolver las unidades de tiempo del modelo DS
        cargado.

        :return: Las unidades del modelo DS cargado.
        :rtype: str

        """
        raise NotImplementedError

    def cambiar_vals_modelo_interno(símismo, valores):
        """
        Este método se deja a las subclases de :class:`~tinamit.MDS.EnvolturaMDS` para implementar.

        Ver :func:`Modelo.Modelo.cambiar_vals_modelo` para más información.

        :param valores: El diccionario de valores para cambiar.
        :type valores: dict

        """
        raise NotImplementedError

    def incrementar(símismo, paso):
        """
        Este método se deja a las subclases de :class:`~tinamit.MDS.EnvolturaMDS` para implementar.

        Debe avanzar la simulación del modelo DS de ``paso`` unidades de tiempo.  Ver
        :func:`Modelo.Modelo.incrementar` para más información.

        :param paso: El paso con cual incrementar el modelo.
        :type paso: int

        """
        raise NotImplementedError

    def leer_vals(símismo):
        """
        Este método se deja a las subclases de :class:`~tinamit.MDS.EnvolturaMDS` para implementar.

        Debe leer los valores de los variables en el modelo MDS. Si es más fácil, puede simplemente leer los valores
        de los variables que están en la lista ``EnvolturaMDS.vars_saliendo`` (los variables del DS que están
        conectados con el modelo biofísico).

        Ver :func:`Modelo.Modelo.leer_vals` para más información.

        """
        raise NotImplementedError

    def iniciar_modelo(símismo, nombre_corrida, tiempo_final):
        """
        Este método se deja a las subclases de :class:`~tinamit.MDS.EnvolturaMDS` para implementar. Notar que la
        implementación de este método debe incluir la aplicación de valores iniciales.

        Ver :func:`Modelo.Modelo.iniciar_modelo` para más información.

        :param nombre_corrida: El nombre de la corrida (útil para guardar datos).
        :type nombre_corrida: str

        :param tiempo_final: El tiempo final de la simulación.
        :type tiempo_final: int

        """
        raise NotImplementedError

    def cerrar_modelo(símismo):
        """
        Este método se deja a las subclases de :class:`~tinamit.MDS.EnvolturaMDS` para implementar.

        Debe llamar acciones necesarias para terminar la simulación y cerrar el modelo DS, si aplican.

        Ver :func:`Modelo.Modelo.cerrar_modelo` para más información.

        """
        raise NotImplementedError


class ModeloVensim(EnvolturaMDS):
    """
    Esta es la envoltura para modelos de tipo VENSIM. Puede leer y controlar (casi) cualquier modelo VENSIM para que
    se pueda emplear en Tinamit.
    Necesitarás la versión DSS de VENSIM para que funcione en Tinamit.
    """

    def __init__(símismo, archivo):
        """
        La función de inicialización del modelo. Creamos el vínculo con el DLL de VENSIM y cargamos el modelo
        especificado.

        :param archivo: El archivo del modelo que queieres cargar, en formato .vpm.
        :type archivo: str
        """

        # Llamar el DLL de VENSIM.
        símismo.dll = dll = ctypes.WinDLL('C:\\Windows\\System32\\vendll32.dll')

        # Inicializar Vensim
        símismo.comanda_vensim(func=dll.vensim_command,
                               args=[''],
                               mensaje_error='Error iniciando VENSIM.')

        # Cargar el modelo
        símismo.comanda_vensim(func=dll.vensim_command,
                               args='SPECIAL>LOADMODEL|%s' % archivo,
                               mensaje_error='Eroor cargando el modelo de VENSIM.')

        # Parámetros estéticos de ejecución.
        símismo.comanda_vensim(func=dll.vensim_be_quiet, args=[2],
                               mensaje_error='Error en la comanda "vensim_be_quiet".',
                               val_error=-1)

        # El paso para incrementar
        símismo.paso = 1

        # Una lista de variables editables
        símismo.editables = []

        # Inicializar ModeloVENSIM como una EnvolturaMDS.
        super().__init__()

    def inic_vars(símismo):
        """
        Inicializamos el diccionario de variables del modelo VENSIM.
        """

        # Primero, verificamos el tamañano de memoria necesario para guardar una lista de los nombres de los variables.

        mem = ctypes.create_string_buffer(0)  # Crear una memoria intermedia

        # Verificar el tamaño necesario
        tamaño_nec = símismo.comanda_vensim(func=símismo.dll.vensim_get_varnames,
                                            args=['*', 0, mem, 0],
                                            mensaje_error='Error obteniendo eñ tamaño de los variables VENSIM.',
                                            val_error=-1, devolver=True
                                            )

        mem = ctypes.create_string_buffer(tamaño_nec)  # Una memoria intermedia con el tamaño apropiado

        # Guardar y decodar los nombres de los variables.
        símismo.comanda_vensim(func=símismo.dll.vensim_get_varnames,
                               args=['*', 0, mem, tamaño_nec],
                               mensaje_error='Error obteniendo los nombres de los variables de VENSIM.',
                               val_error=-1
                               )
        variables = [x for x in mem.raw.decode().split('\x00') if x]

        # Quitar los nombres de variables VENSIM genéricos de la lista.
        for i in ['FINAL TIME', 'TIME STEP', 'INITIAL TIME', 'SAVEPER', 'Time']:
            if i in variables:
                variables.remove(i)

        # Sacar los nombres de variables editables
        símismo.comanda_vensim(func=símismo.dll.vensim_get_varnames,
                               args=['*', 12, mem, tamaño_nec],
                               mensaje_error='Error obteniendo los nombres de los variables editables ("Gaming") de '
                                             'VENSIM.',
                               val_error=-1
                               )

        editables = [x for x in mem.raw.decode().split('\x00') if x]

        # Sacar las unidades y las dimensiones de los variables, e identificar los variables constantes
        unidades = {}
        constantes = []
        niveles = []
        flujos = []
        dims = {}
        nombres_subs = {}

        for var in variables:
            # Para cada variable...

            # Sacar sus unidades
            mem = ctypes.create_string_buffer(50)
            símismo.comanda_vensim(func=símismo.dll.vensim_get_varattrib,
                                   args=[var, 1, mem, 50],
                                   mensaje_error='Error obteniendo las unidades del variable "{}" en '
                                                 'VENSIM'.format(var),
                                   val_error=-1
                                   )
            # Guardamos las unidades en un diccionario temporario.
            unidades[var] = mem.raw.decode().split('\x00')[0]

            # Verificar si el variable es un constante (ingreso)
            mem = ctypes.create_string_buffer(50)
            símismo.comanda_vensim(func=símismo.dll.vensim_get_varattrib,
                                   args=[var, 14, mem, 50],
                                   mensaje_error='Error obteniendo la clase del variable "{}" en VENSIM'.format(var),
                                   val_error=-1)

            tipo_var = mem.value.decode()

            # Guardamos los variables constantes en una lista.
            if tipo_var == 'Constant':
                constantes.append(var)
            elif tipo_var == 'Level':
                niveles.append(var)

            if tipo_var != 'Constraint':
                # Sacar las dimensiones del variable
                mem = ctypes.create_string_buffer(10)
                tmñ_sub = símismo.comanda_vensim(func=símismo.dll.vensim_get_varattrib,
                                                 args=[var, 9, mem, 0],
                                                 mensaje_error='Error leyendo el tamaño de memoria para los subscriptos'
                                                               ' del variable "{}" en Vensim'.format(var),
                                                 val_error=-1,
                                                 devolver=True)

                mem = ctypes.create_string_buffer(tmñ_sub)
                símismo.comanda_vensim(func=símismo.dll.vensim_get_varattrib,
                                       args=[var, 9, mem, tmñ_sub],
                                       mensaje_error='Error leyendo los subscriptos del '
                                                     'variable "{}" en Vensim.'.format(var),
                                       val_error=-1)

                subs = [x for x in mem.raw.decode().split('\x00') if x]

            else:
                subs = []

            if len(subs):
                dims[var] = (len(subs),)  # Para hacer: soporte para más que 1 dimensión
                nombres_subs[var] = subs
            else:
                dims[var] = (1,)
                nombres_subs[var] = None

        # Actualizar el diccionario de variables.
        for var in variables:
            # Para cada variable, creamos un diccionario especial, con su valor y unidades. Puede ser un variable
            # de ingreso si es de tipo editable ("Gaming"), y puede ser un variable de egreso si no es un valor
            # constante.
            dic_var = {'val': None if dims[var] == (1,) else np.empty(dims[var]),
                       'unidades': unidades[var],
                       'ingreso': var in editables,
                       'dims': dims[var],
                       'subscriptos': nombres_subs[var],
                       'egreso': var not in constantes}

            # Guadar el diccionario del variable en el diccionario general de variables.
            símismo.variables[var] = dic_var

        for l in [símismo.editables, símismo.constantes, símismo.niveles, símismo.flujos]:
            l.clear()

        símismo.editables.extend(editables)
        símismo.constantes.extend(constantes)
        símismo.niveles.extend(niveles)
        símismo.flujos.extend(flujos)  # para hacer

    def obt_unidad_tiempo(símismo):
        """
        Aquí, sacamos las unidades de tiempo del modelo VENSIM.

        :return: Las unidades de tiempo.
        :rtype: str

        """

        # Una memoria intermediaria.
        mem_inter = ctypes.create_string_buffer(50)

        # Sacar las unidades del variable "TIME STEP".
        símismo.comanda_vensim(func=símismo.dll.vensim_get_varattrib,
                               args=['TIME STEP', 1, mem_inter, 50],
                               mensaje_error='Error obteniendo las unidades de tiempo de VENSIM.',
                               val_error=-1)

        # Decodar
        unidades = mem_inter.raw.decode().split('\x00')[0]

        return unidades

    def iniciar_modelo(símismo, tiempo_final, nombre_corrida):
        """
        Acciones necesarias para iniciar el modelo VENSIM.

        :param nombre_corrida: El nombre de la corrida del modelo.
        :type nombre_corrida: str

        :param tiempo_final: El tiempo final de la simulación.
        :type tiempo_final: int

        """

        # En Vensim, tenemos que incializar los valores de variables constantes antes de empezar la simulación.
        símismo.cambiar_vals({var: val for var, val in símismo.vals_inic.items()
                              if var in símismo.constantes})

        # Establecer el nombre de la corrida.
        símismo.comanda_vensim(func=símismo.dll.vensim_command,
                               args="SIMULATE>RUNNAME|%s" % nombre_corrida,
                               mensaje_error='Error iniciando la corrida VENSIM.')

        # Establecer el tiempo final.
        símismo.comanda_vensim(func=símismo.dll.vensim_command,
                               args='SIMULATE>SETVAL|%s = %i' % ('FINAL TIME', tiempo_final),
                               mensaje_error='Error estableciendo el tiempo final para VENSIM.')

        # Iniciar la simulación en modo juego ("Game"). Esto permitirá la actualización de los valores de los variables
        # a través de la simulación.
        símismo.comanda_vensim(func=símismo.dll.vensim_command,
                               args="MENU>GAME",
                               mensaje_error='Error inicializando el juego VENSIM.')

        # Aplicar los valores iniciales de variables editables (que
        símismo.cambiar_vals({var: val for var, val in símismo.vals_inic.items()
                              if var not in símismo.constantes})

    def cambiar_vals_modelo_interno(símismo, valores):
        """
        Esta función cambiar los valores de variables en VENSIM. Notar que únicamente los variables identificados como
        de tipo "Gaming" en el modelo podrán actualizarse.

        :param valores: Un diccionario de variables y sus nuevos valores.
        :type valores: dict

        """

        for var, val in valores.items():
            # Para cada variable para cambiar...

            if símismo.variables[var]['dims'] == (1,):
                # Si el variable no tiene dimensiones (subscriptos)...

                # Actualizar el valor en el modelo VENSIM.
                símismo.comanda_vensim(func=símismo.dll.vensim_command,
                                       args='SIMULATE>SETVAL|%s = %f' % (var, val),
                                       mensaje_error='Error cambiando el variable %s.' % var)
            else:
                # Para hacer: opciones de dimensiones múltiples
                # La lista de subscriptos
                subs = símismo.variables[var]['subscriptos']
                if isinstance(val, np.ndarray):
                    matr = val
                else:
                    matr = np.empty(len(subs))
                    matr[:] = val

                for n, s in enumerate(subs):
                    var_s = var + s
                    val_s = matr[n]

                    símismo.comanda_vensim(func=símismo.dll.vensim_command,
                                           args='SIMULATE>SETVAL|%s = %f' % (var_s, val_s),
                                           mensaje_error='Error cambiando el variable %s.' % var_s)

    def incrementar(símismo, paso):
        """
        Esta función avanza la simulación VENSIM de ``paso`` pasos.

        :param paso: El número de pasos para tomar.
        :type paso: int

        """

        # Establecer el paso.
        if paso != símismo.paso:
            símismo.comanda_vensim(func=símismo.dll.vensim_command,
                                   args="GAME>GAMEINTERVAL|%i" % paso,
                                   mensaje_error='Error estableciendo el paso de VENSIM.')
            símismo.paso = paso

        # Avanzar el modelo.
        símismo.comanda_vensim(func=símismo.dll.vensim_command,
                               args="GAME>GAMEON", mensaje_error='Error para incrementar VENSIM.')

    def leer_vals(símismo):
        """
        Este método lee los valores intermediaros de los variables del modelo VENSIM. Para ahorar tiempo, únicamente
        lee esos variables que están en la lista de ``ModeloVENSIM.vars_saliendo``.
        """

        # Una memoria
        mem_inter = ctypes.create_string_buffer(4)

        for var in símismo.vars_saliendo:
            # Para cada variable que está conectado con el modelo biofísico...

            if símismo.variables[var]['dims'] == (1,):
                # Si el variable no tiene dimensiones (subscriptos)...

                # Leer su valor.
                símismo.comanda_vensim(func=símismo.dll.vensim_get_val,
                                       args=[var, mem_inter],
                                       mensaje_error='Error con VENSIM para leer variables.')

                # Decodar
                val = struct.unpack('f', mem_inter)[0]

                # Guardar en el diccionario interno.
                símismo.variables[var]['val'] = val

            else:
                for n, s in enumerate(símismo.variables[var]['subscriptos']):
                    var_s = var + s

                    # Leer su valor.
                    símismo.comanda_vensim(func=símismo.dll.vensim_get_val,
                                           args=[var_s, mem_inter],
                                           mensaje_error='Error con VENSIM para leer variables.')

                    # Decodar
                    val = struct.unpack('f', mem_inter)[0]

                    # Guardar en el diccionario interno.
                    símismo.variables[var]['val'][n] = val  # Para hacer: opciones de dimensiones múltiples

    def cerrar_modelo(símismo):
        """
        Cierre la simulación VENSIM.
        """

        # Llamar la comanda para terminar la simulación.
        símismo.comanda_vensim(func=símismo.dll.vensim_command,
                               args="GAME>ENDGAME",
                               mensaje_error='Error para terminar la simulación VENSIM.')

    def verificar_vensim(símismo):
        """
        Esta función regresa el estatus de Vensim. Es particularmente útil para desboguear (no tiene uso en las
        otras funciones de esta clase, y se incluye como ayuda a la programadora.)

        :return: estatus número integral de código de estatus
            | 0 = Vensim está listo
            | 1 = Vensim está en una simulación activa
            | 2 = Vensim está en una simulación, pero no está respondiendo
            | 3 = Malas noticias
            | 4 = Error de memoria
            | 5 = Vensim está en modo de juego
            | 6 = Memoria no libre. Llamar vensim_command() debería de arreglarlo.
            | 16 += ver documentación de VENSIM para vensim_check_status() en la sección de DLL (Suplemento DSS)
        :rtype: int

        """

        # Obtener el estatus.
        estatus = símismo.comanda_vensim(func=símismo.dll.vensim_check_status,
                                         args=[],
                                         mensaje_error='Error verificando el estatus de VENSIM. De verdad, la cosa'
                                                       'te va muy mal.',
                                         val_error=-1, devolver=True)
        return int(estatus)

    @staticmethod
    def comanda_vensim(func, args, mensaje_error=None, val_error=None, devolver=False):
        """
        Esta función sirve para llamar todo tipo de comanda VENSIM.

        :param func: La función DLL a llamar.
        :type func: callable

        :param args: Los argumento a pasar a la función. Si no hay, usar una lista vacía.
        :type args: list | str

        :param mensaje_error: El mensaje de error para mostrar si hay un error en la comanda.
        :type mensaje_error: str

        :param val_error: Un valor de regreso VENSIM que indica un error para esta función. Si se deja ``None``, todos
        valores que no son 1 se considerarán como erróneas.

        :type val_error: int

        :param devolver: Si se debe devolver el valor devuelto por VENSIM o no.
        :type devolver: bool

        """

        # Asegurarse que args es una lista
        if type(args) is not list:
            args = [args]

        # Encodar en bytes todos los argumentos de texto.
        for n, a in enumerate(args):
            if type(a) is str:
                args[n] = a.encode()

        # Llamar la función VENSIM y guardar el resultado.
        resultado = func(*args)

        # Verificar su hubo un error.
        if val_error is None:
            error = (resultado != 1)
        else:
            error = (resultado == val_error)

        # Si hubo un error, avisar el usuario.
        if error:
            if mensaje_error is None:
                mensaje_error = 'Error con la comanda VENSIM.'

            mensaje_error += ' Código de error {}.'.format(resultado)

            raise OSError(mensaje_error)

        # Devolver el valor devuelto por la función VENSIM, si aplica.
        if devolver:
            return resultado


def generar_mds(archivo):
    """
    Esta función genera una instancia de modelo de DS. Identifica el tipo de archivo por su extensión (p. ej., .vpm) y
    después genera una instancia de la subclase apropiada de ``~Tinamit.MDS.EnvolturaMDS``.

    :param archivo: El archivo del modelo DS.
    :type archivo: str

    :return: Un modelo DS.
    :rtype: tinamit.MDS.EnvolturaMDS

    """

    # Identificar la extensión.
    ext = os.path.splitext(archivo)[1]

    # Crear la instancia de modelo apropiada para la extensión del archivo.
    if ext == '.vpm':
        # Modelos VENSIM
        return ModeloVensim(archivo)
    else:
        # Agregar otros tipos de modelos DS aquí.

        # Mensaje para modelos todavía no incluidos en Tinamit.
        raise ValueError('El tipo de modelo "{}" no se acepta como modelo DS en Tinamit al momento. Si piensas'
                         'que podrías contribuir aquí, ¡contáctenos!'.format(ext))


def limpiar_mem(mem):
    """
    Limpia la memoria de un objeto ctypes.

    :param mem: El objeto de memoria
    """

    tmñ = len(mem)
    mem.value = b'\x00' * tmñ
