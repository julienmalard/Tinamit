import os
import unittest

import pandas as pd
from tinamit.calibs.mod import CalibradorModSpotPy
from tinamit.calibs.valid import ValidadorMod
from tinamit.datos.bd import BD
from tinamit.datos.fuente import FuenteDic
from tinamit.envolt.mds import gen_mds
from tinamit.geog.simul import SimuladorGeog, CalibradorGeog, ValidadorGeog

dir_act = os.path.split(__file__)[0]
arch_mds = os.path.join(dir_act, 'recursos/mds/mod_enferm.mdl')
arch_csv_geog = os.path.join(dir_act, 'recursos/datos/prueba_geog.csv')

líms_paráms = {
    'taza de contacto': (0, 100),
    'taza de infección': (0, 0.02),
    'número inicial infectado': (0, 50),
    'taza de recuperación': (0, 0.1)
}


class TestCalibModelo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paráms = {
            'taza de contacto': 81.25,
            'taza de infección': 0.007,
            'número inicial infectado': 22.5,
            'taza de recuperación': 0.0375
        }
        cls.mod = gen_mds(arch_mds)

        simul = cls.mod.simular(
            t=100,
            vals_extern=cls.paráms,
            vars_interés=['Individuos Suceptibles', 'Individuos Infectados', 'Individuos Resistentes']
        )
        fchs = pd.date_range(0, periods=101)
        datos = {ll: v[:, 0] for ll, v in simul.a_dic().items()}  # Para hacer: dimensiones múltiples,
        datos['f'] = fchs
        cls.datos = FuenteDic(
            datos, 'Datos geográficos', lugares='lugar', fechas='f'
        )

    def test_calibrar_validar(símismo):
        calibs = CalibradorModSpotPy(símismo.mod).calibrar(
            líms_paráms=líms_paráms,
            datos=símismo.datos,
            n_iter=50
        )
        valid = ValidadorMod(símismo.mod).validar(
            t=100, datos=símismo.datos, paráms={prm: trz['mejor'] for prm, trz in calibs.items()}
        )
        símismo.assertGreater(valid['Individuos Suceptibles']['ens'], 0.95)


class TestCalibModeloEspacial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paráms = {
            '708': {
                'taza de contacto': 81.25, 'taza de infección': 0.007, 'número inicial infectado': 22.5,
                'taza de recuperación': 0.0375
            },
            '1010': {
                'taza de contacto': 50, 'taza de infección': 0.005, 'número inicial infectado': 40,
                'taza de recuperación': 0.050
            }
        }
        cls.mod = gen_mds(arch_mds)
        simul = SimuladorGeog(cls.mod).simular(
            t=100, vals_geog=cls.paráms,
            vars_interés=['Individuos Suceptibles', 'Individuos Infectados', 'Individuos Resistentes']
        )
        fchs = pd.date_range(0, periods=101)

        # Para hacer: dimensiones múltiples,
        datos = {lg: {'f': fchs, **{ll: v[:, 0] for ll, v in simul[lg].a_dic().items()}} for lg in cls.paráms}
        cls.datos = BD([
            FuenteDic(datos[lg], 'Datos geográficos', lugares=lg, fechas='f') for lg in cls.paráms
        ])

    def test_calib_valid_espacial(símismo):
        calib = CalibradorGeog(símismo.mod).calibrar(t=100, datos=símismo.datos, líms_paráms=líms_paráms, n_iter=50)
        valid = ValidadorGeog(símismo.mod).validar(
            t=100, datos=símismo.datos,
            paráms={lg: {prm: trz['mejor'] for prm, trz in calib[lg].items()} for lg in símismo.paráms}
        )

        for lg in símismo.paráms:
            símismo.assertTrue(valid[lg]['Individuos Suceptibles']['ens'], 0.95)
