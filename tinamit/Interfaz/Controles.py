import tkinter as tk

from . import Arte as Art
from . import Botones as Bt
from . import ControlesGenéricos as CtrG
from . import Formatos as Fm
from .Formatos import gen_formato as gf


# Caja lenguas
class CajaAñadirLeng(tk.Frame):
    def __init__(símismo, pariente, caja):
        super().__init__(caja, **Fm.formato_cajas)
        Bt.BotónImagen(símismo, comanda=símismo.acción_bt_plus, formato=Fm.formato_botones,
                       img_norm=Art.imagen('BtPlus_norm'), img_sel=Art.imagen('BtPlus_sel'),
                       ubicación=gf(Fm.ubic_CjCamposAñLeng), tipo_ubic='pack')
        símismo.pariente = pariente

        símismo.cj_campos = cj_campos = tk.Frame(símismo, **Fm.formato_cajas)
        símismo.ingr_leng = CtrG.IngrTexto(cj_campos, nombre=None,
                                           ubicación=gf(Fm.ubic_CjCamposAñLeng), tipo_ubic='pack')

        Bt.BotónImagen(cj_campos, comanda=símismo.acción_bt_guardar, formato=Fm.formato_botones,
                       img_norm=Art.imagen('BtMarca_norm'), img_sel=Art.imagen('BtMarca_sel'),
                       ubicación=gf(Fm.ubic_BtsAñadirLeng), tipo_ubic='pack')

        símismo.IzqDer = Bt.BotónAltern(cj_campos, formato=Fm.formato_botones,
                                        img_1=Art.imagen('BtEscribIzqDer'), img_2=Art.imagen('BtEscribDerIzq'),
                                        ubicación=gf(Fm.ubic_BtsAñadirLeng), tipo_ubic='pack')

        símismo.mostrando = False

    def acción_bt_plus(símismo):
        if not símismo.mostrando:
            símismo.cj_campos.pack(**gf(Fm.ubic_CjCamposAñLeng))
        else:
            símismo.cj_campos.pack_forget()

        símismo.mostrando = not símismo.mostrando

    def acción_bt_guardar(símismo):
        nombre = símismo.ingr_leng.val
        if nombre is not None and len(nombre):
            izqder = símismo.IzqDer.val
            símismo.pariente.añadir_lengua(nombre=nombre, izqder=izqder)
        símismo.ingr_leng.borrar()


