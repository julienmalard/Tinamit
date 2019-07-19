"""
Python model "prueba_senc_mdl.py"
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

__pysd_version__ = "0.9.0"


@cache('step')
def aleatorio():
    """
    Real Name: Aleatorio
    Original Eqn: GAME ( 0)
    Units: Sdmn
    Limits: (0.0, 1.0)
    Type: component

    b'Un variable aleatorio que debe provenir del modelo BP.'
    """
    return (0)


@cache('step')
def evaporación():
    """
    Real Name: Evaporación
    Original Eqn: 0.1*Lago
    Units: m3/mes
    Limits: (0.0, None)
    Type: component

    b'La evaporaci\\xf3n del lago, fijo al 10%.'
    """
    return 0.1 * lago()


@cache('step')
def flujo_río():
    """
    Real Name: Flujo río
    Original Eqn: Lluvia
    Units: m3/mes
    Limits: (0.0, None)
    Type: component

    b'El flujo de agua en el r\\xedo.'
    """
    return lluvia()


@cache('step')
def lago():
    """
    Real Name: Lago
    Original Eqn: INTEG ( Flujo río-Evaporación, Nivel lago inicial)
    Units: m3
    Limits: (0.0, None)
    Type: component

    b'La cantidad de agua en el lago.'
    """
    return integ_lago()


@cache('step')
def lluvia():
    """
    Real Name: Lluvia
    Original Eqn: GAME ( 10)
    Units: m3/mes
    Limits: (0.0, None)
    Type: component

    b'La cantidad de lluvia que cae por mes.'
    """
    return (10)


@cache('run')
def nivel_lago_inicial():
    """
    Real Name: Nivel lago inicial
    Original Eqn: 1500
    Units: m3
    Limits: (0.0, None)
    Type: constant

    b'La cantidad inicial  de ag   ua en el lago.'
    """
    return 1500


@cache('run')
def final_time():
    """
    Real Name: FINAL TIME
    Original Eqn: 200
    Units: mes
    Limits: (None, None)
    Type: constant

    b'The final time for the simulation.'
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

    b'The initial time for the simulation.'
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

    b'The frequency with which output is stored.'
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

    b'The time step for the simulation.'
    """
    return 1


integ_lago = functions.Integ(lambda: flujo_río() - evaporación(), lambda: nivel_lago_inicial())
