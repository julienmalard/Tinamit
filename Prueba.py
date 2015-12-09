import ctypes
import struct

# Un ejemplo de base de como conectar e intercambiar valores con Vensim. Este se desarrolló como prueba y NO es
# necesario para el funcionamiento del programa Tinamit.


def verificar_vensim():
    estatus = int(dll.vensim_check_status())
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

dll = ctypes.cdll.LoadLibrary('C:\\Windows\\System32\\vendll32.dll')
dll.vensim_check_status()
ubicación_modelo = "F:\\Julien\\PhD\\Iximulew\\MDS 2015\\Tz'olöj Ya'\\Taller 12\\Prueba dll.vpm"
try:
    print(dll.vensim_command(b'SPECIAL>LOADMODEL|%s' % ubicación_modelo.encode()) == 1)
except ValueError:
    pass

verificar_vensim()
try:
    dll.vensim_start_simulation(1, 0, 1)
except ValueError:
    pass
verificar_vensim()

try:
    dll.vensim_continue_simulation(10)
except ValueError:
    pass

verificar_vensim()

intermed = ctypes.create_string_buffer(100)
try:
    dll.vensim_get_varnames("*", 0, intermed, 100)
except ValueError as e:
    print(e)

print('intermed: ', intermed.raw, ' ')
print([x for x in intermed.raw.decode().split('\x00') if x])

memimed_val = ctypes.create_string_buffer(4)
print('Memimed: ', memimed_val, struct.unpack('f', memimed_val))
val = memimed_val

try:
    dll.vensim_get_val(b"Efecto", memimed_val)
except ValueError as e:
    print(e)

print('Val: ', memimed_val.raw)
x = struct.unpack('f', memimed_val)
x = x[0]
print('val: ', x)
try:
    dll.vensim_finish_simulation()
except ValueError:
    pass

verificar_vensim()
