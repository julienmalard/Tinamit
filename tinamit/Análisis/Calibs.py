from warnings import warn as avisar

import numpy as np
import scipy.stats as estad
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


class Calibrador(object):
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
    def _calibrar_bayesiana(ec, var_y, vars_x, líms_paráms, binario,
                            bd_datos, lugares, jerarquía, mod_jerárquico, ops_método):
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

        if pm is None:
            raise ImportError(_('Debes instalar PyMC3 para poder hacer calibraciones con inferencia bayesiana.'))

        # Generar los datos
        paráms = list(líms_paráms)
        l_vars = vars_x + [var_y]
        obs = bd_datos.obt_datos(l_vars=l_vars, excl_faltan=True)

        # Generar un modelo bayesiano de base,
        mod_bayes = ec.gen_mod_bayes(
            líms_paráms=líms_paráms, obs=obs, vars_x=vars_x, var_y=var_y,
            binario=binario, aprioris=None, mod_jerárquico=mod_jerárquico
        )

        # Calibrar según la situación
        if lugares is None:
            # Si no hay lugares, calibrar el modelo de una vez.
            resultados = _calibrar_mod_bayes(mod_bayes, paráms=paráms, ops=ops_método)

        else:
            # Si hay distribución geográfica, es un poco más complicado.
            if mod_jerárquico:
                # Si estamos implementando un modelo jerárquico...
                mod_bayes_jrq = ec.gen_mod_bayes(jerarquía=True)
                resultados = _calibrar_mod_bayes(mod_bayes_jrq, paráms=paráms, ops=ops_método)

            else:
                # Si no estamos haciendo un único modelo jerárquico, hay que emularlo manualmente.

                def _calibrar_jerárquíco_manual(lugar, jrq, clbs=None):
                    """
                    Una función recursiva para emular un modelo jerárquico.

                    Parameters
                    ----------
                    lugar: list
                        La lista de lugares.
                    jrq: dict
                        La jerarquía de los lugares.
                    clbs: dict
                        Las calibraciones efectuadas.
                        función.

                    Returns
                    -------
                    dict
                        Las calibraciones.
                    """

                    if clbs is None:
                        clbs = {None: {'mod': mod_bayes}}  # Empezar con el modelo original

                    if lugar is None:
                        # Si estamos al cumbre de la jerarquía...

                        obs_lg = obs  # Tomar todos los datos
                        pariente = None  # No tenemos pariente
                        mod_lg = clbs[None]['mod']  # Empezar con el mismo modelo de base

                    else:
                        # Sino, hay un nivel superior en la jerarquía

                        # Obtener los datos correspondiendo a este nivel
                        lgs_potenciales = bd_datos.geog.obt_lugares_en(lugar)
                        obs_lg = obs[obs['lugar'].isin(lgs_potenciales + [lugar])]

                        # Intentar obtener la calibración del nivel superior.
                        try:
                            pariente = jrq[lugar]  # El nivel superior (pariente)

                            # Si todavía no se calibró éste, calibrarlo de manera recursiva.
                            if pariente not in clbs:
                                # Calibrar el pariente
                                _calibrar_jerárquíco_manual(lugar=pariente, jrq=jrq, clbs=clbs)

                                # Generar a prioris de la calibración
                                aprs = _gen_a_prioris(líms=líms_paráms, dic_clbs=clbs[pariente])

                                # Generar un nuevo modelo Bayes con los nuevos a prioris y guardarlo
                                clbs[pariente]['mod'] = ec.gen_mod_bayes(
                                    líms_paráms=líms_paráms, obs_x=obs[vars_x], obs_y=obs[var_y], binario=binario,
                                    aprioris=aprs
                                )

                            # Emplear el modelo pariente como base para la calibración
                            mod_lg = clbs[pariente]['mod']

                        except KeyError:
                            # Si no existe, hay error.
                            raise ValueError(
                                _('El lugar "{}" no está bien inscrito en la jerarquía general.')
                                    .format(lugar)
                            )

                    if len(obs_lg):
                        # Si tenemos datos con los cuales calibrar, hacerlo ahora
                        clbs[lugar] = _calibrar_mod_bayes(
                            mod_bayes=mod_lg, obs_x=obs[vars_x], obs_y=obs[var_y], paráms=paráms, ops=ops_método
                        )

                    else:
                        # Si no hay datos con los cuales calibrar, copiar el diccionario del pariente.
                        clbs[lugar] = clbs[pariente]

                    # Devolver la calibración
                    return clbs

                # Efectuar las calibraciones para todos los lugares.
                dic_calibs = {None: {'mod': mod_bayes}}
                for lg in lugares:
                    _calibrar_jerárquíco_manual(lugar=lg, jrq=jerarquía, clbs=dic_calibs)

                # Quitar los modelos de los resultados
                resultados = {lg: {ll: v for ll, v in d.items() if ll != 'mod'} for lg, d in dic_calibs.items()}

        # Devolver únicamente los lugares de interés (y no lugares de más arriba en la jerarquía).
        return {ll: v for ll, v in resultados.items() if ll in lugares}

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

        if lugares is None:
            # Si no hay lugares, optimizar de una vez con todas las observaciones.
            resultados = _optimizar(f_python, paráms=paráms, líms_paráms=líms_paráms,
                                    obs_x=obs[vars_x], obs_y=obs[var_y], **ops_método)
        else:
            # Si hay lugares...

            def _calibrar_jerárchico_manual(lugar, jrq, clbs=None):
                if clbs is None:
                    clbs = {}

                if lugar is None:
                    obs_lg = obs
                else:
                    lgs_potenciales = bd_datos.geog.obt_lugares_en(lugar)
                    obs_lg = obs[obs['lugar'].isin(lgs_potenciales + [lugar])]
                if len(obs_lg):
                    resultados[lugar] = _optimizar(
                        f_python, paráms=paráms, líms_paráms=líms_paráms,
                        obs_x=obs_lg[vars_x], obs_y=obs_lg[var_y], **ops_método
                    )
                else:
                    try:
                        pariente = jrq[lugar]
                        if pariente not in clbs:
                            _calibrar_jerárchico_manual(lugar=pariente, jrq=jrq, clbs=clbs)
                        resultados[lugar] = clbs[pariente]

                    except KeyError:
                        avisar(_('No encontramos datos para el lugar "{}", ni siguiera en su jerarquía, y por eso'
                                 'no pudimos calibrarlo.').format(lugar))
                        resultados[lugar] = {}

            resultados = {}
            for lg in lugares:
                _calibrar_jerárchico_manual(lugar=lg, jrq=jerarquía, clbs=resultados)
        if lugares is not None:
            return {ll: v for ll, v in resultados.items() if ll in lugares}
        else:
            return resultados


