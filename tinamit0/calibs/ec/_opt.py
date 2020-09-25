from warnings import warn as avisar

import numpy as np
from scipy.optimize import minimize

from tinamit.calibs._utils import eval_funcs
from tinamit.calibs.ec import CalibradorEc
from tinamit.config import _
from tinamit.geog.región import Lugar


class CalibradorEcOpt(CalibradorEc):
    """
    Calibrador de ecuaciones con algoritmo de optimización.
    """

    def __init__(símismo, ec, paráms, nombre=None, dialecto='tinamït'):

        super().__init__(ec, paráms, nombre=nombre, dialecto=dialecto)

        símismo.f_python = símismo.ec.a_python(paráms=símismo.paráms)

    def calibrar(símismo, bd, lugar=None, líms_paráms=None, ops=None, corresp_vars=None, ord_niveles=None):
        """
        Efectua una calibración para cada lugar en ``Lugar`` según los datos en ``bd``.

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

        ops = ops or {}

        líms_paráms = símismo._gen_líms_paráms(líms_paráms)

        # Leer los variables de la ecuación.
        vars_x, var_y = símismo._extraer_vars()

        # Todas las observaciones
        obs = símismo._obt_datos(bd, vars_interés=vars_x + [var_y], corresp_vars=corresp_vars)

        # Calibrar según la situación
        if lugar is None:
            # Si no hay lugares, optimizar de una vez con todas las observaciones.
            return _optimizar(símismo.f_python, líms_paráms=líms_paráms, obs_x=obs[vars_x], obs_y=obs[var_y], **ops)

        # Si hay lugares...

        # Una función recursiva para calibrar según la jerarquía
        def _calibrar_jerárchico_manual(lug, clbs):
            """
            Una función recursiva que permite calibrar en una jerarquía, tomando optimizaciones de niveles más
            altos si no consigue datos para niveles más bajos.

            Parameters
            ----------
            lug: Lugar
                El lugar en cual calibrar.
            clbs: dict
                El diccionario de los resultados de la calibración. (Parámetro recursivo.)
            """

            # Sino, tomar los datos de esta región únicamente.
            obs_lg = obs.where(obs['lugar'].isin([x.cód for x in lug.lugares()]), drop=True)

            # Intentar sacar información del nivel superior en la jerarquía

            if obs_lg.sizes['n']:

                def _buscar_inic_pariente(hj):
                    pariente = lugar.pariente(hj, ord_niveles=ord_niveles)  # El nivel inmediatamente superior
                    if pariente is None:
                        return
                    elif pariente.cód in clbs:
                        # Tomar la calibración superior como punto inicial para facilitar la búsqueda
                        return [clbs[pariente.cód][p]['cumbre'] for p in símismo.paráms]
                    else:
                        return _buscar_inic_pariente(pariente)

                inic = _buscar_inic_pariente(lug)

                resultados[lug.cód] = _optimizar(
                    símismo.f_python, líms_paráms=líms_paráms,
                    obs_x=obs_lg[vars_x], obs_y=obs_lg[var_y], inic=inic, **ops
                )
            for sub in lug.hijos_inmediatos(ord_niveles):
                _calibrar_jerárchico_manual(lug=sub, clbs=clbs)

        # Calibrar para cada lugar
        resultados = {}
        _calibrar_jerárchico_manual(lug=lugar, clbs=resultados)

        return resultados


def _optimizar(func, líms_paráms, obs_x, obs_y, inic=None, **ops):
    """
    Optimiza una función basándose en observaciones.

    Parameters
    ----------
    func: Callable
        La función para optimizar.
    líms_paráms: dict[str, tuple]
        Un diccionario de los parámetros y de sus límites.
    obs_x: pd.DataFrame
        Las observaciones de los variables x.
    obs_y: pd.Series | np.array
        Las observaciones correspondientes del variable y.
    inic: list | np.array
        Los valores iniciales para la optimización.
    ops: dict
        Opciones para pasar a la función de optimización.

    Returns
    -------
    dict
        Los parámetros optimizados.
    """

    # Leer el método de ajusto.
    try:
        med_ajusto = ops.pop('med_ajusto')
    except KeyError:
        med_ajusto = 'rcep'

    # La lista de parámetros de interés.
    paráms = list(líms_paráms)

    # Crear la función objetiva que minimizaremos (SciPy solamente puede minimizar).
    def f(prm):
        """
        Una función objetiva que SciPy puede minimizar.

        Parameters
        ----------
        prm: list | np.ndarray
            Los parámetros para calibrar

        Returns
        -------
        np.ndarray
            El ajusto del modelo con los parámetros actuales.

        """

        f_ajusto = eval_funcs[med_ajusto.lower()]

        # Devolver el ajusto de la función con los parámetros actuales.
        return -f_ajusto(func(prm, obs_x), obs_y, f=None)  # SpotPy maximiza pero nosotr@s aquí minimizamos

    # Generar los estimos iniciales, si necesario
    if inic is not None:
        # No es necesario
        x0 = inic
    else:
        # Sí es necesario
        x0 = []
        for p in paráms:
            # Para cada parámetro...
            lp = líms_paráms[p]  # Sus límites

            # Calcular un punto razonable para empezar la búsqueda
            if lp[0] is None:
                if lp[1] is None:
                    # El caso (-inf, +inf): empezaremos en 0
                    x0.append(0)
                else:
                    # El caso (-inf, R]: empezaremos en R
                    x0.append(lp[1])
            else:
                if lp[1] is None:
                    # El caso [R, +inf): empezaremos en R
                    x0.append(lp[0])
                else:
                    # El caso [R1, R2]: empezaremos en el promedio de R1 y R2
                    x0.append((lp[0] + lp[1]) / 2)

    # Convertir a matriz NumPy
    x0 = np.array(x0)

    # Optimizar
    opt = minimize(f, x0=x0, bounds=[líms_paráms[p] for p in paráms], **ops)

    # Avisar si la optimización no funcionó tan bien como lo esperamos.
    if not opt.success:
        avisar(_('Es posible que haya un error de optimización. Mejor le eches un vistazo a los resultados.'))

    # Devolver los resultados en el formato correcto.
    return {p: {'cumbre': opt.x[i]} for i, p in enumerate(paráms)}
