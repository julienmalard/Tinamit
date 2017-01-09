import ctypes
import os
import struct

from tinamit.Modelo import Modelo


class EnvolturaMDS(Modelo):
    """
    Esta clase sirve para representar modelo de dinámicas de los sistemas (MDS). Se debe crear una subclase para cada
    tipo de MDS. Al moment, el único incluido es VENSIM.
    """

    def __init__(símismo):
        # Modelos DS se identifican por el nombre 'mds'.
        super().__init__(nombre='mds')

    def inic_vars(símismo):
        """
        Este método se deja a las subclases de `Metodo` para implementar.

        Ver :func:`Modelo.inic_vars` para más información.
        """

        raise NotImplementedError

    def obt_unidad_tiempo(símismo):
        """

        :return:
        :rtype: str
        """
        raise NotImplementedError

    def cambiar_vals_modelo(símismo, valores):
        raise NotImplementedError

    def incrementar(símismo, paso):
        raise NotImplementedError

    def leer_vals(símismo):
        raise NotImplementedError

    def iniciar_modelo(símismo, nombre_corrida, tiempo_final):
        """

        :param nombre_corrida:
        :type nombre_corrida:
        :param tiempo_final:
        :type tiempo_final:

        """
        raise NotImplementedError

    def cambiar_var(símismo, var, val):
        """

        :param var:
        :type var:
        :param val:
        :type val:

        """

        símismo.cambiar_vals(valores={var: val})

    def cerrar_modelo(símismo):
        """

        """
        raise NotImplementedError


