import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import sys
from SALib.sample import fast_sampler
from tinamit.Calib.SA_algorithms import soil_class
from tinamit.Calib import gaby_simulation as GS
from tinamit.Calib.SA_algorithms import parameters_sa as P
import json
from tinamit.Calib.SA_algorithms import soil_class as SC
from tinamit.Geog.Geog import Geografía
from enum import Enum
from scipy import optimize
from tinamit.Calib.SA_algorithms.Salib_SA import SA
from tinamit.Calib.SA_algorithms import fast
from scipy.stats import gamma
import scipy.stats as estad

dist = estad.gamma(a=2, loc=0, scale=10)
ptint(dist.pdf(1))
# 0.009048374180359597
print(dist.pdf(11))
# 0.036615819206788754