from dibba import Página, Botón, Imagen, Caja


PáginaInic = Página()

BtAbrir = Botón('Abrir', tamaño=(100, 50),
                acción=PáginaInic.quitar, args_acción='arriba')
BtAyuda = Botón('Ayuda', tamaño=(100, 50),
                enlace='http://tinamit.rtfd.io')

CajaBtns = Caja()
CajaBtns.agregar([BtAbrir, BtAyuda], pos='horizontal', márgenes=20)

LogoCentral = Imagen('LogoCentral.jpg', dim=(300, None))


PáginaInic.agregar(LogoCentral, ref='centro', pos=(0.5, 100), pos_rel=(True, False))
PáginaInic.agregar(CajaBtns, ref='centro', pos=(0.5, 200), pos_rel=(True, False))
