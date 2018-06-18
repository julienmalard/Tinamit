import re
from warnings import warn as avisar

import numpy as np
import scipy.stats as estad
import spotpy
from scipy.optimize import minimize
from scipy.stats import gaussian_kde

from tinamit import _
from tinamit.Análisis.sintaxis import Ecuación

try:
    import pymc3 as pm
except ImportError:
    pm = None

if pm is None:
    dists = None
else:
    dists = {'Beta': {'sp': estad.beta, 'pm': pm.Beta,
                      'sp_a_pm': lambda p: {'alpha': p[0], 'beta': p[1]},
                      'líms': (0, 1)},
             'Cauchy': {'sp': estad.cauchy, 'pm': pm.Cauchy,
                        'sp_a_pm': lambda p: {'alpha': p[0], 'beta': p[1]},
                        'líms': (None, None)},
             'Chi2': {'sp': estad.chi2, 'pm': pm.ChiSquared,
                      'sp_a_pm': lambda p: {'df': p[0]},
                      'líms': (0, None)},
             'Exponencial': {'sp': estad.expon, 'pm': pm.Exponential,
                             'sp_a_pm': lambda p: {'lam': 1 / p[1]},
                             'líms': (0, None)},
             'Gamma': {'sp': estad.gamma, 'pm': pm.Gamma,
                       'sp_a_pm': lambda p: {'alpha': p[0], 'beta': 1 / p[2]},
                       'líms': (0, None)},
             'Laplace': {'sp': estad.laplace, 'pm': pm.Laplace,
                         'sp_a_pm': lambda p: {'mu': p[0], 'b': p[1]},
                         'líms': (None, None)},
             'LogNormal': {'sp': estad.lognorm, 'pm': pm.Lognormal,
                           'sp_a_pm': lambda p: {'mu': p[1], 'sd': p[2]},
                           'líms': (0, None)},
             'MitadCauchy': {'sp': estad.halfcauchy, 'pm': pm.HalfCauchy,
                             'sp_a_pm': lambda p: {'beta': p[1]},
                             'líms': (0, None)},
             'MitadNormal': {'sp': estad.halfnorm, 'pm': pm.HalfNormal,
                             'sp_a_pm': lambda p: {'sd': p[1]},
                             'líms': (0, None)},
             'Normal': {'sp': estad.norm, 'pm': pm.Normal,
                        'sp_a_pm': lambda p: {'mu': p[0], 'sd': p[1]},
                        'líms': (None, None)},
             'T': {'sp': estad.t, 'pm': pm.StudentT,
                   'sp_a_pm': lambda p: {'nu': p[0], 'mu': p[1], 'sd': p[2]},
                   'líms': (None, None)},
             'Uniforme': {'sp': estad.uniform, 'pm': pm.Uniform,
                          'sp_a_pm': lambda p: {'lower': p[0], 'upper': p[0] + p[1]},
                          'líms': (0, 1)},
             'Weibull': {'sp': estad.weibull_min, 'pm': pm.Weibull,
                         'sp_a_pm': lambda p: {'alpha': p[0], 'beta': p[2]},
                         'líms': (0, None)},
             }


