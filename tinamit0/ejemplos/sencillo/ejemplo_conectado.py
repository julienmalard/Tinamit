import os

from tinamit.Conectado import Conectado

modelo = Conectado()

directorio = os.path.dirname(__file__)

modelo.estab_mds(os.path.join(directorio, "mds_bosques.mdl"))
modelo.estab_bf(os.path.join(directorio, 'bf_bosques.py'))

modelo.conectar(var_ds='Lluvia', var_bf='Lluvia', mds_fuente=False)
modelo.conectar(var_ds='Bosques', var_bf='Bosques', mds_fuente=True)

res = modelo.simular(paso=1, t_final=100, nombre='Corrida_Tinamit')
