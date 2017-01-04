import os
import struct
import ctypes

from .Modelo import Modelo


class ModeloMDS(Modelo):
    """

    """

    def __init__(símismo):
        """

        """
        super().__init__(nombre='mds')

    def cambiar_vals(símismo, valores):
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

    def cerrar_modelo(símismo):
        """

        """
        raise NotImplementedError


class ModeloVENSIM(ModeloMDS):
    """

    """

    def __init__(símismo, archivo):

        símismo.dll = dll = ctypes.WinDLL('C:\\Windows\\System32\\vendll32.dll')

        símismo.comanda_vensim(func=dll.vensim_command,
                               args='SPECIAL>LOADMODEL|%s' % archivo,
                               mensaje_error='Eroor cargando el modelo de VENSIM.')

        símismo.comanda_vensim(func=dll.vensim_be_quiet, args=[2],
                               mensaje_error='Error en la comanda "vensim_be_quiet".')

        super().__init__()

    def obt_vars(símismo):
        """

        """

        mem = ctypes.create_string_buffer(0)

        tamaño_nec = símismo.comanda_vensim(func=símismo.dll.vensim_get_varnames,
                                            args=('*', 0, mem, 0),
                                            mensaje_error='Error obteniendo eñ tamaño de los variables VENSIM.',
                                            val_error=-1, devolver=True
                                            )
        mem = ctypes.create_string_buffer(tamaño_nec)

        símismo.comanda_vensim(func=símismo.dll.vensim_get_varnames,
                               args=('*', 0, mem, tamaño_nec),
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
                               args=('*', 12, mem, tamaño_nec),
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
                                   args=(var, 1, mem, 50),
                                   mensaje_error='Error obteniendo las unidades del variable {} en VENSIM'.format(var)
                                   )
            unidades[var] = mem.raw.decode().split('\x00')[0]

            mem = ctypes.create_string_buffer(50)
            símismo.comanda_vensim(func=símismo.dll.vensim_get_varattrib,
                                   args=[var, 14, mem, 50],
                                   mensaje_error='Error obteniendo la clase del variable {} en VENSIM'.format(var))

            tipo_var = mem.raw.decode()

            if tipo_var == 'Constant':
                constantes.append(var)

        for var in variables:
            dic_var = {}

            símismo.variables[var] = (dic_var)

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

    def cambiar_vals(símismo, valores):
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

        for var in símismo.vars_egreso:

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
    :rtype: ModeloMDS

    """

    ext = os.path.splitext(archivo)[1]

    if ext == '.vpm':
        return ModeloVENSIM(archivo)
    else:
        raise ValueError('El tipo de modelo {} no se acepta como modelo DS en Tinamit, al momento. Si piensas'
                         'que podrías contribuir aquí, ¡contáctenos!'.format(ext))
