"""
Code from Jérôme Boisvert-Chouinard under the MIT license.

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

# mioparser.py
#
# This module can parse fixed format text files based on template files
# and convert between different formats.
#
# Example commmand line usage:
#
# python mioparser.py -r example_in.txt example1.tmpl
#
# Parses example_in.txt and print parsed parameters as a dictionary
# This is only really useful for debugging.
#
# python mioparser.py -c example_in.txt example1.tmpl example_out.txt example2.tmpl
#
# Converts example_in.txt (in example1 format) to example2 format, and writes output to example_out.txt
#
# See documentation for details on how to write template files.
#
# jerome.boisvert-chouinard@mail.mcgill.ca
#
##########
import sys
import itertools
from ast import literal_eval
import numpy as np


def parse_l_line(line, parameter_names, parameter_dictionary):
    if parameter_names[0] == '#':
        parameter_dictionary['#'].append(line.strip())
    else:
        parameter_dictionary[parameter_names[0]] = line.strip()
    return parameter_dictionary


def build_l_line(parameter_names, parameter_dictionary):
    if parameter_names[0] == '#':
        try:
            line = parameter_dictionary['#'].pop(0)
        except KeyError:
            line = ''
        except IndexError:
            line = ''
    else:
        line = parameter_dictionary[parameter_names[0]]
    return line + '\n'


def parse_f_line(line, parameter_names, column_widths, parameter_dictionary):
    cursor = 0
    arrayParam = 0

    for i in range(len(column_widths)):
        if not arrayParam:
            if parameter_names[i][0] != '*':
                parameter_dictionary[parameter_names[i]] = line[cursor:cursor + column_widths[i]].strip('\n')
                cursor += column_widths[i]
            else:
                arrayParam = parameter_names[i][1:]
                parameter_dictionary[arrayParam] = []
        if arrayParam:
            parameter_dictionary[arrayParam].append(line[cursor:cursor + column_widths[i]].strip())
            cursor += column_widths[i]
    return parameter_dictionary


def buildFLine(parameterNames, columnWidths, parameterDictionary):
    lineOut = ''
    arrayParam = 0
    for i in range(len(columnWidths)):
        if not arrayParam:
            paramName = parameterNames[i]
            if paramName[0] != '*':
                param = parameterDictionary[paramName]
                param = (columnWidths[i] - len(param)) * ' ' + param
                lineOut += param
            else:
                arrayParam = paramName.strip('*')
                paramList = [parameter for parameter in parameterDictionary[arrayParam]]
        if arrayParam:
            param = paramList.pop(0)
            param = (columnWidths[i] - len(param)) * ' ' + param
            lineOut += param
    return lineOut + '  \n'


def parse_d_line(line, parameterNames, delim, parameterDictionary):
    line = line.strip()
    if delim == 'W':
        values = line.split()
    else:
        values = [value.strip() for value in line.split(delim)]
    arrayParam = 0
    for i in range(len(values)):
        if not arrayParam:
            try:
                if parameterNames[i][0] != '*':
                    parameterDictionary[parameterNames[i]] = values[i]
                else:
                    arrayParam = parameterNames[i][1:]
                    parameterDictionary[arrayParam] = []
            except IndexError:
                return parameterDictionary
        if arrayParam:
            parameterDictionary[arrayParam].append(values[i])
    return parameterDictionary


def buildDLine(parameterNames, delim, parameterDictionary):
    values = []
    # If the separator is whitespace (denotes by 'W'), use a space as separator
    delim = '  ' if delim == 'W' else delim
    for paramName in parameterNames:
        if paramName[0] != '*':
            values.append(str(parameterDictionary[paramName]))
        else:
            values += [str(x) for x in parameterDictionary[paramName.strip('*')]]

    return delim.join(values) + '  \n'


def parseLine(line, parameterNames, lineSpec, parameterDictionary):
    if lineSpec[0] == 'L':
        parse_l_line(line, parameterNames, parameterDictionary)
    elif lineSpec[0] == 'F':
        parse_f_line(line, parameterNames, lineSpec[1], parameterDictionary)
    elif lineSpec[0] == 'D':
        parse_d_line(line, parameterNames, lineSpec[1], parameterDictionary)
    return parameterDictionary


def buildLine(parameterNames, lineSpec, parameterDictionary, configDictionary):
    if lineSpec[0] == 'L':
        line = build_l_line(parameterNames, parameterDictionary)
    elif lineSpec[0] == 'F':
        line = buildFLine(parameterNames, lineSpec[1], parameterDictionary)
    elif lineSpec[0] == 'D':
        line = buildDLine(parameterNames, lineSpec[1], parameterDictionary)
    if 'CSVPAD' in configDictionary.keys():
        diff = configDictionary['CSVPAD'] - 1 - line.count(',')
        if diff > 0:
            line = line.strip() + ',' * diff + '\n'
    return line

def createArrayOfZeros(*dims):
    if len(dims) == 1:
        return [0]*dims[0]
    else:
        arr = []
        for i in range(dims[0]):
            arr.append(createArrayOfZeros(*dims[1:]))
        return arr


def readFile(contentFn, templateFn):
    """
    This function reads a SAHYSMOD input file (.inp or .csv format)
    :param contentFn:
    :type contentFn: str
    :param templateFn:
    :type templateFn: str
    :return:
    :rtype:
    """

    param_dictionary = {'#': []}
    configDictionary = {}
    with open(contentFn, 'r') as contentF, open(templateFn, 'r') as templateF:
        for templateLine in templateF:

            if templateLine[0] == '!':
                configTuple = literal_eval(templateLine[1:].strip())
                configDictionary[configTuple[0]] = configTuple[1]
            elif templateLine[0] != '#':
                templateTuple = literal_eval(templateLine.strip())
                if templateTuple[0][0:4] != 'FOR[':
                    contentLine = contentF.readline().strip('\n')
                    parseLine(contentLine, templateTuple[1], templateTuple[0], param_dictionary)
                else:
                    dims = [i.strip(']') for i in templateTuple[0].split('[')][1:]
                    for i in range(len(dims)):
                        try:
                            dims[i] = int(dims[i])
                        except ValueError:
                            dims[i] = int(param_dictionary[dims[i]])
                    lineSpecTuple = templateTuple[1]
                    for lineSpec in lineSpecTuple:

                        for paramName in lineSpec[1]:
                            paramName = paramName.strip('*')
                            param_dictionary[paramName] = createArrayOfZeros(*dims)

                    iterdims = [range(dim) for dim in dims]
                    for indices in itertools.product(*iterdims):
                        tempDict = {}
                        for lineSpec in lineSpecTuple:
                            contentLine = contentF.readline().strip('\n')
                            parseLine(contentLine, lineSpec[1], lineSpec[0], tempDict)
                            for paramName in lineSpec[1]:
                                paramName = paramName.strip("*")
                                d = param_dictionary[paramName]
                                for i in indices[:-1]:
                                    d = d[i]
                                d[indices[-1]] = tempDict[paramName]

    for k, v in param_dictionary.items():
        if isinstance(v, list):
            param_dictionary[k] = np.array(v).astype(float)

    return param_dictionary


def writeFile(parameterDictionary, contentFn, templateFn):
    # k=1
    configDictionary = {}
    with open(contentFn, 'w') as contentF, open(templateFn, 'r') as templateF:
        for templateLine in templateF:
            # print('building line {} of file {}'.format(k, templateFn))
            # k+=1
            if templateLine[0] == '!':
                configTuple = literal_eval(templateLine[1:].strip())
                configDictionary[configTuple[0]] = configTuple[1]
            elif templateLine[0] != '#':
                templateTuple = literal_eval(templateLine.strip())
                if templateTuple[0][0:4] != 'FOR[':
                    contentF.write(buildLine(templateTuple[1], templateTuple[0], parameterDictionary, configDictionary))
                else:
                    dims = [i.strip(']') for i in templateTuple[0].split('[')][1:]
                    for i in range(len(dims)):
                        try:
                            dims[i] = int(dims[i])
                        except ValueError:
                            dims[i] = int(parameterDictionary[dims[i]])
                    lineSpecTuple = templateTuple[1]
                    iterdims = [range(dim) for dim in dims]
                    for indices in itertools.product(*iterdims):
                        tempDict = {}
                        indicesString = ''.join(['[{}]'.format(i) for i in indices])
                        for lineSpec in lineSpecTuple:
                            for paramName in lineSpec[1]:
                                paramName = paramName.strip('*')
                                p_d = parameterDictionary[paramName]
                                for i in indices:
                                    p_d = p_d[i]

                                tempDict[paramName] = p_d

                            contentF.write(buildLine(lineSpec[1], lineSpec[0], tempDict, configDictionary))
    return contentFn


def main(*args):
    if args[1] == '-r':
        parameterDictionary = readFile(args[2], args[3])
        print(parameterDictionary[args[4]])
    elif args[1] == '-c':
        parameterDictionary = readFile(args[2], args[3])
        writeFile(parameterDictionary, args[4], args[5])
    return 0


# The __name___ built-in variable is set to __main__ when the program is run from command line
# That way main is run when the file is ran from command line but not when it is imported
if __name__ == '__main__':
    main(*sys.argv)
