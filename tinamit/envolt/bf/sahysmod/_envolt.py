import os
import re
import shutil
import tempfile
from subprocess import run

from tinamit.config import _
from tinamit.envolt.bf import ModeloBloques
from ._arch_egr import leer_arch_egr, procesar_cr
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

        # Guardar el número de estaciones y de polígonos
        n_estaciones = int(símismo.dic_ingr['NS'])
        dur_estaciones = [int(float(x)) for x in símismo.dic_ingr['TS']]  # La duración de las estaciones (en meses)
        n_polí = int(símismo.dic_ingr['NN_IN'])

        # Asegurarse que el número de estaciones es igual al número de duraciones de estaciones.
        if n_estaciones != len(dur_estaciones):
            raise ValueError(
                _('Error en el fuente de datos iniciales SAHYSMOD: el número de duraciones de estaciones'
                  'especificadas no corresponde al número de estaciones especificadas (líneas 3 y 4).')
            )

        variables = VariablesSAHYSMOD(dims=(n_polí,), tmñ_bloques=dur_estaciones)

        # Inicializar la clase pariente.
        super().__init__(tmñ_bloques, variables=variables, nombre=nombre)

        # Establecer los variables climáticos.
        símismo.conectar_var_clima(var='Pp - Rainfall', var_clima='Precipitación', combin='total', conv=0.001)

    def iniciar_modelo(símismo, corrida):

        # Crear un diccionario de trabajo específico a esta corrida.
        símismo.direc_trabajo = tempfile.mkdtemp(str(corrida))

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
            raise FileNotFoundError(
                _('El modelo SAHYSMOD no generó egreso. Esto probablemente quiere decir que tuvo problema interno.'
                  '\n¡Diviértete! :)')
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
            archivo=archivo, n_est=símismo.n_estaciones, n_polí=símismo.n_polí, años=[n_ciclos]
        )

        procesar_cr(dic_egr)

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

    def _escribir_archivo_ingr(símismo, n_ciclos, archivo):

        # Establecer el número de años de simulación
        símismo.dic_ingr['NY'] = n_ciclos

        # Copiar datos desde el diccionario de ingresos
        for var in símismo.variables.egresos():
            if isinstance(var, VarBloqSAHYSMOD):
                val = var.obt_val()
            else:
                val = var.obt_val_t()  # para hacer

            llave = var.código.replace('#', '')
            símismo.dic_ingr[llave] = val

        # Y finalmente, escribir el fuente de valores de ingreso
        escribir_desde_dic_paráms(dic_paráms=símismo.dic_ingr, archivo_obj=archivo)
