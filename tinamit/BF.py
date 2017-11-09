import os
import sys
from importlib import import_module as importar_mod

import numpy as np

from tinamit.Modelo import Modelo
from .Unidades.Unidades import convertir


class EnvolturaBF(Modelo):
    """
    Esta clase ofrece una envoltura para **TODOS** tipos de modelos biofísicos.

    Modelos biofísicos específicos se implementan por crear una subclase de `~tinamit.BF.ClaseModeloBF` específica
    para ellos.
    """

    def __init__(símismo, archivo):
        """
        Incializar la envoltura.

        :param archivo: El archivo con el
        :type archivo: str

        """

        dir_mod, nombre_mod = os.path.split(archivo)
        sys.path.append(dir_mod)

        módulo = importar_mod(os.path.splitext(nombre_mod)[0])

        try:
            modelo = módulo.Modelo  # type: ModeloBF
        except AttributeError:
            raise AttributeError('El archivo especificado ({}) no contiene una clase llamada Modelo.'.format(archivo))

        if callable(modelo):
            símismo.modelo = modelo()
        else:
            símismo.modelo = modelo

        if not isinstance(símismo.modelo, ModeloBF):
            raise TypeError('El archivo especificado ("{}") contiene una clase llamada Modelo, pero'
                            'esta clase no es una subclase de ClaseModeloBF.'.format(archivo))

        super().__init__(nombre='bf')

        símismo.vars_entrando = símismo.modelo.vars_entrando
        símismo.vars_saliendo = símismo.modelo.vars_saliendo

    def obt_unidad_tiempo(símismo):
        """
        Esta función debe devolver la unidad de tiempo empleada por el modelo.

        :return: La unidad de tiempo (p. ejemplo, 'meses', 'días', etc.
        :rtype: str

        """

        return símismo.modelo.unidad_tiempo

    def inic_vars(símismo):
        """
        Inicializa los variables del modelo biofísico y los conecta al diccionario de variables del modelo.

        """

        # Crear el vínculo
        símismo.variables = símismo.modelo.variables

    def cambiar_vals_modelo_interno(símismo, valores):
        """
        Esta función cambia el valor de variables en el modelo.

        :param valores: Un diccionario de variables y valores para cambiar, con el formato siguiente:
        >>> {'var1': 10,  'var2': 15,
        >>>    ...
        >>>    }
        :type valores: dict

        """

        símismo.modelo.cambiar_vals(valores=valores)

    def incrementar(símismo, paso):
        """
        Esta función avanza el modelo por un periodo de tiempo especificado en `paso`.

        :param paso: El paso.
        :type paso: int

        """

        símismo.modelo.incrementar(paso=paso)

    def leer_vals(símismo):
        """
        Esta función lee los valores del modelo y los escribe en el diccionario interno de variables.

        """
        símismo.modelo.leer_vals()

    def iniciar_modelo(símismo, **kwargs):
        """
        Inicializa el modelo biofísico interno, incluyendo la inicialización de variables.

        :param kwargs: Argumentos para pasar al modelo interno.

        """

        # Aplicar valores iniciales antes de la inicialización del modelo. Simplemente llamamos la función
        # símismo.cambiar_vals() con el diccionario de valores iniciales.
        símismo.cambiar_vals(símismo.vals_inic)

        # ...y inicializar el modelo.
        símismo.modelo.iniciar_modelo(**kwargs)

    def cerrar_modelo(símismo):
        """
        Cierre el modelo interno.
        """

        símismo.modelo.cerrar_modelo()


class ModeloBF(Modelo):
    """
    Se debe desarrollar una subclase de esta clase para cada tipo modelo biofísico que se quiere volver compatible
    con Tinamit.
    """

    def __init__(símismo):
        """
        Esta función correrá automáticamente con la inclusión de `super().__init__()` en la función `__init__()` de las
        subclases de esta clase.
        """
        super().__init__(nombre='modeloBF')

    def cambiar_vals_modelo_interno(símismo, valores):
        """
        Esta función debe cambiar el valor de variables en el modelo biofísico.

        :param valores: Un diccionario de variables y valores para cambiar, con el formato siguiente:
        >>> {'var1': 10,  'var2': 15,
        >>>    ...
        >>>    }
        :type valores: dict

        """
        raise NotImplementedError

    def incrementar(símismo, paso):
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

    def leer_vals(símismo):
        """
        Esta función debe leer los variables del modelo desde el modelo externo y copiarlos al diccionario interno
        de variables. Asegúrese que esté *actualizando* el diccionario interno, y que no lo esté recreando, lo cual
        quebrará las conexiones con el modelo conectado.
        """
        raise NotImplementedError

    def iniciar_modelo(símismo, **kwargs):
        """
        Esta función debe preparar el modelo para una simulación.
        
        :param kwargs:
        :type kwargs:
        """

        raise NotImplementedError

    def cerrar_modelo(símismo):
        """
        Esta función debe cerrar la simulación. No se aplica a todos los modelos biofísicos (en ese caso, usar ``pass``
        ).
        """
        raise NotImplementedError

    def obt_unidad_tiempo(símismo):
        """
        Esta función debe devolver la unidad de tiempo del modelo biofísico.
        
        :return: La unidad de tiempo del modelo.
        :rtype: str
        """
        raise NotImplementedError

    def inic_vars(símismo):
        """
        Esta función debe iniciar el diccionario interno de variables.
        
        MUY IMPORTANTE: Esta función debe modificar el diccionario que ya existe para símismo.variables, no crear un
        diccionario nuevo.
        Por ejemplo, NO HAGAS:
        |  símismo.variables = {var1: {...}, var2: {...}, ...}

        sino:
        |  símismo.variables[var1] = {...}
        |  símismo.variables[var2] = {...}

        Al no hacer esto, romperás la conección entre los diccionarios de variables de ClaseModeloBF y EnvolturaBF,
        lo cual impedirá después la conexión de estos variables con el modelo DS.

        """

        raise NotImplementedError


