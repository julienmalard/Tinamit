from Conectado import Conectado


modelo = Conectado()

modelo.estab_mds("C:\\Users\\you\\YourDocuments\\Azhar's model.vpm")

modelo.estab_bf('C:\\Users\\jmalar1\\Documents\\PycharmProjects\\Tinamit\\Ejemplos\\'
                'Ejemplo SAHYSMOD\\Envoltura SAHYSMOD.py')
modelo.actualizar()

# Change variable names as needed
modelo.conexiones = [{"var_mds": "Groundwater Table", "mds_fuente": False, "conv": 1, "var_bf": "Groundwater Depth"},
                     {"var_mds": "Groundwater Extraction", "mds_fuente": True, "conv": 1, "var_bf":
                         "Groundwater Extraction"},
                     {"var_mds": "Soil Salinity", "mds_fuente": False, "conv": 1, "var_bf": "Soil Salinity"}
                     ]

modelo.actualizar_conexiones()

modelo.simular(paso=0.5, tiempo_final=12)
