import unittest

import tinamit.Unidades.trads as trads
from tinamit.Unidades.conv import convertir


class Test_ConvertirUnidades(unittest.TestCase):
    """
    Comprobar la conversión de unidades.
    """

    def test_convertir_unids_equivalentes(símismo):
        # Unidades equivalentes deberían dar un factor de conversión de 1.
        símismo.assertEqual(convertir('m2/d', 'm3/d/m'), 1)

    def test_convertir_unids_iguales(símismo):
        # Unidades idénticas deberían dar un factor de conversión de 1.
        símismo.assertEqual(convertir('colibrís', 'colibrís'), 1)

    def test_convertir_con_traducción_necesaria(símismo):
        # Registrar traducciones
        trads.agregar_trad('pound', trad='paj', leng_trad='cak', guardar=False)
        trads.agregar_trad('paj', trad='libra', leng_trad='es', leng_orig='cak', guardar=False)
        de = 'paj'
        a = 'libras'

        # Deberían ser igual ahora.
        símismo.assertEqual(convertir(de, a), 1)

    def test_convertir_con_traducción_desconocida(símismo):
        # Aunque no sepa lo que es una "estación", el programa debería detectar que es lo mismo en ambos y solamente
        # convertir los m3 a cm3.
        símismo.assertAlmostEqual(convertir('m3/estación', 'cm3/estación'), 100 ** 3)

    def test_convertir_con_valor(símismo):
        # Comprobar conversión real.
        símismo.assertEqual(convertir('km', 'm', val=2), 2000)

    def test_conversión_imposible(símismo):
        # ¡Comparemos bananas con naranjas!
        símismo.assertRaises(ValueError, lambda: convertir('bananas', 'naranjas'))

        # Y un error de dimensionalidad.
        símismo.assertRaises(ValueError, lambda: convertir('m3', 'm2'))


class Test_TradsUnidades(unittest.TestCase):
    """
    Pruebas de funciones de traducción de unidades.
    """

    def test_agregar_sinónimo(símismo):
        """
        Comprobar que podemos agregar sinónimos de unidades.
        """

        trads.agregar_sinónimos(unid='foot', sinónimos='feet', leng='en', guardar=False)
        símismo.assertEqual(convertir(de='foot', a='feet'), 1)

    def test_agregar_sinónimo_listas(símismo):
        """
        Comprobar que podemos agregar sinónimos de unidades en formato de lista.
        """

        trads.agregar_sinónimos(unid='meter', sinónimos=['metre', 'm'], leng='en', guardar=False)
        símismo.assertEqual(convertir(de='metre', a='m'), 1)

    def test_agregar_trad(símismo):
        """
        Comprobar que podemos agregar traducciones de unidades.
        """

        trads.agregar_trad(unid='second', trad='پل', leng_orig='en', leng_trad='ur', guardar=False)
        símismo.assertEqual(convertir(de='second', a='پل'), 1)

    def test_agregar_trad_sin_especificar_leng(símismo):
        """
        Comprobar que podemos agregar traducciones de unidades sin especificar la lengua original de la unidad.
        """

        trads.agregar_trad(unid='second', trad='پل', leng_trad='ur', guardar=False)
        símismo.assertEqual(convertir(de='second', a='پل'), 1)

    def test_traducir_sinónimo_pint(símismo):
        """
        Comprobar que podemos traducir una unidad según su sinónimo Pint.
        """
        trads.agregar_trad('inch', trad='pulgado', leng_trad='es', guardar=False)
        símismo.assertEqual(trads.trad_unid('in', 'es'), 'pulgado')

    def test_agregar_trad_por_sinónimo_pint(símismo):
        """
        Comprobar que podemos agregar la traducción de una unidad según su sinónimo Pint.
        """

        trads.agregar_trad(unid='m', trad='mètre', leng_trad='fr', guardar=False)
        trads.agregar_trad(unid='m', trad='metro', leng_trad='es', guardar=False)

        símismo.assertEqual(convertir('mètres', a='metros'), 1)
