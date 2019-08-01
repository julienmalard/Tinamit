from unittest import TestCase

import numpy as np
import numpy.testing as npt
import pandas as pd

from pruebas.recursos.bf.variantes import EjDeterminado, EjBloques
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
        cls.lluvia = np.random.random(366 + 365)
        cls.fechas = pd.date_range('2000-01-01', '2001-12-31')

        cls.clima = Clima(lat=31.569, long=74.355, elev=100, fuentes=جےسن(
            {'بارش': cls.lluvia, 'تاریخ': cls.fechas}, 31.569, 74.355, 100
        ))

    def test_deter(símismo):
        mod = EjDeterminado(tmñ_ciclo=30, unid_tiempo='días')
        mod.conectar_var_clima('ingreso_ciclo', 'بارش', conv=1, combin='total')
        mod.conectar_var_clima('ingreso_paso', 'بارش', conv=1, combin='total')

        ref_paso = símismo.lluvia[:360]
        ref_ciclo = np.repeat(np.array([
            np.sum(símismo.lluvia[x * 30:x * 30 + 30]) for x in range(12)
        ]), 30)

        pruebas = {
            'ingreso_ciclo': ref_ciclo,
            'ingreso_paso': ref_paso
        }

        res = mod.simular(EspecTiempo(30 * 12 - 1, f_inic=símismo.fechas[0]), clima=símismo.clima)

        for prb, ref in pruebas.items():
            if prb == 'ingreso_paso':
                continue
            with símismo.subTest(prb):
                npt.assert_equal(res[prb].vals[:, 0].values, ref)

    def test_bloques(símismo):
        tmñ_bloques = [4, 5, 3]
        mod = EjBloques(tmñ_bloques=tmñ_bloques, unid_tiempo='meses')
        mod.conectar_var_clima('ingreso_paso', 'بارش', conv=1, combin='total')
        mod.conectar_var_clima('ingreso_bloque', 'بارش', conv=1, combin='total')
        mod.conectar_var_clima('ingreso_ciclo', 'بارش', conv=1, combin='total')

        n_días = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        sum_cum = np.cumsum(np.append([0], n_días))
        ref_paso = np.array([
            np.sum(símismo.lluvia[sum_cum[x]:sum_cum[x + 1]]) for x in range(24)
        ])

        sum_cum_bloq = np.cumsum(np.append([0], np.tile(tmñ_bloques, 2)))
        ref_bloques = np.repeat(np.array([
            np.sum(símismo.lluvia[sum_cum[sum_cum_bloq[i]]: sum_cum[sum_cum_bloq[i + 1]]])
            for i in range(len(sum_cum_bloq) - 1)
        ]), np.tile(tmñ_bloques, 2))

        ref_ciclo = np.empty(24)
        ref_ciclo[:12] = np.sum(símismo.lluvia[:np.sum(n_días[:12])])
        ref_ciclo[12:] = np.sum(símismo.lluvia[np.sum(n_días[:12]):])

        pruebas = {
            'ingreso_ciclo': ref_ciclo,
            'ingreso_paso': ref_paso,
            'ingreso_bloque': ref_bloques
        }

        res = mod.simular(EspecTiempo(23, f_inic=símismo.fechas[0]), clima=símismo.clima)
        for prb, ref in pruebas.items():
            if prb in ['ingreso_paso', 'ingreso_bloque']:
                continue
            with símismo.subTest(prb):
                npt.assert_equal(res[prb].vals[:, 0].values, ref)
