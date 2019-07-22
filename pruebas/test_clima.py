from unittest import TestCase

import numpy as np
import numpy.testing as npt
import pandas as pd
from pruebas.recursos.bf.variantes import EjDeterminado
from pruebas.recursos.mod.prueba_mod import ModeloPrueba
from tinamit.mod.clima import Clima
from tinamit.tiempo.tiempo import EspecTiempo
from تقدیر.ذرائع import جےسن


class TestClima(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.lluvia = np.random.random(366 + 365 + 365)
        cls.fechas = pd.date_range('2000-01-01', '2002-12-31')

        cls.clima = Clima(lat=31.569, long=74.355, elev=100, fuentes=جےسن(
            {'بارش': cls.lluvia, 'تاریخ': cls.fechas}, 31.569, 74.355, 100
        ))

    def test_diario(símismo):
        mod = ModeloPrueba(unid_tiempo='días')
        mod.conectar_var_clima('Vacío', 'بارش', conv=1, combin='total')

        res = mod.simular(EspecTiempo(100, f_inic=símismo.fechas[0]), clima=símismo.clima, vars_interés='Vacío')

        npt.assert_equal(res['Vacío'].vals[:, 0], símismo.lluvia[:101])

    def test_mensual(símismo):
        mod = ModeloPrueba(unid_tiempo='mes')
        mod.conectar_var_clima('Vacío', 'بارش', conv=1, combin='total')

        res = mod.simular(EspecTiempo(2, f_inic=símismo.fechas[0]), clima=símismo.clima, vars_interés='Vacío')

        ref = np.array([
            np.sum(x) for x in
            [símismo.lluvia[: 31], símismo.lluvia[31: 31 + 29], símismo.lluvia[31 + 29: 31 + 29 + 31]]
        ])
        npt.assert_equal(res['Vacío'].vals[:, 0], ref)

    def test_anual(símismo):
        mod = ModeloPrueba(unid_tiempo='año')
        mod.conectar_var_clima('Vacío', 'بارش', conv=1, combin='total')

        res = mod.simular(EspecTiempo(2, f_inic=símismo.fechas[0]), clima=símismo.clima, vars_interés='Vacío')

        ref = np.array([
            np.sum(x) for x in
            [símismo.lluvia[: 366], símismo.lluvia[366: 366 + 365], símismo.lluvia[366 + 365: 366 + 365 + 365]]
        ])
        npt.assert_equal(res['Vacío'].vals[:, 0], ref)


class TestClimaBFs(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.lluvia = np.random.random(366)
        cls.fechas = pd.date_range('2000-01-01', '2000-12-31')

        cls.clima = Clima(lat=31.569, long=74.355, elev=100, fuentes=جےسن(
            {'بارش': cls.lluvia, 'تاریخ': cls.fechas}, 31.569, 74.355, 100
        ))

    def test_deter(símismo):
        mod = EjDeterminado(tmñ_ciclo=30, unid_tiempo='días')
        mod.conectar_var_clima('ingreso_ciclo', 'بارش', conv=1, combin='total')
        mod.conectar_var_clima('ingreso', 'بارش', conv=1, combin='total')

        res = mod.simular(EspecTiempo(30*12-1, f_inic=símismo.fechas[0]), clima=símismo.clima)

        ref = np.repeat(np.array([
            np.sum(símismo.lluvia[x * 30:x * 30 + 30]) for x in range(0, 12)
        ]), 30)
        npt.assert_equal(res['ingreso_ciclo'].vals[:, 0], ref)

        npt.assert_equal(res['ingreso'].vals[:, 0], símismo.lluvia[:13])

    def test_bloques(símismo):
        raise NotImplementedError
