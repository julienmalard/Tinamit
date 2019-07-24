import os

from setuptools import setup, find_packages

directorio = os.path.split(os.path.realpath(__file__))[0]


def leer(arch):
    with open(os.path.join(directorio, arch), encoding='UTF-8') as d:
        return d.read().strip()


# Leer la versión de Tinamït
versión = leer(os.path.join('tinamit', 'versión.txt'))

# Lo que sigue es código un poco complicado pero necesario para manejar las traducciones del código y de sus
# mensajes al usuario. En gran parte, su necesidad es culpa del paquete Babel que no reconoce lenguas Mayas, entre
# otras lenguas muy útiles.


# Por fin, el código habitual de instalación.
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
    long_description=leer('README.rst'),

    install_requires=[
        'numpy',
        'scipy',
        'matplotlib',
        'pillow',
        'pandas',
        'python_dateutil',
        'regex',
        'lark-parser',
        'pint',
        'pyshp',
        'taqdir',
        'pysd',
        'lxml',
        'xarray',
        'chardet',
        'spotpy',
        'ennikkai'
    ],
    setup_requires=['Babel', 'polib'],
    zip_safe=False,

    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3 :: Only',
    ],
    include_package_data=True
)
