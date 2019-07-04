import unittest

import tinamit.unids.trads as trads
from tinamit.unids.conv import convertir


class Test_ConvertirUnidades(unittest.TestCase):
    """
    Comprobar la conversión de unidades.
    """

    def test_convertir_unids_equivalentes(símismo):
        # unids equivalentes deberían dar un factor de conversión de 1.
        símismo.assertEqual(convertir('m2/d', 'm3/d/m'), 1)

    def test_convertir_unids_iguales(símismo):
        # unids idénticas deberían dar un factor de conversión de 1.
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
        """
        ¡Comparemos bananas con naranjas!
        """
        símismo.assertRaises(ValueError, lambda: convertir('bananas', 'naranjas'))

        # Y un error de dimensionalidad.
        símismo.assertRaises(ValueError, lambda: convertir('m3', 'm2'))

    def test_convertir_plurial_erróneo(símismo):
        """
        Intentemos convertir un nombre que parece ser forma plurial ("mes" podría reconocerse como el plurial
        de "m"), pero no lo es.
        """
        símismo.assertEqual(convertir('años', 'mes'), 12)


class Test_TradsUnidades(unittest.TestCase):
    """
    Pruebas de funciones de traducción de unidades.
    """

    def test_traducir(símismo):
        """
        Comprobar que podemos traducir.
        """

        res = trads.trad_unid('year', leng_final='es', leng_orig='en')
        símismo.assertEqual(res, 'año')

    def test_traducir_sin_especificar_leng(símismo):
        """
        Comprobar que podamos adividar la lengua original de una unidad.
        """

        res = trads.trad_unid('year', leng_final='es')
        símismo.assertEqual(res, 'año')

    def test_trad_unidad_errónea(símismo):
        """
        Comprobar que devolvamos aviso para unidades que no existen en la lengua especificada.
        """

        res = trads.trad_unid('paj', leng_final='fr', leng_orig='es')

        # Asegurarque que devolvimos el valor inicial para la unidad.
        símismo.assertEqual(res, 'paj')

    def test_trad_unidad_errónea_sin_especificar_leng(símismo):
        """
        Comprobar que devolvamos aviso error para unidades que no existen.
        """

        with símismo.assertRaises(ValueError):
            trads.trad_unid('¡Yo no existo!', leng_final='fr', falla_silencio=False)

    def test_agregar_sinónimo(símismo):
        """
        Comprobar que podemos agregar sinónimos de unidades.
        """

        trads.agregar_sinónimos(unid='foot', sinónimos='feet', leng='en', guardar=True)
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

        trads.agregar_trad(unid='l', trad='litre', leng_trad='fr', guardar=False)
        trads.agregar_trad(unid='l', trad='litro', leng_trad='es', guardar=False)

        símismo.assertEqual(convertir('litres', a='litros'), 1)

    def test_agregar_trad_errónea(símismo):
        """
        Comprobar que tenemos error al agregar traducciones para unidades que no existen en la lengua especificada.
        """

        with símismo.assertRaises(ValueError):
            # "Year" no existe en castellano.
            trads.agregar_trad(unid='year', trad="année", leng_trad='fr', leng_orig='es')

    def test_agregar_trad_errónea_sin_especificar_leng(símismo):
        """
        Comprobar que tenemos error al agregar traducciones para unidades que no existen en cualquier idioma.
        """

        with símismo.assertRaises(ValueError):
            trads.agregar_trad(unid='¡Yo no existo!', trad="Je n'existe pas !", leng_trad='fr')
