class ResultadosGrupo(object):
    pass

class ResultadosSimul(object):

    def guardar(símismo, res=None, nombre=None, frmt='json', l_vars=None):

        if res is None:
            res = símismo.mem_vars
        if nombre is None:
            nombre = símismo.corrida_activa
        if l_vars is None:
            l_vars = list(res.data_vars)
        elif isinstance(l_vars, str):
            l_vars = [l_vars]
        else:
            l_vars = l_vars

        faltan = [x for x in l_vars if x not in res]
        if len(faltan):
            raise ValueError(_('Los variables siguientes no existen en los datos:'
                               '\n{}').format(', '.join(faltan)))

        if frmt[0] != '.':
            frmt = '.' + frmt
        arch = valid_nombre_arch(nombre + frmt)
        if frmt == '.json':
            contenido = res[l_vars].to_dict()
            guardar_json(contenido, arch=arch)

        elif frmt == '.csv':

            with open(arch, 'w', encoding='UTF-8', newline='') as a:
                escr = csv.writer(a)

                escr.writerow(['tiempo'] + res['tiempo'].values.tolist())
                for var in l_vars:
                    vals = res[var].values
                    if len(vals.shape) == 1:
                        escr.writerow([var] + vals.tolist())
                    else:
                        for í in range(vals.shape[1]):
                            escr.writerow(['{}[{}]'.format(var, í)] + vals[:, í].tolist())

        else:
            raise ValueError(_('Formato de resultados "{}" no reconocido.').format(frmt))


class ResultadosModelo(object):
    def __init__(símismo, modelo):
        símismo.modelo = modelo
        símismo._res_vars = {str(v): ResultadosVar(v) for v in modelo.variables}

    def __str__(símismo):
        return str(símismo.modelo)

    def __iter__(símismo):
        for v in símismo._res_vars.values():
            yield v


class ResultadosVar(object):
    def __init__(símismo, var, ):
        símismo.var = var

    def __str__(símismo):
        return str(símismo.var)
