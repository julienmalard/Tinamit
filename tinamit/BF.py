import inspect
import math as mat
import os
import sys
import traceback
import unittest
from copy import deepcopy as copiar_profundo
from importlib import import_module as importar_mod
from warnings import warn as avisar

import numpy as np
import numpy.testing as npt
import xarray as xr
from dateutil.relativedelta import relativedelta as deltarelativo

from tinamit.Modelo import Modelo
from tinamit.config import _
from tinamit.config import guardar_json
from tinamit.cositas import cargar_json


class EnvolturaBF(Modelo):
    """
    Esta clase ofrece una envoltura para **TODOS** tipos de modelos biofísicos.

    Modelos biofísicos específicos se implementan por crear una subclase de `~tinamit.BF.ClaseModeloBF` específica
    para ellos.
    """

    def __init__(símismo, modelo, nombre='bf'):
        """
        Incializar la envoltura.

        :param modelo:
        :type modelo: str | ModeloBF | Callable

        """

        super().__init__(nombre=nombre)

        símismo.archivo = None

        # El modelo externo se debe establecer después de super().__init__ para que no se borren las conexiones
        # dinámicas con los variables sel modelo externo.
        símismo._estab_mod_extern(modelo)

    def _estab_mod_extern(símismo, modelo):
        if isinstance(modelo, str):

            if not os.path.isfile(modelo):
                raise ValueError(_('El archivo "{}" no existe... :(').format(modelo))

            if os.path.splitext(modelo)[1] != '.py':
                raise ValueError(_('El archivo "{}" no parece ser un archivo Python.').format(modelo))

            dir_mod, nombre_mod = os.path.split(modelo)
            sys.path.append(dir_mod)
            módulo = importar_mod(os.path.splitext(nombre_mod)[0])

            candidatos = inspect.getmembers(módulo, inspect.isclass)
            errores = {}
            cands_final = {}
            for nmb, obj in candidatos:
                if callable(obj):
                    # noinspection PyBroadException
                    try:
                        obj = obj()
                    except NotImplementedError:
                        pass
                    except Exception:
                        errores[nmb] = traceback.format_exc()
                if isinstance(obj, ModeloBF):
                    cands_final[nmb] = obj

            if len(cands_final) == 0:
                raise AttributeError(_(
                    'El fuente especificado ("{}") no contiene subclase de "ModeloBF" utilizable. '
                    '\nErrores encontrados:{}'
                ).format(modelo, ''.join(['\n\n\t{}: \n{}'.format(nmb, e) for nmb, e in errores.items()])))
            elif len(cands_final) == 1:
                símismo.modelo = cands_final[list(cands_final)[0]]
            else:
                try:
                    símismo.modelo = cands_final['Envoltura']
                except KeyError:
                    elegido = list(cands_final)[0]
                    símismo.modelo = elegido
                    avisar(_('\nHabía más que una instancia de "ModeloBF" en el fuente "{}", '
                             '\ny ninguna se llamaba "Envoltura". Tomaremos "{}" como la envoltura '
                             '\ny esperaremos que funcione. Si no te parece, asegúrate que la definición de clase u el'
                             '\nobjeto correcto se llame "Envoltura".').format(modelo, elegido))

        else:
            if callable(modelo):
                modelo = modelo()

            if isinstance(modelo, ModeloBF):
                símismo.modelo = modelo
            else:
                raise TypeError(_('El parámetro "modelo" debe ser o una instancia o subclase de "ModeloBF", o un '
                                  'fuente Python que contiene uno.'))

        # Crear el vínculo
        símismo.variables = símismo.modelo.variables
        símismo.vars_saliendo = símismo.modelo.vars_saliendo
        símismo.vars_clima = símismo.modelo.vars_clima
        símismo.archivo = símismo.modelo.archivo

    def unidad_tiempo(símismo):
        """
        Esta función debe devolver la unidad de tiempo empleada por el modelo.

        :return: La unidad de tiempo (p. ejemplo, 'meses', 'مہینہ', etc.
        :rtype: str

        """

        return símismo.modelo.unidad_tiempo()

    def _inic_dic_vars(símismo):
        """
        No necesario porque el diccionario de variables está conectado con él del submodelo, que se inicializa
        al instanciarse el submodelo.

        """
        pass

    def _cambiar_vals_modelo_externo(símismo, valores):
        """
        Esta función cambia el valor de variables en el modelo.

        :param valores: Un diccionario de variables y valores para cambiar.
        :type valores: dict

        """
        símismo.modelo._cambiar_vals_modelo_externo(valores=valores)

    def _incrementar(símismo, paso, guardar_cada=None):
        """
        Esta función avanza el modelo por un periodo de tiempo especificado en `paso`.

        :param paso: El paso.
        :type paso: int

        """

        símismo.modelo.incrementar(paso=paso)

    def _leer_vals(símismo):
        """
        Esta función lee los valores del modelo y los escribe en el diccionario interno de variables.

        """
        símismo.modelo.leer_vals()

    def _vals_inic(símismo):
        """
        Inecesario porque :meth:`ModeloBF.iniciar_modelo` del modelo externo inicializará los variables.
        """
        return {}

    def iniciar_modelo(símismo, n_pasos, t_final, nombre_corrida, vals_inic):
        """
        Inicializa el modelo biofísico interno, incluyendo la inicialización de variables.

        """

        # Inicializar el modelo.
        símismo.modelo.corrida_activa = nombre_corrida
        símismo.modelo.iniciar_modelo(n_pasos, t_final, nombre_corrida, vals_inic=vals_inic)

        # Aplicar valores iniciales después de la inicialización del modelo. Simplemente llamamos la función
        # símismo.cambiar_vals() con el diccionario de valores iniciales.
        símismo.cambiar_vals(vals_inic)

        super().iniciar_modelo(n_pasos, t_final, nombre_corrida, vals_inic)

    def cerrar_modelo(símismo):
        """
        Cierre el modelo interno.
        """

        símismo.modelo.cerrar_modelo()

    def paralelizable(símismo):
        """
        Un modelo BF es paralelizable si su modelo externo lo es.

        :return: La paralelizabilidad del modelo externo.
        :rtype: bool
        """

        return símismo.modelo.paralelizable()

    def __getinitargs__(símismo):
        return símismo.modelo,


