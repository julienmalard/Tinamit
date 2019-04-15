import os
import tkinter as tk
from tkinter import filedialog as diálogo

from . import Arte as Art
from . import Botones as Bt
from . import CajasGenéricas as CjG
from . import Controles as Ctrl
from . import ControlesGenéricos as CtrG
from . import Formatos as Fm
from .Formatos import gen_formato as gf


class CajaSubEtp11(CjG.CajaSubEtapa):
    def __init__(símismo, pariente, apli, total):
        super().__init__(pariente, nombre=None, núm=1, total=total)
        símismo.apli = apli
        símismo.apli.Modelo = apli.Modelo

        caja_mds = tk.Frame(símismo, **Fm.formato_cajas)
        caja_bf = tk.Frame(símismo, **Fm.formato_cajas)

        Bt.BotónTexto(caja_mds, texto=apli.Trads['CargarMDS'], comanda=símismo.buscar_mds,
                      formato_norm=Fm.formato_bts_cargar,
                      formato_sel=Fm.formato_bts_sel,
                      ubicación=gf(Fm.ubic_bts_cargar_mod), tipo_ubic='place')
        símismo.EtiqErrCargarMDS = tk.Label(caja_mds, text=apli.Trads['ErrorCargarMDS'], **Fm.formato_etiq_error)
        símismo.EtiqMDSCargado = tk.Label(caja_mds, **Fm.formato_etiq_todobien)

        Bt.BotónTexto(caja_bf, texto=apli.Trads['CargarModeloBf'], comanda=símismo.buscar_bf,
                      formato_norm=Fm.formato_bts_cargar,
                      formato_sel=Fm.formato_bts_sel,
                      ubicación=gf(Fm.ubic_bts_cargar_mod), tipo_ubic='place')
        símismo.EtiqErrCargarBf = tk.Label(caja_bf, text=apli.Trads['ErrorCargarBf'], **Fm.formato_etiq_error)
        símismo.EtiqBfCargado = tk.Label(caja_bf, **Fm.formato_etiq_todobien)

        caja_mds.place(**gf(Fm.ubic_caja_cargar_mds))
        caja_bf.place(**gf(Fm.ubic_caja_cargar_bf))

    def acción_desbloquear(símismo):
        apli = símismo.apli

        símismo.EtiqErrCargarBf.pack_forget()
        símismo.EtiqErrCargarMDS.pack_forget()
        símismo.EtiqMDSCargado.pack_forget()
        símismo.EtiqBfCargado.pack_forget()

        if símismo.apli.Modelo.mds is not None:
            símismo.EtiqMDSCargado.config(text=apli.Trads['ModeloCargado'] % símismo.apli.Modelo.mds.nombre)
            símismo.EtiqMDSCargado.pack(**gf(Fm.ubic_EtiqCargarMod))

        if símismo.apli.Modelo.bf is not None:
            símismo.EtiqBfCargado.config(text=apli.Trads['ModeloCargado'] % símismo.apli.Modelo.bf.nombre)
            símismo.EtiqBfCargado.pack(**gf(Fm.ubic_EtiqCargarMod))

        símismo.verificar_completo()

    def buscar_mds(símismo):
        apli = símismo.apli
        archivo_mds = diálogo.askopenfilename(filetypes=[(apli.Trads['ModelospublicadosVENSIM'], '*.vpm'),
                                                         (apli.Trads['ModelosVensim'], '*.mdl'),
                                                         (apli.Trads['ModelosXMILE'], '*.xmile'),
                                                         (apli.Trads['ModelosXMILE'], '*.xml')],
                                              title=apli.Trads['CargarMDS'])
        if archivo_mds:
            símismo.apli.receta['mds'] = archivo_mds

            try:
                símismo.apli.Modelo.estab_mds(archivo_mds)
                símismo.EtiqMDSCargado.config(text=apli.Trads['ModeloCargado'] % os.path.basename(archivo_mds))
                símismo.EtiqMDSCargado.pack(**gf(Fm.ubic_EtiqCargarMod))
                símismo.EtiqErrCargarMDS.pack_forget()
            except (OSError, FileNotFoundError, ValueError):
                símismo.EtiqMDSCargado.pack_forget()
                símismo.EtiqErrCargarMDS.pack(**gf(Fm.ubic_EtiqCargarMod))

            símismo.verificar_completo()

    def buscar_bf(símismo):
        apli = símismo.apli
        nombre_archivo_bf = diálogo.askopenfilename(filetypes=[(apli.Trads['ModelosPython'], '*.py')],
                                                    title=apli.Trads['CargarModeloBf'])
        if nombre_archivo_bf:
            símismo.apli.receta['bf'] = nombre_archivo_bf

            try:
                símismo.apli.Modelo.estab_bf(nombre_archivo_bf)
                símismo.EtiqBfCargado.config(text=apli.Trads['ModeloCargado'] % os.path.basename(nombre_archivo_bf))
                símismo.EtiqBfCargado.pack(**gf(Fm.ubic_EtiqCargarMod))
                símismo.EtiqErrCargarBf.pack_forget()
            except (AttributeError, FileNotFoundError):
                símismo.EtiqBfCargado.pack_forget()
                símismo.EtiqErrCargarBf.pack(**gf(Fm.ubic_EtiqCargarMod))

        símismo.verificar_completo()

    def verificar_completo(símismo):

        if símismo.apli.Modelo.mds is not None and símismo.apli.Modelo.bf is not None:
            símismo.pariente.desbloquear_cajas([2])
        else:
            símismo.pariente.bloquear_cajas([2])


