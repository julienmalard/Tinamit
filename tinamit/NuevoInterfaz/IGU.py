from dibba import apli

from .Central.Central import PáginaCentral
from .Control import Control
from .Formatos import formato
from .Inic import PáginaInic
from .Trads import PgTrads

Apli = apli(título='Tinamit', dim=(640, 480), dim_mín=(640, 480), formato=formato,
            lengua_orig='español', dir_imgs='Imgs')

Apli.agregar(PáginaInic, encima=True)
Apli.agregar(PáginaCentral)
Apli.agregar(PgTrads)

Apli.agregar_controles(Control)

if __name__ == '__main__':
    Apli.correr()
