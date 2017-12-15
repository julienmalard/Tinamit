from Dibba import Caja, Botón, ItemaLista, Lista, CtrlLista, Texto, Imagen, IngrMenú, IngrNúm, BtOpción

CjTrabajo2 = Caja('Conexión de variables')


class ItemaListaConex(ItemaLista):
    def __init__(símismo, info):

        símismo.info = info

        símismo.bt_borrar = Botón()
        símismo.bt_editar = Botón()

        cj_bts = Caja()
        cj_bts.agregar([símismo.bt_borrar, símismo.bt_editar])

        símismo.var_mds = var_mds = Texto()
        símismo.unid_mds = unid_mds = Texto()
        símismo.flecha_izq = flecha_izq = Imagen()
        símismo.flecha_der = flecha_der = Imagen()
        símismo.conv = conv = Texto()
        símismo.cj_flecha = cj_flecha = Caja([flecha_izq, conv, flecha_der])
        símismo.unid_bf = unid_bf = Texto()
        símismo.var_bf = var_bf = Texto()

        super().__init__(anchura_cols=[], cols=[var_mds, unid_mds, cj_flecha, unid_bf, var_bf])

    def dibujar(símismo):
        info = símismo.info
        símismo.var_mds.poner_texto(info['mds'])
        símismo.var_bf.poner_texto(info['bf'])
        if info['mds_fuente']:
            símismo.flecha_izq.poner_img('FlchConez_cola.png', )
            símismo.flecha_der.poner_img('FlchConex_cbz.png')
        else:
            símismo.flecha_izq.poner_img('FlchConex_cbz.png', girar=180)
            símismo.flecha_der.poner_img('FlchConez_cola.png', girar=180)

        símismo.conv.poner_texto(info['conv'])
        símismo.unid_mds.ponder_texto(info['unid_mds'])
        símismo.unid_bf.ponder_texto(info['unid_bf'])


ListaConex = Lista(anchura_cols=[], cabeza=['Var MDS', 'Dirección', 'Var BF', None], itemas=ItemaListaConex)

BtGuardar = Botón('Guardar', ayuda='Guardar la conexión')
BtNoGuardar = Botón('No guardar', ayuda='Borrar los cambios')
BtBorrar = Botón('Borrar', ayuda='Borrar esta conexión')

IngrVarMDS = IngrMenú()
IngVarBF = IngrMenú()
IngrConv = IngrNúm('X', ayuda='Factor de conversión entre unidades')
Dir = BtOpción()

Ctrls = CtrlLista(lista=ListaConex, bt_agregar=BtGuardar, bt_noguardar=BtNoGuardar, bt_borrar=BtBorrar,
                  ctrls={
                      'mds': IngrVarMDS,
                      'bf': IngVarBF,
                      'conv': IngrConv,
                      'mds_fuente': Dir
                  },
                  )

CjTrabajo2.agregar(ListaConex)
