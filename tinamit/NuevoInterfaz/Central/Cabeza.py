from dibba import Caja, CajaCuad, Imagen, BotónImg

from NuevoInterfaz.Trads import PáginaTrads

Cabeza = Caja(tamaño=(0, 70), tmñ_rel=(1, 0))
LogoCabeza = Imagen('LogoCabeza.png', tamaño=(None, 60))
BtLenguas = BotónImg('BtLeng_norm.png', img_sel='BtLeng_sel.png', tamaño=(60, 60),
                     acción=PáginaTrads.deslizar, args_acción={'dirección': 'izq'})

CajaArchivo = CajaCuad(tamaño=(60, 60), org=(2, 2))
BtAbrir = BotónImg('BtAbrir_norm.png', img_sel='BtAbrir_sel.png', tamaño=(25, 25))
BtNuevo = BotónImg('BtNuevo_norm.png', img_sel='BtNuevo_sel.png', tamaño=(25, 25))
BtGuardar = BotónImg('BtGuardar_norm.png', img_sel='BtGuardar_sel.png', tamaño=(25, 25))
BtGuardarComo = BotónImg('BtGuardarComo_norm.png', img_sel='BtGuardarComo_sel.png', tamaño=(25, 25))

CajaArchivo.agregar((BtAbrir, BtGuardar, BtNuevo, BtGuardarComo))

Cabeza.agregar(CajaArchivo, pos=(0, ), pos_rel=())
Cabeza.agregar(LogoCabeza, pos_rel=(0.5, 0.5), ref='centro')
Cabeza.agregar(BtLenguas, pos=(-10, 0), pos_rel=(1, 0.5), ref='centro')