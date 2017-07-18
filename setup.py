import os
import platform
import shutil
import sys
import urllib.request
from subprocess import run
from warnings import warn as avisar

from setuptools import setup, find_packages

"""
Esta parte instala todas las dependencias de Tinamit de manera automática. Al momento, funciona para Windows con
Python 3.6 de 32 bits. Necesita una buena conexión internet.
"""

versión_python = str(sys.version_info.major) + str(sys.version_info.minor)
so = platform.system()
bits = platform.architecture()[0][:2]

directorio = os.path.split(os.path.realpath(__file__))[0]
directorio_móds = os.path.join(directorio, 'Módulos')
directorio_python = os.path.split(sys.executable)[0]

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

        if not os.path.exists(directorio_móds):
            dir_creado = True
            os.makedirs(directorio_móds)
        else:
            dir_creado = False

        # Actualizar Pip
        _actualizar_pip()

        # Instalar cada paquete necesario
        for paq in lista_paquetes:
            _instalar_whl(paq)

        if dir_creado:
            shutil.rmtree('Módulos')

    # Verificar que todo esté bien:
    try:
        import numpy as _
        import scipy as _
        import matplotlib as _
    except ImportError:
        _ = None
        avisar('Error: No se instalaron todos los módulos necesarios.')

    try:
        import scipy.stats as _
        _.norm()
        print('¡Todo bien! Los paquetes Python necesarios han sido instalados.')

    except ImportError:
        _ = None
        avisar('¡Error! Por experencia personal, probablemente es porque no instalaste la versión del'
               '"Microsoft C++ 2015 redistributable" {}.'.format('x86' if bits == '32' else 'x64')
               )


if so == 'Windows':
    sistema = 'win' + bits

    for paquete, dic_paq in info_paquetes.items():
        v = dic_paq['versión']
        dic_paq['formato_archivo'] = dic_paq['formato_archivo'].format(versión=v, v_py=versión_python, sis=sistema)

    instalar_requísitos()

"""
Ahora, las cosas normales de instalación.
"""

with open('tinamit/versión.txt') as archivo_versión:
    versión = archivo_versión.read().strip()

setup(
    name='tinamit',
    version=versión,
    packages=find_packages(),
    url='https://tinamit.readthedocs.io',
    download_url='https://github.com/julienmalard/Tinamit',
    license='GNU GPL 3',
    author='Julien Jean Malard',
    author_email='julien.malard@mail.mcgill.ca',
    description='Conexión de modelos socioeconómicos (dinámicas de los sistemas) con modelos biofísicos.',
    long_description='Tinamït permite conectar modelos biofísicos con modelos socioeconómicos de dinámicas de los'
                     'sistemas (MDS). Es muy útil para proyectos de modelización participativa, especialmente'
                     'en proyectos de manejo del ambiente. El interaz gráfico traducible facilita la adopción por'
                     'comunidades en cualquier parte del mundo.',
    requires=['numpy', 'matplotlib', 'scipy'],
    classifiers=[
        'Programming Language :: Python :: 3.5',
    ],
    package_data={
        # Incluir estos documentos de los paquetes:
        '': ['*.txt', '*.vpm', '*.json', '*.png', '*.jpg', '*.gif'],
    },
)
