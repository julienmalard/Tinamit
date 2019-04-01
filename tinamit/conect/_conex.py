class ConexionesVars(object):
    def __init__(símismo):
        símismo._conexiones = set()

    def agregar(símismo, conex):
        símismo._conexiones.add(conex)

    def quitar(símismo, var_fuente, modelo_fuente, modelo_recip, var_recip):
        for c in símismo._buscar(var_fuente, modelo_fuente, modelo_recip, var_recip):
            símismo._conexiones.remove(c)

    def _buscar(símismo, var_fuente, modelo_fuente, modelo_recip, var_recip):
        return [
            c for c in símismo
            if (c.var_fuente == var_fuente) and (c.modelo_fuente == modelo_fuente) and (
                    modelo_recip is None or c.modelo_recip == modelo_recip) and (
                       var_recip is None or c.var_recip == var_recip)
        ]

    def __iter__(símismo):
        for c in símismo._conexiones:
            yield c


class Conex(object):
    def __init__(símismo, var_fuente, modelo_fuente, var_recip, modelo_recip, conv):
        símismo.var_fuente = str(var_fuente)
        símismo.modelo_fuente = str(modelo_fuente)
        símismo.var_recip = str(var_recip)
        símismo.modelo_recip = str(modelo_recip)
        símismo.conv = conv or 1
