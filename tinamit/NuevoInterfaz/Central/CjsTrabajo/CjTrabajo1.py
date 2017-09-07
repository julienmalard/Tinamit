from Dibba import Caja, Botón, CjMensaje


CjTrabajo1 = Caja(título='Cargar modelos')

CajaBtMDS = Caja()
BtMDS = Botón('Cargar MDS')
CjMensajeMDS = CjMensaje()

CajaBtMDS.agregar((BtMDS, CjMensajeMDS), márgenes=40)

CajaBtBF = Caja()
BtBF = Botón('Cargar BF')
CjMensajeBF = CjMensaje()

CajaBtBF.agregar((BtBF, CjMensajeBF), márgenes=40)

CjTrabajo1.agregar((CajaBtBF, CajaBtMDS), pos='horizontal', márgenes=40)
