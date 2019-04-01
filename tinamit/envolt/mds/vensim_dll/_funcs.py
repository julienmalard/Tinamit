import ctypes

from tinamit.config import _


def gen_mod_vensim(archivo):
    try:
        dll_vensim = ops_mód['dll_Vensim']
    except KeyError:
        dll_vensim = None

    # Llamar el DLL de Vensim.
    if dll_vensim is None:
        lugares_probables = [
            'C:\\Windows\\System32\\vendll32.dll',
            'C:\\Windows\\SysWOW64\\vendll32.dll'
        ]
        arch_dll_vensim = símismo._obt_val_config(
            llave='dll_Vensim', cond=os.path.isfile, respaldo=lugares_probables
        )
        if arch_dll_vensim is None:
            dll = None
        else:
            dll = crear_dll_vensim(arch_dll_vensim)
    else:
        dll = crear_dll_vensim(dll_vensim)

    nmbr, ext = os.path.splitext(archivo)
    if ext == '.mdl':
        símismo.tipo_mod = '.mdl'

        if dll is not None:
            # Únicamente recrear el archivo .vpm si necesario
            if not os.path.isfile(nmbr + '.vpm') or arch_más_recién(archivo, nmbr + '.vpm'):
                símismo.publicar_modelo(dll=dll)
            archivo = nmbr + '.vpm'

    elif ext == '.vpm':
        símismo.tipo_mod = '.vpm'

    else:
        raise ValueError(
            _('Vensim no sabe leer modelos del formato "{}". Debes darle un modelo ".mdl" o ".vpm".')
                .format(ext)
        )

    if dll is None:
        return

    # Inicializar Vensim
    cmd_vensim(func=dll.vensim_command,
               args=[''],
               mensaje_error=_('Error iniciando Vensim.'))

    # Cargar el modelo
    cmd_vensim(func=dll.vensim_command,
               args='SPECIAL>LOADMODEL|%s' % archivo,
               mensaje_error=_('Error cargando el modelo de Vensim.'))

    # Parámetros estéticos de ejecución.
    cmd_vensim(func=dll.vensim_be_quiet, args=[2],
               mensaje_error=_('Error en la comanda "vensim_be_quiet".'),
               val_error=-1)

    return dll


def obt_vars(mod):
    l_nombres = []
    for t in [1, 2, 4, 5, 12]:
        mem = ctypes.create_string_buffer(0)  # Crear una memoria intermedia

        # Verificar el tamaño necesario
        tamaño_nec = cmd_vensim(func=mod.vensim_get_varnames,
                                args=['*', t, mem, 0],
                                mensaje_error=_('Error obteniendo eñ tamaño de los variables Vensim.'),
                                val_error=-1, devolver=True
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
    tamaño_nec = cmd_vensim(func=mod.vensim_get_varnames,
                            args=['*', 12, mem, 0],
                            mensaje_error=_('Error obteniendo eñ tamaño de los variables Vensim.'),
                            val_error=-1, devolver=True
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
    tmñ = cmd_vensim(func=mod.vensim_get_varattrib,
                     args=[var, cód_attrib, mem, 0],
                     mensaje_error=mns_error1,
                     val_error=-1,
                     devolver=True)

    mem = ctypes.create_string_buffer(tmñ)
    cmd_vensim(func=mod.vensim_get_varattrib,
               args=[var, cód_attrib, mem, tmñ],
               mensaje_error=mns_error2,
               val_error=-1)

    if lista:
        return [x for x in mem.raw.decode().split('\x00') if x]
    else:
        return mem.value.decode()


def cmd_vensim(func, args, mensaje_error=None, val_error=None, devolver=False):  # pragma: sin cobertura
    """
    Esta función sirve para llamar todo tipo_mod de comanda Vensim.

    :param func: La función DLL a llamar.
    :type func: callable

    :param args: Los argumento a pasar a la función. Si no hay, usar una lista vacía.
    :type args: list | str

    :param mensaje_error: El mensaje de error para mostrar si hay un error en la comanda.
    :type mensaje_error: str

    :param val_error: Un valor de regreso Vensim que indica un error para esta función. Si se deja ``None``, todos
      valores que no son 1 se considerarán como erróneas.
    :type val_error: int

    :param devolver: Si se debe devolver el valor devuelto por Vensim o no.
    :type devolver: bool

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

        raise OSError(mensaje_error)

    # Devolver el valor devuelto por la función Vensim, si aplica.
    if devolver:
        return resultado
