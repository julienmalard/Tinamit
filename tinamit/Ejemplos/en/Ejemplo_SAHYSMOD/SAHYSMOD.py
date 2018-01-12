import os

from tinamit.EnvolturaBF.en.SAHYSMOD.SAHYSMOD_Wrapper import ModeloSAHYSMOD


# Path to the SAHYSMOD input file with the initial data. Change as needed on your computer.
directory = os.path.dirname(__file__)
initial_data = os.path.join(directory, 'INPUT_EXAMPLE2.inp')


# Creates the SAHYSMOD wrapper. Don't change this line.
class Modelo(ModeloSAHYSMOD):
    def __init__(self):
        super().__init__(initial_data=initial_data)
