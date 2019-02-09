import os
import tempfile
from warnings import warn as avisar

import numpy as np
import scipy.stats as estad
import spotpy
import xarray as xr
from scipy.optimize import minimize
from scipy.stats import gaussian_kde

from tinamit.Análisis.Datos import BDtexto, gen_SuperBD, SuperBD
from tinamit.Análisis.Sens.behavior import aic
from tinamit.Análisis.sintaxis import Ecuación
from tinamit.Calib.ej.obs_patrón import compute_superposition
from tinamit.config import _

try:
    import pymc3 as pm
except ImportError:  # pragma: sin cobertura
    pm = None

if pm is None:
    dists = None  # pragma: sin cobertura
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

    def __init__(símismo, ec, var_y=None, otras_ecs=None, corresp_vars=None, dialecto=None):
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
        corresp_vars: dict[str, str]
            Un diccionario de equivalencias de nombres entre ecuación y eventual base de datos.
        """

        # Crear la ecuación.
        símismo.ec = Ecuación(ec, nombre=var_y, otras_ecs=otras_ecs, nombres_equiv=corresp_vars, dialecto=dialecto)

        # Asegurarse que se especificó el variable y.
        if símismo.ec.nombre is None:
            raise ValueError(_('Debes especificar el nombre del variable dependiente, o con el parámetro'
                               '`var_y`, o directamente en la ecuación, por ejemplo: "y = a*x ..."'))

    def calibrar(símismo, bd_datos, paráms=None, líms_paráms=None, método=None, binario=False, geog=None, en=None,
                 escala=None, jrq=None, ops_método=None, no_recalc=None):
        """
        Calibra la ecuación, según datos, y, opcionalmente, una geografía espacial.

        Parameters
        ----------
        bd_datos : SuperBD
            La base de datos. Los nombres de las columnas deben coincidir con los nombres de los variables en la
            ecuación.
        paráms : list[str]
            La lista de los parámetros para calibrar. Si es ``None``, se tomarán los variables que no
            están en `bd_datos`.
        líms_paráms : dict[str, tuple]
            Un diccionario con los límites teoréticos de los parámetros.
        método : {'optimizar', 'inferencia bayesiana'}
            El método para emplear para la calibración.
        binario : bool
            Si la ecuación es binaria o no.
        en : str | int
            El código del lugar donde quieres calibrar esta ecuación. Aplica únicamente si `bd_datos` está
            conectada a un objeto :class:`Geografía`.
        escala : str
            La escala geográfica a la cual quieres calibrar el modelo. Aplica únicamente si `bd_datos` está
            conectada a un objeto :class:`Geografía`.
        ops_método : dict
            Un diccionario de opciones adicionales a pasar directamente al algoritmo de calibración. Por ejemplo,
            puedes pasar argumentos para pymc3.Model.sample() aquí. También puedes especificar opciones
            específicas a Tinamït:
                - 'mod_jerárquico': bool. Determina si empleamos un modelo bayesiano jerárquico para la geografía.

        Returns
        -------
        dict
            La calibración completada.
        """

        # Poner diccionario vacío si `ops_método` no existe.
        if ops_método is None:
            ops_método = {}
        if no_recalc is None:
            no_recalc = {}

        # Leer los variables de la ecuación.
        vars_ec = símismo.ec.variables()
        var_y = símismo.ec.nombre

        # Asegurarse que tenemos observaciones para el variable y.
        if var_y not in bd_datos.variables:
            raise ValueError(_('El variable "{}" no parece existir en la base de datos.').format(var_y))

        # Adivinar los parámetros si ne se especificaron.
        if paráms is None:
            # Todos los variables para cuales no tenemos observaciones.
            paráms = [x for x in vars_ec if x not in bd_datos.variables]

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
        if geog is not None:
            lugares = geog.obt_lugares_en(en, escala=escala)
            jerarquía = geog.obt_jerarquía(en, escala=escala, orden_jerárquico=jrq)
        else:
            if en is not None or escala is not None:
                raise ValueError(_('Debes especificar una geografía en `geog` para emplear `en` o `escala`.'))
            lugares = jerarquía = None

        if all(p in no_recalc and all(lg in no_recalc[p] for lg in lugares) for p in paráms):
            return

        # Ahora, por fin hacer la calibración.
        if método == 'inferencia bayesiana':
            return símismo._calibrar_bayesiana(
                ec=símismo.ec, var_y=var_y, vars_x=vars_x, líms_paráms=líms_paráms_final, binario=binario,
                ops_método=ops_método, bd_datos=bd_datos, lugares=lugares, jerarquía=jerarquía, geog=geog,
                mod_jerárquico=mod_jerárquico
            )
        elif método == 'optimizar':
            return símismo._calibrar_optim(
                ec=símismo.ec, var_y=var_y, vars_x=vars_x, líms_paráms=líms_paráms_final,
                ops_método=ops_método, bd_datos=bd_datos, lugares=lugares, jerarquía=jerarquía, geog=geog
            )
        else:
            raise ValueError(_('Método de calibración "{}" no reconocido.').format(método))

    @staticmethod
    def _calibrar_bayesiana(ec, var_y, vars_x, líms_paráms, binario, bd_datos, lugares, jerarquía, geog,
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
        bd_datos: SuperBD
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
        obs = bd_datos.obt_datos(l_vars=l_vars, excl_faltan=True, interpolar=False)

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

                        nv[:] = [x for x in nv
                                 if len(obs.where(obs['lugar'].isin(geog.obt_lugares_en(x) + [x]), drop=True)['n'])
                                 ]  # para hacer: accelerar con .values()
                    else:

                        nv[:] = [x for x in nv if x in [jerarquía[y] for y in nv_jerarquía[í + 1]]]

                í_nv_jerarquía = [np.array([nv_jerarquía[í - 1].index(jerarquía[x]) for x in y])
                                  for í, y in list(enumerate(nv_jerarquía))[:0:-1]]
                obs = obs.where(obs['lugar'].isin(nv_jerarquía[-1]), drop=True)
                í_nv_jerarquía.insert(0, np.array([nv_jerarquía[-1].index(x) for x in obs['lugar'].values.tolist()]))

                # Generar el modelo bayes
                mod_bayes_jrq = ec.gen_mod_bayes(
                    líms_paráms=líms_paráms, obs_x=obs[vars_x], obs_y=obs[var_y],
                    aprioris=None, binario=binario, nv_jerarquía=í_nv_jerarquía[::-1],
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
                    lgs_potenciales = geog.obt_todos_lugares_en(lg)
                    obs_lg = obs.where(obs['lugar'].isin(lgs_potenciales + [lg]), drop=True)
                    if len(obs_lg['n']):
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
    def _calibrar_optim(ec, var_y, vars_x, líms_paráms, bd_datos, lugares, jerarquía, geog, ops_método):
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
                    lgs_potenciales = geog.obt_todos_lugares_en(lugar)
                    obs_lg = obs.where(obs['lugar'].isin(lgs_potenciales + [lugar]), drop=True)

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
                if len(obs_lg['n']):
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

    def calibrar(símismo, paráms, líms_paráms, bd, método, vars_obs, n_iter, guardar, corresp_vars=None, tipo_proc=None,
                 mapa_paráms=None, final_líms_paráms=None, obj_func='AIC', guar_sim=False, egr_spotpy=False):

        método = método.lower()
        mod = símismo.mod
        if isinstance(bd, xr.Dataset):
            obs = gen_SuperBD(bd)
            t_inic = None
        else:
            obs = _conv_xr(bd, vars_obs)
            t_final = len(obs['n'])
            t_inic = obs['n'].values[0]

        if corresp_vars is None:
            corresp_vars = {}

        if vars_obs is None:
            vars_obs = list(obs.variables)
        vars_obs = [corresp_vars[v] if v in corresp_vars else v for v in vars_obs]

        if isinstance(bd, xr.Dataset) and tipo_proc is not None:
            obs = obs.obt_datos(vars_obs, tipo='datos', interpolar=False)[vars_obs]
            t_final = len(obs['n']) - 1
        elif tipo_proc is None:
            obs = obs.obt_datos(vars_obs, tipo='datos')[vars_obs]
            t_final = len(obs['n']) - 1

        if tipo_proc is not None:
            par_spotpy = {k: str(i) for i, (k, v) in enumerate(final_líms_paráms.items())}

        if not egr_spotpy:
            if método in _algs_spotpy:
                temp = tempfile.NamedTemporaryFile('w', encoding='UTF-8', prefix='CalibTinamït_')
                if tipo_proc is None:
                    mod_spotpy = ModSpotPy(mod=mod, líms_paráms=líms_paráms, obs=obs)
                else:
                    mod_spotpy = PatrónProc(mod=mod, líms_paráms=líms_paráms, obs=obs, tipo_proc=tipo_proc,
                                            mapa_paráms=mapa_paráms, comp_final_líms=final_líms_paráms,
                                            obj_func=obj_func, t_final=t_final, t_inic=t_inic, guar_sim=guar_sim
                                            )
                if método in ['dream', 'mcmc', 'sceua']:
                    muestreador = _algs_spotpy[método](mod_spotpy, dbname=temp.name, dbformat='csv', save_sim=False,
                                                       alt_objfun=None)
                else:
                    muestreador = _algs_spotpy[método](mod_spotpy, dbname=temp.name, dbformat='csv', save_sim=False)

                if final_líms_paráms is not None and método in ['dream', 'demcz', 'sceua']:
                    if método == 'dream':
                        muestreador.sample(repetitions=n_iter, runs_after_convergence=n_iter,  # repetitions= 2000+n_iter
                                           nChains=len(final_líms_paráms))
                    elif método == 'sceua':
                        muestreador.sample(n_iter, ngs=len(final_líms_paráms) * 3)
                    elif método == 'demcz':
                        muestreador.sample(n_iter, nChains=len(final_líms_paráms) * 2)
                else:
                    muestreador.sample(n_iter)

                egr_spotpy = BDtexto(temp.name + '.csv')
            else:
                raise ValueError(_('Método de calibración "{}" no reconocido.').format(método))
        else:
            egr_spotpy = BDtexto(egr_spotpy)

        cols_prm = [c for c in egr_spotpy.obt_nombres_cols() if c.startswith('par')]
        trzs = egr_spotpy.obt_datos(cols_prm)
        probs = egr_spotpy.obt_datos('like1')['like1']

        # if os.path.isfile(temp.name + '.csv'):
        #     os.remove(temp.name + '.csv')

        if isinstance(trzs, dict):
            buenas = (probs >= np.min(np.sort(probs)[int(len(probs) * 0.8):]))
            trzs = {p: trzs[p][buenas] for p in cols_prm}
            probs = probs[buenas]  # like values
        else:
            trzs = trzs[-n_iter:]
            probs = probs[-n_iter:]

            # if método == 'dream':
            #     if isinstance(trzs, dict):
            #         buenas = (probs >= np.min(np.sort(probs)[int(len(probs) * 0.8):]))
            #         trzs = {p: trzs[p][buenas] for p in cols_prm}
            #         probs = probs[buenas]  # like values
            #     else:
            #         trzs = trzs[-n_iter:]
            #         probs = probs[-n_iter:]
            # elif método != 'mcmc':
            #     buenas = (probs >= np.min(np.sort(probs)[int(len(probs) * 0.8):]))
            #     trzs = {p: trzs[p][buenas] for p in cols_prm}
            #     probs = probs[buenas]  # like values

        rango_prob = (probs.min(), probs.max())
        pesos = (probs - rango_prob[0]) / (rango_prob[1] - rango_prob[0])  # those > 0.8 like, weight distribution

        res = {'buenas': np.where(buenas)[0], 'peso': pesos, 'máx_prob': rango_prob[1]}
        if tipo_proc is None:
            for i, p in enumerate(paráms):
                col_p = 'par' + str(i)
                res[p] = {'dist': trzs[col_p], 'val': _calc_máx_trz(trzs[col_p])}
            # calculate the maxi distribution of the simulation results, and the weights
        else:
            for i in range(len(list(trzs.values())[0])):
                x = np.asarray([val[i] for val in list(trzs.values())])
                val_inic = gen_val_inic(x, mapa_paráms, líms_paráms, final_líms_paráms)
                for k, val in val_inic.items():
                    if k in res:
                        res[k]['dist'].append(val)
                    else:
                        res[k] = {'dist': [val], 'val': []}
            for k, v in res.items():
                if k in líms_paráms:
                    if isinstance(líms_paráms[k], tuple):
                        res[k]['val'].append(_calc_máx_trz(trzs['par' + par_spotpy[k]]))
                    elif isinstance(líms_paráms[k], list):
                        res[k]['val'].extend(
                            [_calc_máx_trz(trzs['par' + par_spotpy[f'{k}_{str(i)}']]) for i in
                             range(len(líms_paráms[k]))])
                elif isinstance(v, dict):
                    for p, mapa in mapa_paráms.items():
                        if isinstance(mapa, dict):
                            res[k]['val'].extend(_calc_máx_trz(trzs['par' + par_spotpy[f'{p}_{str(i)}']]) for i in
                                                 range(len(líms_paráms[p])))
        if guardar:
            np.save(guardar, res)
        return res  # 100*215 (100*6) # dist: 6*100, val:6, peso: 6*100


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

    # Calcular el punto de probabilidad máxima
    for p in paráms:
        # Para cada parámetro...

        dims = traza[p].shape
        if len(dims) == 1:
            d_máx[p] = _calc_máx_trz(traza[p])
        elif len(dims) == 2:
            d_máx[p] = np.empty(dims[1])
            for e in range(dims[1]):
                d_máx[p][e] = _calc_máx_trz(traza[p][:, e])
        else:
            raise ValueError

    # Devolver los resultados procesados.
    return {p: {'val': d_máx[p], 'dist': traza[p]} for p in paráms}


def _calc_máx_trz(trz):
    if len(trz) == 1:
        return trz[0]

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


def _conv_xr(datos, vars_obs):  # datos[0] time; datos[1] dict{obspoly: ndarray}
    if isinstance(datos, tuple):
        matriz_vacía = np.empty([len(list(datos[1].values())[0]), len(datos[1])])  # 60, 38
    else:
        raise TypeError(_("Por favor agregue o seleccione el tipo correcto de los datos observados."))

    for poly, data in datos[1].items():
        matriz_vacía[:, list(datos[1]).index(poly)] = np.asarray(datos[1][poly])

    return xr.Dataset(
        data_vars={vars_obs[0]: (('n', 'x0'), matriz_vacía)},
        coords={'n': datos[0],
                'x0': np.asarray(list(datos[1])),
                'tiempo': np.asarray(range(len(list(datos[0])))),
                }
    )


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
    'demcz': spotpy.algorithms.demcz,
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
        obs: xr.Dataset
        """

        símismo.paráms = [
            spotpy.parameter.Uniform(str(list(líms_paráms).index(p)), low=d[0], high=d[1], optguess=(d[0] + d[1]) / 2)
            for p, d in líms_paráms.items()
        ]
        símismo.nombres_paráms = list(líms_paráms)
        símismo.mod = mod
        símismo.vars_interés = sorted(list(obs.data_vars))
        símismo.t_final = len(obs['n']) - 1

        símismo.mu_obs = símismo._aplastar(obs.mean())  # nparrar(3,) -> 1; obs=xr.Dtset(21,3)
        símismo.sg_obs = símismo._aplastar(obs.std())  # nparrar(3,) -> 1
        símismo.obs_norm = símismo._aplastar((obs - obs.mean()) / obs.std())  # ??? (63,)

    def parameters(símismo):
        return spotpy.parameter.generate(símismo.paráms)

    def simulation(símismo, x):
        res = símismo.mod.simular(
            t_final=símismo.t_final, vars_interés=símismo.vars_interés, vals_inic=dict(zip(símismo.nombres_paráms, x))
        )
        m_res = np.array([res[v].values for v in símismo.vars_interés]).T  # Transpose the array shape why?

        return ((m_res - símismo.mu_obs) / símismo.sg_obs).T.ravel()  # (63,) 1*21*3 -> 3*21 -> flatten (??)

    def evaluation(símismo):
        return símismo.obs_norm

    def objectivefunction(símismo, simulation, evaluation, params=None):
        # like = spotpy.likelihoods.gaussianLikelihoodMeasErrorOut(evaluation,simulation)
        like = spotpy.objectivefunctions.nashsutcliffe(evaluation, simulation)  # should be ave()

        return like

    def _aplastar(símismo, datos):
        if isinstance(datos, xr.Dataset):
            return np.array([datos[v].values.ravel() for v in símismo.vars_interés]).ravel()
        elif isinstance(datos, dict):
            return np.array([datos[v].ravel() for v in sorted(datos)]).ravel()


