from tinamit.EnvolturaBF.en.SAHYSMOD.mioparser import main
from tinamit.EnvolturaBF.en.SAHYSMOD.mioparser import write_file
from tinamit.EnvolturaBF.en.SAHYSMOD.mioparser import read_file
from tinamit.EnvolturaBF.en.SAHYSMOD.mioparser import createArrayOfZeros
from tinamit.EnvolturaBF.en.SAHYSMOD.mioparser import buildLine
from tinamit.EnvolturaBF.en.SAHYSMOD.mioparser import parseLine
from tinamit.EnvolturaBF.en.SAHYSMOD.mioparser import build_d_line
from tinamit.EnvolturaBF.en.SAHYSMOD.mioparser import parse_d_line
from tinamit.EnvolturaBF.en.SAHYSMOD.mioparser import build_f_line
from tinamit.EnvolturaBF.en.SAHYSMOD.mioparser import parse_f_line
from tinamit.EnvolturaBF.en.SAHYSMOD.mioparser import build_l_line
from tinamit.EnvolturaBF.en.SAHYSMOD.mioparser import parse_l_line


def parse_l_line(line, parameter_names, parameter_dictionary):
    return parse_l_line(line=line, parameter_names=parameter_names, parameter_dictionary=parameter_dictionary)


def build_l_line(parameter_names, parameter_dictionary):
    return build_l_line(parameter_names=parameter_names, parameter_dictionary=parameter_dictionary)


def parse_f_line(line, parameter_names, column_widths, parameter_dictionary):
    return parse_f_line(line=line, parameter_names=parameter_names, column_widths=column_widths, parameter_dictionary=parameter_dictionary)


def build_f_line(parameterNames, columnWidths, parameterDictionary):
    return build_f_line(parameterNames=parameterNames, columnWidths=columnWidths, parameterDictionary=parameterDictionary)


def parse_d_line(line, parameterNames, delim, parameterDictionary):
    return parse_d_line(line=line, parameterNames=parameterNames, delim=delim, parameterDictionary=parameterDictionary)


def build_d_line(parameterNames, delim, parameterDictionary):
    return build_d_line(parameterNames=parameterNames, delim=delim, parameterDictionary=parameterDictionary)


def parseLine(line, parameterNames, lineSpec, parameterDictionary):
    return parseLine(line=line, parameterNames=parameterNames, lineSpec=lineSpec, parameterDictionary=parameterDictionary)


def buildLine(parameterNames, lineSpec, parameterDictionary, configDictionary, int_params):
    return buildLine(parameterNames=parameterNames, lineSpec=lineSpec, parameterDictionary=parameterDictionary, configDictionary=configDictionary, int_params=int_params)


def createArrayOfZeros():
    return createArrayOfZeros()


def read_file(contentFn, templateFn, int_params):
    return read_file(contentFn=contentFn, templateFn=templateFn, int_params=int_params)


def write_file(parameterDictionary, contentFn, templateFn, int_params):
    return write_file(parameterDictionary=parameterDictionary, contentFn=contentFn, templateFn=templateFn, int_params=int_params)


def main():
    return main()
