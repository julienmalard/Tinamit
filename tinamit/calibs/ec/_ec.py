from tinamit.config import _
from ..sintx.ec import Ecuación


class CalibradorEc(object):
    """
    Clase pariente para implementaciones de calibradores de ecuaciones.
    """

    def __init__(símismo, ec, paráms, nombre=None, dialecto='tinamït'):
        """

        Parameters
        ----------
        ec: str or Ec
            La ecuación para calibrar.
        paráms: list
            La lista de nombres de parámetros en la ecuación (variables que hay que calibrar).
        nombre: str
            El nombre del variable dependiente en la ecuación. Obligatorio si la ecuación no especifica variable
            independiente sí misma (p. ej., ``x * b + a`` en vez de ``y = x * b + a``.
        dialecto: str
            El dialecto de la ecuación. Puede ser ``tinamït`` o ``vensim``.
        """

        símismo.ec = ec if isinstance(ec, Ecuación) else Ecuación(ec, nombre=nombre, dialecto=dialecto)
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
        datos = bd.interpolar(vars_bd)

        return datos.rename(
            {v: ll for ll, v in corresp_vars.items()}
        )

    def calibrar(símismo, bd, lugar=None, líms_paráms=None, ops=None, corresp_vars=None, ord_niveles=None):
        """
        Efectua la calibración.

        Parameters
        ----------
        bd: BD
            La base de datos con observaciones para los variables en la ecuación.
        lugar: Lugar
            El lugar cuyos sublugares hay que calibrar; si es ``None`` se calibrará la ecuación con todos
            los datos en ``bd`` sin tener su lugar en cuenta.
        líms_paráms: list
            Límites teoréticos para los parámetros.
        ops: dict
            Opciones que se pasarán directamente a la función de calibración.
        corresp_vars: dict
            Diccionario de correspondencia entre los nombres de los variables en ``bd`` y sus nombres en la ecuación.
        ord_niveles: list
            Desambiguación del orden de niveles.

        Returns
        -------
        dict
            Diccionario con las calibraciones de cada lugar.
        """

        raise NotImplementedError
