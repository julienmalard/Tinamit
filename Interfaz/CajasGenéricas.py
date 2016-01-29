import tkinter as tk

from Interfaz import Formatos as Fm
from Interfaz import Botones as Bt
from Interfaz import ControlesGenéricos as Ctrl
from Interfaz import Arte as Ic
from Interfaz import Animaciones as Anim


class ContCajaEtps(tk.Frame):
    def __init__(símismo, pariente):
        super().__init__(pariente, **Fm.formato_CjContCjEtps)
        símismo.pariente = pariente

        símismo.Cajas = []
        símismo.CajaActual = None
        símismo.pack(**Fm.ubic_CjContCjEtps)
        símismo.en_transición = False

    def establecer_cajas(símismo, cajas_etapas):
        for n, cj in enumerate(cajas_etapas):
            símismo.Cajas.append(cj)
        símismo.CajaActual = símismo.Cajas[0]
        símismo.CajaActual.lift()

    def ir_a_caja(símismo, núm_cj_nueva):
        if núm_cj_nueva < símismo.CajaActual.núm:
            dirección = 'abajo'
        elif núm_cj_nueva > símismo.CajaActual.núm:
            dirección = 'arriba'
        else:
            return

        if not símismo.en_transición:
            símismo.en_transición = True
            nueva_caja = símismo.Cajas[núm_cj_nueva-1]
            nueva_caja.lift()
            Anim.intercambiar(símismo.CajaActual, nueva_caja, dirección=dirección)
            símismo.CajaActual = nueva_caja
            símismo.en_transición = False

    def bloquear_cajas(símismo, núms_cajas):
        símismo.pariente.bloquear_cajas(núms_cajas)

    def desbloquear_cajas(símismo, núms_cajas):
        símismo.pariente.desbloquear_cajas(núms_cajas)


class CajaEtapa(tk.Frame):
    def __init__(símismo, pariente, nombre, núm, total):
        super().__init__(pariente, **Fm.formato_cajas)
        símismo.núm = núm
        símismo.pariente = pariente
        símismo.SubCajas = []
        símismo.SubCajaActual = None
        
        etiq = tk.Label(símismo, text=nombre, **Fm.formato_EncbzCjEtp)
        etiq.place(**Fm.ubic_EncbzCjEtp)

        símismo.BtAtrás = símismo.BtAdelante = None
        if núm > 1:
            símismo.BtAtrás = Bt.BotónNavEtapa(símismo, tipo='atrás')
        if núm < total:
            símismo.BtAdelante = Bt.BotónNavEtapa(símismo, tipo='adelante')

        símismo.place(**Fm.ubic_CjEtp)

    def especificar_subcajas(símismo, subcajas):
        símismo.SubCajas = subcajas
        símismo.ir_a_sub(1)

    def bloquear_cajas(símismo, núms_cajas):
        símismo.pariente.bloquear_cajas(núms_cajas)

    def desbloquear_cajas(símismo, núms_cajas):
        símismo.pariente.desbloquear_cajas(núms_cajas)

    def bloquear_transición(símismo, dirección):
        if dirección == 'anterior' and símismo.BtAtrás is not None:
            símismo.BtAtrás.bloquear()
        elif dirección == 'siguiente' and símismo.BtAdelante is not None:
            símismo.BtAdelante.bloquear()

    def desbloquear_transición(símismo, dirección):
        if dirección == 'anterior' and símismo.BtAtrás is not None:
            símismo.BtAtrás.desbloquear()
        elif dirección == 'siguiente' and símismo.BtAdelante is not None:
            símismo.BtAdelante.desbloquear()

    def ir_a_sub(símismo, núm_sub_nueva):
        if símismo.SubCajaActual is None:
            símismo.SubCajaActual = símismo.SubCajas[núm_sub_nueva-1]
            símismo.SubCajaActual.lift()
        else:
            if núm_sub_nueva < símismo.SubCajaActual.núm:
                dirección = 'derecha'
            elif núm_sub_nueva > símismo.SubCajaActual.núm:
                dirección = 'izquierda'
            else:
                return
            Anim.intercambiar(símismo.SubCajaActual, símismo.SubCajas[núm_sub_nueva-1], dirección=dirección)
            símismo.SubCajaActual = símismo.SubCajas[núm_sub_nueva-1]

    def traer_me(símismo):
        símismo.pariente.ir_a_caja(símismo.núm)

    def ir_etp_siguiente(símismo):
        símismo.pariente.ir_a_caja(símismo.núm + 1)

    def ir_etp_anterior(símismo):
        símismo.pariente.ir_a_caja(símismo.núm - 1)
        
    def bloquear_subcajas(símismo, núms_cajas):
        for n in núms_cajas:
            if n > 1:
                símismo.SubCajas[n - 2].bloquear_transición(dirección='siguiente')
            if n < len(símismo.SubCajas):
                símismo.SubCajas[n].bloquear_transición(dirección='anterior')

    def desbloquear_subcajas(símismo, núms_cajas):
        for n in núms_cajas:
            símismo.SubCajas[n - 1].acción_desbloquear()
            if n > 1:
                símismo.SubCajas[n - 2].desbloquear_transición(dirección='siguiente')
            if n < len(símismo.SubCajas):
                símismo.SubCajas[n].desbloquear_transición(dirección='anterior')

    def desbloquear(símismo):
        pass


