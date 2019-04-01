from tinamit.envolt.mds import EnvolturaMDS, VarNivel, VarConstante, VariablesMDS, \
    VarInic
from ._funcs import obt_atrib_var, obt_vars, obt_editables, gen_mod_vensim, obt_unid_tiempo, cerrar_vensim, vdf_a_csv
from ._vars import VarAuxiliarVensim


class EnvolturaVensimDLL(EnvolturaMDS):

    def __init__(símismo, archivo, nombre='mds'):
        símismo.mod = gen_mod_vensim(archivo)
        super().__init__(nombre)

    def unidad_tiempo(símismo):
        return obt_unid_tiempo(símismo.mod)

    def cerrar_modelo(símismo):
        """
        Cierre la simulación Vensim.
        """

        cerrar_vensim(símismo.mod, paso)

        #
        vdf_a_csv(símismo.mod)

    def _gen_vars(símismo):
        mod = símismo.mod

        l_vars = []

        vars_y_tipos = {v: obt_atrib_var(mod, v, cód_attrib=14).lower() for v in obt_vars(mod)}

        editables = obt_editables(mod)

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
            líms = (obt_atrib_var(mod, var, cód_attrib=11), obt_atrib_var(mod, var, cód_attrib=12))
            líms = tuple(float(lm) if lm != '' else None for lm in líms)

            # Leer la descripción del variable.
            info = obt_atrib_var(mod, var, 2)

            # Sacar sus unidades
            unid = obt_atrib_var(mod, var, cód_attrib=1)

            # Leer la ecuación del variable, sus hijos y sus parientes directamente de Vensim
            ec = obt_atrib_var(mod, var, 3)
            parientes = [v for v in obt_atrib_var(mod, var, 4) if v in vars_y_tipos]

            if tipo_var == 'constant' or (tipo_var == 'auxiliar' and not len(parientes)):
                var = VarConstante(var, unid=unid, ec=ec, parientes=parientes, líms=líms, info=info)
            elif tipo_var == 'level':
                var = VarNivel(var, unid=unid, ec=ec, parientes=parientes, líms=líms, info=info)
            elif tipo_var == 'auxiliary':
                var = VarAuxiliarVensim(
                    var, editable=var in editables, ec=ec, parientes=parientes, unid=unid,
                    líms=líms, info=info
                )
            elif tipo_var == 'initial':
                var = VarInic(var, unid=unid, ec=ec, parientes=parientes, líms=líms, info=info)
            else:
                raise ValueError(tipo_var)

            # Sacar las dimensiones del variable
            subs = obt_atrib_var(mod, var, cód_attrib=9)

            if len(subs):
                dims = (len(subs),)  # Para hacer: permitir más de 1 dimensión
                nombres_subs = subs
            else:
                dims = (1,)
                nombres_subs = None

            # Actualizar el diccionario de variables.
            # Para cada variable, creamos un diccionario especial, con su valor y unidades. Puede ser un variable
            # de ingreso si es de tipo_mod editable ("Gaming"), y puede ser un variable de egreso si no es un valor
            # constante.
            dic_var = {'val': None if dims == (1,) else np.zeros(dims),  # Se llenarán los valores ahorita
                       'subscriptos': nombres_subs,
                       }

        return VariablesMDS(l_vars)
