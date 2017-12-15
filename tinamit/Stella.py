from .MDS import EnvolturaMDS


class modelo_Stella(EnvolturaMDS):

    import rpy2
    from rpy2.rinterface import R_VERSION_BUILD
    import rpy2.robjects as robjects

    def __init__(símismo):
        # iniciar el modelo R desde rpy 2

        # paso para incrementar
        # iniciar modelo como una envoltura MDS
        super().__init__()

    def inic_vars(símismo):
        # iniciar el diccionario de variables
        # verificar el tamaño de memoria
        # guardar el nombre de las variables
        # identificar las unidades y dimensiones de las variables, y los constantes
        # guardar los constantes en una lista

    def obt_unidad_tiempo(símismo):
        # obtener las unidades de tiempo

    def iniciar_modelo(símismo, nombre_corrida, tiempo_final):
        # nombre de la corrida
        # definir el tiempo final
        # iniciar una simulación para actualizar los valores

    def cambiar_vals_modelo_interno(símismo, valores):
        # permite cambiar los valores de las variables internas del modelo
        # definir las variables que se pueden cambiar en un diccionario
        # cambiar los valores

    def incrementar(símismo, paso):
        # definir el paso
        # avanzar la simulación por cada paso

    def leer_vals(símismo):
        # leer los valores intermediarios de la simulación
        # guardar los valores

    def cerrar_modelo(símismo):
        # cerrar la simulación


