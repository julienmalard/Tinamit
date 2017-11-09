import numpy as np
from warnings import warn as avisar


class Modelo(object):
    """
    Todas las cosas en Tinamit son instancias de `Modelo`, que sea un modelo de dinámicas de los sistemas, un modelo de
    cultivos o de suelos o de clima, o un modelo conectado.
    Cada tipo de modelo se representa por subclases específicas. Por eso, la gran mayoría de los métodos definidos
    aquí se implementan de manera independiente en cada subclase de `Modelo`.
    """

    def __init__(símismo, nombre):
        """
        La función de inicialización de todos modelos, conectados o no.

        :param nombre: El nombre del modelo. Sirve para identificar distintos modelos en un modelo conectado.
        :type nombre: str

        """

        # No se puede incluir nombres de modelos con "_" en el nombre (podría corrumpir el manejo de variables en
        # modelos jerarquizados).
        if "_" in nombre:
            avisar('No se pueden emplear nombres de modelos con "_", así que no puedes nombrar tu modelo"{}".\n'
                   'Sino, causaría problemas de conexión de variables por una razón muy compleja y oscura.\n'
                   'Vamos a renombrar tu modelo "{}". Lo siento.'.format(nombre, nombre.replace('_', '.')))

        # El nombre del modelo (sirve como una referencia a este modelo en el modelo conectado).
        símismo.nombre = nombre

        # El diccionario de variables necesita la forma siguiente. Se llena con la función símismo.inic_vars().
        # {var1: {'val': 13, 'unidades': cm, 'ingreso': True, 'egreso': True},
        #  var2: {...},
        #  ...}
        símismo.variables = {}
        símismo.inic_vars()

        # Un diccionarior para guardar valores de variables iniciales hasta el momento que empezamos la simulación.
        # Es muy útil para modelos cuyos variables no podemos cambiar antes de empezar una simulación (como VENSIM).
        símismo.vals_inic = {}

        # Listas de los nombres de los variables que sirven de conexión con otro modelo.
        símismo.vars_saliendo = []
        símismo.vars_entrando = []

        # Las unidades de tiempo del modelo.
        símismo.unidad_tiempo = símismo.obt_unidad_tiempo()

    def inic_vars(símismo):
        """
        Esta función debe poblar el diccionario de variables del modelo, según la forma siguiente::
            {'var1': {'val': 13, 'unidades': 'cm', 'ingreso': True, dims: (1,), 'egreso': True},
            'var2': {'val': 2, 'unidades': 'cm', 'ingreso': False, dims: (3,2), 'egreso': True}}
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
        Esta función llama cualquier acción necesaria para preparar el modelo para la simulación. Esto incluye aplicar
        valores iniciales. En general es muy fácil y se hace simplemente con "símismo.cambiar_vals(símismo.vals_inic)",
        pero para unos modelos　(como Vensim) es un poco distinto así que los dejamos a ti para implementar.

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

    def inic_val(símismo, var, val):
        """
        Est método cambia el valor inicial de un variable (antes de empezar la simulación). Se emplea principalmente
        para activar y desactivar políticas y para establecer parámetros y valores iniciales para simulaciones.

        :param var: El nombre del variable para cambiar.
        :type var: str

        :param val: El nuevo valor del variable.
        :type val: float

        """

        # Primero, asegurarse que el variable existe.
        if var not in símismo.variables:
            raise ValueError('El variable inicializado "{}" no existe en los variables del modelo.\n'
                             'Pero antes de quejarte al gerente, sería buena idea verificar '
                             'si lo escrbiste bien.'.format(var))  # Sí, lo "escrbí" así por propósito. :)

        # Guardamos el valor en el diccionario `vals_inic`. Se aplicarán los valores iniciales únicamente al momento
        # de empezar la simulación.
        símismo.vals_inic[var] = val

    def limp_vals_inic(símismo):
        """
        Esta función limpa los valores iniciales especificados anteriormente.
        """

        # Limpiar el diccionario.
        símismo.vals_inic.clear()

    def cambiar_vals(símismo, valores):
        """
        Esta función cambiar el calor de uno o más variables del modelo. Cambia primero el valor en el diccionario
        interno del :class:`Modelo`, y después llama la función :func:`~Modelo.Modelo.cambiar_vals_modelo` para cambiar,
        si necesario, los valores de los variables en el modelo externo.

        :param valores: Un diccionario de variables y valores para cambiar, con el formato siguiente:
        >>> {'var1': 10,  'var2': 15,
        >>>    ...
        >>>    }
        :type valores: dict

        """

        for var in valores:
            if isinstance(símismo.variables[var]['val'], np.ndarray):
                símismo.variables[var]['val'][:] = valores[var]
            else:
                símismo.variables[var]['val'] = valores[var]

        símismo.cambiar_vals_modelo_interno(valores=valores)

    def cambiar_vals_modelo_interno(símismo, valores):
        """
        Esta función debe cambiar el valor de variables en el :class:`Modelo`, incluso tomar acciones para asegurarse
        de que el cambio se hizo en el modelo externo, si aplica.

        :param valores: Un diccionario de variables y valores para cambiar, con el formato siguiente:
        >>> {'var1': 10,  'var2': 15,
        >>>    ...
        >>>    }
        :type valores: dict

        """
        raise NotImplementedError

    def cerrar_modelo(símismo):
        """
        Esta función debe tomar las acciones necesarias para terminar la simulación y cerrar el modelo, si aplica.
        Si no aplica, usar ``pass``.
        """
        raise NotImplementedError