class CalibradorEc(object):
    """
    Un objeto para manejar la calibración de ecuaciones.
    """

    def __init__(símismo, ec, var_y=None, otras_ecs=None, nombres_equiv=None):
        """
        Inicializa el `Calibrador`.

        Parameters
        ----------
        ec: str
            La ecuación, en formato texto, para calibrar.
        var_y: str
            El nombre del variable y. Si no se especifica aquí, debe estar en la ecuación sí misma (por ejemplo,
            "y = a*x + b" en vez de simplemente "a*x + b").
        otras_ecs: dict[str, str]
            Un diccionario de otras ecuaciones para substituir variables en la ecuación principal.
        nombres_equiv: dict[str, str]
            Un diccionario de equivalencias de nombres.
        """

        # Crear la ecuación.
        símismo.ec = Ecuación(ec, nombre=var_y, otras_ecs=otras_ecs, nombres_equiv=nombres_equiv)

        # Asegurarse que se especificó el variable y.
        if símismo.ec.nombre is None:
            raise ValueError(_('Debes especificar el nombre del variable dependiente, o con el parámetro'
                               '`var_y`, o directamente en la ecuación, por ejemplo: "y = a*x ..."'))

    def calibrar(símismo, bd_datos, paráms=None, líms_paráms=None, método=None, binario=False, en=None,
                 escala=None, ops_método=None):
        """
        Calibra la ecuación, según datos, y, opcionalmente, una geografía espacial.

        Parameters
        ----------
        bd_datos: pd.DataFrame
            La base de datos. Los nombres de las columnas deben coincidir con los nombres de los variables en la
            ecuación.
        paráms: list[str]
            La lista de los parámetros para calibrar. Si es ``None``, se tomarán los variables que no
            están en `bd_datos`.
        líms_paráms: dict[str, tuple]
            Un diccionario con los límites teoréticos de los parámetros.
        método: {'optimizar', 'inferencia bayesiana'}
            El método para emplear para la calibración.
        binario: bool
            Si la ecuación es binaria o no.
        en: str | int
            El código del lugar donde quieres calibrar esta ecuación. Aplica únicamente si `bd_datos` está
            conectada a un objeto :class:`Geografía`.
        escala: str
            La escala geográfica a la cual quieres calibrar el modelo. Aplica únicamente si `bd_datos` está
            conectada a un objeto :class:`Geografía`.
        ops_método: dict
            Un diccionario de opciones adicionales a pasar directamente al algoritmo de calibración. Por ejemplo,
            puedes pasar argumentos para pymc3.Model.sample() aquí. También puedes especificar opciones
            específicas a Tinamït:
                - 'mod_jerárquico': bool. Determina si empleamos un modelo bayesiano jerárquico para la geografía.

        Returns
        -------
        dict
            La calibración completada.
        """

        # Asiñar diccionario vacío si `ops_método` no existe.
        if ops_método is None:
            ops_método = {}

        # Leer los variables de la ecuación.
        vars_ec = símismo.ec.variables()
        var_y = símismo.ec.nombre

        # Asegurarse que tenemos observaciones para el variable y.
        if var_y not in bd_datos.vars:
            raise ValueError(_('El variable "{}" no parece existir en la base de datos.').format(var_y))

        # Adivinar los parámetros si ne se especificaron.
        if paráms is None:
            # Todos los variables para cuales no tenemos observaciones.
            paráms = [x for x in vars_ec if x not in bd_datos.vars]

        # Los variables x, por definición, son los que no son parámetros.
        vars_x = [v for v in vars_ec if v not in paráms]

        # Generar los límites de parámetros, si necesario.
        if líms_paráms is None:
            líms_paráms = {}

        líms_paráms_final = {}
        for p in paráms:
            # Para cada parámetro...
            if p not in líms_paráms or líms_paráms[p] is None:
                # Aplicar y formatear límites para parámetros sin límites
                líms_paráms_final[p] = (None, None)
            else:
                # Pasar los límites que sí se especificaron.
                if len(líms_paráms[p]) == 2:
                    líms_paráms_final[p] = líms_paráms[p]
                else:
                    # Límites deben se tuplas con únicamente 2 elementos.
                    raise ValueError(
                        _('Límite "{}" inválido. Los límites de parámetros deben tener dos elementos: '
                          '(mínimo, máximo). Utilizar ``None`` para ± infinidad: (None, 10); (0, None).'
                          ).format(líms_paráms[p])
                    )

        # Aplicar el método automáticamente, si necesario.
        if método is None:
            if pm is not None:
                método = 'inferencia bayesiana'
            else:
                método = 'optimizar'
        else:
            método = método.lower()

        # Para calibración bayesiana, emplear modelos jerárquicos si no se especificó el contrario.
        if método == 'inferencia bayesiana':
            if 'mod_jerárquico' not in ops_método or ops_método['mod_jerárquico'] is None:
                ops_método['mod_jerárquico'] = True
            mod_jerárquico = ops_método.pop('mod_jerárquico')
        else:
            mod_jerárquico = False

        # Intentar obtener información geográfica, si posible.
        try:
            lugares = bd_datos.geog_obt_lugares_en(en, escala=escala)
            jerarquía = bd_datos.geog_obt_jerarquía(en, escala=escala)
        except ValueError:
            lugares = jerarquía = None

        # Ahora, por fin hacer la calibración.
        if método == 'inferencia bayesiana':
            return símismo._calibrar_bayesiana(
                ec=símismo.ec, var_y=var_y, vars_x=vars_x, líms_paráms=líms_paráms_final, binario=binario,
                ops_método=ops_método, bd_datos=bd_datos, lugares=lugares, jerarquía=jerarquía,
                mod_jerárquico=mod_jerárquico
            )
        elif método == 'optimizar':
            return símismo._calibrar_optim(
                ec=símismo.ec, var_y=var_y, vars_x=vars_x, líms_paráms=líms_paráms_final,
                ops_método=ops_método, bd_datos=bd_datos, lugares=lugares, jerarquía=jerarquía
            )
        else:
            raise ValueError(_('Método de calibración "{}" no reconocido.').format(método))

    @staticmethod
    def _calibrar_bayesiana(ec, var_y, vars_x, líms_paráms, binario, bd_datos, lugares, jerarquía,
                            mod_jerárquico, ops_método):
        """
        Efectua la calibración bayesiana.

        Parameters
        ----------
        ec: Ecuación
            La ecuación para calibrar.
        var_y: str
            El nombre del variable y.
        vars_x: list[str]
            Los nombres de los variables x.
        líms_paráms: dict[str, tuple]
            El diccionario con límites de parámetros.
        binario: bool
            Si el modelo es binario o no.
        bd_datos: pd.DataFrame
            La base de datos observados.
        lugares: list
            La lista de lugares en los cuales calibrar.
        jerarquía: dict
            La jerarquía de los lugares.
        mod_jerárquico: bool
            Si implementamos un único modelo jerárquico o no.
        ops_método: dict
            Opciones adicionales a pasar a la función de calibración bayesiana de PyMC3.

        Returns
        -------
        dict
            La calibración de los parámetros.

        """

        # Si no tenemos PyMC3, no podemos hacer inferencia bayesiana.
        if pm is None:
            raise ImportError(_('Debes instalar PyMC3 para poder hacer calibraciones con inferencia bayesiana.'))

        # Generar los datos
        paráms = list(líms_paráms)
        l_vars = vars_x + [var_y]
        obs = bd_datos.obt_datos(l_vars=l_vars, excl_faltan=True)

        # Calibrar según la situación
        if lugares is None:
            # Si no hay lugares, generar y calibrar el modelo de una vez.
            mod_bayes = ec.gen_mod_bayes(
                líms_paráms=líms_paráms, obs_x=obs[vars_x], obs_y=obs[var_y],
                binario=binario, aprioris=None, nv_jerarquía=None
            )

            resultados = _calibrar_mod_bayes(mod_bayes, paráms=paráms, ops=ops_método)

        else:
            # Si hay distribución geográfica, es un poco más complicado.
            if mod_jerárquico:
                # Si estamos implementando un modelo jerárquico...

                # Primero, crear una lista de las relaciones jerárquicas, el cual se necesita para crear el modelo
                # jerárquico bayes.

                def _gen_nv_jerarquía(jrq, egr=None, nv_ant=None):
                    """

                    Parameters
                    ----------
                    jrq: dict
                        La jerarquía.
                    egr: list
                        Parámetro para la recursión.
                    nv_ant: list
                        Un lista de los nombres del nivel superior en la jerarquía. Parámetro de recursión.

                    Returns
                    -------
                    list:
                    """

                    # Empezar con el primer nivel
                    if nv_ant is None:
                        nv_ant = [None]

                    # Empezar con egresos vacíos
                    if egr is None:
                        egr = []

                    nv_act = [x for x in jrq if jrq[x] in nv_ant]

                    if len(nv_act):
                        nv_act += [x for x in nv_ant if x in lugares and x not in nv_act]

                        # Agregar a los egresos
                        egr.append(nv_act)

                        # Recursarr en los niveles inferiores
                        _gen_nv_jerarquía(jrq, egr=egr, nv_ant=nv_act)

                    # Devolver el resultado
                    return egr

                # Generar la lista de relaciones jerárquicas
                nv_jerarquía = _gen_nv_jerarquía(jerarquía)

                nv_jerarquía.insert(0, [None])

                for í, nv in list(enumerate(nv_jerarquía))[::-1]:

                    if í == (len(nv_jerarquía) - 1):

                        nv[:] = [x for x in nv if len(obs[obs['lugar'].isin(bd_datos.geog.obt_lugares_en(x) + [x])])]
                    else:

                        nv[:] = [x for x in nv if x in [jerarquía[y] for y in nv_jerarquía[í + 1]]]

                í_nv_jerarquía = [np.array([nv_jerarquía[í - 1].index(jerarquía[x]) for x in y])
                                  for í, y in list(enumerate(nv_jerarquía))[:0:-1]]
                í_nv_jerarquía.insert(0, np.array([nv_jerarquía[-1].index(x) for x in obs['lugar']]))

                # Generar el modelo bayes
                mod_bayes_jrq = ec.gen_mod_bayes(
                    líms_paráms=líms_paráms, obs_x=obs[vars_x], obs_y=obs[var_y],
                    aprioris=None, binario=binario, nv_jerarquía=í_nv_jerarquía[::-1]
                )
                var_res_lugares = {}
                for lg in lugares:
                    if lg in nv_jerarquía[-1]:
                        var_res_lugares[lg] = nv_jerarquía[-1].index(lg)
                    else:
                        for í, nv in enumerate(nv_jerarquía[1::-1]):
                            id_nv = lg
                            while id_nv is not None:
                                id_nv = jerarquía[id_nv]
                                if id_nv in nv:
                                    var_res_lugares[lg] = (í + 1, nv.index(id_nv))
                                    break
                            if lg in var_res_lugares:
                                break

                prms_extras = list({
                    'mu_{p}_nv_{í}'.format(p=p, í=x[0]) for x in set(var_res_lugares.values()) if isinstance(x, tuple)
                    for p in paráms
                })

                # Calibrar
                res_calib = _calibrar_mod_bayes(mod_bayes_jrq, paráms=paráms + prms_extras, ops=ops_método)

                # Formatear los resultados
                resultados = {}
                for lg in lugares:
                    ubic_res = var_res_lugares[lg]

                    if isinstance(ubic_res, int):
                        resultados[lg] = {p: {ll: v[..., ubic_res] for ll, v in res_calib[p].items()} for p in paráms}
                    else:
                        nv, í = ubic_res
                        resultados[lg] = {
                            p: {ll: v[..., í] for ll, v in res_calib['mu_{}_nv_{}'.format(p, nv)].items()}
                            for p in paráms
                        }

            else:
                # Si no estamos haciendo un único modelo jerárquico, hay que calibrar cada lugar individualmente.

                # Efectuar las calibraciones para todos los lugares.
                resultados = {}
                for lg in lugares:
                    lgs_potenciales = bd_datos.geog.obt_todos_lugares_en(lg)
                    obs_lg = obs[obs['lugar'].isin(lgs_potenciales + [lg])]
                    if len(obs_lg):
                        mod_bayes = ec.gen_mod_bayes(
                            líms_paráms=líms_paráms, obs_x=obs_lg[vars_x], obs_y=obs_lg[var_y],
                            binario=binario, aprioris=None, nv_jerarquía=None
                        )
                        resultados[lg] = _calibrar_mod_bayes(
                            mod_bayes=mod_bayes, paráms=paráms, ops=ops_método, obs=obs_lg
                        )
                    else:
                        resultados[lg] = None

        # Devolver únicamente los lugares de interés (y no lugares de más arriba en la jerarquía).
        if lugares is not None:
            return {ll: v for ll, v in resultados.items() if ll in lugares}
        else:
            return resultados

    @staticmethod
    def _calibrar_optim(ec, var_y, vars_x, líms_paráms, bd_datos, lugares, jerarquía, ops_método):
        """
        Calibra la ecuación con un método de optimización.

        Parameters
        ----------
        ec : Ecuación
            La ecuación para calibrar.
        var_y : str
            El variable y.
        vars_x : list[str]
            Los variables x.
        líms_paráms : dict[str, tuple]
            El diccionario de los límites de los parámetros.
        bd_datos : SuperBD
            La base de datos.
        lugares : list[str]
            La lista de lugares de interés.
        jerarquía : dict
            La jerarquía de los lugares.
        ops_método : dict
            Opciones para la optimización.

        Returns
        -------
        dict:
            Los parámetros calibrados.
        """

        # Generar la función dinámica Python
        paráms = list(líms_paráms)
        f_python = ec.gen_func_python(paráms=paráms)

        # Todos los variables
        l_vars = vars_x + [var_y]

        # Todas las observaciones
        obs = bd_datos.obt_datos(l_vars=l_vars, excl_faltan=True)

        # Calibrar según la situación
        if lugares is None:
            # Si no hay lugares, optimizar de una vez con todas las observaciones.
            resultados = _optimizar(f_python, líms_paráms=líms_paráms, obs_x=obs[vars_x], obs_y=obs[var_y],
                                    **ops_método)
        else:
            # Si hay lugares...

            # Una función recursiva para calibrar según la jerarquía
            def _calibrar_jerárchico_manual(lugar, jrq, clbs=None):
                """
                Una función recursiva que permite calibrar en una jerarquía, tomando optimizaciones de niveles más
                altos si no consigue datos para niveles más bajos.

                Parameters
                ----------
                lugar: str
                    El lugar en cual calibrar.
                jrq: dict
                    La jerarquía.
                clbs: dict
                    El diccionario de los resultados de la calibración. (Parámetro recursivo.)

                """

                # Para la recursión
                if clbs is None:
                    clbs = {}

                if lugar is None:
                    # Si estamos al nivel más alto de la jerarquía, tomar todos los datos.
                    obs_lg = obs
                    inic = pariente = None  # Y no tenemos ni estimos iniciales, ni región pariente
                else:
                    # Sino, tomar los datos de esta región únicamente.
                    lgs_potenciales = bd_datos.geog.obt_todos_lugares_en(lugar)
                    obs_lg = obs[obs['lugar'].isin(lgs_potenciales + [lugar])]

                    # Intentar sacar información del nivel superior en la jerarquía
                    try:
                        pariente = jrq[lugar]  # El nivel inmediatemente superior

                        # Calibrar recursivamente si necesario
                        if pariente not in clbs:
                            _calibrar_jerárchico_manual(lugar=pariente, jrq=jrq, clbs=clbs)

                        # Tomar la calibración superior como punto inicial para facilitar la búsqueda
                        inic = [clbs[pariente][p]['val'] for p in paráms]

                    except KeyError:
                        # Error improbable con la jerarquía.
                        avisar(_('No encontramos datos para el lugar "{}", ni siguiera en su jerarquía, y por eso'
                                 'no pudimos calibrarlo.').format(lugar))
                        resultados[lugar] = {}  # Calibración vacía
                        return  # Si hubo error en la jerarquía, no hay nada más que hacer para este lugar.

                # Ahora, calibrar.
                if len(obs_lg):
                    # Si tenemos observaciones, calibrar con esto.
                    resultados[lugar] = _optimizar(
                        f_python, líms_paráms=líms_paráms,
                        obs_x=obs_lg[vars_x], obs_y=obs_lg[var_y], inic=inic, **ops_método
                    )
                else:
                    # Si no tenemos observaciones, copiar la calibración del pariente
                    resultados[lugar] = clbs[pariente]

            # Calibrar para cada lugar
            resultados = {}
            for lg in lugares:
                _calibrar_jerárchico_manual(lugar=lg, jrq=jerarquía, clbs=resultados)

        # Devolver únicamente los lugares de interés.
        if lugares is not None:
            return {ll: v for ll, v in resultados.items() if ll in lugares}
        else:
            return resultados


