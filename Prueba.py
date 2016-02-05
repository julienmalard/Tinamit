import ctypes
import struct

# Un ejemplo de base de como conectar e intercambiar valores con Vensim. Este se desarrolló como prueba y NO es
# necesario para el funcionamiento del programa Tinamit.


class Dll(object):
    def __init__(símismo, ubic_modelo):
        símismo.variables = None

        símismo.dll = ctypes.WinDLL('C:\\Windows\\System32\\vendll32.dll')
        resultado = símismo.dll.vensim_command(('SPECIAL>LOADMODEL|"%s"' % ubic_modelo).encode())
        print('Cargando... ', resultado)
        símismo.verificar_estatus()

    def sacar_nombres_vars(símismo):
        mem_inter = ctypes.create_string_buffer(100)
        resultado = símismo.dll.vensim_get_varnames(b"*", 0, mem_inter, 100)
        símismo.variables = [x for x in mem_inter.raw.decode().split('\x00') if x]

        print('Sacando variables... ', resultado)
        símismo.verificar_estatus()

    def estab_nombre_corrida(símismo, nombre):
        resultado = símismo.dll.vensim_command(("SIMULATE>RUNNAME|%s" % nombre).encode())
        print('Estableciendo nombre de corrida... ', resultado)
        símismo.verificar_estatus()

    def empezar_simul(símismo):
        resultado = símismo.dll.vensim_start_simulation(1, 2, 1)
        print('Empezando simulación... ', resultado)
        símismo.verificar_estatus()

    def avanzar_simul(símismo, paso):
        resultado = símismo.dll.vensim_continue_simulation(paso)
        print('Avanzando simulación... ', resultado)
        símismo.verificar_estatus()

    def empezar_juego(símismo):
        resultado = símismo.dll.vensim_command("MENU>GAME")
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
        resultado = símismo.dll.vensim_command("GAME>ENDGAME")
        print('Terminando juego... ', resultado)
        símismo.verificar_estatus()

    def sacar_val_var(símismo, var):
        mem_inter = ctypes.create_string_buffer(4)
        resultado = símismo.dll.vensim_get_val(var.encode(), mem_inter)
        print('Sacando valor var %s... ' % var, resultado)
        print(var, struct.unpack('f', mem_inter))
        símismo.verificar_estatus()

    def poner_val_var(símismo, val, var):
        símismo.dll.vensim_command(('SIMULATE>SETVAL|%s = %i' % (var, val)).encode())

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

ubicación_modelo = "C:\\Users\\jmalar1\\Documents\\PycharmProjects\\Tinamit\\Prueba dll.vpm"
modelo = Dll(ubicación_modelo)
modelo.sacar_nombres_vars()

modelo.estab_nombre_corrida('Corrida')
modelo.estab_paso_juego(1)
modelo.empezar_juego()
modelo.sacar_val_var('FINAL TIME')
modelo.sacar_val_var('Nivel')

modelo.avanzar_juego()
modelo.sacar_val_var('Nivel')

print('fin')
