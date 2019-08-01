"""
Código modificado de Jérôme Boisvert-Chouinard bajo la licencia MIT.
Code modified from Jérôme Boisvert-Chouinard under the MIT license.

The MIT License (MIT)

Copyright (c) 2014 Jerome Boisvert-Chouinard

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# !/bin/python

# _ie.py

import os
import sys

import numpy as np
from pkg_resources import resource_filename

from tinamit.envolt.bf.sahysmod._arch_ingr import _anlzd_sntct

PLANTILLACSV = resource_filename(__name__, 'rcrs/sahysmod.csv.tmpl')
PLANTILLAINP = resource_filename(__name__, 'rcrs/sahysmod.inp.tmpl')

parámsParaTransponer = [
    'A',
    'B',
    'KCA',
    'KCB',
    'PP',
    'EPA',
    'EPB',
    'EPU',
    'SIU',
    'SOU',
    'SOA',
    'SOB',
    'GW',
    'FRD',
    'LC',
    'CI',
    'IAA',
    'IAB',
    'GU',
    'FW',
    'FSA',
    'FSB',
    'FSU',
    'HS'
]

paráms_enteros = [
    'N_IN',
    'N_EX',
    'KIE_IN',
    'KIE_EX',
    'KLC',
    'FROM_N',
    'TO_N1',
    'TO_N2',
    'TO_N3',
    'TO_N4',
    'KD',
    'KF',
    'KR',
    'KRF',
]


def transponer_paráms(dic_paráms):
    for parám in parámsParaTransponer:
        matr = dic_paráms[parám]  # type: np.ndarray
        matr.transpose()


def leer_info_dic_paráms(archivo_fnt):
    """
    Convierte un fuente de ingresos SAHYSMOD en un diccionario de valores de variables.

    Parameters
    ----------
    archivo_fnt: str
        El fuente con los datos de ingreso, en formato .inp o .csv. 
        
    Returns
    -------
    dict
        El diccionario de los variables y sus valores.

    """

    # Escoger la plantilla apropiada.
    plantilla_fnt = PLANTILLACSV if archivo_fnt[-3:] == 'csv' else PLANTILLAINP

    # Leer el fuente de ingresos.
    dic_paráms = _anlzd_sntct.leer_archivo(archivo_fnt, plantilla_fnt, paráms_ent=paráms_enteros)
    transponer_paráms(dic_paráms)  # Transpose parameters that require it.

    n_en_s = []
    estación = []
    nn_in = int(dic_paráms['NN_IN'])
    for i in range(nn_in):
        n_en_s.append(('{}'.format(i), '', ''))
        estación.append(('1', '2', '3'))

    dic_paráms['NINETYNINE'] = '99'
    dic_paráms['ONE'] = '1'
    dic_paráms['FOURS'] = ['4'] * nn_in
    dic_paráms['N_IN_S'] = n_en_s
    dic_paráms['SEASON'] = estación
    dic_paráms['NNS'] = [str(i) for i in range(1, int(dic_paráms['NS']) + 1)]

    return dic_paráms


def escribir_desde_dic_paráms(dic_paráms, archivo_obj, csv=False):
    plantilla_obj = PLANTILLACSV if csv else PLANTILLAINP

    _anlzd_sntct.escribir_archivo(dic_paráms, archivo_obj, plantilla_obj, paráms_ent=paráms_enteros)


def central(archivo_fnt, archivo_obj):  # pragma: sin cobertura
    dic_paráms = leer_info_dic_paráms(archivo_fnt=archivo_fnt)

    escribir_desde_dic_paráms(dic_paráms=dic_paráms, archivo_obj=archivo_obj,
                              csv=archivo_obj[-3:] == 'csv')
    return 0


if __name__ == '__main__':
    # El código abajo se ejecutará si se llama este fuente desde la línea de comanda (o, por tanto, desde cualquier
    # otro lugar)

    # Leer los argumentos de la línea de comanda. (El primero, sys.argv[0], es simplemente la dirección de este
    # fuente y se ignorará. El segundo es el fuente desde cual hay que leer y el tercero él hacia cual hay que
    # escribir.)
    try:
        archivoFnt = os.path.join(os.getcwd(), sys.argv[1])
        archivoObj = os.path.join(os.getcwd(), sys.argv[2])
    except IndexError:
        # If arguments were not passed, use default file names. This is useful for debugging!
        archivoObj = os.path.join(os.getcwd(), "459anew1.csv")
        archivoFnt = os.path.join(os.getcwd(), "459anew1.inp")

    # Ahora, correr la función central.
    central(archivoFnt, archivoObj)