class CalibradorMod(object):
    def __init__(símismo, mod):
        """

        Parameters
        ----------
        mod : Modelo.Modelo
        """
        símismo.mod = mod

    def calibrar(símismo, paráms, método, líms_paráms=None):

        método = método.lower()
        mod = símismo.mod

        if líms_paráms is None:
            líms_paráms = {}
        for p in paráms:
            if p not in líms_paráms:
                líms_paráms[p] = símismo.mod.obt_lims_var(p)
        líms_paráms = {ll: v for ll, v in líms_paráms.items() if ll in paráms}

        obs = símismo.mod.datos
        t_final = len(obs) - 1  # 1 paso menos por las condiciones iniciales
        mu_obs = obs.mean().values
        sg_obs = obs.std().values
        if método == 'optimizar':
            def f(prm, obs_x):
                mod.inic_vals_vars({p: v for p, v in zip(paráms, prm)})
                res = mod.simular(tiempo_final=t_final, vars_interés=list(obs)).values
                return ((res - mu_obs) / sg_obs).ravel()

            obs_y = ((obs.values - mu_obs) / sg_obs).ravel()
            return _optimizar(func=f, líms_paráms=líms_paráms, obs_x=None, obs_y=obs_y)
        elif método in _algs_spotpy:
            mod_spotpy = ModSpotPy(mod=mod, líms_paráms=líms_paráms, obs=obs)
            muestreador = _algs_spotpy[método](mod_spotpy, dbname='CalibTinamït', dbformat='csv')
            muestreador.sample(100)
            trzs = spotpy.analyser.load_csv_results('CalibTinamït')
            res = {p: trzs[[c for c in trzs.dtype.names if c.startswith('par')][í]] for í, p in enumerate(líms_paráms)}
            sim = {p: trzs[[c for c in trzs.dtype.names if c.startswith('sim')]] for í, p in enumerate(líms_paráms)}
            return res
            """
            n_obs = len(list(obs))
            cols_sim = [c for c in trzs.dtype.names if c.startswith('sim')]
            # for í_o in range(n_obs):
            í_o = 1
            
            dib.clf()
            rango_prob = (trzs['like1'].min(), trzs['like1'].max())
            n_it = 100
            for it in range(n_it):
                x = [trzs[c][í] for í in range(len(trzs)) for c in cols_sim][í_o::n_obs][len(obs) * it:len(obs) * (it + 1)]
                í_color = (trzs['like1'][it] - rango_prob[0]) / (rango_prob[1] - rango_prob[0])
                print(í_color)
                dib.plot(x, linewidth=0.5, color=dib.cm.RdYlBu(í_color))
            dib.plot(mod_spotpy.evaluation()[í_o::n_obs], color='green', linewidth=3)
            """
        else:
            raise ValueError


