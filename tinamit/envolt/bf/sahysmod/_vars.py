import numpy as np

from tinamit.config import _
from tinamit.envolt.bf import VariablesModBloques, VarBloque
from tinamit.mod.var import Variable


class VarSAHYSMOD(Variable):
    def __init__(símismo, cód, **argsll):
        símismo.cód = cód
        super().__init__(**argsll)


class VarBloqSAHYSMOD(VarSAHYSMOD, VarBloque):

    def __init__(símismo, cód, nombre, unid, ingr, egr, tmñ_bloques, inic=0, líms=None, info=''):
        super().__init__(
            cód, nombre=nombre, unid=unid, ingr=ingr, egr=egr, tmñ_bloques=tmñ_bloques, inic=inic, líms=líms, info=info
        )


class VariablesSAHYSMOD(VariablesModBloques):
    def __init__(símismo, inic):
        # Guardar el número de estaciones y de polígonos
        n_estaciones = int(inic['NS'])
        dur_estaciones = [int(x) for x in inic['TS']]  # La duración de las estaciones (en meses)

        # Asegurarse que el número de estaciones es igual al número de duraciones de estaciones.
        if n_estaciones != len(dur_estaciones):
            raise ValueError(
                _('Error en el fuente de datos iniciales SAHYSMOD: el número de duraciones de estaciones'
                  'especificadas no corresponde al número de estaciones especificadas (líneas 3 y 4).')
            )

        super().__init__(_vars_sahysmod(inic, dur_est=dur_estaciones), tmñ_bloques=dur_estaciones)

    def var_a_cód(símismo, var):
        return símismo[var].cód

    def cód_a_var(símismo, cód):
        return next(v for v in símismo if v.cód.strip('#') == cód.strip('#'))


def _vars_sahysmod(d_inic, dur_est):
    n_polí = int(d_inic['NN_IN'])
    n_est = len(dur_est)
    l_vars = []
    for cód, d in _info_vars.items():
        try:
            vals = d_inic[cód.replace('#', '').upper()]
            if '#' in cód and vals.shape == (n_est, n_polí):
                inic = vals[0]
            else:
                inic = vals
                vals = None
        except KeyError:
            vals = None
            inic = np.zeros(n_polí)

        if '#' in cód:
            var = VarBloqSAHYSMOD(
                cód=cód, nombre=d['nombre'], tmñ_bloques=dur_est, unid=d['unid'], ingr=d['ingr'], egr=d['egr'],
                inic=inic
            )
            if vals is not None:
                var.poner_vals_paso(val=vals)
        else:
            var = VarSAHYSMOD(cód=cód, nombre=d['nombre'], unid=d['unid'], ingr=d['ingr'], egr=d['egr'], inic=inic)

        l_vars.append(var)

    return l_vars


