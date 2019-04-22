from warnings import warn as avisar

from tinamit.config import _
from tinamit.unids.conv import convertir


class ConexionesVars(object):
    def __init__(símismo):
        símismo._conexiones = []

    def agregar(símismo, conex):
        if any(conex.var_recip is c.var_recip for c in símismo):
            raise ValueError(_('El variable "{}" ya está conectado como variable recipiente.').format(conex.var_recip))

        # Si esta conexíon depende de otra, asegurarse que la otra se actualice antes de ésta
        i = next((i + 1 for i, c in enumerate(símismo._conexiones) if (c.var_recip is conex.var_fuente)), 0)
        símismo._conexiones.insert(i, conex)

    def quitar(símismo, var_fuente, modelo_fuente, modelo_recip, var_recip):
        for c in símismo._buscar(var_fuente, modelo_fuente, modelo_recip, var_recip):
            símismo._conexiones.remove(c)

    def _buscar(símismo, var_fuente, modelo_fuente, modelo_recip, var_recip):
        return [
            c for c in símismo
            if (c.var_fuente is var_fuente) and (c.modelo_fuente is modelo_fuente) and (
                    modelo_recip is None or c.modelo_recip is modelo_recip) and (
                       var_recip is None or c.var_recip is var_recip)
        ]

    def __iter__(símismo):
        for c in símismo._conexiones:
            yield c


class Conex(object):
    def __init__(símismo, var_fuente, modelo_fuente, var_recip, modelo_recip, conv):

        if modelo_recip is modelo_fuente:
            raise ValueError(_('Los modelos de variables conectados deben ser distintos.'))

        símismo.var_fuente = var_fuente
        símismo.modelo_fuente = modelo_fuente
        símismo.var_recip = var_recip
        símismo.modelo_recip = modelo_recip

        símismo._verificar()

        símismo.conv = _resolv_conv(var_fuente.unid, var_recip.unid, conv=conv)

    def _verificar(símismo):
        v_f = símismo.var_fuente
        v_r = símismo.var_recip

        if v_f.dims != v_r.dims:
            raise ValueError(
                _('Dimensiones incompatibles entre variables "{}" {} y "{}" {}.').format(v_f, v_f.dims, v_r, v_r.dims)
            )

        if not _líms_compat(símismo.var_fuente.líms, símismo.var_recip.líms):
            avisar(_('Límites potencialmente incompatibles entre variables "{}" y "{}".').format(
                símismo.var_fuente, símismo.var_recip)
            )


def _resolv_conv(unid_1, unid_2, conv):
    if conv is None:
        # Si no se especificó factor de conversión...

        mensaje = _('No se pudo identificar una conversión automática entre {} y {}. '
                    'Se está suponiendo un factor de conversión de 1.').format(unid_1, unid_2)
        if unid_1 is None or unid_2 is None:
            conv = 1
            if not (unid_1 is unid_2 is None):
                avisar(mensaje)

        else:
            # Intentar hacer una conversión automática.
            try:
                conv = convertir(de=unid_1, a=unid_2)
            except ValueError:
                # Si eso no funcionó, suponer una conversión de 1.
                conv = 1
                avisar(mensaje)

    return conv


def _líms_compat(líms_1, líms_2):
    return (líms_1[0] >= líms_2[0]) and (líms_1[1] <= líms_2[1])
