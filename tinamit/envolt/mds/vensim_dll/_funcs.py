import csv
import ctypes
import os
import struct

import numpy as np

from tinamit.config import _
from tinamit.cositas import arch_más_recién


def cargar_mod_vensim(mod, archivo):
    nmbr, ext = os.path.splitext(archivo)
    if ext == '.mdl':

        # Únicamente recrear el archivo .vpm si necesario
        if not os.path.isfile(nmbr + '.vpm') or arch_más_recién(archivo, nmbr + '.vpm'):
            publicar_modelo(mod=mod, archivo=archivo)
        archivo = nmbr + '.vpm'

    elif ext != '.vpm':
        raise ValueError(
            _('Vensim no sabe leer modelos del formato "{}". Debes darle un modelo ".mdl" o ".vpm".').format(ext)
        )

    # Inicializar Vensim
    cmd_vensim(func=mod.vensim_command,
               args=[''],
               mensaje_error=_('Error iniciando Vensim.'))

    # Cargar el modelo
    cmd_vensim(func=mod.vensim_command,
               args='SPECIAL>LOADMODEL|%s' % archivo,
               mensaje_error=_('Error cargando el modelo de Vensim.'))

    # Parámetros estéticos de ejecución.
    cmd_vensim(func=mod.vensim_be_quiet, args=[2],
               mensaje_error=_('Error en la comanda "vensim_be_quiet".'),
               val_error=-1)

    return mod


def inic_modelo(mod, paso, n_pasos, nombre_corrida):
    nombre_corrida = _verificar_nombre(nombre_corrida)

    # Establecer el nombre de la corrida.
    cmd_vensim(func=mod.vensim_command,
               args="SIMULATE>RUNNAME|%s" % nombre_corrida,
               mensaje_error=_('Error iniciando la corrida Vensim.'))

    # Establecer el tiempo final.
    cmd_vensim(func=mod.vensim_command,
               args='SIMULATE>SETVAL|%s = %i' % ('FINAL TIME', n_pasos + 1),
               mensaje_error=_('Error estableciendo el tiempo final para Vensim.'))

    # Iniciar la simulación en modo juego ("Game"). Esto permitirá la actualización de los valores de los variables
    # a través de la simulación.
    cmd_vensim(func=mod.vensim_command,
               args="MENU>GAME",
               mensaje_error=_('Error inicializando el juego Vensim.'))

    # Es ABSOLUTAMENTE necesario establecer el intervalo del juego aquí. Sino, no reinicializa el paso
    # correctamente entre varias corridas (aún modelos) distintas.
    cmd_vensim(func=mod.vensim_command,
               args="GAME>GAMEINTERVAL|%i" % paso,
               mensaje_error=_('Error estableciendo el paso de Vensim.'))


def avanzar_modelo(mod):
    # Avanzar el modelo.
    cmd_vensim(func=mod.vensim_command,
               args="GAME>GAMEON", mensaje_error=_('Error en incrementar Vensim.'))


def estab_paso(mod, paso):
    cmd_vensim(func=mod.vensim_command,
               args="GAME>GAMEINTERVAL|%i" % paso,
               mensaje_error=_('Error estableciendo el paso de Vensim.'))


def obt_paso_inicial(mod):
    # para hacer: verificar
    try:
        return obt_val_var(mod, 'Game Interval', subs=None)
    except ValueError:
        return obt_val_var(mod, 'TIME STEP', subs=None)


def cambiar_val(mod, var, val):
    cmd_vensim(func=mod.vensim_command,
               args='SIMULATE>SETVAL|%s = %f' % (var, val),
               mensaje_error=_('Error cambiando el variable %s.') % var)


def verificar_vensim(símismo):
    """
    Esta función regresa el estatus de Vensim. Es particularmente útil para desboguear (no tiene uso en las
    otras funciones de esta clase, y se incluye como ayuda a la programadora.)

    :return: Código de estatus Vensim:
        | 0 = Vensim está listo
        | 1 = Vensim está en una simulación activa
        | 2 = Vensim está en una simulación, pero no está respondiendo
        | 3 = Malas noticias
        | 4 = Error de memoria
        | 5 = Vensim está en modo de juego
        | 6 = Memoria no libre. Llamar vensim_command() debería de arreglarlo.
        | 16 += ver documentación de Vensim para vensim_check_status() en la sección de DLL (Suplemento DSS)
    :rtype: int

    """

    # Obtener el estatus.
    estatus = cmd_vensim(func=símismo.mod.vensim_check_status,
                         args=[],
                         mensaje_error=_('Error verificando el estatus de Vensim. De verdad, la cosa '
                                         'te va muy mal.'),
                         val_error=-1)
    return int(estatus)


