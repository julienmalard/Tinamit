import csv
import datetime as ft
import math
import os
import pickle
import re
from copy import deepcopy as copiar_profundo
from multiprocessing import Pool as Reserva
from warnings import warn as avisar

import numpy as np
import pandas as pd
import xarray as xr
from dateutil.relativedelta import relativedelta as deltarelativo
from lxml import etree as arbole

import tinamit.Geog.Geog as Geog
from tinamit.Análisis.Calibs import CalibradorEc, CalibradorMod
from tinamit.Análisis.Datos import obt_fecha_ft, gen_SuperBD, jsonificar, numpyficar, SuperBD
from tinamit.Análisis.Valids import validar_resultados
from tinamit.Unidades.conv import convertir
from tinamit.config import _, obt_val_config
from tinamit.cositas import detectar_codif, valid_nombre_arch, guardar_json, cargar_json


class Modelo(object):
    """
    Todas las cosas en Tinamit son instancias de `Modelo`, que sea un modelo de dinámicas de los sistemas, un modelo de
    cultivos o de suelos o de clima, o un modelo conectado.
    Cada tipo_mod de modelo se representa por subclases específicas. Por eso, la gran mayoría de los métodos definidos
    aquí se implementan de manera independiente en cada subclase de `Modelo`.
    """

    leng_orig = 'es'

    # Si el modelo puede combinar pasos mientras simula.
    combin_pasos = False
    dialecto_ec = 'vensim'

    def __init__(símismo, nombre):
        """
        La función de inicialización de todos modelos, conectados o no.

        Parameters
        ----------
        nombre : str
            El nombre del modelo.

        """

        # El nombre del modelo (sirve como una referencia a este modelo en el modelo conectado).
        símismo.nombre = _valid_nombre_mod(nombre)

        # El diccionario de variables necesita la forma siguiente. Se llena con la función símismo._inic_dic_vars().
        # {var1: {'val': 13, 'unidades': cm, 'ingreso': True, 'egreso': True},
        #  var2: {...},
        #  ...}
        símismo.variables = {}
        símismo._inic_dic_vars()  # Iniciar los variables.
        símismo._verificar_dic_vars()
        símismo._reinic_vals()

        # Para calibraciones
        símismo.calibs = {}
        símismo.info_calibs = {'calibs': {}, 'micro calibs': {}}

        # Memorio de valores de variables (para leer los resultados más rápidamente después de una simulación).
        símismo.mem_vars = None  # type: xr.Dataset

        # Referencia hacia el nombre de la corrida activa.
        símismo.corrida_activa = None

        # Una referncia para acordarse si los valores de los variables en el diccionario de variables están actualizados
        símismo.vals_actualizadas = False

        # Listas de los nombres de los variables que sirven de conexión con otro modelo o con datos externos.
        símismo.vars_saliendo = set()
        símismo.vars_entrando = set()

        # Para guardar variables climáticos
        símismo.vars_clima = {}  # Formato: {var1: {'nombre_extrn': nombre_oficial, 'combin': 'prom' | 'total'}, ...}

        # Para manejar conversiones entre unidades de tiempo.
        símismo._conv_unid_tiempo = {}

    def _inic_dic_vars(símismo):
        """
        Esta función debe poblar el diccionario de variables del modelo.

        """

        raise NotImplementedError

    def _verificar_dic_vars(símismo, reqs=None):

        requísitos = ['unidades', 'líms', 'ingreso', 'egreso']
        if reqs is not None:
            requísitos += reqs

        for var, d_var in símismo.variables.items():

            if 'val' not in d_var:
                d_var['val'] = None

            faltan = [r for r in requísitos if r not in d_var]
            if len(faltan):
                raise ValueError(
                    _('Al variable "{var}" le falta los atributos siguientes: {atr}')
                        .format(var=var, atr=', '.join(faltan))
                )

    def unidad_tiempo(símismo):
        """
        Esta función debe devolver la unidad de tiempo empleada por el modelo.

        Returns
        -------
        str
            La unidad de tiempo (p. ej., 'meses', 'مہینہ', etc.)
        """

        raise NotImplementedError

    def iniciar_modelo(símismo, n_pasos, t_final, nombre_corrida, vals_inic):
        """
        Esta función llama cualquier acción necesaria para preparar el modelo para la simulación. Esto incluye aplicar
        valores iniciales. En general es muy fácil y se hace simplemente con "símismo.cambiar_vals(vals_inic)",
        pero para unos modelos (como Vensim) es un poco más delicado así que los dejamos a ti para implementar.

        :param n_pasos:
        :type n_pasos: int

        :param nombre_corrida: El nombre de la corrida (generalmente para guardar resultados).
        :type nombre_corrida: str

        """

        # Establecer la corrida actual
        símismo.corrida_activa = nombre_corrida

        # Reestablecer valores iniciales
        símismo._reinic_vals()

        # Actualizar valores iniciales en el diccionario interno
        símismo._act_vals_dic_var(vals_inic)

    def _reinic_vals(símismo):
        vals_inic = símismo._vals_inic()
        símismo._act_vals_dic_var(vals_inic)

        vars_vacíos = [v for v in símismo.variables if símismo.obt_val_actual_var(v) is None]
        if len(vars_vacíos):
            raise ValueError(
                _('No se inicializó valor para los variables siguientes: {}.').format(', '.join(vars_vacíos))
            )

    def _vals_inic(símismo):
        raise NotImplementedError

    def _act_vals_dic_var(símismo, valores):
        """
        Actualiza los valores en el diccionar de variables. Es importante emplear esta función y no poner el valor
        manualmente para evitar errores súbtiles en las simulaciones.

        Parameters
        ----------
        valores : dict[str, np.ndarray | float | int]
            Un diccionario de variables y de sus nuevos valores.

        """

        # Para cara variable y valor...
        for var, val in valores.items():

            val_antes = símismo.variables[var]['val']

            if val_antes is None:
                # Si no existía valor antes, poner el nuevo valor sin pregunta (pero hacemos copias de matrices
                # en caso que la matriz original se pueda modificar en otro lugar).
                símismo.variables[var]['val'] = val.copy() if isinstance(val, np.ndarray) else val

            elif isinstance(val_antes, np.ndarray):
                # Si es matriz, tenemos que cambiar sus valores sin crear nueva matriz.

                if isinstance(val, np.ndarray):
                    existen = np.invert(np.isnan(val))  # No cambiamos nuevos valores que faltan
                    val_antes[existen] = val[existen]
                else:
                    val_antes[:] = val

            else:
                # Si no es matriz, podemos cambiar el valor directamente.
                if not np.isnan(val):  # Evitar cambiar si no existe el nuevo valor.
                    símismo.variables[var]['val'] = val

    def _unid_tiempo_python(símismo):
        unid_ref_tiempo = ref_final = símismo.unidad_tiempo()
        factor = 1
        for u in ['año', 'mes', 'día']:
            try:
                d_conv = símismo._conv_unid_tiempo[unid_ref_tiempo]
                factor = convertir(de=d_conv['ref'], a=u, val=d_conv['factor'])
                ref_final = u
                if factor == d_conv['factor']:
                    break
            except (KeyError, ValueError):
                try:
                    factor = convertir(de=unid_ref_tiempo, a=u)
                    ref_final = u
                    if factor == 1:
                        break
                except ValueError:
                    pass
        if ref_final not in ['año', 'mes', 'día']:
            raise ValueError(_('La unidad de tiempo "{}" no se pudo convertir a años, meses o días.')
                             .format(unid_ref_tiempo))
        return ref_final, factor

    def _procesar_rango_tiempos(símismo, t_inic, t_final, paso):

        if int(paso) != paso:
            raise ValueError(_('`paso` debe ser un número entero.'))
        if paso < 1:
            raise ValueError(_('El paso debe ser superior a 1.'))

        if t_inic is None:
            if isinstance(t_final, int):
                t_inic = 0
            else:
                raise ValueError(_('Si el tiempo final es una fecha, debes especificar un tiempo inicial también.'))
        elif isinstance(t_inic, str):
            t_inic = obt_fecha_ft(t_inic)
        elif isinstance(t_inic, ft.datetime):
            t_inic = t_inic.date()
        elif isinstance(t_inic, np.datetime64):
            t_inic = t_inic.astype('datetime64[D]').tolist()
        elif isinstance(t_inic, (np.float, np.int)):
            t_inic = int(t_inic)

        if isinstance(t_final, str):
            t_final = obt_fecha_ft(t_final)
        elif isinstance(t_final, ft.datetime):
            t_final = t_final.date()
        elif isinstance(t_final, np.datetime64):
            t_final = t_final.astype('datetime64[D]').tolist()
        elif isinstance(t_final, (np.float, np.int)):
            t_final = int(t_final)

        # Calcular el número de pasos necesario
        if isinstance(t_inic, int):
            if isinstance(t_final, int):
                if t_inic >= t_final:
                    t_inic, t_final = t_final, t_inic

                n_iter = int(math.ceil((t_final - t_inic) / paso))
                delta_fecha = None

            else:
                raise ValueError(_('Si el tiempo final es una fecha, el tiempo inicial también debe ser una fecha.'))

        elif isinstance(t_inic, ft.date):

            ref_final, factor = símismo._unid_tiempo_python()

            dic_trad_tiempo = {'año': 'year', 'mes': 'months', 'día': 'days'}

            if isinstance(t_final, int):
                n_iter = int(math.ceil(t_final / paso))
                t_final = t_inic + deltarelativo(
                    **{dic_trad_tiempo[ref_final]: n_iter}
                )  # type: ft.date
            else:
                if t_inic >= t_final:
                    t_inic, t_final = t_final, t_inic

                if ref_final == 'año':
                    dlt = deltarelativo(t_final, t_inic)
                    plazo = dlt.years + (not dlt.months == dlt.days == 0)
                elif ref_final == 'mes':
                    dlt = deltarelativo(t_final, t_inic)
                    plazo = dlt.years * 12 + dlt.months + (not dlt.days == 0)
                elif ref_final == 'día':
                    plazo = (t_final - t_inic).days
                else:
                    raise ValueError
                plazo *= factor
                n_iter = math.ceil(plazo / paso)

            delta_fecha = deltarelativo(**{dic_trad_tiempo[ref_final]: paso})

        else:
            raise TypeError(_('t_inic debe ser fecha o número entero, no "{}".').format(type(t_inic)))

        n_pasos = n_iter * paso
        return n_iter, n_pasos, t_inic, t_final, delta_fecha

    def _procesar_vars_extern(símismo, vars_inic, vars_extern, bd, t_inic, t_final, lg=None):
        """

        Parameters
        ----------
        vars_inic : dict | list
        vars_extern :
        bd : SuperBD | None
        lg :

        Returns
        -------

        """
        if lg is None and bd is not None and len(bd.lugares()) != 1:
            raise ValueError(
                _('Debes emplear ".simular_en()" para simulaciones con bases de datos con lugares múltiples.')
            )

        # Variables externos
        if isinstance(vars_extern, str):
            vars_extern = [vars_extern]
        if vars_extern is vars_inic is None and bd is not None:
            vars_extern = [x for x in list(bd.variables) if x in símismo.variables]
        if vars_extern is None:
            vals_extern = None
        elif isinstance(vars_extern, list):
            if bd is None:
                raise ValueError
            vals_extern = bd.obt_datos(l_vars=vars_extern, lugares=lg, tiempos=(t_inic, t_final), interpolar=False)
        elif isinstance(vars_extern, (dict, pd.DataFrame, xr.Dataset)):
            if isinstance(vars_extern, dict) and all(isinstance(v, str) for v in vars_extern.values()):
                vals_extern = bd.obt_datos(
                    l_vars=list(vars_extern.values()), lugares=lg, tiempos=(t_inic, t_final), interpolar=False
                )
                corresp_extern = {v: ll for ll, v in vars_extern.items()}
                vals_extern.rename(corresp_extern, inplace=True)

            else:
                vals_extern = gen_SuperBD(vars_extern).obt_datos(tiempos=(t_inic, t_final), interpolar=False)
        else:
            raise TypeError(type(vars_extern))

        # Variables iniciales
        if isinstance(vars_inic, str):
            vars_inic = [vars_inic]
        corresps_inic = None
        if vars_inic is None:
            if bd is not None:
                datos_inic = bd.obt_datos(lugares=lg, tiempos=t_inic, interpolar=False)
                if len(datos_inic['tiempo']):
                    vals_inic = {v: datos_inic[v].values[0] for v in bd.variables
                                 if v in símismo.variables and not np.isnan(datos_inic[v])}
                else:
                    vals_inic = {}
            else:
                vals_inic = {}
        elif isinstance(vars_inic, list):
            vals_inic = {v: None for v in vars_inic}
        elif isinstance(vars_inic, dict):
            vals_inic = {ll: v if not isinstance(v, str) else None for ll, v in vars_inic.items()}
            corresps_inic = {ll: v for ll, v in vars_inic.items() if isinstance(v, str)}
            for vr, vr_bd in corresps_inic.items():
                vals_inic[vr_bd] = vals_inic.pop(vr)
        else:
            raise TypeError(type(vars_inic))

        for vr, vl in vals_inic.items():
            if vl is None:
                if vr not in bd.variables:
                    raise ValueError
                else:
                    datos = bd.obt_datos(vr, lugares=lg, tiempos=t_inic)
                    try:
                        vals_inic[vr] = datos[vr].values[0]
                    except IndexError:
                        raise

        if corresps_inic is not None:
            for vr, vr_bd in corresps_inic.items():
                vals_inic[vr] = vals_inic.pop(vr_bd)

        if vals_extern is not None:
            for vr in vals_extern.data_vars:
                if vr not in vals_inic:
                    datos = vals_extern.where(vals_extern['tiempo'] == t_inic, drop=True)[vr].values
                    if len(datos) and not np.isnan(datos):
                        vals_inic[vr] = datos[0]

        return vals_inic, vals_extern

    def simular(
            símismo, t_final=None, t_inic=None, paso=1, nombre_corrida='Corrida Tinamït',
            vals_inic=None, vals_extern=None, bd=None, lugar_clima=None, clima=None, vars_interés=None
    ):
        """
        Correr una simulación del Modelo.

        Parameters
        ----------
        t_final : ft.date | ft.datetime | str | int
            El tiempo final de la simulación. Puede ser en formato de fecha o numérico. Si no se especifica,
            se inferirá de `vars_extern`.
        t_inic : ft.date | ft.datetime | str | int
            El tiempo inicial de la simulación. Puede ser en formato de fecha o numérico. Si no se especifica,
            se inferirá de `vars_extern`.
        paso : int
            El paso para la simulación.
        nombre_corrida : str
            El nombre de la corrida.
        vals_inic : dict | str | list | pd.DataFrame | xr.Dataset
            Valores iniciales para variables. Si es de tipo_mod ``str`` o ``list``, se tomarán los valores de `bd`.
        vals_extern : dict | str | list | pd.DataFrame | xr.Dataset
            Valores externos que hay que actualizar a través de la simulación (no necesariamente iniciales).
            Si es de tipo_mod ``str`` o ``list``, se tomarán los valores de `bd`.
        bd : SuperBD | dict | str | pd.DataFrame | xr.Dataset
            Una base de datos opcional. Si se especifica, se empleará para obtener los valores de variables iniciales
            y externos.
        lugar_clima : Geog.Lugar
            El lugar para simulaciones con clima.
        clima : str | float | int
            El escenario climático.
        vars_interés : str | list[str]
            Los variables de interés en los resultados.

        Returns
        -------
        xr.Dataset
            Los resultados de la simulación.

        """

        # Formatear argumentos
        if vars_interés is None:
            vars_interés = list(símismo.variables)
        elif isinstance(vars_interés, str):
            vars_interés = [vars_interés]

        # Procesar datos, si existen
        if bd is not None:
            bd = gen_SuperBD(bd)

            # Emplear el tiempo inicial o final de la base de datos, si necesario
            t_inic = t_inic or bd.tiempos()[0]
            t_final = t_final or bd.tiempos()[-1]

        # Procesar los tiempos iniciales y finales
        n_iter, n_pasos, t_inic, t_final, delta_fecha = símismo._procesar_rango_tiempos(t_inic, t_final, paso)
        simul_fecha = isinstance(t_inic, ft.date)  # Si tenemos una simulación basada en fechas
        if bd is not None and simul_fecha is not bd.tiempo_fecha():
            raise ValueError(_('Los datos y los tiempos de simulación deben ser ambos o fechas, o números.'))

        # Procesar los valores iniciales y externos
        vals_inic, vals_extern = símismo._procesar_vars_extern(
            vals_inic, vals_extern, bd, t_inic=t_inic, t_final=t_final
        )

        # Preparar conexiones con datos de clima
        if lugar_clima is None:
            if clima is not None:
                raise ValueError(_('Hay que especificar un lugar para incorporar el clima.'))
        else:
            if not simul_fecha:
                raise ValueError(_('Hay que especificar la fecha inicial para simulaciones de clima.'))

            clima = clima or '0'

            # Conectar el clima
            lugar_clima.prep_datos(fecha_inic=t_inic, fecha_final=t_final, tcr=clima)

        # Iniciamos el modelo.
        símismo.iniciar_modelo(n_pasos=n_pasos, t_final=t_final, nombre_corrida=nombre_corrida, vals_inic=vals_inic)

        # Verificar los nombres de los variables de interés
        símismo.vars_saliendo.clear()
        símismo.vars_entrando.clear()

        for i, v in enumerate(vars_interés.copy()):
            var = símismo.valid_var(v)
            vars_interés[i] = var
            símismo.vars_saliendo.add(var)

        if vals_extern is not None:
            for v in vals_extern.data_vars:
                símismo.vars_entrando.add(v)

        # Preparar el objeto Xarray para guardar los resultados
        símismo.mem_vars = mem_vars = xr.Dataset({
            v:
                ('n', np.empty(n_iter + 1)) if (símismo.obt_dims_var(v) in [1, (1,)]) else
                (
                    ('n', *tuple('x' + str(i) for i in símismo.obt_dims_var(v))),
                    np.empty((n_iter + 1, *símismo.obt_dims_var(v)))
                )
            for v in vars_interés
        })

        # Agregar el eje temporal
        if simul_fecha:
            l_tiempos = np.array([t_inic + delta_fecha * i for i in range(n_iter + 1)], dtype='datetime64')
        else:
            l_tiempos = np.arange(t_inic, t_final + paso, paso)
        mem_vars.coords['tiempo'] = ('n', l_tiempos)

        # Aquí tenemos dos opciones. Para accelerar simulaciones, podemos correr toda la simulación de una vez
        # (y no paso por paso) si algunas condiciones se respetan:
        if clima is None and símismo.combin_pasos and vals_extern is None:

            # Correr todos los pasos de una vez
            símismo.incrementar(paso=n_iter * paso, guardar_cada=paso)

            # Después de la simulación, cerramos el modelo.
            símismo.cerrar_modelo()

            # Leer los resultados
            res = símismo.leer_arch_resultados(archivo=nombre_corrida, var=vars_interés)
            if 'tiempo' not in res.coords:
                res.coords['tiempo'] = ('n', l_tiempos)

            # Guardar los variables de interés
            for var in vars_interés:
                mem_vars[var][:] = res[var].where(res['tiempo'].isin(mem_vars['tiempo']), drop=True)

        else:
            # Si la manera más rápida no fue posible, tenemos que ir paso por paso.

            def _act_vals_externos(t):
                # Actualizar variables de clima, si necesario
                if clima is not None:
                    símismo._act_vals_clima(t, mem_vars['tiempo'][i + 1], lugar=lugar_clima)

                # Aplicar valores externos
                if vals_extern is not None:
                    # Únicamente aplicar nuevos valores si tenemos valores para este punto de la simulación
                    if np.isin(t, vals_extern['tiempo'].values):
                        vals_ahora = vals_extern.where(vals_extern['tiempo'] == t, drop=True)
                        nuevas = {
                            vr: vals_ahora[vr].values[0]
                            if vals_ahora[vr].values.shape == (1,) else vals_ahora[vr].values
                            for vr in vals_extern.data_vars
                        }
                        símismo.cambiar_vals(nuevas)

            # Hasta llegar al tiempo final, incrementamos el modelo.
            for i in range(n_iter):

                t_actual = mem_vars['tiempo'].values[i]  # El tiempo actual
                _act_vals_externos(t_actual)

                # Guardar resultados para variables de interés
                for var in vars_interés:
                    mem_vars[var][i] = símismo.obt_val_actual_var(var)

                # Incrementar el modelo
                símismo.incrementar(paso)

                # Guardar valores de variables de interés
                if len(vars_interés):
                    símismo.leer_vals()

            # Actualizar y leer los valores finales
            _act_vals_externos(mem_vars['tiempo'].values[-1])
            for v in vars_interés:
                mem_vars[v][-1] = símismo.obt_val_actual_var(v)

            # Después de la simulación, cerramos el modelo.
            símismo.cerrar_modelo()

        if vars_interés is not None:
            return copiar_profundo(símismo.mem_vars)

    def simular_grupo(
            símismo, t_final, t_inic=None, paso=1, nombre_corrida='', vals_inic=None, vals_extern=None, bd=None,
            lugar_clima=None, clima=None, combinar=True, paralelo=None, vars_interés=None, guardar=False
    ):
        """
        Correr grupos de simulación. Puede ser mucho más fácil que de efectuar las corridas manualmente.

        Parameters
        ----------
        t_final : list | dict | ft.date | ft.datetime | str | int
            El tiempo final de la simulación. Puede ser en formato de fecha o numérico. Si no se especifica,
            se inferirá de `vars_extern`.
        t_inic : list | dict | ft.date | ft.datetime | str | int
            El tiempo inicial de la simulación. Puede ser en formato de fecha o numérico. Si no se especifica,
            se inferirá de `vars_extern`.
        paso : list | dict | int
            El paso para la simulación.
        nombre_corrida : list | str
            El nombre de la corrida.
        vals_inic : list | dict | str | list | pd.DataFrame | xr.Dataset
            Valores iniciales para variables. Si es de tipo_mod ``str`` o ``list``, se tomarán los valores de `bd`.
        vals_extern : list | dict | str | list | pd.DataFrame | xr.Dataset
            Valores externos que hay que actualizar a través de la simulación (no necesariamente iniciales).
            Si es de tipo_mod ``str`` o ``list``, se tomarán los valores de `bd`.
        bd : SuperBD | dict | str | pd.DataFrame | xr.Dataset
            Una base de datos opcional. Si se especifica, se empleará para obtener los valores de variables iniciales
            y externos.
        lugar_clima : list | dict | Geog.Lugar
            El lugar para simulaciones con clima.
        clima : list | dict | str | float | int
            El escenario climático.
        combinar : bool
            Si hay que hacer todas las combinaciones posibles de las opciones.
        paralelo : bool
            Si paralelizamos las corridas para ganar tiempo (con modelos rápidos, pierdes en vez de ganar).
            Si es ``None``, Tinamït adivinará si es mejor paralelizar o no.
        vars_interés : str | list[str]
            Los variables de interés en los resultados.
        guardar : bool
            Si hay que guardar los resultados automáticamente en un archivo externo.

        Returns
        -------
        dict[str, xr.Dataset]
            Los resultados de las simulaciones.

        """

        # Formatear los nombres de variables a devolver.
        if vars_interés is not None:
            if isinstance(vars_interés, str):
                vars_interés = [vars_interés]
            vars_interés = [símismo.valid_var(v) for v in vars_interés]

        # Poner las opciones de simulación en un diccionario.
        opciones = {'paso': paso, 't_inic': t_inic, 'lugar_clima': lugar_clima, 'vals_inic': vals_inic,
                    'vals_extern': vals_extern, 'clima': clima, 't_final': t_final}

        # Entender el tipo_mod de opciones (lista, diccionario, o valor único)
        tipos_ops = {
            nmb: dict if isinstance(op, dict) else list if isinstance(op, list) else 'val'
            for nmb, op in opciones.items()
        }

        # Una excepción para "vals_inic" y "vals_extern":
        # si es un diccionario con nombres de variables como llaves, es valor único;
        # si tiene nombres de corridas como llaves y diccionarios de variables como valores, es de tipo_mod diccionario.
        for op in ['vals_inic', 'vals_extern']:
            op_inic = opciones[op]
            if isinstance(op_inic, list):
                tipos_ops[op] = list if len(op_inic) else 'val'
            elif isinstance(op_inic, dict):
                if all(isinstance(v, (dict, xr.Dataset, pd.DataFrame)) or v is None for v in op_inic.values()):
                    tipos_ops[op] = dict if len(op_inic) else 'val'
                elif not any(isinstance(v, (dict, xr.Dataset, pd.DataFrame) or v is None) for v in op_inic.values()):
                    tipos_ops[op] = 'val'
                else:
                    raise ValueError(_('Error en `{op}`.').format(op=op))

        # Generaremos el diccionario de corridas:
        corridas = _gen_dic_ops_corridas(
            nombre_corrida=nombre_corrida, combinar=combinar, tipos_ops=tipos_ops, opciones=opciones
        )

        # Validar los nombres y evitar un problema con nombres de corridas con '.' en Vensim
        mapa_nombres = {corr: valid_nombre_arch(corr.replace('.', '_')) for corr in corridas}
        for ant, nv in mapa_nombres.items():
            corridas[nv] = corridas.pop(ant)

        # Ahora, hacemos las simulaciones
        resultados = {}  # El diccionario de resultados

        # Verificar si vale la pena hacer corridas paralelas o no
        if paralelo is None:
            antes = ft.datetime.now()
            corr0 = list(corridas)[0]
            d_corr0 = corridas.pop(corr0)

            d_corr0['vars_interés'] = vars_interés

            # Después, simular el modelo.
            res = símismo.simular(**d_corr0, nombre_corrida=corr0)

            if res is not None:
                resultados[mapa_nombres[corr0]] = res

            tiempo_simul = (ft.datetime.now() - antes).total_seconds()
            paralelo = tiempo_simul > 15

        # Efectuar las corridas
        if paralelo and símismo.paralelizable():
            # ...si el modelo y todos sus submodelos son paralelizables...

            # Este código un poco ridículo queda necesario para la paralelización en Windows. Si no estuviera aquí,
            # el programa se travaría para siempre a este punto.

            # Un variable MUY largo, que NO DEBE EXISTIR en cualquier otra parte del programa. Por eso tomamos un
            # nombre de variable muy, muy largo que estoy seguro no encontraremos en otro lugar.
            global ejecutando_simulación_paralela_por_primera_vez

            # Si no existía antes, es la primera vez que estamos ejecutando este código
            if 'ejecutando_simulación_paralela_por_primera_vez' not in globals():
                ejecutando_simulación_paralela_por_primera_vez = True

            # Si no es la primera vez, no querremos correr la simulación. (Sino, creerá ramas infinitas del proceso
            # Python).
            if not ejecutando_simulación_paralela_por_primera_vez:
                avisar(_('Parece que estés corriendo simulaciones en paralelo en Windows o alguna cosa parecida '
                         '\nsin poner tu código principal en "if __name__ == "__main__"". Probablemente funcionará'
                         '\nel código de todo modo, pero de verdad no es buena idea.'))
                return

            # Si era la primera vez, ahora ya no lo es.
            ejecutando_simulación_paralela_por_primera_vez = False

            # Empezar las simulaciones en paralelo
            l_trabajos = []  # type: list[tuple]

            copia_mod = pickle.dumps(símismo)  # Una copia de este modelo.

            # Crear la lista de información necesaria para las simulaciones en paralelo...
            for corr, d_prms_corr in corridas.items():
                d_args = {ll: copiar_profundo(v) for ll, v in d_prms_corr.items()}
                d_args['nombre_corrida'] = corr
                d_args['vars_interés'] = vars_interés
                d_args['bd'] = bd

                l_trabajos.append((copia_mod, d_args))

            # Hacer las corridas en paralelo
            with Reserva() as r:
                res_paralelo = r.map(_correr_modelo, l_trabajos)

            # Ya terminamos la parte difícil. Desde ahora, sí permitiremos otras ejecuciones de esta función.
            ejecutando_simulación_paralela_por_primera_vez = True

            # Formatear los resultados, si hay.
            if res_paralelo is not None:
                resultados.update(
                    {mapa_nombres[corr]: res for corr, res in zip(corridas, res_paralelo)}
                )

        else:
            # Sino simplemente correrlas una tras otra con `Modelo.simular()`
            if paralelo:
                avisar(_('\nNo todos los submodelos del modelo conectado "{}" son paralelizable. Para evitar el riesgo'
                         '\nde errores de paralelización, correremos las corridas como simulaciones secuenciales '
                         '\nnormales. '
                         '\nSi tus modelos sí son paralelizables, crear un método nombrado `.paralelizable()` '
                         '\nque devuelve ``True`` en tu clase de modelo para activar la paralelización.'
                         ).format(símismo.nombre))

            # Para cada corrida...
            for corr, d_prms_corr in corridas.items():
                d_prms_corr['vars_interés'] = vars_interés

                # Después, simular el modelo.
                res = símismo.simular(**d_prms_corr, bd=bd, nombre_corrida=corr)

                if res is not None:
                    resultados[mapa_nombres[corr]] = res

        if guardar:
            for corr, res in resultados:
                símismo.guardar_resultados(res=res, nombre=corr)

        return resultados

    def simular_en(
            símismo, t_final=None, t_inic=None, paso=1, nombre_corrida='',
            en=None, escala=None, geog=None, bd=None, vals_inic=None, vals_extern=None,
            lugar_clima=None, clima=None, vars_interés=None,
            guardar=False, paralelo=None
    ):

        if bd is not None:
            bd = gen_SuperBD(bd)

        # Identificar los códigos de lugares en los cuales tenemos que simular
        if geog is not None:
            # Obtener los lugares de la geografía, si posible
            lugares = geog.obt_lugares_en(en=en, escala=escala)
        else:
            # Si no tenemos geografía...

            if escala is not None:
                # ...no es posible emplear escalas también
                raise ValueError(_('Debes especificar una geografía para poder emplear `escala`.'))

            if en is not None:
                # Si se especificó el lugar, tomarlo ahora
                lugares = en
                if not isinstance(lugares, (list, set, tuple)):
                    lugares = [lugares]
            else:
                # Sino, tomar los lugares de la base de datos
                lugares = bd.lugares()

        # Generar datos iniciales y externos para cada lugar
        vals_inic_por_lg = {lg: None for lg in lugares}
        vals_extern_por_lg = {lg: None for lg in lugares}
        for lg in lugares:
            if t_inic is None and bd is not None and lg in bd.lugares():
                t_inic_lg = bd.tiempos(lugar=lg)[0]
            else:
                t_inic_lg = t_inic
            if t_final is None and bd is not None and lg in bd.lugares():
                t_final_lg = bd.tiempos(lugar=lg)[-1]
            else:
                t_final_lg = t_final
            datos_inic, datos_extern = símismo._procesar_vars_extern(
                vars_inic=vals_inic, vars_extern=vals_extern, bd=bd, t_inic=t_inic_lg, t_final=t_final_lg, lg=lg,
            )
            vals_inic_por_lg[lg] = datos_inic
            vals_extern_por_lg[lg] = datos_extern

        # Extraer datos de calibración para cada lugar
        for lg in lugares:
            for vr, d in símismo.calibs.items():
                if lg in d:
                    vals_inic_por_lg[lg][vr] = d[lg]

        # Correr las simulaciones en grupo
        return símismo.simular_grupo(
            t_final=t_final, t_inic=t_inic, paso=paso, nombre_corrida=nombre_corrida,
            vals_inic=vals_inic_por_lg, vals_extern=vals_extern_por_lg,
            lugar_clima=lugar_clima, clima=clima, combinar=False, paralelo=paralelo,
            vars_interés=vars_interés, guardar=guardar
        )

    def guardar_resultados(símismo, res=None, nombre=None, frmt='json', l_vars=None):
        """

        Parameters
        ----------
        res: xr.Dataset
        nombre: str
        frmt: strr
        l_vars: list[str] | str

        Returns
        -------

        """
        if res is None:
            res = símismo.mem_vars
        if nombre is None:
            nombre = símismo.corrida_activa
        if l_vars is None:
            l_vars = list(res.data_vars)
        elif isinstance(l_vars, str):
            l_vars = [l_vars]
        else:
            l_vars = l_vars

        faltan = [x for x in l_vars if x not in res]
        if len(faltan):
            raise ValueError(_('Los variables siguientes no existen en los datos:'
                               '\n{}').format(', '.join(faltan)))

        if frmt[0] != '.':
            frmt = '.' + frmt
        arch = valid_nombre_arch(nombre + frmt)
        if frmt == '.json':
            contenido = res[l_vars].to_dict()
            guardar_json(contenido, arch=arch)

        elif frmt == '.csv':

            with open(arch, 'w', encoding='UTF-8', newline='') as a:
                escr = csv.writer(a)

                escr.writerow(['tiempo'] + res['tiempo'].values.tolist())
                for var in l_vars:
                    vals = res[var].values
                    if len(vals.shape) == 1:
                        escr.writerow([var] + vals.tolist())
                    else:
                        for í in range(vals.shape[1]):
                            escr.writerow(['{}[{}]'.format(var, í)] + vals[:, í].tolist())

        else:
            raise ValueError(_('Formato de resultados "{}" no reconocido.').format(frmt))

    def _incrementar(símismo, paso, guardar_cada=None):
        """
        Esta función debe avanzar el modelo por un periodo de tiempo especificado.

        Parameters
        ----------
        paso : int
            El paso.
        guardar_cada : int
            El paso para guardar resultados.

        """

        raise NotImplementedError

    def incrementar(símismo, paso, guardar_cada=None):
        símismo.vals_actualizadas = False
        símismo._incrementar(paso=paso, guardar_cada=guardar_cada)

    def leer_vals(símismo):

        if not símismo.vals_actualizadas:
            símismo._leer_vals()

            símismo.vals_actualizadas = True

    def _leer_vals(símismo):
        """
        Esta función debe leer los valores del modelo y escribirlos en el diccionario interno de variables. Se
        implementa frequentement con modelos externos de cuyos egresos hay que leer los resultados de una corrida.

        """

        raise NotImplementedError

    def conectar_var_clima(símismo, var, var_clima, conv, combin=None):
        """
        Conecta un variable climático.

        Parameters
        ----------
        var : str
            El nombre interno del variable en el modelo.
        var_clima : str
            El nombre oficial del variable climático.
        conv : number
            La conversión entre el variable clima en Tinamït y el variable correspondiente en el modelo.
        combin : str
            Si este variable se debe adicionar o tomar el promedio entre varios pasos.
        """

        var = símismo.valid_var(var)

        if var_clima not in Geog.conv_vars:
            raise ValueError(_('El variable climático "{}" no es una posibilidad. Debe ser uno de:\n'
                               '\t{}').format(var_clima, ', '.join(Geog.conv_vars)))

        if combin not in ['prom', 'total', None]:
            raise ValueError(_('"Combin" debe ser "prom", "total", o None, no "{}".').format(combin))

        símismo.vars_clima[var] = {
            'nombre_extrn': var_clima,
            'combin': combin,
            'conv': conv
        }

    def desconectar_var_clima(símismo, var):
        """
        Esta función desconecta un variable climático.

        Parameters
        ----------
        var : str
            El nombre interno del variable en el modelo.

        """

        símismo.vars_clima.pop(var)

    def cambiar_vals(símismo, valores):
        """
        Esta función cambia el valor de uno o más variables del modelo.

        Parameters
        ----------
        valores : dict
            Un diccionario de variables y sus valores para cambiar.


        """

        # Cambia primero el valor en el diccionario interno del Modelo
        símismo._act_vals_dic_var(valores=valores)

        # Cambiar, si necesario, los valores de los variables en el modelo externo
        símismo._cambiar_vals_modelo_externo(valores=valores)

    def _cambiar_vals_modelo_externo(símismo, valores):
        """
        Esta función debe cambiar el valor de variables en el modelo externo, si aplica.
        Parameters
        ----------
        valores : dict
            Un diccionario de variables y sus valores para cambiar.

        """

        raise NotImplementedError

    def cerrar_modelo(símismo):
        """
        Esta función debe tomar las acciones necesarias para terminar la simulación y cerrar el modelo, si aplica.
        Si no aplica, usar ``pass``.
        """
        raise NotImplementedError

    def _act_vals_clima(símismo, f_0, f_1, lugar):
        """
        Actualiza los variables climáticos. Esta función es la automática para cada modelo. Si necesitas algo más
        complicado (como, por ejemplo, predicciones por estación), la puedes cambiar en tu subclase.

        Parameters
        ----------
        f_0 : ft.date | ft.datetime
            La fecha actual.
        f_1 : ft.date | ft.datetime
            La próxima fecha.
        lugar : Lugar
            El objeto `Lugar` del cual obtendremos el clima.

        """

        # Si no tenemos variables de clima, no hay nada que hacer.
        if not len(símismo.vars_clima):
            return

        # Avisar si arriesgamos perder presición por combinar datos climáticos.
        n_días = int((f_1 - f_0) / np.timedelta64(1, 'D'))
        if n_días > 1:
            avisar('El paso es de {} días. Puede ser que las predicciones climáticas pierdan '
                   'en precisión.'.format(n_días))

        # Correspondencia entre variables climáticos y sus nombres en el modelo.
        nombres_extrn = [d['nombre_extrn'] for d in símismo.vars_clima.values()]

        # La lista de maneras de combinar los valores diarios
        combins = [d['combin'] for d in símismo.vars_clima.values()]

        # La lista de factores de conversión
        convs = [d['conv'] for d in símismo.vars_clima.values()]

        # Calcular los datos
        datos = lugar.comb_datos(vars_clima=nombres_extrn, combin=combins, f_inic=f_0, f_final=f_1)

        # Aplicar los valores de variables calculados
        for i, var in enumerate(símismo.vars_clima):
            # Para cada variable en la lista de clima...

            # El nombre oficial del variable de clima
            var_clima = nombres_extrn[i]

            # El factor de conversión de unidades
            conv = convs[i]

            # Aplicar el cambio
            símismo.cambiar_vals(valores={var: datos[var_clima] * conv})

    def estab_conv_unid_tiempo(símismo, unid_ref, unid=None, factor=1):
        """
        Establece, manualmente, el factor de conversión para convertir la unidad de tiempo del modelo a unidades
        reconocidas por Tinamït. Únicamente necesario si Tinamït no logra inferir este factor por sí mismo.

        Parameters
        ----------
        unid_ref : str
            La unidad de referencia.
        unid : str
            La unidad para convertir a la unidad de referencia. Dejar como ``None`` para utilizar la unidad de tiempo
            del modelo.
        factor : float | int
            El factor de conversión entre la unidad del modelo y la de referencia.
        """

        if unid is None:
            unid = símismo.unidad_tiempo()

        símismo._conv_unid_tiempo[unid] = {'ref': unid_ref, 'factor': factor}

    def dibujar_mapa(símismo, var, geog, directorio, corrida=None, i_paso=None, colores=None, escala=None):
        """
        Dibuja mapas espaciales de los valores de un variable.

        :param var: El variable para dibujar.
        :type var: str
        :param corrida: El nombre de la corrida para dibujar.
        :type corrida: str
        :param directorio: El directorio, relativo al fuente EnvolturasMDS, donde hay que poner los dibujos.
        :type directorio: str
        :param i_paso: Los pasos a los cuales quieres dibujar los egresos.
        :type i_paso: list | tuple | int
        :param colores: La escala de colores para representar los valores del variable.
        :type colores: tuple | list | int
        :param escala: La escala de valores para el dibujo. Si ``None``, será el rango del variable.
        :type escala: list | np.ndarray
        """

        if geog is None:
            raise ValueError(_('Debes especificar una geografía para poder dibujar mapas de resultados.'))

        # Validar el nombre del variable.
        var = símismo.valid_var(var)

        # Preparar el nombre del variable para uso en el nombre del fuente.
        nombre_var = valid_nombre_arch(var)

        bd = símismo.leer_resultados(var=var, corrida=corrida)

        if isinstance(i_paso, tuple):
            i_paso = list(i_paso)
        if i_paso is None:
            i_paso = [0, bd.shape[-1]]
        if isinstance(i_paso, int):
            i_paso = [i_paso, i_paso + 1]
        if i_paso[0] is None:
            i_paso[0] = 0
        if i_paso[1] is None:
            i_paso[1] = bd.shape[-1]

        unid = símismo.obt_unidades_var(var)
        if escala is None:
            escala = np.min(bd), np.max(bd)

        # Incluir el nombre de la corrida en el directorio, si no es que ya esté allí.
        if os.path.split(directorio)[1] != corrida:
            dir_corrida = valid_nombre_arch(corrida)
            directorio = os.path.join(directorio, dir_corrida)

        # Crear el directorio, si no existe ya.
        if not os.path.isdir(directorio):
            os.makedirs(directorio)
        else:
            # Si ya existía el directorio, borrar dibujos ya existentes con este nombre (de corridas anteriores).
            for arch in os.listdir(directorio):
                if re.match(valid_nombre_arch(nombre_var), arch):
                    os.remove(os.path.join(directorio, arch))

        for i in range(*i_paso):
            valores = bd[..., i]
            nombre_archivo = os.path.join(directorio, '{}, {}'.format(nombre_var, i))
            geog.dibujar(archivo=nombre_archivo, valores=valores, título=var, unidades=unid,
                         colores=colores, escala_num=escala)

    def valid_var(símismo, var):
        if var in símismo.variables:
            return var
        else:
            raise ValueError(_('El variable "{}" no existe en el modelo "{}". Pero antes de quejarte '
                               'al gerente, sería buena idea verificar '
                               'si lo escrbiste bien.')  # Sí, lo "escrbí" así por propósito. :)
                             .format(var, símismo))

    def obt_info_var(símismo, var):
        """
        Devuelve la documentación de un variable.

        Parameters
        ----------
        var : str
            El nombre del variable.

        Returns
        -------
        str
            La documentación del variable.

        """

        var = símismo.valid_var(var)
        return símismo.variables[var]['info']

    def obt_unidades_var(símismo, var):
        """
        Devuelve las unidades de un variable.

        Parameters
        ----------
        var : str
            El nombre del variable.

        Returns
        -------
        str
            Las unidades del variable.

        """
        var = símismo.valid_var(var)
        return símismo.variables[var]['unidades']

    def obt_val_actual_var(símismo, var):
        """
        Devuelve el valor actual de un variable.

        Parameters
        ----------
        var : str
            El nombre del variable.

        Returns
        -------
        float | int | np.ndarray
            El valor del variable.

        """

        var = símismo.valid_var(var)
        return símismo.variables[var]['val']

    def obt_lims_var(símismo, var):
        """
        Devuelve los límites de un variable.

        Parameters
        ----------
        var : str
            El nombre del variable.

        Returns
        -------
        tuple | None
            Los límites del variable.

        """

        var = símismo.valid_var(var)
        return símismo.variables[var]['líms']

    def obt_dims_var(símismo, var):
        """
        Devuelve las dimensiones de un variable.

        Parameters
        ----------
        var : str
            El nombre del variable.

        Returns
        -------
        tuple
            Las dimensiones del variable.

        """

        var = símismo.valid_var(var)
        val = símismo.variables[var]['val']
        if isinstance(val, np.ndarray):
            return val.shape
        else:
            return (1,)

    def obt_ec_var(símismo, var):
        """
        Devuelve la ecuación de un variable.

        Parameters
        ----------
        var : str
            El nombre del variable.

        Returns
        -------
        str | None
            La ecuación del variable. Si no tiene ecuación, devuelve ``None``.

        """

        var = símismo.valid_var(var)
        try:
            return símismo.variables[var]['ec']
        except KeyError:
            return

    def egresos(símismo):
        """
        Devuelve los variables egresos del modelo.

        Returns
        -------
        list[str]
            Una lista de los variables egresos.

        """

        return [v for v, d_v in símismo.variables.items() if d_v['egreso']]

    def ingresos(símismo):
        """
        Devuelve los variables ingresos del modelo.

        Returns
        -------
        list[str]
            Una lista de los variables ingresos.

        """

        return [v for v, d_v in símismo.variables.items() if d_v['ingreso']]

    def constantes(símismo):
        return [var for var, d_var in símismo.variables.items() if
                'tipo' in d_var and d_var['tipo'] == 'constante']

    def iniciales(símismo):
        return [var for var, d_var in símismo.variables.items() if
                'tipo' in d_var and d_var['tipo'] == 'inicial']

    def paráms(símismo):
        """
        Devuelve los nombres de los parámetros del modelo.

        Returns
        -------
        dict[str, list[str]]
            Un diccionario, dónde `seguros` es una lista de los variables que son seguramente parámetros,
            y `potenciales` una lista de variables que podrían ser parámetros.

        """

        seguros = [v for v in símismo.constantes() if v not in símismo.iniciales()]

        potenciales = [
            v for v, d_v in símismo.variables.items() if
            v not in seguros and v in símismo.ingresos() and v not in símismo.egresos() and v not in símismo.iniciales()
        ]

        return {'seguros': seguros, 'potenciales': potenciales}

    def leer_resultados(símismo, var=None, corrida=None):
        """

        Parameters
        ----------
        var: str | list[str]
        corrida: str

        Returns
        -------

        """

        if isinstance(var, str):
            l_vars = [var]
        else:
            l_vars = var

        # Verificar que existe el variable en este modelo.
        l_vars = [símismo.valid_var(v) for v in l_vars]

        # Si no se especificó corrida especial, tomaremos la corrida más recién.
        if corrida is None:
            if símismo.corrida_activa is None:
                raise ValueError(_('Debes especificar una corrida.'))
            else:
                corrida = símismo.corrida_activa

        res = None
        # Leer de la memoria temporaria, si estamos interesadas en la corrida más recién
        if corrida == símismo.corrida_activa:
            try:
                res = símismo.mem_vars[l_vars]
            except KeyError:
                pass
        if res is None:
            res = símismo.leer_arch_resultados(archivo=corrida, var=l_vars)

        return res

    @classmethod
    def leer_arch_resultados(cls, archivo, var=None, col_tiempo='tiempo'):

        if isinstance(var, str):
            l_vars = [var]
        else:
            l_vars = var

        corr, ext = os.path.splitext(archivo)
        if len(ext):
            ext_potenciales = [ext]
        else:
            ext_potenciales = ['.json', '.csv']
        res = None
        for ex in ext_potenciales:
            arch = corr + ex
            if not os.path.isfile(arch):
                continue
            codif = detectar_codif(arch, cortar=',' if ex == '.csv' else None)
            if ex == '.json':
                dic = cargar_json(arch, codif=codif)
                res = xr.Dataset.from_dict(dic)[l_vars]
                break
            elif ex == '.csv':
                res = {}
                with open(arch, encoding=codif) as d:
                    lector = csv.reader(d)
                    n_datos = None
                    for i, f in enumerate(lector):
                        if i == 0:
                            n_datos = len(f) - 1
                        grp = re.match('(.*)(\[.*\])$', f[0])  # Detectar variables con subscriptos
                        if grp:
                            v = grp.group(1)
                            if v in res:
                                res[v].append(f[1:])
                            else:
                                res[v] = [f[1:]]
                        else:
                            if f[0] in l_vars:
                                if len(f[1:]) == 1:
                                    res[f[0]] = np.full(n_datos, f[1])
                                else:
                                    res[f[0]] = np.array(f[1:], dtype=float)
                            elif f[0] == col_tiempo:
                                try:
                                    res['tiempo'] = np.array(f[1:], dtype=float)
                                except ValueError:
                                    res['tiempo'] = np.array(f[1:], dtype='datetime64')
                for vr, val in res.items():
                    if isinstance(val, list):
                        res[vr] = np.array(val, dtype=float).swapaxes(0, -1)  # eje 0: tiempo, ejes 1+: dims
                res = {ll: np.array(v, dtype=float) for ll, v in res.items()}
                break
            else:
                raise ValueError(_('El formato de datos "{}" no se puede leer al momento.').format(ext))

        if res is None:
            raise FileNotFoundError(_('No se encontró fuente de resultados para "{}".').format(archivo))

        # Convertir a Xarray
        res_xr = xr.Dataset({
            vr:
                ('n', res[vr]) if len(res[vr].shape) == 1 else
                (('n', *tuple('x' + str(i) for i in res[vr].shape)), res[vr])
            for vr in l_vars
        })
        res_xr.coords['tiempo'] = ('n', res['tiempo'])
        return res_xr

    def paralelizable(símismo):
        """
        Indica si el modelo actual se puede paralelizar de manera segura o no. Si implementas una subclase
        paralelizable, reimplementar esta función para devolver ``True``.
        ¿No sabes si es paralelizable tu modelo?
        Si el modelo se puede paralelizar (con corridas de nombres distintos) sin encontrar dificultades
        técnicas (sin riesgo que las corridas paralelas terminen escribiendo en los mismos archivos de egreso),
        entonces sí es paralelizable tu modelo.

        Returns
        -------
        bool:
            Si el modelo es paralelizable o no.
        """

        return False

    def instalado(símismo):
        """
        Si tu modelo depiende en una instalación de otro programa externo a Tinamït, puedes reimplementar esta función
        para devolver ``True`` si el modelo está instalado y ``False`` sino.

        Returns
        -------
        bool
            Si el modelo está instalado completamente o no.
        """

        return True

    def actualizar_trads(símismo, auto_llenar=True):
        raíz = arbole.Element('xliff', version='1.2')
        arch = arbole.SubElement(raíz, 'file', datatype='Modelo Tinamït', original=símismo.nombre)
        arch.set('source-language', símismo.leng_orig)
        cuerpo = arbole.SubElement(arch, 'body')

        for v, d_v in símismo.variables.items():
            grupo = arbole.SubElement(cuerpo, 'group', id=v)

            trans_nombre = arbole.SubElement(grupo, 'trans-unit')
            fnt = arbole.SubElement(trans_nombre, 'source', lang=símismo.leng_orig)
            fnt.text = v

            trans_info = arbole.SubElement(grupo, 'trans-unit')
            fnt = arbole.SubElement(trans_info, 'source', lang=símismo.leng_orig)
            fnt.text = d_v['info']

            trans_unids = arbole.SubElement(grupo, 'trans-unit')
            fnt = arbole.SubElement(trans_unids, 'source', lang=símismo.leng_orig)
            fnt.text = d_v['unidades']

    def cambiar_lengua(símismo, lengua):
        pass

    def agregar_lengua(símismo, lengua):
        pass

    def especificar_micro_calib(símismo, var, método=None, paráms=None, líms_paráms=None, tipo=None,
                                escala=None, ops_método=None, ec=None, binario=False):

        # Verificar el variable
        var = símismo.valid_var(var)

        if ec is None and 'ec' not in símismo.variables[var]:
            raise ValueError(_('El variable "{}" no tiene ecuación asociada.').format(var))

        # Especificar la micro calibración.
        símismo.info_calibs['micro calibs'][var] = {
            'escala': escala,
            'método': método,
            'ops_método': ops_método,
            'paráms': paráms,
            'líms_paráms': líms_paráms,
            'binario': binario,
            'tipo': tipo,
            'ec': ec

        }

    def verificar_micro_calib(símismo, var, bd, en=None, escala=None, geog=None, corresp_vars=None):
        """
        Comprueba una microcalibración a pequeña (o grande) escala. Útil para comprobar calibraciones sin perder
        mucho tiempo calculándolas para toda la región de interés.

        Parameters
        ----------
        var : str
            El variable de interés.

        en : str
            Dónde hay que calibrar. Por ejemplo, calibrar en el departamento de Tz'olöj Ya'. Si no se especifica,
            se tomará la región geográfica en su totalidad. Solamente aplica si la base de datos vinculada tiene
            geografía asociada.

        escala : str
            La escala a la cual calibrar. Por ejemplo, calibrar al nivel municipal en el departamento de Tz'olöj Ya'.
            Si no se especifica, se tomará la escala correspondiendo a `en`. Solamente aplica si la base de datos
            vinculada tiene geografía asociada.

        Returns
        -------
        dict[str, dict]
            La calibración completada.

        """

        # Efectuar la calibración del variable.
        return símismo._calibrar_var(var=var, bd=bd, en=en, escala=escala, geog=geog, corresp_vars=corresp_vars)

    def efectuar_micro_calibs(
            símismo, bd, en=None, escala=None, jrq=None, geog=None, corresp_vars=None, autoguardar=False, recalc=True,
            guardar_en=None
    ):
        """

        Parameters
        ----------
        en : str
            Dónde hay que calibrar. Por ejemplo, calibrar en el departamento de Tz'olöj Ya'. Si no se especifica,
            se tomará la región geográfica en su totalidad. Solamente aplica si la base de datos vinculada tiene
            geografía asociada.

        escala : str
            La escala a la cual calibrar. Por ejemplo, calibrar al nivel municipal en el departamento de Tz'olöj Ya'.
            Si no se especifica, se tomará la escala correspondiendo a `en`. Solamente aplica si la base de datos
            vinculada tiene geografía asociada.

        geog: Geografía
            Una geografía para calibraciones espaciales.

        corresp_vars : dict
            Un diccionario de correspondencia entre nombres de variables en el modelo y los nombres de los variables
            correspondiente en la base de datos.

        autoguardar : bool
            Si hay que guardar los resultados automáticamente entre cada variable calibrado. Útil para calibraciones
            que toman mucho tiempo.

        recalc : bool
            Si hay que recalcular calibraciones que ya se habían calculado.

        Returns
        -------
        dict
            La calibración.
        """

        # Borramos calibraciones existentes
        if recalc:
            símismo.calibs.clear()

        # Para cada microcalibración...
        for var, d_c in símismo.info_calibs['micro calibs'].items():

            no_recalc = {v: [lg for lg in d_v] for v, d_v in símismo.calibs.items()} if not recalc else None

            # Efectuar la calibración
            calib = símismo._calibrar_var(
                var=var, bd=bd, en=en, escala=escala, jrq=jrq, geog=geog, hermanos=True, corresp_vars=corresp_vars,
                no_recalc=no_recalc
            )
            if calib is None:
                continue

            # Guardar las calibraciones para este variable y todos los otros variables que potencialmente
            # fueron calibrados al mismo tiempo.
            for v in calib:
                símismo.calibs[v] = calib[v]

            # Autoguardar, si querremos.
            if autoguardar:
                símismo.guardar_calibs(guardar_en)

    def _calibrar_var(símismo, var, bd, en=None, escala=None, jrq=None, geog=None, hermanos=False, corresp_vars=None,
                      no_recalc=None):
        print(var)
        # La lista de variables que hay que calibrar con este.
        # l_vars = símismo._obt_vars_asociados(var, enforzar_datos=True, incluir_hermanos=hermanos)
        l_vars = {}  # para hacer: arreglar problemas de determinar paráms vs. otras ecuaciones

        # Preparar la ecuación
        ec = símismo.info_calibs['micro calibs'][var]['ec'] or símismo.variables[var]['ec']

        # El objeto de calibración.
        mod_calib = CalibradorEc(
            ec=ec, dialecto=símismo.dialecto_ec, var_y=var, otras_ecs={v: símismo.variables[v]['ec'] for v in l_vars},
            corresp_vars=corresp_vars
        )

        # El método de calibración
        método = símismo.info_calibs['micro calibs'][var]['método']
        líms_paráms = símismo.info_calibs['micro calibs'][var]['líms_paráms']
        paráms = símismo.info_calibs['micro calibs'][var]['paráms']
        ops = símismo.info_calibs['micro calibs'][var]['ops_método']
        tipo = símismo.info_calibs['micro calibs'][var]['tipo']
        binario = símismo.info_calibs['micro calibs'][var]['binario']

        # Aplicar límites automáticos
        if líms_paráms is None:
            if paráms is not None:
                líms_paráms = {p: símismo.variables[p]['líms'] for p in paráms}
            else:
                líms_paráms = {p: símismo.variables[p]['líms'] for p in símismo.variables}

        # Efectuar la calibración.
        calib = mod_calib.calibrar(
            paráms=paráms, líms_paráms=líms_paráms, método=método, bd_datos=bd, geog=geog, tipo=tipo,
            en=en, escala=escala, jrq=jrq, ops_método=ops, no_recalc=no_recalc, binario=binario
        )
        if calib is None:
            return

        # Reformatear los resultados
        resultado = {}
        for lg, d_lg in calib.items():
            if d_lg is None:
                continue
            for p in d_lg:
                if p not in resultado:
                    resultado[p] = {}
                resultado[p][lg] = d_lg[p]

        return resultado

    def _obt_vars_asociados(símismo, var, bd=None, enforzar_datos=False, incluir_hermanos=False):
        """
        Obtiene los variables asociados con un variable de interés.

        Parameters
        ----------
        var : str
            El variable de interés.
        enforzar_datos : bool
            Si buscamos únicamente variables que tienen datos en la base de datos vinculada.
        incluir_hermanos :
            Si incluyemos los hermanos del variable (es decir, otros variables que se computan a base de los parientes
            del variable de interés.

        Returns
        -------
        set
            El conjunto de todos los variables vinculados.

        Raises
        ------
        ValueError
            Si no todos los variables asociados tienen ecuación especificada.
        RecursionError
            Si `enforzar_datos == True` y no hay suficientemente datos disponibles para encontrar parientes con datos
            para todos los variables asociados con el variable de interés.
        """

        # La base de datos
        bd_datos = bd if enforzar_datos else None

        # El diccionario de variables
        d_vars = símismo.variables

        # Una función recursiva queda muy útil en casos así.
        def _sacar_vars_recurs(v, c_v=None, sn_dts=None):
            """
            Una función recursiva para sacar variables asociados con un variable de interés.
            Parameters
            ----------
            v : str
                El variable de interés.
            c_v : set
                El conjunto de variables asociados (parámetro de recursión).

            Returns
            -------
            set
                El conjunto de variables asociados.

            """

            # Para evitar problemas de recursión en Python.
            if c_v is None:
                c_v = set()
            if sn_dts is None:
                sn_dts = set()

            # Verificar que el variable tenga ecuación
            if 'ec' not in d_vars[v]:
                raise ValueError(_('El variable "{}" no tiene ecuación.').format(v))

            # Los parientes del variable
            parientes = d_vars[v]['parientes']

            # Agregar los parientes al conjunto de variables vinculados
            c_v.update(parientes)

            for p in parientes:
                # Para cada pariente...

                p_bd = conex_var_datos[p] if p in conex_var_datos else p
                if bd_datos is not None and p_bd not in bd_datos:
                    # Si tenemos datos y este variable pariente no existe, tendremos que buscar sus parientes también.

                    # ...pero si ya encontramos este variable en otra recursión, quiere decir que no tenemos
                    # suficientemente datos y que estamos andando en círculos.
                    if p in sn_dts:
                        raise RecursionError(
                            _('Estamos andando en círculos buscando variables con datos disponibles. Debes '
                              'especificar más datos. Puedes empezar con uno de estos variables: {}'
                              ).format(', '.join(sn_dts))
                        )

                    # Acordarse que ya intentamos buscar parientes con datos para este variable
                    sn_dts.add(p)

                    # Seguir con la recursión
                    _sacar_vars_recurs(v=p, c_v=c_v, sn_dts=sn_dts)

                if incluir_hermanos:
                    # Si incluyemos a los hermanos, agregarlos y sus parientes aquí.
                    hijos = d_vars[p]['hijos']
                    c_v.update(hijos)
                    for h in hijos:
                        if h not in c_v:
                            _sacar_vars_recurs(v=h, c_v=c_v, sn_dts=sn_dts)

            # Devolver el conjunto de variables asociados
            return c_v

        return _sacar_vars_recurs(var)

    def borrar_micro_calib(símismo, var):
        try:
            símismo.info_calibs['micro calibs'].pop(var)
        except KeyError:
            raise ValueError(_('El variable "{}" no está asociado con una microcalibración.').format(var))

    def borrar_info_calibs(símismo):
        """
        Borra las especificaciones de calibraciones.

        """

        símismo.info_calibs['micro calibs'].clear()
        símismo.info_calibs['calibs'].clear()

    def borrar_calibs(símismo):
        """
        Borra calibraciones.

        """

        símismo.calibs.clear()

    def guardar_calibs(símismo, archivo=None):
        """
        Guarda las calibraciones en un archivo exterior.

        Parameters
        ----------
        archivo : str
            Dónde hay que guardar las calibraciones. Si es ``None``, se tomará el nombre del modelo.

        """

        if archivo is None:
            archivo = '{}_calibs'.format(símismo.nombre)

        # Copiar el diccionario y formatearlo para json.
        dic = símismo.calibs.copy()
        jsonificar(dic)

        # Guardarlo
        guardar_json(dic, archivo)

    def cargar_calibs(símismo, archivo=None):
        if archivo is None:
            archivo = '{}_calibs'.format(símismo.nombre)

        if isinstance(archivo, str):
            dic = cargar_json(archivo)
            numpyficar(dic)
        elif isinstance(archivo, dict):
            dic = archivo
        else:
            raise TypeError

        símismo.calibs.clear()

        símismo.calibs.update(dic)

    def calibrar(símismo, paráms, bd, líms_paráms=None, vars_obs=None, n_iter=500, método='mle'):

        if vars_obs is None:
            l_vars = None
        elif isinstance(vars_obs, str):
            l_vars = [símismo.valid_var(vars_obs)]
        else:
            l_vars = [símismo.valid_var(v) for v in vars_obs]

        if líms_paráms is None:
            líms_paráms = {}
        for p in paráms:
            if p not in líms_paráms:
                líms_paráms[p] = símismo.obt_lims_var(p)
        líms_paráms = {ll: v for ll, v in líms_paráms.items() if ll in paráms}

        if isinstance(bd, dict) and all(isinstance(v, xr.Dataset) for v in bd.values()):
            for lg in bd:
                calibrador = CalibradorMod(símismo)
                d_calibs = calibrador.calibrar(
                    paráms=paráms, bd=bd[lg], líms_paráms=líms_paráms, método=método, n_iter=n_iter, vars_obs=l_vars
                )
                for var in d_calibs:
                    if var not in símismo.calibs:
                        símismo.calibs[var] = {}
                    símismo.calibs[var][lg] = d_calibs[var]

        else:
            calibrador = CalibradorMod(símismo)
            d_calibs = calibrador.calibrar(
                paráms=paráms, bd=bd, líms_paráms=líms_paráms, método=método, n_iter=n_iter, vars_obs=l_vars
            )
            símismo.calibs.update(d_calibs)

    def validar(símismo, bd, var=None, t_final=None, corresp_vars=None):
        if isinstance(bd, dict) and all(isinstance(v, xr.Dataset) for v in bd.values()):
            res = {}
            for lg in bd:
                bd_lg = gen_SuperBD(bd[lg])
                vld = símismo._validar(bd=bd_lg, var=var, t_final=t_final, corresp_vars=corresp_vars, lg=lg)
                res[lg] = vld
            res['éxito'] = all(d['éxito'] for d in res.values())
            return res
        else:
            bd = gen_SuperBD(bd)
            return símismo._validar(bd=bd, var=var, t_final=t_final, corresp_vars=corresp_vars)

    def _validar(símismo, bd, var, t_final, corresp_vars, lg=None):
        if corresp_vars is None:
            corresp_vars = {}

        if var is None:
            l_vars = [v for v in bd.variables if
                      v in símismo.variables or v in corresp_vars.values()]
        elif isinstance(var, str):
            l_vars = [var]
        else:
            l_vars = var
        l_vars = [símismo.valid_var(v) for v in l_vars]
        obs = bd.obt_datos(l_vars)[l_vars]
        if t_final is None:
            t_final = len(obs['n']) - 1
        if lg is None:
            d_vals_prms = {p: d_p['dist'] for p, d_p in símismo.calibs.items()}
        else:
            d_vals_prms = {p: d_p[lg]['dist'] for p, d_p in símismo.calibs.items()}
        n_vals = len(list(d_vals_prms.values())[0])
        vals_inic = [{p: v[í] for p, v in d_vals_prms.items()} for í in range(n_vals)]
        res_simul = símismo.simular_grupo(
            t_final, vals_inic=vals_inic, vars_interés=l_vars, combinar=False, paralelo=False
        )

        matrs_simul = {vr: np.array([d[vr].values for d in res_simul.values()]) for vr in l_vars}

        resultados = validar_resultados(obs=obs, matrs_simul=matrs_simul)
        return resultados

    @classmethod
    def _obt_val_config(cls, llave, cond=None, mnsj_error='', respaldo=None):
        """
        Devuelve un valor de configuración Tinamït para el modelo actual.

        Parameters
        ----------
        llave : str
            La llave de configuración.
        cond : callable
            Una prueba opcional para validar el valor de configuración.
        mnsj_error : str
            Un mensaje en caso de error.
        respaldo : str, list[str]
            Un valor de respaldo si no se obtiene un valor de configuración aceptable.

        Returns
        -------
        str | None
            El valor de configuración. Devuelve ``None`` si no se encontró o si no pasó la prueba de `cond`.

        """

        # Convertir la llave a una lista
        if isinstance(llave, str):
            llave = [llave]

        # Agregar el nombre de la clase actual
        llave = ['envolturas', cls.__name__] + llave

        # Preparar el mensaje de error.
        mnsj_error += '\nPuedes especificar el valor de configuración con' \
                      '\n\ttinamit.config.poner_val_config({ll}, {val})'.format(ll=llave, val='"mi_valor_aquí"')

        # Obtener el valor de configuración.
        return obt_val_config(llave=llave, cond=cond, mnsj_err=mnsj_error, respaldo=respaldo)

    def __str__(símismo):
        return símismo.nombre

    def __getinitargs__(símismo):
        return símismo.nombre,

    def __copy__(símismo):
        copia = símismo.__class__(*símismo.__getinitargs__())
        copia.vars_clima = símismo.vars_clima
        copia._conv_unid_tiempo = símismo._conv_unid_tiempo

        return copia

    def __getstate__(símismo):
        d = {
            'args_inic': símismo.__getinitargs__(),
            'vars_clima': símismo.vars_clima,
            '_conv_unid_tiempo': símismo._conv_unid_tiempo
        }
        return d

    def __setstate__(símismo, estado):
        símismo.__init__(*estado['args_inic'])
        símismo.vars_clima = estado['vars_clima']
        símismo._conv_unid_tiempo = estado['_conv_unid_tiempo']


