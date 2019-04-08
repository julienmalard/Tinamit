import numpy as np
from dateutil.relativedelta import relativedelta as deltarelativo

from tinamit.config import _


class ModeloImpaciente():
    """
    Esta clase ofrece una clase pariente muy útil para modelos biofísicos cuyos pasos mínimos de simulación quedan más
    pequeños que el nivel de detalle que ofrecen. Por ejemplo, el modelo de salinidad SAHYSMOD corre por *al menos* un
    año, pero ofrece detalles al nivel estacional (de 1-12 meses) que pueden ser muy diferentes para distintas
    estaciones. Los llamo "impacientes" porque no los puedes hacer correr por un mes, sin que el modelo simule
    el año entero, sino más.
    Esta envoltura te permite crear envolturas, por ejemplo, con pasos mensuales para este tipo_mod de modelo anual,
    pero sin el dolor de cabeza.
    """

    def _vals_inic(símismo):
        dic_inic = símismo._gen_dic_vals_inic()

        subciclo = símismo._vars_subciclo()
        subciclo_ingr = símismo._vars_subciclo(solamente='ingr')

        for var, val in dic_inic.items():
            if var in subciclo:
                if var in subciclo_ingr:
                    símismo.matrs_ingr[var] = val.copy()
                    dic_inic[var] = val[0]

                if var in símismo.egresos():
                    símismo.matrs_egr[var] = val.copy()

        return dic_inic

    def estab_proces_ingr(símismo, var_ingr, proc):
        posibilidades = ['último', 'suma', 'prom', 'máx', None]
        if proc not in posibilidades:
            raise ValueError(proc)
        var_ingr = símismo.valid_var(var_ingr)

        if var_ingr not in símismo.ingresos():
            raise ValueError(_('El variable "{}" no es variable de ingreso.').format(var_ingr))

        if proc is not None:
            símismo.proces_ingrs[var_ingr] = proc
        else:
            símismo.proces_ingrs.pop(var_ingr)

    def cambiar_vals(símismo, valores):

        for var, val in valores.items():
            símismo.matrs_ingr[var][símismo.paso_en_ciclo] = val

        super().cambiar_vals(valores)

    def procesar_ingr_modelo(símismo):
        for var, proc in símismo.proces_ingrs.items():
            matr = símismo.matrs_ingr[var]
            if proc == 'último':
                símismo._act_vals_dic_var({var: matr[-1]})
            elif proc == 'suma':
                símismo._act_vals_dic_var({var: matr.sum()})
            elif proc == 'prom':
                símismo._act_vals_dic_var({var: matr.mean()})
            elif proc == 'máx':
                símismo._act_vals_dic_var({var: matr.max()})

    def procesar_egr_modelo(símismo, n_ciclos):

        valores = símismo.leer_egr_modelo(n_ciclos=n_ciclos)

        por_subciclo = símismo._vars_subciclo()
        for var, val in valores.items():
            if var in por_subciclo:
                símismo._act_vals_dic_var({var: val[0]})

                if var in símismo.matrs_egr:
                    anterior = símismo.matrs_egr[var]
                    if isinstance(anterior, np.ndarray) and anterior.shape == val.shape:
                        símismo.matrs_egr[var][:] = val
                    else:
                        símismo.matrs_egr[var] = val

            else:
                símismo._act_vals_dic_var({var: val})

    def escribir_ingr(símismo, n_ciclos, archivo=None):
        """
        Escribe un fuente de ingresos del modelo en el formato que lee el modelo externo.

        Parameters
        ----------
        n_ciclos : int
            El número de años para la simulación siguiente.
        archivo : str
            El archivo en el cuál escribir los ingresos.

        """

        if archivo is None:
            archivo = símismo.arch_ingreso

        # Procesar los ingresos
        if símismo.ciclo != -1:
            símismo.procesar_ingr_modelo()

        dic_ingr = {}

        ingr_por_pasito = símismo._vars_subciclo(solamente='ingr')

        for var in símismo.ingresos():
            if var in ingr_por_pasito:
                dic_ingr[var] = símismo.matrs_ingr[var]
            else:
                dic_ingr[var] = símismo.obt_val_actual_var(var)

        símismo._escribir_archivo_ingr(n_ciclos=n_ciclos, dic_ingr=dic_ingr, archivo=archivo)


