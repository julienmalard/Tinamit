import tkinter as tk

from Interfaz import CajasGenéricas as CjG
from Interfaz import CajasSubEtapas as CjSE
from Interfaz import Controles as Ctrl
from Interfaz import ControlesGenéricos as CtrG
from Interfaz import Formatos as Fm, Botones as Bt, Arte as Art, Animaciones as Anim


class CajaIzquierda(object):
    def __init__(símismo, apli, pariente, imgs):

        símismo.caja = tk.Frame(pariente, **Fms.formato_cajas)
        # Crear las líneas de progreso y las cajas necesarias para contenerlas
        cj_líns_izq = tk.Frame(símismo.caja, **Fms.formato_cajas)
        símismo.líneas = {}
        for i in range(1, 5):
            símismo.líneas[str(i)] = tk.Canvas(cj_líns_izq, **Fms.formato_lín_bts)
            símismo.líneas[str(i)].col = Fms.color_bts[str(i)]

        # Crear la los botones de navigación y las cajas necesarias para contenerlos
        cj_bts_izq = tk.Frame(símismo.caja, **Fms.formato_cajas)
        símismo.bts = {}
        for i in range(1, 5):
            símismo.bts[str(i)] = Bts.BotónIzq(apli=apli, pariente=cj_bts_izq, lín=símismo.líneas[str(i)], núm=i,
                                               img=imgs['img_bt_%i' % i], img_bloc=imgs['img_bt_%i_bloc' % i],
                                               img_sel=imgs['img_bt_%i_sel' % i], **Fms.formato_bts_cent)

        for l in range(1, len(símismo.líneas) + 1):
            símismo.líneas[str(l)].pack(**Fms.emplacimiento_lín_bts)
        cj_líns_izq.pack(side='right')

        for b in range(1, len(símismo.bts) + 1):
            símismo.bts[str(b)].bt.pack(**Fms.emplacimiento_bts_cent)
        cj_bts_izq.pack(side='right')

        símismo.caja.place(**Fms.emplacimiento_cj_izq)

    def activar(símismo, núm):
        n = str(núm)
        símismo.bts[n].activar()
        símismo.líneas[n].configure(bg=símismo.líneas[n].col)

    def desactivar(símismo, núm):
        n = str(núm)
        símismo.bts[n].desactivar()
        símismo.líneas[n].configure(bg='#C3C3C3')


class CajaInic(tk.Frame):
    def __init__(símismo, apli):
        super().__init__(**Fm.formato_CjInic)
        trads = apli.Trads
        símismo.logo = Art.imagen('LogoInic')
        logo = tk.Label(símismo, image=símismo.logo, **Fm.formato_LogoInic)
        logo.pack(Fm.ubic_LogoInic)

        cj_bts_inic = tk.Frame(símismo, **Fm.formato_cajas)
        bt_empezar = Bt.BotónTexto(cj_bts_inic, comanda=símismo.acción_bt_empezar, texto=trads['Empezar'],
                                   formato_norm=Fm.formato_BtsInic_norm,
                                   formato_sel=Fm.formato_BtsInic_sel,
                                   ubicación=Fm.ubic_BtsInic, tipo_ubic='pack')
        bt_empezar.bt.pack(**Fm.ubic_BtsInic)
        cj_bts_inic.pack()

        símismo.place(**Fm.ubic_CjInic)

    def acción_bt_empezar(símismo):
        Anim.quitar(símismo, 'arriba')
        símismo.destroy()


