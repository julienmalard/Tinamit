from warnings import warn as avisar

from tinamit.Incertidumbre.Estadísticas import calib_bayes, optimizar, regresión
from tinamit import _
from tinamit.EnvolturaMDS.sintaxis import Ecuación
from tinamit.Incertidumbre.Datos import SuperBD
from tinamit.Modelo import Modelo

try:
    import pymc3 as pm
except ImportError:
    pm = None


class ConexDatos(object):
    def __init__(símismo, bd, modelo):
        """

        :param bd:
        :type bd: SuperBD
        :param modelo:
        :type modelo: Modelo
        """

        símismo.bd = bd
        símismo.modelo = modelo
        símismo.dic_info_calib = {}

    def estab_calib_var(símismo, var, ec=None, líms_paráms=None, paráms=None,
                        método=None, ops_método=None, regional=True):
        símismo.dic_info_calib[var] = {
            'ec': ec,
            'paráms': paráms,
            'líms_paráms': líms_paráms,
            'método': método,
            'ops_método': ops_método,
            'regional': regional
        }

    def borrar_calib_ec(símismo, var):
        símismo.dic_info_calib.pop(var)

    def calib_ecs(símismo, lugar=None, escala=None, fechas=None, bds=None, nombre='Calib Tinamït'):

        mod = símismo.modelo
        if nombre not in mod.calibs:
            mod.calibs[nombre] = {}

        for var, d_info in símismo.dic_info_calib.items():

            if var not in símismo.modelo.variables:
                avisar(_('El variable "{}" no existe en modelo "{}" y por tanto no se pudo calibrar.')
                       .format(var, símismo.modelo))
                continue

            calibración = símismo.calib_var(var=var, lugar=lugar, escala=escala, fechas=fechas, bds=bds, **d_info)
            for lg, clb_lg in calibración.items():
                if lg not in mod.calibs[nombre]:
                    mod.calibs[nombre][lg] = {}
                mod.calibs[nombre][lg][var] = clb_lg

    def calib_var(símismo, var, ec=None, paráms=None, líms_paráms=None, método=None, ops_método=None,
                  en=None, escala=None, por=None, fechas=None, aprioris=True, aprioris_por=None, bds=None):

        símismo.estab_calib_var(var=var, ec=ec, paráms=paráms, líms_paráms=líms_paráms, método=método,
                                ops_método=ops_método, regional=escala != 'individual')

        mod = símismo.modelo
        try:
            d_var = mod.variables[var]
        except KeyError:
            raise ValueError('El variable "{}" no existe en el modelo "{}".'.format(var, mod.nombre))

        lugares = símismo.bd.geog.obt_lugares_en(escala=escala, en=en, por=por)

        if ops_método is None:
            ops_método = {}

        if not isinstance(líms_paráms, list):
            líms_paráms = [líms_paráms] * len(paráms)
        líms_paráms = [(None, None) if x is None else x for x in líms_paráms]

        if paráms is None:
            paráms = [x for x in d_var['parientes'] if x in mod.constantes]
            # Buscar los límites teoréticos de los parámetros
            líms_paráms = []
            for p in paráms:
                try:
                    líms_paráms.append(mod.variables[p]['rango'])
                except KeyError:
                    líms_paráms.append((None, None))

        if not isinstance(paráms, list):
            paráms = [paráms]

        parientes = [x for x in d_var['parientes'] if x not in paráms]

        if ec is None:
            ec = d_var['ec']
        if not len(ec):
            líms_var = mod.variables[var]['líms']
            líms_parientes = [mod.variables[v]['líms'] for v in parientes]

            if len(parientes) == 1:
                raise NotImplementedError
            else:
                raise NotImplementedError

        if método is None:
            if pm:
                método = 'Inf Bayes'
            else:
                método = 'Optimizar'

        obj_ec = Ecuación(ec=ec, dialecto=símismo.modelo.__class__.__name__)
        vars_x = [x for x in obj_ec.variables() if x not in paráms]
        l_vars = vars_x + [var]

        if isinstance(lugares, dict):
            obs = [símismo.bd.obt_datos(l_vars=l_vars, lugar=v, datos=bds, fechas=fechas)['individual'].dropna()  # Arreglarme
                   for v in lugares.values()]
        else:
            obs = [símismo.bd.obt_datos(l_vars=l_vars, lugar=lugares, datos=bds, fechas=fechas)['individual'].dropna()] # Arreglarme

        obs_y = [l[var].values for l in obs]
        obs_x = [{x: l[x].values for x in vars_x} for l in obs]

        d_calib = {}
        for lg, x, y in zip(lugares, obs_x, obs_y):

            if método.lower() == 'inf bayes':
                if aprioris:
                    if aprioris_por is None:
                        lgs_apriosis = símismo.bd.geog.obt_lugares_en()
                    else:
                        raise NotImplementedError
                    obs_ap = símismo.bd.obt_datos(l_vars=l_vars, lugar=lgs_apriosis, datos=bds, fechas=fechas)[
                                  'individual'].dropna()  # Arreglarme

                    obs_y_ap = obs_ap[var].values
                    obs_x_ap = {x: obs_ap[x].values for x in vars_x}
                    res_ap = calib_bayes(obj_ec, paráms, líms_paráms, obs_x_ap, obs_y_ap, **ops_método)
                    info_gen_aprioris = [res_ap[p]['dist'] for p in res_ap]

                else:
                    info_gen_aprioris = None
                resultados = calib_bayes(obj_ec, paráms, líms_paráms, x, y, info_gen_aprioris, **ops_método)

            elif método.lower() == 'optimizar':
                resultados = optimizar(obj_ec, paráms, líms_paráms, x, y, **ops_método)

            elif método.lower() == 'regresión':
                resultados = regresión(obj_ec, paráms, líms_paráms, x, y, **ops_método)
            else:
                raise ValueError('')

            d_calib[lg] = resultados

        return d_calib

    def cargar_modelo(símismo, modelo):
        símismo.modelo = modelo
        for var in símismo.dic_info_calib:
            if var not in modelo.variables:
                avisar(_('El variable "{}" no existe en el nuevo modelo.').format(var))

    def no_calibrados(símismo):
        return [var for var in símismo.modelo.variables if var not in símismo.dic_info_calib]


