import tkinter as tk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from Interfaz import Arte as Art
from Interfaz import Formatos as Fm
from Interfaz import Botones as Bt


class ListaItemas(tk.Frame):
    def __init__(símismo, pariente, ubicación, tipo_ubic, encabezado=False, formato_cj=Fm.formato_CjLstItemas):
        super().__init__(pariente, **formato_cj)
        símismo.ancho = ubicación['width']
        símismo.objetos = {}

        ubic_tela = Fm.ubic_TlLstItemas.copy()
        if encabezado:
            ubic_tela['y'] = Fm.ubic_EncbzLstItemas['height']
            ubic_tela['height'] = -Fm.ubic_EncbzLstItemas['height']
        símismo.Tela = tk.Canvas(símismo, **Fm.formato_TlLstItemas)
        símismo.Tela.place(**ubic_tela)
        símismo.Caja = tk.Frame(símismo.Tela, **Fm.formato_cajas)
        símismo.BaraDesp = tk.Scrollbar(símismo.Tela, orient="vertical", command=símismo.Tela.yview)
        símismo.Tela.configure(yscrollcommand=símismo.BaraDesp.set)

        símismo.BaraDesp.pack(**Fm.ubic_BaraDesp)

        símismo.Tela.create_window((1, 1), window=símismo.Caja, tags="self.frame", width=símismo.ancho-20,
                                   **Fm.ubic_CjTl)

        símismo.Caja.bind("<Configure>", símismo.ajust_auto)

        if tipo_ubic == 'pack:':
            símismo.pack(**ubicación)
        elif tipo_ubic == 'place':
            símismo.place(**ubicación)

    def ajust_auto(símismo, evento):
        símismo.Tela.configure(scrollregion=símismo.Tela.bbox("all"))

    def añadir(símismo, itema):
        itema.pack(**Fm.ubic_CjItemas)


class ListaEditable(ListaItemas):
    def __init__(símismo, pariente, ubicación, tipo_ubic):
        super().__init__(pariente, ubicación=ubicación, tipo_ubic=tipo_ubic, encabezado=True)
        símismo.controles = None

    def gen_encbz(símismo, nombres_cols, anchuras):
        cj_encbz = tk.Frame(símismo, **Fm.formato_cajas)

        ancho_bts = Fm.ancho_cj_bts_itemas
        x = [-ancho_bts*n/len(anchuras) for n in range(len(anchuras))]
        relx = [np.sum(anchuras[:n]) for n in range(len(anchuras))]
        ajust_ancho = [0] * (len(anchuras)-1) + [ancho_bts]
        cols = []
        for n, col in enumerate(nombres_cols):
            cols.append(tk.Label(cj_encbz, text=col, **Fm.formato_EtiqEncbzLst))
            cols[-1].place(relx=relx[n], x=x[n], width=ajust_ancho[n], relwidth=anchuras[n],
                           **Fm.ubic_ColsEncbzLst)

        cj_encbz.place(**Fm.ubic_EncbzLstItemas)

    def editar(símismo, itema):
        símismo.controles.editar(itema)

    def añadir(símismo, itema):
        símismo.objetos[itema.objeto.nombre] = itema.objeto
        super().añadir(itema)

    def quitar(símismo, itema):
        símismo.controles.borrar()
        símismo.objetos.pop(itema.objeto.nombre)
        itema.destroy()


class Itema(tk.Frame):
    def __init__(símismo, lista_itemas, objeto=None):
        super().__init__(lista_itemas.Caja, **Fm.formato_cajas)
        símismo.objeto = objeto
        símismo.lista = lista_itemas

        símismo.lista.añadir(símismo)

    def quitar(símismo):
        símismo.lista.quitar(símismo)


