import sys
from itertools import product
from subprocess import Popen
from unittest import TestCase

import numpy.testing as npt

from pruebas3.ejemplo_cliente import datos
from tinamit3.idm.er import IDMEnchufesRed
from tinamit3.idm.puertos import IDMEnchufes

sistemas = {
    'puertos': IDMEnchufes,
#    'er': IDMEnchufesRed
}
t_final = 15


class PruebaIDM(TestCase):

    def setUp(símismo):
        símismo.clientes = []

    def _empezar_cliente(símismo, tipo, dirección, puerto):
        cliente= Popen([sys.executable, "ejemplo_cliente.py", tipo, dirección, str(puerto), str(t_final)])
        símismo.clientes.append(cliente)
        return cliente

    def test_abrir_cerrar(símismo):
        for nmbr_sstm, sstm in sistemas.items():
            with símismo.subTest(nmbr_sstm), sstm() as servidor:
                símismo._empezar_cliente(nmbr_sstm, servidor.dirección, servidor.puerto)
                servidor.activar()
                servidor.cerrar()

    def test_mandar_datos(símismo):
        for nmbr_sstm, nmbr_dts in product(sistemas, datos):
            sstm = sistemas[nmbr_sstm]
            dts = datos[nmbr_dts]
            with símismo.subTest(sistema=nmbr_sstm, datos=nmbr_dts), sstm() as servidor:
                símismo._empezar_cliente(nmbr_sstm, servidor.dirección, servidor.puerto)
                servidor.activar()

                servidor.mandar('var', dts)

                recibido = servidor.recibir('var')
                npt.assert_equal(dts, recibido)

    def test_recibir_datos(símismo):
        for nmbr_sstm, nmbr_dts in product(sistemas, datos):
            sstm = sistemas[nmbr_sstm]
            dts = datos[nmbr_dts]
            with símismo.subTest(sistema=nmbr_sstm, datos=nmbr_dts), sstm() as servidor:
                símismo._empezar_cliente(nmbr_sstm, servidor.dirección, servidor.puerto)
                servidor.activar()

                recibido = servidor.recibir(nmbr_dts)
                npt.assert_equal(dts, recibido)

    def test_incrementar(símismo):
        for nmbr_sstm, sstm in sistemas.items():
            n_pasos = 5
            with símismo.subTest(nmbr_sstm), sstm() as servidor:
                símismo._empezar_cliente(nmbr_sstm, servidor.dirección, servidor.puerto)
                servidor.activar()
                servidor.incrementar(n_pasos)

                t = servidor.recibir('t')
                símismo.assertEqual(t, n_pasos)

    def test_finalizar(símismo):
        for nmbr_sstm, sstm in sistemas.items():
            with símismo.subTest(nmbr_sstm), sstm() as servidor:
                símismo._empezar_cliente(nmbr_sstm, servidor.dirección, servidor.puerto)
                servidor.activar()

                servidor.finalizar()

                t = servidor.recibir('t')
                símismo.assertEqual(t, t_final)

    def tearDown(símismo):
        for cliente in símismo.clientes:
            cliente.wait()
