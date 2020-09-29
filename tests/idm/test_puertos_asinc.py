import os
import sys
from subprocess import Popen
from unittest import TestCase

import numpy.testing as npt

from tinamit.idm.puertos_asinc import IDMEnchufesAsinc
from .ejemplo_cliente import datos

t_final = 15


class PruebaIDM(TestCase):

    def setUp(símismo):
        símismo.clientes = []

    def _empezar_cliente(símismo, dirección, puerto):
        DIR_BASE = os.path.split(__file__)[0]
        arch_cliente = os.path.join(DIR_BASE, "ejemplo_cliente.py")
        cliente = Popen([sys.executable, arch_cliente, dirección, str(puerto), str(t_final)])

        símismo.clientes.append(cliente)
        return cliente

    async def test_abrir_cerrar(símismo):
        async with IDMEnchufesAsinc() as servidor:
            await servidor.conectar()
            símismo._empezar_cliente(servidor.dirección, servidor.puerto)
            await servidor.activar()
            await servidor.cerrar()

    async def test_mandar_datos(símismo):
        async with IDMEnchufesAsinc() as servidor:
            await servidor.conectar()
            símismo._empezar_cliente(servidor.dirección, servidor.puerto)
            await servidor.activar()

            for nmbr_dts, dts in datos.items():
                with símismo.subTest(datos=nmbr_dts):
                    await servidor.cambiar('var', dts)

                    recibido = await servidor.recibir('var')
                    npt.assert_equal(dts, recibido)

    async def test_recibir_datos(símismo):
        async with IDMEnchufesAsinc() as servidor:
            await servidor.conectar()
            símismo._empezar_cliente(servidor.dirección, servidor.puerto)
            await servidor.activar()

            for nmbr_dts, dts in datos.items():
                with símismo.subTest(datos=nmbr_dts):
                    recibido = await servidor.recibir(nmbr_dts)
                    npt.assert_equal(dts, recibido)

    async def test_incrementar(símismo):
        n_pasos = 5
        async with IDMEnchufesAsinc() as servidor:
            await servidor.conectar()
            símismo._empezar_cliente(servidor.dirección, servidor.puerto)
            await servidor.activar()
            await servidor.incrementar(n_pasos)

            t = await servidor.recibir('t')
            símismo.assertEqual(t, n_pasos)

    async def test_finalizar(símismo):
        async with IDMEnchufesAsinc() as servidor:
            await servidor.conectar()
            símismo._empezar_cliente(servidor.dirección, servidor.puerto)
            await servidor.activar()
            await servidor.finalizar()

            t = await servidor.recibir('t')
            símismo.assertEqual(t, t_final)

    def tearDown(símismo):
        for cliente in símismo.clientes:
            cliente.wait()