class ItemaLeng(CtrG.Itema):
    def __init__(símismo, pariente, lista, nombre, lengua, estado, utilizando=False, utilizable=True, borrable=True):
        super().__init__(lista_itemas=lista)
        símismo.nombre = nombre
        símismo.lengua = lengua

        cj_bt_utilizar = tk.Frame(símismo, **Fm.formato_secciones_itemas)
        cj_central = tk.Frame(símismo, **Fm.formato_secciones_itemas)
        cj_bts = tk.Frame(símismo, **Fm.formato_secciones_itemas)

        if utilizando:
            img_norm = Art.imagen('BtCasilla_sel')
        else:
            img_norm = Art.imagen('BtCasilla_norm')
        bt_utilizar = Bt.BotónImagen(cj_bt_utilizar, comanda=lambda x=nombre: pariente.utilizar(x),
                                     formato=Fm.formato_botones,
                                     img_norm=img_norm,
                                     img_sel=Art.imagen('BtCasilla_sel'),
                                     img_bloq=Art.imagen('BtCasilla_bloq'),
                                     ubicación=gf(Fm.ubic_IzqLstLeng), tipo_ubic='pack')
        if not utilizable:
            bt_utilizar.bloquear()

        if 0 < estado < 1:
            ancho = Fm.ancho_etiq_nombre_estr
        else:
            ancho = Fm.ancho_etiq_nombre_largo

        cj_etiq_nombre_leng = tk.Frame(cj_central, width=ancho, **Fm.formato_cj_etiq_nombre_leng)
        cj_etiq_nombre_leng.pack_propagate(0)
        símismo.etiq_nombre = tk.Label(cj_etiq_nombre_leng, text=símismo.nombre,
                                       font=Fm.fuente_etiq_itema_norm, **Fm.formato_etiq_nombre_leng)
        símismo.etiq_nombre.pack(**gf(Fm.ubic_etiq_nombre_leng))
        cj_etiq_nombre_leng.pack(**gf(Fm.ubic_EtiqNombreLstLeng))

        if 0 < estado < 1:
            color_barra = Art.inter_color(Fm.colores_prog_leng, p=estado, tipo='hex')
            altura, ancho = Fm.dim_barra_prog_leng
            barra_prog = tk.Canvas(cj_central, width=ancho, height=altura, background=Fm.col_fondo,
                                   highlightthickness=1, highlightbackground=color_barra)
            barra_prog.create_rectangle(0, 0, round(ancho*estado), altura, fill=color_barra, outline=color_barra)
            barra_prog.pack(gf(Fm.ubic_DerLstLeng))

        símismo.bt_editar = Bt.BotónImagen(cj_bts, comanda=lambda x=nombre: pariente.editar(x),
                                           formato=Fm.formato_botones,
                                           img_norm=Art.imagen('BtEditarItema_norm'),
                                           img_sel=Art.imagen('BtEditarItema_sel'),
                                           ubicación=gf(Fm.ubic_IzqLstLeng), tipo_ubic='pack')
        símismo.bt_borrar = Bt.BotónImagen(cj_bts, comanda=lambda x=nombre: pariente.confirmar_borrar(x),
                                           formato=Fm.formato_botones,
                                           img_norm=Art.imagen('BtBorrarItema_norm'),
                                           img_sel=Art.imagen('BtBorrarItema_sel'),
                                           img_bloq=Art.imagen('BtBorrarItema_bloq'),
                                           ubicación=gf(Fm.ubic_IzqLstLeng), tipo_ubic='pack')
        if not borrable:
            símismo.bt_borrar.bloquear()

        cj_bt_utilizar.pack(**gf(Fm.ubic_IzqLstLeng))
        cj_central.pack(**gf(Fm.ubic_CjCentLstLeng))
        cj_bts.pack(**gf(Fm.ubic_BtsAñadirLeng))