class CajaLeng(tk.Frame):
    def __init__(símismo, apli):
        super().__init__(**Fm.formato_cajas)
        símismo.apli = apli
        símismo.DicLeng = símismo.apli.DicLeng

        símismo.bt_regreso = Bt.BotónImagen(símismo, comanda=símismo.acción_bt_regreso,
                                            img_norm=Art.imagen('BtRegrCent_norm'),
                                            img_sel=Art.imagen('BtRegrCent_sel'),
                                            formato=Fm.formato_botones,
                                            ubicación=Fm.ubic_BtRegrCent, tipo_ubic='place')
        etiq = tk.Label(símismo, text=apli.Trads['OpsLengs'], **Fm.formato_CbzLeng)
        etiq.place(**Fm.ubic_CbzLeng)

        cj_central = tk.Frame(símismo, **Fm.formato_cajas)

        cj_izq = tk.Frame(cj_central, **Fm.formato_cajas)
        etiq_izq = tk.Label(cj_izq, text=apli.Trads['EnTrabajo'], **Fm.formato_EtiqLengLados)
        etiq_izq.place(**Fm.ubic_EtiqCbzColsLeng)
        símismo.lista_izq = CtrG.ListaItemas(cj_izq, formato_cj=Fm.formato_CjLstLengLados,
                                             ubicación=Fm.ubic_LstsLeng, tipo_ubic='place')

        lín_vert_1 = tk.Frame(cj_central, **Fm.formato_LínVert)

        cj_med = tk.Frame(cj_central, **Fm.formato_cajas)
        etiq_med = tk.Label(cj_med, text=apli.Trads['Listas'], **Fm.formato_EtiqLengCentro)
        etiq_med.place(**Fm.ubic_EtiqCbzColsLeng)
        símismo.lista_med = CtrG.ListaItemas(cj_med, formato_cj=Fm.formato_CjLstLengCentro,
                                             ubicación=Fm.ubic_LstsLeng, tipo_ubic='place')

        lín_vert_2 = tk.Frame(cj_central, **Fm.formato_LínVert)

        cj_derech = tk.Frame(cj_central, **Fm.formato_cajas)
        etiq_derech = tk.Label(cj_derech, text=apli.Trads['ParaHacer'], **Fm.formato_EtiqLengLados)
        etiq_derech.place(**Fm.ubic_EtiqCbzColsLeng)
        cj_añadir = Ctrl.CajaAñadirLeng(símismo, cj_derech)
        símismo.lista_derech = CtrG.ListaItemas(cj_derech, formato_cj=Fm.formato_CjLstLengLados,
                                                ubicación=Fm.ubic_LstsLeng_bajo, tipo_ubic='place')

        símismo.establecer_cols()

        cj_izq.place(**Fm.ubic_CjIzqLeng)
        lín_vert_1.place(**Fm.ubic_LínVert1)

        cj_med.place(**Fm.ubic_CjMedLeng)
        lín_vert_2.place(**Fm.ubic_LínVert2)

        cj_añadir.place(**Fm.ubic_CjAñadirLeng)
        cj_derech.place(**Fm.ubic_CjDerchLeng)

        cj_central.place(**Fm.ubic_CjCentLeng)
        símismo.place(**Fm.ubic_CjLeng)

    def acción_bt_regreso(símismo):
        Anim.quitar(símismo, 'derecha')

    def establecer_cols(símismo):
        símismo.DicLeng.verificar_estados()
        for nombre, leng in sorted(símismo.DicLeng.lenguas.items()):
            if 0 < leng['Estado'] < 1:
                lista = símismo.lista_izq
                utilzb = True
            elif leng['Estado'] == 1:
                lista = símismo.lista_med
                utilzb = True
            elif leng['Estado'] == 0:
                lista = símismo.lista_derech
                utilzb = False
            else:
                raise ValueError

            borr = True
            if nombre == símismo.DicLeng.estándar:
                borr = False

            utilznd = False
            if nombre == símismo.DicLeng.dic['Actual']:
                utilznd = True

            Ctrl.ItemaLeng(símismo, lista=lista, nombre=nombre, lengua=leng, estado=leng['Estado'],
                           utilizando=utilznd, utilizable=utilzb, borrable=borr)

    def refrescar(símismo):
        for lista in [símismo.lista_izq, símismo.lista_med, símismo.lista_derech]:
            lista.borrar()
        símismo.establecer_cols()

    def añadir_lengua(símismo, nombre, izqder):
        símismo.DicLeng.lenguas[nombre] = {'Estado': 0.0, 'IzqaDerech': izqder, 'Trads': {}}
        símismo.DicLeng.guardar()
        símismo.refrescar()

    def utilizar(símismo, nombre):
        if nombre != símismo.DicLeng.leng_act:
            if 'AvisoReinic' in símismo.DicLeng.lenguas[nombre]['Trads'].keys():
                texto = símismo.DicLeng.lenguas[nombre]['Trads']['AvisoReinic']
            else:
                texto = símismo.DicLeng.lenguas[símismo.DicLeng.estándar]['Trads']['AvisoReinic']
            Ctrl.CajaAvisoReinic(texto)
            símismo.DicLeng.dic['Actual'] = nombre
            símismo.DicLeng.guardar()
            símismo.refrescar()

    def editar(símismo, nombre):
        leng_base = símismo.DicLeng.dic['Actual']
        if leng_base == nombre:
            leng_base = símismo.DicLeng.estándar
        dic_leng_base = símismo.DicLeng.lenguas[leng_base]

        dic_leng_edit = símismo.DicLeng.lenguas[nombre]
        Ctrl.CajaEditLeng(símismo, leng_base=leng_base, dic_leng_base=dic_leng_base,
                          leng_edit=nombre, dic_leng_edit=dic_leng_edit)

    def confirmar_borrar(símismo, nombre):
        Ctrl.CajaAvisoBorrar(nombre, símismo.borrar)

        símismo.DicLeng.guardar()

    def borrar(símismo, nombre):
        símismo.DicLeng.lenguas.pop(nombre)
        if símismo.DicLeng.dic['Actual'] == nombre:
            símismo.DicLeng.dic['Actual'] = símismo.DicLeng.estándar
        símismo.DicLeng.guardar()
        símismo.refrescar()


