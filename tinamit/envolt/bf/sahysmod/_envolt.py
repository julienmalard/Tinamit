import os
import re
import shutil
from subprocess import run

import numpy as np

from tinamit.BF import ModeloBloques
from tinamit.config import _
from ._ingr_egr import leer_info_dic_paráms, escribir_desde_dic_paráms
from ._vars import VariablesSAHYSMOD


class ModeloSAHYSMOD(ModeloBloques):
    """
    Envoltura para modelos SAHYSMOD.
    """

    leng_orig = 'en'  # La lengua de los nombres y descripción de los variables (y NO la del código aquí)

    def __init__(símismo, archivo, nombre='SAHYSMOD'):

        # Inicializar la clase pariente.
        super().__init__(nombre=nombre)

        # Necesario para paralelismo
        símismo.argsinic = (archivo, nombre)

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

    def iniciar_modelo(símismo, n_pasos, t_final, nombre_corrida, vals_inic):

        # Crear un diccionario de trabajo específico a esta corrida.
        símismo.direc_trabajo = os.path.join(símismo.direc_base, '_temp', nombre_corrida)
        if os.path.isdir(símismo.direc_trabajo):
            shutil.rmtree(símismo.direc_trabajo)
        os.makedirs(símismo.direc_trabajo)
        símismo.arch_egreso = os.path.join(símismo.direc_trabajo, 'SAHYSMOD.out')
        símismo.arch_ingreso = os.path.join(símismo.direc_trabajo, 'SAHYSMOD.inp')

        super().iniciar_modelo(n_pasos, t_final, nombre_corrida, vals_inic)

    def avanzar_modelo(símismo, n_ciclos):

        símismo._escribir_archivo_ingr(n_ciclos=n_ciclos, dic_ingr=símismo.dic_ingr, archivo=símismo.arch_ingreso)

        # Limpiar archivos de egresos que podrían estar allí
        if os.path.isfile(símismo.arch_egreso):
            os.remove(símismo.arch_egreso)

        # Correr la comanda desde la línea de comanda
        args = dict(SAHYSMOD=símismo.exe_SAHYSMOD, ingreso=símismo.arch_ingreso, egreso=símismo.arch_egreso)
        comanda = '"{SAHYSMOD}" "{ingreso}" "{egreso}"'.format(**args)
        run(comanda, cwd=símismo.direc_trabajo)

        # Verificar que SAHYSMOD generó egresos.
        if not os.path.isfile(símismo.arch_egreso):
            raise FileNotFoundError(_('El modelo SAHYSMOD no genero egreso. Esto probablemente quiere decir que '
                                      'tuvo problema. ¡Diviértete! :)'))

    def cerrar(símismo):

        for f in os.listdir(símismo.direc_trabajo):
            if re.match('Name(0|[0-9]{2})$', f):
                os.remove(f)

    def leer_egr_modelo(símismo, n_ciclos, archivo=None):
        archivo = archivo or símismo.arch_egreso

        dic_egr = leer_arch_egr(archivo=archivo, n_est=símismo.n_estaciones, n_p=símismo.n_polí,
                                n_años=n_ciclos)

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
        dic_final = {códs_a_vars[c]: v for c, v in dic_egr.items()}

        # Devolver el diccionario final
        return dic_final

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

    def __getinitargs__(símismo):
        return símismo.argsinic


def leer_arch_egr(archivo, n_est, n_p, n_años):
    """
    :return: eje 0 = estación, eje 1 = polígono. -1 = valor que falta
    :rtype: dict[str, np.ndarray]
    """

    dic_datos = dict([(k, np.empty((n_est, n_p))) for k in vars_egreso_SAHYSMOD])
    for k, v in dic_datos.items():
        v[:] = -1

    with open(archivo, 'r') as d:
        l = ''
        while 'YEAR:      %i' % n_años not in l:
            l = d.readline()
        for est in range(n_est):
            for estación_polí in range(n_p):  # Leer el egreso de las estaciones del último año

                polí = []
                while re.match(' #', l) is None:
                    polí.append(l)
                    l = d.readline()

                l = d.readline()  # Avanzar una línea más para la próxima estación

                for cód in vars_egreso_SAHYSMOD:
                    var_egr = cód.replace('#', '').replace('*', '\*')

                    for línea in polí:

                        línea += ' '
                        m = re.search(' %s += +([^ ]*)' % var_egr, línea)

                        if m:
                            val = m.groups()[0]
                            if val == '-':
                                val = -1
                            else:
                                try:
                                    val = float(val)
                                except ValueError:
                                    raise ValueError(
                                        _('El variable "{}" no se pudo leer del egreso SAHYSMOD').format(var_egr)
                                    )
                            dic_datos[cód][(est, estación_polí)] = val
                            break
    return dic_datos
