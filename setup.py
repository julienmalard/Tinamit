from setuptools import setup, find_packages


with open('tikon/versión.txt') as archivo_versión:
    versión = archivo_versión.read().strip()


setup(
    name='tinamit',
    version=versión,
    packages=find_packages(),
    url='https://github.com/julienmalard/Tinamit',
    license='GNU GPL 3',
    author='Julien Jean Malard',
    author_email='julien.malard@mail.mcgill.ca',
    description='Conexión de modelos socioeconómicos (dinámicas de los sistemas) con modelos biofísicos.',
    requires=['numpy', 'matplotlib', 'scipy'],
    package_data={
        # Incluir estos documentos de los paquetes:
        '': ['*.txt', '*.vpm', '*.json', '*.png', '*.jpg', '*.gif'],
    },
)
