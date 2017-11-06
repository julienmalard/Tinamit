import os

from tinamit.Conectado import Conectado

# Switch values for runs
ops = {
    'Capacity per tubewell': [153.0, 100.8],
    'Fw': [0.8, 0],
    'Policy Canal lining': [1],
    'Policy RH': [1],
    'Policy Irrigation improvement': [1]
}

runs = {}

for cp in ops['Capacity per tubewell']:
    for fw in ops['Fw']:
        for cl in ops['Policy Canal lining']:
            for rw in ops['Policy RH']:
                for ir in ops['Policy Irrigation improvement']:

                    run_name = 'TC {}, Fw {}, CL {}, RW {}, II {}'.format(
                        cp, fw, cl, rw, ir
                    )

                    runs[run_name] = {
                        'Capacity per tubewell': cp,
                        'Fw': fw,
                        'Policy Canal lining': cl,
                        'Policy RH': rw,
                        'Policy Irrigation improvement': ir
                    }


def run_model(name, switches):
    # Create a coupled model instance
    modelo = Conectado()

    # Establish SDM and Biofisical model paths. The Biofisical model path must point to the Python wrapper for the model
    modelo.estab_mds(os.path.join(os.path.split(__file__)[0], 'Tinamit_sub_v4.vpm'))

    modelo.estab_bf(os.path.join(os.path.split(__file__)[0], 'SAHYSMOD.py'))

    # Set appropriate switches for policy analysis
    for switch, val in switches.items():
        modelo.mds.cambiar_var(var=switch, val=val)

    # Couple models(Change variable names as needed)
    modelo.conectar(var_mds='Soil salinity Tinamit CropA', mds_fuente=False, var_bf="CrA - Root zone salinity crop A")
    modelo.conectar(var_mds='Soil salinity Tinamit CropB', mds_fuente=False, var_bf="CrB - Root zone salinity crop B")
    modelo.conectar(var_mds='Watertable depth Tinamit', mds_fuente=False, var_bf="Dw - Groundwater depth")
    modelo.conectar(var_mds='ECdw Tinamit', mds_fuente=False, var_bf='Cqf - Aquifer salinity')
    modelo.conectar(var_mds='Lc', mds_fuente=True, var_bf='Lc - Canal percolation')
    modelo.conectar(var_mds='Ia CropA', mds_fuente=True, var_bf='IaA - Crop A field irrigation')
    modelo.conectar(var_mds='Ia CropB', mds_fuente=True, var_bf='IaB - Crop B field irrigation')
    modelo.conectar(var_mds='Gw', mds_fuente=True, var_bf='Gw - Groundwater extraction')
    modelo.conectar(var_mds='Irrigation efficiency', mds_fuente=True, var_bf='FsA - Water storage efficiency crop A')
    modelo.conectar(var_mds='Fw', mds_fuente=True, var_bf='Fw - Fraction well water to irrigation')

    # Simulate the coupled model
    modelo.simular(paso=1, tiempo_final=20, nombre_corrida=name)  # time step and final time are in months


# Run the model for all desired runs
for n_run, run in enumerate(runs):
    print('Runing model %s.' % run)
    run_model(run, runs[run])
