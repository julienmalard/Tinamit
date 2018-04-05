import json
import os

import matplotlib.pyplot as dib
import numpy as np

from tinamit.EnvolturaMDS import generar_mds, EnvolturaMDS
from tinamit.Geog.Geog import Geografía

# Este escripto corre corridas del modelo basado en las calibraciones en Ejemplo.py
dir_base = os.path.split(__file__)[0]
dir_gráf_calib = os.path.join(dir_base, 'Gráficos', 'Calibs')
dir_gráf_simuls = os.path.join(dir_base, 'Gráficos', 'Simuls')
if not os.path.isdir(dir_gráf_calib):
    os.makedirs(dir_gráf_calib)
if not os.path.isdir(dir_gráf_simuls):
    os.makedirs(dir_gráf_simuls)

with open(os.path.join(dir_base, 'calib.json'), encoding='UTF-8', mode='r') as d:
    dic_calib = json.load(d)

modelo_mds = generar_mds(archivo='Para Tinamït.vpm')
geog = Geografía('Iximulew')
geog.agregar_info_regiones(archivo='Geografía Iximulew.csv',
                           orden_jer=['Departamento', 'Municipio'],
                           col_cód='Código', grupos='Territorio')

vars_interés = []
munis = {m: geog.árbol_geog_inv[m]['Territorio'] for m in geog.obt_lugares_en()}
munis = {m: tr for m, tr in munis.items() if all(m in d_p or 'Territorio {}'.format(tr) in d_p for d_p in dic_calib.values())}


def graficar_calibs():
    for p, d_p in dic_calib.items():
        hay_dist = all('dist' in d_r for d_r in d_p.values())
        hay_val = all('val' in d_r for d_r in d_p.values())
        hay_es = all('ES' in d_r for d_r in d_p.values())

        if hay_dist:
            for r in d_p:
                dib.hist(d_p[r]['dist'], alpha=0.2, label=r.split()[1] if 'Territorio' in r else r)
            dib.legend()
            dib.title(p)
            dib.savefig(os.path.join(dir_gráf_calib, '{}.jpeg'.format(p)))
            dib.clf()

        elif hay_val:
            fig, eje = dib.subplots()
            vals = [d_r['val'] for d_r in d_p.values() if d_r['val'] != 'None']
            nmbs = [r.split()[1] if 'Territorio' in r else r for r, d_r in d_p.items() if d_r['val'] != 'None']
            if hay_es:
                err = [d_r['ES'] for d_r in d_p.values() if d_r['ES'] != 'None']
            else:
                err = None
            eje.bar(x=np.arange(len(vals)), height=vals, yerr=err)
            eje.set_xticks(np.arange(len(vals)))
            eje.set_xticklabels(nmbs)
            eje.set_title(p)
            dib.savefig(os.path.join(dir_gráf_calib, '{}.jpeg'.format(p)))
            dib.clf()
        else:
            raise ValueError


def correr_mod(mod, n_rep=1):
    """

    Parameters
    ----------
    mod : EnvolturaMDS
    n_rep :

    Returns
    -------

    """
    res = {}
    if n_rep == 1:
        dic_prms = {'{}'.format(m): {p: dic_calib[p][m]['val'] if m in dic_calib[p] else dic_calib[p]['Territorio {}'.format(tr)]
                                     for p in dic_calib} for m, tr in munis.items()}

        for lg in dic_prms:
            corr = 'Vld {}'.format(lg)
            mod.inic_vals(dic_prms[lg])
            mod.simular(tiempo_final=20, nombre_corrida=corr, )
            res[lg] = {v: mod.leer_resultados_mds(corrida=corr, var=v) for v in vars_interés}

    else:
        raise NotImplementedError

    return res


# graficar_calibs()
if __name__ == '__main__':
    correr_mod(mod=modelo_mds)
