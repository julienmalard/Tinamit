from setuptools import setup, find_packages

setup(
    name='tinamit',
    version='1.2.0',
    packages=find_packages(),
    url='https://github.com/julienmalard/Tinamit',
    license='GNU GPL 3',
    author='Julien Jean Malard',
    author_email='julien.malard@mail.mcgill.ca',
    description='Conexión de modelos socioeconómicos (dinámicas de los sistemas) con modelos biofísicos.',
    requires=['numpy', 'matplotlib', 'scipy'],
    include_package_data=True
)
