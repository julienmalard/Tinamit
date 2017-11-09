from Dibba import Caja, Botón, CjMensaje, escoger_archivo

from tinamit.NuevoInterfaz.Control import Control

CjTrabajo1 = Caja(título='Cargar modelos')


def cargar_mds():
    archivo = escoger_archivo(título='Escoget un modelo DS.', tipos={'.vpm': 'Modelo publicado VENSIM'})
    if archivo:
        Control.estab_mds(archivo_mds=archivo)


CajaBtMDS = Caja()
BtMDS = Botón('Cargar MDS', acción=cargar_mds)
CjMensajeMDS = CjMensaje()

CajaBtMDS.agregar((BtMDS, CjMensajeMDS), márgenes=40)


def cargar_bf():
    archivo = escoger_archivo(título='Escoget un modelo biofísico.', tipos={'.py': 'Envoltura BF Tinamït'})
    if archivo:
        try:
            Control.estab_bf(archivo_bf=archivo)
        except:
            CjMensajeMDS.poner_mensaje('Error con el modelo biofísico.', formato='error')


CajaBtBF = Caja()
BtBF = Botón('Cargar BF', acción=cargar_bf)
CjMensajeBF = CjMensaje()

CajaBtBF.agregar((BtBF, CjMensajeBF), márgenes=40)

CjTrabajo1.agregar((CajaBtBF, CajaBtMDS), pos='horizontal', márgenes=40)
