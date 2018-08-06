# -*- coding: utf-8 -*-
'''
Copyright 2015 by Tobias Houska
This file is part of Statistical Parameter Estimation Tool (SPOTPY).

:author: Tobias Houska

This class holds the example code from the getting_started web-documention.
'''
from __future__ import print_function, division, absolute_import, unicode_literals
# Getting started

# To start your experience with SPOT you need to have SPOT installed. Please see the [Installation chapter](index.md) for further details.
# To use SPOT we have to import it and use one of the pre-build examples:
import spotpy  # Load the SPOT package into your working storage
from tinamit.Calib.tinamit_setup import spot_setup  # Import the two dimensional Rosenbrock example

# The example comes along with parameter boundaries, the Rosenbrock function, the optimal value of the function and RMSE as a likelihood.
# So we can directly start to analyse the Rosenbrock function with one of the algorithms. We start with a simple Monte Carlo sampling:
if __name__ == '__main__':
    # Give Monte Carlo algorithm the example setup and saves results in a RosenMC.csv file
    # spot_setup.slow = True
    sampler = spotpy.algorithms.mc(spot_setup(), dbname='Sa_fast', dbformat='ram')

    # Now we can sample with the implemented Monte Carlo algortihm:
    sampler.sample(100)  # Sample 100.000 parameter combinations
    results = sampler.getdata()
    print(results)
