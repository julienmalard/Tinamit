import os

from tinamit.EnvolturaBF.en.SAHYSMOD.SAHYSMOD_Wrapper import ModeloSAHYSMOD

# Path to SAHYSMOD executable. Change as needed on your computer.
SAHYSMOD = 'D:\\Sahysmod\\SahysModConsole.exe'
# path of the Julien's computer

# Path to the SAHYSMOD input file with the initial data. Change as needed on your computer.
directory = os.path.dirname(__file__)
initial_data = os.path.join(directory, 'INPUT_EXAMPLE2.inp')
#initial_data = os.path.join(directory, 'testIO')

# Creates the SAHYSMOD wrapper. Don't change this line.
class Modelo(ModeloSAHYSMOD):
    def __init__(self):
        super().__init__(sayhsmod_exe=SAHYSMOD, initial_data=initial_data)

