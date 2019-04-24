import numpy as np

from tinamit.envolt.bf import VariablesModBloques, VarBloque
from tinamit.mod.var import Variable


class VarSAHYSMOD(Variable):
    def __init__(símismo, nombre, cód, unid, ingr, egr, inic, líms=None, info=''):
        símismo.cód = cód
        super().__init__(nombre, unid=unid, ingr=ingr, egr=egr, inic=inic, líms=líms, info=info)


class VarBloqSAHYSMOD(VarSAHYSMOD, VarBloque):
    pass


class VariablesSAHYSMOD(VariablesModBloques):
    def __init__(símismo, inic, tmñ_bloques):
        super().__init__(_vars_sahysmod(inic), tmñ_bloques=tmñ_bloques)

    def var_a_cód(símismo, var):
        return símismo[var].cód

    def cód_a_var(símismo, cód):
        return next(v for v in símismo if v.cód.strip('#') == cód.strip('#'))


def _vars_sahysmod(d_inic):
    n_polí = int(d_inic['NN_IN'])
    l_vars = []
    for cód, d in _info_vars.items():
        cls = d['cls']
        try:
            inic = d_inic[cód]
        except KeyError:
            inic = np.zeros(n_polí)

        var = cls(d['nombre'], cód=cód, unid=d['unid'], ingr=d['ingr'], egr=d['egr'], inic=inic)
        if isinstance(var, VarBloqSAHYSMOD):
            var.poner_vals_paso()
        l_vars.append(var)

    return l_vars