class CajaCentral(tk.Frame):
    def __init__(símismo, apli):
        super().__init__(**Fm.formato_CjCent)
        símismo.CjCabeza = CajaCabeza(símismo, apli=apli)

        símismo.ContCjEtapas = CjG.ContCajaEtps(símismo)
        núm_etapas = 4
        símismo.CajasEtapas = [CajaEtp1(símismo.ContCjEtapas, apli, núm_etapas),
                               CajaEtp2(símismo.ContCjEtapas, apli, núm_etapas),
                               CajaEtp3(símismo.ContCjEtapas, apli, núm_etapas),
                               CajaEtp4(símismo.ContCjEtapas, apli, núm_etapas),
                               ]
        símismo.ContCjEtapas.establecer_cajas(símismo.CajasEtapas)

        símismo.CjIzq = CajaIzq(símismo, cajas_etapas=símismo.CajasEtapas)

        símismo.bloquear_cajas(list(range(2, len(símismo.CajasEtapas) + 1)))

        símismo.place(**Fm.ubic_CjCent)

    def bloquear_cajas(símismo, núms_cajas):
        for n in núms_cajas:
            if n > 1:
                símismo.CajasEtapas[n - 2].bloquear_transición(dirección='siguiente')
            if n < len(símismo.CajasEtapas):
                símismo.CajasEtapas[n].bloquear_transición(dirección='anterior')
            símismo.CjIzq.bts[n - 1].bloquear()

    def desbloquear_cajas(símismo, núms_cajas):
        for n in núms_cajas:
            símismo.CajasEtapas[n-1].desbloquear()
            if n > 1:
                símismo.CajasEtapas[n - 2].desbloquear_transición(dirección='siguiente')
            if n < len(símismo.CajasEtapas):
                símismo.CajasEtapas[n].desbloquear_transición(dirección='anterior')
            símismo.CjIzq.bts[n - 1].desbloquear()


