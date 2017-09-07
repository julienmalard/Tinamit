from dibba import apli
from .Inic import PáginaInic
from .Central.Central import PáginaCentral
from .Trads import PgTrads
from .Formatos import formato
from .Control import Control

Apli = apli(título='Tinamit', dim=(640, 480), dim_mín=(640, 480), formato=formato,
            lengua_orig='español', dir_imgs='Imgs')

Apli.agregar(PáginaInic, encima=True)
Apli.agregar(PáginaCentral)
Apli.agregar(PgTrads)

Apli.agregar_controles(Control)

if __name__ == '__main__':
    Apli.correr()