class ItemaEditable(Itema):
    def __init__(símismo, grupo_control, lista_itemas):
        super().__init__(lista_itemas, grupo_control.objeto)
        símismo.receta = grupo_control.receta
        símismo.lista_itemas = lista_itemas
        símismo.columnas = []

        símismo.cj_cols = NotImplemented

        símismo.cj_bts = tk.Frame(símismo, **Fm.formato_cajas)

        símismo.bt_editar = Bt.BotónImagen(símismo.cj_bts, comanda=símismo.editar, formato=Fm.formato_botones,
                                           img_norm=Art.imagen('BtEditarItema_norm'),
                                           img_sel=Art.imagen('BtEditarItema_sel'),
                                           ubicación=Fm.ubic_BtsItemas, tipo_ubic='pack')
        símismo.bt_borrar = Bt.BotónImagen(símismo.cj_bts, comanda=símismo.quitar, formato=Fm.formato_botones,
                                           img_norm=Art.imagen('BtBorrarItema_norm'),
                                           img_sel=Art.imagen('BtBorrarItema_sel'),
                                           ubicación=Fm.ubic_BtsItemas, tipo_ubic='pack')

        símismo.bind('<Enter>', lambda event, i=símismo: i.resaltar())
        símismo.bind('<Leave>', lambda event, i=símismo: i.desresaltar())

    def estab_columnas(símismo, anchuras):
        x = [np.sum(anchuras[:n]) for n in range(len(anchuras))]
        for n, col in enumerate(símismo.columnas):
            col.place(relx=x[n], relwidth=anchuras[n], **Fm.ubic_ColsItemasEdit)

        símismo.cj_cols.pack(**Fm.ubic_CjColsItemas)
        símismo.cj_bts.pack(**Fm.ubic_CjBtsItemas)

    def editar(símismo):
        símismo.lista.editar(símismo)

    def actualizar(símismo):
        raise NotImplementedError

    def resaltar(símismo):
        raise NotImplementedError

    def desresaltar(símismo):
        raise NotImplementedError


class GrupoControles(object):
    def __init__(símismo, controles, constructor_itema=None, itema=None, gráfico=None, lista=None,
                 bt_guardar=None, bt_borrar=None):
        símismo.controles = controles
        símismo.constructor_itema = constructor_itema
        símismo.itema = itema
        símismo.gráfico = gráfico
        símismo.lista = lista
        símismo.bt_guardar = bt_guardar
        símismo.bt_borrar = bt_borrar
        símismo.objeto = None
        símismo.receta = {}

        for ll in símismo.controles:
            símismo.controles[ll].comanda = símismo.cambió_control

        if símismo.lista is not None:
            símismo.lista.controles = símismo

        if símismo.gráfico is not None:
            símismo.gráfico.controles = símismo.controles

        if símismo.bt_guardar is not None:
            símismo.bt_guardar.estab_comanda(símismo.guardar)
            símismo.bt_guardar.bloquear()
        if símismo.bt_borrar is not None:
            símismo.bt_borrar.estab_comanda(símismo.borrar)
            símismo.bt_borrar.bloquear()

    def cambió_control(símismo, *args):

        if símismo.bt_borrar is not None:
            símismo.bt_borrar.desbloquear()
        if símismo.verificar_completo() is True:
            símismo.recrear_objeto()
            if símismo.gráfico is not None:
                símismo.gráfico.objeto = símismo.objeto
                símismo.gráfico.redibujar()
            if símismo.itema is not None:
                símismo.lista.objeto = símismo.objeto
            if símismo.bt_guardar is not None:
                símismo.bt_guardar.desbloquear()
        else:
            if símismo.bt_guardar is not None:
                símismo.bt_guardar.bloquear()

    def guardar(símismo, borrar=True):
        if símismo.itema is not None:
            símismo.itema.actualizar()
        elif símismo.constructor_itema is not None:
            símismo.itema = símismo.constructor_itema(símismo, símismo.lista)

        if borrar:
            símismo.borrar()
            símismo.itema = None

    def borrar(símismo):
        símismo.objeto = None
        símismo.receta = {}
        for ll, control in símismo.controles.items():
            control.confirmar_borrar()

        if símismo.gráfico is not None:
            símismo.gráfico.confirmar_borrar()

        if símismo.bt_guardar is not None:
            símismo.bt_guardar.bloquear()
        if símismo.bt_borrar is not None:
            símismo.bt_borrar.bloquear()

    def editar(símismo, itema):
        símismo.borrar()
        símismo.itema = itema
        símismo.objeto = itema.objeto
        for i in itema.receta:
            símismo.controles[i].poner(itema.receta[i])

        símismo.receta = itema.receta

    def verificar_completo(símismo):
        raise NotImplementedError

    def recrear_objeto(símismo):
        raise NotImplementedError


class Gráfico(object):
    def __init__(símismo, pariente, ubicación, tipo_ubic):
        símismo.objeto = None
        símismo.controles = None

        cuadro = Figure()
        cuadro.patch.set_facecolor(Fm.col_fondo)
        símismo.fig = cuadro.add_subplot(111)
        símismo.tela = FigureCanvasTkAgg(cuadro, master=pariente)
        símismo.tela.show()

        if tipo_ubic == 'place':
            símismo.tela.get_tk_widget().place(**ubicación)
        elif tipo_ubic == 'pack':
            símismo.tela.get_tk_widget().pack(**ubicación)

    def redibujar(símismo):
        símismo.borrar()
        símismo.dibujar()
        símismo.tela.draw()

    def borrar(símismo):
        while len(símismo.fig.patches):
            símismo.fig.patches[0].remove()
        while len(símismo.fig.lines):
            símismo.fig.lines[0].remove()
        símismo.tela.draw()

    def dibujar(símismo):
        raise NotImplementedError


