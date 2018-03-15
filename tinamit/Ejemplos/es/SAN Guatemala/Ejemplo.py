from tinamit.Incertidumbre.Datos import DatosIndividuales, DatosRegión, SuperBD
from tinamit.EnvolturaMDS import generar_mds
from tinamit.Geog.Geog import Geografía
from tinamit.Incertidumbre.ConexDatos import ConexDatos

# EnvolturaMDS es una función que genera una instancia de ModeloMDS, tal como VENSIM
modelo = generar_mds(archivo='Para Tinamït.mdl')
print('vars', modelo.variables.keys())
print('internos', modelo.internos)  # variables internos al EnvolturaMDS (p. ej., TIMESTEP y TIME en VENSIM)
print('auxiliares', modelo.auxiliares)
print('flujos', modelo.flujos)
print('niveles', modelo.niveles)
print('constantes', modelo.constantes)
# print('vacíos', modelo.vacíos())

ENCOVI_hog_2011 = DatosIndividuales('ENCOVI hog 2011', archivo='Datos\\ENCOVI_hog_2011.csv', fecha=2011,
                                    lugar='munidept', cód_vacío=['NA', 'na', 'Na', 'nan', 'NaN'])
ENCOVI_ind_2011 = DatosIndividuales('ENCOVI ind 2011', archivo='Datos\\ENCOVI_ind_2011.csv', fecha=2011,
                                    lugar='munidept', cód_vacío=['NA', 'na', 'Na', 'nan', 'NaN'])

# ENCOVI_hog_2011 = DatosIndividuales(fuente='')
# ENCOVI_hog_2011.estab_col_año(col='año')

geog = Geografía('Iximulew')
geog.agregar_info_regiones(archivo='Geografía Iximulew.csv',
                           orden_jer=['Departamento', 'Municipio'],
                           col_cód='Código', grupos='Territorio')

datos_desnutr = DatosRegión('Desnutrición municipal', archivo='Datos\\Desnutrición_muni.csv', fecha='Año',
                            lugar='Código_lugar', tmñ_muestra='Tamaño_muestra')
# ENCOVI_reg_2011 = DatosRegión('ENCOVI reg 2011', archivo='Datos\\ENCOVI_reg_2011.csv', fecha=2011,
#                               lugar='Código_lugar', cód_vacío=['NA', 'na', 'Na'])

bd = SuperBD('BD Iximulew', bds=[ENCOVI_hog_2011, ENCOVI_ind_2011, datos_desnutr], geog=geog)
bd.espec_var('ISA', var_bd='ISA_23', bds='ENCOVI hog 2011')
bd.espec_var('Educación formal', var_bd='educación', bds='ENCOVI ind 2011')
bd.espec_var('Educación sexual', var_bd='educación.sexual', bds='ENCOVI ind 2011')
bd.espec_var('Fertilidad', var_bd='fertilidad', bds='ENCOVI ind 2011')

# bd.espec_var('Ingresos salarial', var_bd='Ingresos.de.salario', cód_vacío='NA')
# bd.espec_var('Ingresos agrícolas', var_bd='Ingresos.agrícolas', cód_vacío='NA')
# bd.espec_var('Ingresos familiares', var_bd='Ingresos', cód_vacío='NA')
# bd.espec_var('% tierras uso comercial', var_bd='Porcentaje.tierras.producción.comercial', cód_vacío='NA')
# bd.espec_var('Producción autoconsumo', var_bd='Producción.autoconsumo', cód_vacío='NA')
# bd.espec_var('Tamaño familias', var_bd='Tamaño.de.las.familias', cód_vacío='NA')
# bd.espec_var('Repetición escolar', var_bd='Repetición.escolar', cód_vacío='NA')
# bd.espec_var('Enfermedades infantilies', var_bd='Enfermedades.infantiles', cód_vacío='NA')
# # bd.espec_var('Población', var_bd='Población')
# bd.espec_var('Desnutrición crónica infantil', var_bd='Desntr_crón_inft')

conex = ConexDatos(bd=bd, modelo=modelo)
conex.no_calibrados()

datos = bd.obt_datos(['Educación formal', 'Educación sexual', 'Fertilidad'])['individual'].dropna()
x = datos['Educación formal'].values
x1 = datos['Educación sexual'].values
y = datos['Fertilidad'].values

from tinamit.EnvolturaMDS.sintaxis import Ecuación
import numpy as np, pymc3 as pm
ec = Ecuación(ec='b/(x+a)+c', dialecto='tinamït')
tx = ec.gen_texto(paráms=['a', 'b', 'c'])
f = ec.gen_func_python(paráms=['a', 'b', 'c'])
f([1,2,2], {'x': np.array([0,0,1,2,3,4,5,6,7,8,9,10,15,20])})
d_calib = conex.calib_var('Fertilidad', ec='b/(Educación formal+a)+c', paráms=['a', 'b', 'c'],
                          líms_paráms=[(0, None), None, (0, None)], por='Territorio', aprioris=True)

m = ec.gen_mod_bayes(paráms=['a', 'b', 'c'], líms_paráms=[(0, None), (0, None), (0, None)],
                     obs_x={'x': x}, obs_y=y)
with m:
    t = pm.sample()
pm.traceplot(t)

ec2 = Ecuación(ec='b/(x+a) + b1*x1 + c', dialecto='tinamït')
m2 = ec2.gen_mod_bayes(paráms=['a', 'b', 'b1', 'c'], líms_paráms=[(0, None)]*4,
                       obs_x={'x': x, 'x1': x1}, obs_y=y)
with m2:
    t2 = pm.sample()
pm.traceplot(t2)




conex.calib_var('Fertilidad')

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

raise SystemExit(0)

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
control.graficar_ec(var='', var_y=None, var_z=None, datos=None, años=None)  # Grafica los datos (اعداد.relación) y la línea, con incertdumbre, de la ecuación calibrada


control.guardar_incert_paráms(archivo='')  # Dic. de var, parám, y distribución
control.cargar_incert_paráms(fuente='')
control.gen_doc_incert(fuente='')  # Formato de especicificaciones de corridas de incertidumbre VENSIM/otro

control.escribir_modelo(archivo='')
control.correr(nombre_corrida='')
control.analizar_incert(nombre_corrida='', manera='natural')  # Utilizando la función de incertidumbre del programa de EnvolturaMDS
control.visualizar_corrida(var='')

control.validar_MDS(año_inic=None, cód_lugar=['0112'], n_reps=100)  # Genera los análises de Barlas, gráficos, etc.
control.validar_conectado(conectado=ObjDeModeloConectado)

control.guardar(proyecto='')
control.cargar(fuente='')


otro_modelo = mds(archivo_mds='')
control.estab_modelo(otro_modelo)
control.recalibrar_ecs(cód_lugar='0113')  # Calibrar todas las equationes y constantes anteriormente calibradas

control.guardar(proyecto='otro archivo')