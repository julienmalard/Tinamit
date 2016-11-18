class Var(object):
    def __init__(símismo, nombre, parientes, ec, unidades, comentarios):
        símismo.nombre = nombre
        símismo.parientes = parientes
        símismo.hijos = []
        símismo.ec = ec
        símismo.unidades = unidades
        símismo.comentarios = comentarios


class VarVENSIM(Var):

    máx_car = 80

    def __init__(símismo, texto):


        super().__init__(nombre, parientes, ec, unidades, comentarios)

    def






def sacar_variables(texto, n=None):
    """

    :param texto:
    :type texto: str

    :param n:
    :type n: int

    :return:
    :rtype: list[str]
    """

    return regex(".*"
    o[a - zA - Z][a - zA - Z0 - 9] *, n)