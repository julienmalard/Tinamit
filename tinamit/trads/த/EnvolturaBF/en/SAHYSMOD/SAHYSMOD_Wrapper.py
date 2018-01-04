from tinamit.EnvolturaBF.en.SAHYSMOD.SAHYSMOD_Wrapper import read_output_file
from tinamit.EnvolturaBF.en.SAHYSMOD.SAHYSMOD_Wrapper import SAHYSMOD_output_vars
from tinamit.EnvolturaBF.en.SAHYSMOD.SAHYSMOD_Wrapper import SAHYSMOD_input_vars
from tinamit.EnvolturaBF.en.SAHYSMOD.SAHYSMOD_Wrapper import codes_to_vars
from tinamit.EnvolturaBF.en.SAHYSMOD.SAHYSMOD_Wrapper import vars_SAHYSMOD
from tinamit.EnvolturaBF.en.SAHYSMOD.SAHYSMOD_Wrapper import ModeloSAHYSMOD


class ModeloSAHYSMOD(ModeloSAHYSMOD):

    def மாறிகளை_ஆரம்ப(self):
        return self.inic_vars()

    def iniciar_modelo(self):
        return super().iniciar_modelo()

    def avanzar_modelo(self):
        return super().avanzar_modelo()

    def cerrar_modelo(self):
        return super().cerrar_modelo()

    def escribir_archivo_ingr(self, n_años_simul, dic_ingr):
        return super().escribir_archivo_ingr(n_años_simul=n_años_simul, dic_ingr=dic_ingr)

    def leer_archivo_egr(self, n_años_egr):
        return super().leer_archivo_egr(n_años_egr=n_años_egr)

    def leer_archivo_vals_inic(self):
        return super().leer_archivo_vals_inic()

vars_SAHYSMOD = vars_SAHYSMOD

codes_to_vars = codes_to_vars

SAHYSMOD_input_vars = SAHYSMOD_input_vars

SAHYSMOD_output_vars = SAHYSMOD_output_vars
