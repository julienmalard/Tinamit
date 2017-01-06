import threading
from warnings import warn as avisar

from tinamit.BF import EnvolturaBF
from .Modelo import Modelo
from .MDS import generar_mds
from .Unidades.Unidades import convertir


class SuperConectado(Modelo):
    """

    """

    def __init__(símismo, nombre="SuperConectado"):
        """

        :param nombre:
        :type nombre: str

        """

        símismo.modelos = {}

        símismo.conexiones = []
        símismo.conex_rápida = {}

        símismo.conv_tiempo = {}

        super().__init__(nombre=nombre)

    def estab_modelo(símismo, modelo):
        """

        :param modelo:
        :type modelo: Modelo

        """

        if len(símismo.modelos) >= 2:
            raise ValueError('Ya hay dos modelo conectados. Desconecta uno primero o emplea una instancia de'
                             'SuperConectado para conectar más que 2 modelos.')

        if modelo.nombre in símismo.modelos:
            avisar('El modelo {} ya existe. El nuevo modelo reemplazará el modelo anterior.'.format(modelo.nombre))

        símismo.modelos[modelo.nombre] = modelo

        for var in modelo.variables:
            nombre_var = '{mod}_{var}'.format(var=var, mod=modelo.nombre)
            símismo.variables[nombre_var] = modelo.variables[var]

        símismo.obt_unidad_tiempo()

    def inic_vars(símismo):
        """

        """

        for nombre_mod, mod in símismo.modelos.items():
            símismo.variables[nombre_mod] = mod.inic_vars()

    def obt_unidad_tiempo(símismo):
        """

        :return:
        :rtype: str

        """

        if len(símismo.modelos) < 2:
            return None

        l_mods = list(símismo.modelos)

        unid_mod_1 = símismo.modelos[l_mods[0]].unidad_tiempo
        unid_mod_2 = símismo.modelos[l_mods[1]].unidad_tiempo

        if unid_mod_1 == unid_mod_2:

            símismo.conv_tiempo[l_mods[0]] = 1
            símismo.conv_tiempo[l_mods[1]] = 1

            return unid_mod_1

        else:
            try:
                factor_conv = convertir(de=unid_mod_1, a=unid_mod_2)
            except ValueError:
                avisar('No se pudo inferir la conversión de unidades de tiempo entre {} y {}.'
                       'Especificarla con la función .estab_conv_tiempo().'.format(unid_mod_1, unid_mod_2))
                return

            if factor_conv > 1:
                símismo.conv_tiempo[l_mods[0]] = 1
                símismo.conv_tiempo[l_mods[1]] = factor_conv
                return unid_mod_1

            else:
                factor_conv = 1 / factor_conv
                if int(factor_conv) != factor_conv:
                    factor_conv = int(factor_conv)

                    avisar('Las unidades de tiempo de los dos modelos ({} y {}) no tienen denominator común.'
                           'Se aproximará la conversión.'.format(unid_mod_1, unid_mod_2))

                símismo.conv_tiempo[l_mods[1]] = 1
                símismo.conv_tiempo[l_mods[0]] = factor_conv
                return unid_mod_2

    def estab_conv_tiempo(símismo, mod_base, conv):
        """

        :param mod_base:
        :type mod_base: str
        :param conv:
        :type conv: int

        """

        if mod_base not in símismo.modelos:
            raise ValueError('El modelo "{}" no esiste en este modelo conectado.'.format(mod_base))

        l_mod = list(símismo.modelos)
        mod_otro = l_mod[(l_mod.index(mod_base)+1) % 2]

        símismo.conv_tiempo[mod_base] = 1
        símismo.conv_tiempo[mod_otro] = conv

    def cambiar_vals_modelo(símismo, valores):
        """

        :param valores:
        :type valores: dict

        """

        for nombre_mod, vals in valores.items():
            símismo.modelos[nombre_mod].cambiar_vals(valores=vals)

    def simular(símismo, tiempo_final, paso=1, nombre_corrida='Corrida Tinamit'):
        """

        :param tiempo_final:
        :type tiempo_final: int
        :param paso:
        :type paso: int
        :param nombre_corrida:
        :type nombre_corrida: str

        """

        if len(símismo.modelos) < 2:
            raise ValueError('Hay que conectar dos modelos antes de empezar una simulación.')

        if not len(símismo.conv_tiempo):
            raise AttributeError('Hay que especificar la conversión de unidades de tiempo con '
                                 '.estab_conv_tiempo() antes de correr la simulación.')

        símismo.iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida='Corrida Tinamit')

        for i in range(tiempo_final):
            símismo.incrementar(paso)

        for mod in símismo.modelos.values():
            mod.cerrar_modelo()

    def incrementar(símismo, paso):
        """

        :param paso:
        :type paso: int

        """

        # Un hilo para cada modelo
        l_hilo = [threading.Thread(name='hilo_%s' % nombre,
                                   target=mod.incrementar, args=(símismo.conv_tiempo[nombre] * paso,))
                  for nombre, mod in símismo.modelos.items()]

        # Empezar los dos hilos al mismo tiempo
        for hilo in l_hilo:
            hilo.start()

        # Esperar que los dos hilos hayan terminado
        for hilo in l_hilo:
            hilo.join()

        # Intercambiar variables
        l_mods = [m for m in símismo.modelos.items()]

        vars_egr = [dict([(símismo.conex_rápida[nombre][v]['var'],
                           m.variables[v]['val'] * símismo.conex_rápida[nombre][v]['conv'])
                          for v in m.vars_saliendo]) for nombre, m in l_mods]

        for n, tup in enumerate(l_mods):
            tup[1].cambiar_vals(valores=vars_egr[(n + 1) % 2])

    def leer_vals(símismo):
        """

        """
        for mod in símismo.modelos.values():
            mod.leer_vals()

    def iniciar_modelo(símismo, **kwargs):
        """

        """

        símismo.conex_rápida.clear()
        for conex in símismo.conexiones:

            l_mod = list(símismo.modelos)
            mod_fuente = conex['modelo_fuente']
            mod_recip = l_mod[(l_mod.index(mod_fuente) + 1) % 2]

            var_fuente = conex['vars'][mod_fuente]
            var_recip = conex['vars'][mod_recip]

            if mod_fuente not in símismo.conex_rápida:
                símismo.conex_rápida[mod_fuente] = {}

            símismo.conex_rápida[mod_fuente][var_fuente] = {'var': var_recip, 'conv': conex['conv']}

        for mod in símismo.modelos.values():
            mod.iniciar_modelo(**kwargs)

    def cerrar_modelo(símismo):
        """

        """

        for mod in símismo.modelos:
            mod.cerrar_modelo()

    def conectar_vars(símismo, dic_vars, modelo_fuente, conv=1):
        """

        :param dic_vars:
        :type dic_vars: dict
        :param modelo_fuente:
        :type modelo_fuente: str
        :param conv:
        :type conv: float

        """

        l_modelos = list(símismo.modelos)

        for nombre_mod in dic_vars:
            if nombre_mod not in símismo.modelos:
                raise ValueError('Nombre de modelo "{}" erróneo.'.format(nombre_mod))

            mod = símismo.modelos[nombre_mod]
            var = dic_vars[nombre_mod]
            if var in mod.vars_saliendo or var in mod.vars_entrando:
                raise ValueError('El variable "{}" del modelo "{}" ya está conectado. '
                                 'Desconéctalo primero con .desconectar_vars().'.format(var, nombre_mod))

        try:
            índ_mod_fuente = l_modelos.index(modelo_fuente)
            modelo_recip = l_modelos[(índ_mod_fuente + 1) % 2]
        except ValueError:
            raise ValueError('Nombre de modelo "{}" erróneo.'.format(modelo_fuente))

        var_fuente = dic_vars[modelo_fuente]
        var_recip = dic_vars[modelo_recip]

        dic_conex = {'modelo_fuente': modelo_fuente,
                     'vars': {modelo_recip: var_recip,
                              modelo_fuente: var_fuente
                              },
                     'conv': conv
                     }

        símismo.conexiones.append(dic_conex)

        # Para hacer: el siguiente debe ser recursivo.
        símismo.modelos[modelo_fuente].vars_saliendo.append(var_fuente)
        símismo.modelos[modelo_recip].vars_entrando.append(var_recip)

    def desconectar_vars(símismo, var, modelo_fuente):
        """

        :param var:
        :type var:
        :param modelo_fuente:
        :type modelo_fuente:

        """

        l_mod = list(símismo.modelos)

        for n, conex in enumerate(símismo.conexiones):
            if conex['modelo_fuente'] == modelo_fuente and conex['vars'][modelo_fuente] == var:

                mod_recip = l_mod[(l_mod.index(modelo_fuente) + 1) % 2]
                var_recipiente = conex['vars'][mod_recip]

                símismo.conexiones.pop(n)

                símismo.modelos[modelo_fuente].vars_saliendo.remove(var)
                símismo.modelos[mod_recip].vars_entrando.remove(var_recipiente)