def publicar_modelo(mod, archivo):  # pragma: sin cobertura

    cmd_vensim(mod.vensim_command, 'SPECIAL>LOADMODEL|%s' % archivo)

    archivo_frm = os.path.join(os.path.split(os.path.dirname(__file__))[0], 'VENSIM.frm')
    cmd_vensim(mod.vensim_command, ('FILE>PUBLISH|%s' % archivo_frm))


def obt_vars(mod):
    l_nombres = []
    for t in [1, 2, 4, 5, 12]:
        mem = ctypes.create_string_buffer(0)  # Crear una memoria intermedia

        # Verificar el tamaño necesario
        tamaño_nec = cmd_vensim(
            func=mod.vensim_get_varnames,
            args=['*', t, mem, 0],
            mensaje_error=_('Error obteniendo eñ tamaño de los variables Vensim.'),
            val_error=-1
        )

        mem = ctypes.create_string_buffer(tamaño_nec)  # Una memoria intermedia con el tamaño apropiado

        # Guardar y decodar los nombres de los variables.
        cmd_vensim(func=mod.vensim_get_varnames,
                   args=['*', t, mem, tamaño_nec],
                   mensaje_error=_('Error obteniendo los nombres de los variables de Vensim.'),
                   val_error=-1
                   )
        l_nombres += [
            x for x in mem.raw.decode().split('\x00')
            if x and x not in ['FINAL TIME', 'TIME STEP', 'INITIAL TIME', 'SAVEPER', 'Time']
        ]
    return l_nombres


def obt_editables(mod):
    # Para obtener los nombres de variables editables (se debe hacer así y no por `tipo_var` porque Vensim
    # los reporta como de tipo `Auxiliary`.
    mem = ctypes.create_string_buffer(0)  # Crear una memoria intermedia

    # Verificar el tamaño necesario
    tamaño_nec = cmd_vensim(
        func=mod.vensim_get_varnames,
        args=['*', 12, mem, 0],
        mensaje_error=_('Error obteniendo eñ tamaño de los variables Vensim.'),
        val_error=-1
    )

    mem = ctypes.create_string_buffer(tamaño_nec)  # Una memoria intermedia con el tamaño apropiado

    cmd_vensim(
        func=mod.vensim_get_varnames,
        args=['*', 12, mem, tamaño_nec],
        mensaje_error=_('Error obteniendo los nombres de los variables editables ("Gaming") de '
                        'VENSIM.'),
        val_error=-1
    )

    return [x for x in mem.raw.decode().split('\x00') if x]


def obt_unid_tiempo(mod):
    return obt_atrib_var(
        mod, var='TIME STEP', cód_attrib=1,
        mns_error=_('Error obteniendo la unidad de tiempo para el modelo Vensim.')
    )


def _obt_val_var_unidim(mod, var):
    # Una memoria
    mem_inter = ctypes.create_string_buffer(4)

    # Leer el valor del variable
    cmd_vensim(func=mod.vensim_get_val,
               args=[str(var), mem_inter],
               mensaje_error=_('Error con Vensim para leer variable "{}".').format(var))

    # Decodar
    return struct.unpack('f', mem_inter)[0]


def vdf_a_csv(mod, archivo_csv):

    # Vensim hace la conversión para nosotr@s
    cmd_vensim(
        mod.vensim_command,
        'MENU>VDF2CSV|{archVDF}|{archCSV}'.format(
            archVDF='!.vdf', archCSV='!.csv'  # En Vensim, "!" quiere decir la corrida activa
        ).encode()
    )

    # Cortar el último paso de simulación. Tinamït siempre corre simulaciones de Vensim para 1 paso adicional
    # para permitir que valores de variables conectados se puedan actualizar.
    # Para que quede claro: esto es por culpa de un error en Vensim, no es culpa nuestra.
    with open(archivo_csv + '.csv', 'r', encoding='UTF-8') as d:
        filas = [f[:-1] if len(f) > 2 else f for f in csv.reader(d)]

    # Hay que abrir el archivo de nuevo para re-escribir sobre el contenido existente-
    with open(archivo_csv + '.csv', 'w', encoding='UTF-8', newline='') as d:
        csv.writer(d).writerows(filas)


