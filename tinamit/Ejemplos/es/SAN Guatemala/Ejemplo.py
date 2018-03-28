import os

from tinamit.EnvolturaMDS import generar_mds
from tinamit.Geog.Geog import Geografía
from tinamit.Incertidumbre.ConexDatos import ConexDatos
from tinamit.Incertidumbre.Datos import DatosIndividuales, DatosRegión, SuperBD

c = lambda x: os.path.join('C:\\Users\\jmalar1\\Documents\\Julien\\Bases de datos\\Iximulew', x)
# EnvolturaMDS es una función que genera una instancia de ModeloMDS, tal como VENSIM
modelo = generar_mds(archivo='Para Tinamït.mdl')
print('vars', modelo.variables.keys())
print('internos', modelo.internos)  # variables internos al EnvolturaMDS (p. ej., TIMESTEP y TIME en VENSIM)
print('auxiliares', modelo.auxiliares)
print('flujos', modelo.flujos)
print('niveles', modelo.niveles)
print('constantes', modelo.constantes)
# print('vacíos', modelo.vacíos())

ENCOVI_ind_2011 = DatosIndividuales('ENCOVI ind 2011', archivo=c('ENCOVIs\\2011\\BD Personas_final.csv'), fecha=2011,
                                    lugar='munidept')
ENCOVI_hog_2011 = DatosIndividuales('ENCOVI hog 2011', archivo=c('ENCOVIs\\2011\\BD Hogares_final.csv'), fecha=2011,
                                    lugar='munidept')
ENCOVI_reg_2011 = DatosRegión('ENCOVI reg 2011', archivo=c('ENCOVIs\\2011\\BD regional_final.csv'), fecha=2011,
                              lugar='id')

geog = Geografía('Iximulew')
geog.agregar_info_regiones(archivo='Geografía Iximulew.csv',
                           orden_jer=['Departamento', 'Municipio'],
                           col_cód='Código', grupos='Territorio')

datos_muni = DatosRegión('Datos municipales', archivo=c('Datos muni\\Datos Muni Iximulew.csv'), fecha='Año',
                         lugar='Código_lugar')
datos_pob = DatosRegión('Población', archivo=c('Población\\Población INE.csv'), fecha='Año', lugar='Código')
datos_tierra = DatosRegión('Uso tierra', archivo=c('Uso de tierra\\Uso de tierra.csv'), fecha='Año', lugar='Código')
datos_superficie = DatosRegión('Superficie', archivo=c('Uso de tierra\\Superficie.csv'), fecha=None, lugar='Código')

#
bd = SuperBD('BD Iximulew', bds=[ENCOVI_hog_2011, ENCOVI_ind_2011, ENCOVI_reg_2011, datos_muni,
                                 datos_pob, datos_tierra, datos_superficie], geog=geog)
bd.espec_var('Seguridad alimentaria', var_bd='ISA_23', bds=ENCOVI_hog_2011)
bd.espec_var('Educación formal', var_bd='educación.adultos', bds=ENCOVI_hog_2011)
bd.espec_var('Educación sexual', var_bd='educación.sexual', bds=ENCOVI_ind_2011)
bd.espec_var('Fertilidad', var_bd='fertilidad', bds=ENCOVI_ind_2011)
bd.espec_var('Calidad de la dieta', var_bd='défic.shannon.calidad.dieta', bds=ENCOVI_hog_2011)
bd.espec_var('Cantidad de alimentos', var_bd='cantidad.dieta', bds=ENCOVI_hog_2011)

