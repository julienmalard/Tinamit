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


def anlz_línea_l(línea, nombres_parámetros, dic_parámetros):
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


def anlz_línea_f(línea, nombres_parámetros, anchura_cols, dic_parámetros):  # pragma: sin cobertura
    cursor = 0
    matriz_paráms = 0

    for i in range(len(anchura_cols)):
        if not matriz_paráms:
            if nombres_parámetros[i][0] != '*':
                dic_parámetros[nombres_parámetros[i]] = línea[cursor:cursor + anchura_cols[i]].strip('\n')
                cursor += anchura_cols[i]
            else:
                matriz_paráms = nombres_parámetros[i][1:]
                dic_parámetros[matriz_paráms] = []
        if matriz_paráms:
            dic_parámetros[matriz_paráms].append(línea[cursor:cursor + anchura_cols[i]].strip())
            cursor += anchura_cols[i]
    return dic_parámetros


def construir_línea_f(nombres_paráms, anchura_cols, dic_paráms):  # pragma: sin cobertura
    línea_egr = ''
    matriz_paráms = 0
    for i in range(len(anchura_cols)):
        if not matriz_paráms:
            nombre_parám = nombres_paráms[i]
            if nombre_parám[0] != '*':
                parám = dic_paráms[nombre_parám]
                parám = (anchura_cols[i] - len(parám)) * ' ' + parám
                línea_egr += parám
            else:
                matriz_paráms = nombre_parám.strip('*')
                lista_parám = [parameter for parameter in dic_paráms[matriz_paráms]]
        if matriz_paráms:
            parám = lista_parám.pop(0)
            parám = (anchura_cols[i] - len(parám)) * ' ' + parám
            línea_egr += parám
    return línea_egr + '  \n'


def anal_línea_d(línea, nombres_paráms, delim, dic_paráms):
    línea = línea.strip()
    if delim == 'W':
        valores = línea.split()
    else:
        valores = [value.strip() for value in línea.split(delim)]
    matriz_paráms = 0
    for i in range(len(valores)):
        if not matriz_paráms:
            try:
                if nombres_paráms[i][0] != '*':
                    dic_paráms[nombres_paráms[i]] = valores[i]
                else:
                    matriz_paráms = nombres_paráms[i][1:]
                    dic_paráms[matriz_paráms] = []
            except IndexError:
                return dic_paráms
        if matriz_paráms:
            dic_paráms[matriz_paráms].append(valores[i])
    return dic_paráms


def build_d_línea(nombres_paráms, delim, dic_paráms):
    valores = []
    # Si el separador es espacio blanco ('W'), emplear un espacio cono separador
    delim = '  ' if delim == 'W' else delim
    for nombreParám in nombres_paráms:
        if nombreParám[0] != '*':
            valores.append(str(dic_paráms[nombreParám]))
        else:
            valores += [str(x) for x in dic_paráms[nombreParám.strip('*')]]

    return delim.join(valores) + '  \n'


def anal_línea(línea, nombres_paráms, espec_línea, dic_paráms):
    if espec_línea[0] == 'L':
        anlz_línea_l(línea, nombres_paráms, dic_paráms)
    elif espec_línea[0] == 'F':
        anlz_línea_f(línea, nombres_paráms, espec_línea[1], dic_paráms)
    elif espec_línea[0] == 'D':
        anal_línea_d(línea, nombres_paráms, espec_línea[1], dic_paráms)
    return dic_paráms


def construir_línea(nombres_paráms, espec_línea, dic_paráms, dic_config, paráms_ent):
    if paráms_ent is not None:
        for p in dic_paráms:
            if p in paráms_ent:
                dic_paráms[p] = dic_paráms[p].astype(int)
    if espec_línea[0] == 'L':
        línea = construir_línea_l(nombres_paráms, dic_paráms)
    elif espec_línea[0] == 'F':
        línea = construir_línea_f(nombres_paráms, espec_línea[1], dic_paráms)
    elif espec_línea[0] == 'D':
        línea = build_d_línea(nombres_paráms, espec_línea[1], dic_paráms)
    else:
        raise ValueError(espec_línea[0])
    if 'CSVPAD' in dic_config.keys():
        diff = dic_config['CSVPAD'] - 1 - línea.count(',')
        if diff > 0:
            línea = línea.strip() + ',' * diff + '\n'
    return línea


def _crear_matriz_de_zeros(*dims):
    if len(dims) == 1:
        return [0] * dims[0]
    else:
        matr = []
        for i in range(dims[0]):
            matr.append(_crear_matriz_de_zeros(*dims[1:]))
        return matr


