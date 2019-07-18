import ctypes
import os
import sys

import numpy as np

from tinamit.config import _
from tinamit.mod import Variable
from . import _funcs as f
from ._vars import VarAuxEditable, VariablesModVensimDLL
from .._envolt import ModeloDS
from .._vars import VarNivel, VarConstante, VarInic, VarAuxiliar


class ModeloVensimDLL(ModeloDS):
    """
    Esta es la envoltura para modelos de tipo Vensim. Puede leer y controlar cualquier modelo Vensim para que
    se pueda emplear en Tinamït.
    Necesitarás la versión DSS de Vensim para que funcione.
    """
    ext = ['.vpm']

    def __init__(símismo, archivo, nombre='mds'):
        símismo.inicializado = False
        símismo.mod = f.cargar_mod_vensim(_obt_dll_vensim(), archivo)
        símismo.paso = f.obt_paso_inicial(símismo.mod)
        super().__init__(_gen_vars(símismo.mod), nombre)

    def unidad_tiempo(símismo):
        return f.obt_unid_tiempo(símismo.mod)

    def iniciar_modelo(símismo, corrida):
        símismo.corrida = corrida
        corrida.variables.reinic()

        t = corrida.t
        # En Vensim, tenemos que incializar los valores de variables no editables antes de empezar la simulación.
        no_editables = [str(v) for v in símismo.variables.no_editables()]
        if corrida.extern:
            símismo.cambiar_vals(
                {vr: vl.values for vr, vl in corrida.obt_extern_act().items() if vr in no_editables}
            )
        if corrida.clima:
            símismo.cambiar_vals(
                {vr: vl.values for vr, vl in corrida.clima.obt_todos_vals(t, símismo.vars_clima).items()}
            )

        f.inic_modelo(símismo.mod, paso=t.tmñ_paso, n_pasos=t.n_pasos, nombre_corrida=str(corrida))

        # Aplicar los valores iniciales de variables editables
        if corrida.extern:
            símismo.cambiar_vals(
                {var: val for var, val in
                 corrida.obt_extern_act(var=[str(v) for v in símismo.variables.editables()]).items()}
            )

        # Debe venir después de `f.inic_modelo()` sino no obtenemos datos para los variables
        símismo._leer_vals_de_vensim()

        símismo.inicializado = True

        corrida.actualizar_res()
        # NO llamamos a super() porque ya hicimos todo aquí. Se tenía que reimplementar para poder separar
        # la actualización de variables dinámicos y constantes en Vensim DLL.

    def incrementar(símismo, rebanada):
        corrida = símismo.corrida
        # Establecer el paso.
        paso = corrida.t.tmñ_paso
        if paso != símismo.paso:
            f.estab_paso(símismo.mod, paso)
            símismo.paso = paso

        f.avanzar_modelo(símismo.mod)
        símismo._leer_vals_de_vensim(rebanada.resultados.variables())

        super().incrementar(rebanada)

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
        f.vdf_a_csv(símismo.mod, símismo.corrida.nombre)

    @classmethod
    def instalado(cls):
        return _obt_arch_dll_vensim() is not None

    def paralelizable(símismo):
        return True

    def _leer_vals_de_vensim(símismo, l_vars=None):
        if isinstance(l_vars, Variable):
            l_vars = [l_vars]
        elif l_vars is None:
            l_vars = símismo.variables

        for v in l_vars:
            val = f.obt_val_var(símismo.mod, str(v), v.subs)

            # Guardar en el diccionario interno.
            símismo.variables.cambiar_vals({v: val})


def _obt_dll_vensim():
    if sys.platform[:3] != 'win':
        raise OSError(
            _('\nDesafortunadamente, el DLL de Vensim funciona únicamente en Windows.'
              '\nPuedes intentar la envoltura ModeloPySDMDL con un modelo .mdl en vez.')
        )
    return ctypes.WinDLL(_obt_arch_dll_vensim())


def _obt_arch_dll_vensim():
    return ModeloVensimDLL.obt_conf(
        'dll', auto=[
            'C:/Windows/System32/vendll32.dll',
            'C:/Windows/SysWOW64/vendll32.dll'
        ], cond=os.path.isfile,
        mnsj_err=_(
            '\nDebes instalar Vensim DSS en tu computadora y, si todavía aparece este mensaje,'
            '\nespecificar la ubicación del dll manualmente, p. ej.'
            '\n\tModeloVensimDLL.estab_conf("dll", "C:/Camino/raro/para/vendll32.dll")'
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

    for var, tipo_var in vars_y_tipos.items():
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
            subs = None
        inic = np.zeros(dims)

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

        l_vars.append(cls(var, unid=unid, ec=ec, subs=subs, parientes=parientes, inic=inic, líms=líms, info=info))

    return VariablesModVensimDLL(l_vars)
