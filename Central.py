from Conectado import Conectado
from MDS import CoberturaMDS
from Biofísico import CoberturaBF


def conectar_modelos(ubicación_mds, ubicación_biofísico, programa_mds='Vensim'):
    mds = CoberturaMDS(programa_mds=programa_mds, ubicación_modelo=ubicación_mds)
    bf = CoberturaBF(ubicación_modelo=ubicación_biofísico)
    modelo_conectado = Conectado(mds=mds, bf=bf)

    return modelo_conectado