class CajaCabeza(tk.Frame):
    def __init__(símismo, pariente, apli):
        super().__init__(pariente, **Fm.formato_CjCabeza)
        símismo.apli = apli
        símismo.logo_cabeza = Art.imagen('LogoCent')
        logo_cabeza = tk.Label(símismo, image=símismo.logo_cabeza, **Fm.formato_LogoCabz)
        logo_cabeza.place(**Fm.ubic_LogoCabz)

        símismo.bt_leng = Bt.BotónImagen(símismo, comanda=símismo.acción_bt_leng,
                                         img_norm=Art.imagen('BtLeng_norm'),
                                         img_sel=Art.imagen('BtLeng_sel'),
                                         formato=Fm.formato_botones,
                                         ubicación=Fm.ubic_BtLeng, tipo_ubic='place')
        símismo.pack(**Fm.ubic_CjCabeza)

    def acción_bt_leng(símismo):
        Anim.sobreponer(símismo.apli.CajaCentral, símismo.apli.CajaLenguas, 'izquierda')


class CajaIzq(tk.Frame):
    def __init__(símismo, pariente, cajas_etapas):
        super().__init__(pariente, **Fm.formato_cajas)
        cj_bts = tk.Frame(símismo, **Fm.formato_cajas)
        lín = tk.Frame(símismo, **Fm.formato_LínIzq)

        símismo.bts = []
        for cj in cajas_etapas:
            símismo.bts.append(Bt.BotónNavIzq(cj_bts, caja=cj))

        cj_bts.pack(**Fm.ubic_CjBtsIzq)
        lín.pack(**Fm.ubic_LínIzq)
        símismo.pack(**Fm.ubic_CjIzq)


class CajaEtp1(CjG.CajaEtapa):
    def __init__(símismo, pariente, apli, total):
        super().__init__(pariente, nombre=apli.Trads['BasedeDatos'], núm=1, total=total)

        total_subcajas = 1
        subcajas = [CjSE.CajaSubEtp11(símismo, apli, total=total_subcajas)]

        símismo.especificar_subcajas(subcajas)
        símismo.bloquear_subcajas([2])


class CajaEtp2(CjG.CajaEtapa):
    def __init__(símismo, pariente, apli, total):
        super().__init__(pariente, nombre=apli.Trads['Variables'], núm=2, total=total)
        total_subcajas = 1
        subcajas = [CjSE.CajaSubEtp21(símismo, apli, total=total_subcajas)]

        símismo.especificar_subcajas(subcajas)
        símismo.bloquear_subcajas([1, 2])

    def desbloquear(símismo):
        símismo.desbloquear_subcajas([1])


class CajaEtp3(CjG.CajaEtapa):
    def __init__(símismo, pariente, apli, total):
        super().__init__(pariente, nombre=apli.Trads['Verificar'], núm=3, total=total)

        total_subcajas = 1
        subcajas = [CjSE.CajaSubEtp31(símismo, apli, total=total_subcajas)]

        símismo.especificar_subcajas(subcajas)

    def desbloquear(símismo):
        símismo.desbloquear_subcajas([1])


class CajaEtp4(CjG.CajaEtapa):
    def __init__(símismo, pariente, apli, total):
        super().__init__(pariente, nombre=apli.Trads['Predecir'], núm=4, total=total)
        total_subcajas = 1
        subcajas = [CjSE.CajaSubEtp41(símismo, apli, total=total_subcajas)]
        símismo.especificar_subcajas(subcajas)


