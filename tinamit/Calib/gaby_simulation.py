import os

from tinamit.Conectado import Conectado
from tinamit.Geog.Geog import Lugar, Geografía
from tinamit.EnvolturasBF import ModeloSAHYSMOD
import numpy as np
# from tinamit.Calib.SA_algorithms import test as t
from tinamit.Calib.SA_algorithms import parameters_sa as P

# mod = ModeloSAHYSMOD(datos_iniciales='')

# def setup_parameters(sampling_parameters=None, n_seasons=1):
#
#     if sampling_parameters is None:
#         sampling_parameters = {}
#
#     runs_simpler = {'CWU': {'Capacity per tubewell': 100.8, 'Fw': 0.8, 'Policy Canal lining': 0,
#                             'Policy RH': 0, 'Policy Irrigation improvement': 0}}
#     # 3. Now create the model
#     # Create a coupled model instance
#     modelo = Conectado()
#
#     # Establish SDM and Biofisical model paths. The Biofisical model path must point to the Python wrapper for the model
#     modelo.estab_mds(os.path.join(os.path.split(__file__)[0], 'Tinamit_sub_v4.vpm'))
#     modelo.estab_bf(os.path.join(os.path.split(__file__f)[0], 'SAHYSMOD.py'))
#     modelo.estab_conv_tiempo(mod_base='mds', conv=6)
#
#     print(len(modelo.bf.variables)) #104
#     print(modelo.bf.inic_val) # empty, if variables couldn't find the vals, problly will get from the inic_val.
#     print(len(modelo.mds.inic_val))
#
#     # print('Peq - Aquifer effective porosity', modelo.bf.variables['Peq - Aquifer effective porosity'])
#     # print('Pex - Transition zone effective porosity', modelo.bf.variables['Pex - Transition zone effective porosity'])
#
#     # test
#     # change input variables with parameters value, i = n_parameter(index);para=215 (should name it n_poly)
#     for var, val in sampling_parameters.items():
#         modelo.bf.inic_val(var=var, val=val)
#         #modelo.mds.inic_val
#
#     # Couple models(Change variable names as needed)
#     modelo.conectar(var_mds='Soil salinity Tinamit CropA', mds_fuente=False, var_bf="CrA - Root zone salinity crop A")
#     modelo.conectar(var_mds='Soil salinity Tinamit CropB', mds_fuente=False, var_bf="CrB - Root zone salinity crop B")
#     modelo.conectar(var_mds='Watertable depth Tinamit', mds_fuente=False, var_bf="Dw - Groundwater depth")
#     modelo.conectar(var_mds='ECdw Tinamit', mds_fuente=False, var_bf='Cqf - Aquifer salinity')
#     modelo.conectar(var_mds='Lc', mds_fuente=True, var_bf='Lc - Canal percolation')
#     modelo.conectar(var_mds='Ia CropA', mds_fuente=True, var_bf='IaA - Crop A field irrigation')
#     modelo.conectar(var_mds='Ia CropB', mds_fuente=True, var_bf='IaB - Crop B field irrigation')
#     modelo.conectar(var_mds='Gw', mds_fuente=True, var_bf='Gw - Groundwater extraction')
#     modelo.conectar(var_mds='Irrigation efficiency', mds_fuente=True, var_bf='FsA - Water storage efficiency crop A')
#     modelo.conectar(var_mds='Fw', mds_fuente=True, var_bf='Fw - Fraction well water to irrigation')
#
#     # Run the model for all desired runs
#     for name, run in runs_simpler.items():
#
#         # print('Runing model {}.\n-----------------'.format(name))
#         #print(name, run)
#
#         # Set appropriate switches for policy analysis
#         for switch, val in run.items():
#             #print("switch: ", switch, " ----- val: ", val)
#             modelo.mds.inic_val(var=switch, val=val)
#
#         # Simulate the coupled model
#         # (step, final time, running name)
#         # modelo.simular(paso=1, tiempo_final=20, nombre_corrida=name)  # time step and final time are in seasons
#         modelo.simular(paso=1, tiempo_final=n_seasons, nombre_corrida=name)
#         #result = modelo.mds.leer_resultados_mds(name, var='Watertable depth Tinamit')
#     return modelo.mds.leer_resultados_mds(name, var='Watertable depth Tinamit')
#
#     # modelo.simular_paralelo()  # Does NOT go here. 在这里不行！！
# sahysmod is by month, the sdm is by season >>>>>> here tiempo_final is by season

'''
def get_result():
    return SW.read_output_file(
        'D:\\Thesis\\pythonProject\\Tinamit\\tinamit\\Calib\\SAHYSMOD.out',
        n_s=1, n_p=215, n_y=1)['Dw#'][0]
# get the Dw# from the output simulation results
'''