class PatrónProc(object):
    itr = 0

    def __init__(símismo, mod, líms_paráms, obs, tipo_proc, mapa_paráms, comp_final_líms, obj_func, t_final,
                 t_inic, guar_sim):
        símismo.paráms = [
            spotpy.parameter.Uniform(str(list(comp_final_líms).index(p)), low=d[0], high=d[1],
                                     optguess=(d[0] + d[1]) / 2)
            for p, d in comp_final_líms.items()
        ]
        símismo.mapa_paráms = mapa_paráms
        símismo.líms_paráms = líms_paráms
        símismo.final_líms_paráms = comp_final_líms
        símismo.obj_func = obj_func
        símismo.mod = mod
        símismo.guar_sim = guar_sim
        símismo.vars_interés = sorted(list(obs.data_vars))
        símismo.t_inic = t_inic
        símismo.t_final = t_final
        símismo.tipo_proc = tipo_proc
        símismo.obs = obs
        símismo.mu_obs, símismo.sg_obs, símismo.obs_norm = aplastar(obs, símismo.vars_interés)

        símismo.eval, símismo.len_bparam = patro_proces(símismo.tipo_proc, símismo.obs, símismo.obs_norm,
                                                        símismo.vars_interés)  # multidim: 6*21//21*38//1*1*38

    def parameters(símismo):
        return spotpy.parameter.generate(símismo.paráms)

    def simulation(símismo, x):
        vals_inic = {PatrónProc.itr:
                         gen_val_inic(x, símismo.mapa_paráms, símismo.líms_paráms, símismo.final_líms_paráms)}

        res = símismo.mod.simular_grupo(vars_interés=símismo.vars_interés[0], t_final= 41, #símismo.t_final,
                                        vals_inic=vals_inic, guardar=símismo.guar_sim)

        PatrónProc.itr += 1

        if isinstance(res, dict):
            m_res = np.array([list(res.values())[0][v] for v in símismo.vars_interés][0])  # 42*215
        else:
            m_res = np.array([res[v].values for v in símismo.vars_interés][0])  # 62*215
        if m_res.shape[1] != símismo.obs['x0'].values.size:
            if m_res.shape[0] != símismo.obs['n'].values.size:
                m_res = m_res[:-1, :]
                n_res = np.empty([len(m_res), símismo.obs['x0'].values.size])
                for ind, v in enumerate([int(i) for i in símismo.obs['x0'].values]):
                    n_res[:, ind] = m_res[:, v - 1]
            else:
                raise ValueError(" ")
        else:
            n_res = m_res  # 21*6
        return ((n_res - símismo.mu_obs) / símismo.sg_obs).T  # 62*38 -> 38*62//6*21//18*62

    def evaluation(símismo):
        return símismo.eval

    def objectivefunction(símismo, simulation, evaluation, params=None):
        # like = spotpy.likelihoods.gaussianLikelihoodMeasErrorOut(evaluation,simulation)
        # like = spotpy.objectivefunctions.nashsutcliffe(evaluation, simulation)
        gof = gen_gof(símismo.tipo_proc, simulation, evaluation, símismo.obj_func, símismo.len_bparam)
        return gof


