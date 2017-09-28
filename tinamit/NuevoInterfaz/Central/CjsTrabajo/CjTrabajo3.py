from Dibba import Caja, Botón, BotónImg, Anim, IngrNúm, IngrTexto
from ...Control import Control


CjTrabajo3 = Caja('Simulación')

IngrTFinal = IngrNúm('Tiempo final')
IngrPaso = IngrNúm('Paso')
IngrNombreSimul = IngrNúm('Nombre de la simulación')

CjIngresos = Caja()
CjIngresos.agregar([IngrTFinal, IngrPaso, IngrNombreSimul])

CjTrabajo3.agregar(CjIngresos)


BtSimular = Botón('Simular', acción=Control.simular, paralelo=True,
                  args_acción={
                      'paso': IngrPaso,
                      'tiempo_final': IngrTFinal,
                      'nombre_corrida': IngrNombreSimul
                  })

CjSimulando = Caja()
AnimSimul = Anim('Simulando')
BtCancelar = BotónImg('BtBorrarItema_norm.png', img_sel='BtBorrarItema_sel.png', ayuda='Cancelar la simulación',
                      acción=BtSimular.parar_acción)

CjSimulando.agregar(AnimSimul, BtCancelar)
CjSimulando.esconder()

CjTrabajo3.agregar(BtSimular)
CjTrabajo3.agregar(CjSimulando)
