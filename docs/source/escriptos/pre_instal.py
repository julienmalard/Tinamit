import os
import platform
import shutil
import sys
import urllib.request
from subprocess import run
from warnings import warn as avisar
from zipfile import ZipFile as ArchZip

"""
Esta parte instala todas las dependencias de Tinamit de manera automática. Al momento, funciona para Windows con
Python 3.6 de 32 bits. Necesita una buena conexión internet.
"""


so = platform.system()
bits = platform.architecture()[0][:2]

directorio = os.path.split(os.path.realpath(__file__))[0]
directorio_python = os.path.split(sys.executable)[0]
directorio_móds = os.path.join(directorio, 'Módulos')

versión_python = str(sys.version_info.major) + str(sys.version_info.minor)

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

try:
    import pandas
except ImportError:
    pandas = None

info_paquetes = {'numpy': {'__versión__': '1.13.1',
                           'formato_archivo': 'numpy-{__versión__}+mkl-cp{v_py}-cp{v_py}m-{sis}.whl',
                           '35': {
                               'Windows': {
                                   '32': {'id_dropbox': None
                                          },
                                   '64': {'id_dropbox': None
                                          }
                               }
                           },
                           '36': {
                               'Windows': {
                                   '32': {'id_dropbox': 'y66rav81q0i9gtu/numpy-1.11.3%2Bmkl-cp36-cp36m-win32.whl'
                                          },
                                   '64': {'id_dropbox': '1aedimitzcmk34b/numpy-1.13.1%2Bmkl-cp36-cp36m-win_amd64.whl'
                                          }
                               }
                           },
                           },
                 'scipy': {'__versión__': '0.19.1',
                           'formato_archivo': 'scipy-{__versión__}-cp{v_py}-cp{v_py}m-{sis}.whl',
                           '35': {
                               'Windows': {
                                   '32': {'id_google': None
                                          },
                                   '64': {'id_google': None
                                          }
                               }
                           },
                           '36': {
                               'Windows': {
                                   '32': {'id_dropbox': '46vls88hkpohki8/scipy-0.19.1-cp36-cp36m-win32.whl'
                                          },
                                   '64': {'id_dropbox': '18rf9r0gbjl8zil/scipy-0.19.1-cp36-cp36m-win_amd64.whl'
                                          }
                               }
                           },
                           },
                 'matplotlib': {'__versión__': '2.0.2',
                                'formato_archivo': 'matplotlib-{__versión__}-cp{v_py}-none-{sis}.whl',
                                '35': {
                                    'Windows': {
                                        '32': {'id_google': None
                                               },
                                        '64': {'id_google': None
                                               }
                                    }
                                },
                                '36': {
                                    'Windows': {
                                        '32': {'id_google': '0B8RjC9bwyAOwRDlIU2x1YlY0U1U',
                                               'id_dropbox': '0nto54jhq4iwgvm/matplotlib-2.0.2-cp36-cp36m-win32.whl'
                                               },
                                        '64': {'id_dropbox': 'ibq24o9299ij7ta/matplotlib-2.0.2-cp36-cp36m-win_amd64.whl'
                                               }
                                    }
                                },
                                },
                 'pandas': {'__versión__': '0.21.1',
                            'formato_archivo': 'pandas-{__versión__}-cp{v_py}-cp{v_py}m-{sis}.whl',
                            '35': {
                                'Windows': {
                                    '32': {'id_google': None
                                           },
                                    '64': {'id_google': None
                                           }
                                }
                            },
                            '36': {
                                'Windows': {
                                    '32': {'id_google': None,
                                           'id_dropbox': 'rjjupn6c0xyga1h/pandas-0.21.1-cp36-cp36m-win32.whl'
                                           },
                                    '64': {'id_dropbox': 'nn5o8cn9lf8cv0j/pandas-0.21.1-cp36-cp36m-win_amd64.whl'
                                           }
                                }
                            },
                            },

                 }


def _actualizar_pip():
    print('Actualizando pip...')
    comanda_pip = '%s install --upgrade pip' % (os.path.join(directorio_python, 'Scripts', 'pip'))
    run(comanda_pip)