class CajaEditLeng(tk.Frame):
    def __init__(símismo, pariente, apli, leng_base, dic_leng_base, leng_edit, dic_leng_edit):
        super().__init__(pariente, **Fm.formato_CjEditLeng)
        símismo.pariente = pariente
        símismo.apli = apli
        símismo.dic_leng_edit = dic_leng_edit

        cj_cbz = tk.Frame(símismo, **Fm.formato_cajas)

        etiq_cbz = tk.Label(cj_cbz, text=apli.Trads['Traducciones'], **Fm.formato_EtiqCbzEditLeng)

        cj_nombres_lengs = tk.Frame(cj_cbz, **Fm.formato_cajas)
        etiq_base = tk.Label(cj_nombres_lengs, text=leng_base, **Fm.formato_EtiqLengBase)
        etiq_edit = tk.Label(cj_nombres_lengs, text=leng_edit, **Fm.formato_EtiqLengEdit)

        etiq_base.pack(**gf(Fm.ubic_EtiqLengs))
        etiq_edit.pack(**gf(Fm.ubic_EtiqLengs))

        lín_hor_1 = tk.Frame(símismo, **Fm.formato_LínHor)

        etiq_cbz.pack(**gf(Fm.ubic_CjNomEditLeng))
        cj_nombres_lengs.pack(**gf(Fm.ubic_CjNomEditLeng))

        cj_lista = tk.Frame(símismo, **Fm.formato_cajas)
        lista = CtrG.ListaItemas(cj_lista, formato_cj=Fm.formato_LstEditLeng,
                                 ubicación=gf(Fm.ubic_LstEditLeng), tipo_ubic='place')
        símismo.itemas = []
        for ll, texto in sorted(dic_leng_base['Trads'].items()):
            if ll in dic_leng_edit['Trads'].keys():
                texto_trad = dic_leng_edit['Trads'][ll]
            else:
                texto_trad = ''
            nuevo_itema = ItemaEditTrad(lista=lista, llave=ll, texto_origin=texto, texto_trad=texto_trad)
            símismo.itemas.append(nuevo_itema)

        lín_hor_2 = tk.Frame(símismo, **Fm.formato_LínHor)

        cj_bts = tk.Frame(símismo, **Fm.formato_cajas)
        símismo.bt_guardar = Bt.BotónTexto(cj_bts, texto=apli.Trads['Guardar'],
                                           formato_norm=Fm.formato_BtGuardar_norm,
                                           formato_sel=Fm.formato_BtGuardar_sel,
                                           ubicación=gf(Fm.ubic_BtsGrupo), tipo_ubic='pack',
                                           comanda=símismo.guardar)

        símismo.bt_no_guardar = Bt.BotónTexto(cj_bts, texto=apli.Trads['NoGuardar'],
                                              formato_norm=Fm.formato_BtBorrar_norm,
                                              formato_sel=Fm.formato_BtBorrar_sel,
                                              ubicación=gf(Fm.ubic_BtsGrupo), tipo_ubic='pack',
                                              comanda=símismo.cerrar)

        cj_cbz.pack(**gf(Fm.ubic_CjCbzCjEditLeng))
        lín_hor_1.pack(**gf(Fm.ubic_LínHorCjEditLeng))
        cj_lista.pack(**gf(Fm.ubic_CjCentrCjEditLeng))
        lín_hor_2.pack(**gf(Fm.ubic_LínHorCjEditLeng))
        cj_bts.pack(**gf(Fm.ubic_CjBtsCjEditLeng))
        símismo.place(**gf(Fm.ubic_CjEditLeng))

    def guardar(símismo):
        for itema in símismo.itemas:
            símismo.dic_leng_edit['Trads'][itema.llave] = itema.sacar_trad()
        símismo.pariente.DicLeng.guardar()
        símismo.pariente.refrescar()
        símismo.cerrar()

    def cerrar(símismo):
        símismo.destroy()


class ItemaEditTrad(CtrG.Itema):
    def __init__(símismo, lista, llave, texto_origin, texto_trad):
        super().__init__(lista_itemas=lista)
        símismo.llave = llave
        cj_tx_orig = tk.Frame(símismo, **Fm.formato_CjLengTxOrig)
        etiq_tx_orig = tk.Label(cj_tx_orig, text=texto_origin, **Fm.formato_EtiqLengTxOrig)
        etiq_tx_orig.pack(side='top')

        cj_trad = tk.Frame(símismo, **Fm.formato_cajas)
        símismo.campo_texto = tk.Text(cj_trad, **Fm.formato_CampoTexto)
        símismo.campo_texto.insert('end', texto_trad)

        símismo.campo_texto.pack()
        cj_tx_orig.pack(**gf(Fm.ubic_CjTxOrigTradLeng))

        cj_trad.pack(**gf(Fm.ubic_EtiqLengs))

    def sacar_trad(símismo):
        return símismo.campo_texto.get('1.0', 'end').replace('\n', '')


class CajaAviso(tk.Frame):
    def __init__(símismo, apli, texto):
        super().__init__(**Fm.formato_CajaAvisoReinic)

        etiq = tk.Label(símismo, text=texto, **Fm.formato_EtiqLengReinic)
        etiq.pack(**gf(Fm.ubic_etiq_aviso_inic_leng))

        símismo.bt = Bt.BotónTexto(símismo, texto=apli.Trads['Entendido'],
                                   formato_norm=Fm.formato_BtAvisoInic_norm,
                                   formato_sel=Fm.formato_BtAvisoInic_sel,
                                   ubicación=gf(Fm.ubic_bt_aviso_inic_leng), tipo_ubic='pack',
                                   comanda=símismo.destroy)

        símismo.place(**gf(Fm.ubic_CjAvisoReinic))