def patro_proces(tipo_proc, obs, norm_obs, vars_interés):
    if tipo_proc == 'multidim':  # {var: nparray[61, 38]}
        return norm_obs, 0  # nparray[38, 61]
    elif tipo_proc == 'patrón':
        d_patron = compute_superposition(obs, norm_obs)[1]
        matriz_vacía = np.empty([obs[vars_interés[0]].values.shape[0], len(d_patron)])  # 61, 38
        length_params = []
        for poly, d_data in d_patron.items():
            matriz_vacía[:, list(d_patron).index(poly)] = np.asarray(d_patron[poly]['y_pred'])
            length_params.append(len(list(d_data.values())[0]['bp_params']))
        return matriz_vacía.T, length_params  # (nparray 38*61, [list of the length of the bp_params])


def aplastar(datos, vars_interés):
    npoly = datos['x0'].values
    if isinstance(datos, xr.Dataset):
        dato = np.asarray([datos[v].values for v in vars_interés][0])  # 61*38
        mu = np.array([np.nanmean(dato[:, p]) for p in list((range(len(npoly))))])  # 215
        sg = np.array([np.nanstd(dato[:, p]) for p in list((range(len(npoly))))])  # 215

        norm = np.array([((dato[:, p] - mu[p]) / sg[p]) for p in list((range(len(npoly))))])  # 38*61
        return mu, sg, norm