def _descargar_whl(nombre, v_py, sis, b):
    print('Descargando paquete "{}"...'.format(nombre))
    llave = url = None

    repositorios = {'id_dropbox': 'https://www.dropbox.com/s/{}?dl=1',
                    'id_google': 'https://drive.google.com/uc?export=download&id={}'
                    }

    for r, u in repositorios.items():
        try:
            llave = info_paquetes[nombre][v_py][sis][b][r]  # type: str
        except KeyError:
            pass
        if llave is not None:
            url = u.format(llave)
            break

    if url is None:
        avisar('No existe descarga para paquete {} en {} bits.'.format(nombre, bits))
        return False

    nombre_archivo = info_paquetes[nombre]['formato_archivo']
    urllib.request.urlretrieve(url, os.path.join(directorio_móds, nombre_archivo))

    return True


def _instalar_whl(nombre):
    nombre_archivo = info_paquetes[nombre]['formato_archivo']

    if os.path.isfile(os.path.join(directorio_móds, nombre_archivo)):
        éxito = True
    else:
        éxito = _descargar_whl(nombre, v_py=versión_python, sis=so, b=bits)

    if éxito:
        print('Instalando paquete "{}"...'.format(nombre))

        comanda = '%s install %s' % \
                  (os.path.join(directorio_python, 'Scripts', 'pip'),
                   os.path.join(directorio_móds, nombre_archivo))
        run(comanda)


def _instalar_taqdir():
    if not os.path.exists(directorio_móds):
        os.makedirs(directorio_móds)
        dir_creado = True
    else:
        dir_creado = False

    url = 'https://github.com/julienmalard/taqdir/archive/master.zip'
    arch_zip = os.path.join(directorio_móds, 'taqdir.zip')
    dir_taqdir = os.path.join(directorio_móds, 'taqdir')
    urllib.request.urlretrieve(url, arch_zip)
    with ArchZip(arch_zip, 'r') as d:
        d.extractall(dir_taqdir)

    comanda = '{} setup.py install'.format(os.path.join(directorio_python, 'python'))
    run(comanda, cwd=os.path.join(dir_taqdir, 'taqdir-master'))

    if dir_creado:
        shutil.rmtree(directorio_móds)


def _instalar_de_pypi(paquetes):
    for paq in paquetes:
        comanda = '%s install %s' % (os.path.join(directorio_python, 'Scripts', 'pip'), paq)
        run(comanda)


def instalar_requísitos():
    print('Instalando paquetes requísitos...')

    lista_paquetes = []

    if np is None:
        lista_paquetes.append('numpy')

    if matplotlib is None:
        lista_paquetes.append('matplotlib')

    if estad is None:
        lista_paquetes.append('scipy')

    if pandas is None:
        lista_paquetes.append('pandas')

    if len(lista_paquetes):

        if not os.path.exists(directorio_móds):
            os.makedirs(directorio_móds)
            dir_creado = True
        else:
            dir_creado = False

        # Actualizar Pip
        _actualizar_pip()

        # Instalar cada paquete necesario
        for paq in lista_paquetes:
            _instalar_whl(paq)

        if dir_creado:
            shutil.rmtree(directorio_móds)

    _instalar_taqdir()

    _instalar_de_pypi(['pyshp', 'python_dateutil'])

    # Verificar que todo esté bien:
    try:
        import numpy as _
        import scipy as _
        import matplotlib as _
        import taqdir as _
        import pandas as _
        import pyshp as _
        import dateutil as _
    except ImportError:
        _ = None
        pass

    try:
        import scipy.stats as _
        _.norm()
        print('¡Todo bien! Los paquetes Python necesarios han sido instalados.')

    except ImportError:
        _ = None
        avisar('¡Error! Por experencia personal, probablemente es porque no instalaste la __versión__ del'
               '"Microsoft C++ 2015 redistributable" {}.\n'
               'Lo puedes conseguir de "https://www.microsoft.com/es-ES/download/details.aspx?id=48145".'
               .format('x86' if bits == '32' else 'x64')
               )


if so == 'Windows':

    if bits == '32':
        sistema = 'win' + bits
    elif bits == '64':
        sistema = 'win_amd' + bits
    else:
        raise ValueError('Número de bits "{}" no reconocido.'.format(bits))

    for paquete, dic_paq in info_paquetes.items():
        v = dic_paq['__versión__']
        dic_paq['formato_archivo'] = dic_paq['formato_archivo'].format(versión=v, v_py=versión_python, sis=sistema)

    instalar_requísitos()
