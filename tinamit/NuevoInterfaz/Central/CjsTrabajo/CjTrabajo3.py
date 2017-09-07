from Dibba import Caja, Botón, BotónImg, Anim, IngrNúm, IngrTexto

CjTrabajo3 = Caja('Simulación')

BtSimular = Botón('Simular')

CjSimulando = Caja()
AnimSimul = Anim('Simulando')
BtCancelar = BotónImg('BtBorrarItema_norm.png', img_sel='BtBorrarItema_sel.png', info='Cancelar la simulación')

CjSimulando.agregar(AnimSimul, BtCancelar)
CjSimulando.esconder()

CjTrabajo3.agregar(BtSimular)
CjTrabajo3.agregar(CjSimulando)

IngrTFinal = IngrNúm('Tiempo final')
IngrPaso = IngrNúm('Paso')
IngrNombreSimul = IngrNúm('Nombre de la simulación')

CjIngresos = Caja()
CjIngresos.agregar([IngrTFinal, IngrPaso, IngrNombreSimul])

CjTrabajo3.agregar(CjIngresos)
