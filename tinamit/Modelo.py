import datetime as ft
from warnings import warn as avisar

import numpy as np
from dateutil.relativedelta import relativedelta as deltarelativo

import tinamit.Geog.Geog as Geog
from tinamit.Unidades.Unidades import convertir


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
        símismo.vars_clima = {}  # Formato: var_intern1: {'nombre_extrn': nombre_oficial, 'combin': 'prom' | 'total'}
        símismo.lugar = None  # type: Geog.Lugar

        # Listas de los nombres de los variables que sirven de conexión con otro modelo.
        símismo.vars_saliendo = []
        símismo.vars_entrando = []

        # Las unidades de tiempo del modelo.
        símismo.unidad_tiempo = símismo.obt_unidad_tiempo()

    def inic_vars(símismo):
        """
        Esta función debe poblar el diccionario de variables del modelo, según la forma siguiente:
        {'var1': {'val': 13, 'unidades': 'cm', 'ingreso': True, dims: (1,), 'egreso': True},
        'var2': {'val': 2, 'unidades': 'cm', 'ingreso': False, dims: (3,2), 'egreso': True}}
        }

        """
        raise NotImplementedError

    def obt_unidad_tiempo(símismo):
        """
        Esta función debe devolver la unidad de tiempo empleada por el modelo.

        :return: La unidad de tiempo (p. ejemplo, 'meses', 'مہینہ', etc.
        :rtype: str

        """
        raise NotImplementedError

    def iniciar_modelo(símismo, tiempo_final, nombre_corrida):
        """
        Esta función llama cualquier acción necesaria para preparar el modelo para la simulación. Esto incluye aplicar
        valores iniciales. En general es muy fácil y se hace simplemente con "símismo.cambiar_vals(símismo.vals_inic)",
        pero para unos modelos (como Vensim) es un poco más delicado así que los dejamos a ti para implementar.

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

    def _limp_vals_inic(símismo):
        """
        Esta función limpa los valores iniciales especificados anteriormente.
        """

        # Limpiar el diccionario.
        for v in símismo.vals_inic.values():
            v.clear()

    def conectar_var_clima(símismo, var, var_clima, combin=None):
        """
        Conecta un variable climático.

        :param var: El nombre interno del variable en el modelo.
        :type var: str
        :param var_clima: El nombre oficial del variable climático.
        :type var_clima: str
        :param combin: Si este variable se debe adicionar o tomar el promedio entre varios pasos.
        :type combin: str

        """
        if var not in símismo.variables:
            raise ValueError('El variable "{}" no existe en este modelo. ¿De pronto lo escribiste mal?'.format(var))
        if var_clima not in Geog.conv_vars:
            raise ValueError('El variable climático "{}" no es una posibilidad. Debe ser uno de:\n'
                             '\t{}'.format(var_clima, ', '.join(Geog.conv_vars)))

        if combin not in ['prom', 'total', None]:
            raise ValueError('"Combin" debe ser "prom", "total", o None, no "{}".'.format(combin))

        símismo.vars_clima[var] = {'nombre_extrn': var_clima,
                                   'combin': combin}

    def desconectar_var_clima(símismo, var):
        """
        Esta función desconecta un variable climático.

        :param var: El nombre interno del variable en el modelo.
        :type var: str

        """

        símismo.vars_clima.pop(var)

    def cambiar_vals(símismo, valores):
        """
        Esta función cambia el valor de uno o más variables del modelo. Cambia primero el valor en el diccionario
        interno del :class:`Modelo`, y después llama la función :func:`~Modelo.Modelo.cambiar_vals_modelo` para cambiar,
        si necesario, los valores de los variables en el modelo externo.

        :param valores: Un diccionario de variables y sus valores para cambiar.
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
        Esta función debe cambia el valor de variables en el :class:`Modelo`, incluso tomar acciones para asegurarse
        de que el cambio se hizo en el modelo externo, si aplica.

        :param valores: Un diccionario de variables y sus valores para cambiar.
        :type valores: dict

        """
        raise NotImplementedError

    def cerrar_modelo(símismo):
        """
        Esta función debe tomar las acciones necesarias para terminar la simulación y cerrar el modelo, si aplica.
        Si no aplica, usar ``pass``.
        """
        raise NotImplementedError

    def act_vals_clima(símismo, n_paso, f):
        """
        Actualiza los variables climáticos. Esta función es la automática para cada modelo. Si necesitas algo más
        complicado (como, por ejemplo, predicciones por estación), la puedes cambiar en tu subclase.

        :param n_paso: El número de pasos para avanzar
        :type n_paso: int
        :param f: La fecha actual.
        :type f: ft.datetime | ft.date
        """

        if not len(símismo.vars_clima):
            return

        # La lista de variables climáticos
        vars_clima = list(símismo.vars_clima)
        nombres_extrn = [d['nombre_extrn'] for d in símismo.vars_clima.values()]

        # La lista de maneras de combinar los valores diarios
        combins = [d['combin'] for d in símismo.vars_clima.values()]

        # La fecha final
        if símismo.unidad_tiempo == 'Días':
            f_final = f + deltarelativo(days=+n_paso)
            n_meses = n_paso / 30
        else:
            try:
                n_meses = convertir(de=símismo.unidad_tiempo, a='Mes', val=n_paso)
                if int(n_meses) != n_meses:
                    avisar('Tuvimos que redondear la unidad de tiempo, {} {}, a {} meses'.
                           format(n_meses, símismo.unidad_tiempo, int(n_meses)))
            except ValueError:
                raise ValueError('La unidad de tiempo "{}" no se pudo convertir a meses.')

            f_final = f + deltarelativo(months=n_meses)

        if n_meses > 1:
            avisar('El paso ({} {}) es superior a 1 mes. Puede ser que las predicciones climáticas pierdan '
                   'en precisión.'
                   .format(n_paso, símismo.unidad_tiempo))

        # Calcular los datos
        datos = símismo.lugar.comb_datos(vars_clima=nombres_extrn, combin=combins,
                                         f_inic=f, f_final=f_final)

        # Aplicar los valores de variables calculados
        for i, var in enumerate(vars_clima):
            # Para cada variable en la lista de clima...

            # El nombre oficial del variable de clima
            var_clima = nombres_extrn[i]

            # Aplicar el cambio
            símismo.cambiar_vals(valores={var: datos[var_clima]})
