"""
Python model "Prueba dll.py"
Translated using PySD version 0.9.0
"""
from __future__ import division

import numpy as np

from pysd.py_backend import functions
from pysd.py_backend.functions import cache

_subscript_dict = {}

_namespace = {
    'TIME': 'time',
    'Time': 'time',
    'Deforestación': 'deforestación',
    'Bosques': 'bosques',
    'Regeneración': 'regeneración',
    'Máx bosques': 'máx_bosques',
    'Río': 'río',
    'Evaporación': 'evaporación',
    'Agua en lago': 'agua_en_lago',
    'Lluvia': 'lluvia',
    'Pesca': 'pesca',
    'FINAL TIME': 'final_time',
    'INITIAL TIME': 'initial_time',
    'SAVEPER': 'saveper',
    'TIME STEP': 'time_step'
}

__pysd_version__ = "0.9.0"


@cache('step')
def deforestación():
    """
    Real Name: Deforestación
    Original Eqn: MIN(Bosques, (1-Pesca)*10000)
    Units: m*m/mes
    Limits: (None, None)
    Type: component


    """
    return np.minimum(bosques(), (1 - pesca()) * 10000)


@cache('step')
def bosques():
    """
    Real Name: Bosques
    Original Eqn: INTEG ( Regeneración-Deforestación, Máx bosques )
    Units: m*m
    Limits: (None, None)
    Type: component

    Cantidad de cobertura forestal.
    """
    return integ_bosques()


@cache('step')
def regeneración():
    """
    Real Name: Regeneración
    Original Eqn: 0.01 *Bosques * (Máx bosques-Bosques)/Máx bosques
    Units: 
    Limits: (None, None)
    Type: component

    La regeneración es una ecuación logística.
    """
    return 0.01 * bosques() * (máx_bosques() - bosques()) / máx_bosques()


@cache('run')
def máx_bosques():
    """
    Real Name: Máx bosques
    Original Eqn: 1e+006
    Units: 
    Limits: (None, None)
    Type: constant

    La cantidad máxima de bosques.
    """
    return 1e+006


@cache('step')
def río():
    """
    Real Name: Río
    Original Eqn: Lluvia
    Units: m*m*m/mes
    Limits: (None, None)
    Type: component


    """
    return lluvia()


@cache('step')
def evaporación():
    """
    Real Name: Evaporación
    Original Eqn: Agua en lago*0.1
    Units: m*m*m/mes
    Limits: (None, None)
    Type: component


    """
    return agua_en_lago() * 0.1


@cache('step')
def agua_en_lago():
    """
    Real Name: Agua en lago
    Original Eqn: INTEG ( Río-Evaporación, 10)
    Units: m*m*m
    Limits: (None, None)
    Type: component


    """
    return integ_agua_en_lago()


@cache('step')
def lluvia():
    """
    Real Name: Lluvia
    Original Eqn: GAME ( 2)
    Units: m*m*m/mes
    Limits: (None, None)
    Type: component


    """
    return (2)


@cache('step')
def pesca():
    """
    Real Name: Pesca
    Original Eqn: WITH LOOKUP ( Agua en lago*3, ([(0,0)-(20,1)],(0,0),(4.77064,0.0921053),(8.99083,0.214912),(10.8257,0.359649),(11.9266\ ,0.54386),(12.2936,0.692982),(13.8226,0.815789),(16.4526,0.942982),(20,1) ))
    Units: Dmnl
    Limits: (None, None)
    Type: component

    Porcentaje de necesidades que se pueden cumplir por la pesca.
    """
    return functions.lookup(
        agua_en_lago() * 3, [0, 4.77064, 8.99083, 10.8257, 11.9266, 12.2936, 13.8226, 16.4526, 20],
        [0, 0.0921053, 0.214912, 0.359649, 0.54386, 0.692982, 0.815789, 0.942982, 1])


@cache('run')
def final_time():
    """
    Real Name: FINAL TIME
    Original Eqn: 120
    Units: Meses
    Limits: (None, None)
    Type: constant

    The final time for the simulation.
    """
    return 120


@cache('run')
def initial_time():
    """
    Real Name: INITIAL TIME
    Original Eqn: 0
    Units: Meses
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
    Units: Meses
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
    Units: Meses
    Limits: (0.0, None)
    Type: constant

    The time step for the simulation.
    """
    return 1


integ_bosques = functions.Integ(lambda: regeneración() - deforestación(), lambda: máx_bosques())

integ_agua_en_lago = functions.Integ(lambda: río() - evaporación(), lambda: 10)
