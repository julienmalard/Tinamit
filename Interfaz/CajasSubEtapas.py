import tkinter as tk
from tkinter import filedialog as diálogo
import os

from Interfaz import CajasGenéricas as CjG
from Interfaz import Botones as Bt
from Interfaz import Formatos as Fm
from Interfaz import ControlesGenéricos as CtrG
from Interfaz import Controles as Ctrl
from Interfaz import Arte as Art


class CajaSubEtp11(CjG.CajaSubEtapa):
    def __init__(símismo, pariente, apli, total):
        super().__init__(pariente, nombre=None, núm=1, total=total)
        símismo.apli = apli
        símismo.Modelo = apli.Modelo
        símismo.receta = símismo.Modelo.receta

        caja_mds = tk.Frame(símismo, **Fm.formato_cajas)
        caja_bf = tk.Frame(símismo, **Fm.formato_cajas)

        Bt.BotónTexto(caja_mds, texto=apli.Trads['CargarMDS'], comanda=símismo.buscar_mds,
                      formato_norm=Fm.formato_bts_cargar,
                      formato_sel=Fm.formato_bts_sel,
                      ubicación=Fm.ubic_bts_cargar_mod, tipo_ubic='place')
        símismo.EtiqErrCargarMDS = tk.Label(caja_mds, text=apli.Trads['ErrorCargarMDS'], **Fm.formato_etiq_error)
        símismo.EtiqMDSCargado = tk.Label(caja_mds, **Fm.formato_etiq_todobien)

        Bt.BotónTexto(caja_bf, texto=apli.Trads['CargarModeloBf'], comanda=símismo.buscar_bf,
                      formato_norm=Fm.formato_bts_cargar,
                      formato_sel=Fm.formato_bts_sel,
                      ubicación=Fm.ubic_bts_cargar_mod, tipo_ubic='place')
        símismo.EtiqErrCargarBf = tk.Label(caja_bf, text=apli.Trads['ErrorCargarBf'], **Fm.formato_etiq_error)
        símismo.EtiqBfCargado = tk.Label(caja_bf, **Fm.formato_etiq_todobien)

        caja_mds.place(**Fm.ubic_caja_cargar_mds)
        caja_bf.place(**Fm.ubic_caja_cargar_bf)

    def acción_desbloquear(símismo):
        símismo.EtiqErrCargarBf.pack_forget()
        símismo.EtiqErrCargarMDS.pack_forget()
        símismo.EtiqMDSCargado.pack_forget()
        símismo.EtiqBfCargado.pack_forget()

        símismo.verificar_completo()

    def buscar_mds(símismo):
        apli = símismo.apli
        nombre_archivo_mds = diálogo.askopenfilename(filetypes=[(apli.Trads['ModelospublicadosVENSIM'], '*.vpm')],
                                                     title=apli.Trads['CargarMDS'])
        if nombre_archivo_mds:
            rec = símismo.receta
            rec['mds'] = nombre_archivo_mds

            try:
                símismo.Modelo.actualizar()
                símismo.EtiqMDSCargado.config(text=apli.Trads['ModeloCargado'] % os.path.basename(nombre_archivo_mds))
                símismo.EtiqMDSCargado.pack(**Fm.ubic_EtiqCargarMod)
                símismo.EtiqErrCargarMDS.pack_forget()
            except ConnectionError:
                símismo.EtiqMDSCargado.pack_forget()
                símismo.EtiqErrCargarMDS.pack(**Fm.ubic_EtiqCargarMod)

            símismo.verificar_completo()

    def buscar_bf(símismo):
        apli = símismo.apli
        nombre_archivo_bf = diálogo.askopenfilename(filetypes=[(apli.Trads['ModelosPython'], '*.py')],
                                                    title=apli.Trads['CargarModeloBf'])
        if nombre_archivo_bf:
            rec = símismo.receta
            rec['bf'] = nombre_archivo_bf

            try:
                símismo.Modelo.actualizar()
                símismo.EtiqBfCargado.config(text=apli.Trads['ModeloCargado'] % os.path.basename(nombre_archivo_bf))
                símismo.EtiqBfCargado.pack(**Fm.ubic_EtiqCargarMod)
                símismo.EtiqErrCargarBf.pack_forget()
            except ConnectionError:
                símismo.EtiqBfCargado.pack_forget()
                símismo.EtiqErrCargarBf.pack(**Fm.ubic_EtiqCargarMod)

        símismo.verificar_completo()

    def verificar_completo(símismo):
        símismo.Modelo.actualizar()

        if símismo.Modelo.mds is not None and símismo.Modelo.bf is not None:
            símismo.pariente.desbloquear_cajas([2])
        else:
            símismo.pariente.bloquear_cajas([2])