class CajaAvisoBorrar(tk.Frame):
    def __init__(símismo, apli, nombre, acción):
        super().__init__(**Fm.formato_CajaAvisoReinic)
        símismo.acción = acción
        símismo.nombre = nombre

        etiq = tk.Label(símismo, text=apli.Trads["AvisoBorrarLeng"] % nombre, **Fm.formato_EtiqLengBorrar)
        etiq.pack(**gf(Fm.ubic_etiq_aviso_borrar_leng))

        cj_bts = tk.Frame(símismo, **Fm.formato_cajas)
        símismo.bt_no = Bt.BotónTexto(cj_bts, texto=apli.Trads['No'],
                                      formato_norm=Fm.formato_BtGuardar_norm,
                                      formato_sel=Fm.formato_BtGuardar_sel,
                                      ubicación=gf(Fm.ubic_bts_aviso_borrar_leng), tipo_ubic='pack',
                                      comanda=símismo.destroy)

        símismo.bt_sí = Bt.BotónTexto(cj_bts, texto=apli.Trads['Sí'],
                                      formato_norm=Fm.formato_BtBorrar_norm,
                                      formato_sel=Fm.formato_BtBorrar_sel,
                                      ubicación=gf(Fm.ubic_bts_aviso_borrar_leng), tipo_ubic='pack',
                                      comanda=símismo.acción_borrar)

        cj_bts.pack(**gf(Fm.ubic_cj_bts_aviso_borrar_leng))

        símismo.place(**gf(Fm.ubic_CjAvisoReinic))

    def acción_borrar(símismo):
        símismo.acción(símismo.nombre)
        símismo.destroy()


# Subcaja 2.1
class GrpCtrlsConex(CtrG.GrupoControles):
    def __init__(símismo, pariente, apli, controles, lista, bt_guardar, bt_borrar, comanda):
        super().__init__(controles, constructor_itema=ItemaConexión, lista=lista,
                         bt_guardar=bt_guardar, bt_borrar=bt_borrar, comanda=comanda)
        símismo.apli = apli
        símismo.pariente = pariente

    def verificar_completo(símismo):
        campos_necesarios = ['var_mds', 'mds_fuente', 'conv', 'var_bf']
        completos = [símismo.controles[x].val is not None and símismo.controles[x].val is not ''
                     for x in campos_necesarios]
        if min(completos):
            return True
        else:
            return False

    def recrear_objeto(símismo):
        for ll, control in símismo.controles.items():
            símismo.receta[ll] = control.val


class ListaConexiónes(CtrG.ListaEditable):
    def __init__(símismo, pariente, apli, ubicación, tipo_ubic):
        super().__init__(pariente, ubicación=ubicación, tipo_ubic=tipo_ubic)

        símismo.pariente = pariente
        nombres_cols = [apli.Trads['VariableMDS'], '', apli.Trads['VariableBiofísico']]
        anchuras = Fm.anchos_cols_listacon
        símismo.gen_encbz(nombres_cols, anchuras)

    def añadir(símismo, itema):
        super().añadir(itema)
        símismo.pariente.verificar_completo()

    def quitar(símismo, itema):
        super().quitar(itema)
        símismo.pariente.verificar_completo()