class ModeloBF(Modelo):
    """
    Se debe desarrollar una subclase de esta clase para cada tipo_mod modelo biofísico que se quiere volver compatible
    con Tinamit.
    """

    def __init__(símismo, archivo=None, nombre='modeloBF'):
        """
        Esta función correrá automáticamente con la inclusión de `super().__init__()` en la función `__init__()` de las
        subclases de esta clase.
        """

        símismo.archivo = archivo
        super().__init__(nombre=nombre)

    def _cambiar_vals_modelo_externo(símismo, valores):
        """
        Esta función debe cambiar el valor de variables en el modelo biofísico.

        :param valores: Un diccionario de variables y valores para cambiar.
        :type valores: dict

        """
        raise NotImplementedError

    def _incrementar(símismo, paso, guardar_cada=None):
        """
        Esta función debe incrementar el modelo de `paso` unidades de tiempo.
        :param paso: El número de pasos
        :type paso: int

        Parameters
        ----------
        guardar_cada :
        """

        raise NotImplementedError

    def _leer_vals(símismo):
        """
        Esta función debe leer los variables del modelo desde el modelo externo y copiarlos al diccionario interno
        de variables. Asegúrese que esté *actualizando* el diccionario interno, y que no lo esté recreando, lo cual
        quebrará las conexiones con el modelo conectado.

        """
        raise NotImplementedError

    def iniciar_modelo(símismo, n_pasos, t_final, nombre_corrida, vals_inic):
        """
        Esta función debe preparar el modelo para una simulación.

        """

        if not símismo.instalado():
            raise OSError(_('El modelo "{}" se debe instalar corectamente antes de hacer simulaciones.')
                          .format(símismo.__class__.__name__))

        super().iniciar_modelo(n_pasos, t_final, nombre_corrida, vals_inic)

    def cerrar_modelo(símismo):
        """
        Esta función debe cerrar la simulación. No se aplica a todos los modelos biofísicos (en ese caso, usar ``pass``
        ).
        """
        raise NotImplementedError

    def unidad_tiempo(símismo):
        """
        Esta función debe devolver la unidad de tiempo del modelo biofísico.
        
        :return: La unidad de tiempo del modelo.
        :rtype: str
        """
        raise NotImplementedError

    def _inic_dic_vars(símismo):
        """
        Esta función debe iniciar el diccionario interno de variables.

        MUY IMPORTANTE: Esta función debe modificar el diccionario que ya existe para símismo.variables, no crear un
        diccionario nuevo.

        Por ejemplo, NO HAGAS: ``símismo.variables = {var1: {...}, var2: {...}, ...}``

        sino: ``símismo.variables[var1] = {...}``, ``símismo.variables[var2] = {...}``, etc.

        Al no hacer esto, romperás la conección entre los diccionarios de variables de :class:`ModeloBF` y
        :class:`EnvolturasBF`, lo cual impedirá después la conexión de estos variables con el modelo DS.

        """

        raise NotImplementedError

    def _vals_inic(símismo):
        """
        Lee los valores iniciales de los variables.

        """

        raise NotImplementedError

    @classmethod
    def verificar(cls, clase_unittest=None):
        """

        Parameters
        ----------
        clase_unittest : unittest.TestCase

        Returns
        -------

        """
        if clase_unittest is None:
            clase_unittest = unittest.TestCase()

        with clase_unittest.subTest('inic_dic_vals'):
            cls.verificar_inic_dic_vals()
        with clase_unittest.subTest('avanzar'):
            cls.verificar_avanzar()
        with clase_unittest.subTest('leer_egr'):
            cls.verificar_leer_egr()

    @classmethod
    def verificar_inic_dic_vals(cls):
        try:
            arch_inic, arch_ref = cls.refs_prb_vals_inic()
        except NotImplementedError:
            return

        mod = cls(arch_inic)

        try:
            ref = cargar_json(arch_ref)
        except FileNotFoundError:
            avisar(_(
                '\nNo encontramos diccionario con los valores corectos de referencia para comprobar que el'
                '\nmodelo sí esté leyendo bien los datos iniciales. Lo generaremos con base en el los valores'
                '\nactualmente leídos por el modelo. Asegúrate que los valores generados en'
                '\n\t"{}"'
                '\nestén correctos, y si no lo son, bórralo. En el futuro, se empleará este fuente para '
                '\ncomprobar la función de lectura de datos iniciales.').format(arch_ref)
                   )
            d_vals = copiar_profundo(mod.variables)
            for d_v in d_vals.values():
                if isinstance(d_v['val'], np.ndarray):
                    d_v['val'] = d_v['val'].tolist()
            guardar_json(d_vals, arch=arch_ref)

            ref = d_vals

        for var in mod.variables:
            npt.assert_equal(ref[var]['val'], mod.obt_val_actual_var(var), err_msg=var)

    @classmethod
    def verificar_avanzar(cls, n_pasos=3):
        try:
            arch_ref = cls.refs_prb_avanzar()
            arch_inic = cls.refs_prb_vals_inic()[0]
        except NotImplementedError:
            return

        mod = cls(archivo=arch_inic)
        res = mod.simular(t_final=n_pasos)

        try:
            ref = xr.Dataset.from_dict(cargar_json(arch_ref))
        except FileNotFoundError:
            avisar(_(
                '\nNo encontramos diccionario con los valores corectos de referencia para comprobar que el'
                '\nmodelo sí esté simulando correctamente. Lo generaremos con base en el los valores'
                '\nactualmente leídos por el modelo. Asegúrate que los valores generados en'
                '\n\t"{}"'
                '\nestén correctos, y si no lo son, bórralo. En el futuro, se empleará este fuente para '
                '\ncomprobar la función de simulación de modelo.').format(arch_ref)
                   )

            guardar_json(res.to_dict(), arch=arch_ref)

            ref = res

        xr.testing.assert_equal(ref, res)

    @classmethod
    def verificar_leer_egr(cls):
        try:
            arch_egr, arch_ref = cls.refs_prb_leer_egr()
        except NotImplementedError:
            return

        egr = cls.leer_arch_resultados(arch_egr)

        try:
            ref = cargar_json(arch_ref)
        except FileNotFoundError:
            avisar(_(
                '\nNo encontramos diccionario con los valores corectos de referencia para comprobar que el'
                '\nmodelo sí esté leyendo bien los archivos de egresos. Lo generaremos con base en el los valores'
                '\nactualmente leídos por el modelo. Asegúrate que los valores generados en'
                '\n\t"{}"'
                '\nestén correctos, y si no lo son, bórralo. En el futuro, se empleará este fuente para '
                '\ncomprobar la función de lectura de egresos.').format(arch_ref)
                   )
            for var, val in egr.items():
                if isinstance(val, np.ndarray):
                    egr[var] = val.tolist()
            guardar_json(egr, arch=arch_ref)

            ref = egr

        for var in ref:
            npt.assert_equal(ref[var], egr[var], err_msg=var)

    @classmethod
    def refs_prb_vals_inic(cls):
        raise NotImplementedError

    @classmethod
    def refs_prb_avanzar(cls):
        """

        Returns
        -------
        str
        """
        raise NotImplementedError

    @classmethod
    def refs_prb_leer_egr(cls):
        raise NotImplementedError

    def __getinitargs__(símismo):
        return tuple()


