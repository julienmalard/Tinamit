import asyncio


class Simulación(object):
    async def incr(símismo):
        raise NotImplementedError


class SimulConectado(Simulación):
    def correr(símismo):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(símismo.incr())
        loop.close()

    async def incr(símismo):
        await asyncio.gather(*[m.incr() for m in símismo.modelos])


class SimulEnchufes(Simulación):
    def __init__(símismo):
        símismo.proceso = asyncio.run(asyncio.create_subprocess_exec(
            símismo.comanda, símismo.args, cwd=símismo.directorio
        ))
    async def incr(símismo):
        
        await símismo.proceso.wait()

