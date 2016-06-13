import os

from Conectado import Conectado


modelo = Conectado()

directorio = os.path.dirname(__file__)

modelo.estab_mds(os.path.join(directorio, "Prueba dll.vpm"))
modelo.estab_bf(os.path.join(directorio, 'Prueba bf.py'))

modelo.conectar(var_mds='Lluvia', var_bf='var1', mds_fuente=False)

print('Simulando...')
modelo.simular(paso=1, tiempo_final=100)