# Un diccionario de variables SAHYSMOD. Ver la documentación SAHYSMOD para más detalles.
_info_vars = {
    'Pp#': {'nombre': 'Pp - Rainfall', 'unid': 'm3/season/m2', 'ingr': True, 'egr': False},
    'Ci#': {'nombre': 'Ci - Incoming canal salinity', 'unid': 'dS/m', 'ingr': True,
            'egr': True},
    'Cinf': {'nombre': 'Cinf - Aquifer inflow salinity', 'unid': 'dS/m', 'ingr': True,
             'egr': False},
    'Dc': {'nombre': 'Dc - Capillary rise critical depth', 'unid': 'm', 'ingr': True, 'egr': False},
    'Dd': {'nombre': 'Dd - Subsurface drain depth', 'unid': 'm', 'ingr': True, 'egr': False},
    'Dr': {'nombre': 'Dr - Root zone thickness', 'unid': 'm', 'ingr': True, 'egr': False},
    'Dx': {'nombre': 'Dx - Transition zone thickness', 'unid': 'm', 'ingr': True, 'egr': False},
    'EpA#': {'nombre': 'EpA - Potential ET crop A', 'unid': 'm3/season/m2', 'ingr': True,
             'egr': False},
    'EpB#': {'nombre': 'EpB - Potential ET crop B', 'unid': 'm3/season/m2', 'ingr': True,
             'egr': False},
    'EpU#': {'nombre': 'EpU - Potential ET non-irrigated', 'unid': 'm3/season/m2', 'ingr': True,
             'egr': False},
    'Flq': {'nombre': 'Flq - Aquifer leaching efficienty', 'unid': 'Dmnl', 'ingr': True,
            'egr': False},
    'Flr': {'nombre': 'Flr - Root zone leaching efficiency', 'unid': 'Dmnl', 'ingr': True,
            'egr': False},
    'Flx': {'nombre': 'Flx - Transition zone leaching efficiency', 'unid': 'Dmnl', 'ingr': True,
            'egr': False},
    'Frd#': {'nombre': 'Frd - Drainage function reduction factor', 'unid': 'Dmnl', 'ingr': True,
             'egr': False},
    'FsA#': {'nombre': 'FsA - Water storage efficiency crop A', 'unid': 'Dmnl', 'ingr': True,
             'egr': False},
    'FsB#': {'nombre': 'FsB - Water storage efficiency crop B', 'unid': 'Dmnl', 'ingr': True,
             'egr': False},
    'FsU#': {'nombre': 'FsU - Water storage efficiency non-irrigated', 'unid': 'Dmnl',
             'ingr': True, 'egr': False},
    'Fw#': {'nombre': 'Fw - Fraction well water to irrigation', 'unid': 'Dmnl', 'ingr': True,
            'egr': False},
    'Gu#': {'nombre': 'Gu - Subsurface drainage for irrigation', 'unid': 'm3/season/m2',
            'ingr': True, 'egr': False},
    'Gw#': {'nombre': 'Gw - Groundwater extraction', 'unid': 'm3/season/m2', 'ingr': True,
            'egr': True},
    'Hc': {'nombre': 'Hp - Initial water level semi-confined', 'unid': 'm', 'ingr': True,
           'egr': False},
    'IaA#': {'nombre': 'IaA - Crop A field irrigation', 'unid': 'm3/season/m2', 'ingr': True,
             'egr': True},
    'IaB#': {'nombre': 'IaB - Crop B field irrigation', 'unid': 'm3/season/m2', 'ingr': True,
             'egr': True},
    'KcA#': {'nombre': 'Rice A - Crop A paddy?', 'unid': 'Dmnl', 'ingr': True, 'egr': False},
    'KcB#': {'nombre': 'Rice B - Crop B paddy?', 'unid': 'Dmnl', 'ingr': True, 'egr': False},
    'Kd': {'nombre': 'Kd - Subsurface drainage?', 'unid': 'Dmnl', 'ingr': True, 'egr': False},
    'Kf': {'nombre': 'Kf - Farmers\'s responses', 'unid': 'Dmnl', 'ingr': True, 'egr': False},
    'Kaq1': {'nombre': 'Kaq1 - Horizontal hydraulic conductivity 1', 'unid': 'm/day', 'ingr': True,
             'egr': False},
    'Kaq2': {'nombre': 'Kaq2 - Horizontal hydraulic conductivity 2', 'unid': 'm/day', 'ingr': True,
             'egr': False},
    'Kaq3': {'nombre': 'Kaq3 - Horizontal hydraulic conductivity 3', 'unid': 'm/day', 'ingr': True,
             'egr': False},
    'Kaq4': {'nombre': 'Kaq4 - Horizontal hydraulic conductivity 4', 'unid': 'm/day', 'ingr': True,
             'egr': False},
    'Ksc1': {'nombre': 'Ksc1 - Semi-confined aquifer 1?', 'unid': 'Dmnl', 'ingr': True,
             'egr': False},
    'Ksc2': {'nombre': 'Ksc2 - Semi-confined aquifer 2?', 'unid': 'Dmnl', 'ingr': True,
             'egr': False},
    'Ksc3': {'nombre': 'Ksc3 - Semi-confined aquifer 3?', 'unid': 'Dmnl', 'ingr': True,
             'egr': False},
    'Ksc4': {'nombre': 'Ksc4 - Semi-confined aquifer 4?', 'unid': 'Dmnl', 'ingr': True,
             'egr': False},
    'Kr#': {'nombre': 'Kr - Land use key', 'unid': 'Dmnl', 'ingr': True, 'egr': True},
    'Kvert': {'nombre': 'Kvert - Vertical hydraulic conductivity semi-confined', 'unid': 'm/day',
              'ingr': True, 'egr': False},
    'Lc#': {'nombre': 'Lc - Canal percolation', 'unid': 'm3/season/m2', 'ingr': True,
            'egr': False},
    'Peq': {'nombre': 'Peq - Aquifer effective porosity', 'unid': 'm/m', 'ingr': True,
            'egr': False},
    'Per': {'nombre': 'Per - Root zone effective porosity', 'unid': 'm/m', 'ingr': True,
            'egr': False},
    'Pex': {'nombre': 'Pex - Transition zone effective porosity', 'unid': 'm/m', 'ingr': True,
            'egr': False},
    'Psq': {'nombre': 'Psq - Semi-confined aquifer storativity', 'unid': 'Dmnl', 'ingr': True,
            'egr': False},
    'Ptq': {'nombre': 'Ptq - Aquifer total pore space', 'unid': 'm/m', 'ingr': True, 'egr': False},
    'Ptr': {'nombre': 'Ptr - Root zone total pore space', 'unid': 'm/m', 'ingr': True,
            'egr': False},
    'Ptx': {'nombre': 'Ptx - Transition zone total pore space', 'unid': 'm/m', 'ingr': True,
            'egr': False},
    'QH1': {'nombre': 'QH1 - Drain discharge to water table height ratio', 'unid': 'm/day/m',
            'ingr': True, 'egr': False},
    'QH2': {'nombre': 'QH2 - Drain discharge to sq. water table height ratio', 'unid': 'm/day/m2',
            'ingr': True, 'egr': False},
    'Qinf': {'nombre': 'Qinf - Aquifer inflow', 'unid': 'm3/season/m2', 'ingr': True, 'egr': False},
    'Qout': {'nombre': 'Qout - Aquifer outflow', 'unid': 'm3/season/m2', 'ingr': True,
             'egr': False},
    'SL': {'nombre': 'SL - Soil surface level', 'unid': 'm', 'ingr': True, 'egr': False},
    'SiU#': {'nombre': 'SiU - Surface inflow to non-irrigated', 'unid': 'm3/season/m2',
             'ingr': True, 'egr': False},
    'SoA#': {'nombre': 'SdA - Surface outflow crop A', 'unid': 'm3/season/m2', 'ingr': True,
             'egr': False},
    'SoB#': {'nombre': 'SdB - Surface outflow crop B', 'unid': 'm3/season/m2', 'ingr': True,
             'egr': False},
    'SoU#': {'nombre': 'SoU - Surface outflow non-irrigated', 'unid': 'm3/season/m2',
             'ingr': True, 'egr': False},
    'It#': {'nombre': 'It - Total irrigation', 'unid': 'm3/season/m2', 'ingr': False,
            'egr': True},
    'Is#': {'nombre': 'Is - Canal irrigation', 'unid': 'm3/season/m2', 'ingr': False,
            'egr': True},
    'FfA#': {'nombre': 'FfA - Irrigation efficiency crop A', 'unid': 'Dmnl', 'ingr': False,
             'egr': True},
    'FfB#': {'nombre': 'FfB - Irrigation efficiency crop B', 'unid': 'Dmnl', 'ingr': False,
             'egr': True},
    'FfT#': {'nombre': 'FfT - Total irrigation efficiency', 'unid': 'Dmnl', 'ingr': False,
             'egr': True},
    'Io#': {'nombre': 'Io - Water leaving by canal', 'unid': 'm3/season/m2', 'ingr': False,
            'egr': True},
    'JsA#': {'nombre': 'JsA - Irrigation sufficiency crop A', 'unid': 'Dmnl', 'ingr': False,
             'egr': True},
    'JsB#': {'nombre': 'JsB - Irrigation sufficiency crop B', 'unid': 'Dmnl', 'ingr': False,
             'egr': True},
    'EaU#': {'nombre': 'EaU - Actual evapotranspiration nonirrigated', 'unid': 'm3/season/m2',
             'ingr': False, 'egr': True},
    'LrA#': {'nombre': 'LrA - Root zone percolation crop A', 'unid': 'm3/season/m2',
             'ingr': False, 'egr': True},
    'LrB#': {'nombre': 'LrB - Root zone percolation crop B', 'unid': 'm3/season/m2',
             'ingr': False, 'egr': True},
    'LrU#': {'nombre': 'LrU - Root zone percolation nonirrigated', 'unid': 'm3/season/m2',
             'ingr': False, 'egr': True},
    'LrT#': {'nombre': 'LrT - Total root zone percolation', 'unid': 'm3/season/m2',
             'ingr': False, 'egr': True},
    'RrA#': {'nombre': 'RrA - Capillary rise crop A', 'unid': 'm3/season/m2', 'ingr': False,
             'egr': True},
    'RrB#': {'nombre': 'RrB - Capillary rise crop B', 'unid': 'm3/season/m2', 'ingr': False,
             'egr': True},
    'RrU#': {'nombre': 'RrU - Capillary rise non-irrigated', 'unid': 'm3/season/m2',
             'ingr': False, 'egr': True},
    'RrT#': {'nombre': 'RrT - Total capillary rise', 'unid': 'm3/season/m2', 'ingr': False,
             'egr': True},
    'Gti#': {'nombre': 'Gti - Trans zone horizontal incoming groundwater',
             'unid': 'm3/season/m2', 'ingr': False, 'egr': True},
    'Gto#': {'nombre': 'Gto - Trans zone horizontal outgoing groundwater',
             'unid': 'm3/season/m2', 'ingr': False, 'egr': True},
    'Qv#': {'nombre': 'Qv - Net vertical water table recharge', 'unid': 'm', 'ingr': False,
            'egr': True},
    'Gqi#': {'nombre': 'Gqi - Aquifer horizontal incoming groundwater', 'unid': 'm3/season/m2',
             'ingr': False, 'egr': True},
    'Gqo#': {'nombre': 'Gqo - Aquifer horizontal outgoing groundwater', 'unid': 'm3/season/m2',
             'ingr': False, 'egr': True},
    'Gaq#': {'nombre': 'Gaq - Net aquifer horizontal flow', 'unid': 'm3/season/m2',
             'ingr': False, 'egr': True},
    'Gnt#': {'nombre': 'Gnt - Net horizontal groundwater flow', 'unid': 'm3/season/m2',
             'ingr': False, 'egr': True},
    'Gd#': {'nombre': 'Gd - Total subsurface drainage', 'unid': 'm3/season/m2', 'ingr': False,
            'egr': True},
    'Ga#': {'nombre': 'Ga - Subsurface drainage above drains', 'unid': 'm3/season/m2',
            'ingr': False, 'egr': True},
    'Gb#': {'nombre': 'Gb - Subsurface drainage below drains', 'unid': 'm3/season/m2',
            'ingr': False, 'egr': True},
    'Dw#': {'nombre': 'Dw - Groundwater depth', 'unid': 'm', 'ingr': False, 'egr': True},
    'Hw#': {'nombre': 'Hw - Water table elevation', 'unid': 'm', 'ingr': True, 'egr': True},
    'Hq#': {'nombre': 'Hq - Subsoil hydraulic head', 'unid': 'm', 'ingr': False, 'egr': True},
    'Sto#': {'nombre': 'Sto - Water table storage', 'unid': 'm', 'ingr': False, 'egr': True},
    'Zs#': {'nombre': 'Zs - Surface water salt', 'unid': 'm*dS/m', 'ingr': False, 'egr': True},
    'A#': {'nombre': 'Area A - Seasonal fraction area crop A', 'unid': 'Dmnl', 'ingr': True,
           'egr': True},
    'B#': {'nombre': 'Area B - Seasonal fraction area crop B', 'unid': 'Dmnl', 'ingr': True,
           'egr': True},
    'U#': {'nombre': 'Area U - Seasonal fraction area nonirrigated', 'unid': 'Dmnl',
           'ingr': False, 'egr': True},
    'Uc#': {'nombre': 'Uc - Fraction permanently non-irrigated', 'unid': 'Dmnl', 'ingr': False,
            'egr': True},
    'CrA#': {'nombre': 'CrA - Root zone salinity crop A', 'unid': 'dS / m', 'ingr': True,
             'egr': True},
    'CrB#': {'nombre': 'CrB - Root zone salinity crop B', 'unid': 'dS / m', 'ingr': True,
             'egr': True},
    'CrU#': {'nombre': 'CrU - Root zone salinity non-irrigated', 'unid': 'dS / m', 'ingr': True,
             'egr': True},
    'Cr4#': {'nombre': 'Cr4 - Fully rotated land irrigated root zone salinity',
             'unid': 'dS / m', 'ingr': False, 'egr': True},
    'C1*#': {'nombre': 'C1 - Key 1 non-permanently irrigated root zone salinity',
             'unid': 'dS / m', 'ingr': False, 'egr': True},
    'C2*#': {'nombre': 'C2 - Key 2 non-permanently irrigated root zone salinity',
             'unid': 'dS / m', 'ingr': False, 'egr': True},
    'C3*#': {'nombre': 'C3 - Key 3 non-permanently irrigated root zone salinity',
             'unid': 'dS / m', 'ingr': False, 'egr': True},
    'Cxf#': {'nombre': 'Cxf - Transition zone salinity', 'unid': 'dS / m', 'ingr': True,
             'egr': True},
    'Cxa#': {'nombre': 'Cxa - Transition zone above-drain salinity', 'unid': 'dS / m',
             'ingr': True, 'egr': True},
    'Cxb#': {'nombre': 'Cxb - Transition zone below-drain salinity', 'unid': 'dS / m',
             'ingr': True, 'egr': True},
    'Cti#': {'nombre': 'Cti - Transition zone incoming salinity', 'unid': 'dS / m',
             'ingr': False, 'egr': True},
    'Cqf#': {'nombre': 'Cqf - Aquifer salinity', 'unid': 'dS / m', 'ingr': True, 'egr': True},
    'Cd#': {'nombre': 'Cd - Drainage salinity', 'unid': 'ds / m', 'ingr': False, 'egr': True},
    'Cw#': {'nombre': 'Cw - Well water salinity', 'unid': 'ds / m', 'ingr': False, 'egr': True}
}
