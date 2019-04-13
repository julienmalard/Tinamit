from pint import UnitRegistry

regu = UnitRegistry()
C_ = regu.Quantity

from .trads import agregar_trad, agregar_sinónimos, trad_unid