def leer_archivo(nombre_arch_contenido, nombre_arch_plantilla, paráms_ent=None):
    if paráms_ent is None:
        paráms_ent = []

    dic_paráms = {'#': []}
    config_dic = {}
    with open(nombre_arch_contenido, 'r') as archContenido, open(nombre_arch_plantilla, 'r') as archPlantilla:
        for línea_plantilla in archPlantilla:

            if línea_plantilla[0] == '!':
                config_tupla = literal_eval(línea_plantilla[1:].strip())
                config_dic[config_tupla[0]] = config_tupla[1]
            elif línea_plantilla[0] != '#':
                template_tuple = literal_eval(línea_plantilla.strip())
                if template_tuple[0][0:4] != 'FOR[':
                    línea_contenido = archContenido.readline().strip('\n')
                    anal_línea(línea_contenido, template_tuple[1], template_tuple[0], dic_paráms)
                else:
                    dims = [i.strip(']') for i in template_tuple[0].split('[')][1:]
                    for i in range(len(dims)):
                        try:
                            dims[i] = int(dims[i])
                        except ValueError:
                            dims[i] = int(dic_paráms[dims[i]])
                    tuple_espec_línea = template_tuple[1]
                    for especLínea in tuple_espec_línea:

                        for nombre_parám in especLínea[1]:
                            nombre_parám = nombre_parám.strip('*')
                            dic_paráms[nombre_parám] = _crear_matriz_de_zeros(*dims)

                    iterdims = [range(dim) for dim in dims]
                    for indices in itertools.product(*iterdims):
                        dic_temp = {}
                        for especLínea in tuple_espec_línea:
                            línea_contenido = archContenido.readline().strip('\n')
                            anal_línea(línea_contenido, especLínea[1], especLínea[0], dic_temp)
                            for nombre_parám in especLínea[1]:
                                nombre_parám = nombre_parám.strip("*")
                                d = dic_paráms[nombre_parám]
                                for i in indices[:-1]:
                                    d = d[i]
                                d[indices[-1]] = dic_temp[nombre_parám]

    for k, v in dic_paráms.items():
        if isinstance(v, list):
            if k in paráms_ent:
                dic_paráms[k] = np.array(v).astype(int)
            else:
                dic_paráms[k] = np.array(v).astype(float)

    return dic_paráms


def escribir_archivo(dic_paráms, nombre_arch_contenido, nombre_arch_plantilla, paráms_ent=None):
    # k=1
    dic_config = {}
    with open(nombre_arch_contenido, 'w') as archContenido, open(nombre_arch_plantilla, 'r') as arch_plantilla:
        for templatelínea in arch_plantilla:
            if templatelínea[0] == '!':
                tupla_config = literal_eval(templatelínea[1:].strip())
                dic_config[tupla_config[0]] = tupla_config[1]
            elif templatelínea[0] != '#':
                tupla_plantilla = literal_eval(templatelínea.strip())
                if tupla_plantilla[0][0:4] != 'FOR[':
                    archContenido.write(
                        construir_línea(tupla_plantilla[1], tupla_plantilla[0], dic_paráms, dic_config, paráms_ent)
                    )
                else:
                    dims = [i.strip(']') for i in tupla_plantilla[0].split('[')][1:]
                    for i in range(len(dims)):
                        try:
                            dims[i] = int(dims[i])
                        except ValueError:
                            dims[i] = int(dic_paráms[dims[i]])
                    línea_espec_tuple = tupla_plantilla[1]
                    iterdims = [range(dim) for dim in dims]
                    for indices in itertools.product(*iterdims):
                        dic_temp = {}
                        for especLínea in línea_espec_tuple:
                            for nombre_parám in especLínea[1]:
                                nombre_parám = nombre_parám.strip('*')
                                p_d = dic_paráms[nombre_parám]
                                for i in indices:
                                    p_d = p_d[i]

                                dic_temp[nombre_parám] = p_d

                            archContenido.write(
                                construir_línea(especLínea[1], especLínea[0], dic_temp, dic_config, paráms_ent))
    return nombre_arch_contenido


def central(*args):  # pragma: sin cobertura
    if args[1] == '-r':
        dic_paráms = leer_archivo(args[2], args[3])
    elif args[1] == '-c':
        dic_paráms = leer_archivo(args[2], args[3])
        escribir_archivo(dic_paráms, args[4], args[5])
    return 0


# El variable __name___ es igual a __main__ cuando el programa se llama desde la línea de comanda.
# Así, se corre la función `central` cuando se llama desde la línea de comanda, pero no cuando se importa el módulo.
if __name__ == '__main__':
    central(*sys.argv)