# Unas funciones auxiliares
def _calibrar_mod_bayes(mod_bayes, paráms, obs=None, vars_compartidos=None, ops=None):
    """
    Esta función calibra un modelo bayes.

    Parameters
    ----------
    mod_bayes: pm.Modelo
        El modelo para calibrar.
    paráms: list[str]
        Una lista de los nombres de los parámetros de interés para sacar de la traza del modelo.
    obs: dict
        Base de datos observados.
    vars_compartidos: dict
        Un diccionario con los variables compartidos Theano en los cuales podemos poner nuevas observaciones.
    ops: dict
        Opciones adicionales para pasar a pm.Modelo.sample.

    Returns
    -------

    """

    # El diccionario de opciones adicionales.
    if ops is None:
        ops = {}

    # Si hay variables de datos compartidos, poner los nuevos datos.
    if vars_compartidos is not None:
        for var, var_pymc in vars_compartidos.items():
            var_pymc.set_value(obs[var])

    # Crear el diccionarion de argumentos
    ops_auto = {
        'tune': 1000,
        'cores': 1
    }
    ops_auto.update(ops)

    # Efectuar la calibración
    with mod_bayes:
        t = pm.sample(**ops_auto)

    # Devolver los datos procesados
    return _procesar_calib_bayes(t, paráms=paráms)


