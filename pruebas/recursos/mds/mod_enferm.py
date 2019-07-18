"""
Python model "mod_enferm.py"
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
    'Individuos Infectados': 'individuos_infectados',
    'Individuos Resistentes': 'individuos_resistentes',
    'población total': 'población_total',
    'Recuperación': 'recuperación',
    'taza de recuperación': 'taza_de_recuperación',
    'fracción población infectada': 'fracción_población_infectada',
    'taza de infección': 'taza_de_infección',
    'infecciones': 'infecciones',
    'taza de contacto': 'taza_de_contacto',
    'FINAL TIME': 'final_time',
    'número inicial infectado': 'número_inicial_infectado',
    'INITIAL TIME': 'initial_time',
    'contactos con suceptibles': 'contactos_con_suceptibles',
    'Individuos Suceptibles': 'individuos_suceptibles',
    'contactos entre suceptibles e infectados': 'contactos_entre_suceptibles_e_infectados',
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
def individuos_infectados():
    """
    Real Name: b'Individuos Infectados'
    Original Eqn: b'INTEG ( infecciones-Recuperaci\\xf3n, n\\xfamero inicial infectado)'
    Units: b'Person'
    Limits: (None, None)
    Type: component

    b''
    """
    return _integ_individuos_infectados()


@cache('step')
def individuos_resistentes():
    """
    Real Name: b'Individuos Resistentes'
    Original Eqn: b'INTEG ( Recuperaci\\xf3n, 0)'
    Units: b''
    Limits: (None, None)
    Type: component

    b'0'
    """
    return _integ_individuos_resistentes()


@cache('step')
def población_total():
    """
    Real Name: b'poblaci\\xf3n total'
    Original Eqn: b'Individuos Suceptibles + Individuos Infectados + Individuos Resistentes'
    Units: b'Person'
    Limits: (None, None)
    Type: component

    b''
    """
    return individuos_suceptibles() + individuos_infectados() + individuos_resistentes()


@cache('step')
def recuperación():
    """
    Real Name: b'Recuperaci\\xf3n'
    Original Eqn: b'Individuos Infectados*taza de recuperaci\\xf3n'
    Units: b''
    Limits: (None, None)
    Type: component

    b''
    """
    return individuos_infectados() * taza_de_recuperación()


@cache('run')
def taza_de_recuperación():
    """
    Real Name: b'taza de recuperaci\\xf3n'
    Original Eqn: b'0.05'
    Units: b''
    Limits: (0.0, 1.0)
    Type: constant

    b''
    """
    return 0.05


@cache('step')
def fracción_población_infectada():
    """
    Real Name: b'fracci\\xf3n poblaci\\xf3n infectada'
    Original Eqn: b'Individuos Infectados/poblaci\\xf3n total'
    Units: b'Dmnl'
    Limits: (None, None)
    Type: component

    b''
    """
    return individuos_infectados() / población_total()


@cache('run')
def taza_de_infección():
    """
    Real Name: b'taza de infecci\\xf3n'
    Original Eqn: b'0.005'
    Units: b'Dmnl'
    Limits: (0.0, 0.01)
    Type: constant

    b''
    """
    return 0.005


@cache('step')
def infecciones():
    """
    Real Name: b'infecciones'
    Original Eqn: b'MIN(contactos entre suceptibles e infectados * taza de infecci\\xf3n, Individuos Suceptibles)'
    Units: b'Person/Year'
    Limits: (None, None)
    Type: component

    b''
    """
    return np.minimum(contactos_entre_suceptibles_e_infectados() * taza_de_infección(),
                      individuos_suceptibles())


@cache('run')
def taza_de_contacto():
    """
    Real Name: b'taza de contacto'
    Original Eqn: b'100'
    Units: b'1/Year'
    Limits: (0.0, 500.0)
    Type: constant

    b''
    """
    return 100


@cache('run')
def final_time():
    """
    Real Name: b'FINAL TIME'
    Original Eqn: b'2010'
    Units: b'Year'
    Limits: (None, None)
    Type: constant

    b'The final time for the simulation.'
    """
    return 2010


@cache('run')
def número_inicial_infectado():
    """
    Real Name: b'n\\xfamero inicial infectado'
    Original Eqn: b'10'
    Units: b'Person'
    Limits: (0.0, 100.0)
    Type: constant

    b''
    """
    return 10


@cache('run')
def initial_time():
    """
    Real Name: b'INITIAL TIME'
    Original Eqn: b'1960'
    Units: b'Year'
    Limits: (None, None)
    Type: constant

    b'The initial time for the simulation.'
    """
    return 1960


@cache('step')
def contactos_con_suceptibles():
    """
    Real Name: b'contactos con suceptibles'
    Original Eqn: b'Individuos Suceptibles * taza de contacto'
    Units: b'Person/Year'
    Limits: (None, None)
    Type: component

    b''
    """
    return individuos_suceptibles() * taza_de_contacto()


@cache('step')
def individuos_suceptibles():
    """
    Real Name: b'Individuos Suceptibles'
    Original Eqn: b'INTEG ( -infecciones, 1000)'
    Units: b'Person'
    Limits: (None, None)
    Type: component

    b''
    """
    return _integ_individuos_suceptibles()


@cache('step')
def contactos_entre_suceptibles_e_infectados():
    """
    Real Name: b'contactos entre suceptibles e infectados'
    Original Eqn: b'contactos con suceptibles * fracci\\xf3n poblaci\\xf3n infectada'
    Units: b'Person/Year'
    Limits: (None, None)
    Type: component

    b''
    """
    return contactos_con_suceptibles() * fracción_población_infectada()


@cache('step')
def saveper():
    """
    Real Name: b'SAVEPER'
    Original Eqn: b'TIME STEP'
    Units: b'Year'
    Limits: (None, None)
    Type: component

    b'The frequency with which data are saved.'
    """
    return time_step()


@cache('run')
def time_step():
    """
    Real Name: b'TIME STEP'
    Original Eqn: b'0.5'
    Units: b'Year'
    Limits: (None, None)
    Type: constant

    b'The time step for the simulation.'
    """
    return 0.5


_integ_individuos_infectados = functions.Integ(lambda: infecciones() - recuperación(),
                                               lambda: número_inicial_infectado())

_integ_individuos_resistentes = functions.Integ(lambda: recuperación(), lambda: 0)

_integ_individuos_suceptibles = functions.Integ(lambda: -infecciones(), lambda: 1000)
