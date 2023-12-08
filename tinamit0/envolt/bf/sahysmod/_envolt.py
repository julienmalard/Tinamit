import os

from pkg_resources import resource_filename

from tinamit.config import _
from tinamit.envolt.bf import ModeloBloques
from ._arch_egr import leer_arch_egr
from ._arch_ingr import leer_info_dic_paráms
from ._vars import VariablesSAHYSMOD


class ModeloSAHYSMOD(ModeloBloques):
    """
    Envoltura para modelos SAHYSMOD.
    """

    idioma_orig = 'en'  # La lengua de los nombres y descripción de los variables (y NO la del código aquí)

    def __init__(símismo, archivo, nombre='SAHYSMOD'):
        # Buscar la ubicación del modelo SAHYSMOD.
        símismo.exe_SAHYSMOD = símismo.obt_conf(
            'exe',
            cond=os.path.isfile,
            mnsj_err=_(
                '\nDebes especificar la ubicación del ejecutable SAHYSMOD, p. ej.'
                '\n\tModeloSAHYSMOD.estab_conf("exe", "C:\\Camino\\hacia\\mi\\SAHYSMODConsole.exe")'
                '\npara poder hacer simulaciones con modelos SAHYSMOD.'
                '\nSi no instalaste SAHYSMOD, lo puedes conseguir para Linux, Mac o Windows de '
                'https://github.com/julienmalard/sahysmod-sourcecode.'
            )
        )

    @classmethod
    def instalado(cls):
        return cls.obt_conf('exe') is not None

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