def _procesar_calib_bayes(traza, paráms):
    """
    Procesa los resultados de una calibración bayes. Con base en la traza PyMC3, calcula el punto de probabilidad más
    alta para cada parámetro de interés.

    Parameters
    ----------
    traza: pm.Trace
        La traza PyMC3.
    paráms: list
        La lista de parámetros de interés.

    Returns
    -------
    dict
        Los resultados procesados.
    """

    # El diccionario para los resultados
    d_máx = {}

    def procesar_trz(trz):
        # Ajustar el rango, si es muy grande (necesario para las funciones que siguen)
        escl = np.max(trz)
        rango = escl - np.min(trz)
        if escl < 10e10:
            escl = 1  # Si no es muy grande, no hay necesidad de ajustar

        # Intentar calcular la densidad máxima.
        try:
            # Se me olvidó cómo funciona esta parte.
            fdp = gaussian_kde(trz / escl)
            x = np.linspace(trz.min() / escl - 1 * rango, trz.max() / escl + 1 * rango, 1000)
            máx = x[np.argmax(fdp.evaluate(x))] * escl
            return máx

        except BaseException:
            return np.nan

    # Calcular el punto de probabilidad máxima
    for p in paráms:
        # Para cada parámetro...

        dims = traza[p].shape
        if len(dims) == 1:
            d_máx[p] = procesar_trz(traza[p])
        elif len(dims) == 2:
            d_máx[p] = np.empty(dims[1])
            for e in range(dims[1]):
                d_máx[p][e] = procesar_trz(traza[p][:, e])
        else:
            raise ValueError

    # Devolver los resultados procesados.
    return {p: {'val': d_máx[p], 'dist': traza[p]} for p in paráms}


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
        med_ajusto = 'rmec'

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

        # Definir la función de ajusto.
        if med_ajusto.lower() == 'rmec':
            # Raíz media del error cuadrado
            def f_ajusto(y, y_o):
                return np.sqrt(np.sum(np.square(y - y_o)) / len(y))

        else:
            # Implementar otras medidas de ajusto aquí.
            raise ValueError(_('La medida de ajusto "{}" no se reconoció.').format(med_ajusto))

        # Devolver el ajusto de la función con los parámetros actuales.
        return f_ajusto(func(prm, obs_x), obs_y)

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
    return {p: {'val': opt.x[i]} for i, p in enumerate(paráms)}


