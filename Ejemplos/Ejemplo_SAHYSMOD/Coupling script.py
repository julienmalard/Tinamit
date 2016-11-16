import os

from Conectado import Conectado


# Create a coupled model instance
modelo = Conectado()

# Establish SDM and Biofisical model paths. The Biofisical model path must point to the Python wrapper for the model.
modelo.estab_mds("C:\\SahysMod\\julien\\GBSDM_V2.vpm")

modelo.estab_bf(os.path.join(os.path.split(__file__)[0], 'SAHYSMOD_wrapper.py'))

# Couple models(Change variable names as needed)
modelo.conectar(var_mds='Soil salinity AS1', mds_fuente=False, var_bf="CrA - Root zone salinity crop A")
modelo.conectar(var_mds='Soil salinity BS1', mds_fuente=False, var_bf="CrB - Root zone salinity crop B")
modelo.conectar(var_mds='watertable depth', mds_fuente=False, var_bf="Dw - Groundwater depth")
modelo.conectar(var_mds='ECdw', mds_fuente=False, var_bf='Cqi - Aquifer salinity')
modelo.conectar(var_mds='Lc', mds_fuente=True, var_bf='Lc - Canal percolation')
modelo.conectar(var_mds='IaAS1', mds_fuente=True, var_bf='IaA - Crop A field irrigation')
modelo.conectar(var_mds='IaBS1', mds_fuente=True, var_bf='IaB - Crop B field irrigation')
modelo.conectar(var_mds='Gw', mds_fuente=True, var_bf='Gw - Groundwater extraction')
modelo.conectar(var_mds='Irrigation efficiency', mds_fuente=True, var_bf='FsA - Water storage efficiency crop A')

# Simulate the coupled model
modelo.simular(paso=1, tiempo_final=360, nombre_simul='Tinamit_16-11-16')
