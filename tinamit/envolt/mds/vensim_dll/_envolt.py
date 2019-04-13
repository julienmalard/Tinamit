import ctypes
import os
import sys
from warnings import warn as avisar

import numpy as np

from tinamit.envolt.mds import EnvolturaMDS, VarNivel, VarConstante, VariablesMDS, VarInic, VarAuxiliar
from tinamit.mod import Variable
from . import _funcs as f
from ._vars import VarAuxEditable


class EnvolturaVensimDLL(EnvolturaMDS):
    """
    Esta es la envoltura para modelos de tipo Vensim. Puede leer y controlar cualquier modelo Vensim para que
    se pueda emplear en Tinamït.
    Necesitarás la versión DSS de Vensim para que funcione.
    """

    def __init__(símismo, archivo, nombre='mds'):
        símismo.mod = f.cargar_mod_vensim(ctypes.WinDLL(_obt_dll_vensim()), archivo)
        símismo.paso = f.obt_paso_inicial(símismo.mod)
        vars_ = _gen_vars(símismo.mod)
        super().__init__(vars_, nombre)

    def unidad_tiempo(símismo):
        return f.obt_unid_tiempo(símismo.mod)

    def iniciar_modelo(símismo, corrida):

        eje_tiempo = corrida.eje_tiempo
        # En Vensim, tenemos que incializar los valores de variables no editables antes de empezar la simulación.
        símismo.variables.cambiar_vals(
            {var: val for var, val in corrida.vals_inic() if not isinstance(var, VarAuxEditable)}
        )

        f.inic_modelo(símismo.mod, paso=eje_tiempo.paso, n_pasos=eje_tiempo.n_pasos, nombre_corrida=str(corrida))

        # Aplicar los valores iniciales de variables editables
        símismo.variables.cambiar_vals(
            {var: val for var, val in corrida.vals_inic() if isinstance(var, VarAuxEditable)}
        )

        # Debe venir después de `f.inic_modelo()` sino no obtenemos datos para los variables
        símismo._leer_vals_de_vensim()

        super().iniciar_modelo(corrida)

    def incrementar(símismo, corrida):

        # Establecer el paso.
        if corrida != símismo.paso:
            f.estab_paso(símismo.mod, corrida)
            símismo.paso = corrida

        f.avanzar_modelo(símismo.mod)
        símismo._leer_vals_de_vensim(corrida.resultados.vars_interés)

    def cambiar_vals(símismo, valores):
        super().cambiar_vals(valores)

        for var, val in valores.items():
            # Para cada variable para cambiar...

            if símismo.variables[var].dims == (1,):
                # Si el variable no tiene dimensiones (subscriptos)...

                # Actualizar el valor en el modelo Vensim.
                if not np.isnan(val):
                    f.cambiar_val(símismo.mod, var, val)

            else:
                # Para hacer: opciones de dimensiones múltiples
                # La lista de subscriptos
                subs = símismo.variables[var].subs

                if isinstance(val, np.ndarray) and val.shape:
                    matr = val
                else:
                    matr = np.empty(len(subs))
                    matr[:] = val

                for n, s in enumerate(subs):
                    var_s = var + s
                    val_s = matr[n]
                    if not np.isnan(val_s):
                        f.cambiar_val(símismo.mod, var_s, val_s)

    def cerrar(símismo):
        """
        Cierre la simulación Vensim.
        """

        f.cerrar_vensim(símismo.mod)

        #
        f.vdf_a_csv(símismo.mod)

    @classmethod
    def instalado(cls):
        return _obt_dll_vensim() is not None

    def paralelizable(símismo):
        return True

    def _leer_vals_de_vensim(símismo, l_vars=None):
        if isinstance(l_vars, Variable):
            l_vars = [l_vars]
        elif l_vars is None:
            l_vars = símismo.variables

        for v in l_vars:
            if v.dims == (1,):
                # Si el variable no tiene dimensiones (subscriptos)...

                # Leer su valor.
                val = f.obt_val_var(símismo.mod, v)

                # Guardar en el diccionario interno.
                símismo.variables.cambiar_vals({v: val})

            else:
                matr_val = v.val
                for n, s in enumerate(símismo.variables[v].subs):
                    var_s = str(v) + s

                    # Leer su valor.
                    val = f.obt_val_var(símismo.mod, var_s)

                    # Guardar en el diccionario interno.
                    matr_val[n] = val  # Para hacer: opciones de dimensiones múltiples


def _obt_dll_vensim():
    if sys.platform[:3] != 'win':
        avisar(_('Desafortunadamente, el DLL de Vensim funciona únicamente en Windows.'))
        return False

    return EnvolturaVensimDLL.obt_conf(
        'dll', auto=[
            'C:/Windows/System32/vendll32.dll',
            'C:/Windows/SysWOW64/vendll32.dll'
        ], cond=os.path.isfile,
        mnsj_err=_(
            'Debes instalar Vensim DSS en tu computadora y, si todavía aparece este mensaje,'
            '\nespecificar la ubicación del dll manualmente, p. ej.'
            '\n\tEnvolturaVensimDLL.estab_conf("dll", "C:/Camino/raro/para/vendll32.dll")'
            '\npara poder hacer simulaciones con Vensim DSS.'
        )
    )

def _gen_vars(mod):
    l_vars = []

    vars_y_tipos = {v: f.obt_atrib_var(mod, v, cód_attrib=14).lower() for v in f.obt_vars(mod)}

    editables = f.obt_editables(mod)

    omitir = [
        'Data', 'Constraint', 'Lookup', 'Group', 'Subscript Range', 'Test Input', 'Time Base',
        'Subscript Constant'
    ]

    for var, tipo_var in vars_y_tipos:
        # Para cada variable...

        # No incluir los variables de verificación (pruebas de modelo) Vensim, de subscriptos, de datos, etc.
        if tipo_var in omitir:
            continue

        # Sacar los límites del variable
        líms = (f.obt_atrib_var(mod, var, cód_attrib=11), f.obt_atrib_var(mod, var, cód_attrib=12))
        líms = tuple(float(lm) if lm != '' else None for lm in líms)

        # Leer la descripción del variable.
        info = f.obt_atrib_var(mod, var, 2)

        # Sacar sus unidades
        unid = f.obt_atrib_var(mod, var, cód_attrib=1)

        # Sacar las dimensiones del variable
        subs = f.obt_atrib_var(mod, var, cód_attrib=9)
        if len(subs):
            dims = (len(subs),)  # Para hacer: permitir más de 1 dimensión
        else:
            dims = (1,)

        # Leer la ecuación del variable, sus hijos y sus parientes directamente de Vensim
        ec = f.obt_atrib_var(mod, var, 3)
        parientes = [v for v in f.obt_atrib_var(mod, var, 4) if v in vars_y_tipos]

        if tipo_var == 'constant' or (tipo_var == 'auxiliar' and not len(parientes)):
            cls = VarConstante
        elif tipo_var == 'level':
            cls = VarNivel
        elif tipo_var == 'auxiliary':
            cls = VarAuxEditable if var in editables else VarAuxiliar
        elif tipo_var == 'initial':
            cls = VarInic
        else:
            raise ValueError(tipo_var)

        l_vars.append(cls(var, unid=unid, ec=ec, subs=subs, parientes=parientes, dims=dims, líms=líms, info=info))

    return VariablesMDS(l_vars)