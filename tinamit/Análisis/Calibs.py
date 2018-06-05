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
                ops_método['mod_jerárquico'] = False
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
                binario=binario, aprioris=None, vars_compart=False, nv_jerarquía=None
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
                    Genera una lista de relaciones jerárquicas para el modelo bayes. Cada elemento en la lista es
                    una lista de índices de cada región en el nivel superior de la jerarquía. El último elemento
                    de la lista representa los índices de las observaciones.

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
                    list[np.ndarray]
                        Los índices de cada región, en orden de niveles jerárquicos.
                    """

                    # Empezar con el primer nivel
                    if nv_ant is None:
                        nv_ant = [None]

                    # Empezar con egresos vacíos
                    if egr is None:
                        egr = []

                    # Calcular el índice de cada lugar, en orden alfabético, en el nivel inmediatamente superior en la
                    # jerarquía.
                    nv_act = [x for x in sorted(jrq) if jrq[x] in nv_ant]

                    # Agregar a los egresos
                    if len(nv_act):
                        # Si no es el último nivel de la jerarquía, agregar éste
                        egr.append(np.array([nv_ant.index(jrq[x]) for x in nv_act]))

                        # Recursarr en los niveles inferiores
                        _gen_nv_jerarquía(jrq, egr=egr, nv_ant=nv_act)

                    else:
                        # Si era el último nivel, agregar los ínices de las observaciones
                        egr.append(np.array([nv_ant.index(x) for x in obs['lugar']]))

                    # Devolver el resultado
                    return egr

                # Generar la lista de relaciones jerárquicas
                nv_jerarquía = _gen_nv_jerarquía(jerarquía)

                # Generar el modelo bayes
                mod_bayes_jrq = ec.gen_mod_bayes(
                    líms_paráms=líms_paráms, obs_x=obs[vars_x], obs_y=obs[var_y],
                    aprioris=None, binario=binario, vars_compart=False, nv_jerarquía=nv_jerarquía
                )

                # Calibrar
                res_calib = _calibrar_mod_bayes(mod_bayes_jrq, paráms=paráms, ops=ops_método)

                # Formatear los resultados
                resultados = {}
                for p in paráms:
                    resultados[p] = {lg: res_calib[p][í] for í, lg in enumerate(lugares)}

            else:
                # Si no estamos haciendo un único modelo jerárquico, hay que emularlo manualmente.

                # Una función recursiva para poder calibrar de manera jerárquica.
                def _calibrar_jerárquíco_manual(lugar, jrq, clbs=None, d_mods=None):
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

                    if d_mods is None:
                        d_mods = {}
                    if clbs is None:
                        clbs = {}

                    if lugar is None:
                        # Si estamos al punto más alto de la jerarquía...

                        obs_lg = obs  # Tomar todos los datos
                        pariente = None  # No tenemos pariente

                        # Empezar con el modelo de base
                        mod_lg, vars_comp_lg = ec.gen_mod_bayes(
                            líms_paráms=líms_paráms, obs_x=obs[vars_x], obs_y=obs[var_y], binario=binario,
                            aprioris=None, vars_compart=True, nv_jerarquía=None
                        )

                        d_mods[None] = {
                            'mod': mod_lg,
                            'vars_compart': vars_comp_lg
                        }

                    else:
                        # Sino, hay un nivel superior en la jerarquía

                        # Obtener los datos correspondiendo a este nivel
                        lgs_potenciales = bd_datos.geog.obt_lugares_en(lugar)
                        obs_lg = obs[obs['lugar'].isin(lgs_potenciales + [lugar])]

                        # Intentar obtener la calibración del nivel superior.
                        try:
                            pariente = jrq[lugar]  # El nivel superior (pariente)

                            # Si todavía no se calibró éste, calibrarlo de manera recursiva.
                            if pariente not in d_mods:

                                # Calibrar el pariente
                                _calibrar_jerárquíco_manual(lugar=pariente, jrq=jrq, clbs=clbs, d_mods=d_mods)

                                if pariente in jrq and clbs[pariente] == clbs[jrq[pariente]]:
                                    d_mods[pariente] = d_mods[jrq[pariente]]
                                    mod_lg = d_mods[pariente]['mod']
                                    vars_comp_lg = d_mods[pariente]['vars_compart']

                                else:
                                    # Generar a prioris de la calibración
                                    aprs = _gen_a_prioris(líms=líms_paráms, dic_clbs=clbs[pariente])

                                    # Generar un nuevo modelo Bayes con los nuevos a prioris y guardarlo
                                    mod_lg, vars_comp_lg = ec.gen_mod_bayes(
                                        líms_paráms=líms_paráms, obs_x=obs[vars_x], obs_y=obs[var_y], binario=binario,
                                        aprioris=aprs, vars_compart=True, nv_jerarquía=None
                                    )

                                    d_mods[pariente] = {
                                        'mod': mod_lg,
                                        'vars_compart': vars_comp_lg
                                    }

                            else:
                                # Emplear el modelo pariente como base para la calibración
                                mod_lg = d_mods[pariente]['mod']
                                vars_comp_lg = d_mods[pariente]['vars_compart']

                        except KeyError:
                            # Si no existe, hay error.
                            raise ValueError(
                                _('El lugar "{}" no está bien inscrito en la jerarquía general.').format(lugar)
                            )

                    if len(obs_lg):
                        # Si tenemos datos con los cuales calibrar, hacerlo ahora
                        clbs[lugar] = _calibrar_mod_bayes(
                            mod_bayes=mod_lg, paráms=paráms, ops=ops_método, obs=obs_lg, vars_compartidos=vars_comp_lg
                        )

                    else:
                        # Si no hay datos con los cuales calibrar, copiar el diccionario del pariente.
                        clbs[lugar] = clbs[pariente]

                    # Devolver la calibración
                    return clbs

                # Efectuar las calibraciones para todos los lugares.
                dic_calibs = {}
                dic_modelos = {}
                for lg in lugares:
                    _calibrar_jerárquíco_manual(lugar=lg, jrq=jerarquía, clbs=dic_calibs, d_mods=dic_modelos)

                # Quitar los modelos de los resultados
                resultados = {
                    lg: {ll: v for ll, v in d.items() if ll not in ['mod', 'vars_compart']}
                    for lg, d in dic_calibs.items()
                }

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
                    lgs_potenciales = bd_datos.geog.obt_lugares_en(lugar)
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


def _gen_a_prioris(líms, dic_clbs):
    """
    Genera a prioris, basándose en los límites de los parámetros y en una calibración anterior. Devolvemos la clase
    de la distribución y sus parámetros de forma en una tupla (en vez de crear la distribución sí misma de una vez
    aquí) porque las distribuciones de PyMC3 se deben crear adentro de un bloque de contexto de modelo PyMC3, al cual
    no tenemos acceso aquí por el momento.

    Parameters
    ----------
    líms: dict[str, tuple]
        Un diccionario de los límites teoréticos de cada parámetro.
    dic_clbs: dict
        Un diccionario con los resultados procesados de una calibración anterior.

    Returns
    -------
    dict[str, tuple]
        Un diccionario con la distribución (clase PyMC3), y sus parámetros, de cada parámetro de interés.
    """

    # Para los resultados
    aprioris = {}

    for p, lp in líms.items():
        # Para cada parámetro de interés...

        dic = dic_clbs[p]  # El diccionario de calibraciones para este parámetro

        # Encontrar la distribución compatible con los límites y con el mejor ajusto con la calibración anterior.
        ajust_sp = _ajust_dist(datos=dic['dist'], líms=lp)
        nombre = ajust_sp['tipo']

        # El objeto PyMC3 correspondiendo a esta distribución
        dist_pm = dists[nombre]['pm']

        # Extraer y convertir los parámetros de la distribución PyMC3
        prms_sp = ajust_sp['prms']
        prms_pm = dists[nombre]['sp_a_pm'](prms_sp)

        # Guardar el resultado
        aprioris[p] = (dist_pm, prms_pm)

    # Devolver el diccionario de distribuciones a prioris.
    return aprioris


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

    # Calcular el punto de probabilidad máxima
    for p in paráms:
        # Para cada parámetro...

        # Ajustar el rango, si es muy grande (necesario para las funciones que siguen)
        escl = np.max(traza[p])
        rango = escl - np.min(traza[p])
        if escl < 10e10:
            escl = 1  # Si no es muy grande, no hay necesidad de ajustar

        # Intentar calcular la densidad máxima.
        try:
            # Se me olvidó cómo funciona esta parte.
            fdp = gaussian_kde(traza[p] / escl)
            x = np.linspace(traza[p].min() / escl - 1 * rango, traza[p].max() / escl + 1 * rango, 1000)
            máx = x[np.argmax(fdp.evaluate(x))] * escl
            d_máx[p] = máx

        except BaseException:
            d_máx[p] = None

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
        avisar(_('Error de optimización.'))

    # Devolver los resultados en el formato correcto.
    return {p: {'val': opt.x[i]} for i, p in enumerate(paráms)}


def _ajust_dist(datos, líms):
    """
    Basándose en límites teoréticos y datos de una traza, escoger la mejor distribución teorética para representar
    la traza.

    Parameters
    ----------
    datos: np.array
        La traza de datos.
    líms: tuple
        Los límites de la distribución.

    Returns
    -------
    dict[str, str]
        Un diccionario de la mejor distribución, sus parámetros ajustados y una medida de su ajusto.
    """

    # Empezemos el mejor ajusto en 0.
    mejor_ajusto = {'p': 0, 'tipo': None}

    # Tomaremos únicamente las distribuciones teoréticamente compatibles con los límites del parámetro.
    dists_potenciales = {ll: v['sp'] for ll, v in dists.items() if _líms_compat(líms, v['líms'])}

    # Buscar la mejor distribución
    for nombre_dist, dist_sp in dists_potenciales.items():
        # Para cada distribución posible...

        # Establecer los parámetros que no queremos calibrar, según el caso.
        if nombre_dist == 'Beta':
            restric = {'floc': líms[0], 'fscale': líms[1] - líms[0]}
        elif nombre_dist == 'Cauchy':
            restric = {}
        elif nombre_dist == 'Chi2':
            restric = {'floc': líms[0]}
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
            raise ValueError(_('Distribución "{}" no reconocida.').format(nombre_dist))

        # Intentar ajustar la distribución.
        try:
            tupla_prms = dist_sp.fit(datos, **restric)
        except BaseException:
            # Es posible que SciPy, en vez de una respuesta, nos devuelve un error muy obscuro. En general pasa
            # si le damos unos muy, muy mal ajustables a la distribución. En este caso, seguimoms en adelante sin
            # la distribución que no quiso cooperar.
            tupla_prms = None

        # Si logramos un ajusto...
        if tupla_prms is not None:
            # Medir el ajusto de la distribución
            p = estad.kstest(rvs=datos, cdf=dist_sp(*tupla_prms).cdf)[1]

            # Si el ajusto es mejor que el mejor ajusto anterior...
            if p > mejor_ajusto['p'] or mejor_ajusto['tipo'] is None:
                # Guardarlo
                mejor_ajusto['p'] = p
                mejor_ajusto['prms'] = tupla_prms
                mejor_ajusto['tipo'] = nombre_dist

    # Si no logramos un buen ajusto, avisarle al usuario.
    if mejor_ajusto['p'] <= 0.10:
        avisar(
            _('El ajusto de la mejor distribución ("{d}") quedó muy mal (p = {p}). Un buen valor sería > 0.1'
              ).format(d=mejor_ajusto['d'], p=round(mejor_ajusto['p'], 4))
        )

    # Devolver la distribución con el mejor ajusto, tanto como el valor de su ajusto.
    return mejor_ajusto


def _líms_compat(l_1, l_2):
    """
    Verifica si dos límites de parámetro son compatibles o no.

    Parameters
    ----------
    l_1: tuple
        El primer límite.
    l_2: tuple
        El otro límite.

    Returns
    -------
    bool
        Si son compatibles o no.
    """

    # Cambiar ±inf a None y números a 0.
    l_1 = [None if x is None or np.isinf(x) else 0 for x in l_1]
    l_2 = [None if x is None or np.isinf(x) else 0 for x in l_2]

    # Verificar si son compatibles
    return l_1 == l_2
