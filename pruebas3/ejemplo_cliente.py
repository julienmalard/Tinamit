import json
import socket
import sys
import time
from struct import unpack, pack

import numpy as np

datos = {
    'entero': np.arange(5, dtype=int),
    'decimal': np.arange(0, 5, 0.5),
    'entero negativo': np.arange(-5, 5, dtype=int),
    'decimal negativo': np.arange(-5, 5, 0.5),
    'multidim': np.arange(2 * 3 * 5).reshape((2, 3, 5))
}


def cliente_puertos(dirección, puerto, t_final):
    t_final = int(t_final)
    vals = datos.copy()
    vals['t'] = np.array([0])
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as e:
        e.connect((dirección, int(puerto)))

        while True:
            encab = _recibir_encabezado(e)
            tipo = encab['tipo'].lower()

            if tipo == 'incr':
                n_pasos = encab['n_pasos']
                if n_pasos == 0:
                    vals['t'][:] = t_final
                else:
                    vals['t'][:] = min(vals['t'] + n_pasos, t_final)

            elif tipo == 'leer':
                var = encab['var']

                vals_bits = vals[var].tobytes()
                encabezado = json.dumps({
                    'tamaño': len(vals_bits),
                    'tipo_cont': str(vals[var].dtype),
                    'forma': vals[var].shape
                }).encode('utf8')
                e.sendall(pack('i', len(encabezado)))
                e.sendall(encabezado)

                e.sendall(vals_bits)

            elif tipo == 'cambiar':
                var = encab['var']
                tmñ = encab['tamaño']
                tipo_m = encab['tipo_cont']
                forma = encab['forma']

                val = np.frombuffer(e.recv(tmñ), dtype=tipo_m).reshape(forma)
                vals[var] = val

            elif tipo == 'cerrar':
                break

            else:
                raise ValueError(tipo)


def _recibir_encabezado(e):
    tmñ = unpack('i', e.recv(4))[0]
    return json.loads(e.recv(tmñ).decode('utf8'))


if __name__ == '__main__':
    cliente_puertos(*sys.argv[1:])