class CajaSubEtp21(CjG.CajaSubEtapa):
    def __init__(símismo, pariente, apli, total):
        super().__init__(pariente, nombre=None, núm=1, total=total)
        símismo.apli = apli
        símismo.apli.Modelo = símismo.apli.Modelo

        cj_bajo = tk.Frame(símismo, **Fm.formato_cajas)

        cj_ctrls = tk.Frame(cj_bajo, **Fm.formato_cajas)
        cj_izq = tk.Frame(cj_ctrls, **Fm.formato_cajas)
        símismo.MnVarsMDS = CtrG.Menú(cj_izq, nombre=apli.Trads['mds'], opciones='', ancho=Fm.ancho_MnVars,
                                      ubicación=gf(Fm.ubic_CtrlsConectar), tipo_ubic='pack')
        símismo.EtiqUnidMDS = tk.Label(cj_izq, text='', **Fm.formato_EtiqsUnid)
        símismo.EtiqUnidMDS.pack(**gf(Fm.ubic_EtiqsUnid))

        cj_med = tk.Frame(cj_ctrls, **Fm.formato_cajas)
        if Fm.IzqaDerech:
            img_1 = Art.imagen('BtConecciónIzqDer')
            img_2 = Art.imagen('BtConecciónDerIzq')
        else:
            img_1 = Art.imagen('BtConecciónDerIzq')
            img_2 = Art.imagen('BtConecciónIzqDer')

        símismo.BtMDSFuente = Bt.BotónAltern(cj_med, formato=Fm.formato_botones,
                                             comanda_segundaria=símismo.actualizar_menús,
                                             img_1=img_1, img_2=img_2,
                                             ubicación=gf(Fm.ubic_CtrlsConectar), tipo_ubic='pack')
        símismo.factor_conv = CtrG.IngrNúm(cj_med, límites=(0, None), val_inic=1, prec='dec', nombre=apli.Trads['X'],
                                           ubicación=gf(Fm.ubic_CtrlsConectar), tipo_ubic='pack')
        cj_derech = tk.Frame(cj_ctrls, **Fm.formato_cajas)
        símismo.MnVarsBf = CtrG.Menú(cj_derech, nombre=apli.Trads['Biofísico'], opciones='', ancho=Fm.ancho_MnVars,
                                     ubicación=gf(Fm.ubic_CtrlsConectar), tipo_ubic='pack')
        símismo.EtiqUnidBf = tk.Label(cj_derech, text='', **Fm.formato_EtiqsUnid)
        símismo.EtiqUnidBf.pack(**gf(Fm.ubic_EtiqsUnid))

        cj_bts = tk.Frame(cj_bajo, **Fm.formato_cajas)
        bt_guardar = Bt.BotónTexto(cj_bts, texto=apli.Trads['Guardar'],
                                   ubicación=gf(Fm.ubic_BtsGrupo), tipo_ubic='pack',
                                   formato_norm=Fm.formato_BtGuardar_norm,
                                   formato_sel=Fm.formato_BtGuardar_sel,
                                   formato_bloq=Fm.formato_BtGuardars_bloq,
                                   )
        bt_borrar = Bt.BotónTexto(cj_bts, texto=apli.Trads['Borrar'],
                                  ubicación=gf(Fm.ubic_BtsGrupo), tipo_ubic='pack',
                                  formato_norm=Fm.formato_BtBorrar_norm,
                                  formato_sel=Fm.formato_BtBorrar_sel,
                                  formato_bloq=Fm.formato_BtBorrars_bloq,
                                  )

        cj_izq.pack(**gf(Fm.ubic_CjsCtrlsConectar))
        cj_med.pack(**gf(Fm.ubic_CjMedCtrlsConectar))
        cj_derech.pack(**gf(Fm.ubic_CjsCtrlsConectar))

        dic_controles = {'var_mds': símismo.MnVarsMDS, 'mds_fuente': símismo.BtMDSFuente,
                         'conv': símismo.factor_conv, 'var_bf': símismo.MnVarsBf}

        símismo.lista = Ctrl.ListaConexiónes(símismo, apli, ubicación=gf(Fm.ubic_CjLstConecciones), tipo_ubic='place')

        símismo.grupo_controles = Ctrl.GrpCtrlsConex(
            pariente=símismo,
            apli=apli, controles=dic_controles,
            lista=símismo.lista,
            bt_guardar=bt_guardar, bt_borrar=bt_borrar,
            comanda=símismo.actualizar_unidades
        )

        cj_ctrls.place(**gf(Fm.ubic_CjCtrlsConectar))
        cj_bts.place(**gf(Fm.ubic_CjBtsConectar))
        cj_bajo.place(**gf(Fm.ubic_CjBajoConex))

    def acción_desbloquear(símismo):

        símismo.lista.borrar()

        vars_mds = sorted(list(símismo.apli.Modelo.mds.variables))
        vars_bf = sorted(list(símismo.apli.Modelo.bf.variables))
        símismo.MnVarsMDS.refrescar(opciones=vars_mds)
        símismo.MnVarsBf.refrescar(opciones=vars_bf)

        for conex in símismo.apli.receta['conexiones']:
            Ctrl.ItemaConexión(grupo_control=símismo.grupo_controles, lista_itemas=símismo.lista,
                               receta=conex, creando_manual=False)

        símismo.actualizar_menús()
        símismo.verificar_completo()

    def actualizar_menús(símismo):
        vars_mds = sorted(list(símismo.apli.Modelo.mds.variables))
        vars_mds_editables = [v for v in vars_mds if símismo.apli.Modelo.mds.variables[v]['ingreso']]
        vars_bf = sorted(list(símismo.apli.Modelo.bf.variables))

        for var in vars_mds:
            símismo.MnVarsMDS.reinstaurar(var)
        for var in vars_bf:
            símismo.MnVarsBf.reinstaurar(var)

        for conex in símismo.apli.receta['conexiones']:
            var_mds = conex['var_fuente'] if conex['modelo_fuente'] == 'mds' else conex['var_recip']
            var_bf = conex['var_fuente'] if conex['modelo_fuente'] == 'bf' else conex['var_recip']
            símismo.MnVarsMDS.excluir(var_mds)
            símismo.MnVarsBf.excluir(var_bf)

        if símismo.BtMDSFuente.val:
            opciones_mds = vars_mds
        else:
            opciones_mds = vars_mds_editables

        excluir_mds = [x for x in vars_mds if x not in opciones_mds]

        for var in excluir_mds:
            símismo.MnVarsMDS.excluir(var)
            if var == símismo.MnVarsMDS.val:
                símismo.MnVarsMDS.poner('')

    def actualizar_unidades(símismo):
        var = símismo.MnVarsMDS.val
        if var is not None and var != '':
            símismo.EtiqUnidMDS.config(text=símismo.apli.Modelo.mds.variables[var]['unidades'])
        else:
            símismo.EtiqUnidMDS.config(text='')
        var = símismo.MnVarsBf.val
        if var is not None and var != '':
            símismo.EtiqUnidBf.config(text=símismo.apli.Modelo.bf.variables[var]['unidades'])
        else:
            símismo.EtiqUnidBf.config(text='')

    def añadir_conexión(símismo, conexión):

        if 'modelo_fuente' in conexión:
            mds_fuente = conexión['modelo_fuente'] == 'EnvolturasMDS'
            dic_conex = {
                'mds_fuente': mds_fuente,
                'var_mds': conexión['var_fuente'] if mds_fuente else conexión['var_recip'],
                'var_bf': conexión['var_recip'] if mds_fuente else conexión['var_fuente'],
                'conv': conexión['conv']
            }
        else:
            dic_conex = conexión

        try:
            símismo.apli.Modelo.conectar(**dic_conex)
        except ValueError:
            pass

        símismo.actualizar_menús()

    def quitar_conexión(símismo, conexión):
        if conexión['mds_fuente']:
            var_fuente = conexión['var_mds']
            modelo_fuente = 'mds'
        else:
            var_fuente = conexión['var_bf']
            modelo_fuente = 'bf'
        símismo.apli.Modelo.desconectar_vars(var_fuente=var_fuente, modelo_fuente=modelo_fuente)
        símismo.actualizar_menús()

    def verificar_completo(símismo):
        if len(símismo.apli.receta['conexiones']):
            símismo.pariente.desbloquear_cajas([3, 4])
            return True
        else:
            símismo.pariente.bloquear_cajas([3, 4])
            return False