# bd.espec_var('Ingresos salarial', var_bd='Ingresos.de.salario', cód_vacío='NA')
# bd.espec_var('Ingresos agrícolas', var_bd='Ingresos.agrícolas', cód_vacío='NA')
# bd.espec_var('Ingresos familiares', var_bd='Ingresos', cód_vacío='NA')
bd.espec_var('Comercialización', var_bd='hog.prc.tierra.comercial', bds=ENCOVI_reg_2011)
# bd.espec_var('Producción autoconsumo', var_bd='Producción.autoconsumo', cód_vacío='NA')
bd.espec_var('Tamaño familia', var_bd='tamaño.familia', bds=ENCOVI_hog_2011)
# bd.espec_var('Repetición escolar', var_bd='Repetición.escolar', cód_vacío='NA')
bd.espec_var('Enfermedades infantiles', var_bd='enfermedades.infantiles.fam', bds=ENCOVI_hog_2011)
bd.espec_var('Calidad del agua', var_bd='disponibilidad.agua', bds=ENCOVI_hog_2011)
bd.espec_var('Consumo leña por hogar', var_bd='talla.árb', bds=ENCOVI_hog_2011)
bd.espec_var('Población', var_bd='Población', bds=datos_pob)
bd.espec_var('Infraestructura vial', var_bd='Densidad vial (km/km2)', bds=datos_muni)
bd.espec_var('Desnutrición crónica infantil', var_bd='Desntr_crón_inft', bds=datos_muni)

bd.espec_var('Costumbre de consumo', var_bd='prc.dieta.hort', bds=ENCOVI_hog_2011)
bd.espec_var('Superficie municipio', var_bd='Superficie (ha)', bds=datos_superficie)
bd.espec_var('Fracción tierras a hortalizas', var_bd='prc.tierra.hortalizas', bds=ENCOVI_hog_2011)
bd.espec_var('Fracción infantes inicial', var_bd='ind.edad.0.a.4', bds=ENCOVI_reg_2011)
bd.espec_var('Fracción niños inicial', var_bd='ind.edad.5.a.14', bds=ENCOVI_reg_2011)
bd.espec_var('Fracción adultos inicial', var_bd='ind.edad.15.a.54', bds=ENCOVI_reg_2011)

conex = ConexDatos(bd=bd, modelo=modelo)
conex.no_calibrados()


_ = conex.calib_var('Seguridad alimentaria', ec='1/(1 + a*exp(-b*Calidad de la dieta+b2*Cantidad de alimentos))', paráms=['a', 'b', 'b2'],
                    líms_paráms=[(0, None), (0, None), (0, None)],
                    por='Territorio', aprioris=True, regional=False)

_ = conex.calib_var('Enfermedades infantiles', ec='1/(b*Calidad del agua-a)+c', paráms=['a', 'b', 'c'],
                    líms_paráms=[(0, None), (0, 50), (0, None)], por='Territorio', binario=True, aprioris=True)


_ = conex.estim_constante(const='Fracción infantes inicial', líms=(0, None), por='Territorio', regional=True)
_ = conex.estim_constante(const='Fracción niños inicial', líms=(0, None), por='Territorio', regional=True)
_ = conex.estim_constante(const='Fracción adultos inicial', líms=(0, None), por='Territorio', regional=True)
_ = conex.estim_constante(const='Consumo leña por hogar', líms=(0, None), por='Territorio')
_ = conex.estim_constante(const='Infraestructura vial', líms=(0, None), regional=True)
_ = conex.estim_constante(const='Costumbre de consumo', líms=(0, None), por='Territorio')
_ = conex.estim_constante(const='Educación sexual', líms=(0, None), por='Territorio')
_ = conex.estim_constante(const='Superficie municipio', líms=(0, None), regional=True)
_ = conex.estim_constante(const='Fracción tierras a hortalizas', líms=(0, None), por='Territorio')

conex.espec_inicial('Desnutrición inicial', var='Desnutrición crónica infantil')
conex.espec_inicial('Población inicial', var='Población')

_ = conex.calib_var('Fertilidad', ec='1/(b*Educación formal+b2*Educación sexual+a)+c', paráms=['a', 'b', 'b2', 'c'],
                    líms_paráms=[(0, None), (0, 50), (0, 50), (0, None)], por='Territorio', aprioris=True)

