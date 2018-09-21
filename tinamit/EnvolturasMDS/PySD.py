import os
import xml.etree.ElementTree as ET
from ast import literal_eval

import numpy as np
import regex
import xarray as xr

import pysd
from tinamit.Análisis.sintaxis import Ecuación
from tinamit.EnvolturasMDS.Vensim import gen_archivo_mdl
from tinamit.MDS import EnvolturaMDS
from tinamit.config import _


class ModeloPySD(EnvolturaMDS):
    combin_pasos = True

    def __init__(símismo, archivo, nombre='mds'):

        símismo.tipo_mod = None
        símismo._conv_nombres = {}
        símismo.tiempo_final = None
        símismo.cont_simul = False
        símismo.paso_act = 0
        símismo.vars_para_cambiar = {}
        símismo._res_recién = None  # pd.DataFrame

        super().__init__(archivo, nombre=nombre)

    def _generar_mod(símismo, archivo, **ops_mód):
        nmbr, ext = os.path.splitext(archivo)

        if ext == '.py':  # Modelos PySD ya traducidos
            símismo.tipo_mod = '.py'
            return pysd.load(archivo)

        else:
            if ext == '.mdl':
                símismo.tipo_mod = '.mdl'
            elif ext in ['.xmile', '.xml']:
                símismo.tipo_mod = '.xmile'
            else:
                raise ValueError(
                    _('PySD no sabe leer modelos del formato "{}". Debes darle un modelo ".py", ".mdl" o ".xmile".')
                        .format(ext)
                )

            # Únicamente recrear el archivo .py si necesario
            if os.path.isfile(nmbr + '.py') and (os.path.getmtime(nmbr + '.py') > os.path.getmtime(archivo)):
                return pysd.load(nmbr + '.py')
            else:
                return pysd.read_vensim(archivo) if ext == '.mdl' else pysd.read_xmile(archivo)

    def _inic_dic_vars(símismo):
        símismo.variables.clear()
        símismo._conv_nombres.clear()

        internos = ['FINAL TIME', 'TIME STEP', 'SAVEPER', 'INITIAL TIME']
        for i, f in símismo.mod.doc().iterrows():

            if f['Type'] == 'lookup':
                continue

            nombre = f['Real Name']
            if nombre not in internos:
                nombre_py = f['Py Name']
                unidades = f['Unit']
                líms = literal_eval(f['Lims'])
                ec = f['Eqn']
                obj_ec = Ecuación(ec)
                var_juego = obj_ec.sacar_args_func('GAME') is not None

                if símismo.tipo_mod == '.mdl':
                    if regex.match(r'INTEG *\(', ec):
                        tipo = 'nivel'
                    else:
                        tipo = 'auxiliar'  # cambiaremos el resto después
                else:
                    try:
                        getattr(símismo.mod.components, 'integ_' + nombre_py)
                        tipo = 'nivel'
                    except AttributeError:
                        tipo = 'auxiliar'

                parientes = obj_ec.variables()

                if tipo == 'auxiliar' and not len(parientes):
                    tipo = 'constante'

                símismo.variables[nombre] = {
                    'val': getattr(símismo.mod.components, nombre_py)(),
                    'unidades': unidades,
                    'ec': ec,
                    'hijos': [],
                    'parientes': parientes,
                    'líms': líms,
                    'info': f['Comment'],
                    'tipo': tipo,
                    'ingreso': True,
                    'egreso': not var_juego
                }

                símismo._conv_nombres[nombre] = nombre_py

        # Aplicar los otros tipos de variables
        for niv in símismo.niveles():
            ec = Ecuación(símismo.obt_ec_var(niv), dialecto='vensim')
            if símismo.tipo_mod == '.mdl':
                args_integ, args_inic = ec.sacar_args_func('INTEG')  # Analizar la función INTEG de VENSIM

                # Identificar variables iniciales
                if args_inic in símismo.variables:
                    símismo.variables[args_inic]['tipo'] = 'inicial'

                # Los flujos, por definición, son los otros parientes de los niveles.
                flujos = [v for v in Ecuación(args_integ, dialecto='vensim').variables() if
                          v not in internos]
            else:
                flujos = ec.variables()

            for flujo in flujos:
                # Para cada nivel en el modelo...
                símismo.variables[flujo]['tipo'] = 'flujo'

        # Detectar los variables iniciales de XMILE
        if símismo.tipo_mod == '.xmile':
            for nv in ET.parse(símismo.archivo).getroot().iter('{http://www.systemdynamics.org/XMILE}stock'):
                inic = nv.find('{http://www.systemdynamics.org/XMILE}eqn').text

                if inic in símismo.variables:
                    símismo.variables[inic]['tipo'] = 'inicial'
                    símismo.variables[nv.attrib['name']]['parientes'].add(inic)

        # Aplicar parientes a hijos
        for v, d_v in símismo.variables.items():
            for p in d_v['parientes']:
                d_p = símismo.variables[p]
                d_p['hijos'].append(v)

    def unidad_tiempo(símismo):
        docs = símismo.mod.doc()

        if símismo.tipo_mod == '.mdl':
            unid_tiempo = docs.loc[docs['Real Name'] == 'TIME STEP', 'Unit'].values[0]

        else:
            with open(símismo.mod.py_model_file, 'r', encoding='UTF-8') as d:
                f = d.readline()
                while f != 'def time_step():\n':
                    f = d.readline()
                while not f.strip().startswith('Units:'):
                    f = d.readline()
                unid_tiempo = f.split(':')[1].strip()

        return unid_tiempo

    def iniciar_modelo(símismo, tiempo_final, nombre_corrida, vals_inic):

        # Poner los variables y el tiempo a sus valores iniciales
        símismo.mod.reload()
        símismo.mod.initialize()

        símismo.cont_simul = False
        símismo.tiempo_final = tiempo_final
        símismo.paso_act = símismo.mod.time._t
        símismo.vars_para_cambiar.clear()
        símismo.vars_para_cambiar.update(vals_inic)

        super().iniciar_modelo(tiempo_final, nombre_corrida, vals_inic)

    def _reinic_vals(símismo):
        """
        Empleamos :meth:`_act_vals_dic_var` y no :meth:`cambiar_vals` porque no hay necesidad de cambiar los valores
        en el modelo externo, visto que de allí estamos tomando los nuevos valores.
        """

        símismo._act_vals_dic_var({
            var: getattr(símismo.mod.components, símismo._conv_nombres[var])() for var in símismo.variables
        })

    def _cambiar_vals_modelo_externo(símismo, valores):
        símismo.vars_para_cambiar.clear()
        símismo.vars_para_cambiar.update(
            {var: val for var, val in valores.items() if not np.isnan(val)}
        )

    def _incrementar(símismo, paso, guardar_cada=None):
        guardar_cada = guardar_cada or paso
        pasos_devolv = list(range(símismo.paso_act, símismo.paso_act + 1 + paso, guardar_cada))
        símismo.paso_act += paso

        if símismo.cont_simul:
            símismo._res_recién = símismo.mod.run(
                initial_condition='current', params=símismo.vars_para_cambiar,
                return_timestamps=pasos_devolv, return_columns=símismo.vars_saliendo
            )
        else:
            símismo._res_recién = símismo.mod.run(
                return_timestamps=pasos_devolv, params=símismo.vars_para_cambiar,
                return_columns=símismo.vars_saliendo
            )
            símismo.cont_simul = True

        símismo.vars_para_cambiar.clear()

    def _leer_vals(símismo):
        valores = {}
        for v in símismo.vars_saliendo:
            valores[v] = símismo._res_recién[v].values[-1]

        símismo._act_vals_dic_var(valores)

    def leer_arch_resultados(símismo, archivo, var=None, col_tiempo='tiempo'):

        if archivo != símismo.corrida_activa:
            raise ValueError(_('PySD solamente puede leer los resultados de la última corrida.'))
        if var is None:
            l_vars = list(símismo._res_recién)
        elif isinstance(var, str):
            l_vars = [var]
        else:
            l_vars = var
        return xr.Dataset({v: ('n', símismo._res_recién[v].values) for v in l_vars})

    def cerrar_modelo(símismo):
        pass

    def _generar_archivo_mod(símismo):
        if símismo.tipo_mod == '.mdl':
            return gen_archivo_mdl(archivo_plantilla=símismo.archivo, d_vars=símismo.variables)
        else:
            raise NotImplementedError(símismo.tipo_mod)

    def paralelizable(símismo):
        return True

    def editable(símismo):
        return símismo.tipo_mod != '.py' and símismo.tipo_mod != '.xmile'  # para hacer: agregar xmile
