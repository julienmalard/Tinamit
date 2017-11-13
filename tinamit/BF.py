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

        # Número y duración de las estaciones del año. Para modelos puramente mensuales, puedes utilizar 12 y 1.
        # Se deben modificar, si necesario, en la función __init__() de la subclase.
        símismo.n_estaciones = 12
        símismo.dur_estaciones = [1] * 12

        # Inicializar como la clase pariente.
        super().__init__()

        símismo.paso_mín = "Año"
        símismo.ratio_pasos = convertir(de=símismo.unidad_tiempo, a=símismo.paso_mín)
        símismo.estacionales = símismo.gen_estacionales()

        # El mes y la estación iniciales
        símismo.estación = 0
        símismo.mes = 0

        # Creamos un diccionario para guardar valores de variables para cada paso. Tiene el formato siguiente:
        # {'var 1': [valorpaso1, valorpaso2, ...],
        #  'var 2': [valorpaso1, valorpaso2, ...],
        #  ...
        #  }
        símismo.datos_internos = dict([(var, np.array([])) for var in símismo.variables
                                       if var in símismo.estacionales])

    def cambiar_vals_modelo_interno(símismo, valores):
        """
        Solamente nos tenemos que asegurar que los datos internos (para variables estacionales) queda consistente
        con los nuevos valores cambiadas por la conexión con el modelo externo. La función `.avanzar_modelo()` debe
        utilizar este diccionario interno para mandar los nuevos valores a la próxima simulación.

        :param valores: Un diccionario de variables y valores para cambiar.
        :type valores: dict

        """

        for var, val in valores.items():
            # Para cada valor para cambiar...

            if var in símismo.datos_internos:
                # Si el variable queda presente en los datos internos...

                # Cambiar el valor del diccionario interno para la estación actual.
                símismo.datos_internos[var][símismo.estación] = val

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

        # Para simplificar el código un poco.
        m = símismo.mes
        e = símismo.estación
        a = 0  # El número de años para simular

        m += int(paso)

        while m >= símismo.dur_estaciones[e]:
            m %= int(símismo.dur_estaciones[e])
            a += 1

        if e >= símismo.n_estaciones:  # s empieza a contar en 0 (convención de Python)
            a += e // símismo.n_estaciones
            e %= símismo.n_estaciones

        # Guardar la estación y el mes por la próxima vez.
        símismo.mes = m
        símismo.estación = e

        # Si es el primer mes de la estación, hay que cambiar los variables
        if m == 0:
            # Apuntar el diccionario interno de los valores al valor de esta estación
            for var in símismo.datos_internos:
                # Para cada variable en el diccionario interno de variables (es decir, todos los variables que
                # cambian por estación)...

                # Poner el valor del variable al valor de esta estación
                try:
                    símismo.variables[var]['val'] = símismo.datos_internos[var][e]
                except IndexError:
                    pass

            # Si es la primera estación del año, también hay que correr una simulación del modelo externo.
            if e == 0:
                # Avanzar la simulación
                símismo.avanzar_modelo(n_años=a)

                # Leer los egresos
                símismo.leer_egr(n_años_egr=a)

        # Guardar los nuevos valores de los variables conectados en los datos internos
        for var in símismo.variables:
            if var in símismo.vars_entrando:
                símismo.datos_internos[var][e] = símismo.variables[var]['val']

    def leer_vals(símismo):
        """
        Empleamos leer_egr() en vez, lo cual lee los egresos de todas los pasos de la última simulación.
        .incrementar() arrelga lo de apuntar los diccionarios de variables actuales a la estación apropiada.
        """
        pass

    def obt_unidad_tiempo(símismo):
        """
        **¡Cuidado!** Esta función devuelve la unidad de tiempo del modelo **a la cual quieres que pueda
        evaluarse**.  Así que función debe devolver "mes" y no "año".

        :return: La unidad de tiempo **deseada** del modelo.
        :rtype: str
        """
        return "Mes"

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

    def avanzar_modelo(símismo, n_años):
        """
        Esta función debe avanzar el modelo de `n_paso_mín` de paso mínimos de simulación. Por ejemplo, si tienes
        un modelo que simula con un paso mínimo de 1 año pero que quieres conectar con paso mensual, esta función
        debe avanzar el modelo de `n_paso_mín` **años**.

        :param n_años: El número de pasos mínimos con el cual avanzar.
        :type n_años: int

        """
        raise NotImplementedError

    def leer_egr(símismo, n_años_egr):
        """

        :param n_años_egr:
        :type n_años_egr: int

        """
        raise NotImplementedError

    def gen_estacionales(símismo):
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