class ModeloImpaciente(ModeloBF):
    """
    Esta clase ofrece una clase pariente muy útil para modelos biofísicos cuyos pasos mínimos de simulación quedan más
    pequeños que el nivel de detalle que ofrecen. Por ejemplo, el modelo de salinidad SAHYSMOD corre por *al menos* un
    año, pero ofrece detalles al nivel estacional (de 1-12 meses) que pueden ser muy diferentes para distintas
    estaciones. Los llamo "impacientes" porque no los puedes hacer correr por un mes, sin que el modelo simule
    el año entero, sino más.
    Esta envoltura te permite crear envolturas, por ejemplo, con pasos mensuales para este tipo_mod de modelo anual,
    pero sin el dolor de cabeza.
    """

    def __init__(símismo, archivo=None, nombre='modeloBF'):
        símismo.paso_en_ciclo = None
        símismo.ciclo = None
        símismo.test = None
        símismo.tmñ_ciclo = None
        símismo.arch_ingreso = None
        símismo.matrs_egr = {}
        símismo.matrs_ingr = {}
        símismo.proces_ingrs = {}

        super().__init__(archivo=archivo, nombre=nombre)

    def _cambiar_vals_modelo_externo(símismo, valores):
        """
        Esta función no se necesita porque :meth:`avanzar_modelo` se cargará de pasar los valores necesarios a la
        próxima simulación del modelo externo.
        """

        pass

    def _leer_vals(símismo):
        """
        No necesario porque :meth:`_incrementar` ya incluye funciones para leer los egresos del modelo.
        """
        pass

    def _vars_por_pasito(símismo, solamente=None):

        posibles = ['pasito', 'pasito-ingr', 'pasito-egr']
        if solamente == 'ingr':
            posibles.remove('pasito-egr')
        elif solamente == 'egr':
            posibles.remove('pasito-ingr')

        return [var for var, d_var in símismo.variables.items() if 'por' in d_var and d_var['por'] in posibles]

    def _vals_inic(símismo):
        dic_inic = símismo._gen_dic_vals_inic()

        subciclo = símismo._vars_subciclo()
        subciclo_ingr = símismo._vars_subciclo(solamente='ingr')

        for var, val in dic_inic.items():
            if var in subciclo:
                if var in subciclo_ingr:
                    símismo.matrs_ingr[var] = val.copy()
                    dic_inic[var] = val[0]

                if var in símismo.egresos():
                    símismo.matrs_egr[var] = val.copy()

        return dic_inic

    def estab_proces_ingr(símismo, var_ingr, proc):
        posibilidades = ['último', 'suma', 'prom', 'máx', None]
        if proc not in posibilidades:
            raise ValueError(proc)
        var_ingr = símismo.valid_var(var_ingr)

        if var_ingr not in símismo.ingresos():
            raise ValueError(_('El variable "{}" no es variable de ingreso.').format(var_ingr))

        if proc is not None:
            símismo.proces_ingrs[var_ingr] = proc
        else:
            símismo.proces_ingrs.pop(var_ingr)

    def iniciar_modelo(símismo, n_pasos, t_final, nombre_corrida, vals_inic):

        símismo.paso_en_ciclo = símismo.ciclo = -1

        super().iniciar_modelo(n_pasos=n_pasos, t_final=t_final, nombre_corrida=nombre_corrida, vals_inic=vals_inic)

    def cambiar_vals(símismo, valores):

        for var, val in valores.items():
            símismo.matrs_ingr[var][símismo.paso_en_ciclo] = val

        super().cambiar_vals(valores)

    def procesar_ingr_modelo(símismo):
        for var, proc in símismo.proces_ingrs.items():
            matr = símismo.matrs_ingr[var]
            if proc == 'último':
                símismo._act_vals_dic_var({var: matr[-1]})
            elif proc == 'suma':
                símismo._act_vals_dic_var({var: matr.sum()})
            elif proc == 'prom':
                símismo._act_vals_dic_var({var: matr.mean()})
            elif proc == 'máx':
                símismo._act_vals_dic_var({var: matr.max()})

    def procesar_egr_modelo(símismo, n_ciclos):

        valores = símismo.leer_egr_modelo(n_ciclos=n_ciclos)

        por_subciclo = símismo._vars_subciclo()
        for var, val in valores.items():
            if var in por_subciclo:
                símismo._act_vals_dic_var({var: val[0]})

                if var in símismo.matrs_egr:
                    anterior = símismo.matrs_egr[var]
                    if isinstance(anterior, np.ndarray) and anterior.shape == val.shape:
                        símismo.matrs_egr[var][:] = val
                    else:
                        símismo.matrs_egr[var] = val

            else:
                símismo._act_vals_dic_var({var: val})

    def escribir_ingr(símismo, n_ciclos, archivo=None):
        """
        Escribe un fuente de ingresos del modelo en el formato que lee el modelo externo.

        Parameters
        ----------
        n_ciclos : int
            El número de años para la simulación siguiente.
        archivo : str
            El archivo en el cuál escribir los ingresos.

        """

        if archivo is None:
            archivo = símismo.arch_ingreso

        # Procesar los ingresos
        if símismo.ciclo != -1:
            símismo.procesar_ingr_modelo()

        dic_ingr = {}

        ingr_por_pasito = símismo._vars_subciclo(solamente='ingr')

        for var in símismo.ingresos():
            if var in ingr_por_pasito:
                dic_ingr[var] = símismo.matrs_ingr[var]
            else:
                dic_ingr[var] = símismo.obt_val_actual_var(var)

        símismo.test = dic_ingr
        símismo._escribir_archivo_ingr(n_ciclos=n_ciclos, dic_ingr=dic_ingr, archivo=archivo)

    def _vars_subciclo(símismo, solamente=None):
        return símismo._vars_por_pasito(solamente)

    def _incrementar(símismo, paso, guardar_cada=None):
        raise NotImplementedError

    def unidad_tiempo(símismo):
        raise NotImplementedError

    def _inic_dic_vars(símismo):
        raise NotImplementedError

    def _gen_dic_vals_inic(símismo):
        raise NotImplementedError

    def leer_egr_modelo(símismo, n_ciclos, archivo=None):
        raise NotImplementedError

    def cerrar_modelo(símismo):
        raise NotImplementedError

    def obt_tmñ_ciclo(símismo):
        raise NotImplementedError

    def _escribir_archivo_ingr(símismo, n_ciclos, dic_ingr, archivo):
        raise NotImplementedError