_algs_spotpy = {
    'fast': spotpy.algorithms.fast,
    'dream': spotpy.algorithms.dream,
    'mc': spotpy.algorithms.mc,
    'mcmc': spotpy.algorithms.mcmc,
    'mle': spotpy.algorithms.mle,
    'lhs': spotpy.algorithms.lhs,
    'sa': spotpy.algorithms.sa,
    'sceua': spotpy.algorithms.sceua,
    'rope': spotpy.algorithms.rope,
    'abc': spotpy.algorithms.abc,
    'fscabc': spotpy.algorithms.fscabc,

}


class ModSpotPy(object):
    def __init__(símismo, mod, líms_paráms, obs):
        """

        Parameters
        ----------
        mod : Modelo.Modelo
        líms_paráms : dict
        obs: pd.DataFrame
        """

        símismo.paráms = [
            spotpy.parameter.Uniform(re.sub('\W|^(?=\d)', '_', p), low=d[0], high=d[1], optguess=(d[0] + d[1]) / 2)
            for p, d in líms_paráms.items()
        ]
        símismo.nombres_paráms = list(líms_paráms)
        símismo.mod = mod
        símismo.mu_obs = obs.mean().values
        símismo.sg_obs = obs.std().values
        símismo.obs_norm = ((obs.values - símismo.mu_obs) / símismo.sg_obs).ravel()
        símismo.vars_interés = list(obs)
        símismo.t_final = len(obs) - 1

    def parameters(símismo):
        return spotpy.parameter.generate(símismo.paráms)

    def simulation(símismo, x):
        símismo.mod.inic_vals_vars({ll: x_i for ll, x_i in zip(símismo.nombres_paráms, x)})
        res = símismo.mod.simular(tiempo_final=símismo.t_final, vars_interés=list(símismo.vars_interés)).values

        return ((res - símismo.mu_obs) / símismo.sg_obs).ravel()

    def evaluation(símismo):
        return símismo.obs_norm

    def objectivefunction(símismo, simulation, evaluation, params=None):
        # like = spotpy.likelihoods.gaussianLikelihoodMeasErrorOut(evaluation,simulation)
        like = spotpy.objectivefunctions.nashsutcliffe(evaluation, simulation)

        return like
