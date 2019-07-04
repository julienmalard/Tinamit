import os
import shutil
import tempfile
from subprocess import run

import numpy as np
from pkg_resources import resource_filename

from tinamit.config import _
from tinamit.envolt.bf import ModeloBloques
from ._arch_egr import leer_arch_egr
from ._arch_ingr import leer_info_dic_paráms, escribir_desde_dic_paráms
from ._vars import VariablesSAHYSMOD, VarBloqSAHYSMOD


class ModeloSAHYSMOD(ModeloBloques):
    """
    Envoltura para modelos SAHYSMOD.
    """

    idioma_orig = 'en'  # La lengua de los nombres y descripción de los variables (y NO la del código aquí)

    def __init__(símismo, archivo, nombre='SAHYSMOD'):

        símismo.archivo = archivo

        símismo.direc_trabajo = ''

        # Directorio vacío para guardar datos de ingresos después
        símismo.dic_ingr = {}

        # Buscar la ubicación del modelo SAHYSMOD.
        símismo.exe_SAHYSMOD = símismo.obt_conf(
            'exe',
            cond=os.path.isfile,
            mnsj_err=_(
                'Debes especificar la ubicación del ejecutable SAHYSMOD, p. ej.'
                '\n\tModeloSAHYSMOD.estab_conf("exe", "C:\\Camino\\hacia\\mi\\SAHYSMODConsole.exe")'
                '\npara poder hacer simulaciones con modelos SAHYSMOD.'
            )
        )

        # Leer el fuente de ingreso
        símismo.dic_ingr = leer_info_dic_paráms(archivo_fnt=símismo.archivo)

        variables = VariablesSAHYSMOD(inic=símismo.dic_ingr)

        # Inicializar la clase pariente.
        super().__init__(variables=variables, nombre=nombre)

        # Establecer los variables climáticos.
        símismo.conectar_var_clima(var='Pp - Rainfall', var_clima='بارش', combin='total', conv=0.001)

    def iniciar_modelo(símismo, corrida):

        # Crear un diccionario de trabajo específico a esta corrida.
        símismo.direc_trabajo = tempfile.mkdtemp('_' + str(corrida))
        super().iniciar_modelo(corrida)

    def avanzar_modelo(símismo, n_ciclos):
        arch_egreso = os.path.join(símismo.direc_trabajo, 'SAHYSMOD.out')
        arch_ingreso = os.path.join(símismo.direc_trabajo, 'SAHYSMOD.inp')

        símismo._escribir_archivo_ingr(n_ciclos=n_ciclos, archivo=arch_ingreso)

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
            with open(os.path.join(símismo.direc_trabajo, 'error.lst')) as d:
                mnsj_sahysmod = d.readlines()

            raise FileNotFoundError(_(
                '\nEl modelo SAHYSMOD no generó egreso. Esto probablemente quiere decir que tuvo problema interno.'
                '\n¡Diviértete! :)'
                '\nMensajes de error de SAHYSMOD:'
                '\n{}').format(mnsj_sahysmod))

        símismo.leer_egr_modelo(n_ciclos=n_ciclos)

    def cerrar(símismo):
        shutil.rmtree(símismo.direc_trabajo)

    def leer_egr_modelo(símismo, n_ciclos):
        archivo = os.path.join(símismo.direc_trabajo, 'SAHYSMOD.out')

        dic_egr = leer_arch_egr(
            archivo=archivo, años=n_ciclos
        )

        # Convertir códigos de variables a nombres de variables
        for c, v in dic_egr.items():
            símismo.variables.cód_a_var[c].poner_val(v[0])  # v[0] para quitar dimensión de año

    @classmethod
    def instalado(cls):
        return cls.obt_conf('exe') is not None

    def paralelizable(símismo):
        return True

    def unidad_tiempo(símismo):
        return 'mes'

    @classmethod
    def prb_egreso(cls):
        arch = resource_filename(__name__, 'rcrs/prb_egresos.out')

        return arch, leer_arch_egr

    @classmethod
    def prb_ingreso(cls):
        arch = resource_filename(__name__, 'rcrs/prb_ingresos.inp')

        def f(a):
            return VariablesSAHYSMOD(leer_info_dic_paráms(a))

        return arch, f

    @classmethod
    def prb_simul(cls):
        return resource_filename(__name__, 'rcrs/prb_ingresos.inp')

    def _escribir_archivo_ingr(símismo, n_ciclos, archivo):

        # Establecer el número de años de simulación
        símismo.dic_ingr['NY'] = n_ciclos

        # Copiar datos desde el diccionario de ingresos
        for var in símismo.variables.egresos():
            llave = var.cód.replace('#', '').upper()
            if llave in símismo.dic_ingr:
                m = símismo.dic_ingr[llave]

                if isinstance(var, VarBloqSAHYSMOD):
                    val = var.obt_vals_paso()
                    if m.shape == val.shape:
                        m[:] = val
                    else:
                        m[:] = val[-1]
                else:
                    val = var.obt_val()
                    m[:] = val
                m[np.isnan(m)] = -1

        # Y finalmente, escribir el fuente de valores de ingreso
        escribir_desde_dic_paráms(dic_paráms=símismo.dic_ingr, archivo_obj=archivo)
