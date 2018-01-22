import os

from babel.messages import frontend as babel
from setuptools import setup, find_packages

directorio = os.path.split(os.path.realpath(__file__))[0]

with open(os.path.join(directorio, 'tinamit', 'versión.txt')) as archivo_versión:
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
                     'sistemas (EnvolturaMDS). Es muy útil para proyectos de modelización participativa, especialmente'
                     'en proyectos de manejo del ambiente. El interaz gráfico traducible facilita la adopción por'
                     'comunidades en cualquier parte del mundo.',
    requires=['numpy', 'matplotlib', 'scipy', 'taqdir', 'python_dateutil', 'pyshp', 'pandas', 'lark'],
    setup_requires=['Babel'],
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3.6',
    ],
    package_data={
        # Incluir estos documentos de los paquetes:
        '': ['*.txt', '*.vpm', '*.json', '*.png', '*.jpg', '*.gif'],
    },
    cmdclass={'compile_catalog': babel.compile_catalog,
              'extract_messages': babel.extract_messages,
              'init_catalog': babel.init_catalog,
              'update_catalog': babel.update_catalog}
)

# lassi.gen_trads(__file__)  # para hacer: activar generación automática de traducciones con lassi
