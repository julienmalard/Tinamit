import os
import re
import shutil
from subprocess import run

import numpy as np
import pkg_resources

from tinamit.BF import ModeloBloques
from tinamit.EnvolturasBF.SAHYSMOD.variables import vars_SAHYSMOD, códs_a_vars, vars_ingreso_SAHYSMOD, \
    vars_egreso_SAHYSMOD
from tinamit.config import _
from ._sahysmodIE import leer_info_dic_paráms, escribir_desde_dic_paráms


class ModeloSAHYSMOD(ModeloBloques):
    """
    Envoltura para modelos SAHYSMOD.
    """

    @classmethod
    def refs_prb_avanzar(cls):
        raise NotImplementedError

    leng_orig = 'en'  # La lengua de los nombres y descripción de los variables (y NO la del código aquí)

    @classmethod
    def refs_prb_leer_egr(cls):
        prb_arch_egr = pkg_resources.resource_filename(__name__, 'recursos/prb_egresos.out')
        dic_prb_egr = pkg_resources.resource_filename(__name__, 'recursos/dic_prb_egr.json')
        return NotImplementedError
        return prb_arch_egr, dic_prb_egr

    @classmethod
    def refs_prb_vals_inic(cls):
        prb_datos_inic = pkg_resources.resource_filename(__name__, 'recursos/prb_datos_inic.inp')
        dic_prb_datos_inic = pkg_resources.resource_filename(__name__, 'recursos/dic_prb_datos_inic.json')
        return prb_datos_inic, dic_prb_datos_inic

    def __init__(símismo, datos_iniciales, exe_sahysmod=None, nombre='SAHYSMOD'):

        # Necesario para paralelismo
        símismo.argsinic = (datos_iniciales, exe_sahysmod, nombre)

        # Número de polígonos internos
        símismo.n_polí = None

        # Directorio vacío para guardar datos de ingresos después
        símismo.dic_ingr = {}

        # Poner el directorio de trabajo (donde escribiremos los egresos del modelo), y acordarse de dónde se ubican
        # los datos iniciales.
        símismo.datos_inic = datos_iniciales
        símismo.direc_base = os.path.split(datos_iniciales)[0]

        símismo.arch_egreso = símismo.arch_ingreso = None

        # Estableceremos el directorio para escribir y leer ingresos y egresos según el nombre de la corrida más tarde
        símismo.direc_trabajo = None  # type: str

        # Estableceremos la comanda SAHYSMOD más tarde también
        símismo.comanda = None

        # Inicializar la clase pariente.
        super().__init__(nombre=nombre, archivo=datos_iniciales)

        # Buscar la ubicación del modelo SAHYSMOD.
        símismo.exe_SAHYSMOD = símismo._obt_val_config(
            'exe_SAHYSMOD',
            cond=os.path.isfile,
            mnsj_error=_(
                'Debes especificar la ubicación del ejecutable SAHYSMOD, p. ej.'
                '\n\t"C:\\Camino\\hacia\\mi\\SAHYSMODConsole.exe"'
                '\npara poder hacer simulaciones con modelos SAHYSMOD.')
        )

        # Establecer los variables climáticos.
        símismo.conectar_var_clima(var='Pp - Rainfall', var_clima='Precipitación', combin='total', conv=0.001)

    def _inic_dic_vars(símismo):

        símismo.variables.clear()

        ingresos_no_estacionales = [
            'Kr', 'CrA', 'CrB', 'CrU', 'Cr4', 'Hw', 'C1*', 'C2*', 'C3*', 'Cxf', 'Cxa', 'Cxb', 'Cqf'
        ]

        for nombre, dic in vars_SAHYSMOD.items():
            cód = vars_SAHYSMOD[nombre]['cód']

            if cód[-1] == '#':
                if cód[:-1] in ingresos_no_estacionales:
                    por = 'bloque-egr'
                else:
                    por = 'bloque'
            else:
                por = 'ciclo'

            símismo.variables[nombre] = {
                'val': None,
                'unidades': dic['unids'],
                'ingreso': dic['ingr'],
                'egreso': dic['egr'],
                'líms': dic['líms'] if 'líms' in dic else (None, None),
                'info': '',
                'por': por
            }

    def iniciar_modelo(símismo, n_pasos, t_final, nombre_corrida, vals_inic):

        # Crear un diccionario de trabajo específico a esta corrida.
        símismo.direc_trabajo = os.path.join(símismo.direc_base, '_temp', nombre_corrida)
        if os.path.isdir(símismo.direc_trabajo):
            shutil.rmtree(símismo.direc_trabajo)
        os.makedirs(símismo.direc_trabajo)
        símismo.arch_egreso = os.path.join(símismo.direc_trabajo, 'SAHYSMOD.out')
        símismo.arch_ingreso = os.path.join(símismo.direc_trabajo, 'SAHYSMOD.inp')

        # Generar la comanda de corrida (para después)
        args = dict(SAHYSMOD=símismo.exe_SAHYSMOD, ingreso=símismo.arch_ingreso, egreso=símismo.arch_egreso)
        símismo.comanda = '"{SAHYSMOD}" "{ingreso}" "{egreso}"'.format(**args)

        super().iniciar_modelo(n_pasos, t_final, nombre_corrida, vals_inic)

    def avanzar_modelo(símismo, n_ciclos):

        símismo._escribir_archivo_ingr(n_ciclos=n_ciclos, dic_ingr=símismo.dic_ingr, archivo=símismo.arch_ingreso)

        # Limpiar archivos de egresos que podrían estar allí
        if os.path.isfile(símismo.arch_egreso):
            os.remove(símismo.arch_egreso)

        # Correr la comanda desde la línea de comanda
        run(símismo.comanda, cwd=símismo.direc_trabajo)

        # Verificar que SAHYSMOD generó egresos.
        if not os.path.isfile(símismo.arch_egreso):
            raise FileNotFoundError(_('El modelo SAHYSMOD no genero egreso. Esto probablemente quiere decir que '
                                      'tuvo problema. ¡Diviértete! :)'))

    def cerrar_modelo(símismo):

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

    def unidad_tiempo(símismo):
        return 'mes'

    def obt_tmñ_bloques(símismo):
        return símismo.dur_estaciones

    def _escribir_archivo_ingr(símismo, n_ciclos, dic_ingr, archivo):

        # Establecer el número de años de simulación
        símismo.dic_ingr['NY'] = n_ciclos

        # Copiar datos desde el diccionario de ingresos
        for var, val in dic_ingr.items():
            var_cód = vars_SAHYSMOD[var]['cód']
            llave = var_cód.replace('#', '').upper()

            símismo.dic_ingr[llave] = val

        # Aseguarse que no quedamos con áreas que faltan
        for k in ["A", "B"]:
            vec = símismo.dic_ingr[k]
            vec[vec == -1] = 0

        # Y finalmente, escribir el fuente de valores de ingreso
        escribir_desde_dic_paráms(dic_paráms=símismo.dic_ingr, archivo_obj=archivo)

    def _gen_dic_vals_inic(símismo, archivo=None):

        if archivo is None:
            archivo = símismo.datos_inic

        # Leer el fuente de ingreso
        dic_ingr = leer_info_dic_paráms(archivo_fnt=archivo)
        símismo.dic_ingr.clear()
        símismo.dic_ingr.update(dic_ingr)  # Guardar valores para escribir el fuente de valores iniciales en el futuro

        # Guardar el número de estaciones y de polígonos
        símismo.n_estaciones = int(dic_ingr['NS'])
        símismo.dur_estaciones = [int(float(x)) for x in dic_ingr['TS']]  # La duración de las estaciones (en meses)
        símismo.n_polí = int(dic_ingr['NN_IN'])

        # Asegurar únicamente un año de simulación.
        dic_ingr['NY'] = 1

        # Asegurars que el número de estaciones es igual al número de duraciones de estaciones.
        if símismo.n_estaciones != len(símismo.dur_estaciones):
            raise ValueError(_('Error en el fuente de datos iniciales SAHYSMOD: el número de duraciones de estaciones'
                               'especificadas no corresponde al número de estaciones especificadas (líneas 3 y 4).'))

        # Formatear el diccionario final
        dic_final = {}
        for c in vars_ingreso_SAHYSMOD:
            llave = c.upper().replace('#', '')

            nombre_var = códs_a_vars[c]
            dic_final[nombre_var] = dic_ingr[llave]

        por_bloques = símismo._vars_por_bloques()

        for c in vars_egreso_SAHYSMOD:

            nombre_var = códs_a_vars[c]
            if nombre_var not in dic_final:
                if nombre_var in por_bloques:
                    tmñ = (símismo.n_estaciones, símismo.n_polí)
                else:
                    tmñ = símismo.n_polí
                dic_final[nombre_var] = np.zeros(tmñ)

        return dic_final

    def paralelizable(símismo):
        """
        El modelo SAHYSMOD sí es paralelizable si las corridas tienen nombres distintos.

        Returns
        -------
        bool
            Verdadero
        """

        return True

    def instalado(símismo):
        return símismo.exe_SAHYSMOD is not None

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