def _gen_a_prioris(líms, dic_clbs):
    aprioris = {}
    for p, dic in dic_clbs.items():
        lp = líms[p]

        ajust_sp = _ajust_dist(datos=dic['dist'], líms=lp)
        nombre = ajust_sp['tipo']
        dist_pm = dists[nombre]['pm']

        prms_sp = ajust_sp['prms']
        prms_pm = dists[nombre]['sp_a_pm'](prms_sp)

        aprioris[p] = (dist_pm, prms_pm)

    return aprioris


def _calibrar_mod_bayes(mod_bayes, vars_compartidos, obs, paráms, ops):

    for var, var_pymc in vars_compartidos:
        var_pymc.set_value(obs[var])

    ops_auto = {
        'tune': 1000,
        'cores': 1
    }
    ops_auto.update(ops)

    with mod_bayes:

        t = pm.sample(**ops_auto)

    return _procesar_calib_bayes(t, paráms=paráms)


def _procesar_calib_bayes(traza, paráms):
    d_máx = {}
    for p in paráms:
        escl = np.max(traza[p])
        rango = escl - np.min(traza[p])
        if escl < 10e10:
            escl = 1
        try:
            fdp = gaussian_kde(traza[p] / escl)
            x = np.linspace(traza[p].min() / escl - 1 * rango, traza[p].max() / escl + 1 * rango, 1000)
            máx = x[np.argmax(fdp.evaluate(x))] * escl
            d_máx[p] = máx
        except BaseException:
            d_máx[p] = None

    return {p: {'val': d_máx[p], 'dist': traza[p]} for p in paráms}


