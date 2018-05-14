import tkinter as tk

from . import Arte as Gr
from . import Formatos as Fm
from .Formatos import gen_formato as gf


class Botón(object):
    def __init__(símismo, pariente, comanda=None, formato=None, img_norm=None, img_sel=None, img_bloq=None,
                 texto=None, formato_norm=None, formato_sel=None, formato_bloq=None,
                 ubicación=None, tipo_ubic=None, tipo_combin='left'):

        símismo.formato = {}
        if tipo_combin is not None:
            símismo.formato['compound'] = tipo_combin
        if texto is not None:
            símismo.formato['text'] = texto
        if formato is not None:
            for ll, v in formato.items():
                símismo.formato[ll] = v

        símismo.formato_norm = {}
        símismo.formato_bloq = {}
        símismo.formato_sel = {}

        if img_norm is not None:
            símismo.formato_norm['image'] = img_norm
        if img_sel is not None:
            símismo.formato_sel['image'] = img_sel
        if img_bloq is not None:
            símismo.formato_bloq['image'] = img_bloq
        if formato_norm is not None:
            for ll, v in formato_norm.items():
                símismo.formato_norm[ll] = v
        if formato_sel is not None:
            for ll, v in formato_sel.items():
                símismo.formato_sel[ll] = v
        if formato_bloq is not None:
            for ll, v in formato_bloq.items():
                símismo.formato_bloq[ll] = v

        símismo.estado = 'Normal'

        # Hasta que aprende cómo cargar Python 3.5 en esta compu...
        dic_formato = símismo.formato.copy()
        dic_formato.update(símismo.formato_norm)

        símismo.bt = tk.Button(pariente, relief=tk.FLAT, command=comanda,
                               **dic_formato)

        símismo.bloquear()
        símismo.desbloquear()
        símismo.bt.bind('<Enter>', lambda event, b=símismo: b.resaltar())
        símismo.bt.bind('<Leave>', lambda event, b=símismo: b.desresaltar())

        if tipo_ubic == 'pack':
            símismo.bt.pack(**ubicación)
        elif tipo_ubic == 'place':
            símismo.bt.place(**ubicación)
        elif tipo_ubic == 'grid':
            símismo.bt.grid(**ubicación)

    def bloquear(símismo):
        símismo.estado = 'Bloqueado'
        símismo.bt.configure(cursor='X_cursor', state='disabled', **símismo.formato_bloq)

    def desbloquear(símismo):
        símismo.estado = 'Normal'
        símismo.bt.configure(cursor='arrow', state='normal', **símismo.formato_norm)

    def resaltar(símismo):
        if símismo.estado == 'Normal':
            símismo.bt.configure(**símismo.formato_sel)

    def desresaltar(símismo):
        if símismo.estado == 'Normal':
            símismo.bt.configure(**símismo.formato_norm)

    def seleccionar(símismo):
        if símismo.estado == 'Normal':
            símismo.bt.configure(**símismo.formato_sel)

    def deseleccionar(símismo):
        if símismo.estado == 'Normal':
            símismo.bt.configure(**símismo.formato_norm)

    def estab_comanda(símismo, comanda):
        símismo.bt.config(command=comanda)


class BotónTexto(Botón):
    def __init__(símismo, pariente, texto, formato_norm, formato_sel,
                 ubicación, tipo_ubic, comanda=None, formato_bloq=None):
        super().__init__(pariente, comanda, texto=texto, formato_norm=formato_norm,
                         formato_sel=formato_sel, formato_bloq=formato_bloq,
                         ubicación=ubicación, tipo_ubic=tipo_ubic)


class BotónImagen(Botón):
    def __init__(símismo, pariente, comanda, formato, img_norm, img_sel, img_bloq=None,
                 ubicación=None, tipo_ubic=None):
        super().__init__(pariente, comanda=comanda, formato=formato, img_norm=img_norm,
                         img_sel=img_sel, img_bloq=img_bloq,
                         ubicación=ubicación, tipo_ubic=tipo_ubic)