class Conectado(SuperConectado):
    """

    """

    def __init__(símismo):

        símismo.mds = None
        símismo.bf = None

        super().__init__()

    def estab_mds(símismo, archivo_mds):
        """

        :param archivo_mds:
        :type archivo_mds: str

        """

        modelo_mds = generar_mds(archivo=archivo_mds)

        símismo.estab_modelo(modelo=modelo_mds)

        símismo.mds = modelo_mds

    def estab_bf(símismo, archivo_bf):
        """

        :param archivo_bf:
        :type archivo_bf: str

        """

        modelo_bf = EnvolturaBF(archivo=archivo_bf)

        símismo.estab_modelo(modelo=modelo_bf)

        símismo.bf = modelo_bf

    def conectar(símismo, var_mds, var_bf, mds_fuente, conv=1):
        """

        :param var_mds:
        :type var_mds: str
        :param var_bf:
        :type var_bf: str
        :param mds_fuente:
        :type mds_fuente: bool
        :param conv:
        :type conv: float

        """

        dic_vars = {'mds': var_mds, 'bf': var_bf}

        if mds_fuente:
            fuente = 'mds'
        else:
            fuente = 'bf'

        símismo.conectar_vars(dic_vars=dic_vars, modelo_fuente=fuente, conv=conv)

    def desconectar(símismo, var_mds):
        """

        :param var_mds:
        :type var_mds:

        """

        símismo.desconectar_vars(var=var_mds, modelo_fuente='mds')
