"""
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

# sahysmodIO.py

import os
import sys

import numpy as np
from pkg_resources import resource_filename

from . import mioparser

CSVTEMPLATE = resource_filename(__name__, 'sahysmod.csv.tmpl')
INPTEMPLATE = resource_filename(__name__, 'sahysmod.inp.tmpl')

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


def transpose_params(parameter_dictionary):
    for param in paramsToTranspose:
        array = parameter_dictionary[param]  # type: np.ndarray
        array.transpose()


def read_into_param_dic(from_fn):
    """
    Reads SAHYSMOD input data from a file into a dictionary.

    :param from_fn: The file name of the input data. Can be in SAHYSMOD input (.inp) or in .csv format.
    :type from_fn: str

    :return: A dictionary with the initial data arranged by parameter name.
    :rtype: dict
    """

    # Select the appropriate template.
    from_template = CSVTEMPLATE if from_fn[-3:] == 'csv' else INPTEMPLATE

    # Read the input file.
    param_dictionary = mioparser.readFile(from_fn, from_template)
    transpose_params(param_dictionary)  # Transpose parameters that require it.

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
    param_dictionary['NNS'] = [str(i) for i in range(1, int(param_dictionary['NS']) + 1)]

    return param_dictionary


def write_from_param_dic(param_dictionary, to_fn, csv=False):

    to_template = CSVTEMPLATE if csv else INPTEMPLATE

    mioparser.writeFile(param_dictionary, to_fn, to_template)


def main(from_fn, to_fn):

    param_dictionary = read_into_param_dic(from_fn=from_fn)

    write_from_param_dic(param_dictionary=param_dictionary, to_fn=to_fn,
                         csv=to_fn[-3:] == 'csv')
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