# Un diccionario de variables SAHYSMOD. Ver la documentación SAHYSMOD para más detalles.
_info_vars = {
    'Pp#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Pp - Rainfall', 'unid': 'm3/season/m2', 'ingr': True, 'egr': False},
    'Ci#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Ci - Incoming canal salinity', 'unid': 'dS/m', 'ingr': True,
            'egr': True},
    'Cinf': {'cls': VarSAHYSMOD, 'nombre': 'Cinf - Aquifer inflow salinity', 'unid': 'dS/m', 'ingr': True,
             'egr': False},
    'Dc': {'cls': VarSAHYSMOD, 'nombre': 'Dc - Capillary rise critical depth', 'unid': 'm', 'ingr': True, 'egr': False},
    'Dd': {'cls': VarSAHYSMOD, 'nombre': 'Dd - Subsurface drain depth', 'unid': 'm', 'ingr': True, 'egr': False},
    'Dr': {'cls': VarSAHYSMOD, 'nombre': 'Dr - Root zone thickness', 'unid': 'm', 'ingr': True, 'egr': False},
    'Dx': {'cls': VarSAHYSMOD, 'nombre': 'Dx - Transition zone thickness', 'unid': 'm', 'ingr': True, 'egr': False},
    'EpA#': {'cls': VarBloqSAHYSMOD, 'nombre': 'EpA - Potential ET crop A', 'unid': 'm3/season/m2', 'ingr': True,
             'egr': False},
    'EpB#': {'cls': VarBloqSAHYSMOD, 'nombre': 'EpB - Potential ET crop B', 'unid': 'm3/season/m2', 'ingr': True,
             'egr': False},
    'EpU#': {'cls': VarBloqSAHYSMOD, 'nombre': 'EpU - Potential ET non-irrigated', 'unid': 'm3/season/m2', 'ingr': True,
             'egr': False},
    'Flq': {'cls': VarSAHYSMOD, 'nombre': 'Flq - Aquifer leaching efficienty', 'unid': 'Dmnl', 'ingr': True,
            'egr': False},
    'Flr': {'cls': VarSAHYSMOD, 'nombre': 'Flr - Root zone leaching efficiency', 'unid': 'Dmnl', 'ingr': True,
            'egr': False},
    'Flx': {'cls': VarSAHYSMOD, 'nombre': 'Flx - Transition zone leaching efficiency', 'unid': 'Dmnl', 'ingr': True,
            'egr': False},
    'Frd#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Frd - Drainage function reduction factor', 'unid': 'Dmnl', 'ingr': True,
             'egr': False},
    'FsA#': {'cls': VarBloqSAHYSMOD, 'nombre': 'FsA - Water storage efficiency crop A', 'unid': 'Dmnl', 'ingr': True,
             'egr': False},
    'FsB#': {'cls': VarBloqSAHYSMOD, 'nombre': 'FsB - Water storage efficiency crop B', 'unid': 'Dmnl', 'ingr': True,
             'egr': False},
    'FsU#': {'cls': VarBloqSAHYSMOD, 'nombre': 'FsU - Water storage efficiency non-irrigated', 'unid': 'Dmnl',
             'ingr': True, 'egr': False},
    'Fw#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Fw - Fraction well water to irrigation', 'unid': 'Dmnl', 'ingr': True,
            'egr': False},
    'Gu#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Gu - Subsurface drainage for irrigation', 'unid': 'm3/season/m2',
            'ingr': True, 'egr': False},
    'Gw#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Gw - Groundwater extraction', 'unid': 'm3/season/m2', 'ingr': True,
            'egr': True},
    'Hc': {'cls': VarSAHYSMOD, 'nombre': 'Hp - Initial water level semi-confined', 'unid': 'm', 'ingr': True,
           'egr': False},
    'IaA#': {'cls': VarBloqSAHYSMOD, 'nombre': 'IaA - Crop A field irrigation', 'unid': 'm3/season/m2', 'ingr': True,
             'egr': True},
    'IaB#': {'cls': VarBloqSAHYSMOD, 'nombre': 'IaB - Crop B field irrigation', 'unid': 'm3/season/m2', 'ingr': True,
             'egr': True},
    'KcA#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Rice A - Crop A paddy?', 'unid': 'Dmnl', 'ingr': True, 'egr': False},
    'KcB#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Rice B - Crop B paddy?', 'unid': 'Dmnl', 'ingr': True, 'egr': False},
    'Kd': {'cls': VarSAHYSMOD, 'nombre': 'Kd - Subsurface drainage?', 'unid': 'Dmnl', 'ingr': True, 'egr': False},
    'Kf': {'cls': VarSAHYSMOD, 'nombre': 'Kf - Farmers\'s responses', 'unid': 'Dmnl', 'ingr': True, 'egr': False},
    'Kaq1': {'cls': VarSAHYSMOD, 'nombre': 'Kaq1 - Horizontal hydraulic conductivity 1', 'unid': 'm/day', 'ingr': True,
             'egr': False},
    'Kaq2': {'cls': VarSAHYSMOD, 'nombre': 'Kaq2 - Horizontal hydraulic conductivity 2', 'unid': 'm/day', 'ingr': True,
             'egr': False},
    'Kaq3': {'cls': VarSAHYSMOD, 'nombre': 'Kaq3 - Horizontal hydraulic conductivity 3', 'unid': 'm/day', 'ingr': True,
             'egr': False},
    'Kaq4': {'cls': VarSAHYSMOD, 'nombre': 'Kaq4 - Horizontal hydraulic conductivity 4', 'unid': 'm/day', 'ingr': True,
             'egr': False},
    'Ksc1': {'cls': VarSAHYSMOD, 'nombre': 'Ksc1 - Semi-confined aquifer 1?', 'unid': 'Dmnl', 'ingr': True,
             'egr': False},
    'Ksc2': {'cls': VarSAHYSMOD, 'nombre': 'Ksc2 - Semi-confined aquifer 2?', 'unid': 'Dmnl', 'ingr': True,
             'egr': False},
    'Ksc3': {'cls': VarSAHYSMOD, 'nombre': 'Ksc3 - Semi-confined aquifer 3?', 'unid': 'Dmnl', 'ingr': True,
             'egr': False},
    'Ksc4': {'cls': VarSAHYSMOD, 'nombre': 'Ksc4 - Semi-confined aquifer 4?', 'unid': 'Dmnl', 'ingr': True,
             'egr': False},
    'Kr#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Kr - Land use key', 'unid': 'Dmnl', 'ingr': True, 'egr': True},
    'Kvert': {'cls': VarSAHYSMOD, 'nombre': 'Kvert - Vertical hydraulic conductivity semi-confined', 'unid': 'm/day',
              'ingr': True, 'egr': False},
    'Lc#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Lc - Canal percolation', 'unid': 'm3/season/m2', 'ingr': True,
            'egr': False},
    'Peq': {'cls': VarSAHYSMOD, 'nombre': 'Peq - Aquifer effective porosity', 'unid': 'm/m', 'ingr': True,
            'egr': False},
    'Per': {'cls': VarSAHYSMOD, 'nombre': 'Per - Root zone effective porosity', 'unid': 'm/m', 'ingr': True,
            'egr': False},
    'Pex': {'cls': VarSAHYSMOD, 'nombre': 'Pex - Transition zone effective porosity', 'unid': 'm/m', 'ingr': True,
            'egr': False},
    'Psq': {'cls': VarSAHYSMOD, 'nombre': 'Psq - Semi-confined aquifer storativity', 'unid': 'Dmnl', 'ingr': True,
            'egr': False},
    'Ptq': {'cls': VarSAHYSMOD, 'nombre': 'Ptq - Aquifer total pore space', 'unid': 'm/m', 'ingr': True, 'egr': False},
    'Ptr': {'cls': VarSAHYSMOD, 'nombre': 'Ptr - Root zone total pore space', 'unid': 'm/m', 'ingr': True,
            'egr': False},
    'Ptx': {'cls': VarSAHYSMOD, 'nombre': 'Ptx - Transition zone total pore space', 'unid': 'm/m', 'ingr': True,
            'egr': False},
    'QH1': {'cls': VarSAHYSMOD, 'nombre': 'QH1 - Drain discharge to water table height ratio', 'unid': 'm/day/m',
            'ingr': True, 'egr': False},
    'QH2': {'cls': VarSAHYSMOD, 'nombre': 'QH2 - Drain discharge to sq. water table height ratio', 'unid': 'm/day/m2',
            'ingr': True, 'egr': False},
    'Qinf': {'cls': VarSAHYSMOD, 'nombre': 'Qinf - Aquifer inflow', 'unid': 'm3/season/m2', 'ingr': True, 'egr': False},
    'Qout': {'cls': VarSAHYSMOD, 'nombre': 'Qout - Aquifer outflow', 'unid': 'm3/season/m2', 'ingr': True,
             'egr': False},
    'SL': {'cls': VarSAHYSMOD, 'nombre': 'SL - Soil surface level', 'unid': 'm', 'ingr': True, 'egr': False},
    'SiU#': {'cls': VarBloqSAHYSMOD, 'nombre': 'SiU - Surface inflow to non-irrigated', 'unid': 'm3/season/m2',
             'ingr': True, 'egr': False},
    'SoA#': {'cls': VarBloqSAHYSMOD, 'nombre': 'SdA - Surface outflow crop A', 'unid': 'm3/season/m2', 'ingr': True,
             'egr': False},
    'SoB#': {'cls': VarBloqSAHYSMOD, 'nombre': 'SdB - Surface outflow crop B', 'unid': 'm3/season/m2', 'ingr': True,
             'egr': False},
    'SoU#': {'cls': VarBloqSAHYSMOD, 'nombre': 'SoU - Surface outflow non-irrigated', 'unid': 'm3/season/m2',
             'ingr': True, 'egr': False},
    'It#': {'cls': VarBloqSAHYSMOD, 'nombre': 'It - Total irrigation', 'unid': 'm3/season/m2', 'ingr': False,
            'egr': True},
    'Is#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Is - Canal irrigation', 'unid': 'm3/season/m2', 'ingr': False,
            'egr': True},
    'FfA#': {'cls': VarBloqSAHYSMOD, 'nombre': 'FfA - Irrigation efficiency crop A', 'unid': 'Dmnl', 'ingr': False,
             'egr': True},
    'FfB#': {'cls': VarBloqSAHYSMOD, 'nombre': 'FfB - Irrigation efficiency crop B', 'unid': 'Dmnl', 'ingr': False,
             'egr': True},
    'FfT#': {'cls': VarBloqSAHYSMOD, 'nombre': 'FfT - Total irrigation efficiency', 'unid': 'Dmnl', 'ingr': False,
             'egr': True},
    'Io#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Io - Water leaving by canal', 'unid': 'm3/season/m2', 'ingr': False,
            'egr': True},
    'JsA#': {'cls': VarBloqSAHYSMOD, 'nombre': 'JsA - Irrigation sufficiency crop A', 'unid': 'Dmnl', 'ingr': False,
             'egr': True},
    'JsB#': {'cls': VarBloqSAHYSMOD, 'nombre': 'JsB - Irrigation sufficiency crop B', 'unid': 'Dmnl', 'ingr': False,
             'egr': True},
    'EaU#': {'cls': VarBloqSAHYSMOD, 'nombre': 'EaU - Actual evapotranspiration nonirrigated', 'unid': 'm3/season/m2',
             'ingr': False, 'egr': True},
    'LrA#': {'cls': VarBloqSAHYSMOD, 'nombre': 'LrA - Root zone percolation crop A', 'unid': 'm3/season/m2',
             'ingr': False, 'egr': True},
    'LrB#': {'cls': VarBloqSAHYSMOD, 'nombre': 'LrB - Root zone percolation crop B', 'unid': 'm3/season/m2',
             'ingr': False, 'egr': True},
    'LrU#': {'cls': VarBloqSAHYSMOD, 'nombre': 'LrU - Root zone percolation nonirrigated', 'unid': 'm3/season/m2',
             'ingr': False, 'egr': True},
    'LrT#': {'cls': VarBloqSAHYSMOD, 'nombre': 'LrT - Total root zone percolation', 'unid': 'm3/season/m2',
             'ingr': False, 'egr': True},
    'RrA#': {'cls': VarBloqSAHYSMOD, 'nombre': 'RrA - Capillary rise crop A', 'unid': 'm3/season/m2', 'ingr': False,
             'egr': True},
    'RrB#': {'cls': VarBloqSAHYSMOD, 'nombre': 'RrB - Capillary rise crop B', 'unid': 'm3/season/m2', 'ingr': False,
             'egr': True},
    'RrU#': {'cls': VarBloqSAHYSMOD, 'nombre': 'RrU - Capillary rise non-irrigated', 'unid': 'm3/season/m2',
             'ingr': False, 'egr': True},
    'RrT#': {'cls': VarBloqSAHYSMOD, 'nombre': 'RrT - Total capillary rise', 'unid': 'm3/season/m2', 'ingr': False,
             'egr': True},
    'Gti#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Gti - Trans zone horizontal incoming groundwater',
             'unid': 'm3/season/m2', 'ingr': False, 'egr': True},
    'Gto#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Gto - Trans zone horizontal outgoing groundwater',
             'unid': 'm3/season/m2', 'ingr': False, 'egr': True},
    'Qv#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Qv - Net vertical water table recharge', 'unid': 'm', 'ingr': False,
            'egr': True},
    'Gqi#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Gqi - Aquifer horizontal incoming groundwater', 'unid': 'm3/season/m2',
             'ingr': False, 'egr': True},
    'Gqo#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Gqo - Aquifer horizontal outgoing groundwater', 'unid': 'm3/season/m2',
             'ingr': False, 'egr': True},
    'Gaq#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Gaq - Net aquifer horizontal flow', 'unid': 'm3/season/m2',
             'ingr': False, 'egr': True},
    'Gnt#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Gnt - Net horizontal groundwater flow', 'unid': 'm3/season/m2',
             'ingr': False, 'egr': True},
    'Gd#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Gd - Total subsurface drainage', 'unid': 'm3/season/m2', 'ingr': False,
            'egr': True},
    'Ga#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Ga - Subsurface drainage above drains', 'unid': 'm3/season/m2',
            'ingr': False, 'egr': True},
    'Gb#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Gb - Subsurface drainage below drains', 'unid': 'm3/season/m2',
            'ingr': False, 'egr': True},
    'Dw#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Dw - Groundwater depth', 'unid': 'm', 'ingr': False, 'egr': True},
    'Hw#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Hw - Water table elevation', 'unid': 'm', 'ingr': True, 'egr': True},
    'Hq#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Hq - Subsoil hydraulic head', 'unid': 'm', 'ingr': False, 'egr': True},
    'Sto#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Sto - Water table storage', 'unid': 'm', 'ingr': False, 'egr': True},
    'Zs#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Zs - Surface water salt', 'unid': 'm*dS/m', 'ingr': False, 'egr': True},
    'A#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Area A - Seasonal fraction area crop A', 'unid': 'Dmnl', 'ingr': True,
           'egr': True},
    'B#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Area B - Seasonal fraction area crop B', 'unid': 'Dmnl', 'ingr': True,
           'egr': True},
    'U#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Area U - Seasonal fraction area nonirrigated', 'unid': 'Dmnl',
           'ingr': False, 'egr': True},
    'Uc#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Uc - Fraction permanently non-irrigated', 'unid': 'Dmnl', 'ingr': False,
            'egr': True},
    'CrA#': {'cls': VarBloqSAHYSMOD, 'nombre': 'CrA - Root zone salinity crop A', 'unid': 'dS / m', 'ingr': True,
             'egr': True},
    'CrB#': {'cls': VarBloqSAHYSMOD, 'nombre': 'CrB - Root zone salinity crop B', 'unid': 'dS / m', 'ingr': True,
             'egr': True},
    'CrU#': {'cls': VarBloqSAHYSMOD, 'nombre': 'CrU - Root zone salinity non-irrigated', 'unid': 'dS / m', 'ingr': True,
             'egr': True},
    'Cr4#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Cr4 - Fully rotated land irrigated root zone salinity',
             'unid': 'dS / m', 'ingr': False, 'egr': True},
    'C1*#': {'cls': VarBloqSAHYSMOD, 'nombre': 'C1 - Key 1 non-permanently irrigated root zone salinity',
             'unid': 'dS / m', 'ingr': False, 'egr': True},
    'C2*#': {'cls': VarBloqSAHYSMOD, 'nombre': 'C2 - Key 2 non-permanently irrigated root zone salinity',
             'unid': 'dS / m', 'ingr': False, 'egr': True},
    'C3*#': {'cls': VarBloqSAHYSMOD, 'nombre': 'C3 - Key 3 non-permanently irrigated root zone salinity',
             'unid': 'dS / m', 'ingr': False, 'egr': True},
    'Cxf#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Cxf - Transition zone salinity', 'unid': 'dS / m', 'ingr': True,
             'egr': True},
    'Cxa#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Cxa - Transition zone above-drain salinity', 'unid': 'dS / m',
             'ingr': True, 'egr': True},
    'Cxb#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Cxb - Transition zone below-drain salinity', 'unid': 'dS / m',
             'ingr': True, 'egr': True},
    'Cti#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Cti - Transition zone incoming salinity', 'unid': 'dS / m',
             'ingr': False, 'egr': True},
    'Cqf#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Cqf - Aquifer salinity', 'unid': 'dS / m', 'ingr': True, 'egr': True},
    'Cd#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Cd - Drainage salinity', 'unid': 'ds / m', 'ingr': False, 'egr': True},
    'Cw#': {'cls': VarBloqSAHYSMOD, 'nombre': 'Cw - Well water salinity', 'unid': 'ds / m', 'ingr': False, 'egr': True}
}