class CajaTrabajo(object):
    def __init__(símismo, apli, pariente, núm, imgs):
        símismo.núm = núm
        símismo.caja = tk.Frame(pariente, **Fms.formato_cajas_trab)
        símismo.bts = {}

        if núm == 1:
            símismo.crear_caja_1(apli=apli)

        if núm == 2:
            símismo.crear_caja_2(apli=apli, imgs=imgs)

        if núm == 3:
            símismo.crear_caja_3(apli=apli, imgs=imgs)

        if núm == 4:
            símismo.crear_caja_4(apli=apli, imgs=imgs)

        if núm > 1:
            símismo.bt_anterior = Bts.Botón(símismo.caja, comanda=apli.ir_atrás,
                                            img=imgs['bt_ant'], img_sel=imgs['bt_ant_sel'],
                                            img_bloc=imgs['bt_ant_bloc'],
                                            **Fms.formato_bts_ant_sig)
            símismo.bt_anterior.bt.place(**Fms.emplacimiento_bt_anterior)

        if núm < 4:
            símismo.bt_siguiente = Bts.Botón(símismo.caja, comanda=apli.ir_adelante,
                                             img=imgs['bt_sig'], img_sel=imgs['bt_sig_sel'],
                                             img_bloc=imgs['bt_sig_bloc'],
                                             **Fms.formato_bts_ant_sig)
            símismo.bt_siguiente.bt.place(**Fms.emplacimiento_bt_siguiente)

        símismo.caja.place(**Fms.emplacimiento_cajas_trab)

    def crear_caja_1(símismo, apli):

        caja_mds = tk.Frame(símismo.caja, **Fms.formato_cajas)
        lín_vert = tk.Label(símismo.caja, bg='black')
        caja_bf = tk.Frame(símismo.caja, **Fms.formato_cajas)
        lín_hor = tk.Frame(símismo.caja, bg='black')
        caja_con = tk.Frame(símismo.caja, **Fms.formato_cajas)

        caja_mds.place(**Fms.emplacimiento_caja_cargar_mds)
        lín_vert.place(**Fms.emplacimiento_lín_vert_med)
        caja_bf.place(**Fms.emplacimiento_caja_cargar_bf)
        lín_hor.place(**Fms.emplacimiento_lín_hor)
        caja_con.place(**Fms.emplacimiento_caja_cargar_conectado)

        etiq_mds = tk.Label(caja_mds, text='MDS', **Fms.formato_etiq_cargar_mod)
        símismo.bts['bt_cargar_mds'] = tk.Button(caja_mds, text='Cargar', command=apli.buscar_mds,
                                                 **Fms.formato_bts_cargar)
        etiq_bf = tk.Label(caja_bf, text='Modelo biofísico', **Fms.formato_etiq_cargar_mod)
        símismo.bts['bt_cargar_bf'] = tk.Button(caja_bf, text='Cargar', command=apli.buscar_bf,
                                                **Fms.formato_bts_cargar)
        etiq_sino = tk.Label(caja_con, text='O...', **Fms.formato_etiq_sino)
        etiq_con = tk.Label(caja_con, text='Cargar un modelo ya conectado', **Fms.formato_etiq_cargar_con)
        símismo.bts['bt_cargar_con'] = tk.Button(caja_con, text='Modelo conectado', command=apli.buscar_con,
                                                 **Fms.formato_bts_cargar)

        for i in [símismo.bts['bt_cargar_bf'], símismo.bts['bt_cargar_mds'], símismo.bts['bt_cargar_con']]:
            i.bind('<Enter>', lambda event, b=i: b.configure(bg=Fms.color_bts['1']))
            i.bind('<Leave>', lambda event, b=i: b.configure(bg='white'))

        etiq_mds.place(x=10, y=10)
        símismo.bts['bt_cargar_mds'].place(**Fms.emplacimiento_bts_cargar_mod)
        etiq_bf.place(x=10, y=10)
        símismo.bts['bt_cargar_bf'].place(**Fms.emplacimiento_bts_cargar_mod)
        etiq_sino.pack(pady=10)
        etiq_con.pack(pady=10)
        símismo.bts['bt_cargar_con'].pack()

    def error(símismo, bt):
        símismo.bts[bt].configure(bg=Fms.color_error)

    def noerror(símismo, bt):
        símismo.bts[bt].configure(bg=Fms.color_bts['1'])

    def crear_caja_2(símismo, apli, imgs):
        pass

    def crear_caja_3(símismo, apli, imgs):
        pass

    def crear_caja_4(símismo, apli, imgs):
        pass

    def traer(símismo):
        símismo.caja.lift()

    def quitar(símismo):
        símismo.caja.lower()


class CajaLista(object):
    def __init__(símismo, máx_itemas):
        pass