def gen_val_inic(x, mapa_paráms, líms_paráms, final_líms_paráms):
    # if isinstance(x, np.ndarray):
    vals_inic = {p: np.array(x[list(final_líms_paráms).index(p)]) for p in líms_paráms if p in final_líms_paráms}
    # else:
    # raise TypeError(f"simulation results {x} must be the type of np.ndarray")

    for p, mapa in mapa_paráms.items():
        if isinstance(mapa, list):
            mapa = np.array(mapa)

        if isinstance(mapa, np.ndarray):
            vals_inic[p] = np.empty(len(mapa))
            for i, cof in enumerate(mapa):
                vals_inic[p][i] = x[list(final_líms_paráms).index(f'{p}_{cof}')]

        elif isinstance(mapa, dict):
            transf = mapa['transf'].lower()
            for var, mp_var in mapa['mapa'].items():
                vals_inic[var] = np.empty(len(mp_var))
                if transf == 'prom':
                    for i, t_índ in enumerate(mp_var):
                        vals_inic[var][i] = (x[list(final_líms_paráms).index(f'{p}_{t_índ[0]}')] +
                                             x[list(final_líms_paráms).index(f'{p}_{t_índ[1]}')]) / 2
                else:
                    raise ValueError(_('Transformación "{}" no reconocida.').format(transf))

    return vals_inic