raise SystemExit(0)
# Gráfico de "caja" con incertidumbre
bd.graficar(var='ISA', fechas=2011, cód_lugar='0708', datos=None)
bd.graficar(var='ISA', fechas=2011, lugar=['Iximulew', "Tz'olöj Ya'", 'Concepción'])  # Da lo mismo al antecedente

# Gráfico de línea con tiempo en el eje x e incertidumbre mostrada
bd.graficar(var='Población', años=(2000, None), cód_lugar='0112')

# Varias "cajas" en el mismo gráfico (eje x = lugares)
bd.graficar(var='Población', fechas=2011, cód_lugar=['0112', 1204])

# Varias líneas en el mismo gráfico (eje x = tiempo)
bd.graficar(var='Población', fechas=None, cód_lugar=['0112', 1204])

# Gráfico de un variable contra el otro
bd.graf_comparar(var_x='Sueldo', var_y='Educación', escala='individual', datos=None)
# اعداد.comparar(var_x='Lluvia', var_y='Rendimiento', var_z='Suelo', escala='individual')


bd.guardar(proyecto='')
bd.cargar(fuente='')
bd.cambiar_datos(nombre_datos, nueva_ubic)

control = Control(bd=bd, modelo=modelo, fuente='')

control.conectar_var_ind(datos=ENCOVI_hog_2011, var_bd='', var_modelo='', transformación='promedio')
control.conectar_var_ind(datos=ENCOVI_hog_2011, var_bd='', var_modelo='', transformación='máximo')
control.conectar_var_reg(datos=datos_desnutr, var_bd='Desnutr_crón_inft', var_modelo='', calc_error='porcentaje')

control.comparar(var_mod_x='', var_mod_y='', escala='individual')  # llama BasedeDatos.comparar()
control.estimar(constante='Desnutrición', escala='individual')  # Mal ejemplo
control.estimar(constante='Rendimiento potencial', manera='inversa')  # Estima por aproximación
control.estimados()

control.calibrar_ec(var='Sueldo', relación='logística', cód_lugar='0112', años=None)
control.calibrar_ec(var='Sueldo', cód_lugar='0113', años=None)  # Toma la relación existente
control.calibrados()

var = control.detalles_var(var='')  # Llama Modelo.var()
modelo.parientes(var='')
modelo.hijos(var='')
eq_var = var.eq
eq = control.eq(var='Sueldo')
eq_var is eq
eq.paráms()  # Dic de parám, distribución y valor
control.calibrar_ec(var='', años=None, escala='Municipio', cód_lugar='0112')
control.graficar_ec(var='', var_y=None, var_z=None, datos=None,
                    años=None)  # Grafica los datos (اعداد.relación) y la línea, con incertdumbre, de la ecuación calibrada

control.guardar_incert_paráms(archivo='')  # Dic. de var, parám, y distribución
control.cargar_incert_paráms(fuente='')
control.gen_doc_incert(fuente='')  # Formato de especicificaciones de corridas de incertidumbre VENSIM/otro

control.escribir_modelo(archivo='')
control.correr(nombre_corrida='')
control.analizar_incert(nombre_corrida='',
                        manera='natural')  # Utilizando la función de incertidumbre del programa de EnvolturaMDS
control.visualizar_corrida(var='')

control.validar_MDS(año_inic=None, cód_lugar=['0112'], n_reps=100)  # Genera los análises de Barlas, gráficos, etc.
control.validar_conectado(conectado=ObjDeModeloConectado)

control.guardar(proyecto='')
control.cargar(fuente='')

otro_modelo = mds(archivo_mds='')
control.estab_modelo(otro_modelo)
control.recalibrar_ecs(cód_lugar='0113')  # Calibrar todas las equationes y constantes anteriormente calibradas

control.guardar(proyecto='otro archivo')
