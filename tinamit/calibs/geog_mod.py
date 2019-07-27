from tqdm import tqdm

from tinamit.config import _
from tinamit.mod import OpsSimulGrupo
from .mod import CalibradorModSpotPy
from .valid import ValidadorMod, vars_datos_interés


class SimuladorGeog(object):
    """
    Simulador geográfico.
    """

    def __init__(símismo, mod):
        """

        Parameters
        ----------
        mod: Modelo
            El modelo para simular.
        """

        símismo.mod = mod

    def simular(símismo, t, vals_geog, vals_const=None, vars_interés=None, paralelo=False):
        """
        Efectua una simulación geográfica.

        Parameters
        ----------
        t: int or EspecTiempo
            El eje de tiempo para la simulación.
        vals_geog: dict
            Diccionario de cada lugar con sus valores de parámetros.
        vals_const: dict
            Valores de parámetros cuyos valores no cambian según el lugar.
        vars_interés: str or Variable or list
            Los variables cuyos resultados nos interesan.
        paralelo: bool
            Si se puede simular en paralelo.

        Returns
        -------
        ResultadosGrupo
        """
        vals_const = vals_const or {}

        ops = OpsSimulGrupo(
            t=t, extern=[dict(**vals_const, **vls_lg) for vls_lg in vals_geog.values()],
            vars_interés=vars_interés, nombre=list(vals_geog)
        )
        return símismo.mod.simular_grupo(ops_grupo=ops, paralelo=paralelo)


class CalibradorGeog(object):
    """
    Objeto para efectuar calibraciones geográficas.
    """

    def __init__(símismo, mod, calibrador=CalibradorModSpotPy):
        """

        Parameters
        ----------
        mod: Modelo
            El modelo para calibrar.
        calibrador: type
            Una subclase de :class:`~tinamit.calibs.mod.CalibradorMod`.
        """
        símismo.mod = mod
        símismo.calibrador = calibrador

    def calibrar(símismo, t, datos, líms_paráms, método='epm', n_iter=300, vars_obs=None, vals_geog=None,
                 vals_const=None):
        # Para hacer: acordarme de lo que quería hacer con ``vals_geog`` y ``vals_const``.
        vals_datos = datos.obt_vals()
        clbrd = símismo.calibrador(símismo.mod)

        calibs = {}
        for lg in datos.lugares:
            datos_lg = vals_datos.where(vals_datos[_('lugar')] == lg, drop=True)
            calibs[lg] = clbrd.calibrar(líms_paráms, datos=datos_lg, método=método, n_iter=n_iter, vars_obs=vars_obs)

        return calibs


class ValidadorGeog(object):
    """
    Objeto para correr validaciones de calibraciones geográficas.
    """

    def __init__(símismo, mod):
        """

        Parameters
        ----------
        mod: Modelo
            El modelo para validar.
        """
        símismo.mod = mod

    def validar(símismo, t, datos, paráms=None, funcs=None, vars_extern=None, corresp_vars=None):
        """
        Efectuar la validación.

        Parameters
        ----------
        t: int or EspecTiempo
            La especificación de tiempo para la validación.
        datos: BD
            La base de datos para la validación.
        paráms: dict
            Diccionario de los parámetros calibrados para cada lugar.
        funcs: list
            Funciones de validación para aplicar a los resultados.
        vars_extern: str or list or Variable
            Variable(s) exógenos cuyos valores se tomarán de la base de datos para alimentar la simulación y con
            los cuales por supuesto no se validará el modelo.
        corresp_vars:
            Diccionario de correspondencia entre nombres de valores en el modelo y en la base de datos.

        Returns
        -------
        dict
            Diccionario de la validación del modelo para cada variable con datos en cada lugar.
        """

        paráms = paráms or {}

        vars_interés = vars_datos_interés(símismo.mod, datos, corresp_vars=corresp_vars)

        vals_datos = datos.obt_vals(vars_interés)

        # Para hacer: utilizar `SimuladorGeog` para paralelizar y ahorar tiempo.
        valids = {}
        for lg in tqdm(datos.lugares):
            prms_lg = paráms[lg] if lg in paráms else {}
            datos_lg = vals_datos.where(vals_datos[_('lugar')] == lg, drop=True)

            if datos_lg.sizes['n']:
                valids[lg] = ValidadorMod(símismo.mod).validar(
                    t, datos=datos_lg, paráms=prms_lg, funcs=funcs, vars_extern=vars_extern, corresp_vars=corresp_vars
                )

        return valids
