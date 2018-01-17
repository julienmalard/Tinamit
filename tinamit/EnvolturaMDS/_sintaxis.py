import regex


def sacar_variables(texto, rgx, n=None, excluir=None):
    """
    Esat ecuación saca los variables de un texto.

    :param texto: El texto de cual extraer los nombres de los variables.
    :type texto: str

    :param rgx: La expersión regex correspondiendo al formato de los variables.
    :type rgx: str

    :param n: El número máximo de variables que sacar.
    :type n: int

    :param excluir: Nombres de variables para excluir
    :type excluir: list

    :return: Una lista de los nombres de los variables.
    :rtype: list

    """

    # Poner el variable excluir en el formato necesario.
    if excluir is None:
        excluir = []
    if type(excluir) is str:
        excluir = [excluir]

    # Buscar los nombres
    b = regex.findall(rgx, texto)

    # Quitar espacios extras
    b = [x.strip(' ') for x in b]

    # Devolver una lista de nombres de variables únicos.
    if n is None:
        return [x for x in set(b) if x not in excluir]
    else:
        return [x for x in set(b[:n]) if x not in excluir]


def sacar_arg(ec, regex_var, regex_fun, i=None):
    """
    Esta función saca los argumentos de una función.

    :param ec: La ecuación que contiene una función.
    :type ec: str

    :param regex_var:
    :type regex_var: str

    :param regex_fun:
    :type regex_fun: str

    :param i: El índice del argumento que querremos extraer (opcional)
    :type i: int

    :return: Una lista de los argumentos de la función
    :rtype: list[str] | str

    """

    # El principio de la función
    princ_fun = regex.match(regex_fun, ec).end()

    # El fin de la función
    fin_fun = regex.search(r' *\) *\n?$', ec).start()

    # La parte de la ecuación con los argumentos de la función
    sec_args = ec[princ_fun:fin_fun]

    # Una lista de tuples con los índices de las ubicaciones de los variables
    pos_vars = [m.span() for m in regex.finditer(regex_var, sec_args)]

    # Una lista de las ubicaciones de TODAS las comas en el ecuación
    pos_comas = [m.start() for m in regex.finditer(r',', sec_args)]

    # Las índes de separación de argumentos de la función. Solo miramos las comas que NO hagan parte de un variable,
    # y agregamos un 0 al principio, y el último índice del texto al final.
    sep_args = [0] + [j for j in pos_comas if not any([p[0] <= j < p[1] for p in pos_vars])] + [len(sec_args)]

    # Dividimos la ecuación en argumentos
    args = [sec_args[p:sep_args[j+1]] for j, p in enumerate(sep_args[:-1])]

    # Y devolvemos el argumento pedido.
    if i is None:
        return args
    else:
        return args[i]


def juntar_líns(l, cabeza=None, cola=None):
    """
    Esta función junta una lista de líneas de texto en una sola línea de texto.

    :param l: La lexta de líneas de texto.
    :type l: list[str]

    :param cabeza:
    :type cabeza:

    :param cola:
    :type cola:

    :return: El texto combinado.
    :rtype: str

    """

    # Quitar text no deseado del principio y del final
    if cabeza is not None:
        l[0] = regex.sub(r'^({})'.format(cabeza), '', l[0])
    if cola is not None:
        l[-1] = regex.sub(r'{}$'.format(cola), '', l[-1])

    # Quitar tabulaciones y símbolos de final de línea
    l = [x.lstrip('\t').rstrip('\n').rstrip('\\') for x in l]

    # Combinar las líneas y quitar espacios al principio y al final
    texto = ''.join(l).strip(' ')

    # Devolver el texto combinado.
    return texto


def cortar_líns(texto, máx_car, lín_1=None, lín_otras=None):

    lista = []

    while len(texto):
        if len(texto) <= máx_car:
            l = texto
        else:
            dif = máx_car - texto

            l = regex.search(r'(.*)\W.[%s,]' % dif, texto).groups()[0]

        lista.append(l)
        texto = texto[len(l):]

    if lín_1 is not None:
        lista[0] = lín_1 + lista[0]

    if lín_otras is not None:
        for n, l in enumerate(lista[1:]):
            lista[n] = lín_otras + l

    return lista


dic_funs = {
    'min(': {'VENSIM': 'MIN('},
    'max(': {'VENSIM': 'MAX('},
    'abs(': {'VENSIM': 'ABS('},
    'math.exp(': {'VENSIM': 'EXP('},
    'int(': {'VENSIM': 'INTEGER('},
    'math.log(': {'VENSIM': 'LN('},
    'math.sin(': {'VENSIM': 'SIN('},
    'math.cos(': {'VENSIM': 'COS('},
    'math.tan(': {'VENSIM': 'TAN('},
    'math.asin(': {'VENSIM': 'ARCSIN('},
    'math.acos(': {'VENSIM': 'ARCCOS('},
    'math.atan(': {'VENSIM': 'ARCTAN('},
    'math.log10(': {'VENSIM': 'LOG('},

}


dic_ops = {
    '+': {'VENSIM': '+'},
    '-': {'VENSIM': '-'},
    '*': {'VENSIM': '*'},
    '/': {'VENSIM': '/'}
}


dic_funs_inv = {}
for fun, d_fun in dic_funs.items():
    for tipo, v in d_fun.items():
        if tipo not in dic_funs_inv:
            dic_funs_inv[tipo] = {}
        dic_funs_inv[tipo][v] = fun


dic_ops_inv = {}
for op, d_op in dic_ops.items():
    for tipo, v in d_op.items():
        if tipo not in dic_ops_inv:
            dic_ops_inv[tipo] = {}
        dic_ops_inv[tipo][v] = op