def _correr_modelo(x):
    """
    Función para inicializar y correr un modelo en paralelo.

    Parameters
    ----------
    x : tuple[Modelo, dict]
        Los parámetros. El primero es el modelo, el segundo el diccionario de parámetros para la simulación.

    Returns
    -------
    dict
        Los resultados de la simulación.
    """

    estado_mod, d_args = x

    mod = pickle.loads(estado_mod)

    # Después, simular el modelo y devolver los resultados, si hay.
    return mod.simular(**d_args)


def _gen_dic_ops_corridas(nombre_corrida, combinar, tipos_ops, opciones):
    """
    Genera un diccionario de corridas con sus opciones.

    Parameters
    ----------
    nombre_corrida : str
        El nombre de base de la corrida.
    combinar : bool
        Si hay que hacer todas las permutaciones posibles de las opciones.
    tipos_ops : dict
        Un diccionario especificando si cada opción está en formato de lista, diccionario, o valor.
    opciones : dict
        El diccionario de las opciones para las corridas.

    Returns
    -------
    dict[str, dict]
        El diccionario formateado correctamente.

    """

    # Una matriz con el número de valores distintos para cada opción, guardando únicamente las opciones con valores
    # múltiples.
    l_n_ops = np.array(
        [
            len(v) for ll, v in opciones.items()  # El número de opciones
            if tipos_ops[ll] in [list, dict]  # Si no es de valor único
        ]
    )
    # Una lista con el nombre de cada opción (p. ej., "paso", etc.) con valores múltiples.
    l_nmbs_ops_var = [
        ll for ll, v in opciones.items()  # El nombre de la opción
        if tipos_ops[ll] in [list, dict]  # Si no es de valor único
    ]

    # Crear el diccionario de corridas
    if combinar:
        # Si estamos combinando las opciones...

        # El nombre de corrida no puede ser una lista si estamos combinando las opciones
        if isinstance(nombre_corrida, list):
            raise TypeError(_('No puedes especificar una lista de nombres de corridas si estás'
                              ' simulando todas las combinaciones posibles de las opciones.'))

        # El número de corridas es el producto del número de valores por opción.
        n_corridas = int(np.prod(l_n_ops))

        dic_ops = {}  # Un diccionario de nombres de simulación y sus opciones de corrida

        # Poblar el diccionario de opciones iniciales
        ops = {}  # Las opciones iniciales
        nombre = []  # Una lista que se convertirá en el nombre de la opción
        for ll, op in opciones.items():
            # Para cada opción...

            if tipos_ops[ll] == 'val':
                # Si no hay valores múltiples, su único valor será su valor permanente.
                ops[ll] = op

            else:
                # Pero si tenemos valores múltiples, damos el primero de la lista o diccionario para empezar.
                if tipos_ops[ll] == dict:
                    # Si es un diccionario...

                    # Tomar el nombre de la primera corrida especificada en el diccionario
                    id_op = list(op)[0]

                    # ...y el valor para esta corrida
                    ops[ll] = op[id_op]

                    # Guardar el nombre también.
                    nombre.append(id_op)

                else:
                    # Si es una lista...

                    ops[ll] = op[0]  # Empezar con el primer valor de la lista

                    # Convertir el índice del valor a un nombre para las corridas
                    nombre.append(f'{ll}0')

        # Una matriz con el número cumulativo de combinaciones de opciones
        l_n_ops_cum = np.roll(l_n_ops.cumprod(), 1)  # Pasamos el número final al principio
        if len(l_n_ops_cum):
            l_n_ops_cum[0] = 1  # ... y reemplazamos el número ahora inicial con ``1``.
        else:
            l_n_ops_cum = [1]  # ... si no tenemos combinaciones que hacer, darle ``1``

        # Crear la lista de diccionarios de opciones para cada corrida.
        for í_c in range(n_corridas):
            # Para cada corrida...

            # Calcular el índice del valor actual para cada opción que tiene valores múltiples
            í_ops = [int(np.floor(í_c / l_n_ops_cum[n]) % l_n_ops[n]) for n in range(l_n_ops.shape[0])]

            # Para cada opción...
            for í_op, n in enumerate(í_ops):

                # Sacamos el nombre de la opción actual
                nmbr_op = l_nmbs_ops_var[í_op]
                op = opciones[nmbr_op]  # El valor de la opción

                # Aplicar los cambios al diccionario transitorio de opciones
                if tipos_ops[nmbr_op] == list:
                    # Si la opción está en formato de lista...

                    # Guardar su valor
                    ops[nmbr_op] = op[n]

                    # Y cambiar su nombre
                    nombre[í_op] = f'{nmbr_op}{n}'

                elif tipos_ops[nmbr_op] == dict:
                    # Sino, es un diccionario

                    # Guardar nu nombre y valor
                    id_op = list(op)[n]
                    ops[nmbr_op] = op[id_op]
                    nombre[í_op] = str(id_op)

                else:
                    raise TypeError(_('Tipo de variable "{}" erróneo. Debería ser imposible llegar hasta este '
                                      'error.'.format(type(op))))

            # Concatenar el nombre y guardar una copia del diccionario transitorio de opciones.
            dic_ops[' '.join(nombre)] = ops.copy()

        # Formatear las corridas con sus nombres de corridas.
        corridas = {
            '{}{}'.format(nombre_corrida + ('_' if nombre_corrida and ll else ''), ll): ops
            for ll, ops in dic_ops.items()
        }  # type: dict[str, dict]

        # Y, por fin, si solamente tenemos una corrida que hacer, asegurarse que tenga un nombre.
        if len(corridas) == 1 and list(corridas)[0] == '':
            corridas['Corrida Tinamït'] = corridas.pop('')

    else:
        # Si no estamos haciendo todas las combinaciones posibles de opciones, es un poco más fácil.

        # Asegurarse de que todas las opciones múltiples sean o diccionarios, o listas
        if any(t is dict for t in tipos_ops.values()):
            if any(t is list for t in tipos_ops.values()):
                raise TypeError(
                    _('Si no estás haciendo combinaciones, no puedes combinar diccionarios con listas.'))
            frmt = dict
        elif any(t is list for t in tipos_ops.values()):
            frmt = list
        else:
            frmt = 'val'

        if frmt is dict:
            # Verificar que las llaves sean consistentes
            lls_dics = next((op.keys() for nmb, op in opciones.items() if tipos_ops[nmb] == dict), None)  # Las llaves
            for nmb, op in opciones.items():
                # Asegurarse que las llaves de esta opción sean iguales al estándar.
                if tipos_ops[nmb] == dict and op.keys() != lls_dics:
                    raise ValueError(_('Las llaves de diccionario de cada opción deben ser iguales.'))

        # Asegurarse de que todas las opciones tengan el mismo número de opciones.
        tmñs_únicos = np.unique(l_n_ops)
        if tmñs_únicos.size == 0:
            n_corridas = 1
        elif tmñs_únicos.size == 1:
            n_corridas = tmñs_únicos[0]  # El número de corridas
        else:
            raise ValueError(_('Si `combinar` == ``False``, todas las opciones en forma de lista o diccionario '
                               'deben tener el mismo número de opciones.'))

        # Preparar la lista de nombres de corridas
        if isinstance(nombre_corrida, str):
            # Si el nombre especificado para la corrida queda en formato texto...

            # ...tenemos que agregarle algo para distinguir entre las varias corridas.
            if frmt is dict:
                # Si hay diccionarios de opciones con nombres de corridas, utilizar éstas.
                l_nombres = next(list(opciones[nmb]) for nmb, t in tipos_ops.items() if t is dict)

                # Generar el diccionario de nombres de corridas con sus valores de simulación correspondientes.
                corridas = {
                    (nombre_corrida + ('_' if len(nombre_corrida) else '')) + nmb_corr:
                        {
                            ll: op[nmb_corr] if tipos_ops[ll] is dict else op for ll, op in opciones.items()
                        }
                    for nmb_corr in l_nombres
                }
            else:
                # Sino, las daremos nombres según números consecutivos
                corridas = {
                    (nombre_corrida + ('_' if len(nombre_corrida) else '')) + str(i):
                        {
                            nmb: op[i] if tipos_ops[nmb] is list else op for nmb, op in opciones.items()
                        }
                    for i in range(n_corridas)
                }

        elif isinstance(nombre_corrida, list):
            # Si tenemos una lista de nombres de corridas...

            # Asegurarse que tenga el tamaño necesario
            if len(nombre_corrida) != n_corridas:
                raise ValueError(
                    _('Una lista de nombres de corrida debe tener el mismo número de nombres ("{}") que hay '
                      'valores de opciones en la simulación ("{}").').format(len(nombre_corrida), n_corridas)
                )

            if frmt is dict:
                raise ValueError(
                    _('No puedes especificar una lista de nombres de corridas si tienes opciones en '
                      'formato de diccionario.')
                )

            # Generar el diccionario de corridas
            corridas = {
                nmb: {ll: op[i] if tipos_ops[ll] is list else op for ll, op in opciones.items()}
                for i, nmb in enumerate(nombre_corrida)
            }

        else:
            raise TypeError(_('El nombre de corrida debe ser o una cadena de texto, o una lista de cadenas '
                              'de texto.'))

    return corridas


def _valid_nombre_mod(nombre):
    """
    No se puede incluir nombres de modelos con "_" en el nombre (podría corrumpir el manejo de variables en
    modelos jerarquizados).

    Parameters
    ----------
    nombre : str
        El nombre propuesto para el modelo.

    Returns
    -------
    str:
        Un nombre aceptable.
    """

    if "_" in nombre:
        avisar(_('No se pueden emplear nombres de modelos con "_", así que no puedes nombrar tu modelo "{}".\n'
                 'Sino, causaría problemas de conexión de variables por una razón muy compleja y oscura.\n'
                 'Vamos a renombrar tu modelo "{}". Lo siento.').format(nombre, nombre.replace('_', '.')))
        nombre = nombre.replace('_', '.')

    return nombre
