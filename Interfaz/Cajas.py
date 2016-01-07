import tkinter as tk

from Interfaz import Formatos as Fms
from Interfaz import Botones as Bts


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