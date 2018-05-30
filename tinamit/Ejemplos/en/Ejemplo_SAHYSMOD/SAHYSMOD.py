import os

from EnvolturasBF.SAHYSMOD import ModeloSAHYSMOD

# Path to the SAHYSMOD input file with the initial data. Change as needed on your computer.
directory = os.path.dirname(__file__)
initial_data = os.path.join(directory, '459anew1.inp')

# Creates the SAHYSMOD wrapper. Don't change this line.
Envoltura = ModeloSAHYSMOD(datos_iniciales=initial_data)
