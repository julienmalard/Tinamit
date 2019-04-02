from tinamit.envolt.mds import EnvolturaMDS, VarNivel, VarConstante, VariablesMDS, \
    VarInic
from tinamit.mod import Variable
from ._funcs import obt_atrib_var, obt_vars, obt_editables, gen_mod_vensim, obt_unid_tiempo, cerrar_vensim, vdf_a_csv, \
    obt_val_var
from ._vars import VarAuxiliarVensim


class EnvolturaVensimDLL(EnvolturaMDS):
    """
    Esta es la envoltura para modelos de tipo Vensim. Puede leer y controlar cualquier modelo Vensim para que
    se pueda emplear en Tinamït.
    Necesitarás la versión DSS de Vensim para que funcione.
    """

    def __init__(símismo, archivo, nombre='mds'):
        símismo.mod = gen_mod_vensim(archivo)
        super().__init__(nombre)

    def unidad_tiempo(símismo):
        return obt_unid_tiempo(símismo.mod)

    def iniciar_modelo(símismo, eje_tiempo, extern, nombre_corrida):
        # En Vensim, tenemos que incializar los valores de variables constantes antes de empezar la simulación.
        símismo.cambiar_vals({var: val for var, val in vals_inic.items() if var not in símismo.editables})

        # Establecer el nombre de la corrida.
        cmd_vensim(func=símismo.mod.vensim_command,
                   args="SIMULATE>RUNNAME|%s" % nombre_corrida,
                   mensaje_error=_('Error iniciando la corrida Vensim.'))

        # Establecer el tiempo final.
        cmd_vensim(func=símismo.mod.vensim_command,
                   args='SIMULATE>SETVAL|%s = %i' % ('FINAL TIME', n_pasos + 1),
                   mensaje_error=_('Error estableciendo el tiempo final para Vensim.'))

        # Iniciar la simulación en modo juego ("Game"). Esto permitirá la actualización de los valores de los variables
        # a través de la simulación.
        cmd_vensim(func=símismo.mod.vensim_command,
                   args="MENU>GAME",
                   mensaje_error=_('Error inicializando el juego Vensim.'))

        # Es ABSOLUTAMENTE necesario establecer el intervalo del juego aquí. Sino, no reinicializa el paso
        # correctamente entre varias corridas (aún modelos) distintas.
        cmd_vensim(func=símismo.mod.vensim_command,
                   args="GAME>GAMEINTERVAL|%i" % símismo.paso,
                   mensaje_error=_('Error estableciendo el paso de Vensim.'))

        # Aplicar los valores iniciales de variables editables
        símismo.cambiar_vals({var: val for var, val in vals_inic.items() if var in símismo.editables})

        # Reinicializar el diccionario interno también.
        símismo._leer_vals_de_vensim()

    def incrementar(símismo):

        # Establecer el paso.
        if paso != símismo.paso:
            cmd_vensim(func=símismo.mod.vensim_command,
                       args="GAME>GAMEINTERVAL|%i" % paso,
                       mensaje_error=_('Error estableciendo el paso de Vensim.'))
            símismo.paso = paso

        # Avanzar el modelo.
        cmd_vensim(func=símismo.mod.vensim_command,
                   args="GAME>GAMEON", mensaje_error=_('Error para incrementar Vensim.'))

    def cerrar(símismo):
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

            # Sacar las dimensiones del variable
            subs = obt_atrib_var(mod, var, cód_attrib=9)
            if len(subs):
                dims = (len(subs),)  # Para hacer: permitir más de 1 dimensión
            else:
                dims = (1,)

            # Leer la ecuación del variable, sus hijos y sus parientes directamente de Vensim
            ec = obt_atrib_var(mod, var, 3)
            parientes = [v for v in obt_atrib_var(mod, var, 4) if v in vars_y_tipos]

            if tipo_var == 'constant' or (tipo_var == 'auxiliar' and not len(parientes)):
                var = VarConstante(var, unid=unid, ec=ec, parientes=parientes, dims=dims, líms=líms, info=info)
            elif tipo_var == 'level':
                var = VarNivel(var, unid=unid, ec=ec, parientes=parientes, dims=dims, líms=líms, info=info)
            elif tipo_var == 'auxiliary':
                var = VarAuxiliarVensim(
                    var, editable=var in editables, ec=ec, parientes=parientes, unid=unid,
                    dims=dims, líms=líms, info=info
                )
            elif tipo_var == 'initial':
                var = VarInic(var, unid=unid, ec=ec, parientes=parientes, dims=dims, líms=líms, info=info)
            else:
                raise ValueError(tipo_var)

            l_vars.append(var)

        return VariablesMDS(l_vars)

    def _leer_vals_de_vensim(símismo, l_vars=None):
        if isinstance(l_vars, Variable):
            l_vars = [l_vars]

        # para hacer
        for v in l_vars:
            if v.dims == (1,):
                # Si el variable no tiene dimensiones (subscriptos)...

                # Leer su valor.
                val = obt_val_var(símismo.mod, v)

                # Guardar en el diccionario interno.
                símismo._act_vals_dic_var({v: val})

            else:
                matr_val = v.val
                for n, s in enumerate(símismo.variables[v]['subscriptos']):
                    var_s = str(v) + s

                    # Leer su valor.
                    val = obt_val_var(símismo.mod, var_s)

                    # Guardar en el diccionario interno.
                    matr_val[n] = val  # Para hacer: opciones de dimensiones múltiples
