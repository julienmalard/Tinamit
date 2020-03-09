import argparse
import json
import socket
import struct
from struct import pack

import numpy as np


def cliente(puerto):
    HUÉSPED = '127.0.0.1'
    valores = {'numérico': 1, 'matriz': np.arange(12).reshape((3, 4))}

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
        c.connect((HUÉSPED, puerto))
        while True:
            encab, cont = recibir(c)
            tipo = encab['tipo']
            if tipo == 'cerrar':
                break

            elif tipo == 'cambiar':
                var = encab['var']
                matr = encab['matr']
                if matr:
                    val = np.frombuffer(cont)
                else:
                    val = struct.unpack('f', cont)
                if matr:
                    if isinstance(valores[var], np.ndarray):
                        valores[var][:] = val.reshape(valores[var].shape)
                    else:
                        raise TypeError
                else:
                    if isinstance(valores[var], np.ndarray):
                        valores[var][:] = val
                    else:
                        valores[var] = val

                c.sendall(b'0')
            
            elif tipo == 'leer':
                var = encab['var']
                val = valores[var]
                if isinstance(val, np.ndarray):
                    matr = True
                    val = val.tobytes()
                else:
                    matr = False
                    val = struct.pack('f', val)

                mandar(c, encab={'tamaño': len(val), 'matr': matr}, cont=val)

            elif tipo == 'incr':
                n_pasos = encab['n_pasos']
                for var, val in valores.items():
                    valores[var] = val + n_pasos

                c.sendall(b'0')

            else:
                raise ValueError(tipo)


def recibir(con):
    tmñ = con.recv(4)
    encabezado = json.loads(con.recv(tmñ).decode('utf8'))
    tmñ_cont = encabezado['tamaño']
    if tmñ_cont:
        contenido = con.recv()
    else:
        contenido = None

    return encabezado, contenido


def mandar(con, encab, cont):
    encabezado_bytes = json.dumps(encab, ensure_ascii=False).encode('utf8')
    con.sendall(pack('i', len(encabezado_bytes)))

    if cont:
        con.sendall(cont)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ejemplo de cliente enchufe.')
    parser.add_argument("--p", help='El número de puerto para la conexión.')

    args = parser.parse_args()
    cliente(int(args.p))
