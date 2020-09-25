"""
Python model "prueba_senc_mdl.py"
Translated using PySD version 0.10.0
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
    'Aleatorio': 'aleatorio',
    'Evaporación': 'evaporación',
    'Flujo río': 'flujo_río',
    'Lago': 'lago',
    'Lluvia': 'lluvia',
    'Nivel lago inicial': 'nivel_lago_inicial',
    'FINAL TIME': 'final_time',
    'INITIAL TIME': 'initial_time',
    'SAVEPER': 'saveper',
    'TIME STEP': 'time_step'
}

__pysd_version__ = "0.10.0"

__data = {'scope': None, 'time': lambda: 0}


def _init_outer_references(data):
    for key in data:
        __data[key] = data[key]


def time():
    return __data['time']()


@cache('step')
def aleatorio():
    """
    Real Name: b'Aleatorio'
    Original Eqn: b'GAME ( 0)'
    Units: b'Sdmn'
    Limits: (0.0, 1.0)
    Type: component

    b'Un variable aleatorio que debe provenir del modelo BP.'
    """
    return (0)


@cache('step')
def evaporación():
    """
    Real Name: b'Evaporaci\\xf3n'
    Original Eqn: b'0.1*Lago'
    Units: b'm3/mes'
    Limits: (0.0, None)
    Type: component

    b'La evaporaci\\xf3n del lago, fijo al 10%.'
    """
    return 0.1 * lago()


@cache('step')
def flujo_río():
    """
    Real Name: b'Flujo r\\xedo'
    Original Eqn: b'Lluvia'
    Units: b'm3/mes'
    Limits: (0.0, None)
    Type: component

    b'El flujo de agua en el r\\xedo.'
    """
    return lluvia()


@cache('step')
def lago():
    """
    Real Name: b'Lago'
    Original Eqn: b'INTEG ( Flujo r\\xedo-Evaporaci\\xf3n, Nivel lago inicial)'
    Units: b'm3'
    Limits: (0.0, None)
    Type: component

    b'La cantidad de agua en el lago.'
    """
    return _integ_lago()


@cache('step')
def lluvia():
    """
    Real Name: b'Lluvia'
    Original Eqn: b'GAME ( 10)'
    Units: b'm3/mes'
    Limits: (0.0, None)
    Type: component

    b'La cantidad de lluvia que cae por mes.'
    """
    return (10)


@cache('run')
def nivel_lago_inicial():
    """
    Real Name: b'Nivel lago inicial'
    Original Eqn: b'1500'
    Units: b'm3'
    Limits: (0.0, None)
    Type: constant

    b'La cantidad inicial  de ag   ua en el lago.'
    """
    return 1500


@cache('run')
def final_time():
    """
    Real Name: b'FINAL TIME'
    Original Eqn: b'200'
    Units: b'mes'
    Limits: (None, None)
    Type: constant

    b'The final time for the simulation.'
    """
    return 200


@cache('run')
def initial_time():
    """
    Real Name: b'INITIAL TIME'
    Original Eqn: b'0'
    Units: b'mes'
    Limits: (None, None)
    Type: constant

    b'The initial time for the simulation.'
    """
    return 0


@cache('step')
def saveper():
    """
    Real Name: b'SAVEPER'
    Original Eqn: b'TIME STEP'
    Units: b'mes'
    Limits: (0.0, None)
    Type: component

    b'The frequency with which output is stored.'
    """
    return time_step()


@cache('run')
def time_step():
    """
    Real Name: b'TIME STEP'
    Original Eqn: b'1'
    Units: b'mes'
    Limits: (0.0, None)
    Type: constant

    b'The time step for the simulation.'
    """
    return 1


_integ_lago = functions.Integ(lambda: flujo_río() - evaporación(), lambda: nivel_lago_inicial())