class ModeloIndeterminado(ModeloImpaciente):

    def __init__(símismo, archivo=None, nombre='modeloIndeterminado'):
        símismo.dic_ingr = {}
        super().__init__(archivo=archivo, nombre=nombre)

    def cambiar_vals(símismo, valores):
        for var, val in valores.items():
            proc = símismo.proces_ingrs[var]
            if símismo.dic_ingr[var] is None:
                símismo.dic_ingr[var] = val
            else:
                if proc == 'máx':
                    símismo.dic_ingr[var] = np.maximum(símismo.dic_ingr[var], val)
                elif proc == 'último':
                    símismo.dic_ingr[var] = val
                elif proc in ['suma', 'prom']:
                    símismo.dic_ingr[var] += val  # La división para `prom` se hará después en `procesar_ingr_modelo()`
                else:
                    raise ValueError(proc)

    def _incrementar(símismo, paso, guardar_cada=None):
        # Para simplificar el código un poco.
        i = símismo.paso_en_ciclo

        # Aplicar el incremento de paso
        i += int(paso)
        while i >= símismo.tmñ_ciclo:

            # Escribir el archivo de ingresos
            símismo.escribir_ingr(n_ciclos=1)

            símismo.ciclo += 1
            i -= símismo.tmñ_ciclo

            símismo.tmñ_ciclo = símismo.mandar_modelo()

            if i <= símismo.tmñ_ciclo:
                # Leer los egresos del modelo
                símismo.procesar_egr_modelo(n_ciclos=1)
                for ll in símismo.dic_ingr:
                    símismo.dic_ingr[ll] = None

                    # Guardar el pasito actual para la próxima vez.
        símismo.paso_en_ciclo = i

        # Apuntar el diccionario interno de los valores al valor de este paso del ciclo
        símismo._act_vals_dic_var({var: matr[i] for var, matr in símismo.matrs_egr.items()})

    def _leer_vals(símismo):
        """
        No necesario porque :meth:`_incrementar` ya incluye funciones para leer los egresos del modelo.
        """

        pass

    def _vals_inic(símismo):
        return símismo._gen_dic_vals_inic()

    def iniciar_modelo(símismo, n_pasos, t_final, nombre_corrida, vals_inic):
        símismo.tmñ_ciclo = 0

        for var in símismo.vars_entrando:
            if var not in símismo.proces_ingrs:
                símismo.proces_ingrs[var] = 'último'

        símismo.dic_ingr.clear()
        símismo.dic_ingr.update({
            vr: None for vr in símismo.vars_entrando
        })

        símismo.matrs_egr.clear()
        for var in símismo._vars_subciclo():
            if var in símismo.vars_saliendo:
                símismo.matrs_egr[var] = None

        super().iniciar_modelo(n_pasos=n_pasos, t_final=t_final, nombre_corrida=nombre_corrida, vals_inic=vals_inic)

    def procesar_ingr_modelo(símismo):
        for var, proc in símismo.proces_ingrs.items():
            val = símismo.dic_ingr[var]
            if proc == 'prom':
                símismo._act_vals_dic_var({var: val / símismo.tmñ_ciclo})
            else:
                símismo._act_vals_dic_var({var: val})

    def obt_tmñ_ciclo(símismo):
        return símismo.tmñ_ciclo

    def unidad_tiempo(símismo):
        raise NotImplementedError

    def _inic_dic_vars(símismo):
        raise NotImplementedError

    def _gen_dic_vals_inic(símismo):
        raise NotImplementedError

    def _escribir_archivo_ingr(símismo, n_ciclos, dic_ingr, archivo):
        raise NotImplementedError

    def leer_egr_modelo(símismo, n_ciclos, archivo=None):
        raise NotImplementedError

    def mandar_modelo(símismo):
        raise NotImplementedError

    def cerrar_modelo(símismo):
        raise NotImplementedError


