

class Modelo(object):
    """
    Todas las cosas en Tinamit son instancias de Modelo, que sea un modelo de dinámicas de los sistemas, un modelo de
    cultivos o de suelos o de clima, o un modelo conectado.
    Cada tipo de modelo se representa por subclases específicas. Por eso, la gran mayoría de los métodos definidos
    aquí se implementan de manera independiente en cada
    """

    def __init__(símismo, nombre):
        """

        :param nombre: El nombre del modelo. Sirve para identificar distintos modelos en un modelo conectado.
        :type nombre: str

        """

        # No se puede incluir nombres de modelos con "_" en el nombre (podría corrumpir el manejo de variables en
        # modelos jerarquizados).
        if "_" in nombre:
            raise ValueError('No se pueden emplear nombres de modelos con "_".')

        # El nombre del modelo (sirve como una referencia a este modelo en el modelo conectado).
        símismo.nombre = nombre

        # El diccionario de variables necesita la forma siguiente. Se llena con la función símismo.inic_vars().
        # {var1: {'val': 13, 'unidades': cm, 'ingreso': True, 'egreso': True},
        #  var2: {...},
        #  ...}
        símismo.variables = {}
        símismo.inic_vars()

        # Listas de los nombres de los variables que sirven de conexión con otro modelo.
        símismo.vars_saliendo = []
        símismo.vars_entrando = []

        # Las unidades de tiempo del modelo.
        símismo.unidad_tiempo = símismo.obt_unidad_tiempo()

    def inic_vars(símismo):
        """
        Esta función debe poblar el diccionario de variables del modelo, según la forma siguiente::
            {'var1': {'val': 13, 'unidades': 'cm', 'ingreso': True, 'egreso': True},
            'var2': {'val': 2, 'unidades': 'cm', 'ingreso': False, 'egreso': True}}
            }

        """
        raise NotImplementedError

    def obt_unidad_tiempo(símismo):
        """
        Esta función debe devolver la unidad de tiempo empleada por el modelo.

        :return: La unidad de tiempo (p. ejemplo, 'meses', 'días', etc.
        :rtype: str

        """
        raise NotImplementedError

    def iniciar_modelo(símismo, tiempo_final, nombre_corrida):
        """
        Esta función llama cualquier acción necesaria para preparar el modelo para la simulación.
        Si no es necesario, usar "pass".

        :param tiempo_final: El tiempo final de la simulación.
        :type tiempo_final: int

        :param nombre_corrida: El nombre de la corrida (generalmente para guardar resultados).
        :type nombre_corrida: str

        """
        raise NotImplementedError

    def incrementar(símismo, paso):
        """
        Esta función debe avanzar el modelo por un periodo de tiempo especificado.

        :param paso: El paso.
        :type paso: int

        """
        raise NotImplementedError

    def leer_vals(símismo):
        """
        Esta función debe leer los valores del modelo y escribirlos en el diccionario interno de variables. Se
        implementa frequentement con modelos externos de cuyos egresos hay que leer los resultados de una corrida.

        """
        raise NotImplementedError

    def cambiar_vals(símismo, valores):
        """
        Esta función cambiar el calor de uno o más variables del modelo. Cambia primero el valor en el diccionario
        interno del :class:`Modelo`, y después llama la función :func:`~Modelo.Modelo.cambiar_vals_modelo` para cambiar,
        si necesario, los valores de los variables en el modelo externo.

        :param valores: Un diccionario de variables y valores para cambiar, con el formato siguiente:
        { var1: nuevovalor,
          var2: nuevovalor,
          ...
        }
        :type valores: dict

        """

        for var in valores:
            símismo.variables[var]['val'] = valores[var]

        símismo.cambiar_vals_modelo(valores=valores)

    def cambiar_vals_modelo(símismo, valores):
        """
        Esta función debe cambiar el valor de variables en el :class:`Modelo`, incluso tomar acciones para asegurarse
        de que el cambio se hizo en el modelo externo, si aplica.

        :param valores: Un diccionario de variables y valores para cambiar, con el formato siguiente:
        { var1: nuevovalor,
          var2: nuevovalor,
          ...
        }
        :type valores: dict

        """
        raise NotImplementedError

    def cerrar_modelo(símismo):
        """
        Esta función debe tomar las acciones necesarias para terminar la simulación y cerrar el modelo, si aplica.
        Si no aplica, usar "pass".
        """
        raise NotImplementedError
