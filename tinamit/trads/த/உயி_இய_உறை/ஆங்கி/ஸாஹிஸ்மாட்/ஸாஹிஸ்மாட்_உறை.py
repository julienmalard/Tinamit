from tinamit.EnvolturaBF.en.SAHYSMOD.SAHYSMOD_Wrapper import ModeloSAHYSMOD
from tinamit.EnvolturaBF.en.SAHYSMOD.SAHYSMOD_Wrapper import SAHYSMOD_input_vars
from tinamit.EnvolturaBF.en.SAHYSMOD.SAHYSMOD_Wrapper import SAHYSMOD_output_vars
from tinamit.EnvolturaBF.en.SAHYSMOD.SAHYSMOD_Wrapper import codes_to_vars
from tinamit.EnvolturaBF.en.SAHYSMOD.SAHYSMOD_Wrapper import read_output_file
from tinamit.EnvolturaBF.en.SAHYSMOD.SAHYSMOD_Wrapper import vars_SAHYSMOD


class ஸாஹிஸ்மாட்_மாதிரி(ModeloSAHYSMOD):

    def மாதிரி_ஆரம்பு(தன், tiempo_final, nombre_corrida):
        return தன்.iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida=nombre_corrida)

    def avanzar_modelo(தன்):
        return super().avanzar_modelo()

    def மாதிரி_முடி(தன்):
        return தன்.cerrar_modelo()

    def escribir_archivo_ingr(தன், n_años_simul, உள்ளீடு_அகராதி):
        return super().escribir_archivo_ingr(n_años_simul=n_años_simul, dic_ingr=உள்ளீடு_அகராதி)

    def வேளியீடு_கோப்பை_படி(தன், n_años_egr):
        return தன்.leer_archivo_egr(n_años_egr=n_años_egr)

    def leer_archivo_vals_inic(தன்):
        return super().leer_archivo_vals_inic()

    def paralelizable(símismo):
        return super().paralelizable()


ஸாஹிஸ்மாட்_மாறிகள் = vars_SAHYSMOD

codes_to_vars = codes_to_vars

ஸாஹிஸ்மாட்_உள்ளீடு_மாறிகள் = SAHYSMOD_input_vars

ஸாஹிஸ்மாட்_வேளியீடு_மாறிகள் = SAHYSMOD_output_vars


def வேளியீடு_கோப்பை_படி(கோப்பு_பாதை, n_s, n_p, n_y):
    return read_output_file(file_path=கோப்பு_பாதை, n_s=n_s, n_p=n_p, n_y=n_y)