def cerrar_vensim(mod):
    # Necesario para guardar los últimos valores de los variables conectados. (Muy incómodo, yo sé.)
    estab_paso(mod, 1)  # justo acaso

    cmd_vensim(func=mod.vensim_command,
               args="GAME>GAMEON",
               mensaje_error=_('Error terminando la simulación Vensim.'))

    # ¡Por fin! Llamar la comanda para terminar la simulación.
    cmd_vensim(func=mod.vensim_command,
               args="GAME>ENDGAME",
               mensaje_error=_('Error terminando la simulación Vensim.'))


def obt_atrib_var(mod, var, cód_attrib, mns_error=None):
    if cód_attrib in [4, 5, 6, 7, 8, 9, 10]:
        lista = True
    elif cód_attrib in [1, 2, 3, 11, 12, 13, 14]:
        lista = False
    else:
        raise ValueError(_('Código "{}" no reconocido para la comanda Vensim de obtener atributos de variables.')
                         .format(cód_attrib))

    if mns_error is None:
        l_atrs = [_('las unidades'), _('la descipción'), _('la ecuación'), _('las causas'), _('las consecuencias'),
                  _('la causas iniciales'), _('las causas activas'), _('los subscriptos'),
                  _('las combinaciones de subscriptos'), _('los subscriptos de gráfico'), _('el mínimo'),
                  _('el máximo'), _('el rango'), _('el tipo_mod')]
        mns_error1 = _('Error leyendo el tamaño de memoria para obtener {} del variable "{}" en Vensim') \
            .format(l_atrs[cód_attrib - 1], var)
        mns_error2 = _('Error leyendo {} del variable "{}" en Vensim.').format(l_atrs[cód_attrib - 1], var)
    else:
        mns_error1 = mns_error2 = mns_error

    mem = ctypes.create_string_buffer(10)
    tmñ = cmd_vensim(
        func=mod.vensim_get_varattrib,
        args=[var, cód_attrib, mem, 0],
        mensaje_error=mns_error1,
        val_error=-1,
    )

    mem = ctypes.create_string_buffer(tmñ)
    cmd_vensim(func=mod.vensim_get_varattrib,
               args=[var, cód_attrib, mem, tmñ],
               mensaje_error=mns_error2,
               val_error=-1)

    if lista:
        return [x for x in mem.raw.decode().split('\x00') if x]
    else:
        return mem.value.decode()


def cmd_vensim(func, args, mensaje_error=None, val_error=None):  # pragma: sin cobertura
    """
    Esta función sirve para llamar todo tipo_mod de comanda Vensim.

    Parameters
    ----------
    func: callable
        La función DLL a llamar.
    args: list | str
        Los argumento a pasar a la función. Si no hay, usar una lista vacía.
    mensaje_error: str
        El mensaje de error para mostrar si hay un error en la comanda.
    val_error: int
        Un valor de regreso Vensim que indica un error para esta función. Si se deja ``None``, todos
        valores que no son 1 se considerarán como erróneas.

    Returns
    -------
    int
        El código devuelto por Vensim.
    """

    # Asegurarse que args es una lista
    if type(args) is not list:
        args = [args]

    # Encodar en bytes todos los argumentos de texto.
    for n, a in enumerate(args):
        if type(a) is str:
            args[n] = a.encode()

    # Llamar la función Vensim y guardar el resultado.
    try:
        resultado = func(*args)
    except OSError:
        try:
            resultado = func(*args)
        except OSError as e:
            raise OSError(e)

    # Verificar su hubo un error.
    if val_error is None:
        error = (resultado != 1)
    else:
        error = (resultado == val_error)

    # Si hubo un error, avisar el usuario.
    if error:
        if mensaje_error is None:
            mensaje_error = _('Error con la comanda Vensim.')

        mensaje_error += _(' Código de error {}.').format(resultado)

        raise ValueError(mensaje_error)

    # Devolver el valor devuelto por la función Vensim
    return resultado


def _verificar_nombre(nombre):
    # Vensim tiene un problema raro con nombres de corridas con '.' (y quién sabe qué más)
    return nombre.replace('.', '_')


def obt_val_var(mod, var, subs):
    if not subs:
        # Si el variable no tiene dimensiones (subscriptos)...

        # Leer su valor.
        val = _obt_val_var_unidim(mod, var)

    else:
        val = np.zeros_like(subs)
        for n, s in enumerate(subs):
            var_s = str(var) + s

            # Leer su valor.
            v = _obt_val_var_unidim(mod, var_s)

            # Guardar en el diccionario interno.
            val[n] = v  # Para hacer: opciones de dimensiones múltiples

    return val