class ModeloIndeterminado(ModeloImpaciente):

    def cambiar_vals(símismo, valores):
        for var, val in valores.items():
            proc = símismo.proces_ingrs[var]
            if símismo.dic_ingr[var] is None:
                símismo.dic_ingr[var] = val
            else:
                if proc == 'máx':
                    símismo.dic_ingr[var] = np.maximum(símismo.dic_ingr[var], val)
                elif proc == 'último':
                    símismo.dic_ingr[var] = val
                elif proc in ['suma', 'prom']:
                    símismo.dic_ingr[var] += val  # La división para `prom` se hará después en `procesar_ingr_modelo()`
                else:
                    raise ValueError(proc)

    def _vals_inic(símismo):
        return símismo._gen_dic_vals_inic()

    def iniciar_modelo(símismo, n_pasos, t_final, nombre_corrida, vals_inic):
        símismo.tmñ_ciclo = 0

        for var in símismo.vars_entrando:
            if var not in símismo.proces_ingrs:
                símismo.proces_ingrs[var] = 'último'

        símismo.dic_ingr.clear()
        símismo.dic_ingr.update({
            vr: None for vr in símismo.vars_entrando
        })

        símismo.matrs_egr.clear()
        for var in símismo._vars_subciclo():
            if var in símismo.vars_saliendo:
                símismo.matrs_egr[var] = None

        super().iniciar_modelo(n_pasos=n_pasos, t_final=t_final, nombre_corrida=nombre_corrida, vals_inic=vals_inic)

    def procesar_ingr_modelo(símismo):
        for var, proc in símismo.proces_ingrs.items():
            val = símismo.dic_ingr[var]
            if proc == 'prom':
                símismo._act_vals_dic_var({var: val / símismo.tmñ_ciclo})
            else:
                símismo._act_vals_dic_var({var: val})

    def obt_tmñ_ciclo(símismo):
        return símismo.tmñ_ciclo


class ModeloDeterminado(ModeloImpaciente):

    def iniciar_modelo(símismo, n_pasos, t_final, nombre_corrida, vals_inic):

        símismo.tmñ_ciclo = símismo.obt_tmñ_ciclo()

        símismo.matrs_ingr.clear()
        símismo.matrs_egr.clear()

        for vr in símismo.vars_entrando:
            dims = símismo.obt_dims_var(vr)
            símismo.matrs_ingr[vr] = np.zeros((símismo.tmñ_ciclo, *dims) if dims != (1,) else símismo.tmñ_ciclo)

        por_pasito = símismo._vars_por_pasito()
        for vr in símismo.vars_saliendo:
            if vr in por_pasito:
                dims = símismo.obt_dims_var(vr)
                símismo.matrs_egr[vr] = np.zeros((símismo.tmñ_ciclo, *dims) if dims != (1,) else símismo.tmñ_ciclo)

        super().iniciar_modelo(n_pasos, t_final, nombre_corrida, vals_inic)


class ModeloBloques(ModeloImpaciente):

    def iniciar_modelo(símismo, n_pasos, t_final, nombre_corrida, vals_inic):
        """
        Esta función debe preparar el modelo para una simulación. Si necesitas esta función para tu subclase,
        no se te olvide llamar ``super().iniciar_modelo()`` para no saltar la reinicialización del bloque y del paso.
        """
        símismo.tmñ_bloques = símismo.obt_tmñ_bloques()
        símismo.tmñ_ciclo = símismo.obt_tmñ_ciclo()

        símismo.matrs_ingr.clear()
        símismo.matrs_egr.clear()

        for vr in símismo.vars_entrando:
            dims = símismo.obt_dims_var(vr)
            símismo.matrs_ingr[vr] = np.zeros((símismo.tmñ_ciclo, *dims) if dims != (1,) else símismo.tmñ_ciclo)

        por_pasito = símismo._vars_por_pasito()
        for vr in símismo.vars_saliendo:
            if vr in por_pasito:
                dims = símismo.obt_dims_var(vr)
                símismo.matrs_egr[vr] = np.zeros((símismo.tmñ_ciclo, *dims) if dims != (1,) else símismo.tmñ_ciclo)

        super().iniciar_modelo(n_pasos, t_final, nombre_corrida, vals_inic=vals_inic)

    def _act_vals_clima(símismo, f_0, f_1, lugar):

        # Solamante hay que cambiar los datos si es el principio de un nuevo ciclo.
        if símismo.ciclo == 0 and símismo.paso_en_ciclo == 0:

            # La lista de variables climáticos
            vars_clima = list(símismo.vars_clima)
            nombres_extrn = [d['nombre_extrn'] for d in símismo.vars_clima.values()]

            # La lista de maneras de combinar los valores diarios
            combins = [d['combin'] for d in símismo.vars_clima.values()]

            # La lista de factores de conversiones de variables de clima
            convs = [d['conv'] for d in símismo.vars_clima.values()]

            # La fecha inicial
            f_inic = f_0

            for b, tmñ in enumerate(símismo.tmñ_bloques):
                # Para cada bloque...

                # La fecha final
                base_t, factor = símismo._unid_tiempo_python()
                f_final = f_0 + deltarelativo(**{base_t: tmñ * factor})

                # Calcular los datos
                datos = lugar.comb_datos(vars_clima=nombres_extrn, combin=combins, f_inic=f_inic, f_final=f_final)

                # Aplicar los valores de variables calculados
                for i, var in enumerate(vars_clima):
                    # Para cada variable en la lista de clima...

                    # El nombre oficial del variable de clima
                    var_clima = nombres_extrn[i]

                    # El factor de conversión
                    conv = convs[i]

                    # Guardar el valor para esta estación
                    símismo.matrs_ingr[var][b, ...] = datos[var_clima] * conv

                # Avanzar la fecha
                f_inic = f_final

    def obt_tmñ_ciclo(símismo):
        return np.sum(símismo.obt_tmñ_bloques())
