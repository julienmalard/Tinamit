import tkinter as tk
from Interfaz import Cajas as Cjs, Botones as Bts, Formatos as Fms


class PantallaInicio(object):
    def __init__(símismo, apli, imgs):
        símismo.caja = tk.Frame(**Fms.formato_cajas)

        # El logo 'Tinamit'
        logo_inic = tk.Label(símismo.caja, image=imgs['img_logo'], **Fms.formato_logo_inic)

        # Una caja para los dos botones, tanto como los botones sí mismos
        caja_bts_inic = tk.Frame(símismo.caja, **Fms.formato_cajas)
        bt_empezar = tk.Button(caja_bts_inic, text='Empezar', command=apli.acción_bt_empezar,
                               **Fms.formato_bts_inic)
        bt_ayuda = tk.Button(caja_bts_inic, text='Ayuda', command=apli.acción_bt_ayuda,
                             **Fms.formato_bts_inic)
        for i in [bt_empezar, bt_ayuda]:
            i.bind('<Enter>', lambda event, b=i: b.configure(bg='#ccff66'))
            i.bind('<Leave>', lambda event, b=i: b.configure(bg='white'))

        # Dibujar todo
        logo_inic.pack(Fms.emplacimiento_logo_inic)
        bt_empezar.pack(Fms.emplacimiento_bts_inic)
        bt_ayuda.pack(Fms.emplacimiento_bts_inic)
        caja_bts_inic.pack(pady=20)
        símismo.caja.place(**Fms.emplacimiento_cajas_cent)


class PantallaCentral(object):
    def __init__(símismo, apli, imgs):
        # La caja principal que contiene todo visible en esta pantalla
        símismo.caja = tk.Frame(**Fms.formato_cajas)

        # Hacer el encabezado de la pantalla con el logo, etc.
        caja_cabeza = tk.Frame(símismo.caja, **Fms.formato_cajas)
        logo_cent = tk.Label(caja_cabeza, image=imgs['img_logo_cent'], **Fms.formato_logo_cent)
        bt_leng = Bts.Botón(caja_cabeza, comanda=apli.acción_bt_leng, img=imgs['img_ulew'],
                            img_sel=imgs['img_ulew_sel'], **Fms.formato_bt_leng)

        # Crear la caja de izquierda para contener los botones de navigación
        símismo.caja_izq = Cjs.CajaIzquierda(apli=apli, pariente=símismo.caja, imgs=imgs)

        # Dibujar lo que creamos
        logo_cent.place(**Fms.emplacimiento_logo_cent)
        bt_leng.bt.place(**Fms.emplacimiento_bt_leng)
        caja_cabeza.place(**Fms.emplacimiento_caja_cabeza)

        # Crear las otras cajas
        símismo.cajas_trabajo = {}
        for i in range(1, 5):
            símismo.cajas_trabajo[str(i)] = Cjs.CajaTrabajo(apli=apli, pariente=símismo.caja, núm=i, imgs=imgs)
        símismo.caja_trab_act = 1

        # Poner la caja central en su lugar
        símismo.caja.place(**Fms.emplacimiento_cajas_cent)

    def bloquear_caja(símismo, núm_caja):
        if núm_caja > 1:
            símismo.cajas_trabajo[str(núm_caja - 1)].bt_siguiente.desactivar()
        if núm_caja < 4:
            símismo.cajas_trabajo[str(núm_caja + 1)].bt_anterior.desactivar()

        símismo.caja_izq.desactivar(núm_caja)

    def desbloquear_caja(símismo, núm_caja):
        if núm_caja > 1:
            símismo.cajas_trabajo[str(núm_caja - 1)].bt_siguiente.activar()
        if núm_caja < 4:
            símismo.cajas_trabajo[str(núm_caja + 1)].bt_anterior.activar()

        símismo.caja_izq.activar(núm_caja)

    def ir_adelante(símismo):
        if símismo.caja_trab_act < 4:
            símismo.pasar_a_caja(símismo.caja_trab_act + 1)

    def ir_atrás(símismo):
        if símismo.caja_trab_act > 1:
            símismo.pasar_a_caja(símismo.caja_trab_act - 1)

    def pasar_a_caja(símismo, n):
        if n != símismo.caja_trab_act:
            símismo.cajas_trabajo[str(n)].traer()
            símismo.cajas_trabajo[str(símismo.caja_trab_act)].quitar()

            símismo.caja_izq.bts[str(n)].seleccionar()
            símismo.caja_izq.bts[str(símismo.caja_trab_act)].deseleccionar()
            símismo.caja_trab_act = n


class PantallaLengua(object):
    def __init__(símismo, apli, imgs):
        # La caja principal que contiene todo visible en esta pantalla
        símismo.caja = tk.Frame(**Fms.formato_cajas)

        temp = tk.Label(símismo.caja,
                        text='Falta implementar la interfaz para el manejo de lenguas. Siéntese libre de contribuir.')
        temp.pack()

        bt_regr_cent = Bts.Botón(símismo.caja, comanda=apli.acción_bt_regr_cent, img=imgs['bt_regr_cent'])
        bt_regr_cent.bt.pack()

        # Poner la caja central en su lugar
        símismo.caja.place(**Fms.emplacimiento_cajas_cent)
