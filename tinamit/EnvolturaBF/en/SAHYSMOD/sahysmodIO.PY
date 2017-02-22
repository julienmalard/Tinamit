#!/bin/python

# sahysmodIO.py

from tinamit.EnvolturaBF.en.SAHYSMOD import mioparser
import os
import sys

CSVTEMPLATE = 'sahysmod.csv.tmpl'
INPTEMPLATE = 'sahysmod.inp.tmpl'

paramsToTranspose = [
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
    'FCD',
    'LC',
    'CIC',
    'IAA',
    'IAB',
    'GU',
    'FW',
    'FSA',
    'FSB',
    'FSU',
    'HS'
]


def transpose_params(parameter_dictionary):
    for param in paramsToTranspose:
        array_a = parameter_dictionary[param]
        array_b = []
        for i in range(len(array_a[0])):
            array_b.append([])
        for vector in array_a:
            i = 0
            for element in vector:
                array_b[i].append(element)
                i += 1
        parameter_dictionary[param] = array_b


def main(from_fn, to_fn):
    from_template = CSVTEMPLATE if from_fn[-3:] == 'csv' else INPTEMPLATE
    to_template = INPTEMPLATE if from_fn[-3:] == 'csv' else CSVTEMPLATE

    param_dictionary = mioparser.readFile(from_fn, from_template)
    transpose_params(param_dictionary)

    n_in_s = []
    season = []
    nn_in = int(param_dictionary['NN_IN'])
    for i in range(nn_in):
        n_in_s.append(('{}'.format(i), '', ''))
        season.append(('1', '2', '3'))

    param_dictionary['NINETYNINE'] = '99'
    param_dictionary['ONE'] = '1'
    param_dictionary['FOURS'] = ['4'] * nn_in
    param_dictionary['N_IN_S'] = n_in_s
    param_dictionary['SEASON'] = season
    param_dictionary['NNS'] = ['{}'.format(i) for i in range(1, int(param_dictionary['NS']) + 1)]

    mioparser.writeFile(param_dictionary, to_fn, to_template)
    return 0


if __name__ == '__main__':
    # This code below will run if the file is caled as a script from the command line (or anywhere else, for that
    # matter).

    # Read the command line arguments. (The first argument, sys.argv[0], is simply the path of this file and so is
    # ignored. The second argument is the file to read from and the third the file to write to.)
    try:
        fromFn = os.path.join(os.getcwd(), sys.argv[1])
        toFn = os.path.join(os.getcwd(), sys.argv[2])
    except IndexError:
        # If arguments were not passed, use default file names. This is useful for debugging!
        toFn = os.path.join(os.getcwd(), "459anew1.csv")
        fromFn = os.path.join(os.getcwd(), "459anew1.inp")

    # Now run the main function.
    main(fromFn, toFn)
