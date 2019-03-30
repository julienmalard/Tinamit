import ctypes

from tinamit.config import _


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
