import asyncio
import json
import logging

import websockets


def cambiar(simul, pedida):
    for vr, vl in pedida:
        simul.estab_valor(vr, vl)


async def recibir(websocket, simul, contenido):
    datos = {vr: simul.obt_valor(vr) for vr in contenido}
    await websocket.send(json.dumps(datos, ensure_ascii=False))


async def incrementar(simul, contenido):
    if not simul.terminado:
        await simul.incr(contenido['n'])


async def finalizar(simul):
    await incrementar(simul)


async def cerrar(simul):
    await simul.cerrar()


async def servidor(websocket, path):

    # Recibir instrucciones de simulación
    espec = await websocket.recv()

    simul = gen_simul(espec)
    while True:
        mensaje = json.loads(await websocket.recv(), encoding='utf8')
        acción, contenido = mensaje['acción'], mensaje['contenido']

        if acción == "recibir":
            await recibir(websocket, simul, contenido)
        elif acción == "cambiar":
            await cambiar(simul, mensaje)
        elif acción == "avanzar":
            await incrementar(simul, contenido)
        elif acción == "finalizar":
            await finalizar(simul)
        elif acción == "cerrar":
            break
        else:
            logging.error("Acción no reconocida: {}", acción)

    await cerrar(simul)


def correr(dirección, puerto):
    start_server = websockets.serve(servidor(), dirección, puerto)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
