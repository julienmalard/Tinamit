import shutil
import tempfile
from subprocess import Popen

from tinamit3.envolt.enchufe import SimulEnchufe
from tinamit3.mod import Modelo


class SimulSwatPlusEnchufe(SimulEnchufe):
    def __init__(símismo, modelo, corrida):
        
        super().__init__(modelo=modelo, corrida=corrida)

        # Crear un diccionario de trabajo específico a esta corrida.
        símismo.dir_trabajo = tempfile.mkdtemp('_' + str(hash(corrida)))

    def iniciar_proceso(símismo):
        símismo._escribir_archivos_ingreso()
        return Popen(
            [símismo.modelo.exe, "--p", str(símismo.puerto)],
            cwd=símismo.dir_trabajo
        )

    def _escribir_archivos_ingreso(símismo):
        pass

    def cerrar(símismo):
        shutil.rmtree(símismo.dir_trabajo)


class ModeloSwatPlusEnchufe(Modelo):
    simulador = SimulSwatPlusEnchufe

    def __init__(símismo, archivo, nombre='SWAT+', exe=None):
        símismo.archivo = archivo
        variables =
        super().__init__(nombre, variables=variables)

    @property
    def unids(símismo):
        return 'mes'