class CampoIngreso(object):
    def __init__(símismo, pariente, nombre, val_inic, comanda, ubicación, tipo_ubic, ancho, orden='texto'):
        símismo.comanda = comanda
        símismo.val_inic = val_inic

        símismo.var = tk.StringVar()
        símismo.var.set(símismo.val_inic)
        símismo.var.trace('w', símismo.acción_cambió)

        símismo.val = val_inic

        cj = tk.Frame(pariente, **Fm.formato_cajas)

        símismo.CampoIngr = tk.Entry(cj, textvariable=símismo.var, width=ancho, **Fm.formato_CampoIngr)

        if nombre is not None:
            símismo.Etiq = tk.Label(cj, text=nombre, **Fm.formato_EtiqCtrl)

        if orden is 'texto':
            if nombre is not None:
                símismo.Etiq.pack(**Fm.ubic_EtiqIngrNúm)
            símismo.CampoIngr.pack(**Fm.ubic_CampoIngrEscl)
        else:
            símismo.CampoIngr.pack(**Fm.ubic_CampoIngrEscl)
            if nombre is not None:
                símismo.Etiq.pack(**Fm.ubic_EtiqIngrNúm)

        if tipo_ubic == 'pack':
            cj.pack(**ubicación)
        elif tipo_ubic == 'place':
            cj.place(**ubicación)

    def acción_cambió(símismo, *args):
        nueva_val = símismo.var.get()

        try:
            nueva_val = símismo.validar_ingreso(nueva_val)
            símismo.CampoIngr.config(**Fm.formato_CampoIngr)

            if nueva_val == '':
                símismo.val = None
                return
            if nueva_val != símismo.val:
                símismo.val = nueva_val
                símismo.comanda(nueva_val)

        except ValueError:
            símismo.var.set('')
            símismo.val = None
            símismo.CampoIngr.config(**Fm.formato_CampoIngr_error)
            return

    def borrar(símismo):
        símismo.var.set(símismo.val_inic)

    def bloquear(símismo):
        símismo.CampoIngr.configure(state=tk.DISABLED, cursor='X_cursor', **Fm.formato_BtMn_bloq)
        símismo.Etiq.config(**Fm.formato_EtiqCtrl_bloq)

    def desbloquear(símismo):
        símismo.CampoIngr.configure(state=tk.NORMAL, cursor='arrow', **Fm.formato_BtMn)
        símismo.Etiq.config(**Fm.formato_EtiqCtrl)

    def poner(símismo, valor):
        símismo.var.set(str(valor))

    def validar_ingreso(símismo, nueva_val):
        raise NotImplementedError


class IngrNúm(CampoIngreso):
    def __init__(símismo, pariente, límites, prec, ubicación, tipo_ubic, ancho=5, comanda=None,
                 nombre=None, val_inic='', orden='texto'):

        if prec not in ['dec', 'ent']:
            raise ValueError('"Prec" debe ser uno de "ent" o "dec".')
        símismo.prec = prec

        símismo.val_inic = val_inic

        if límites is None:
            límites = (float('-Inf'), float('Inf'))
        símismo.límites = límites

        super().__init__(pariente, nombre, val_inic, comanda, ubicación, tipo_ubic, ancho, orden=orden)

    def validar_ingreso(símismo, nueva_val):
        if símismo.prec == 'ent':
            nueva_val = int(nueva_val)
        elif símismo.prec == 'dec':
            nueva_val = round(float(nueva_val), 3)
        else:
            raise KeyError('"Prec" debe ser uno de "ent" o "dec".')

        if not (símismo.límites[0] <= nueva_val <= símismo.límites[1]):
            raise ValueError

        return nueva_val


class IngrTexto(CampoIngreso):
    def __init__(símismo, pariente, nombre, ubicación, tipo_ubic, comanda=None):
        super().__init__(pariente, nombre=nombre, val_inic='', comanda=comanda,
                         ubicación=ubicación, tipo_ubic=tipo_ubic, ancho=20)

    def validar_ingreso(símismo, nueva_val):
        return nueva_val


