import tkinter as tk
import webbrowser
import Formatos as fm
import Gráficos as gr
import Objetos as ob
from MDS import cargar_mds


class Apli(tk.Frame):
    def __init__(símismo, pariente):
        tk.Frame.__init__(símismo, pariente)
        pariente.title('Tinamit')
        pariente.geometry('%ix%i' % fm.dim_ventana)
        pariente.configure(background='white')

        símismo.imgs = gr.cargar_imágenes()

        símismo.pantalla_inicio = símismo.crear_pantalla_inicio(imgs=símismo.imgs)
        símismo.pantalla_central = símismo.crear_pantalla_central(imgs=símismo.imgs)
        símismo.pantalla_lengua = símismo.crear_pantalla_lengua(imgs=símismo.imgs)
        símismo.caja_activa = símismo.pantalla_central.cajas_trabajo['1']
        símismo.pantalla_central.lower()
        símismo.pantalla_lengua.lower()

    def crear_pantalla_inicio(símismo, imgs):
        # La caja principal que contiene todo visible en esta pantalla
        cj_pant_inic = tk.Frame(**fm.formato_cajas)

        # El logo 'Tinamit'

        cj_pant_inic.logo_inic = tk.Label(cj_pant_inic, image=imgs['img_logo'], **fm.formato_logo_inic)

        # Una caja para los dos botones, tanto como los botones sí mismos
        cj_pant_inic.caja_bts_inic = tk.Frame(cj_pant_inic, **fm.formato_cajas)
        cj_pant_inic.bt_empezar = tk.Button(cj_pant_inic.caja_bts_inic, text='Empezar',
                                            command=símismo.acción_bt_empezar, **fm.formato_bts_inic)
        cj_pant_inic.bt_ayuda = tk.Button(cj_pant_inic.caja_bts_inic, text='Ayuda', command=símismo.acción_bt_ayuda,
                                          **fm.formato_bts_inic)
        for i in [cj_pant_inic.bt_empezar, cj_pant_inic.bt_ayuda]:
            i.bind('<Enter>', lambda event, b=i: b.configure(bg='#ccff66'))
            i.bind('<Leave>', lambda event, b=i: b.configure(bg='white'))

        # Dibujar todo
        cj_pant_inic.logo_inic.pack(fm.emplacimiento_logo_inic)
        cj_pant_inic.bt_empezar.pack(fm.emplacimiento_bts_inic)
        cj_pant_inic.bt_ayuda.pack(fm.emplacimiento_bts_inic)
        cj_pant_inic.caja_bts_inic.pack(pady=20)
        cj_pant_inic.place(**fm.emplacimiento_cajas_cent)

        return cj_pant_inic

    def acción_bt_empezar(símismo):
        símismo.pantalla_inicio.destroy()

    @staticmethod
    def acción_bt_ayuda():
        webbrowser.open('Documentación.txt')

    def crear_pantalla_central(símismo, imgs):

        # La caja principal que contiene todo visible en esta pantalla
        cj_pant_cent = tk.Frame(**fm.formato_cajas)

        #
        cj_pant_cent.caja_cabeza = tk.Frame(cj_pant_cent, **fm.formato_cajas)
        cj_pant_cent.logo_cent = tk.Label(cj_pant_cent.caja_cabeza, image=imgs['img_logo_cent'], **fm.formato_logo_cent)
        cj_pant_cent.bt_leng = tk.Button(cj_pant_cent.caja_cabeza, command=símismo.acción_bt_leng,
                                         image=imgs['img_ulew'], **fm.formato_bt_leng)
        bt_leng = cj_pant_cent.bt_leng
        bt_leng.bind('<Enter>', lambda event, bt=bt_leng: bt.configure(image=imgs['img_ulew_act']))
        bt_leng.bind('<Leave>', lambda event, bt=bt_leng: bt.configure(image=imgs['img_ulew']))

        #
        cj_pant_cent.caja_izq = tk.Frame(cj_pant_cent, **fm.formato_cajas)
        cj_izq = cj_pant_cent.caja_izq

        #
        cj_izq.cj_líns_izq = tk.Frame(cj_pant_cent.caja_izq, **fm.formato_cajas)
        cj_líns_izq = cj_izq.cj_líns_izq
        cj_líns_izq.líns = {}
        for i in range(1, 5):
            cj_líns_izq.líns[str(i)] = tk.Canvas(cj_izq.cj_líns_izq, **fm.formato_lín_bts)
            cj_líns_izq.líns[str(i)].col = '#%02x%02x%02x' % fm.color_bts[str(i)]

        #
        cj_izq.caja_bts_izq = tk.Frame(cj_izq, **fm.formato_cajas)
        cj_bts_izq = cj_izq.caja_bts_izq

        cj_bts_izq.bts = {}
        for i in range(1, 5):
            obj_bt = cj_bts_izq.bts
            obj_bt[str(i)] = ob.BotónIzq(apli=símismo, pariente=cj_bts_izq, lín=cj_líns_izq.líns[str(i)], i=i,
                                         img=símismo.imgs['img_bt_%i' % i],
                                         img_bloc=símismo.imgs['img_bt_%i_bloc' % i],
                                         img_sel=símismo.imgs['img_bt_%i_sel' % i])
        for i in range(1, 5):
            obj_bt[str(i)].bt.bind('<Enter>', lambda event, k=obj_bt[str(i)]: poner_enf(k))
            obj_bt[str(i)].bt.bind('<Leave>', lambda event, k=obj_bt[str(i)]: quitar_énf(k))

        def poner_enf(botón):
            if botón.bt['state'] == 'normal':
                botón.bt.configure(image=botón.img_sel)

        def quitar_énf(botón):
            if botón.bt['state'] == 'normal':
                botón.bt.configure(image=botón.img)

        # Desactivar los botones no disponibles
        símismo.activar_bt(cj_bts_izq.bts['1'])
        for i in [2, 3, 4]:
            símismo.desactivar_bt(cj_bts_izq.bts[str(i)])

        # Dibujar lo que creamos
        cj_pant_cent.logo_cent.place(**fm.emplacimiento_logo_cent)
        cj_pant_cent.bt_leng.place(**fm.emplacimiento_bt_leng)
        cj_pant_cent.caja_cabeza.place(**fm.emplacimiento_caja_cabeza)

        for l in sorted(cj_líns_izq.líns.keys()):
            cj_líns_izq.líns[l].pack(**fm.emplacimiento_lín_bts)
        cj_izq.cj_líns_izq.pack(side='right')

        for b in sorted(cj_bts_izq.bts.keys()):
            cj_bts_izq.bts[b].bt.pack(**fm.emplacimiento_bts_cent)
        cj_bts_izq.pack(side='right')
        cj_izq.place(**fm.emplacimiento_cj_izq)

        # Crear las otras cajas
        cj_pant_cent.cajas_trabajo = {}
        for i in range(1, 5):
            cj_pant_cent.cajas_trabajo[str(i)] = símismo.crear_caja_trabajo(cj_pant_cent, i, imgs=símismo.imgs)


        # Poner la caja central en su lugar
        cj_pant_cent.place(**fm.emplacimiento_cajas_cent)

        return cj_pant_cent

    def crear_pantalla_lengua(símismo, imgs):
                # La caja principal que contiene todo visible en esta pantalla
        cj_pant_leng = tk.Frame(**fm.formato_cajas)

        temp = tk.Label(cj_pant_leng,
                        text='Falta implementar la interfaz para el manejo de lenguas. Siéntese libre de contribuir.')
        temp.pack()
        cj_pant_leng.place(**fm.emplacimiento_cajas_cent)

        return cj_pant_leng

    def cambiar_caja_trabajo(símismo, núm_nueva):
        if símismo.caja_activa.núm is not núm_nueva:
            símismo.intercambiar(símismo.caja_activa,
                                 símismo.pantalla_central.cajas_trabajo[str(núm_nueva)])
            símismo.caja_activa = símismo.pantalla_central.cajas_trabajo[str(símismo.núm)]

    def acción_bt_leng(símismo):
        símismo.pantalla_lengua.lift()

    @staticmethod
    def intercambiar(caja_orig, caja_nueva):
        caja_orig.lower()
        caja_nueva.lift()

    @staticmethod
    def desactivar_bt(botón):
        botón.bt.configure(image=botón.img_bloc, state='disabled')
        botón.lín.configure(bg='#C3C3C3')

    @staticmethod
    def activar_bt(botón):
        botón.bt.configure(image=botón.img, state='normal')
        botón.lín.configure(bg=botón.lín.col)

    def crear_caja_trabajo(símismo, pariente, i, imgs):
        caja = tk.Frame(pariente, **fm.formato_cajas_núm)
        prueba = tk.Label(caja, text='prueba', bg='white')
        prueba.pack()
        if i > 1:
            caja.bt_siguiente = tk.Button(caja, image=imgs['bt_sig'], command=símismo.ir_adelante,
                                          **fm.formato_bts_ant_sig)
            caja.bt_siguiente.place(**fm.emplacimiento_bt_siguiente)
            caja.bt_siguiente.bind('<Enter>', lambda event, b=caja.bt_siguiente: b.configure(image=imgs['bt_sig_sel']))
            caja.bt_siguiente.bind('<Leave>', lambda event, b=caja.bt_siguiente: b.configure(image=imgs['bt_sig']))
        if i < 4:
            caja.bt_anterior = tk.Button(caja, image=imgs['bt_ant'], command=símismo.ir_atrás,
                                         **fm.formato_bts_ant_sig)
            caja.bt_anterior.bind('<Enter>', lambda event, b=caja.bt_anterior: b.configure(image=imgs['bt_ant_sel']))
            caja.bt_anterior.bind('<Leave>', lambda event, b=caja.bt_anterior: b.configure(image=imgs['bt_ant']))
            caja.bt_anterior.place(**fm.emplacimiento_bt_anterior)

        caja.núm = i
        caja.place(**fm.emplacimiento_cajas_núm)

        return caja

    def ir_adelante(símismo):
        símismo.intercambiar(símismo.caja_activa,
                             símismo.pantalla_central.cajas_trabajo[str(símismo.caja_activa.núm + 1)])

    def ir_atrás(símismo):
        símismo.intercambiar(símismo.caja_activa,
                             símismo.pantalla_central.cajas_trabajo[str(símismo.caja_activa.núm - 1)])


if __name__ == '__main__':
    raíz = tk.Tk()
    apli = Apli(raíz)
    apli.mainloop()
