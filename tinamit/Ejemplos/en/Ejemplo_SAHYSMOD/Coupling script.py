import os

from tinamit.Conectado import Conectado

# Switch values for runs
runs = {'CWU': {'Capacity per tubewell': 100.8, 'Fw': 0.8, 'Policy Canal lining': 0,
                'Policy RH': 0, 'Policy Irrigation improvement': 0},
        'VD': {'Capacity per tubewell': 153.0, 'Fw': 0.8, 'Policy Canal lining': 0,
               'Policy RH': 0, 'Policy Irrigation improvement': 0},
        'CL': {'Capacity per tubewell': 0, 'Fw': 0, 'Policy Canal lining': 1,
               'Policy RH': 0, 'Policy Irrigation improvement': 0},
        'RWH': {'Capacity per tubewell': 0, 'Fw': 0, 'Policy Canal lining': 0,
                'Policy RH': 1, 'Policy Irrigation improvement': 0},
        'PIM': {'Capacity per tubewell': 0, 'Fw': 0, 'Policy Canal lining': 0,
                'Policy RH': 0, 'Policy Irrigation improvement': 1}
        }


def run_model(name, switches):
    # Create a coupled model instance
    modelo = Conectado()

    # Establish SDM and Biofisical model paths. The Biofisical model path must point to the Python wrapper for the model
    modelo.estab_bf(os.path.join(os.path.split(__file__)[0], 'SAHYSMOD.py'))

    modelo.estab_mds(os.path.join(os.path.split(__file__)[0], 'Tinamit_sub_v2.vpm'))

    # Set appropriate switches for policy analysis
    modelo.mds.inic_vals_vars(switches)

    # Couple models(Change variable names as needed)
    modelo.conectar(var_mds='Soil salinity Tinamit CropA', mds_fuente=False,
                    var_bf="Cr4 - Fully rotated land irrigated root zone salinity")
    modelo.conectar(var_mds='Soil salinity Tinamit CropB', mds_fuente=False,
                    var_bf="Cr4 - Fully rotated land irrigated root zone salinity")
    modelo.conectar(var_mds='Watertable depth Tinamit', mds_fuente=False, var_bf="Dw - Groundwater depth")
    modelo.conectar(var_mds='ECdw Tinamit', mds_fuente=False, var_bf='Cqf - Aquifer salinity')
    modelo.conectar(var_mds='Lc', mds_fuente=True, var_bf='Lc - Canal percolation')
    modelo.conectar(var_mds='IaAS1', mds_fuente=True, var_bf='IaA - Crop A field irrigation')
    modelo.conectar(var_mds='IaBS1', mds_fuente=True, var_bf='IaB - Crop B field irrigation')
    modelo.conectar(var_mds='Gw', mds_fuente=True, var_bf='Gw - Groundwater extraction')
    modelo.conectar(var_mds='Irrigation efficiency', mds_fuente=True, var_bf='FsA - Water storage efficiency crop A')
    modelo.conectar(var_mds='Fw', mds_fuente=True, var_bf='Fw - Fraction well water to irrigation')

    # Simulate the coupled model
    modelo.simular(paso=1, t_final=240, nombre=name)  # time step and final time are in months


# Run the model for all desired runs
for n_run, run in enumerate(runs):
    print('Runing model %s.' % run)
    run_model(run, runs[run])
