import numpy as np
from dateutil.relativedelta import relativedelta as deltarelativo

from tinamit.config import _


class ModeloImpaciente:
    """
    Esta clase ofrece una clase pariente muy útil para modelos biofísicos cuyos pasos mínimos de simulación quedan más
    pequeños que el nivel de detalle que ofrecen. Por ejemplo, el modelo de salinidad SAHYSMOD corre por *al menos* un
    año, pero ofrece detalles al nivel estacional (de 1-12 meses) que pueden ser muy diferentes para distintas
    estaciones. Los llamo "impacientes" porque no los puedes hacer correr por un mes, sin que el modelo simule
    el año entero, sino más.
    Esta envoltura te permite crear envolturas, por ejemplo, con pasos mensuales para este tipo_mod de modelo anual,
    pero sin el dolor de cabeza.
    """

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


class ModeloBloques(ModeloImpaciente):

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
