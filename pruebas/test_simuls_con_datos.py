import os
import unittest

import numpy as np
import numpy.testing as npt

from pruebas.recursos.BF.prueba_bf import ModeloPrueba

dir_act = os.path.split(__file__)[0]
arch_mds = os.path.join(dir_act, 'recursos/MDS/prueba_senc.mdl')