class ItemaConexión(CtrG.ItemaEditable):
    def __init__(símismo, grupo_control, lista_itemas, receta=None, creando_manual=True):
        símismo.pariente = grupo_control.pariente
        if receta is not None:
            símismo.receta = receta

        super().__init__(grupo_control=grupo_control, lista_itemas=lista_itemas, creando_manual=creando_manual)

        símismo.cj_cols = cj_cols = tk.Frame(símismo, **Fm.formato_cajas)
        cj_var_mds = tk.Frame(cj_cols, **Fm.formato_secciones_itemas)
        cj_conv = tk.Frame(cj_cols, **Fm.formato_secciones_itemas)
        cj_var_bf = tk.Frame(cj_cols, **Fm.formato_secciones_itemas)

        símismo.flecha = {'cola_izq': Art.imagen('FlchConex_colaizq'),
                          'cola_der': Art.imagen('FlchConex_colader'),
                          'cbz_izq': Art.imagen('FlchConex_cbzizq'),
                          'cbz_der': Art.imagen('FlchConex_cbzder')}

        símismo.etiq_varMDS = tk.Label(cj_var_mds, **Fm.formato_texto_itemas)
        símismo.etiq_izqflecha = tk.Label(cj_conv, **Fm.formato_etiq)
        símismo.etiq_conversión = tk.Label(cj_conv, **Fm.formato_etiq_conversión)
        símismo.etiq_derflecha = tk.Label(cj_conv, **Fm.formato_etiq)
        símismo.etiq_varBf = tk.Label(cj_var_bf, **Fm.formato_texto_itemas)

        símismo.etiquetas = [símismo.etiq_varMDS, símismo.etiq_izqflecha, símismo.etiq_conversión,
                             símismo.etiq_derflecha, símismo.etiq_varBf]
        símismo.columnas = [cj_var_mds, cj_conv, cj_var_bf]
        for etiq in símismo.etiquetas:
            etiq.pack(**gf(Fm.ubic_EtiqItemas))

        símismo.estab_columnas(anchuras=Fm.anchos_cols_listacon)

        símismo.actualizar()

    def actualizar(símismo):
        try:
            símismo.etiq_varMDS.config(text=símismo.receta['vars']['mds'])
            símismo.etiq_varBf.config(text=símismo.receta['vars']['bf'])
            modelo_fuente = símismo.receta['modelo_fuente']
        except KeyError:
            símismo.etiq_varMDS.config(text=símismo.receta['var_mds'])
            símismo.etiq_varBf.config(text=símismo.receta['var_bf'])
            if símismo.receta['mds_fuente']:
                modelo_fuente = 'mds'
            else:
                modelo_fuente = 'bf'

        símismo.etiq_conversión.config(text='X %s' % símismo.receta['conv'])

        if modelo_fuente == 'mds':
            if Fm.IzqaDerech:
                símismo.etiq_izqflecha.config(image=símismo.flecha['cola_izq'])
                símismo.etiq_derflecha.config(image=símismo.flecha['cbz_der'])
            else:
                símismo.etiq_izqflecha.config(image=símismo.flecha['cola_der'])
                símismo.etiq_derflecha.config(image=símismo.flecha['cbz_izq'])
        else:
            if Fm.IzqaDerech:
                símismo.etiq_izqflecha.config(image=símismo.flecha['cbz_izq'])
                símismo.etiq_derflecha.config(image=símismo.flecha['cola_der'])
            else:
                símismo.etiq_izqflecha.config(image=símismo.flecha['cbz_der'])
                símismo.etiq_derflecha.config(image=símismo.flecha['cola_izq'])

    def resaltar(símismo):
        for etiq in símismo.etiquetas:
            if etiq is not símismo.etiq_conversión:
                etiq.config(font=gf(Fm.fuente_etiq_itema_sel))

    def desresaltar(símismo):
        for etiq in símismo.etiquetas.copy():
            if etiq is not símismo.etiq_conversión:
                etiq.config(font=gf(Fm.fuente_etiq_itema_norm))

    def añadir(símismo):
        símismo.pariente.añadir_conexión(símismo.receta)
        super().añadir()

    def quitar(símismo):
        print(símismo.receta)
        símismo.pariente.quitar_conexión(símismo.receta)
        super().quitar()
