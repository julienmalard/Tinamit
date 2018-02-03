from tinamit.MDS.MDS import EnvolturaMDS
from tinamit.MDS._StellaR import run as correr_stellar  # Importamos una copia local de Stellar

# Importamos todo al principio
import os, site
# os.environ['R_HOME'] = 'C:\Program Files\Microsoft\R Open\R-3.4.0'
# Si tienes problemas, activar la línea arriba con tu instalación de R
os.environ['R_USER'] = os.path.join(site.getsitepackages()[0], 'rpy2')

import rpy2.robjects as robjects
# encapsulación de paquetes de funciones de R en una forma amigable para Python
from rpy2.robjects.vectors import DataFrame
from rpy2.robjects.packages import importr, data
from rpy2.robjects.vectors import StrVector

# importar el módulo de paquetes de rpy2
import rpy2.robjects.packages as rpackages

# Hagamos todas las cosa que solamente tenemos que hacer una vez aquí. Si las ponemos en modelo_Stella,
# se repetirán cada vez que creamos un nuevo modelo, lo cual no querremos.

# Instalar paquetes de R que faltan
paq_r = ['deSolve']
para_instalar = [p for p in paq_r if not rpackages.isinstalled(p)]
if len(para_instalar) > 0:
    # importar paquete de R utils
    utils = rpackages.importr('utils')

    # seleccionar un espejo para paquetes de R, selecciona el primero
    utils.chooseCRANmirror(ind=1)

    # Instalar
    utils.install_packages(StrVector(para_instalar))

importr('deSolve')


class ModeloStella(EnvolturaMDS):

    def __init__(símismo, archivo):

        # Primero tenemos que crear el modelo en R a base del archivo. Para que funcione StellaR no deben haber tildes
        direc, arch = os.path.split(archivo)
        nombre_mod = os.path.splitext(arch)[0]
        dir_egr = os.path.join(direc, nombre_mod)
        correr_stellar(archivo, dir_egr)

        # Aquí guardamos todo el modelo, formato texto de R, en símismo.mod_txt
        with open(os.path.join(dir_egr, nombre_mod + '.R')) as d:
            símismo.mod_txt = d.readlines()

        # iniciar modelo como una envoltura MDS
        super().__init__(archivo=archivo)

    def inic_vars(símismo):
        # iniciar el diccionario de variables
        # verificar el tamaño de memoria
        # guardar el nombre de las variables
        # identificar las unidades y dimensiones de las variables, y las constantes
        # guardar las constantes en una lista

        variables = {}
        # este es el diccionario con los distintos tipos de variables
        flujos = []
        # flujos y otras variables dinámicas los lee igual R creo

        unidades = []
        constantes = []
        # las constantes, o parámetros los lee en: parms <- c()

        niveles = []
        # stocks están en la lista Y <- ()

        # Aquí puedes leer símismo.mod_txt para
        for line in símismo.mod_txt:
            if "parms <-" in line:
                constantes.append(line)
            elif "Y <-" in line:
                niveles.append(line)
            else:
                flujos.append(line)

        # también podrían leerse las líneas del modelo en R(que son variables, algunas repetidas) como objetos R,
        # tal vez se pueden leer mejor

        pass

    def obt_unidad_tiempo(símismo):
        # obtener las unidades de tiempo

        # De pronto tendrás que incluir una función para que el usuario lo especifique. No aparece esta información en
        # el archivo de Stella
        pass

    def iniciar_modelo(símismo, nombre_corrida, tiempo_final):
        # nombre de la corrida
        # definir el tiempo final
        # iniciar una simulación para actualizar los valores

        # guardar una referencia (con símismo) a nombre_corrida y tiempo_final.
        pass

    def cambiar_vals_modelo_interno(símismo, valores):
        # permite cambiar los valores de las variables internas del modelo
        # definir las variables que se pueden cambiar en un diccionario
        # cambiar los valores

        # Cambiar valores de parámetros en mod_txt
        pass

    def incrementar(símismo, paso):
        # definir el paso
        # avanzar la simulación por cada paso

        # generar un archivo como mod_txt, pero modificado con paso, nombre_corrida y tiempo_final.

        # Después, ejecutar el modelo con rpy2
        pass

    def leer_vals(símismo):
        # leer los valores intermediarios de la simulación
        # guardar los valores

        # Leer los valores desde rpy2
        pass

    def cerrar_modelo(símismo):
        # cerrar la simulación


        pass


