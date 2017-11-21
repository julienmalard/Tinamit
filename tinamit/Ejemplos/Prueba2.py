import ctypes
import random
import struct
import os

# Un ejemplo de base de como conectar e intercambiar valores con Vensim. Este se desarrolló como prueba y NO es
# necesario para el funcionamiento del programa Tinamit.


class Dll(object):
    def __init__(símismo, ubic_modelo):
        símismo.nombre_corrida = None
        símismo.variables = None

        símismo.dll = ctypes.WinDLL('C:\\Windows\\System32\\vendll32.dll')
        resultado = símismo.dll.vensim_command(('SPECIAL>LOADMODEL|"%s"' % ubic_modelo).encode())
        print('Cargando... ', resultado)
        símismo.verificar_estatus()

    def silenciar(símismo):
        símismo.dll.vensim_be_quiet(2)

    def sacar_nombres_vars(símismo):
        mem_inter = ctypes.create_string_buffer(100)
        resultado = símismo.dll.vensim_get_varnames(b"*", 0, mem_inter, 100)
        símismo.variables = [x for x in mem_inter.raw.decode().split('\x00') if x]

        print('Sacando variables... ', resultado)
        print(símismo.variables)
        símismo.verificar_estatus()

    def sacar_subscripto_var(símismo, nombre):
        """
        
        :param nombre: 
        :type nombre: str 
        :return: 
        :rtype: 
        """

        mem_inter = ctypes.create_string_buffer(10)

        tamaño = símismo.dll.vensim_get_varattrib(nombre.encode(), 9, mem_inter, 0)
        mem_inter = ctypes.create_string_buffer(tamaño)
        resultado = símismo.dll.vensim_get_varattrib(nombre.encode(), 9, mem_inter, tamaño)

        subs = [x for x in mem_inter.raw.decode().split('\x00') if x]

        print('Sacando subscriptos...', resultado)
        print(subs)
        símismo.verificar_estatus()

    def estab_nombre_corrida(símismo, nombre):
        símismo.nombre_corrida = nombre
        resultado = símismo.dll.vensim_command(("SIMULATE>RUNNAME|%s" % nombre).encode())
        print('Estableciendo nombre de corrida... ', resultado)
        símismo.verificar_estatus()

    def empezar_simul(símismo):
        resultado = símismo.dll.vensim_start_simulation(1, 0, 1)
        print('Empezando simulación... ', resultado)
        símismo.verificar_estatus()

    def avanzar_simul(símismo, paso):
        resultado = símismo.dll.vensim_continue_simulation(paso)
        print('Avanzando simulación... ', resultado)
        símismo.verificar_estatus()

    def empezar_juego(símismo):
        resultado = símismo.dll.vensim_command(b"MENU>GAME")
        print('Empezando juego... ', resultado)
        símismo.verificar_estatus()

    def estab_paso_juego(símismo, paso):
        resultado = símismo.dll.vensim_command(("GAME>GAMEINTERVAL|%i" % paso).encode())
        print('Estableciendo paso juego... ', resultado)
        símismo.verificar_estatus()

    def avanzar_juego(símismo):
        resultado = símismo.dll.vensim_command(b"GAME>GAMEON")
        print('Avanzando juego... ', resultado)
        símismo.verificar_estatus()

    def terminar_juego(símismo):
        resultado = símismo.dll.vensim_command(b"GAME>ENDGAME")
        print('Terminando juego... ', resultado)
        símismo.verificar_estatus()

    def sacar_val_var(símismo, var, imprim=True):
        mem_inter = ctypes.create_string_buffer(4)
        resultado = símismo.dll.vensim_get_val(var.encode(), mem_inter)
        if imprim:
            print('Sacando valor var %s... ' % var, resultado)
            print(var, struct.unpack('f', mem_inter))
            símismo.verificar_estatus()
        else:
            return float(struct.unpack('f', mem_inter)[0])

    def poner_val_var(símismo, val, var):
        resultado = símismo.dll.vensim_command(('SIMULATE>SETVAL|%s = %f' % (var, val)).encode())
        print('Poniendo valor %f a var %s... ' % (val, var), resultado)
        nuevo_val = símismo.sacar_val_var(var, imprim=False)
        print('Ahora var %s es igual a %f' % (var, nuevo_val))
        símismo.verificar_estatus()

    def terminar_simulación(símismo):
        resultado = símismo.dll.vensim_finish_simulation()
        print('Terminando simulación... ', resultado)
        símismo.verificar_estatus()

    def verificar_estatus(símismo):
        estatus = int(símismo.dll.vensim_check_status())
        if estatus == 0:
            print('Listo.', estatus)
        elif estatus == 1:
            print('Simulando.', estatus)
        elif estatus == 5:
            print('Jugando.', estatus)
        elif estatus == 6:
            print('Memoria no libre.', estatus)
        else:
            print('Tienes un problema.', estatus)

    def guardar_csv(símismo, archivo):
        archivo_csv = os.path.split(archivo)[1].replace('.vdf', '.csv')
        símismo.dll.vensim_command('MENU>VDF2CSV|{vdffile}|{CSVfile}'.format(vdffile=archivo, CSVfile=archivo_csv)
                                   .encode())


ubicación_modelo = "C:\\Users\\jmalar1\\PycharmProjects\\Tinamit\\tinamit\\Ejemplos\\Subscripts.vpm"
modelo = Dll(ubicación_modelo)
modelo.silenciar()
modelo.sacar_nombres_vars()

modelo.estab_nombre_corrida('Corrida')
modelo.sacar_val_var('FINAL TIME')
modelo.poner_val_var(120, 'FINAL TIME')  # Absolutamente necesario

modelo.sacar_subscripto_var('Naher')
modelo.sacar_subscripto_var('Barish')

# input()

modelo.empezar_juego()

modelo.estab_paso_juego(10)
modelo.sacar_val_var('Time')
modelo.sacar_val_var('Barish')
modelo.sacar_val_var('Zamin[N3]')
modelo.poner_val_var(8.8, 'Zamin["naher\_s"]')
input()
modelo.poner_val_var(12, 'Nadi[N2]')

modelo.sacar_val_var('Time')
modelo.sacar_val_var('Naher[N3]')

for i in range(12):
    for s in range(1, 11):
        val_ant = modelo.sacar_val_var('Nadi[N{}]'.format(s), imprim=False)
        val_ahora = val_ant + random.random() - 0.5
        modelo.poner_val_var(val_ahora, 'Nadi[N{}]'.format(s))
        modelo.sacar_val_var('Naher[N{}]'.format(s))
    modelo.avanzar_juego()
    modelo.sacar_val_var('Time')

    # input('Presione "Intro" para seguir...')

modelo.terminar_juego()

modelo.guardar_csv(os.path.join(os.path.split(ubicación_modelo)[0], 'Corrida.vdf'))

print('fin')
