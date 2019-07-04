import os

from tinamit.envolt.bf.sahysmod import ModeloSAHYSMOD

# Path to the SAHYSMOD input file with the initial data. Change as needed on your computer.
directory = os.path.dirname(__file__)
initial_data = os.path.join(directory, '459anew1.inp')

# Creates the SAHYSMOD wrapper. Don't change this line.
Envoltura = ModeloSAHYSMOD(archivo=initial_data)
