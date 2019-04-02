import os

import numpy as np
import regex

from tinamit.config import _


class ModeloVensim():  # pragma: sin cobertura


    def _inic_dic_vars(símismo):
        """
        Inicializamos el diccionario de variables del modelo Vensim.
        """

        # Aplicar los variables iniciales
        símismo._leer_vals_de_vensim()

    def _cambiar_vals_modelo_externo(símismo, valores):
        """
        Esta función cambiar los valores de variables en Vensim. Notar que únicamente los variables identificados como
        de tipo_mod "Gaming" en el modelo podrán actualizarse.

        :param valores: Un diccionario de variables y sus nuevos valores.
        :type valores: dict

        """

        for var, val in valores.items():
            # Para cada variable para cambiar...

            if símismo.obt_dims_var(var) == (1,):
                # Si el variable no tiene dimensiones (subscriptos)...

                # Actualizar el valor en el modelo Vensim.
                if not np.isnan(val):
                    cmd_vensim(func=símismo.mod.vensim_command,
                               args='SIMULATE>SETVAL|%s = %f' % (var, val),
                               mensaje_error=_('Error cambiando el variable %s.') % var)
            else:
                # Para hacer: opciones de dimensiones múltiples
                # La lista de subscriptos
                subs = símismo.variables[var]['subscriptos']
                if isinstance(val, np.ndarray) and len(val.shape) > 0:
                    matr = val
                else:
                    matr = np.empty(len(subs))
                    matr[:] = val

                for n, s in enumerate(subs):
                    var_s = var + s
                    val_s = matr[n]
                    if not np.isnan(val_s):
                        cmd_vensim(func=símismo.mod.vensim_command,
                                   args='SIMULATE>SETVAL|%s = %f' % (var_s, val_s),
                                   mensaje_error=_('Error cambiando el variable %s.') % var_s)

    def _leer_vals(símismo):
        """
        Este método lee los valores intermediaros de los variables del modelo Vensim. Para ahorrar tiempo, únicamente
        lee esos variables que están en la lista de ``ModeloVensim.vars_saliendo``.

        """

        # Para cada variable que está conectado con el modelo biofísico...
        símismo._leer_vals_de_vensim(l_vars=list(símismo.vars_saliendo))

    def leer_arch_resultados(símismo, archivo, var=None, col_tiempo='Time'):
        """
        Esta función no lee los archivos directamente, pero los convierte en el formato .csv para que se puedan leer
        por Tinamït.

        Parameters
        ----------
        archivo : str
            El nombre del archivo.
        var : str | list[str]
            El variable o lista de variables de interés.
        col_tiempo: str
            El nombre de la columna de tiempo.

        Returns
        -------
        xr.Dataset
            Los resultados de la corrida.
        """

        corr, ext = os.path.splitext(archivo)

        # Si no se especificó extensión, tenemos que decidir entre el formato .vdf o .csv. Tomaremos el archivo más
        # recién, el cuál nos dará la simulación más recién efectuada por el usuario.
        if not len(ext):
            if os.path.isfile(corr + '.vdf'):
                if not os.path.isfile(corr + '.csv'):
                    ext = '.vdf'
                else:
                    ext = '.vdf' if os.path.getmtime(corr + '.vdf') > os.path.getmtime(corr + '.csv') else '.csv'
            elif os.path.isfile(corr + '.csv'):
                ext = '.csv'
            else:
                raise FileNotFoundError(_('No encontramos archivo para "{}".').format(archivo))

        # Si tenemos formato '.vdf', debemos convertirlo a '.csv' primero.
        if ext == '.vdf':
            archivo = corr + '.csv'
            símismo._vdf_a_csv(corr)

        # Delegar la lectura de archivos .csv a la clase pariente
        return super().leer_arch_resultados(archivo=archivo, var=var, col_tiempo=col_tiempo)

    def editable(símismo):
        return símismo.instalado() and símismo.tipo_mod == '.mdl'


def gen_archivo_mdl(archivo_plantilla, d_vars):
    # Leer las tres secciones generales de la fuente
    with open(archivo_plantilla, encoding='UTF-8') as d:
        # La primera línea del documento, con {UTF-8}
        cabeza = [d.readline()]

        ln = d.readline()
        # Seguir hasta la primera línea que NO contiene información de variables ("****...***" para Vensim).
        while not regex.match(r'\*+\n$', ln) and not regex.match(r'\\\\\\\-\-\-\/\/\/', ln):
            ln = d.readline()

        # Guardar todo el resto del fuente (que no contiene información de ecuaciones de variables).
        cola = d.readlines()
        cola += [ln] + cola

    cuerpo = [_escribir_var(var, d_var) for var, d_var in d_vars.items()]

    return '\n'.join(*(cabeza + cuerpo + cola))


def _escribir_var(var, dic_var):
    """

    :param var:
    :type var: str

    :return:
    :rtype: str
    """

    if dic_var['ec'] == '':
        dic_var['ec'] = 'A FUNCTION OF (%s)' % ', '.join(dic_var['parientes'])
    lím_línea = 80

    texto = [var + '=\n',
             _cortar_líns(dic_var['ec'], lím_línea, lín_1='\t', lín_otras='\t\t'),
             _cortar_líns(dic_var['unidades'], lím_línea, lín_1='\t', lín_otras='\t\t'),
             _cortar_líns(dic_var['comentarios'], lím_línea, lín_1='\t~\t', lín_otras='\t\t'), '\t' + '|']

    return texto


def _cortar_líns(texto, máx_car, lín_1=None, lín_otras=None):
    lista = []

    while len(texto):
        if len(texto) <= máx_car:
            ln = texto
        else:
            dif = máx_car - texto

            ln = regex.search(r'(.*)\W.[%s,]' % dif, texto).groups()[0]

        lista.append(ln)
        texto = texto[len(ln):]

    if lín_1 is not None:
        lista[0] = lín_1 + lista[0]

    if lín_otras is not None:
        for n, ln in enumerate(lista[1:]):
            lista[n] = lín_otras + ln

    return lista