class CajaSubEtapa(tk.Frame):
    def __init__(símismo, pariente, nombre, núm, total):
        super().__init__(pariente, **Fm.formato_cajas)

        símismo.pariente = pariente
        símismo.núm = núm
        
        if nombre is not None:
            etiq = tk.Label(símismo, text=nombre, **Fm.formato_EncbzCjSubEtp)
            etiq.place(**Fm.ubic_EncbzCjSubEtp)
            
        símismo.BtAdelante = None
        símismo.BtAtrás = None
        if núm < total:
            símismo.BtAdelante = Bt.BotónNavSub(símismo, tipo='adelante')
        if núm > 1:
            símismo.BtAtrás = Bt.BotónNavSub(símismo, tipo='atrás')

        símismo.place(Fm.ubic_CjSubEtp)

    def bloquear_transición(símismo, dirección):
        if dirección == 'anterior' and símismo.BtAtrás is not None:
            símismo.BtAtrás.bloquear()
        elif dirección == 'siguiente' and símismo.BtAdelante is not None:
            símismo.BtAdelante.bloquear()

    def desbloquear_transición(símismo, dirección):
        if dirección == 'anterior' and símismo.BtAtrás is not None:
            símismo.BtAtrás.desbloquear()
        elif dirección == 'siguiente' and símismo.BtAdelante is not None:
            símismo.BtAdelante.desbloquear()

    def ir_sub_siguiente(símismo):
        símismo.pariente.ir_a_sub(símismo.núm + 1)

    def ir_sub_anterior(símismo):
        símismo.pariente.ir_a_sub(símismo.núm - 1)

    def ir_etp_siguiente(símismo):
        símismo.pariente.ir_etp_siguiente()

    def ir_etp_anterior(símismo):
        símismo.pariente.ir_etp_anterior()

    def acción_desbloquear(símismo):
        pass  # A implementar en subcajas específicas donde necesario

    def verificar_completo(símismo):
        pass  # A implementar en subcajas específicas donde necesario


class CajaActivable(tk.Frame):
    def __init__(símismo, pariente, ubicación, tipo_ubic):
        super().__init__(pariente, **Fm.formato_cajas)
        símismo.etiquetas = []
        símismo.colores_etiquetas = []
        símismo.botones = []
        
        if tipo_ubic == 'pack':
            símismo.pack(**ubicación)
        elif tipo_ubic == 'place':
            símismo.place(**ubicación)

    def especificar_objetos(símismo, objetos):
        símismo.etiquetas = [x for x in objetos if type(x) is tk.Label]
        símismo.botones = [x for x in objetos if
                           type(x) is Bt.BotónImagen or
                           type(x) is Bt.BotónTexto or
                           type(x) is Ctrl.Menú]

        símismo.colores_etiquetas = [x.cget['fg'] for x in símismo.etiquetas]

    def bloquear(símismo):
        for etiq in símismo.etiquetas:
            etiq.configure(Fm.formato_EtiqCtrl_bloq)
        for bt in símismo.botones:
            bt.bloquear()

    def desbloquear(símismo):
        for n, etiq in enumerate(símismo.etiquetas):
            etiq.configure(color=símismo.colores_etiquetas[n])
        for bt in símismo.botones:
            bt.desbloquear()


class CajaAvanzada(tk.Frame):
    def __init__(símismo, pariente, ubicación, tipo_ubic):
        super().__init__(pariente)

        símismo.caja_móbil = None
        símismo.flechita_avnz = Ic.imagen('FlchAvzd')
        símismo.flechita_senc = Ic.imagen('FlchSenc')
        símismo.bt = tk.Button(símismo, text='Avanzado', image=símismo.flechita_avnz,
                               command=símismo.bajar,
                               compound='right')
        símismo.bt.pack()

        if tipo_ubic == 'place':
            símismo.place(**ubicación)
        elif tipo_ubic == 'pack':
            símismo.pack(**ubicación)

    def establecer_caja_móbil(símismo, caja_móbil):
        símismo.caja_móbil = caja_móbil
        símismo.caja_móbil.cj.place(**Fm.ubic_CjMóbl)

    def bajar(símismo):
        símismo.bt.configure(text='Sencillo', image=símismo.flechita_senc, command=símismo.subir)
        Anim.deslizar(objetos=[símismo.caja_móbil, símismo.bt],
                      pos_inic=[símismo.caja_móbil.winfo_y(), símismo.bt.winfo_y()],
                      dirección='abajo',
                      distancia=símismo.caja_móbil.winfo_height())

    def subir(símismo):
        símismo.bt.configure(text='Avanzado', image=símismo.flechita_avnz, command=símismo.bajar)
        Anim.deslizar(objetos=[símismo.caja_móbil, símismo.bt],
                      pos_inic=[símismo.caja_móbil.winfo_y(), símismo.bt.winfo_y()],
                      dirección='arriba',
                      distancia=símismo.caja_móbil.winfo_height())