def gen_gof(tipo_proc, sim=None, eval=None, obj_func=None, len_bparam=None):
    if obj_func == 'NSE':
        if eval.shape == sim.shape:
            return nse(eval, sim)
        else:
            return np.array([nse(eval, sim[i, :]) for i in range(len(sim))])
    elif obj_func == 'AIC':
        if tipo_proc == 'multidim':
            raise TypeError(_(f"{obj_func} no puede procesar el tipo {tipo_proc}"))
        elif tipo_proc == 'patrón':
            if not isinstance(eval, tuple):
                len_obs_poly = np.empty([len(eval)])
                for i, poly in enumerate(sim):
                    len_obs_poly[i] = -aic(len_bparam[i], eval[i], poly)
                return np.nanmean(len_obs_poly)
            else:
                len_bparam = eval[1]
                eval = eval[0]
                len_valid_sim = np.empty([len(sim), len(len_bparam)])  # 20*poly6
                for i, poly_aray in enumerate(sim):  # i=[1, 20], pa=[6*21]
                    for j, poly in enumerate(poly_aray):  # j=1, 6; poly [21]
                        len_valid_sim[i, j] = -aic(len_bparam[j], eval[j], poly)
                return np.nanmean(len_valid_sim, axis=1)


def nse(obs, sim):
    s, e = np.array(sim), np.array(obs)
    # s,e=simulation,evaluation
    mean_observed = np.nanmean(e)
    # compute numerator and denominator
    numerator = np.nansum((e - s) ** 2)
    denominator = np.nansum((e - mean_observed) ** 2)
    # compute coefficient
    return 1 - (numerator / denominator)
