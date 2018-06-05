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

import itertools
##########
import sys
from ast import literal_eval

import numpy as np


# _anlzd_sntct.py
#
# Este módulo analiza archivos en formato de texto a base de una plantilla de la sintaxis y convierte entre varios
# formatos.
#
# Ejemplo de uso en línea de comanda:
#
# python _anlzd_sntct.py -r ejemplo_in.txt ejemplo1.tmpl
#
# Analizará ejemplo_in.txt y devolverá un diccionario de los parámetros analizados.
# Es únicamente útil así para la depuración.
#
# python _anlzd_sntct.py -c ejemplo_in.txt ejemplo1.tmpl ejemplo_egr.txt ejemplo2.tmpl
#
# Convertirá ejemplo_in.txt (en formato ejemplo1) a formato ejemplo2, y lo escribirá en ejemplo_egr.txt
#
# Ver la documentación por detalles acerca de la escritura de plantillas.
#
# jerome.boisvert-chouinard@mail.mcgill.ca
# Traducido y modificado por Julien Malard (julien.malard@mail.mcgill.ca)
#


def anal_línea_l(línea, nombres_parámetros, dic_parámetros):
    if nombres_parámetros[0] == '#':
        dic_parámetros['#'].append(línea.strip())
    else:
        dic_parámetros[nombres_parámetros[0]] = línea.strip()
    return dic_parámetros


def construir_línea_l(nombres_parámetros, dic_parámetros):
    if nombres_parámetros[0] == '#':
        try:
            línea = dic_parámetros['#'].pop(0)
        except KeyError:
            línea = ''
        except IndexError:
            línea = ''
    else:
        línea = dic_parámetros[nombres_parámetros[0]]
    return línea + '\n'


def parse_f_línea(línea, nombres_parámetros, anchura_cols, dic_parámetros):
    cursor = 0
    matrizParáms = 0

    for i in range(len(anchura_cols)):
        if not matrizParáms:
            if nombres_parámetros[i][0] != '*':
                dic_parámetros[nombres_parámetros[i]] = línea[cursor:cursor + anchura_cols[i]].strip('\n')
                cursor += anchura_cols[i]
            else:
                matrizParáms = nombres_parámetros[i][1:]
                dic_parámetros[matrizParáms] = []
        if matrizParáms:
            dic_parámetros[matrizParáms].append(línea[cursor:cursor + anchura_cols[i]].strip())
            cursor += anchura_cols[i]
    return dic_parámetros


def construir_línea_f(nombresParáms, anchuraCols, dicParáms):
    líneaEgr = ''
    matrizParáms = 0
    for i in range(len(anchuraCols)):
        if not matrizParáms:
            paramName = nombresParáms[i]
            if paramName[0] != '*':
                parám = dicParáms[paramName]
                parám = (anchuraCols[i] - len(parám)) * ' ' + parám
                líneaEgr += parám
            else:
                matrizParáms = paramName.strip('*')
                listaParám = [parameter for parameter in dicParáms[matrizParáms]]
        if matrizParáms:
            parám = listaParám.pop(0)
            parám = (anchuraCols[i] - len(parám)) * ' ' + parám
            líneaEgr += parám
    return líneaEgr + '  \n'


def anal_línea_d(línea, nombresParáms, delim, dicParáms):
    línea = línea.strip()
    if delim == 'W':
        valores = línea.split()
    else:
        valores = [value.strip() for value in línea.split(delim)]
    matrizParáms = 0
    for i in range(len(valores)):
        if not matrizParáms:
            try:
                if nombresParáms[i][0] != '*':
                    dicParáms[nombresParáms[i]] = valores[i]
                else:
                    matrizParáms = nombresParáms[i][1:]
                    dicParáms[matrizParáms] = []
            except IndexError:
                return dicParáms
        if matrizParáms:
            dicParáms[matrizParáms].append(valores[i])
    return dicParáms


def build_d_línea(nombresParáms, delim, dicParáms):
    valores = []
    # Si el separador es espacio blanco ('W'), emplear un espacio cono separador
    delim = '  ' if delim == 'W' else delim
    for nombreParám in nombresParáms:
        if nombreParám[0] != '*':
            valores.append(str(dicParáms[nombreParám]))
        else:
            valores += [str(x) for x in dicParáms[nombreParám.strip('*')]]

    return delim.join(valores) + '  \n'


def anal_línea(línea, nombresParáms, especLínea, dicParáms):
    if especLínea[0] == 'L':
        anal_línea_l(línea, nombresParáms, dicParáms)
    elif especLínea[0] == 'F':
        parse_f_línea(línea, nombresParáms, especLínea[1], dicParáms)
    elif especLínea[0] == 'D':
        anal_línea_d(línea, nombresParáms, especLínea[1], dicParáms)
    return dicParáms


def construir_línea(nombresParáms, especLínea, dicParáms, dicConfig, paráms_ent):
    if paráms_ent is not None:
        for p in dicParáms:
            if p in paráms_ent:
                dicParáms[p] = dicParáms[p].astype(int)
    if especLínea[0] == 'L':
        línea = construir_línea_l(nombresParáms, dicParáms)
    elif especLínea[0] == 'F':
        línea = construir_línea_f(nombresParáms, especLínea[1], dicParáms)
    elif especLínea[0] == 'D':
        línea = build_d_línea(nombresParáms, especLínea[1], dicParáms)
    else:
        raise ValueError(especLínea[0])
    if 'CSVPAD' in dicConfig.keys():
        diff = dicConfig['CSVPAD'] - 1 - línea.count(',')
        if diff > 0:
            línea = línea.strip() + ',' * diff + '\n'
    return línea


