from Conectado import Conectado
from MDS import EnvolturaMDS
from Biofísico import EnvolturaBF


def conectar_modelos(ubicación_mds, ubicación_biofísico, programa_mds='Vensim'):
    mds = EnvolturaMDS(programa_mds=programa_mds, ubicación_modelo=ubicación_mds)
    bf = EnvolturaBF(ubicación_modelo=ubicación_biofísico)
    modelo_conectado = Conectado(mds=mds, bf=bf)

    return modelo_conectado
