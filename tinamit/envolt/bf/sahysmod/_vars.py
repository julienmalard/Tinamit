from tinamit.envolt.bf import VariablesModBloques, VarIngrBloque, VarEgrBloque, VarBloque
from tinamit.mod.var import Variable


class VarSAHYSMOD(Variable):
    def __init__(símismo, nombre, cód, unid, ingr, egr, líms=None, info=''):
        símismo.cód = cód
        super().__init__(nombre, unid=unid, ingr=ingr, egr=egr, líms=líms, info=info)


class VarIngrBloqSAHYSMOD(VarSAHYSMOD, VarIngrBloque):
    pass


class VarEgrBloqSAHYSMOD(VarSAHYSMOD, VarEgrBloque):
    pass


class VarBloqSAHYSMOD(VarSAHYSMOD, VarBloque):
    pass


class VariablesSAHYSMOD(VariablesModBloques):
    def __init__(símismo):
        super().__init__(_vars_SAHYSMOD)

    def var_a_cód(símismo, var):
        return símismo[str(var)].cód

    def cód_a_var(símismo, cód):
        return next(v for v in símismo if v.cód == cód)


# Un diccionario de variables SAHYSMOD. Ver la documentación SAHYSMOD para más detalles.
_vars_SAHYSMOD = [
    VarBloqSAHYSMOD('Pp - Rainfall', cód='Pp#', unid='m3/season/m2', ingr=True, egr=False),
    VarBloqSAHYSMOD('Ci - Incoming canal salinity', cód='Ci#', unid='dS/m', ingr=True, egr=True),
    VarSAHYSMOD('Cinf - Aquifer inflow salinity', unid='dS/m', ingr=True, egr=False, cód='Cinf'),
    VarSAHYSMOD('Dc - Capillary rise critical depth', unid='m', ingr=True, egr=False, cód='Dc'),
    VarSAHYSMOD('Dd - Subsurface drain depth', cód='Dd', unid='m', ingr=True, egr=False),
    VarSAHYSMOD('Dr - Root zone thickness', cód='Dr', unid='m', ingr=True, egr=False),
    VarSAHYSMOD('Dx - Transition zone thickness', cód='Dx', unid='m', ingr=True, egr=False),
    VarBloqSAHYSMOD('EpA - Potential ET crop A', cód='EpA#', unid='m3/season/m2', ingr=True, egr=False),
    VarBloqSAHYSMOD('EpB - Potential ET crop B', cód='EpB#', unid='m3/season/m2', ingr=True, egr=False),
    VarBloqSAHYSMOD('EpU - Potential ET non-irrigated', cód='EpU#', unid='m3/season/m2', ingr=True, egr=False),
    VarSAHYSMOD('Flq - Aquifer leaching efficienty', cód='Flq', unid='Dmnl', ingr=True, egr=False),
    VarSAHYSMOD('Flr - Root zone leaching efficiency', cód='Flr', unid='Dmnl', ingr=True, egr=False),
    VarSAHYSMOD('Flx - Transition zone leaching efficiency', cód='Flx', unid='Dmnl', ingr=True, egr=False),
    VarBloqSAHYSMOD('Frd - Drainage function reduction factor', cód='Frd#', unid='Dmnl', ingr=True, egr=False),
    VarBloqSAHYSMOD('FsA - Water storage efficiency crop A', cód='FsA#', unid='Dmnl', ingr=True, egr=False),
    VarBloqSAHYSMOD('FsB - Water storage efficiency crop B', cód='FsB#', unid='Dmnl', ingr=True, egr=False),
    VarBloqSAHYSMOD('FsU - Water storage efficiency non-irrigated', cód='FsU#', unid='Dmnl', ingr=True, egr=False),
    VarBloqSAHYSMOD('Fw - Fraction well water to irrigation', cód='Fw#', unid='Dmnl', ingr=True, egr=False),
    VarBloqSAHYSMOD('Gu - Subsurface drainage for irrigation', cód='Gu#', unid='m3/season/m2', ingr=True, egr=False),
    VarBloqSAHYSMOD('Gw - Groundwater extraction', cód='Gw#', unid='m3/season/m2', ingr=True, egr=True),
    VarSAHYSMOD('Hp - Initial water level semi-confined', cód='Hc', unid='m', ingr=True, egr=False),
    VarBloqSAHYSMOD('IaA - Crop A field irrigation', cód='IaA#', unid='m3/season/m2', ingr=True, egr=True),
    VarBloqSAHYSMOD('IaB - Crop B field irrigation', cód='IaB#', unid='m3/season/m2', ingr=True, egr=True),
    VarBloqSAHYSMOD('Rice A - Crop A paddy?', cód='KcA#', unid='Dmnl', ingr=True, egr=False),
    VarBloqSAHYSMOD('Rice B - Crop B paddy?', cód='KcB#', unid='Dmnl', ingr=True, egr=False),
    VarSAHYSMOD('Kd - Subsurface drainage?', cód='Kd', unid='Dmnl', ingr=True, egr=False),
    VarSAHYSMOD('Kf - Farmers\'s responses?', cód='Kf', unid='Dmnl', ingr=True, egr=False),
    VarSAHYSMOD('Kaq1 - Horizontal hydraulic conductivity 1', cód='Kaq1', unid='m/day', ingr=True, egr=False),
    VarSAHYSMOD('Kaq2 - Horizontal hydraulic conductivity 2', cód='Kaq2', unid='m/day', ingr=True, egr=False),
    VarSAHYSMOD('Kaq3 - Horizontal hydraulic conductivity 3', cód='Kaq3', unid='m/day', ingr=True, egr=False),
    VarSAHYSMOD('Kaq4 - Horizontal hydraulic conductivity 4', cód='Kaq4', unid='m/day', ingr=True, egr=False),
    VarSAHYSMOD('Ksc1 - Semi-confined aquifer 1?', cód='Ksc1', unid='Dmnl', ingr=True, egr=False),
    VarSAHYSMOD('Ksc2 - Semi-confined aquifer 2?', cód='Ksc2', unid='Dmnl', ingr=True, egr=False),
    VarSAHYSMOD('Ksc3 - Semi-confined aquifer 3?', cód='Ksc3', unid='Dmnl', ingr=True, egr=False),
    VarSAHYSMOD('Ksc4 - Semi-confined aquifer 4?', cód='Ksc4', unid='Dmnl', ingr=True, egr=False),
    VarIngrBloqSAHYSMOD('Kr - Land use key', cód='Kr#', unid='Dmnl', ingr=True, egr=True),
    VarSAHYSMOD('Kvert - Vertical hydraulic conductivity semi-confined', cód='Kvert', unid='m/day', ingr=True,
                egr=False),
    VarBloqSAHYSMOD('Lc - Canal percolation', cód='Lc#', unid='m3/season/m2', ingr=True, egr=False),
    VarSAHYSMOD('Peq - Aquifer effective porosity', cód='Peq', unid='m/m', ingr=True, egr=False),
    VarSAHYSMOD('Per - Root zone effective porosity', cód='Per', unid='m/m', ingr=True, egr=False),
    VarSAHYSMOD('Pex - Transition zone effective porosity', cód='Pex', unid='m/m', ingr=True, egr=False),
    VarSAHYSMOD('Psq - Semi-confined aquifer storativity', cód='Psq', unid='Dmnl', ingr=True, egr=False),
    VarSAHYSMOD('Ptq - Aquifer total pore space', cód='Ptq', unid='m/m', ingr=True, egr=False),
    VarSAHYSMOD('Ptr - Root zone total pore space', cód='Ptr', unid='m/m', ingr=True, egr=False),
    VarSAHYSMOD('Ptx - Transition zone total pore space', cód='Ptx', unid='m/m', ingr=True, egr=False),
    VarSAHYSMOD('QH1 - Drain discharge to water table height ratio', cód='QH1', unid='m/day/m', ingr=True, egr=False),
    VarSAHYSMOD('QH2 - Drain discharge to sq. water table height ratio', cód='QH2', unid='m/day/m2', ingr=True,
                egr=False),
    VarSAHYSMOD('Qinf - Aquifer inflow', cód='Qinf', unid='m3/season/m2', ingr=True, egr=False),
    VarSAHYSMOD('Qout - Aquifer outflow', cód='Qout', unid='m3/season/m2', ingr=True, egr=False),
    VarSAHYSMOD('SL - Soil surface level', cód='SL', unid='m', ingr=True, egr=False),
    VarBloqSAHYSMOD('SiU - Surface inflow to non-irrigated', cód='SiU#', unid='m3/season/m2', ingr=True, egr=False),
    VarBloqSAHYSMOD('SdA - Surface outflow crop A', cód='SoA#', unid='m3/season/m2', ingr=True, egr=False),
    VarBloqSAHYSMOD('SdB - Surface outflow crop B', cód='SoB#', unid='m3/season/m2', ingr=True, egr=False),
    VarBloqSAHYSMOD('SoU - Surface outflow non-irrigated', cód='SoU#', unid='m3/season/m2', ingr=True, egr=False),
    VarBloqSAHYSMOD('It - Total irrigation', cód='It#', unid='m3/season/m2', ingr=False, egr=True),
    VarBloqSAHYSMOD('Is - Canal irrigation', cód='Is#', unid='m3/season/m2', ingr=False, egr=True),
    VarBloqSAHYSMOD('FfA - Irrigation efficiency crop A', cód='FfA#', unid='Dmnl', ingr=False, egr=True),
    VarBloqSAHYSMOD('FfB - Irrigation efficiency crop B', cód='FfB#', unid='Dmnl', ingr=False, egr=True),
    VarBloqSAHYSMOD('FfT - Total irrigation efficiency', cód='FfT#', unid='Dmnl', ingr=False, egr=True),
    VarBloqSAHYSMOD('Io - Water leaving by canal', cód='Io#', unid='m3/season/m2', ingr=False, egr=True),
    VarBloqSAHYSMOD('JsA - Irrigation sufficiency crop A', cód='JsA#', unid='Dmnl', ingr=False, egr=True),
    VarBloqSAHYSMOD('JsB - Irrigation sufficiency crop B', cód='JsB#', unid='Dmnl', ingr=False, egr=True),
    VarBloqSAHYSMOD('EaU - Actual evapotranspiration nonirrigated', cód='EaU#', unid='m3/season/m2', ingr=False,
                    egr=True),
    VarBloqSAHYSMOD('LrA - Root zone percolation crop A', cód='LrA#', unid='m3/season/m2', ingr=False, egr=True),
    VarBloqSAHYSMOD('LrB - Root zone percolation crop B', cód='LrB#', unid='m3/season/m2', ingr=False, egr=True),
    VarBloqSAHYSMOD('LrU - Root zone percolation nonirrigated', cód='LrU#', unid='m3/season/m2', ingr=False, egr=True),
    VarBloqSAHYSMOD('LrT - Total root zone percolation', cód='LrT#', unid='m3/season/m2', ingr=False, egr=True),
    VarBloqSAHYSMOD('RrA - Capillary rise crop A', cód='RrA#', unid='m3/season/m2', ingr=False, egr=True),
    VarBloqSAHYSMOD('RrB - Capillary rise crop B', cód='RrB#', unid='m3/season/m2', ingr=False, egr=True),
    VarBloqSAHYSMOD('RrU - Capillary rise non-irrigated', cód='RrU#', unid='m3/season/m2', ingr=False, egr=True),
    VarBloqSAHYSMOD('RrT - Total capillary rise', cód='RrT#', unid='m3/season/m2', ingr=False, egr=True),
    VarBloqSAHYSMOD('Gti - Trans zone horizontal incoming groundwater', cód='Gti#', unid='m3/season/m2', ingr=False,
                    egr=True),
    VarBloqSAHYSMOD('Gto - Trans zone horizontal outgoing groundwater', cód='Gto#', unid='m3/season/m2', ingr=False,
                    egr=True),
    VarBloqSAHYSMOD('Qv - Net vertical water table recharge', cód='Qv#', unid='m', ingr=False, egr=True),
    VarBloqSAHYSMOD('Gqi - Aquifer horizontal incoming groundwater', cód='Gqi#', unid='m3/season/m2', ingr=False,
                    egr=True),
    VarBloqSAHYSMOD('Gqo - Aquifer horizontal outgoing groundwater', cód='Gqo#', unid='m3/season/m2', ingr=False,
                    egr=True),
    VarBloqSAHYSMOD('Gaq - Net aquifer horizontal flow', cód='Gaq#', unid='m3/season/m2', ingr=False, egr=True),
    VarBloqSAHYSMOD('Gnt - Net horizontal groundwater flow', cód='Gnt#', unid='m3/season/m2', ingr=False, egr=True),
    VarBloqSAHYSMOD('Gd - Total subsurface drainage', cód='Gd#', unid='m3/season/m2', ingr=False, egr=True),
    VarBloqSAHYSMOD('Ga - Subsurface drainage above drains', cód='Ga#', unid='m3/season/m2', ingr=False, egr=True),
    VarBloqSAHYSMOD('Gb - Subsurface drainage below drains', cód='Gb#', unid='m3/season/m2', ingr=False, egr=True),
    VarBloqSAHYSMOD('Dw - Groundwater depth', cód='Dw#', unid='m', ingr=False, egr=True),
    VarIngrBloqSAHYSMOD('Hw - Water table elevation', cód='Hw#', unid='m', ingr=True, egr=True),
    VarBloqSAHYSMOD('Hq - Subsoil hydraulic head', cód='Hq#', unid='m', ingr=False, egr=True),
    VarBloqSAHYSMOD('Sto - Water table storage', cód='Sto#', unid='m', ingr=False, egr=True),
    VarBloqSAHYSMOD('Zs - Surface water salt', cód='Zs#', unid='m*dS/m', ingr=False, egr=True),
    VarBloqSAHYSMOD('Area A - Seasonal fraction area crop A', cód='A#', unid='Dmnl', ingr=True, egr=True),
    VarBloqSAHYSMOD('Area B - Seasonal fraction area crop B', cód='B#', unid='Dmnl', ingr=True, egr=True),
    VarBloqSAHYSMOD('Area U - Seasonal fraction area nonirrigated', cód='U#', unid='Dmnl', ingr=False, egr=True),
    VarBloqSAHYSMOD('Uc - Fraction permanently non-irrigated', cód='Uc#', unid='Dmnl', ingr=False, egr=True),
    VarIngrBloqSAHYSMOD('CrA - Root zone salinity crop A', cód='CrA#', unid='dS / m', ingr=True, egr=True),
    VarIngrBloqSAHYSMOD('CrB - Root zone salinity crop B', cód='CrB#', unid='dS / m', ingr=True, egr=True),
    VarIngrBloqSAHYSMOD('CrU - Root zone salinity non-irrigated', cód='CrU#', unid='dS / m', ingr=True, egr=True),
    VarIngrBloqSAHYSMOD('Cr4 - Fully rotated land irrigated root zone salinity', cód='Cr4#', unid='dS / m', ingr=False,
                        egr=True),
    VarIngrBloqSAHYSMOD('C1 - Key 1 non-permanently irrigated root zone salinity', cód='C1*#', unid='dS / m',
                        ingr=False,
                        egr=True),
    VarIngrBloqSAHYSMOD('C2 - Key 2 non-permanently irrigated root zone salinity', cód='C2*#', unid='dS / m',
                        ingr=False,
                        egr=True),
    VarIngrBloqSAHYSMOD('C3 - Key 3 non-permanently irrigated root zone salinity', cód='C3*#', unid='dS / m',
                        ingr=False,
                        egr=True),
    VarIngrBloqSAHYSMOD('Cxf - Transition zone salinity', cód='Cxf#', unid='dS / m', ingr=True, egr=True),
    VarIngrBloqSAHYSMOD('Cxa - Transition zone above-drain salinity', cód='Cxa#', unid='dS / m', ingr=True, egr=True),
    VarIngrBloqSAHYSMOD('Cxb - Transition zone below-drain salinity', cód='Cxb#', unid='dS / m', ingr=True, egr=True),
    VarBloqSAHYSMOD('Cti - Transition zone incoming salinity', cód='Cti#', unid='dS / m', ingr=False, egr=True),
    VarIngrBloqSAHYSMOD('Cqf - Aquifer salinity', cód='Cqf#', unid='dS / m', ingr=True, egr=True),
    VarBloqSAHYSMOD('Cd - Drainage salinity', cód='Cd#', unid='ds / m', ingr=False, egr=True),
    VarBloqSAHYSMOD('Cw - Well water salinity', cód='Cw#', unid='ds / m', ingr=False, egr=True),
]
