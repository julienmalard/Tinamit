import os

from Conectado import Conectado


# Create a coupled model instance
modelo = Conectado()

# Establish SDM and Biofisical model paths. The Biofisical model path must point to the Python wrapper for the model.
modelo.estab_mds("C:\\Users\\gis_lab\\Dropbox\\Tinamit\\julien\\LCEM.vpm")

modelo.estab_bf(os.path.join(os.path.split(__file__)[0], 'SAHYSMOD_wrapper.py'))

# Couple models(Change variable names as needed)
modelo.conectar(var_mds='"EC (From Sahysmod)"', mds_fuente=False, var_bf="Root zone salinity crop A")

# Simulate the coupled model
modelo.simular(paso=1, tiempo_final=120)