def _optimizar(func, paráms, líms_paráms, obs_x, obs_y, **ops):
    try:
        med_ajuste = ops['med_ajuste']
    except KeyError:
        med_ajuste = 'rmec'

    def f(prm):

        if med_ajuste.lower() == 'rmec':
            def f_ajuste(y, y_o):
                return np.sqrt(np.sum(np.square(y - y_o)) / len(y))
        else:
            raise ValueError('')

        return f_ajuste(func(prm, obs_x), obs_y)

    x0 = []
    for p in paráms:
        lp = líms_paráms[p]
        if lp[0] is None:
            if lp[1] is None:
                x0.append(0)
            else:
                x0.append(lp[1])
        else:
            if lp[1] is None:
                x0.append(lp[0])
            else:
                x0.append((lp[0] + lp[1]) / 2)

    x0 = np.array(x0)
    opt = minimize(f, x0=x0, bounds=[líms_paráms[p] for p in paráms], **ops)

    if not opt.success:
        avisar(_('Error de optimización para ecuación "{}".').format(str(func)))

    return {p: {'val': opt.x[i]} for i, p in enumerate(paráms)}


def _ajust_dist(datos, líms):
    mejor_ajuste = {'p': 0, 'tipo': None}

    dists_potenciales = {ll: v['sp'] for ll, v in dists.items() if _líms_compat(líms, v['líms'])}

    for nombre_dist, dist_sp in dists_potenciales.items():

        if nombre_dist == 'Beta':
            restric = {'floc': líms[0], 'fscale': líms[1] - líms[0]}
        elif nombre_dist == 'Cauchy':
            restric = {}
        elif nombre_dist == 'Chi2':
            restric = {'floc': líms[0], 'fscale': líms[1] - líms[0]}
        elif nombre_dist == 'Exponencial':
            restric = {'floc': líms[0]}
        elif nombre_dist == 'Gamma':
            restric = {'floc': líms[0]}
        elif nombre_dist == 'Laplace':
            restric = {}
        elif nombre_dist == 'LogNormal':
            restric = {'fs': 1}
        elif nombre_dist == 'MitadCauchy':
            restric = {'floc': líms[0]}
        elif nombre_dist == 'MitadNormal':
            restric = {'floc': líms[0]}
        elif nombre_dist == 'Normal':
            restric = {}
        elif nombre_dist == 'T':
            restric = {}
        elif nombre_dist == 'Uniforme':
            restric = {}
        elif nombre_dist == 'Weibull':
            restric = {'floc': líms[0]}
        else:
            raise ValueError

        try:
            tupla_prms = dist_sp.fit(datos, **restric)
        except:
            tupla_prms = None

        if tupla_prms is not None:
            # Medir el ajuste de la distribución
            p = estad.kstest(rvs=datos, cdf=dist_sp(*tupla_prms).cdf)[1]

            # Si el ajuste es mejor que el mejor ajuste anterior...
            if p > mejor_ajuste['p'] or mejor_ajuste['tipo'] is None:
                # Guardarlo
                mejor_ajuste['p'] = p
                mejor_ajuste['prms'] = tupla_prms
                mejor_ajuste['tipo'] = nombre_dist

    # Si no logramos un buen aujste, avisar al usuario.
    if mejor_ajuste['p'] <= 0.10:
        avisar('El ajuste de la mejor distribución quedó muy mal (p = {}).'.format(round(mejor_ajuste['p'], 4)))

    # Devolver la distribución con el mejor ajuste, tanto como el valor de su ajuste.
    return mejor_ajuste


def _líms_compat(l_1, l_2):
    l_1 = [None if x is None or np.isinf(x) else 0 for x in l_1]
    l_2 = [None if x is None or np.isinf(x) else 0 for x in l_2]

    return l_1 == l_2