class BotónNavIzq(object):
    def __init__(símismo, pariente, caja):
        img_norm = Gr.imagen('BtNavIzq_%i_norm' % caja.núm)
        img_bloq = Gr.imagen('BtNavIzq_%i_bloq' % caja.núm)
        img_sel = Gr.imagen('BtNavIzq_%i_sel' % caja.núm)

        cj = tk.Frame(pariente, **Fm.formato_cajas)
        símismo.bt = BotónImagen(pariente=cj, comanda=caja.traer_me, img_norm=img_norm, img_bloq=img_bloq,
                                 img_sel=img_sel, ubicación=gf(Fm.ubic_BtNavIzq), tipo_ubic='pack',
                                 formato=Fm.formato_BtsNavIzq)

        símismo.color = Fm.color_bts[str(caja.núm)]
        símismo.lín = tk.Frame(cj, bg=símismo.color, **Fm.formato_lín_bts)

        símismo.lín.pack(**gf(Fm.ubic_LínNavIzq))
        cj.pack(**gf(Fm.ubic_CjBtNavIzq))

    def desbloquear(símismo):
        símismo.bt.desbloquear()
        símismo.lín.configure(bg=símismo.color)

    def bloquear(símismo):
        símismo.bt.bloquear()
        símismo.lín.configure(bg=Fm.color_gris)


class BotónNavEtapa(BotónImagen):
    def __init__(símismo, pariente, tipo):
        if tipo == 'adelante':
            img_norm = Gr.imagen('BtNavEtp_adel_norm')
            img_bloq = Gr.imagen('BtNavEtp_adel_bloq')
            img_sel = Gr.imagen('BtNavEtp_adel_sel')
            ubicación = gf(Fm.ubic_BtNavEtp_adel)
            comanda = pariente.ir_etp_siguiente
        elif tipo == 'atrás':
            img_norm = Gr.imagen('BtNavEtp_atrs_norm')
            img_bloq = Gr.imagen('BtNavEtp_atrs_bloq')
            img_sel = Gr.imagen('BtNavEtp_atrs_sel')
            ubicación = gf(Fm.ubic_BtNavEtp_atrs)
            comanda = pariente.ir_etp_anterior
        else:
            raise ValueError

        super().__init__(pariente=pariente, comanda=comanda, img_norm=img_norm, img_bloq=img_bloq,
                         img_sel=img_sel, ubicación=ubicación, tipo_ubic='place',
                         formato=Fm.formato_BtsNavEtapa)


class BotónNavSub(BotónImagen):
    def __init__(símismo, pariente, tipo):
        if tipo == 'adelante':
            img_norm = Gr.imagen('BtNavSub_adel_norm')
            img_bloq = Gr.imagen('BtNavSub_adel_bloq')
            img_sel = Gr.imagen('BtNavSub_adel_sel')
            ubicación = gf(Fm.ubic_BtNavSub_adel)
            comanda = pariente.ir_sub_siguiente
        elif tipo == 'atrás':
            img_norm = Gr.imagen('BtNavSub_atrs_norm')
            img_bloq = Gr.imagen('BtNavSub_atrs_bloq')
            img_sel = Gr.imagen('BtNavSub_atrs_sel')
            ubicación = gf(Fm.ubic_BtNavSub_atrs)
            comanda = pariente.ir_sub_anterior
        else:
            raise ValueError

        super().__init__(pariente=pariente, comanda=comanda, img_norm=img_norm, img_bloq=img_bloq,
                         img_sel=img_sel, ubicación=ubicación, tipo_ubic='place',
                         formato=Fm.formato_BtsNavSub)


class BotónAltern(BotónImagen):
    def __init__(símismo, pariente, formato, img_1, img_2, img_bloq=None, comanda_segundaria=None,
                 ubicación=None, tipo_ubic=None):
        super().__init__(pariente, comanda=símismo.acción, formato=formato, img_norm=img_1,
                         img_sel=img_2, img_bloq=img_bloq,
                         ubicación=ubicación, tipo_ubic=tipo_ubic)
        símismo.img_1 = img_1
        símismo.img_2 = img_2
        símismo.comanda_segundaria = comanda_segundaria

        símismo.val = True

    def acción(símismo):
        símismo.poner(not símismo.val)
        if símismo.comanda_segundaria is not None:
            símismo.comanda_segundaria()

    def borrar(símismo):
        símismo.poner(True)

    def poner(símismo, valor):
        símismo.val = valor

        if símismo.val:
            símismo.formato_sel['image'] = símismo.img_2
            símismo.formato_norm['image'] = símismo.img_1
        else:
            símismo.formato_sel['image'] = símismo.img_1
            símismo.formato_norm['image'] = símismo.img_2

        símismo.bt.configure(image=símismo.formato_norm['image'])
