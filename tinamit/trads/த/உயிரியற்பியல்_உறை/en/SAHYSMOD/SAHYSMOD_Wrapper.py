from tinamit.உயிரியற்பியல்_உறை.en.SAHYSMOD.SAHYSMOD_Wrapper import read_output_file
from tinamit.உயிரியற்பியல்_உறை.en.SAHYSMOD.SAHYSMOD_Wrapper import SAHYSMOD_output_vars
from tinamit.உயிரியற்பியல்_உறை.en.SAHYSMOD.SAHYSMOD_Wrapper import SAHYSMOD_input_vars
from tinamit.உயிரியற்பியல்_உறை.en.SAHYSMOD.SAHYSMOD_Wrapper import codes_to_vars
from tinamit.உயிரியற்பியல்_உறை.en.SAHYSMOD.SAHYSMOD_Wrapper import vars_SAHYSMOD
from tinamit.உயிரியற்பியல்_உறை.en.SAHYSMOD.SAHYSMOD_Wrapper import ModeloSAHYSMOD


class ModeloSAHYSMOD(ModeloSAHYSMOD):

    def __init__(self, sayhsmod_exe, initial_data):
        super().__init__(sayhsmod_exe=sayhsmod_exe, initial_data=initial_data)

    def மாறிகளை_ஆரம்ப(self):
        return self.inic_vars()

    def iniciar_modelo(self):
        return self.iniciar_modelo()

    def avanzar_modelo(self):
        return self.avanzar_modelo()

    def cerrar_modelo(self):
        return self.cerrar_modelo()

    def escribir_archivo_ingr(self, n_años_simul, dic_ingr):
        return self.escribir_archivo_ingr(n_años_simul, dic_ingr)

    def leer_archivo_egr(self, n_años_egr):
        return self.leer_archivo_egr(n_años_egr)

    def leer_archivo_vals_inic(self):
        return self.leer_archivo_vals_inic()


vars_SAHYSMOD = vars_SAHYSMOD

codes_to_vars = codes_to_vars

SAHYSMOD_input_vars = SAHYSMOD_input_vars

SAHYSMOD_output_vars = SAHYSMOD_output_vars


def read_output_file(file_path, n_s, n_p, n_y):
    return read_output_file(file_path=file_path, n_s=n_s, n_p=n_p, n_y=n_y)