class Menú(object):
    def __init__(símismo, pariente, opciones, ubicación, tipo_ubic,
                 nombre=None, comanda=None, texto_opciones=None, inicial='',
                 formato_bt=Fm.formato_BtMn, formato_mn=Fm.formato_MnMn, ancho=15):
        símismo.opciones = opciones
        if texto_opciones is None:
            texto_opciones = opciones
        símismo.conv = {}

        símismo.comanda = comanda

        símismo.val_inicial = inicial
        símismo.var = tk.StringVar()

        símismo.val = inicial
        símismo.exclusivos = []

        cj = tk.Frame(pariente, **Fm.formato_cajas)

        if nombre is not None:
            símismo.Etiq = tk.Label(cj, text=nombre, **Fm.formato_EtiqCtrl)
            símismo.Etiq.pack(**Fm.ubic_EtiqMenú)

        símismo.MenúOpciones = tk.OptionMenu(cj, símismo.var, '')
        símismo.MenúOpciones.config(takefocus=True)
        símismo.refrescar(opciones, texto_opciones)
        símismo.var.trace('w', símismo.acción_cambió)

        símismo.MenúOpciones.config(width=ancho, **formato_bt)
        símismo.MenúOpciones['menu'].config(**formato_mn)

        símismo.MenúOpciones.pack(**Fm.ubic_Menú)

        if tipo_ubic == 'pack':
            cj.pack(**ubicación)
        elif tipo_ubic == 'place':
            cj.place(**ubicación)

    def estab_exclusivo(símismo, otro_menú):
        assert type(otro_menú) is Menú
        if otro_menú not in símismo.exclusivos:
            símismo.exclusivos.append(otro_menú)
        if símismo not in otro_menú.exclusivos:
            otro_menú.estab_exclusivo(símismo)

    def refrescar(símismo, opciones, texto_opciones=None):
        símismo.opciones = opciones
        if texto_opciones is None:
            texto_opciones = opciones

        símismo.MenúOpciones['menu'].delete(0, 'end')

        símismo.conv = {'': ''}
        for op, tx in zip(opciones, texto_opciones):
            símismo.conv[op] = tx
            símismo.MenúOpciones['menu'].add_command(label=tx, command=tk._setit(símismo.var, tx))

        símismo.borrar()

    def acción_cambió(símismo, *args):
        texto_campo = símismo.var.get()
        nueva_val = [ll for ll, v in símismo.conv.items() if v == texto_campo][0]

        if nueva_val == '':
            símismo.val = None
            return

        if nueva_val != símismo.val:
            for menú in símismo.exclusivos:
                menú.excluir(nueva_val)
                if símismo.val is not None:
                    menú.reinstaurar(símismo.val)

            símismo.val = nueva_val
            símismo.comanda(nueva_val)

    def excluir(símismo, valor):
        menú = símismo.MenúOpciones['menu']
        i = símismo.opciones.index(valor)
        menú.entryconfig(i, state=tk.DISABLED)

    def reinstaurar(símismo, valor):
        menú = símismo.MenúOpciones['menu']
        i = símismo.opciones.index(valor)
        menú.entryconfig(i, state=tk.NORMAL)

    def borrar(símismo):
        símismo.val = símismo.val_inicial
        símismo.var.set(símismo.conv[símismo.val])

    def bloquear(símismo):
        símismo.MenúOpciones.configure(state=tk.DISABLED, cursor='X_cursor', **Fm.formato_BtMn_bloq)
        símismo.Etiq.config(**Fm.formato_EtiqCtrl_bloq)

    def desbloquear(símismo):
        símismo.MenúOpciones.configure(state=tk.NORMAL, cursor='arrow', **Fm.formato_BtMn)
        símismo.Etiq.config(**Fm.formato_EtiqCtrl)

    def poner(símismo, valor):
        símismo.var.set(símismo.conv[valor])
        símismo.val = valor


