from Dibba import PáginaTrads, Caja, InterfazTrads

PgTrads = PáginaTrads()

Cabeza = Caja(tamaño=(0, 70), tmñ_rel=(1, 0))

PgTrads.agregar(Cabeza)

CjPrincipal = InterfazTrads(tamaño=(0, -Cabeza.tmñ[0]), tmñ_rel=(1, 1))

PgTrads.agregar(CjPrincipal)
