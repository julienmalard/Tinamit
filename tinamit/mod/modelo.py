import csv
import datetime as ft
import pickle
from copy import deepcopy as copiar_profundo
from multiprocessing import Pool as Reserva
from warnings import warn as avisar

import numpy as np
import pandas as pd
import tinamit.Geog_.Geog as Geog
import xarray as xr
from tinamit.Análisis.Calibs import CalibradorEc, CalibradorMod
from tinamit.Análisis.Datos import gen_SuperBD, jsonificar, numpyficar, SuperBD
from tinamit.Análisis.Valids import validar_resultados
from tinamit.config import _, conf_mods
from tinamit.cositas import valid_nombre_arch, guardar_json, cargar_json

from .corrida import Corrida
from .var import VariablesMod, Variable


class Modelo(object):
    """
    Todas las cosas en Tinamit son instancias de `Modelo`, que sea un modelo de dinámicas de los sistemas, un modelo de
    cultivos o de suelos o de clima, o un modelo conectado.
    Cada tipo de modelo se representa por subclases específicas. Por eso, la gran mayoría de los métodos definidos
    aquí se implementan de manera independiente en cada subclase de `Modelo`.
    """

    leng_orig = 'es'

    def __init__(símismo, nombre):
        """
        La función de inicialización de todos modelos, conectados o no.

        Parameters
        ----------
        nombre : str
            El nombre del modelo.

        """

        # El nombre del modelo
        símismo.nombre = nombre

        símismo.variables = VariablesMod(símismo._gen_vars())

    def _gen_vars(símismo):
        """

        Returns
        -------
        list[Variable]

        """

        raise NotImplementedError

    def unidad_tiempo(símismo):
        """
        Esta función debe devolver la unidad de tiempo empleada por el modelo.

        Returns
        -------
        str
            La unidad de tiempo (p. ej., 'meses', 'مہینہ', etc.)
        """

        raise NotImplementedError

    def simular(símismo, t, nombre_corrida='Tinamït', vals_inic=None, vals_extern=None, clima=None, vals_interés=None):
        vars_interés = vals_interés or símismo.variables

        corrida = Corrida(
            nombre_corrida, eje_tiempo=gen_eje_tiempo(t), extern=gen_vals_extern(vals_inic, vals_extern)
        )

        símismo.iniciar_modelo(corrida)
        res = símismo.correr(corrida)
        símismo.cerrar()

        return res

    def simular_grupo(símismo, t, nombre_corrida='Tinamït', vals_inic=None, vals_extern=None):
        pass

    def iniciar_modelo(símismo, corrida):
        símismo.variables.resultados.actualizar()

    def correr(símismo, corrida):
        while corrida.eje_tiempo.avanzar():
            símismo.incrementar(corrida)
            if corrida.eje_tiempo.t_guardar():
                símismo.variables.resultados.actualizar()
        return símismo.variables.resultados()

    def incrementar(símismo, corrida):
        raise NotImplementedError

    def cerrar(símismo):
        """
        Esta función debe tomar las acciones necesarias para terminar la simulación y cerrar el modelo, si aplica.
        Si no aplica, usar ``pass``.
        """
        raise NotImplementedError

    def cambiar_vals(símismo, valores):
        """
        Esta función cambia el valor de uno o más variables del modelo.

        Parameters
        ----------
        valores : dict
            Un diccionario de variables y sus valores para cambiar.
        """

        # Cambia primero el valor en el diccionario interno del Modelo
        símismo.variables.cambiar_vals(valores=valores)

    def valid_var(símismo, var):
        if var in símismo.variables:
            return símismo.variables[var]
        else:
            raise ValueError(_(
                'El variable "{v}" no existe en el modelo "{m}". Pero antes de quejarte '
                'al gerente, sería buena idea verificar si lo escrbiste bien.'  # Sí, lo "escrbí" así por propósito. :)
            ).format(v=var, m=símismo))

    @classmethod
    def obt_conf(cls, llave, auto=None, cond=None, mnsj_err=None):

        auto = auto or []
        if isinstance(auto, str):
            auto = [auto]

        try:
            op = conf_mods[cls.__name__][llave]
            if cond is None or cond(op):
                return op
        except KeyError:
            pass

        for op in auto:
            if cond is None or cond(op):
                conf_mods[cls.__name__][llave] = op
                return op

        if mnsj_err:
            avisar(mnsj_err)

    @classmethod
    def estab_conf(cls, llave, valor):
        conf_mods['envolt'][cls.__name__][llave] = valor

    @classmethod
    def instalado(cls):
        """
        Si tu modelo depiende en una instalación de otro programa externo a Tinamït, puedes reimplementar esta función
        para devolver ``True`` si el modelo está instalado y ``False`` sino.

        Returns
        -------
        bool
            Si el modelo está instalado completamente o no.
        """

        return True

    def __str__(símismo):
        return símismo.nombre

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
            símismo, bd=None, lugar_clima=None, clima=None, vars_interés=None
    ):

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
