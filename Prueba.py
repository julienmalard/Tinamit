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

dll = ctypes.WinDLL('C:\\Windows\\System32\\vendll32.dll')
print('1')
verificar_vensim()
ubicación_modelo = "C:\\Users\\jmalar1\\Documents\\PycharmProjects\\Tinamit\\Prueba dll.vpm"

dll.vensim_command('')
print('2')
verificar_vensim()

dll.vensim_command(('SPECIAL>LOADMODEL|"%s"' % ubicación_modelo).encode())
intermed = ctypes.create_string_buffer(100)
dll.vensim_get_varnames(b"*", 0, intermed, 100)
print([x for x in intermed.raw.decode().split('\x00') if x])

print('3')
verificar_vensim()

var = 'FINAL TIME'
comanda = ('SIMULATE>SETVAL|%s = %i' % (var, 200)).encode()
dll.vensim_command(comanda)

intermed_0 = ctypes.create_string_buffer(4)
dll.vensim_get_val(var.encode(), intermed_0)
print('val : ', struct.unpack('f', intermed_0)[0])

dll.vensim_start_simulation(1, 0, 1)
verificar_vensim()

comanda = ('SIMULATE>SETVAL|%s = %i' % (var, 300)).encode()
dll.vensim_command(comanda)
dll.vensim_get_val(var.encode(), intermed_0)
print('val : ', struct.unpack('f', intermed_0)[0])

variable = 'Variable 1'
inter1 = ctypes.create_string_buffer(4)

dll.vensim_get_val(variable.encode(), inter1)

print('Variable inicial:', struct.unpack('f', inter1)[0])

comanda = ('SIMULATE>SETVAL|%s = %i' % (variable, 200)).encode()

dll.vensim_command(comanda)

inter2 = ctypes.create_string_buffer(4)

dll.vensim_get_val(variable.encode(), inter2)
print('Variable modificado:', struct.unpack('f', inter2)[0])

dll.vensim_continue_simulation(10)
dll.vensim_get_val(variable.encode(), inter2)

print('Variable modificado:', struct.unpack('f', inter2)[0])

dll.vensim_finish_simulation()

verificar_vensim()

print('fin')