class ModeloImpaciente(ModeloBF):
    """
    Esta clase ofrece una clase pariente muy útil para modelos biofísicos cuyos pasos mínimos de simulación quedan más
    pequeños que el nivel de detalle que ofrecen. Por ejemplo, el modelo de salinidad SAHYSMOD corre por *al menos* un
    año, pero ofrece detalles al nivel estacional (de 1-12 meses) que pueden ser muy diferentes para distintas
    estaciones. Los llamo "impacientes" porque no los puedes hacer correr por un mes, sin que el modelo simule
    el año entero, sino más.
    Esta envoltura te permite crear envolturas con pasos mensuales para este tipo de modelo anual,　pero sin　el
    dolor de cabeza.
    """

    def __init__(símismo):
        """
        Esta función correrá automáticamente con la inclusión de `super().__init__()` en la función `__init__()` de las
        subclases de esta clase.
        """
        super().__init__()

        símismo.paso_mín = "Año"
        símismo.ratio_pasos = convertir(de=símismo.unidad_tiempo, a=símismo.paso_mín)

        # Creamos un diccionario para guardar valores de variables para cada paso. Tiene el formato siguiente:
        # {'var 1': [valorpaso1, valorpaso2, ...],
        #  'var 2': [valorpaso1, valorpaso2, ...],
        #  ...
        #  }
        símismo.datos_internos = dict([(var, np.array([])) for var in símismo.variables
                                   if var in símismo.estacionales])

    def cambiar_vals_modelo_interno(símismo, valores):
        """
        Esta función debe cambiar el valor de variables en el modelo biofísico.

        :param valores: Un diccionario de variables y valores para cambiar, con el formato siguiente:
        >>> {'var1': 10,  'var2': 15,
        >>>    ...
        >>>    }
        :type valores: dict

        """
        raise NotImplementedError

    def incrementar(símismo, paso):
        """
        Incrementa el modelo, tomando valores de variables desde el diccionario de valores internos.
        Si necesitamos avanzar la simulación del modelo externo, lo hace ahora y después lee los resultados.

        :param paso: El paso con cual avanzar la simulación.
        :type paso: int

        """

        # No podemos tener pasos fraccionales
        if int(paso) != paso:
            raise ValueError('El paso debe ser un número entero.')


        m = self.month
        s = self.season
        y = 0  # The number of years to simulate.

        m += int(paso)

        while m >= self.len_seasons[self.season]:
            m %= int(self.len_seasons[s])
            s += 1

        if s >= self.n_seasons:  # s starts counting at 0 (Python convention)
            y += s // self.n_seasons
            s %= self.n_seasons

        # Save the season and month for the next time.
        self.month = m
        self.season = s

        # If this is the first month of the season, we change the variables dictionary values accordingly
        if m == 0:
            # Set the internal diccionary of values to this season's values
            for var in self.internal_data:
                # For every variable in the internal data dictionary (i.e., all variables that vary by season)

                # Set the variables dictionary value to this season's value
                try:
                    self.variables[var]['val'] = self.internal_data[var][s]
                except IndexError:
                    pass

            # If this is also the first season of the year, we also run a SAHYSMOD simulation
            if s == 0:
                # Create the appropriate input file:
                self._write_inp(n_year=y)

                # Run the command prompt command
                run(self.command, cwd=self.working_dir)

                # Read the output
                self._read_out(n_year=y)

        # Save incoming coupled variables to the internal data
        for var in self.variables:
            if var in self.vars_entrando:
                self.internal_data[var][s] = self.variables[var]['val']


    def leer_vals(símismo):
        """
        Esta función debe leer los variables del modelo desde el modelo externo y copiarlos al diccionario interno
        de variables. Asegúrese que esté *actualizando* el diccionario interno, y que no lo esté recreando, lo cual
        quebrará las conexiones con el modelo conectado.
        """
        raise NotImplementedError

    def iniciar_modelo(símismo, **kwargs):
        """
        Esta función debe preparar el modelo para una simulación.

        :param kwargs:
        :type kwargs:
        """

        raise NotImplementedError

    def cerrar_modelo(símismo):
        """
        Esta función debe cerrar la simulación. No se aplica a todos los modelos biofísicos (en ese caso, usar ``pass``
        ).
        """
        raise NotImplementedError

    def obt_unidad_tiempo(símismo):
        """
        **¡Cuidado!** Esta función debe devolver la unidad de tiempo del modelo **a la cual quieres que pueda
        evaluarse**.  Por ejemplo, si tu modelo biofísico evalua con un paso de simulación mínimo de 1 año, pero
        quieres que se pueda conectar con un paso de 1 mes, esta función debe devolver "mes" y no "año".

        :return: La unidad de tiempo **deseada** del modelo.
        :rtype: str
        """
        return "Mes"

    def inic_vars(símismo):
        """
        Esta función debe iniciar el diccionario interno de variables.

        MUY IMPORTANTE: Esta función debe modificar el diccionario que ya existe para símismo.variables, no crear un
        diccionario nuevo.
        Por ejemplo, NO HAGAS:
        |  símismo.variables = {var1: {...}, var2: {...}, ...}

        sino:
        |  símismo.variables[var1] = {...}
        |  símismo.variables[var2] = {...}

        Al no hacer esto, romperás la conección entre los diccionarios de variables de ClaseModeloBF y EnvolturaBF,
        lo cual impedirá después la conexión de estos variables con el modelo DS.

        """

        raise NotImplementedError

    def avanzar_modelo(símismo, n_paso_mín):
        """
        Esta función debe avanzar el modelo de `n_paso_mín` de paso mínimos de simulación. Por ejemplo, si tienes
        un modelo que simula con un paso mínimo de 1 año pero que quieres conectar con paso mensual, esta función
        debe avanzar el modelo de `n_paso_mín` **años**.

        :param n_paso_mín: El número de pasos mínimos con el cual avanzar.
        :type n_paso_mín: int

        """
        raise NotImplementedError


