from dibba import Página, Caja

from .Cabeza import Cabeza
from .Recuadro import CjRecuadro
from .Trabajo import CjTrabajo

PáginaCentral = Página()
PáginaCentral.agregar(Cabeza)

CjPrincipal = Caja(tamaño=(0, -Cabeza.tmñ[0]), tmñ_rel=(1, 1))
CjPrincipal.agregar(CjRecuadro, pos='horizontal')
CjPrincipal.agregar(CjTrabajo, pos='horizontal')

for i, caja in enumerate(CjTrabajo.cajas):
    botón = CjRecuadro.botones[i]
    botón.estab_comanda(CjTrabajo.traer(caja))
    caja.estab_acción('bloquear', botón.bloquear())
    caja.estab_acción('desbloquear', botón.desbloquear())

PáginaCentral.agregar(CjPrincipal)
