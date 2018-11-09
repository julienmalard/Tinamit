import os

from tinamit.Conectado import Conectado

modelo = Conectado()

directorio = os.path.dirname(__file__)

modelo.estab_mds(os.path.join(directorio, "Prueba dll.mdl"))
modelo.estab_bf(os.path.join(directorio, 'Prueba bf.py'))

modelo.conectar(var_mds='Lluvia', var_bf='Lluvia', mds_fuente=False)
modelo.conectar(var_mds='Bosques', var_bf='Bosques', mds_fuente=True)

res = modelo.simular(paso=1, t_final=100, nombre_corrida='Corrida_Tinamit')
print(res)