class Escala(object):
    def __init__(símismo, pariente, texto, límites, prec, ubicación, tipo_ubic, comanda=None, valor_inicial=None):
        símismo.cj = tk.Frame(pariente, **Fm.formato_cajas)
        símismo.comanda = comanda
        if valor_inicial is None:
            valor_inicial = (límites[0] + límites[1])/2
        símismo.valor_inicial = valor_inicial

        símismo.val = símismo.valor_inicial

        símismo.etiq = tk.Label(símismo.cj, text=texto, **Fm.formato_EtiqCtrl)

        etiq_inic = tk.Label(símismo.cj, text=límites[0], **Fm.formato_EtiqNúmEscl)
        símismo.escl = CosoEscala(símismo, límites, val_inic=valor_inicial, prec=prec)
        etiq_fin = tk.Label(símismo.cj, text=límites[1], **Fm.formato_EtiqNúmEscl)

        símismo.etiq.pack(**Fm.ubic_EtiqEscl)
        etiq_inic.pack(**Fm.ubic_EtiqNúmEscl)
        símismo.escl.pack(**Fm.ubic_Escl)
        etiq_fin.pack(**Fm.ubic_EtiqNúmEscl)

        símismo.ingr = IngrNúm(símismo.cj, nombre=None, límites=límites, val_inic=valor_inicial, prec=prec,
                               ubicación=Fm.ubic_CampoIngrEscl, tipo_ubic='pack',
                               comanda=símismo.cambio_ingr)

        if tipo_ubic == 'pack':
            símismo.cj.pack(**ubicación)
        elif tipo_ubic == 'place':
            símismo.cj.place(**ubicación)

    def cambio_ingr(símismo, val):
        if val != símismo.escl.val:
            símismo.escl.poner(float(val))
            símismo.val = float(val)
            if símismo.comanda is not None:
                símismo.comanda(val)

    def cambio_escl(símismo, val):
        if str(val) != símismo.val:
            símismo.val = val
            símismo.ingr.var.set(val)

            if símismo.comanda is not None:
                símismo.comanda(val)

    def borrar(símismo):
        pass
        # símismo.escl.poner(símismo.valor_inicial)
        # símismo.ingr.var.set(símismo.valor_inicial)
        # símismo.val = símismo.valor_inicial

    def poner(símismo, valor):
        símismo.escl.poner(valor)
        símismo.ingr.var.set(valor)
        símismo.val = valor


class CosoEscala(tk.Canvas):
    def __init__(símismo, pariente, límites, val_inic, ancho=150, altura=30, prec='cont'):
        super().__init__(pariente.cj, width=ancho, height=altura, background=Fm.col_fondo, highlightthickness=0)

        símismo.dim = (ancho, altura)
        símismo.límites = límites
        símismo.pariente = pariente
        símismo.tipo = prec
        símismo.val = val_inic

        símismo.create_rectangle(0, 0, 1, altura, **Fm.formato_lín_escl)
        símismo.create_rectangle(ancho-2, 0, ancho, altura, **Fm.formato_lín_escl)
        símismo.create_line(0, round(altura/2), ancho, round(altura/2), fill=Fm.col_1)

        símismo.info_mov = {"x": 0, "y": 0}

        símismo.manilla = símismo.create_rectangle(float(ancho / 2) - 3, 0, float(ancho / 2) + 3, altura,
                                                   outline=Fm.col_5, fill=Fm.col_5)

        símismo.tag_bind(símismo.manilla, "<ButtonPress-1>", símismo.acción_empujar)
        símismo.tag_bind(símismo.manilla, "<ButtonRelease-1>", símismo.acción_soltar)
        símismo.tag_bind(símismo.manilla, "<B1-Motion>", símismo.acción_movimiento)
        símismo.bind("<ButtonRelease-1>", símismo.acción_soltar)

        símismo.poner(símismo.val)

    def acción_empujar(símismo, event):
        símismo.info_mov["x"] = (símismo.coords(símismo.manilla)[0] + símismo.coords(símismo.manilla)[2])/2

    def acción_soltar(símismo, event):
        símismo.info_mov["x"] = 0

    def acción_movimiento(símismo, event):
        x = event.x
        if x > símismo.dim[0]:
            x = símismo.dim[0]
        elif x < 0:
            x = 0

        símismo.val = round(x/símismo.dim[0] * (símismo.límites[1] - símismo.límites[0]) + símismo.límites[0], 3)

        if símismo.tipo == 'ent':
            símismo.val = int(símismo.val)
            x = (símismo.val - símismo.límites[0])/(símismo.límites[1] - símismo.límites[0])*símismo.dim[0]

        delta_x = x - símismo.info_mov["x"]

        símismo.move(símismo.manilla, delta_x, 0)

        símismo.info_mov["x"] = x

        símismo.pariente.cambio_escl(símismo.val)

    def poner(símismo, val):
        símismo.val = val
        x_manilla = (símismo.coords(símismo.manilla)[0] + símismo.coords(símismo.manilla)[2])/2
        nuevo_x = (símismo.val - símismo.límites[0])/(símismo.límites[1] - símismo.límites[0])*símismo.dim[0]
        delta_x = nuevo_x - x_manilla
        símismo.move(símismo.manilla, delta_x, 0)