class CajaSubEtp31(CjG.CajaSubEtapa):
    def __init__(símismo, pariente, apli, total):
        super().__init__(pariente, nombre=None, núm=1, total=total)
        símismo.apli = apli
        símismo.apli.Modelo = símismo.apli.Modelo

        cj_ctrls_tiempo = tk.Frame(símismo, **Fm.formato_cajas)

        cj_unidad_tiempo = tk.Frame(cj_ctrls_tiempo, **Fm.formato_cajas)
        etiq_1_tiempo_ref = tk.Label(cj_unidad_tiempo, text='1', **Fm.formato_etiqs_ctrls_tiempo)
        etiq_1_tiempo_ref.pack(**gf(Fm.ubic_CtrlsUnidTiempo))
        símismo.MnTiempoRef = CtrG.Menú(cj_unidad_tiempo, opciones=[], ancho=7,
                                        comanda=símismo.acción_cambió_ref_unid,
                                        ubicación=gf(Fm.ubic_CtrlsUnidTiempo), tipo_ubic='pack')
        símismo.IngrConvUnidTiempo = CtrG.IngrNúm(cj_unidad_tiempo, nombre='=',
                                                  límites=(1, None), prec='ent', val_inic=1,
                                                  comanda=símismo.acción_cambió_conversión,
                                                  ubicación=gf(Fm.ubic_CtrlsUnidTiempo), tipo_ubic='pack')
        símismo.EtiqUnidTiempoNoRef = tk.Label(cj_unidad_tiempo, **Fm.formato_etiqs_ctrls_tiempo)
        símismo.EtiqUnidTiempoNoRef.pack(**gf(Fm.ubic_CtrlsUnidTiempo))
        cj_unidad_tiempo.pack(**gf(Fm.ubic_CtrlsTiempo))

        cj_paso = tk.Frame(cj_ctrls_tiempo, **Fm.formato_cajas)
        símismo.IngrPaso = CtrG.IngrNúm(cj_paso, nombre=apli.Trads['Paso'],
                                        límites=(1, None), prec='ent', val_inic=1,
                                        ubicación=gf(Fm.ubic_CtrlsUnidTiempo), tipo_ubic='pack')
        cj_paso.pack(**gf(Fm.ubic_CtrlsTiempo))

        cj_tiempo_final = tk.Frame(cj_ctrls_tiempo, **Fm.formato_cajas)
        símismo.IngrTempFinal = CtrG.IngrNúm(cj_tiempo_final, nombre=apli.Trads['TiempoFinal'],
                                             límites=(0, None), lím_incl=False, prec='ent', val_inic=100,
                                             ubicación=gf(Fm.ubic_CtrlsUnidTiempo), tipo_ubic='pack')
        símismo.EtiqUnidTiempoFinal = tk.Label(cj_tiempo_final, **Fm.formato_etiqs_ctrls_tiempo)
        símismo.EtiqUnidTiempoFinal.pack(**gf(Fm.ubic_CtrlsTiempo))
        cj_tiempo_final.pack(**gf(Fm.ubic_CtrlsTiempo))

        cj_corrida = tk.Frame(símismo, **Fm.formato_cajas)
        símismo.IngrCorrida = CtrG.IngrTexto(cj_corrida, nombre=apli.Trads['Corrida'],
                                             ubicación=gf(Fm.ubic_CtrlsUnidTiempo), tipo_ubic='pack')
        cj_corrida.place(**gf(Fm.ubic_cj_corrida))

        cj_bt_simul = tk.Frame(símismo, **Fm.formato_cajas)
        símismo.BtSimul = Bt.BotónTexto(cj_bt_simul, texto=apli.Trads['Simular'], comanda=símismo.acción_simular,
                                        formato_norm=Fm.formato_bt_simular,
                                        formato_sel=Fm.formato_bts_sel,
                                        ubicación=gf(Fm.ubic_bt_simular), tipo_ubic='pack')

        símismo.CjSimulando = tk.Frame(cj_bt_simul, **Fm.formato_CjSimulando)
        etiq_simulando = tk.Label(símismo.CjSimulando, text=apli.Trads['Simulando'], **Fm.formato_etiq_simulando)
        etiq_simulando.place(**gf(Fm.ubic_EtiqSimulando))

        cj_ctrls_tiempo.place(**gf(Fm.ubic_CjCtrlsTiempo))
        cj_bt_simul.place(**gf(Fm.ubic_cj_bt_simular))

    def acción_desbloquear(símismo):
        mds = símismo.apli.Modelo.mds
        bf = símismo.apli.Modelo.bf
        unidad_tiempo_mds = mds.unidad_tiempo()
        unidad_tiempo_bf = bf.unidad_tiempo()
        símismo.MnTiempoRef.refrescar(opciones=[unidad_tiempo_mds, unidad_tiempo_bf])
        if not len(símismo.apli.Modelo.conv_tiempo_mods):
            símismo.apli.Modelo.estab_conv_unid_tiempo(unidad_tiempo_mds, unid=unidad_tiempo_bf, factor=1)

        if símismo.apli.Modelo.conv_tiempo_mods['mds'] == 1:
            símismo.MnTiempoRef.poner(unidad_tiempo_mds)
            conv = símismo.apli.Modelo.conv_tiempo_mods['bf']
        else:
            símismo.MnTiempoRef.poner(unidad_tiempo_bf)
            conv = símismo.apli.Modelo.conv_tiempo_mods['mds']
        símismo.IngrConvUnidTiempo.poner(conv)

        símismo.verificar_completo()

    def acción_cambió_ref_unid(símismo, val):
        unidad_tiempo_mds = símismo.apli.Modelo.mds.unidad_tiempo()
        unidad_tiempo_bf = símismo.apli.Modelo.bf.unidad_tiempo()

        val_conv = símismo.IngrConvUnidTiempo.val

        if val == unidad_tiempo_mds:
            símismo.apli.Modelo.conv_tiempo_mods['mds'] = 1
            símismo.apli.Modelo.conv_tiempo_mods['bf'] = val_conv
            símismo.EtiqUnidTiempoFinal.config(text=unidad_tiempo_mds)
            símismo.EtiqUnidTiempoNoRef.config(text=unidad_tiempo_bf)
        else:
            símismo.apli.Modelo.conv_tiempo_mods['mds'] = val_conv
            símismo.apli.Modelo.conv_tiempo_mods['bf'] = 1
            símismo.EtiqUnidTiempoFinal.config(text=unidad_tiempo_bf)
            símismo.EtiqUnidTiempoNoRef.config(text=unidad_tiempo_mds)

    def acción_cambió_conversión(símismo, val):

        unidad_tiempo_mds = símismo.apli.Modelo.mds.unidad_tiempo()

        mod_tiempo_ref = símismo.MnTiempoRef.val

        if mod_tiempo_ref == unidad_tiempo_mds:
            símismo.apli.Modelo.conv_tiempo['bf'] = val
        else:
            símismo.apli.Modelo.conv_tiempo['mds'] = val

    def acción_simular(símismo):
        símismo.CjSimulando.pack(**gf(Fm.ubic_CjSimulando))
        símismo.apli.update()
        símismo.BtSimul.bloquear()

        def func_simular():
            nombre = símismo.IngrCorrida.val
            if nombre == '':
                nombre = 'Corrida Tinamït'

            símismo.apli.Modelo.simular(paso=símismo.IngrPaso.val, t_final=símismo.IngrTempFinal.val,
                                        nombre_corrida=nombre)
            símismo.apli.Modelo.guardar_resultados()
            símismo.BtSimul.desbloquear()
            símismo.CjSimulando.pack_forget()

        import threading

        t = threading.Thread(name='simulación', target=func_simular)
        t.setDaemon(True)
        t.start()


class CajaSubEtp41(CjG.CajaSubEtapa):
    def __init__(símismo, pariente, apli, total):
        super().__init__(pariente, nombre=None, núm=1, total=total)
        símismo.apli = apli
        símismo.apli.Modelo = símismo.apli.Modelo

    def acción_desbloquear(símismo):
        pass

    def verificar_completo(símismo):
        pass
