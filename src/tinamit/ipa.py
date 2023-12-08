import click

from . import servidor


@click.command()
@click.option('--dirección', default='localhost', help='La dirección IP. Generalmente 127.0.0.1.')
@click.option('--puerto', help='Puerto para la conexión.')
def correr(dirección, puerto):
    servidor.correr(dirección, int(puerto))
