import os
import platform
import sys
from subprocess import run
import urllib.request
import shutil


"""
Este programa instala Tinamit y todas sus dependencias de manera automática. Al momento, funciona para Windows con
Python 3.6 de 32 bits. Necesita una buena conexión internet.
Tinamit se instala de la versión más recién en PyPI. Si no quieres instalar Tinamit, pero únicamente sus requísitos,
usar la función instalar_requísitos() en vez de instalar_todo().
"""

try:
    import numpy as np
except ImportError:
    np = None

try:
    import matplotlib
except ImportError:
    matplotlib = None

try:
    import scipy.stats as estad
except ImportError:
    estad = None

directorio = os.path.split(os.path.realpath(__file__))[0]

directorio_móds = os.path.join(directorio, 'Módulos')

if not os.path.exists(directorio_móds):
    os.makedirs(directorio_móds)

directorio_python = os.path.split(sys.executable)[0]

versión_python = str(sys.version_info.major) + str(sys.version_info.minor)

so = platform.system()

if so != 'Windows':
    raise OSError('Este programa de instalación funciona únicamente para Windows.')

bits = platform.architecture()[0][:2]
sistema = 'win' + bits

info_paquetes = {'numpy': {'versión': '1.11.3',
                           'formato_archivo': 'numpy-{versión}+mkl-cp{v_py}-cp{v_py}m-{sis}.whl',
                           'id_google': {'32': '0B8RjC9bwyAOwUV9zV2lSdjA3eHM',
                                         '64': None}
                           },
                 'scipy': {'versión': '0.18.1',
                           'formato_archivo': 'scipy-{versión}-cp{v_py}-none-{sis}.whl',
                           'id_google': {'32': '0B8RjC9bwyAOwTEZCdWdMbDQ4VG8',
                                         '64': None}
                           },
                 'matplotlib': {'versión': '2.0.0',
                                'formato_archivo': 'matplotlib-{versión}-cp{v_py}-none-{sis}.whl',
                                'id_google': {'32': '0B8RjC9bwyAOwRDlIU2x1YlY0U1U',
                                              '64': None}
                                }
                 }


for paquete, dic_paq in info_paquetes.items():
    v = dic_paq['versión']
    dic_paq['formato_archivo'] = dic_paq['formato_archivo'].format(versión=v, v_py=versión_python, sis=sistema)


def _actualizar_pip():
    print('Actualizando pip...')
    comanda_pip = '%s install --upgrade pip' % (os.path.join(directorio_python, 'Scripts', 'pip'))
    run(comanda_pip)


def _descargar_whl(nombre):

    print('Descargando paquete "{}"...'.format(nombre))
    llave = info_paquetes[nombre]['id_google'][bits]  # type: str
    if llave is None:
        raise ValueError('No existe descarga para paquete {} en {} bits.'.format(nombre, bits))
    if nombre == 'numpy':
        url = 'https://www.dropbox.com/s/rmsmiu1ivpnvizd/numpy-1.11.3%2Bmkl-cp36-cp36m-win32.whl?dl=1'
    else:
        url = 'https://drive.google.com/uc?export=download&id=' + llave
    nombre_archivo = info_paquetes[nombre]['formato_archivo']
    urllib.request.urlretrieve(url, os.path.join(directorio_móds, nombre_archivo))


def _instalar_whl(nombre):

    nombre_archivo = info_paquetes[nombre]['formato_archivo']

    if not os.path.isfile(os.path.join(directorio_móds, nombre_archivo)):
        _descargar_whl(nombre)

    print('Instalando paquete "{}"...'.format(nombre))

    comanda = '%s install %s' % (os.path.join(directorio_python, 'Scripts', 'pip'),
                                 os.path.join(directorio_móds, nombre_archivo))
    run(comanda)


def instalar_requísitos():
    lista_paquetes = []

    if np is None:
        lista_paquetes.append('numpy')

    if matplotlib is None:
        lista_paquetes.append('matplotlib')

    if estad is None:
        lista_paquetes.append('scipy')

    if len(lista_paquetes):
        # Actualizar Pip
        _actualizar_pip()

        # Instalar cada paquete necesario
        for paq in lista_paquetes:
            _instalar_whl(paq)

        shutil.rmtree('Módulos')

    # Verificar que todo esté bien:
    try:
        import numpy as _
        import scipy as _
        import matplotlib as _
    except ImportError:
        _ = None
        raise ImportError('Error: No se instalaron todos los módulos necesarios.')

    try:
        import scipy.stats as _
        _.norm()
        print('¡Todo bien! Los paquetes Python necesarios han sido instalados.')

    except ImportError:
        _ = None
        raise ImportError('¡Error! Por experencia personal, probablemente es porque no instalaste la versión del'
                          '"Microsoft C++ 2015 redistributable" {}.'.format('x86' if bits == '32' else 'x64')
                          )


def instalar_todo():

    print('Instalando paquetes requísitos...')
    instalar_requísitos()

    print('Instalando Tiko\'n...')
    comanda = '%s install tinamit' % os.path.join(directorio_python, 'Scripts', 'pip')

    run(comanda)


if __name__ == '__main__':
    instalar_todo()
