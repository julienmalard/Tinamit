import math as mat
import os
import sys
from importlib import import_module as importar_mod
from warnings import warn as avisar

import numpy as np
import datetime as ft
from dateutil.relativedelta import relativedelta as deltarelativo

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
        símismo.vars_clima = símismo.modelo.vars_clima

    def obt_unidad_tiempo(símismo):
        """
        Esta función debe devolver la unidad de tiempo empleada por el modelo.

        :return: La unidad de tiempo (p. ejemplo, 'meses', 'مہینہ', etc.
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

        :param valores: Un diccionario de variables y valores para cambiar.
        :type valores: dict

        """

        símismo.modelo.cambiar_vals_modelo_interno(valores=valores)

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

    def act_vals_clima(símismo, n_paso, f):
        """

        :param n_paso:
        :type n_paso: int
        :param f:
        :type f:

        """
        símismo.modelo.act_vals_clima(n_paso=n_paso, f=f)

    def iniciar_modelo(símismo, **kwargs):
        """
        Inicializa el modelo biofísico interno, incluyendo la inicialización de variables.

        :param kwargs: Argumentos para pasar al modelo interno.

        """

        # Aplicar valores iniciales antes de la inicialización del modelo. Simplemente llamamos la función
        # símismo.cambiar_vals() con el diccionario de valores iniciales.
        símismo.cambiar_vals(símismo.vals_inic)

        # ...y inicializar el modelo.
        símismo.modelo.lugar = símismo.lugar
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

        :param valores: Un diccionario de variables y valores para cambiar.
        :type valores: dict

        """
        raise NotImplementedError

    def incrementar(símismo, paso):
        """
        Esta función debe incrementar el modelo de `paso` unidades de tiempo.
        :param paso: El número de pasos
        :type paso: int
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

        """

        símismo.leer_vals_inic()

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

        Por ejemplo, NO HAGAS: ``símismo.variables = {var1: {...}, var2: {...}, ...}``

        sino: ``símismo.variables[var1] = {...}``, ``símismo.variables[var2] = {...}``, etc.

        Al no hacer esto, romperás la conección entre los diccionarios de variables de :class:`ModeloBF` y
        :class:`EnvolturaBF`, lo cual impedirá después la conexión de estos variables con el modelo DS.

        """

        raise NotImplementedError

    def leer_vals_inic(símismo):
        """
        Lee los valores iniciales de los variables.

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

        # Número y duración de las estaciones del año. Para modelos puramente اعداد_مہینہ, puedes utilizar 12 y 1.
        # Se deben modificar, si necesario, en la función leer_archivo_vals_inic() de la subclase.
        símismo.n_estaciones = 12
        símismo.dur_estaciones = [1] * 12

        # Un diccionario de variables de ingreso, egreso, y variables estacionales de cada tipo.
        símismo.tipos_vars = {
            'Ingresos': [], 'Egresos': [], 'IngrEstacionales': [], 'EgrEstacionales': []
        }

        # Inicializar como la clase pariente.
        super().__init__()

        símismo.paso_mín = "Año"
        símismo.ratio_pasos = convertir(de=símismo.unidad_tiempo, a=símismo.paso_mín)

        # Una lista de todos los variables estacionales (que sean ingresos o egresos)
        símismo.tipos_vars['Estacionales'] = list(
            {*símismo.tipos_vars['IngrEstacionales'], *símismo.tipos_vars['EgrEstacionales']})

        # El mes y la estación iniciales
        símismo.estación = 0
        símismo.mes = 0

        # Creamos un diccionario para guardar valores de variables para cada estación. Tiene el formato siguiente:
        # {'var 1': [valorestación1, valorestación2, ...],
        #  'var 2': [valorestación1, valorestación2, ...],
        #  ...
        #  }
        símismo.datos_internos = {var: None for var in símismo.variables if var in símismo.tipos_vars['Estacionales']}

        # Leer los valores iniciales
        símismo.leer_vals_inic()

    def cambiar_vals_modelo_interno(símismo, valores):
        """
        Solamente nos tenemos que asegurar que los datos internos (para variables estacionales) queda consistente
        con los nuevos valores cambiadas por la conexión con el modelo externo. La función `.avanzar_modelo()` debe
        utilizar este diccionario interno para mandar los nuevos valores a la próxima simulación.

        :param valores: Un diccionario de variables y valores para cambiar.
        :type valores: dict

        """
        pass

    def act_vals_clima(símismo, n_paso, f):
        """
        Actualiza los variables climáticos., según la estación.

        :param n_paso: El número de pasos para avanzar
        :type n_paso: int
        :param f: La fecha actual.
        :type f: ft.datetime | ft.date

        """

        # Si avanzamos por más que un año, perderemos la precisión del clima
        if n_paso > 12:
            avisar('El paso es superior a 1 año (12 meses). Las predicciones climáticas perderán su precisión.')

        # Solamante hay que cambiar los datos si es el principio de un nuevo año.
        if símismo.mes == 0 and símismo.estación == 0:

            # La lista de variables climáticos
            vars_clima = list(símismo.vars_clima)
            nombres_extrn = [d['nombre_extrn'] for d in símismo.vars_clima.values()]

            # La lista de maneras de combinar los valores diarios
            combins = [d['combin'] for d in símismo.vars_clima.values()]
            
            # La lista de factores de conversiones de variables de clima
            convs = [d['conv'] for d in símismo.vars_clima.values()]
            
            # La fecha inicial
            f_inic = f

            for e, dur in enumerate(símismo.dur_estaciones):
                # Para cada estación...

                # La fecha final
                f_final = f_inic + deltarelativo(months=+dur)

                # Calcular los datos
                datos = símismo.lugar.comb_datos(vars_clima=nombres_extrn, combin=combins,
                                                 f_inic=f_inic, f_final=f_final)

                # Aplicar los valores de variables calculados
                for i, var in enumerate(vars_clima):
                    # Para cada variable en la lista de clima...

                    # El nombre oficial del variable de clima
                    var_clima = nombres_extrn[i]
                    
                    # El factor de conversión
                    conv = convs[i]

                    # Guardar el valor para esta estación
                    símismo.datos_internos[var][e, ...] = datos[var_clima] * conv

                # Avanzar la fecha
                f_inic = f_final

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

        # Si es el primer mes de la estación, hay que cambiar los variables
        if m == 0:
            # Apuntar el diccionario interno de los valores al valor de esta estación
            for var in símismo.datos_internos:
                # Para cada variable en el diccionario interno de variables (es decir, todos los variables que
                # cambian por estación)...

                # Poner el valor del variable al valor de esta estación. (Guarda el enlace dinámico.)
                símismo.variables[var]['val'] = símismo.datos_internos[var][e]

            # Si es la primera estación del año, también hay que correr una simulación del modelo externo.
            if e == 0:

                # El número de سال para simular
                a = mat.ceil(paso / 12)  # type: int

                # Escribir el archivo de ingresos
                símismo.escribir_ingr(n_años_simul=a)

                # Avanzar la simulación
                símismo.avanzar_modelo()

                # Leer los egresos
                símismo.leer_egr(n_años_egr=a)

        # Aplicar el incremento de paso
        m += int(paso)

        # Calcular la nueva estación y mes para el próximo incremento
        while m >= símismo.dur_estaciones[e]:
            m -= int(símismo.dur_estaciones[e])
            e += 1
            e %= símismo.n_estaciones  # s empieza a contar en 0 (convención de Python)

        # Guardar la estación y el mes por la próxima vez.
        símismo.mes = m
        símismo.estación = e

    def leer_vals(símismo):
        """
        Empleamos :func:`ModeloImpaciente.leer_egr` en vez, lo cual lee los egresos de todas los pasos de la última
        simulación. :func:`ModeloImpaciente.incrementar` arregla lo de apuntar los diccionarios de
        variables actuales a la estación apropiada.
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
        Esta función debe preparar el modelo para una simulación. Si necesitas esta función para tu subclase,
        no se te olvide llamar ``super().iniciar_modelo`` para no saltar la reinicialización de la estación y del mes.

        """

        # Reestablecer el mes y la estación inicial
        símismo.estación = 0
        símismo.mes = 0

        super().iniciar_modelo(**kwargs)

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

        Por ejemplo, NO HAGAS: ``símismo.variables = {var1: {...}, var2: {...}, ...}``

        sino: ``símismo.variables[var1] = {...}``, ``símismo.variables[var2] = {...}``, etc.

        Al no hacer esto, romperás la conección entre los diccionarios de variables de :class:`ModeloBF` y
        :class:`EnvolturaBF`, lo cual impedirá después la conexión de estos variables con el modelo DS.

        También debe actualizar ``símismo.tipos_vars``, poniendo en 'Ingresos' los nombres de todos los variables
        de ingreso, en 'Egresos' todos los variables de egreso, en 'IngrEstacionales' únicamente los variables de
        ingreso estacionales, y en 'EgrEstacionales' los variables de egresos estacionales.

        """

        raise NotImplementedError

    def avanzar_modelo(símismo):
        """
        Esta función debe avanzar el modelo de ``n_paso_mín`` de paso mínimos de simulación. Por ejemplo, si tienes
        un modelo que simula con un paso mínimo de 1 año pero que quieres conectar con paso mensual, esta función
        debe avanzar el modelo de `n_paso_mín` **años**.

        """
        raise NotImplementedError

    def leer_vals_inic(símismo):
        """
        Esta función lee los valores iniciales del modelo.

        """
        dic_inic, dims = símismo.leer_archivo_vals_inic()

        for var, d_var in símismo.variables.items():
            d_var['val'] = np.zeros(dims, dtype=float)
            d_var['dims'] = dims

            if var in símismo.tipos_vars['Estacionales']:
                símismo.datos_internos[var] = np.zeros((símismo.n_estaciones, *dims), dtype=float)

        for var in símismo.tipos_vars['Ingresos']:
            datos = np.array(dic_inic[var], dtype=float)
            if var in símismo.tipos_vars['IngrEstacionales']:
                símismo.datos_internos[var][:] = datos
                símismo.variables[var]['val'] = datos[0]  # Crear un enlace dinámico
            else:
                if var in símismo.tipos_vars['Estacionales']:
                    símismo.datos_internos[var][:] = datos
                    símismo.variables[var]['val'] = datos[0]  # Crear un enlace dinámico
                else:
                    símismo.variables[var]['val'][:] = datos

    def leer_archivo_vals_inic(símismo):
        """
        Esta función devuelve un diccionario con los valores leídos del archivo de valores iniciales.
        :return: Un diccionario de los variables iniciales y sus valores, con el número de polígonos (para modelos
        espaciales). Si el modelo no es espacial, devolver ``(1,)`` para las dimensiones.
        :rtype: (dict, tuple)
        """
        raise NotImplementedError

    def leer_egr(símismo, n_años_egr):
        """
        Lee los egresos del modelo y los guarda en los diccionarios internos apropiados.

        :param n_años_egr: El número de años que se corrió la última simulación. Solamente se leerá el último año
        　　de egresos.
        :type n_años_egr: int

        """

        # Leer el archivo de egreso
        dic_egr = símismo.leer_archivo_egr(n_años_egr=n_años_egr)

        # Para simplificar el código
        estacionales = símismo.tipos_vars['EgrEstacionales']
        finales = [v for v in símismo.tipos_vars['Egresos'] if v not in estacionales]

        # Guardar los nuevos valores
        for var in estacionales:
            # Para variables estacionales...

            símismo.datos_internos[var][:] = dic_egr[var]
            # Nota: el enlace dinámico con símismo.variables ya se hizo antes.

        for var in finales:
            # Para variables no estacionales...

            símismo.variables[var]['val'][:] = dic_egr[var]

    def escribir_ingr(símismo, n_años_simul):
        """
        Escribe un archivo de ingresos del modelo en el formato que lee el modelo externo.
        :param n_años_simul: El número de años para la simulación siguiente.
        :type n_años_simul: int
        """

        dic_ingr = {}

        ingresos = símismo.tipos_vars['Ingresos']
        estacionales = símismo.tipos_vars['Estacionales']
        ingr_estacional = símismo.tipos_vars['IngrEstacionales']

        for var in ingresos:
            if var in estacionales:
                if var in ingr_estacional:
                    dic_ingr[var] = símismo.datos_internos[var]
                else:
                    dic_ingr[var] = símismo.datos_internos[var][-1, ...]
            else:
                dic_ingr[var] = símismo.variables[var]['val']

        símismo.escribir_archivo_ingr(n_años_simul=n_años_simul, dic_ingr=dic_ingr)

    def leer_archivo_egr(símismo, n_años_egr):
        """
        Lee un archivo de egresos del modelo.

        :param n_años_egr: El número de años en los egresos. Solamente leerá el último año.
        :type n_años_egr: int
        :return: Un diccionario de los resultados por variable.
        :rtype: dict
        """

        raise NotImplementedError

    def escribir_archivo_ingr(símismo, n_años_simul, dic_ingr):
        """
        Escribe un archivo de ingresos para el modelo, en un formato que lee el modelo externo.

        :param n_años_simul: El número de años para simular.
        :type n_años_simul: int
        :param dic_ingr: El diccionario de valores iniciales, por variable.
        :type dic_ingr: dict

        """

        raise NotImplementedError


class ModeloFlexible(ModeloBF):
    """
    Esta clase permite desarrollar envolturas para modelos con pasos variables (por ejemplo, modelos de cultivos
    cuyas duraciones de simulación depienden del tiempo hasta la cosecha).
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

        :param valores: Un diccionario de variables y valores para cambiar．
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

    def leer_vals_inic(símismo):
        """

        """
        raise NotImplementedError

    def leer_archivo_vals_inic(símismo):
        """
        Esta función devuelve un diccionario con los valores leídos del archivo de valores iniciales.
        :return:
        :rtype: (dict, tuple)
        """
        raise NotImplementedError

    def mandar_simul(símismo):
        """

        :return: El número de pasos que avanzamos con esta simulación.
        :rtype: int
        """

        raise NotImplementedError

    def leer_archivo_egr(símismo, n_años_egr):
        """

        :param n_años_egr:
        :type n_años_egr:
        :return:
        :rtype: dict
        """

        raise NotImplementedError

    def escribir_archivo_ingr(símismo, n_años_simul, dic_ingr):
        """

        :param n_años_simul:
        :type n_años_simul: int
        :param dic_ingr:
        :type dic_ingr: dict

        """

        raise NotImplementedError
