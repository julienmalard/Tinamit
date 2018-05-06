import unittest

from tinamit.Unidades.conv import convertir
from tinamit.Unidades.trads import agregar_trad


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
        agregar_trad('pound', trad='paj', leng_trad='cak', guardar=False)
        agregar_trad('paj', trad='libra', leng_trad='es', leng_orig='cak', guardar=False)
        de = 'paj'
        a = 'libras'

        # Deberían ser igual ahora.
        símismo.assertEqual(convertir(de, a), 1)

    def test_convertir_con_traducción_desconocida(símismo):
        # Aunque no sepa lo que es una "estación", el programa debería detectar que es lo mismo en ambos y solamente
        # convertir los m3 a cm3.
        símismo.assertAlmostEqual(convertir('m3/estación', 'cm3/estación'), 100**3)

    def test_convertir_con_valor(símismo):
        # Comprobar conversión real.
        símismo.assertEqual(convertir('km', 'm', val=2), 2000)

    def test_conversión_imposible(símismo):
        # ¡Comparemos bananas con naranjas!
        símismo.assertRaises(ValueError, lambda: convertir('bananas', 'naranjas'))

        # Y un error de dimensionalidad.
        símismo.assertRaises(ValueError, lambda: convertir('m3', 'm2'))