class ModeloVENSIM(EnvolturaMDS):
    """

    """

    def __init__(símismo, archivo):

        símismo.dll = dll = ctypes.WinDLL('C:\\Windows\\System32\\vendll32.dll')

        símismo.comanda_vensim(func=dll.vensim_command,
                               args=[''],
                               mensaje_error='Error iniciando VENSIM.')

        símismo.comanda_vensim(func=dll.vensim_command,
                               args='SPECIAL>LOADMODEL|%s' % archivo,
                               mensaje_error='Eroor cargando el modelo de VENSIM.')

        símismo.comanda_vensim(func=dll.vensim_be_quiet, args=[2],
                               mensaje_error='Error en la comanda "vensim_be_quiet".',
                               val_error=-1)

        super().__init__()

    def inic_vars(símismo):
        """

        """

        mem = ctypes.create_string_buffer(0)

        tamaño_nec = símismo.comanda_vensim(func=símismo.dll.vensim_get_varnames,
                                            args=['*', 0, mem, 0],
                                            mensaje_error='Error obteniendo eñ tamaño de los variables VENSIM.',
                                            val_error=-1, devolver=True
                                            )
        mem = ctypes.create_string_buffer(tamaño_nec)

        símismo.comanda_vensim(func=símismo.dll.vensim_get_varnames,
                               args=['*', 0, mem, tamaño_nec],
                               mensaje_error='Error obteniendo los nombres de los variables de VENSIM.',
                               val_error=-1
                               )

        variables = [x for x in mem.raw.decode().split('\x00') if x]
        for i in ['FINAL TIME', 'TIME STEP', 'INITIAL TIME', 'SAVEPER', 'Time']:
            if i in variables:
                variables.remove(i)

        # Sacar variables editables
        mem = ctypes.create_string_buffer(tamaño_nec)
        símismo.comanda_vensim(func=símismo.dll.vensim_get_varnames,
                               args=['*', 12, mem, tamaño_nec],
                               mensaje_error='Error obteniendo los nombres de los variables editables ("Gaming") de '
                                             'VENSIM.',
                               val_error=-1
                               )

        editables = [x for x in mem.raw.decode().split('\x00') if x]

        # Sacar las unidades de los variables, e identificar los variables constantes
        unidades = {}
        constantes = []
        for var in variables:
            mem = ctypes.create_string_buffer(50)
            símismo.comanda_vensim(func=símismo.dll.vensim_get_varattrib,
                                   args=[var, 1, mem, 50],
                                   mensaje_error='Error obteniendo las unidades del variable {} en VENSIM'.format(var),
                                   val_error=-1
                                   )
            unidades[var] = mem.raw.decode().split('\x00')[0]

            mem = ctypes.create_string_buffer(50)
            símismo.comanda_vensim(func=símismo.dll.vensim_get_varattrib,
                                   args=[var, 14, mem, 50],
                                   mensaje_error='Error obteniendo la clase del variable {} en VENSIM'.format(var),
                                   val_error=-1)

            tipo_var = mem.raw.decode()

            if tipo_var == 'Constant':
                constantes.append(var)

        for var in variables:
            dic_var = {'val': None,
                       'unidades': unidades[var],
                       'ingreso': var in editables,
                       'egreso': var not in constantes}

            símismo.variables[var] = dic_var

    def obt_unidad_tiempo(símismo):
        """

        :return:
        :rtype: str

        """

        mem_inter = ctypes.create_string_buffer(50)

        símismo.comanda_vensim(func=símismo.dll.vensim_get_varattrib,
                               args=['TIME STEP', 1, mem_inter, 50],
                               mensaje_error='Error obteniendo las unidades de tiempo de VENSIM.',
                               val_error=-1)

        unidades = mem_inter.raw.decode().split('\x00')[0]

        return unidades

    def iniciar_modelo(símismo, nombre_corrida, tiempo_final):
        """

        """

        if nombre_corrida is None:
            nombre_corrida = 'Corrida Tinamit'

        símismo.comanda_vensim(func=símismo.dll.vensim_command,
                               args="SIMULATE>RUNNAME|%s" % nombre_corrida,
                               mensaje_error='Error iniciando la corrida VENSIM.')

        símismo.comanda_vensim(func=símismo.dll.vensim_command,
                               args='SIMULATE>SETVAL|%s = %i' % ('FINAL TIME', tiempo_final),
                               mensaje_error='Error estableciendo el tiempo final para VENSIM.')

        símismo.comanda_vensim(func=símismo.dll.vensim_command,
                               args="MENU>GAME",
                               mensaje_error='Error inicializando el juego VENSIM.')

    def cambiar_vals_modelo(símismo, valores):
        """

        :param valores:
        :type valores: dict

        """

        for var, val in valores.items():
            símismo.comanda_vensim(func=símismo.dll.vensim_command,
                                   args='SIMULATE>SETVAL|%s = %f' % (var, val),
                                   mensaje_error='Error cambiando el variable %s.' % var)

    def incrementar(símismo, paso):
        """

        :param paso:
        :type paso:

        """

        símismo.comanda_vensim(func=símismo.dll.vensim_command,
                               args="GAME>GAMEINTERVAL|%i" % paso,
                               mensaje_error='Error estableciendo el paso de VENSIM.')

        símismo.comanda_vensim(func=símismo.dll.vensim_command,
                               args="GAME>GAMEON", mensaje_error='Error para incrementar VENSIM.')

    def leer_vals(símismo):
        """

        """

        for var in símismo.vars_saliendo:
            mem_inter = ctypes.create_string_buffer(4)

            símismo.comanda_vensim(func=símismo.dll.vensim_get_val,
                                   args=[var.encode(), mem_inter],
                                   mensaje_error='Error con VENSIM para leer variables.')

            val = struct.unpack('f', mem_inter)[0]

            símismo.variables[var]['val'] = val

    def cerrar_modelo(símismo):
        """

        """

        símismo.comanda_vensim(func=símismo.dll.vensim_command,
                               args="GAME>ENDGAME",
                               mensaje_error='Error para terminar la simulación VENSIM.')

    def verificar_vensim(símismo):
        """
        Esta función regresa el estatus de Vensim. Es particularmente útil para desboguear (no tiene uso en las
          otras funciones de esta clase, y se incluye como ayuda a la programadora.)

        :return: estatus número integral de código de estatus
            0 = Vensim está listo
            1 = Vensim está en una simulación activa
            2 = Vensim está en una simulación, pero no está respondiendo
            3 = Malas noticias
            4 = Error de memoria
            5 = Vensim está en modo de juego
            6 = Memoria no libre. Llamar vensim_command() debería de arreglarlo.
            16 += ver documentación de VENSIM para vensim_check_status() en la sección de DLL (Suplemento DSS)
        :rtype: int

        """

        estatus = símismo.comanda_vensim(func=símismo.dll.vensim_check_status,
                                         args=[],
                                         mensaje_error='Error verificando el estatus de VENSIM. De verdad, la cosa'
                                                       'te va muy mal.',
                                         val_error=-1, devolver=True)
        return int(estatus)

    @staticmethod
    def comanda_vensim(func, args, mensaje_error=None, val_error=None, devolver=False):
        """

        :param func:
        :type func: function
        :param args:
        :type args: list | tuple | str
        :param mensaje_error:
        :type mensaje_error: str
        :param val_error:
        :type val_error: int
        :param devolver:
        :type devolver: bool

        """

        if type(args) is not list:
            args = [args]

        for n, a in enumerate(args):
            if type(a) is str:
                args[n] = a.encode()

        resultado = func(*args)

        if val_error is None:
            error = (resultado != 1)
        else:
            error = (resultado == val_error)

        if error:
            if mensaje_error is None:
                mensaje_error = 'Error con la comanda VENSIM.'

            mensaje_error += ' Código de error {}.'.format(resultado)

            raise OSError(mensaje_error)

        if devolver:
            return resultado


def generar_mds(archivo):
    """

    :param archivo:
    :type archivo: str

    :return:
    :rtype: EnvolturaMDS

    """

    ext = os.path.splitext(archivo)[1]

    if ext == '.vpm':
        return ModeloVENSIM(archivo)
    else:
        raise ValueError('El tipo de modelo {} no se acepta como modelo DS en Tinamit, al momento. Si piensas'
                         'que podrías contribuir aquí, ¡contáctenos!'.format(ext))
