import os

import polib
from babel.messages import frontend as babel
from setuptools import setup, find_packages
from setuptools.command.sdist import sdist

directorio = os.path.split(os.path.realpath(__file__))[0]


def leer(arch):
    with open(os.path.join(directorio, arch), encoding='UTF-8') as d:
        return d.read().strip()


# Leer la versión de Tinamït
versión = leer(os.path.join('tinamit', 'versión.txt'))

# Lo que sigue es código un poco complicado pero necesario para manejar las traducciones del código y de sus
# mensajes al usuario. En gran parte, su necesidad es culpa del paquete Babel que no reconoce lenguas Mayas, entre
# otras lenguas muy útiles.


# Leer la lista de idiomas para traducción del código. (Esto NO incluye traducciones de la documentación. Estas
# se manejan a parte.)
dir_local = os.path.join('tinamit', 'local')
dir_fuente = os.path.join(dir_local, '_fuente')
dir_constr = os.path.join(dir_local, '_constr')

# Idiomas que queremos
idiomas = leer(os.path.join(dir_local, 'lenguas.txt')).split('\n')

# Idiomas que ya tenemos, y nuevos idiomas
idiomas_ya = [x for x in os.listdir(dir_fuente) if os.path.isdir(os.path.join(dir_fuente, x))]
idiomas_nuevos = [x for x in idiomas if x not in idiomas_ya]


class dist_f(sdist):
    """
    Clase para crear distribución de código fuente.
    """

    def run(símismo):
        # Antes de generar la distribución de código fuente, tenemos que actualizar las traducciones...

        # Primero, extraer los nuevos mensajes para traducir.
        símismo.run_command('extraer_mens')

        # Ahora, inicializar los nuevos idiomas.
        for i in idiomas_nuevos:
            inicializador = babel.init_catalog(dist=símismo.distribution)
            inicializador.locale = i
            inicializador.run()

        # Actualizar traducciones existentes.
        símismo.run_command('act_cat')

        # Compilar todo.
        símismo.run_command('compilar_cat')

        # lassi.gen_trads(__file__)  # para hacer: activar generación automática de traducciones de código con lassi

        # Seguimos con la generación de distribución fuente según el proceso habitual de Python.
        super().run()


def act_cat_leng(l):
    dir_leng = os.path.join(dir_fuente, l, 'LC_MESSAGES')
    po = polib.pofile(os.path.join(dir_leng, 'tinamit.po'))
    pot = polib.pofile(os.path.join(dir_constr, 'tinamit.pot'))
    po.merge(pot)
    po.save()


def compilar_cat_leng(l):
    dir_leng = os.path.join(dir_fuente, l, 'LC_MESSAGES')
    po = polib.pofile(os.path.join(dir_leng, 'tinamit.po'))
    po.save_as_mofile(os.path.join(dir_leng, 'tinamit.mo'))


def inic_cat_leng(l):
    pot = polib.pofile(os.path.join(dir_constr, l, 'tinamit.pot'))
    pot.save_as_pofile(os.path.join(dir_fuente, 'LC_MESSAGES', 'tinamit.po'))


class compilar_cat(babel.compile_catalog):

    def run(símismo):
        for i in idiomas_ya:
            if babel.localedata.exists(i):
                símismo.locale = i
                super().run()
            else:
                compilar_cat_leng(i)


class act_cat(babel.update_catalog):
    def run(símismo):
        for i in idiomas:
            if babel.localedata.exists(i):
                if i in idiomas_ya:
                    símismo.locale = i
                    super().run()
            else:
                act_cat_leng(i)


class inic_cat(babel.init_catalog):
    def __init__(self, dist):
        super().__init__(dist)

    def run(símismo):
        if babel.localedata.exists(símismo.locale):
            super().run()
        else:
            inic_cat_leng(símismo.locale)


# Por fin, el código habitual de instalación.
setup(
    name='tinamit',
    version=versión,
    packages=find_packages('tinamit'),
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
        'theano',
        'pymc3>=3.4',
        'python_dateutil',
        'regex',
        'lark-parser',
        'Babel',
        'pint',
        'pyshp',
        'taqdir',
        'pysd',
        'lxml',
        'spotpy'
    ],

    dependency_links=[
        "git+git://github.com/julienmalard/pysd.git",
        "git+git://github.com/julienmalard/تقدیر.git"
    ],
    setup_requires=['Babel', 'polib'],
    zip_safe=False,

    include_package_data=True,

    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
    ],

    # Tenemos que hacer unos cambiocitos a las funciones de distribución automáticas para poder compilar
    # traducciones de manera automática.
    cmdclass={'compilar_cat': compilar_cat,  # Compilar el catálogo (PO a MO)
              'extraer_mens': babel.extract_messages,  # Extraer mensajes (crear POT)
              'inic_cat': inic_cat,  # Iniciar el catálogo (agregar idiomas)
              'act_cat': act_cat,  # Actualizar catálogo (sincronizar PO con POT)
              'sdist': dist_f  # Comanda para crear distribución instalable
              }
)
