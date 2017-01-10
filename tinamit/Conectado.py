import threading
from warnings import warn as avisar

from tinamit.BF import EnvolturaBF
from tinamit.Modelo import Modelo
from tinamit.MDS import generar_mds
from tinamit.Unidades.Unidades import convertir


class SuperConectado(Modelo):
    """
    Esta clase representa el más alto nivel posible de modelo conectado. Tiene la función muy útil de poder conectar
    instancias de sí misma, así permitiendo la conexión de números arbitrarios de modelos.
    """

    def __init__(símismo, nombre="SuperConectado"):
        """
        El nombre automático para este modelo es "SuperConectado". Si vas a conectar más que un modelo SuperConectado,
        asegúrate de darle un nombre distinto al menos a un de ellos.

        :param nombre: El nombre del modelo SuperConectado.
        :type nombre: str

        """

        # Un diccionario de los modelos que se van a conectar en este modelo. Tiene la forma general
        # {'nombre_modelo': objecto_modelo,
        #  'nombre_modelo_2': objecto_modelo_2}
        símismo.modelos = {}

        # Una lista de las conexiones entre los modelos.
        símismo.conexiones = []

        # Un diccionario para aceder rápidamente a las conexiones.
        símismo.conex_rápida = {}

        # Un diccionario con la información de conversiones de unidades de tiempo entre los dos modelos conectados.
        # Tiene la forma general:
        # {'nombre_modelo_1': factor_conv,
        # {'nombre_modelo_2': factor_conv}
        # Al menos uno de los dos factores siempre será = a 1.
        símismo.conv_tiempo = {}

        # Inicializamos el SuperConectado como todos los Modelos.
        super().__init__(nombre=nombre)

    def estab_modelo(símismo, modelo):
        """
        Esta función agrega un modelo al SuperConectado. Una vez que dos modelos estén agregados, se pueden conectar
        y simular juntos.

        :param modelo: El modelo para agregar.
        :type modelo: Modelo

        """

        # Si ya hay dos modelos conectados, no podemos conectar un modelo más.
        if len(símismo.modelos) >= 2:
            raise ValueError('Ya hay dos modelo conectados. Desconecta uno primero o emplea una instancia de'
                             'SuperConectado para conectar más que 2 modelos.')

        # Si ya se conectó otro modelo con el mismo nombre, avisarlo al usuario.
        if modelo.nombre in símismo.modelos:
            avisar('El modelo {} ya existe. El nuevo modelo reemplazará el modelo anterior.'.format(modelo.nombre))

        # Agregar el nuevo modelo al diccionario de modelos.
        símismo.modelos[modelo.nombre] = modelo

        # Ahora, tenemos que agregar los variables del modelo agregado al diccionaro de variables de este modelo
        # también. Se prefija el nombre del modelo al nombre de su variable para evitar posibilidades de nombres
        # desduplicados.
        for var in modelo.variables:
            nombre_var = '{mod}_{var}'.format(var=var, mod=modelo.nombre)
            símismo.variables[nombre_var] = modelo.variables[var]

        # Establecemos las unidades de tiempo del modelo SuperConectado según las unidades de tiempo de sus submodelos.
        símismo.unidad_tiempo = símismo.obt_unidad_tiempo()




class Conectado(SuperConectado):
    """
    Esta clase representa un tipo especial de modelo SuperConectado: la conexión entre un modelo biofísico y un modelo
    DS.
    """

    def __init__(símismo):
        """
        Inicializar el modelo Conectado.
        """

        # Referencias rápidas a los submodelos.
        símismo.mds = None
        símismo.bf = None

        # Inicializar este como su clase superior.
        super().__init__()

    def estab_mds(símismo, archivo_mds):
        """
        Establecemos el modelo DS.

        :param archivo_mds: El archivo del modelo DS.
        :type archivo_mds: str

        """

        # Generamos un objeto de modelo DS.
        modelo_mds = generar_mds(archivo=archivo_mds)

        # Conectamos el modelo DS.
        símismo.estab_modelo(modelo=modelo_mds)

        # Y hacemos la referencia rápida.
        símismo.mds = modelo_mds

    def estab_bf(símismo, archivo_bf):
        """
        Establece el modelo biofísico.

        :param archivo_bf: El archivo con la clase del modelo biofísico. **Debe** ser un archivo de Python.
        :type archivo_bf: str

        """

        # Creamos una instancia de la Envoltura BF con este modelo.
        modelo_bf = EnvolturaBF(archivo=archivo_bf)

        # Conectamos el modelo biofísico.
        símismo.estab_modelo(modelo=modelo_bf)

        # Y guardamos la referencia rápida.
        símismo.bf = modelo_bf

    def conectar(símismo, var_mds, var_bf, mds_fuente, conv=None):
        """
        Una función para conectar variables entre el modelo biofísico y el modelo DS.

        :param var_mds: El nombre del variable en el modelo DS.
        :type var_mds: str

        :param var_bf: El nombre del variable correspondiente en el modelo biofísico.
        :type var_bf: str

        :param mds_fuente: Si True, el modelo DS es el modelo fuente para la conexión. Sino, será el modelo
        biofísico.
        :type mds_fuente: bool

        :param conv: El factor de conversión entre los variables.
        :type conv: float

        """

        # Hacer el diccionario necesario para especificar la conexión.
        dic_vars = {'mds': var_mds, 'bf': var_bf}

        # Establecer el modelo fuente.
        if mds_fuente:
            fuente = 'mds'
        else:
            fuente = 'bf'

        # Llamar la función apropiada de la clase superior.
        símismo.conectar_vars(dic_vars=dic_vars, modelo_fuente=fuente, conv=conv)

    def desconectar(símismo, var_mds):
        """
        Esta función deshacer una conexión entre el modelo biofísico y el modelo DS. Se especifica la conexión por
        el nombre del variable en el modelo DS.

        :param var_mds: El nombre del variable conectado en el modelo DS.
        :type var_mds: str

        """

        # Llamar la función apropiada de la clase superior.
        símismo.desconectar_vars(var_fuente=var_mds, modelo_fuente='mds')
