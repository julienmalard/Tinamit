from Conectado import Conectado


modelo = Conectado()
# modelo.estab_mds("F:\\Julien\\PhD\\Iximulew\\MDS 2015\\Tz'olöj Ya'\\Taller 12\\Para tinamit.vpm")
modelo.estab_mds("C:\\Users\\jmalar1\\Documents\\PycharmProjects\\Tinamit\\Ejemplos\\Prueba dll.vpm")
# modelo.estab_bf('F:\\Julien\\PhD\\Python\\Tikon\\Tinamit.py')
modelo.estab_bf('C:\\Users\\jmalar1\\Documents\\PycharmProjects\\Tinamit\\Ejemplos\\Prueba bf.py')
modelo.actualizar()

modelo.conexiones=[{"var_mds": "Variable 1", "mds_fuente": True, "conv": 1, "var_bf": "var1"}]
modelo.actualizar_conexiones()

modelo.simular(paso=1, tiempo_final=12)
