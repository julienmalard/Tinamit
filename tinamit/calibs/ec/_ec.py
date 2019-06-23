from tinamit.config import _
from ..sintx.ec import Ecuación


class CalibradorEc(object):
    def __init__(símismo, ec, paráms):
        símismo.ec = ec if isinstance(ec, Ecuación) else Ecuación(ec)
        símismo.paráms = paráms

        # Asegurarse que se especificó el variable y.
        if símismo.ec.nombre is None:
            raise ValueError(_(
                'Debes especificar el nombre de la ecuación del variable dependiente, o con el parámetro'
                '`nombre`, o directamente en la ecuación, por ejemplo: "y = a*x ..."'
            ))

    def _gen_líms_paráms(símismo, líms_paráms):
        # Aplicar y formatear límites para parámetros sin límites
        líms_paráms = líms_paráms or {}
        for p in símismo.paráms:
            if p not in líms_paráms or líms_paráms[p] is None:
                líms_paráms[p] = (None, None)

        return líms_paráms

    def _extraer_vars(símismo):
        vars_ec = símismo.ec.variables()
        vars_x = [v for v in vars_ec if v not in símismo.paráms]
        var_y = símismo.ec.nombre

        return vars_x, var_y

    @staticmethod
    def _obt_datos(bd, vars_interés, corresp_vars):
        corresp_vars = corresp_vars or {}
        vars_bd = [v if v not in corresp_vars else corresp_vars[v] for v in vars_interés]
        return bd.obt_vals(vars_bd).dropna('n').rename(corresp_vars)

    def calibrar(símismo, bd, lugar=None, líms_paráms=None, ops=None, corresp_vars=None, ord_niveles=None):
        raise NotImplementedError