class ModeloFlexible(ModeloBF):
    """

    """
    def __init__(símismo):
        """
        Esta función correrá automáticamente con la inclusión de `super().__init__()` en la función `__init__()` de las
        subclases de esta clase.
        """
        super().__init__()

    def cambiar_vals_modelo_interno(símismo, valores):
        """
        Esta función debe cambiar el valor de variables en el modelo biofísico.

        :param valores: Un diccionario de variables y valores para cambiar, con el formato siguiente:
        >>> {'var1': 10,  'var2': 15,
        >>>    ...
        >>>    }
        :type valores: dict

        """
        raise NotImplementedError

    def incrementar(símismo, paso):
        """


        """

        raise NotImplementedError

    def leer_vals(símismo):
        """
        Esta función debe leer los variables del modelo desde el modelo externo y copiarlos al diccionario interno
        de variables. Asegúrese que esté *actualizando* el diccionario interno, y que no lo esté recreando, lo cual
        quebrará las conexiones con el modelo conectado.
        """
        raise NotImplementedError

    def iniciar_modelo(símismo, **kwargs):
        """
        Esta función debe preparar el modelo para una simulación.

        :param kwargs:
        :type kwargs:
        """

        raise NotImplementedError

    def cerrar_modelo(símismo):
        """
        Esta función debe cerrar la simulación. No se aplica a todos los modelos biofísicos (en ese caso, usar ``pass``
        ).
        """
        raise NotImplementedError

    def obt_unidad_tiempo(símismo):
        """
        **¡Cuidado!** Esta función debe devolver la unidad de tiempo del modelo **a la cual quieres que pueda
        evaluarse**.  Por ejemplo, si tu modelo biofísico evalua con un paso de simulación mínimo de 1 año, pero
        quieres que se pueda conectar con un paso de 1 mes, esta función debe devolver "mes" y no "año".

        :return: La unidad de tiempo **deseada** del modelo.
        :rtype: str
        """
        raise NotImplementedError

    def inic_vars(símismo):
        """
        Esta función debe iniciar el diccionario interno de variables.

        MUY IMPORTANTE: Esta función debe modificar el diccionario que ya existe para símismo.variables, no crear un
        diccionario nuevo.
        Por ejemplo, NO HAGAS:
        |  símismo.variables = {var1: {...}, var2: {...}, ...}

        sino:
        |  símismo.variables[var1] = {...}
        |  símismo.variables[var2] = {...}

        Al no hacer esto, romperás la conección entre los diccionarios de variables de ClaseModeloBF y EnvolturaBF,
        lo cual impedirá después la conexión de estos variables con el modelo DS.

        """

        raise NotImplementedError

    def mandar_simul(símismo):
        """

        :return: El número de pasos que avanzamos con esta simulación.
        :rtype: int
        """

        raise NotImplementedError