class CajaSubEtp21(CjG.CajaSubEtapa):
    def __init__(símismo, pariente, apli, total):
        super().__init__(pariente, nombre=None, núm=1, total=total)
        símismo.apli = apli
        símismo.Modelo = símismo.apli.Modelo

        cj_bajo = tk.Frame(símismo, **Fm.formato_cajas)

        cj_ctrls = tk.Frame(cj_bajo, **Fm.formato_cajas)
        cj_izq = tk.Frame(cj_ctrls, **Fm.formato_cajas)
        símismo.MnVarsMDS = CtrG.Menú(cj_izq, nombre=apli.Trads['MDS'], opciones='', ancho=Fm.ancho_MnVars,
                                      ubicación=Fm.ubic_CtrlsConectar, tipo_ubic='pack')
        cj_med = tk.Frame(cj_ctrls, **Fm.formato_cajas)
        bt_dir = Bt.BotónAltern(cj_med, formato=Fm.formato_botones,
                                img_1=Art.imagen('BtConecciónIzqDer'), img_2=Art.imagen('BtConecciónDerIzq'),
                                ubicación=Fm.ubic_CtrlsConectar, tipo_ubic='pack')
        símismo.factor_conv = CtrG.IngrNúm(cj_med, límites=(0, None), val_inic=1, prec='dec', nombre=apli.Trads['X'],
                                           ubicación=Fm.ubic_CtrlsConectar, tipo_ubic='pack')
        cj_derech = tk.Frame(cj_ctrls, **Fm.formato_cajas)
        símismo.MnVarsBf = CtrG.Menú(cj_derech, nombre=apli.Trads['Biofísico'], opciones='', ancho=Fm.ancho_MnVars,
                                     ubicación=Fm.ubic_CtrlsConectar, tipo_ubic='pack')

        cj_bts = tk.Frame(cj_bajo, **Fm.formato_cajas)
        bt_guardar = Bt.BotónTexto(cj_bts, texto=apli.Trads['Guardar'],
                                   ubicación=Fm.ubic_BtsGrupo, tipo_ubic='pack',
                                   formato_norm=Fm.formato_BtGuardar_norm,
                                   formato_sel=Fm.formato_BtGuardar_sel,
                                   formato_bloq=Fm.formato_BtGuardars_bloq,
                                   )
        bt_borrar = Bt.BotónTexto(cj_bts, texto=apli.Trads['Borrar'],
                                  ubicación=Fm.ubic_BtsGrupo, tipo_ubic='pack',
                                  formato_norm=Fm.formato_BtBorrar_norm,
                                  formato_sel=Fm.formato_BtBorrar_sel,
                                  formato_bloq=Fm.formato_BtBorrars_bloq,
                                  )

        cj_izq.pack(**Fm.ubic_CjsCtrlsConectar)
        cj_med.pack(**Fm.ubic_CjMedCtrlsConectar)
        cj_derech.pack(**Fm.ubic_CjsCtrlsConectar)

        dic_controles = {'var_mds': símismo.MnVarsMDS, 'mds_fuente': bt_dir, 'conv': símismo.factor_conv,
                         'var_bf': símismo.MnVarsBf}

        símismo.lista = Ctrl.ListaConexiónes(símismo, apli, ubicación=Fm.ubic_CjLstConecciones, tipo_ubic='place')

        símismo.grupo_controles = Ctrl.GrpCtrlsConex(
                pariente=símismo,
                apli=apli, controles=dic_controles,
                lista=símismo.lista,
                bt_guardar=bt_guardar, bt_borrar=bt_borrar
        )

        cj_ctrls.place(**Fm.ubic_CjCtrlsConectar)
        cj_bts.place(**Fm.ubic_CjBtsConectar)
        cj_bajo.place(**Fm.ubic_CjBajoConex)

    def acción_desbloquear(símismo):
        símismo.Modelo.actualizar_conexiones()

        vars_mds = símismo.Modelo.vars_mds
        vars_bf = símismo.Modelo.vars_bf

        símismo.MnVarsMDS.refrescar(opciones=vars_mds)
        símismo.MnVarsBf.refrescar(opciones=vars_bf)

        for conex in símismo.Modelo.receta['conexiones']:
            Ctrl.ItemaConexión(grupo_control=símismo.grupo_controles, lista_itemas=símismo.lista,
                               receta=conex, creando_manual=False)

        símismo.verificar_completo()

    def añadir_conexión(símismo, conexión):
        símismo.MnVarsMDS.excluir(conexión['var_mds'])
        símismo.MnVarsBf.excluir(conexión['var_bf'])
        símismo.Modelo.conectar(conexión)

    def quitar_conexión(símismo, conexión):
        símismo.MnVarsMDS.reinstaurar(conexión['var_mds'])
        símismo.MnVarsBf.reinstaurar(conexión['var_bf'])
        símismo.Modelo.desconectar(conexión)

    def verificar_completo(símismo):
        if len(símismo.Modelo.receta['conexiones']):
            símismo.pariente.desbloquear_cajas([3, 4])
            return True
        else:
            símismo.pariente.bloquear_cajas([3, 4])
            return False