def _crearMatrizDeZeros(*dims):
    if len(dims) == 1:
        return [0] * dims[0]
    else:
        matr = []
        for i in range(dims[0]):
            matr.append(_crearMatrizDeZeros(*dims[1:]))
        return matr


def leer_archivo(nombre_archContenido, nombre_archPlantilla, paráms_ent=None):
    if paráms_ent is None:
        paráms_ent = []

    dic_paráms = {'#': []}
    configDic = {}
    with open(nombre_archContenido, 'r') as archContenido, open(nombre_archPlantilla, 'r') as archPlantilla:
        for línea_plantilla in archPlantilla:

            if línea_plantilla[0] == '!':
                configTupla = literal_eval(línea_plantilla[1:].strip())
                configDic[configTupla[0]] = configTupla[1]
            elif línea_plantilla[0] != '#':
                templateTuple = literal_eval(línea_plantilla.strip())
                if templateTuple[0][0:4] != 'FOR[':
                    línea_contenido = archContenido.readline().strip('\n')
                    anal_línea(línea_contenido, templateTuple[1], templateTuple[0], dic_paráms)
                else:
                    dims = [i.strip(']') for i in templateTuple[0].split('[')][1:]
                    for i in range(len(dims)):
                        try:
                            dims[i] = int(dims[i])
                        except ValueError:
                            dims[i] = int(dic_paráms[dims[i]])
                    tupleEspecLínea = templateTuple[1]
                    for especLínea in tupleEspecLínea:

                        for nombreParám in especLínea[1]:
                            nombreParám = nombreParám.strip('*')
                            dic_paráms[nombreParám] = _crearMatrizDeZeros(*dims)

                    iterdims = [range(dim) for dim in dims]
                    for indices in itertools.product(*iterdims):
                        dicTemp = {}
                        for especLínea in tupleEspecLínea:
                            línea_contenido = archContenido.readline().strip('\n')
                            anal_línea(línea_contenido, especLínea[1], especLínea[0], dicTemp)
                            for nombreParám in especLínea[1]:
                                nombreParám = nombreParám.strip("*")
                                d = dic_paráms[nombreParám]
                                for i in indices[:-1]:
                                    d = d[i]
                                d[indices[-1]] = dicTemp[nombreParám]

    for k, v in dic_paráms.items():
        if isinstance(v, list):
            if k in paráms_ent:
                dic_paráms[k] = np.array(v).astype(int)
            else:
                dic_paráms[k] = np.array(v).astype(float)

    return dic_paráms


def escribir_archivo(dicParáms, nombre_archContenido, nombre_archPlantilla, paráms_ent=None):
    # k=1
    dicConfig = {}
    with open(nombre_archContenido, 'w') as archContenido, open(nombre_archPlantilla, 'r') as archPlantilla:
        for templatelínea in archPlantilla:
            # print('building línea {} of file {}'.format(k, nombre_archPlantilla))
            # k+=1
            if templatelínea[0] == '!':
                tuplaConfig = literal_eval(templatelínea[1:].strip())
                dicConfig[tuplaConfig[0]] = tuplaConfig[1]
            elif templatelínea[0] != '#':
                tuplaPlantilla = literal_eval(templatelínea.strip())
                if tuplaPlantilla[0][0:4] != 'FOR[':
                    archContenido.write(
                        construir_línea(tuplaPlantilla[1], tuplaPlantilla[0], dicParáms, dicConfig, paráms_ent)
                    )
                else:
                    dims = [i.strip(']') for i in tuplaPlantilla[0].split('[')][1:]
                    for i in range(len(dims)):
                        try:
                            dims[i] = int(dims[i])
                        except ValueError:
                            dims[i] = int(dicParáms[dims[i]])
                    líneaSpecTuple = tuplaPlantilla[1]
                    iterdims = [range(dim) for dim in dims]
                    for indices in itertools.product(*iterdims):
                        dicTemp = {}
                        for especLínea in líneaSpecTuple:
                            for nombreParám in especLínea[1]:
                                nombreParám = nombreParám.strip('*')
                                p_d = dicParáms[nombreParám]
                                for i in indices:
                                    p_d = p_d[i]

                                dicTemp[nombreParám] = p_d

                            archContenido.write(
                                construir_línea(especLínea[1], especLínea[0], dicTemp, dicConfig, paráms_ent))
    return nombre_archContenido


def central(*args):
    if args[1] == '-r':
        dicParáms = leer_archivo(args[2], args[3])
        print(dicParáms[args[4]])
    elif args[1] == '-c':
        dicParáms = leer_archivo(args[2], args[3])
        escribir_archivo(dicParáms, args[4], args[5])
    return 0


# El variable __name___ es igual a __main__ cuando el programa se llama desde la línea de comanda.
# Así, se corre la función `central` cuando se llama desde la línea de comanda, pero no cuando se importa el módulo.
if __name__ == '__main__':
    central(*sys.argv)
