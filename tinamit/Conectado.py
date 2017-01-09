import threading
from warnings import warn as avisar

from tinamit.BF import EnvolturaBF
from .Modelo import Modelo
from .MDS import generar_mds
from .Unidades.Unidades import convertir


class SuperConectado(Modelo):
    """
    Esta clase representa el más alto nivel posible de modelo conectado. Tiene la función muy útil de poder conectar
    instancias de sí misma, así permitiendo la conexión de números arbitrarios de modelos.
    """

    def __init__(símismo, nombre="SuperConectado"):
        """
        El nombre automático para este modelo es "SuperConectado". Si vas a conectar más que un modelo SuperConectado,
        asegúrate de darle un nombre distinto al menos a un de ellos.

        :param nombre: El nombre del modelo SuperConectado.
        :type nombre: str

        """

        # Un diccionario de los modelos que se van a conectar en este modelo. Tiene la forma general
        # {'nombre_modelo': objecto_modelo,
        #  'nombre_modelo_2': objecto_modelo_2}
        símismo.modelos = {}

        # Una lista de las conexiones entre los modelos.
        símismo.conexiones = []

        # Un diccionario para aceder rápidamente a las conexiones.
        símismo.conex_rápida = {}

        # Un diccionario con la información de conversiones de unidades de tiempo entre los dos modelos conectados.
        # Tiene la forma general:
        # {'nombre_modelo_1': factor_conv,
        # {'nombre_modelo_2': factor_conv}
        # Al menos uno de los dos factores siempre será = a 1.
        símismo.conv_tiempo = {}

        # Inicializamos el SuperConectado como todos los Modelos.
        super().__init__(nombre=nombre)

    def estab_modelo(símismo, modelo):
        """
        Esta función agrega un modelo al SuperConectado. Una vez que dos modelos estén agregados, se pueden conectar
        y simular juntos.

        :param modelo: El modelo para agregar.
        :type modelo: Modelo

        """

        # Si ya hay dos modelos conectados, no podemos conectar un modelo más.
        if len(símismo.modelos) >= 2:
            raise ValueError('Ya hay dos modelo conectados. Desconecta uno primero o emplea una instancia de'
                             'SuperConectado para conectar más que 2 modelos.')

        # Si ya se conectó otro modelo con el mismo nombre, avisarlo al usuario.
        if modelo.nombre in símismo.modelos:
            avisar('El modelo {} ya existe. El nuevo modelo reemplazará el modelo anterior.'.format(modelo.nombre))

        # Agregar el nuevo modelo al diccionario de modelos.
        símismo.modelos[modelo.nombre] = modelo

        # Ahora, tenemos que agregar los variables del modelo agregado al diccionaro de variables de este modelo
        # también. Se prefija el nombre del modelo al nombre de su variable para evitar posibilidades de nombres
        # desduplicados.
        for var in modelo.variables:
            nombre_var = '{mod}_{var}'.format(var=var, mod=modelo.nombre)
            símismo.variables[nombre_var] = modelo.variables[var]

        # Establecemos las unidades de tiempo del modelo SuperConectado según las unidades de tiempo de sus submodelos.
        símismo.unidad_tiempo = símismo.obt_unidad_tiempo()

    def inic_vars(símismo):
        """
        Esta función no es necesaria, por lo de estab_modelo.
        """
        pass

    def obt_unidad_tiempo(símismo):
        """
        Esta función devolverá las unidades de tiempo del modelo conectado. Dependerá de los submodelos.
        Si los dos submodelos tienen las mismas unidades, esta será la unidad del modelo conectado también.
        Si los dos tienen unidades distintas, intentaremos encontrar la conversión entre los dos y después se
        considerará como unidad de tiempo de base la más grande de los dos. Por ejemplo, si se conecta un modelo
        con una unidad de tiempo de meses con un modelo de unidad de año, se aplicará una unidad de tiempo de años
        al modelo conectado.

        Después se actualiza el variable ``símismo.conv_tiempo`` para guardar en memoria la conversión necesaria entre
        los pasos de los dos submodelos.

        Se emplea el módulo :module:`Unidades.Unidades` para convertir unidades.

        :return: El tiempo de paso del modelo SuperConectado.
        :rtype: str

        """

        # Si todavía no se han conectado 2 modelos, no hay nada que hacer.
        if len(símismo.modelos) < 2:
            return None

        # Identificar las unidades de los dos submodelos.
        l_mods = list(símismo.modelos)

        unid_mod_1 = símismo.modelos[l_mods[0]].unidad_tiempo
        unid_mod_2 = símismo.modelos[l_mods[1]].unidad_tiempo

        # Una función auxiliar aquí para verificar si el factor de conversión es un nombre entero o no.
        def verificar_entero(factor):

            if int(factor) != factor:
                # Si el factor no es un número entero, avisar antes de redondearlo.
                avisar('Las unidades de tiempo de los dos modelos ({} y {}) no tienen denominator común.'
                       'Se aproximará la conversión.'.format(unid_mod_1, unid_mod_2))

            # Devolver la mejor aproximación entera
            return round(factor)

        if unid_mod_1 == unid_mod_2:
            # Si las unidades son idénticas, ya tenemos nuestra respuesta.
            símismo.conv_tiempo[l_mods[0]] = 1
            símismo.conv_tiempo[l_mods[1]] = 1

            return unid_mod_1

        else:
            # Sino, intentemos convertir automáticamente
            try:
                factor_conv = convertir(de=unid_mod_1, a=unid_mod_2)

            except ValueError:
                # Si no lo logramos, hay un error.
                avisar('No se pudo inferir la conversión de unidades de tiempo entre {} y {}.'
                       'Especificarla con la función .estab_conv_tiempo().'.format(unid_mod_1, unid_mod_2))
                return None

            if factor_conv > 1:
                # Si la unidad de tiempo del primer modelo es más grande que la del otro...

                # Verificar que sea un factor entero
                factor_conv = verificar_entero(factor_conv)

                # ...y usar esta como unidad de tiempo y guardar el factor de conversión.
                símismo.conv_tiempo[l_mods[0]] = 1
                símismo.conv_tiempo[l_mods[1]] = factor_conv

                return unid_mod_1

            else:
                # Si la unidad de tiempo del segundo modelo es la más grande...

                # Tomar el recíproco de la conversión
                factor_conv = 1 / factor_conv

                # Verificar que sea un factor entero
                factor_conv = verificar_entero(factor_conv)

                # ...y usar las unidades del segundo modelo como referencia.
                símismo.conv_tiempo[l_mods[1]] = 1
                símismo.conv_tiempo[l_mods[0]] = factor_conv

                return unid_mod_2

    def estab_conv_tiempo(símismo, mod_base, conv):
        """
        Esta función establece la conversión de tiempo entre los dos modelos (útil para unidades que Tinamit
        no reconoce).

        :param mod_base: El modelo con la unidad de tiempo mayor.
        :type mod_base: str

        :param conv: El factor de conversión con la unidad de tiempo del otro modelo.
        :type conv: int

        """

        # Veryficar que el modelo de base es un nombre de modelo válido.
        if mod_base not in símismo.modelos:
            raise ValueError('El modelo "{}" no existe en este modelo conectado.'.format(mod_base))

        # Identificar el modelo que no sirve de referencia para la unidad de tiempo
        l_mod = list(símismo.modelos)
        mod_otro = l_mod[(l_mod.index(mod_base)+1) % 2]

        # Establecer las conversiones
        símismo.conv_tiempo[mod_base] = 1
        símismo.conv_tiempo[mod_otro] = conv

        # Y guardar la unidad de tiempo.
        símismo.unidad_tiempo = símismo.modelos[mod_base].unidad_tiempo

    def cambiar_vals_modelo(símismo, valores):
        """
        Esta función cambia los valores del modelo. A través de la función :func:`Conectado.cambiar_vals`, es recursivo.
        :param valores:
        :type valores: dict

        """

        # Para cada nombre de variable...
        for nombre_var, val in valores.items():

            # Primero, vamos a sacar el nombre del variable y el nombre del submodelo.
            nombre_mod, var = nombre_var.split('_', 1)

            # Ahora, pedimos a los submodelos de hacer los cambios en los modelos externos, si hay.
            símismo.modelos[nombre_mod].cambiar_vals(valores={var: val})

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

        símismo.iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida=nombre_corrida)

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

    def conectar_vars(símismo, dic_vars, modelo_fuente, conv=None):
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
        unid_fuente = símismo.modelos[modelo_fuente]['vars'][var_fuente]['unidades']
        unid_recip = símismo.modelos[modelo_recip]['vars'][var_recip]['unidades']

        if conv is None:
            try:
                conv = convertir(de=unid_fuente,
                                 a=unid_recip)
            except ValueError:
                avisar('No se pudo identificar una conversión automática para las unidades de los variables'
                       '"{}" (unidades: {}) y "{}" (unidades: {}). Se está suponiendo un factor de conversión de 1.'
                       .format(var_fuente, unid_fuente, var_recip, unid_recip))
                conv = 1

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
