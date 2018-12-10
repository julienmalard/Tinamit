"""
Python model "prueba_para_calib.py"
Translated using PySD version 0.9.0
"""
from __future__ import division
import numpy as np
from pysd import utils
import xarray as xr

from pysd.py_backend.functions import cache
from pysd.py_backend import functions

_subscript_dict = {}

_namespace = {
    'TIME': 'time',
    'Time': 'time',
    'Factor a': 'factor_a',
    'Factor b': 'factor_b',
    'X': 'x',
    'Y': 'y',
    'FINAL TIME': 'final_time',
    'INITIAL TIME': 'initial_time',
    'SAVEPER': 'saveper',
    'TIME STEP': 'time_step'
}

__pysd_version__ = "0.9.0"


@cache('run')
def factor_a():
    """
    Real Name: Factor a
    Original Eqn: 1
    Units: 
    Limits: (0.0, None)
    Type: constant


    """
    return 1


@cache('run')
def factor_b():
    """
    Real Name: Factor b
    Original Eqn: 0
    Units: 
    Limits: (None, None)
    Type: constant


    """
    return 0


@cache('run')
def x():
    """
    Real Name: X
    Original Eqn: 0
    Units: 
    Limits: (None, None)
    Type: constant


    """
    return 0


@cache('step')
def y():
    """
    Real Name: Y
    Original Eqn: Factor a*X+Factor b
    Units: 
    Limits: (None, None)
    Type: component


    """
    return factor_a() * x() + factor_b()


@cache('run')
def final_time():
    """
    Real Name: FINAL TIME
    Original Eqn: 200
    Units: mes
    Limits: (None, None)
    Type: constant

    The final time for the simulation.
    """
    return 200


@cache('run')
def initial_time():
    """
    Real Name: INITIAL TIME
    Original Eqn: 0
    Units: mes
    Limits: (None, None)
    Type: constant

    The initial time for the simulation.
    """
    return 0


@cache('step')
def saveper():
    """
    Real Name: SAVEPER
    Original Eqn: TIME STEP
    Units: mes
    Limits: (0.0, None)
    Type: component

    The frequency with which output is stored.
    """
    return time_step()


@cache('run')
def time_step():
    """
    Real Name: TIME STEP
    Original Eqn: 1
    Units: mes
    Limits: (0.0, None)
    Type: constant

    The time step for the simulation.
    """
    return 1
