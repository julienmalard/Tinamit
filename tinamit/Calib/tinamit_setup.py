'''
Copyright 2015 by Tobias Houska
This file is part of Statistical Parameter Estimation Tool (SPOTPY).

:author: Tobias Houska

This example implements the Rosenbrock function into SPOT.
'''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import spotpy
import numpy as np
from spotpy.objectivefunctions import rmse
from tinamit.Calib import read_xl


class spot_setup(object):
    def __init__(self):
        self.params = [spotpy.parameter.Uniform('Ptq', low=0.351, high=0.555, optguess=0.47),
                       spotpy.parameter.Uniform('Ptr', low=0.368, high=0.506, optguess=0.39),
                       spotpy.parameter.Uniform('Ptx', low=0.374, high=0.5, optguess=0.41),

                       spotpy.parameter.logNormal('Kaq1', mean=4, sigma=0.5, optguess=51.71),
                       spotpy.parameter.logNormal('Kaq2', mean=4, sigma=0.5, optguess=51.71),
                       spotpy.parameter.logNormal('Kaq3', mean=4, sigma=0.5, optguess=51.71),
                       spotpy.parameter.logNormal('Kaq4', mean=4, sigma=0.5, optguess=51.71),
                       spotpy.parameter.Uniform('FsA', low=0.65, high=0.75, ),
                       spotpy.parameter.Uniform('FsB', low=0.65, high=0.75, ),
                       spotpy.parameter.Uniform('FsU', low=0.65, high=0.75, ),
                       spotpy.parameter.Uniform('Peq', low=0.01, high=0.33, )]
        # Maximum Likelihood Estimation (MLE)
        # setup observated data

        self.evals = [10]
        print(len(self.params))

    def parameters(self):
        return spotpy.parameter.generate(self.params)

    def simulation(self, vector):
        print('testing.........')
        print(vector)
        x = np.array(vector)
        # print('x', x)

        y = [0]
        return y

    def evaluation(self):
        return self.evals

    def objectivefunction(self, simulation, evaluation, params=None):
        objectivefunction = -rmse(evaluation=evaluation, simulation=simulation)
        return objectivefunction

# gaby = spot_setup()
# print(gaby.parameters())

