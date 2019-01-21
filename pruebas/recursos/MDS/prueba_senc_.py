"""
Python model "prueba_senc_.py"
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
    'time': 'time',
    'Evaporación': 'evaporación',
    'Flujo río': 'flujo_río',
    'Lago': 'lago',
    'Lluvia': 'lluvia',
    'Aleatorio': 'aleatorio',
    'Nivel lago inicial': 'nivel_lago_inicial'
}

__pysd_version__ = "0.9.0"


@cache('step')
def evaporación():
    """
    Real Name: Evaporación
    Original Eqn: 0.1*Lago
    Units: m3/mes
    Limits: (0.0, None)
    Type: component

    La evaporación del lago, fija al 10%.
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

    El flujo de agua en el río.
    """
    return lluvia()


@cache('run')
def lluvia():
    """
    Real Name: Lluvia
    Original Eqn: 10
    Units: m3/mes
    Limits: (0.0, None)
    Type: constant

    La cantidad de lluvia que cae por mes.
    """
    return 10


@cache('run')
def aleatorio():
    """
    Real Name: Aleatorio
    Original Eqn: 0
    Units: Sdmn
    Limits: (0.0, 1.0)
    Type: constant

    Un variable aleatorio que debe provenir del modelo BP.
    """
    return 0


@cache('run')
def nivel_lago_inicial():
    """
    Real Name: Nivel lago inicial
    Original Eqn: 1500
    Units: m3
    Limits: (0.0, None)
    Type: constant

    La cantidad inicial de agua en el lago.
    """
    return 1500


@cache('step')
def lago():
    """
    Real Name: Lago
    Original Eqn: Flujo río - Evaporación
    Units: m3
    Limits: (0.0, None)
    Type: component

    La cantidad de agua en el lago.
    """
    return integ_lago()


integ_lago = functions.Integ(lambda: flujo_río() - evaporación(), lambda: nivel_lago_inicial())


@cache('run')
def initial_time():
    """
    Real Name: INITIAL TIME
    Original Eqn: 0
    Units: mes
    Limits: None
    Type: constant

    The initial time for the simulation.
    """
    return 0


@cache('run')
def final_time():
    """
    Real Name: FINAL TIME
    Original Eqn: 0
    Units: mes
    Limits: None
    Type: constant

    The final time for the simulation.
    """
    return 200


@cache('run')
def time_step():
    """
    Real Name: TIME STEP
    Original Eqn: 1
    Units: mes
    Limits: None
    Type: constant

    The time step for the simulation.
    """
    return 1


@cache('run')
def saveper():
    """
    Real Name: SAVEPER
    Original Eqn: 1
    Units: mes
    Limits: None
    Type: constant

    The time step for the simulation.
    """
    return time_step()