class ModeloDeterminado(ModeloImpaciente):

    def __init__(símismo, archivo=None, nombre='modeloDeterminado'):
        super().__init__(archivo, nombre)

    def _incrementar(símismo, paso, guardar_cada=None):
        # Para simplificar el código un poco.
        i = símismo.paso_en_ciclo

        paso = int(paso)

        # Aplicar el incremento de paso
        avanzar = i == símismo.ciclo == -1
        i += paso
        avanzar = avanzar or (i // símismo.tmñ_ciclo > 0)
        i %= símismo.tmñ_ciclo

        # Guardar el pasito actual para la próxima vez.
        símismo.paso_en_ciclo = i

        # Si hay que avanzar el modelo externo, lanzar una su simulación aquí.
        if avanzar:
            # El número de ciclos para simular
            c = mat.ceil(paso / símismo.tmñ_ciclo)  # type: int
            símismo.ciclo += c

            # Escribir los archivos de ingreso
            símismo.escribir_ingr(n_ciclos=c)

            # Avanzar la simulación
            símismo.avanzar_modelo(n_ciclos=c)

            # Leer los egresos del modelo
            símismo.procesar_egr_modelo(n_ciclos=c)

        # Apuntar el diccionario interno de los valores al valor de este paso del ciclo
        símismo._act_vals_dic_var({var: matr[i] for var, matr in símismo.matrs_egr.items()})

    def iniciar_modelo(símismo, n_pasos, t_final, nombre_corrida, vals_inic):

        símismo.tmñ_ciclo = símismo.obt_tmñ_ciclo()

        símismo.matrs_ingr.clear()
        símismo.matrs_egr.clear()

        for vr in símismo.vars_entrando:
            dims = símismo.obt_dims_var(vr)
            símismo.matrs_ingr[vr] = np.zeros((símismo.tmñ_ciclo, *dims) if dims != (1,) else símismo.tmñ_ciclo)

        por_pasito = símismo._vars_por_pasito()
        for vr in símismo.vars_saliendo:
            if vr in por_pasito:
                dims = símismo.obt_dims_var(vr)
                símismo.matrs_egr[vr] = np.zeros((símismo.tmñ_ciclo, *dims) if dims != (1,) else símismo.tmñ_ciclo)

        super().iniciar_modelo(n_pasos, t_final, nombre_corrida, vals_inic)

    def unidad_tiempo(símismo):
        raise NotImplementedError

    def obt_tmñ_ciclo(símismo):
        raise NotImplementedError

    def _inic_dic_vars(símismo):
        raise NotImplementedError

    def _gen_dic_vals_inic(símismo):
        raise NotImplementedError

    def _escribir_archivo_ingr(símismo, n_ciclos, dic_ingr, archivo):
        raise NotImplementedError

    def leer_egr_modelo(símismo, n_ciclos, archivo=None):
        raise NotImplementedError

    def avanzar_modelo(símismo, n_ciclos):
        raise NotImplementedError

    def cerrar_modelo(símismo):
        raise NotImplementedError


class ModeloBloques(ModeloImpaciente):

    def __init__(símismo, archivo=None, nombre='modeloBloques'):
        super().__init__(nombre=nombre, archivo=archivo)

        símismo.tmñ_bloques = None

    def iniciar_modelo(símismo, n_pasos, t_final, nombre_corrida, vals_inic):
        """
        Esta función debe preparar el modelo para una simulación. Si necesitas esta función para tu subclase,
        no se te olvide llamar ``super().iniciar_modelo()`` para no saltar la reinicialización del bloque y del paso.

        """

        símismo.tmñ_bloques = símismo.obt_tmñ_bloques()
        símismo.tmñ_ciclo = símismo.obt_tmñ_ciclo()

        símismo.matrs_ingr.clear()
        símismo.matrs_egr.clear()

        for vr in símismo.vars_entrando:
            dims = símismo.obt_dims_var(vr)
            símismo.matrs_ingr[vr] = np.zeros((símismo.tmñ_ciclo, *dims) if dims != (1,) else símismo.tmñ_ciclo)

        por_pasito = símismo._vars_por_pasito()
        for vr in símismo.vars_saliendo:
            if vr in por_pasito:
                dims = símismo.obt_dims_var(vr)
                símismo.matrs_egr[vr] = np.zeros((símismo.tmñ_ciclo, *dims) if dims != (1,) else símismo.tmñ_ciclo)

        super().iniciar_modelo(n_pasos, t_final, nombre_corrida, vals_inic=vals_inic)

    def _incrementar(símismo, paso, guardar_cada=None):

        # Para simplificar el código un poco.
        i = símismo.paso_en_ciclo

        paso = int(paso)

        # Aplicar el incremento de paso
        primer_incr = i == símismo.ciclo == -1

        i += paso
        avanzar = primer_incr or (i // símismo.tmñ_ciclo > 0)
        i %= símismo.tmñ_ciclo

        # Guardar el pasito actual para la próxima vez.
        símismo.paso_en_ciclo = i

        # Si hay que avanzar el modelo externo, lanzar una su simulación aquí.
        if avanzar:
            # El número de ciclos para simular
            c = mat.ceil(paso / símismo.tmñ_ciclo)  # type: int
            símismo.ciclo += c

            # Escribir los archivos de ingreso
            símismo.escribir_ingr(n_ciclos=c)

            # Avanzar la simulación
            símismo.avanzar_modelo(n_ciclos=c)

            # Leer los egresos del modelo
            símismo.procesar_egr_modelo(n_ciclos=c)

        # Apuntar los valores de egreso al bloque actual
        b = símismo.bloque_actual()
        símismo._act_vals_dic_var(
            {var: símismo.matrs_egr[var][b] for var in símismo._vars_por_bloques() if var in símismo.egresos()})

        símismo._act_vals_dic_var(
            {var: símismo.matrs_egr[var][i] for var in símismo._vars_por_pasito() if var in símismo.egresos()})

    def bloque_actual(símismo):
        tmñ_bloques_cum = np.cumsum(símismo.obt_tmñ_bloques())
        n_bloques = len(tmñ_bloques_cum)

        for i in range(n_bloques):
            if símismo.paso_en_ciclo < tmñ_bloques_cum[i]:
                return i

        raise ValueError(símismo.paso_en_ciclo)

    def _vars_subciclo(símismo, solamente=None):
        return símismo._vars_por_pasito(solamente) + símismo._vars_por_bloques(solamente)

    def _vars_por_bloques(símismo, solamente=None):
        posibles = ['bloque', 'bloque-ingr', 'bloque-egr']
        if solamente == 'ingr':
            posibles.remove('bloque-egr')
        elif solamente == 'egr':
            posibles.remove('bloque-ingr')

        return [var for var, d_var in símismo.variables.items() if 'por' in d_var and d_var['por'] in posibles]

    def _act_vals_clima(símismo, f_0, f_1, lugar):

        # Solamante hay que cambiar los datos si es el principio de un nuevo ciclo.
        if símismo.ciclo == 0 and símismo.paso_en_ciclo == 0:

            # La lista de variables climáticos
            vars_clima = list(símismo.vars_clima)
            nombres_extrn = [d['nombre_extrn'] for d in símismo.vars_clima.values()]

            # La lista de maneras de combinar los valores diarios
            combins = [d['combin'] for d in símismo.vars_clima.values()]

            # La lista de factores de conversiones de variables de clima
            convs = [d['conv'] for d in símismo.vars_clima.values()]

            # La fecha inicial
            f_inic = f_0

            for b, tmñ in enumerate(símismo.tmñ_bloques):
                # Para cada bloque...

                # La fecha final
                base_t, factor = símismo._unid_tiempo_python()
                f_final = f_0 + deltarelativo(**{base_t: tmñ * factor})

                # Calcular los datos
                datos = lugar.comb_datos(vars_clima=nombres_extrn, combin=combins, f_inic=f_inic, f_final=f_final)

                # Aplicar los valores de variables calculados
                for i, var in enumerate(vars_clima):
                    # Para cada variable en la lista de clima...

                    # El nombre oficial del variable de clima
                    var_clima = nombres_extrn[i]

                    # El factor de conversión
                    conv = convs[i]

                    # Guardar el valor para esta estación
                    símismo.matrs_ingr[var][b, ...] = datos[var_clima] * conv

                # Avanzar la fecha
                f_inic = f_final

    def obt_tmñ_ciclo(símismo):
        return np.sum(símismo.obt_tmñ_bloques())

    def _gen_dic_vals_inic(símismo):
        raise NotImplementedError

    def leer_egr_modelo(símismo, n_ciclos, archivo=None):
        raise NotImplementedError

    def _escribir_archivo_ingr(símismo, n_ciclos, dic_ingr, archivo):
        raise NotImplementedError

    def cerrar_modelo(símismo):
        raise NotImplementedError

    def unidad_tiempo(símismo):
        raise NotImplementedError

    def _inic_dic_vars(símismo):
        raise NotImplementedError

    def obt_tmñ_bloques(símismo):
        raise NotImplementedError

    def avanzar_modelo(símismo, n_ciclos):
        """
        Esta función debe avanzar el modelo de `n_ciclos` ciclos.

        """

        raise NotImplementedError