class CajaSubEtp31(CjG.CajaSubEtapa):
    def __init__(símismo, pariente, apli, total):
        super().__init__(pariente, nombre=None, núm=1, total=total)
        símismo.apli = apli
        símismo.Modelo = símismo.apli.Modelo

        cj_ctrls_tiempo = tk.Frame(símismo, **Fm.formato_cajas)

        cj_unidades_tiempo = tk.Frame(cj_ctrls_tiempo, **Fm.formato_cajas)
        etiq_1_tiempo_ref = tk.Label(cj_unidades_tiempo, text='1', **Fm.formato_EtiqCtrl)
        etiq_1_tiempo_ref.pack(**Fm.ubic_CtrlsUnidTiempo)
        símismo.MnTiempoRef = CtrG.Menú(cj_unidades_tiempo, opciones=[], ancho=7,
                                        comanda=símismo.acción_cambió_ref_unid,
                                        ubicación=Fm.ubic_CtrlsUnidTiempo, tipo_ubic='pack')
        símismo.IngrConvUnidTiempo = CtrG.IngrNúm(cj_unidades_tiempo, nombre='=',
                                                  límites=(0, None), prec='ent',
                                                  comanda=símismo.acción_cambió_conversión,
                                                  ubicación=Fm.ubic_CtrlsUnidTiempo, tipo_ubic='pack')
        símismo.EtiqUnidTiempoNoRef = tk.Label(cj_unidades_tiempo, text='Prueba', **Fm.formato_EtiqCtrl)
        símismo.EtiqUnidTiempoNoRef.pack(**Fm.ubic_CtrlsUnidTiempo)
        cj_unidades_tiempo.pack(**Fm.ubic_CtrlsTiempo)

        cj_tiempo_final = tk.Frame(cj_ctrls_tiempo, **Fm.formato_cajas)
        símismo.IngrTempFinal = CtrG.IngrNúm(cj_tiempo_final, nombre=apli.Trads['TiempoFinal'],
                                             límites=(0, None), lím_incl=False, prec='ent', val_inic=100,
                                             ubicación=Fm.ubic_CtrlsUnidTiempo, tipo_ubic='pack')
        símismo.EtiqUnidTiempoFinal = tk.Label(cj_tiempo_final, **Fm.formato_EtiqCtrl)
        símismo.EtiqUnidTiempoFinal.pack(**Fm.ubic_CtrlsTiempo)
        cj_tiempo_final.pack(**Fm.ubic_CtrlsTiempo)

        cj_bt_simul = tk.Frame(símismo, **Fm.formato_cajas)
        símismo.BtSimul = Bt.BotónTexto(cj_bt_simul, texto=apli.Trads['Simular'], comanda=símismo.acción_simular,
                                        formato_norm=Fm.formato_bt_simular,
                                        formato_sel=Fm.formato_bts_sel,
                                        ubicación=Fm.ubic_bt_simular, tipo_ubic='pack')

        símismo.CjSimulando = tk.Frame(cj_bt_simul, **Fm.formato_CjSimulando)
        etiq_simulando = tk.Label(símismo.CjSimulando, text=apli.Trads['Simulando'], **Fm.formato_etiq_simulando)
        etiq_simulando.place(**Fm.ubic_EtiqSimulando)

        cj_ctrls_tiempo.place(**Fm.ubic_CjCtrlsTiempo)
        cj_bt_simul.place(**Fm.ubic_cj_bt_simular)

    def acción_desbloquear(símismo):
        unidades_tiempo_mds = símismo.Modelo.mds.unidades_tiempo
        unidades_tiempo_bf = símismo.Modelo.bf.unidades_tiempo
        símismo.MnTiempoRef.refrescar(opciones=[unidades_tiempo_mds, unidades_tiempo_bf])
        if símismo.Modelo.receta['ref_tiempo_mds']:
            símismo.MnTiempoRef.poner(unidades_tiempo_mds)
        else:
            símismo.MnTiempoRef.poner(unidades_tiempo_bf)
        símismo.IngrConvUnidTiempo.poner(símismo.Modelo.receta['conv_unid_tiempo'])

        símismo.verificar_completo()

    def acción_cambió_ref_unid(símismo, val):
        unidades_tiempo_mds = símismo.Modelo.mds.unidades_tiempo
        unidades_tiempo_bf = símismo.Modelo.bf.unidades_tiempo
        print(unidades_tiempo_mds, unidades_tiempo_bf)

        if val == unidades_tiempo_mds:
            símismo.Modelo.receta['ref_tiempo_mds'] = True
            símismo.EtiqUnidTiempoFinal.config(text=unidades_tiempo_mds)
            símismo.EtiqUnidTiempoNoRef.config(text=unidades_tiempo_bf)
        else:
            símismo.Modelo.receta['ref_tiempo_mds'] = False
            símismo.EtiqUnidTiempoFinal.config(text=unidades_tiempo_bf)
            símismo.EtiqUnidTiempoNoRef.config(text=unidades_tiempo_mds)

    def acción_cambió_conversión(símismo, val):
        símismo.Modelo.receta['conv_unid_tiempo'] = val

    def acción_simular(símismo):
        símismo.CjSimulando.pack(**Fm.ubic_CjSimulando)
        símismo.BtSimul.bloquear()

        símismo.Modelo.simular(tiempo_final=símismo.IngrTempFinal.val)

        símismo.BtSimul.desbloquear()
        símismo.CjSimulando.pack_forget()


class CajaSubEtp41(CjG.CajaSubEtapa):
    def __init__(símismo, pariente, apli, total):
        super().__init__(pariente, nombre=None, núm=1, total=total)
        símismo.apli = apli
        símismo.Modelo = símismo.apli.Modelo

    def acción_desbloquear(símismo):
        pass

    def verificar_completo(símismo):
        pass
