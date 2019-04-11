import os
import re
import shutil
import tempfile
from subprocess import run

import numpy as np

from tinamit.config import _
from tinamit.envolt.bf import ModeloBloques
from ._arch_egr import leer_arch_egr
from ._arch_ingr import leer_info_dic_paráms, escribir_desde_dic_paráms
from ._vars import VariablesSAHYSMOD


class ModeloSAHYSMOD(ModeloBloques):
    """
    Envoltura para modelos SAHYSMOD.
    """

    leng_orig = 'en'  # La lengua de los nombres y descripción de los variables (y NO la del código aquí)

    def __init__(símismo, archivo, nombre='SAHYSMOD'):

        # Inicializar la clase pariente.
        super().__init__(nombre=nombre)

        símismo.direc_trabajo = ''

        # Directorio vacío para guardar datos de ingresos después
        símismo.dic_ingr = {}

        # Buscar la ubicación del modelo SAHYSMOD.
        símismo.exe_SAHYSMOD = símismo.obt_conf(
            'exe',
            cond=os.path.isfile,
            mnsj_err=_(
                'Debes especificar la ubicación del ejecutable SAHYSMOD, p. ej.'
                '\n\tEnvolturaSAHYDMOD.estab_conf("exe", "C:\\Camino\\hacia\\mi\\SAHYSMODConsole.exe")'
                '\npara poder hacer simulaciones con modelos SAHYSMOD.'
            )
        )

        # Establecer los variables climáticos.
        símismo.conectar_var_clima(var='Pp - Rainfall', var_clima='Precipitación', combin='total', conv=0.001)

    def _gen_vars(símismo):
        # Leer el fuente de ingreso
        dic_ingr = leer_info_dic_paráms(archivo_fnt=símismo.archivo)
        # Asegurar únicamente un año de simulación, por el momento (para hacer: ¿necesario?).
        dic_ingr['NY'] = 1

        # Guardar el número de estaciones y de polígonos
        símismo.n_estaciones = int(dic_ingr['NS'])
        símismo.dur_estaciones = [int(float(x)) for x in dic_ingr['TS']]  # La duración de las estaciones (en meses)
        n_polí = int(dic_ingr['NN_IN'])

        # Asegurars que el número de estaciones es igual al número de duraciones de estaciones.
        if símismo.n_estaciones != len(símismo.dur_estaciones):
            raise ValueError(
                _('Error en el fuente de datos iniciales SAHYSMOD: el número de duraciones de estaciones'
                  'especificadas no corresponde al número de estaciones especificadas (líneas 3 y 4).')
            )

        return VariablesSAHYSMOD(dims=(n_polí,), símismo.n_estaciones)

    def iniciar_modelo(símismo, corrida):

        # Crear un diccionario de trabajo específico a esta corrida.
        símismo.direc_trabajo = tempfile.mkdtemp(str(corrida))

        super().iniciar_modelo(corrida)

    def avanzar_modelo(símismo, n_ciclos):
        arch_egreso = os.path.join(símismo.direc_trabajo, 'SAHYSMOD.out')
        arch_ingreso = os.path.join(símismo.direc_trabajo, 'SAHYSMOD.inp')

        símismo._escribir_archivo_ingr(n_ciclos=n_ciclos, dic_ingr=símismo.dic_ingr, archivo=arch_ingreso)

        # Limpiar archivos de egresos que podrían estar allí
        if os.path.isfile(arch_egreso):
            os.remove(arch_egreso)

        # Correr la comanda desde la línea de comanda
        comanda = '"{SAHYSMOD}" "{ingreso}" "{egreso}"'.format(
            SAHYSMOD=símismo.exe_SAHYSMOD, ingreso=arch_ingreso, egreso=arch_egreso
        )
        run(comanda, cwd=símismo.direc_trabajo)

        # Verificar que SAHYSMOD generó egresos.
        if not os.path.isfile(arch_egreso):
            raise FileNotFoundError(
                _('El modelo SAHYSMOD no genero egreso. Esto probablemente quiere decir que tuvo problema. '
                  '¡Diviértete! :)')
            )

        símismo.leer_egr_modelo(n_ciclos=n_ciclos)

    def cerrar(símismo):

        for f in os.listdir(símismo.direc_trabajo):
            if re.match('Name(0|[0-9]{2})$', f):
                os.remove(f)

        shutil.rmtree(símismo.direc_trabajo)

    def leer_egr_modelo(símismo, n_ciclos):
        archivo = os.path.join(símismo.direc_trabajo, 'SAHYSMOD.out')

        dic_egr = leer_arch_egr(
            archivo=archivo, n_est=símismo.n_estaciones, n_p=símismo.n_polí, n_años=n_ciclos
        )

        for cr in ['CrA#', 'CrB#', 'CrU#', 'Cr4#', 'A#', 'B#', 'U#']:
            dic_egr[cr][dic_egr[cr] == -1] = 0

        # Ajustar la salinidad por la presencia de varios cultivos
        kr = dic_egr['Kr#']

        salin_suelo = np.zeros((símismo.n_estaciones, símismo.n_polí))

        # Crear una máscara boleana para cada valor potencial de Kr y llenarlo con la salinidad correspondiente
        kr0 = (kr == 0)
        salin_suelo[kr0] = dic_egr['A#'][kr0] * dic_egr['CrA#'][kr0] + dic_egr['B#'][kr0] * dic_egr['CrB#'][kr0] + \
                           dic_egr['U#'][kr0] * dic_egr['CrU#'][kr0]

        kr1 = (kr == 1)
        salin_suelo[kr1] = dic_egr['CrU#'][kr1] * dic_egr['U#'][kr1] + dic_egr['C1*#'][kr1] * (1 - dic_egr['U#'][kr1])

        kr2 = (kr == 2)
        salin_suelo[kr2] = dic_egr['CrA#'][kr2] * dic_egr['A#'][kr2] + dic_egr['C2*#'][kr2] * (1 - dic_egr['A#'][kr2])

        kr3 = (kr == 3)
        salin_suelo[kr3] = dic_egr['CrB#'][kr3] * dic_egr['B#'][kr3] + dic_egr['C3*#'][kr3] * (1 - dic_egr['B#'][kr3])

        kr4 = (kr == 4)
        salin_suelo[kr4] = dic_egr['Cr4#'][kr4]

        para_llenar = [
            {'mask': kr0, 'cr': ['Cr4#']},
            {'mask': kr1, 'cr': ['CrA#', 'CrB#', 'Cr4#']},
            {'mask': kr2, 'cr': ['CrB#', 'CrU#', 'Cr4#']},
            {'mask': kr3, 'cr': ['CrA#', 'CrU#', 'Cr4#']},
            {'mask': kr4, 'cr': ['CrA#', 'CrB#', 'CrU#']}
        ]

        for d in para_llenar:
            l_cr = d['cr']
            mask = d['mask']

            for cr in l_cr:
                dic_egr[cr][mask] = salin_suelo[mask]

        # Convertir códigos de variables a nombres de variables
        for c, v in dic_egr.items():
            símismo.variables.cód_a_var[c].poner_val(v)


    @classmethod
    def instalado(cls):
        return cls.obt_conf('exe') is not None

    def paralelizable(símismo):
        return True

    def unidad_tiempo(símismo):
        return 'mes'

    def obt_tmñ_bloques(símismo):
        return símismo.dur_estaciones

    def _escribir_archivo_ingr(símismo, n_ciclos, dic_ingr, archivo):

        # Establecer el número de años de simulación
        símismo.dic_ingr['NY'] = n_ciclos

        # Copiar datos desde el diccionario de ingresos
        for var, val in dic_ingr.items():
            var_cód = símismo.variables.c
            llave = var_cód.replace('#', '').upper()

            símismo.dic_ingr[llave] = val

        # Aseguarse que no quedamos con áreas que faltan
        for k in ["A", "B"]:
            vec = símismo.dic_ingr[k]
            vec[vec == -1] = 0

        # Y finalmente, escribir el fuente de valores de ingreso
        escribir_desde_dic_paráms(dic_paráms=símismo.dic_ingr, archivo_obj=archivo)