def simulation(sampling_parameters, tiempo_final, nombre):
    run = {'Capacity per tubewell': 100.8, 'Fw': 0.8, 'Policy Canal lining': 0,
                            'Policy RH': 0, 'Policy Irrigation improvement': 0}
    #'Fw': 0.5

    # 3. Now create the model
    # Create a coupled model instance
    modelo = Conectado()

    # Establish SDM and Biofisical model paths. The Biofisical model path must point to the Python wrapper for the model
    modelo.estab_mds(os.path.join(os.path.split(__file__)[0], 'Rechna Doab.vpm'))
    modelo.estab_bf(os.path.join(os.path.split(__file__)[0], 'SAHYSMOD.py'))
    modelo.estab_conv_tiempo(mod_base='mds', conv=6)

    # Couple models(Change variable names as needed)
    '''modelo.conectar(var_mds='Soil salinity Tinamit CropA', mds_fuente=False, var_bf="CrA - Root zone salinity crop A")
    modelo.conectar(var_mds='Soil salinity Tinamit CropB', mds_fuente=False, var_bf="CrB - Root zone salinity crop B")
    modelo.conectar(var_mds='Watertable depth Tinamit', mds_fuente=False, var_bf="Dw - Groundwater depth")
    modelo.conectar(var_mds='ECdw Tinamit', mds_fuente=False, var_bf='Cqf - Aquifer salinity')
    modelo.conectar(var_mds='Lc', mds_fuente=True, var_bf='Lc - Canal percolation')
    modelo.conectar(var_mds='Ia CropA', mds_fuente=True, var_bf='IaA - Crop A field irrigation')
    modelo.conectar(var_mds='Ia CropB', mds_fuente=True, var_bf='IaB - Crop B field irrigation')
    modelo.conectar(var_mds='Gw', mds_fuente=True, var_bf='Gw - Groundwater extraction')
    modelo.conectar(var_mds='Irrigation efficiency', mds_fuente=True, var_bf='FsA - Water storage efficiency crop A')
    modelo.conectar(var_mds='Fw', mds_fuente=True, var_bf='Fw - Fraction well water to irrigation')
    '''

    modelo.conectar(var_mds='Soil salinity Tinamit CropA', mds_fuente=False, var_bf="CrA - Root zone salinity crop A")
    modelo.conectar(var_mds='Soil salinity Tinamit CropB', mds_fuente=False, var_bf="CrB - Root zone salinity crop B")
    modelo.conectar(var_mds='Area fraction Tinamit CropA', mds_fuente=False,
                    var_bf="Area A - Seasonal fraction area crop A")
    modelo.conectar(var_mds='Area fraction Tinamit CropB', mds_fuente=False,
                    var_bf="Area B - Seasonal fraction area crop B")
    modelo.conectar(var_mds='Watertable depth Tinamit', mds_fuente=False, var_bf="Dw - Groundwater depth")
    modelo.conectar(var_mds='ECdw Tinamit', mds_fuente=False, var_bf='Cqf - Aquifer salinity')
    modelo.conectar(var_mds='Rainfall Tinamit', mds_fuente=False, var_bf='Pp - Rainfall')
    modelo.conectar(var_mds='Lc', mds_fuente=True, var_bf='Lc - Canal percolation')
    modelo.conectar(var_mds='Ia CropA', mds_fuente=True, var_bf='IaA - Crop A field irrigation')
    modelo.conectar(var_mds='Ia CropB', mds_fuente=True, var_bf='IaB - Crop B field irrigation')
    modelo.conectar(var_mds='Gw', mds_fuente=True, var_bf='Gw - Groundwater extraction')
    modelo.conectar(var_mds='EpA', mds_fuente=True, var_bf='EpA - Potential ET crop A')
    modelo.conectar(var_mds='EpB', mds_fuente=True, var_bf='EpB - Potential ET crop B')
    modelo.conectar(var_mds='Irrigation efficiency', mds_fuente=True, var_bf='FsA - Water storage efficiency crop A')
    modelo.conectar(var_mds='Fw', mds_fuente=True, var_bf='Fw - Fraction well water to irrigation')

    # Set appropriate switches for policy analysis
    for switch, val in run.items():
        modelo.mds.inic_val(var=switch, val=val)
        # print(modelo.mds.variables)

    return modelo.simular_paralelo(paso=1, tiempo_final=tiempo_final, nombre_corrida=nombre,
                                   vals_inic=sampling_parameters, devolver='Watertable depth Tinamit', paralelo=True)
#devolver='Watertable depth Tinamit'
#print(vals_inic)

'''
print("\n\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>run climate >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n ")
# Climate change runs
location = Lugar(lat=32.178207, long=73.217391, elev=217)
location.observar_mensuales('مشاہدہ بارش.csv', meses='مہینہ', años='سال',
                            cols_datos={'Precipitación': 'بارش (میٹر)'})
# icpp. 
for rcp in [2.6, 4.5, 6.0, 8.5]:
    print('Runing with rcp {}\n************'.format(rcp))

    for name, run in runs.items():

        print('\tRuning model {}.\n\t-----------------'.format(name))

        nombre_corrida = '{}, {}'.format(rcp, name)
        # Set appropriate switches for policy analysis
        for switch, val in run.items():
            print("switch: ", switch, "-> val: ", val)
            modelo.mds.inic_val(var=switch, val=val)

        #(step, final time, start tiime, location, ...)
        modelo.simular(paso=1, tiempo_final=100 * 2, fecha_inic=1990, lugar=location, tcr=rcp, clima=True, recalc=False,
                       nombre_corrida=nombre_corrida)

        modelo.dibujar(geog=Rechna_Doab, corrida=nombre_corrida, var='Watertable depth Tinamit',
                       directorio='Maps')
        modelo.dibujar(geog=Rechna_Doab, corrida=nombre_corrida, var='Soil salinity Tinamit CropA',
                       directorio='Maps')
'''


