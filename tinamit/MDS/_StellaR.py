# -------------------------------------------------------------------------------
# Name:        StellaR
# Version:     2.0
# Purpose:     Translate dynamic simulation models from Stella into R
#
# Author:      Babak Naimi
#	       Jessica Gorzo
#	       Alexey Voinov
# Email:       naimi.b@gmail.com
#	       gorzo@wisc.edu
# website:     www.r-gis.net
# Modificado por inclusión en Tinamït.
# Modified for inclusion in Tinamït
# -------------------------------------------------------------------------------
import os
import re
import sys


def run(fname1, outputName):
    outPath = outputName
    outName_split = re.split('(\\\|/)', outputName)
    if len(outName_split) > 1:
        outputName = outName_split[-1]

    #############################
    ## Classes-------------------
    ###-----------------------------
    class model:
        models = 0

        def __init__(self, name):
            self.modeltxtlist = name
            self.setup()
            model.models += 1

        def setup(self):
            self.inflows = []
            self.outflows = []
            self.rank = 0
            self.init = 0

    class flow:
        flows = 0

        def __init__(self, name):
            self.name = name
            self.input_txt = ""
            self.setup()
            flow.flows += 1

        def setup(self):
            self.in_convertors = []
            self.in_stocks = []
            self.in_flows = []
            self.hasFunction = False
            self.isIf = False
            self.Eq = None

    class convertor:
        convertors = 0

        def __init__(self, name):
            self.name = name
            self.input_txt = ""
            self.setup()
            convertor.convertors += 1

        def setup(self):
            self.in_convertors = []
            self.value = None
            self.hasFunction = False
            self.isIf = False
            self.Eq = None
            self.isData = False
            self.Data = None

    class if_class:
        if_classes = 0

        def __init__(self, name):
            self.name = name
            self.if_clause = ""
            self.then_clause = ""
            self.else_clause = ""
            if_class.if_classes += 1

    class multi_if_class:
        if_classes = 0

        def __init__(self, name):
            self.name = name
            self.if_clause = ""
            self.then_clause = ""
            self.else_clause = ""
            multi_if_class.if_classes += 1

    class inputData:
        inputData = 0

        def __init__(self, name):
            self.name = name
            self.xname = ""
            self.x = []
            self.y = []

    #############################
    ## Functions-------------------
    ###-----------------------------
    def convExplore(lines, convname):
        i = [line for line, s in enumerate(lines) if s.startswith(convname + " =")][0]
        convEq = lines[i].split("=", 1)[1].strip()
        tempc = i + 1
        multilineconv = True
        while (multilineconv):
            if tempc == len(lines):
                multilineconv = False
            elif ('=' not in lines[tempc].strip().split() or re.search("(ELSE|else)$",
                                                                       lines[tempc - 1].strip()) or re.search("^else",
                                                                                                              lines[
                                                                                                                  tempc].strip()) or re.search(
                    "^then", lines[tempc].strip())):
                convEq = convEq + ' ' + ' '.join(lines[tempc].strip().split())
                tempc += 1
            else:
                multilineconv = False
        convEq = re.sub('{.*}', '', convEq).strip()
        return (convEq)

    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def if_extract(stella_var, conv):
        stella = stella_var
        txtline = str(stella[conv].Eq)
        if stella[conv].isIf:
            pattern = '(if\s+|IF\s+|If\s+|if\(|IF|If)'
            if_pattern = re.compile(pattern)
            function_pattern = '(\^|\*|DELAY|exp|min|max|mean|sum|abs|sin|cos|tan|log10|sqrt|round|log|atan|acos|floor)\(.*\)'
            protectedstrings = []
            for m in re.finditer(function_pattern, txtline):
                if m.group().count("(") < m.group().count(")"):
                    endpos = [m.start() for m in re.finditer('\)', m.group())][
                                 m.group().count("(") - m.group().count(")")] + m.start()
                else:
                    endpos = m.group().rfind(")") + m.start() + 1
                startpos = m.group().find("(") + m.start()
                protectedstrings.append(startpos)
                protectedstrings.append(endpos)
            protectedstrings.insert(0, 0)
            if protectedstrings[-1] == len(txtline):
                parts = [txtline[i:j] for i, j in zip(protectedstrings, protectedstrings[1:])]
            else:
                parts = [txtline[i:j] for i, j in zip(protectedstrings, protectedstrings[1:] + [None])]
            for i in range(0, len(parts), 2):
                if ('(' in parts[i]): parts[i] = parts[i].replace('(', ' ')
                if (')' in parts[i]): parts[i] = parts[i].replace(')', ' ')
            txtline = ''.join(parts)
            ifs = if_pattern.finditer(txtline)
            ifspos = []
            for y in ifs: ifspos.append(y.start())
            for ifst in reversed(ifspos):
                if_clause = re.match(
                    '(if\s+|IF\s+|If\s+|if(?!else)|IF|If)(?P<ifclause>.*?)\s+(then\s+|THEN\s+|Then\s+|then|THEN|Then)',
                    txtline[ifst:])
                ifclause = if_clause.group('ifclause')
                then_clause = re.search(
                    '(then\s+|THEN\s+|Then\s+|then|THEN|Then)(?P<thenclause>.*?)\s*((?<!if)else\s+|ELSE\s+|Else\s+|(?<!if)else|ELSE|Else)',
                    txtline[ifst:])
                thenclause = then_clause.group('thenclause')
                if len(re.split('((?<!if)else\s+|ELSE\s+|Else\s+|(?<!if)else|ELSE|Else)', txtline[ifst:])) > 2:
                    elseclause = re.split('((?<!if)else\s+|ELSE\s+|Else\s+|(?<!if)else|ELSE|Else)', txtline[ifst:])[
                        2].strip()
                else:
                    elseclause = None
                ifelse = "ifelse(" + ifclause + "," + thenclause + "," + elseclause + ")" + ' '.join(
                    re.split('((?<!if)else\s+|ELSE\s+|Else\s+|(?<!if)else|ELSE|Else)', txtline[ifst:])[3:])
                txtline = txtline[:ifst] + ifelse
            txtline = re.sub('(?<!<|>)=', '==', txtline)
            if (' OR ' in txtline): txtline = txtline.replace(' OR ', ' | ')
            if (' or ' in txtline): txtline = txtline.replace(' or ', ' | ')
            if (' AND ' in txtline): txtline = txtline.replace(' AND ', ' & ')
            if (' and ' in txtline): txtline = txtline.replace(' and ', ' & ')
        return (txtline)

    def special_match(strg, search=re.compile(r'^(?:(?:.*[^A-Za-z0-9:()_\s\\])|(?:THEN|ELSE|then|else)).*$').search):
        return not bool(search(strg))

    # ---------------------------------
    f1 = open(fname1)
    models = {}
    flows = {}
    convertors = {}
    ifclasses = {}
    Mifclasses = {}
    lines = f1.readlines()
    f1.close()
    init_pattern = r"INIT\s+(?P<initname>[a-zA-Z0-9_]+)\s+=\s+(?P<initvalue>.*)"
    init_expr = re.compile(init_pattern)
    i = 0
    modelrank = 0
    ln = 0

    while ln < len(lines):
        ltxt = lines[ln].strip().split()
        while ('' in ltxt): ltxt.remove('')
        if len(ltxt) > 0:
            lines[ln] = lines[ln].expandtabs()
            if special_match(lines[ln]) and not re.search("ELSE$", lines[ln - 1].strip()):
                lines.remove(lines[ln])
            else:
                lines[ln] = lines[ln].replace('\\', '_')
                lines[ln] = lines[ln].replace('%', 'percent')
                lines[ln] = lines[ln].replace('[', '_')
                lines[ln] = lines[ln].replace(']', '')
                lines[ln] = lines[ln].replace(' MOD ', ' %% ')
                lines[ln] = lines[ln].replace('delay(', 'DELAY(')
                lines[ln] = lines[ln].replace(' EXP', ' exp')
                lines[ln] = lines[ln].replace(' MIN', ' min')
                lines[ln] = lines[ln].replace(' MAX', ' max')
                lines[ln] = lines[ln].replace(' MEAN', ' mean')
                lines[ln] = lines[ln].replace(' SUM', ' sum')
                lines[ln] = lines[ln].replace(' ABS', ' abs')
                lines[ln] = lines[ln].replace(' SIN', ' sin')
                lines[ln] = lines[ln].replace(' COS', ' cos')
                lines[ln] = lines[ln].replace('TAN', 'tan')
                lines[ln] = lines[ln].replace('LOG10', 'log10')
                lines[ln] = lines[ln].replace(' SQRT', ' sqrt')
                lines[ln] = lines[ln].replace(' ROUND', ' round')
                lines[ln] = lines[ln].replace(' LOGN', ' log')
                lines[ln] = lines[ln].replace(' ARCTAN', ' atan')
                lines[ln] = lines[ln].replace(' ARCCOS', ' acos')
                lines[ln] = lines[ln].replace('TIME', 't')
                lines[ln] = lines[ln].replace('(time', '(t')
                lines[ln] = lines[ln].replace(' PI', ' pi')
                lines[ln] = lines[ln].replace(' INT', ' floor')
                lines[ln] = re.sub(r'\(0\-([a-zA-Z0-9_]+)\)<0', r'\1>0', lines[ln])
                ln += 1
        else:
            lines.remove(lines[ln])

    ln = 0
    while ln < len(lines):
        if "INIT" in lines[ln]:
            init_position = lines[ln].find("INIT")
            if init_position > 0:
                init_line = lines[ln][init_position:]
                lines.insert(ln + 1, init_line)
                lines[ln] = lines[ln][0:init_position]
        ln += 1

    for line in lines:
        init_match = re.search(init_expr, line)
        if init_match and len(lines[i - 1].strip().split()[6:-2]) > 0:
            models[init_match.group('initname')] = model(init_match.group('initname'))
            models[init_match.group('initname')].init = init_match.group('initvalue')
            modelrank += 1
            models[init_match.group('initname')].rank = modelrank
            nextflow = True
            ltxt = lines[i - 1].strip().split()[6:-2]
            for txt in ltxt:
                txt = txt.replace('(', '')
                txt = txt.replace(')', '')
                if (txt == "-"):
                    nextflow = False
                if (txt != "+" and txt != "-"):
                    if (nextflow):
                        models[init_match.group('initname')].inflows.append(txt)
                        if (txt not in flows):
                            flows[txt] = flow(txt)
                            flows[txt].input_txt = convExplore(lines, txt)
                    else:
                        models[init_match.group('initname')].outflows.append(txt)
                        if (txt not in flows):
                            flows[txt] = flow(txt)
                            flows[txt].input_txt = convExplore(lines, txt)
                        nextflow = True
        i += 1

    ######## Analyzing text of each flow equations
    supported_func = ['DELAY', 'delay', 'exp', 'min', 'max', 'mean', 'sum', 'abs', 'sin', 'cos', 'tan', 'log10', 'sqrt',
                      'round', 'log', 'atan', 'acos', 't', 'pi', 'floor', 'dt']

    optlist = ['*', '/', '+', '-', '(', ')', '=', '<', '>', '<=', '>=', ',', "", " ", '{', '}', '^', '\\', '%%']
    for fl in list(flows.keys()):
        txtline = flows[fl].input_txt
        txtline = re.split('(=|\*|>(?!=)|<(?!=)|,|\^|\+|\-|\)|\(|[{]|[}]|/|>=|<=|%%)', txtline)
        while ('' in txtline): txtline.remove('')
        while (' ' in txtline): txtline.remove(' ')
        txtline = ''.join(txtline)
        flows[fl].input_txt = txtline
        # check for IF statement
        if "0*" in txtline:
            init_position = txtline.find("0*")
            txtline = txtline.replace(txtline[init_position:], "0")
        if_num = len(re.findall('(if\s+|IF\s+|If\s+|if\(|IF|If)', txtline))
        if (if_num > 0): flows[fl].isIf = True
        flows[fl].Eq = txtline
        # extract convertors
        conv_temp = re.split('=|\*|>(?!=)|<(?!=)|,|\^|\+|\-|\)|\(|[{]|[}]|/|\s+|>=|<=|%%', txtline)
        for i in range(0, len(conv_temp)):
            conv_temp[i] = conv_temp[i].strip()
            if ((conv_temp[i]) in supported_func):
                flows[fl].hasFunction = True
                Rformatting = []
                for x in re.split('(\()', flows[fl].Eq): Rformatting.append(x.strip())
                flows[fl].Eq = ''.join(Rformatting)
            # conv_temp = re.split('=|\*|>|<|,|\+|\^|\-|\)|\(|[{]|[}]|/|\s+|%%', convertors[conv].Eq)
            restricted_words = ['if', 'If', 'IF', 'AND', 'and', 'THEN', 'then', 'ELSE', 'else', 'OR', '',
                                'or'] + supported_func
            if ((conv_temp[i] not in restricted_words) and (not is_number(conv_temp[i]))):
                if (conv_temp[i] not in list(convertors.keys()) and conv_temp[i] not in list(models.keys()) and
                        conv_temp[i] not in list(flows.keys())):
                    convertors[conv_temp[i]] = convertor(conv_temp[i])
                # if (conv_temp[i] not in flows[fl].in_convertors):
                #    flows[fl].in_convertors.append(conv_temp[i])
                elif (conv_temp[i] in list(models.keys()) and conv_temp[i] not in flows[fl].in_stocks):
                    flows[fl].in_stocks.append(conv_temp[i])
                if (conv_temp[i] in list(convertors.keys()) and (conv_temp[i] not in flows[fl].in_convertors)):
                    flows[fl].in_convertors.append(conv_temp[i])
                if (conv_temp[i] in list(flows.keys())):
                    flows[fl].in_flows.append(conv_temp[i])

    ##################
    ## Analyzing text for each convertor ---------
    ##################
    newconv = {}
    for conv in list(convertors.keys()):
        txtline = convExplore(lines, conv)
        convertors[conv].input_txt = txtline
        if ('GRAPH' in txtline):
            convertors[conv].isData = True
        elif (is_number(txtline)):
            convertors[conv].value = float(txtline)
        else:
            if (len(re.findall('(if\s+|IF\s+|If\s+|if\(|IF|If)', txtline)) > 0): convertors[conv].isIf = True
            convertors[conv].Eq = txtline
            conv_temp = re.split('=|\*|>(?!=)|<(?!=)|,|\^|\+|\-|\)|\(|[{]|[}]|/|\s+|>=|<=|%%', txtline)
            for i in range(0, len(conv_temp)):
                conv_temp[i] = conv_temp[i].strip()
                if (conv_temp[i] in supported_func):
                    convertors[conv].hasFunction = True
                    Rformatting = []
                    for x in re.split('(\()', convertors[conv].Eq): Rformatting.append(x.strip())
                    convertors[conv].Eq = ''.join(Rformatting)
            conv_temp = re.split('=|\*|>|<|,|\+|\^|\-|\)|\(|[{]|[}]|/|\s+|%%', convertors[conv].Eq)
            restricted_words = ['', 'and', 'if', 'or', 'If', 'IF', 'AND', 'THEN', 'then', 'ELSE', 'else',
                                'OR'] + supported_func
            for i in range(0, len(conv_temp)):
                if ((conv_temp[i] not in restricted_words) and (not is_number(conv_temp[i]))):
                    if (conv_temp[i] not in list(convertors.keys()) and conv_temp[i] not in list(newconv.keys()) and
                            conv_temp[i] not in list(models.keys()) and conv_temp[i] not in list(flows.keys())):
                        newconv[conv_temp[i]] = convertor(conv_temp[i])
                    if (conv_temp[i] not in convertors[conv].in_convertors): convertors[conv].in_convertors.append(
                        conv_temp[i])

    rr = True
    while (rr):
        newconv2 = {}
        for add_conv in list(newconv.keys()):
            convertors[add_conv] = newconv[add_conv]
            txtline = convExplore(lines, add_conv)
            convertors[add_conv].input_txt = txtline
            if ('GRAPH' in txtline):
                convertors[add_conv].isData = True
            elif (is_number(txtline)):
                convertors[add_conv].value = float(txtline)
            else:
                if (len(re.findall('(if\s+|IF\s+|If\s+|if\(|IF|If)', txtline)) > 0): convertors[add_conv].isIf = True
                convertors[add_conv].Eq = txtline
                conv_temp = re.split('=|\*|>|<|,|\+|\^|\-|[)]|[(]|[{]|[}]|/|\s+|%%', txtline)
                for i in range(0, len(conv_temp)):
                    conv_temp[i] = conv_temp[i].strip()
                    if (conv_temp[i] in supported_func):
                        convertors[add_conv].hasFunction = True
                        Rformatting = []
                        for x in re.split('(\()', convertors[add_conv].Eq): Rformatting.append(x.strip())
                        convertors[add_conv].Eq = ''.join(Rformatting)
                restricted_words = ['', 'and', 'if', 'or', 'If', 'IF', 'AND', 'THEN', 'then', 'ELSE', 'else',
                                    'OR'] + supported_func
                conv_temp = re.split('=|\*|>|<|,|\+|\^|\-|\)|\(|[{]|[}]|/|\s+|%%', convertors[add_conv].Eq)
                for i in range(0, len(conv_temp)):
                    if ((conv_temp[i].strip() not in restricted_words) and (not is_number(conv_temp[i].strip()))):
                        if (conv_temp[i].strip() not in list(convertors.keys()) and conv_temp[i].strip() not in list(
                                models.keys()) and conv_temp[i].strip() not in list(flows.keys())):
                            newconv2[conv_temp[i].strip()] = convertor(conv_temp[i].strip())
                        if (conv_temp[i].strip() not in convertors[add_conv].in_convertors):
                            convertors[add_conv].in_convertors.append(conv_temp[i].strip())
        if len(list(newconv2.keys())) > 0:
            newconv = newconv2
        else:
            rr = False

    additional_lines = {}
    ln = 0
    while ln < len(lines):
        parts = lines[ln].strip().split()
        var = re.split('([)]|[(]|[{]|[}]|\s+|\*)', parts[0])[0]
        special_words = ['INIT', '', 'THEN', 'then', 'if', 'IF', 'else', 'ELSE'] + supported_func + list(
            flows.keys()) + list(convertors.keys()) + list(models.keys())
        if (var not in special_words and not lines[ln].startswith(var + '(t)')):
            txtline = convExplore(lines, var)
            if ('GRAPH' in txtline):
                convertors[var] = convertor(var)
                convertors[var].input_txt = txtline
                convertors[var].isData = True
            elif (is_number(txtline)):
                convertors[var] = convertor(var)
                convertors[var].input_txt = txtline
                convertors[var].value = float(txtline)
            else:
                additional_lines[var] = lines[ln]
        ln += 1

    ###############
    ##inputs={}
    for conv in list(convertors.keys()):
        if (convertors[conv].isData):
            txt = convertors[conv].input_txt.strip().split()
            arg = txt[0]
            arg = re.split('GRAPH\(|\)', arg)
            while ('' in arg): arg.remove('')
            convertors[conv].Data = inputData(conv)
            if (arg[0] in list(convertors.keys())):
                convertors[conv].Data.xname = arg[0]
            else:
                convertors[conv].Data.xname = 't'
            t = [];
            v = []

            for i in range(1, len(txt)):
                txts = re.split('(,|\(|\))', txt[i])
                while ('' in txts): txts.remove('')
                while (',' in txts): txts.remove(',')
                if ('(' in txts):
                    t.append(float(txts[1]))
                elif (')' in txts):
                    v.append(float(txts[0]))

            # inputs[conv+'_Time']=t
            # inputs[conv+'_Value']=v
            convertors[conv].Data.x = t
            convertors[conv].Data.y = v
    ###################################
    # writing output
    if (not os.path.isdir(outPath)):
        os.mkdir(outPath)
    ff = open(outPath + "/" + outputName + ".R", 'w')
    ff.write("rm(list = ls())\n")
    ff.writelines(["library(deSolve) #If you don't have the package 'deSolve' installed, install it.\n"])

    convlist = list(convertors.keys())
    parms = []
    convT = []

    ff.writelines(["\n"])
    convs = []
    for conv in convlist:
        if (convertors[conv].value is not None): convs.append(conv)
    # convs = sorted(convs)
    for i in range(0, len(convs)):
        convertors[convs[i]].value = '{0:g}'.format(convertors[convs[i]].value)
    #    ff.writelines([convs[i], " <- ", str(convertors[convs[i]].value), "\n"])

    ff.writelines(["model<-function(t,Y,parms,...) { \n"])
    # -----
    ff.writelines(["\n"])
    ff.writelines(["\tTime <<- t\n"])
    Eqs = list(models.keys())
    Eqs_init = []
    for eq in Eqs:
        ff.writelines(["\t", eq, " <- Y['", eq, "']\n"])
        Eqs_init.append(eq)

    ff.writelines(["\n"])
    # ----
    for conv in convlist:
        if (convertors[conv].value is not None):
            ff.writelines(["\t", conv, " <- parms['", conv, "']\n"])
            parms.append(conv)
            convT.append(conv)

    for conv in convT: convlist.remove(conv)

    ff.writelines(["\n"])
    convT2 = []
    for conv in convlist:
        if convertors[conv].isData:
            if (convertors[conv].Data.xname != 't'):
                if (convertors[conv].Data.xname not in convT2 and convertors[conv].Data.xname in convlist and not
                convertors[(convertors[conv].Data.xname)].isData):
                    convT2.append(convertors[conv].Data.xname)
                    ff.writelines(
                        ["\t", convertors[conv].Data.xname, " <- ", convertors[convertors[conv].Data.xname].Eq, "\n"])
                elif (convertors[conv].Data.xname not in convT2 and convertors[conv].Data.xname in convlist and
                      convertors[(convertors[conv].Data.xname)].isData):
                    ff.writelines(["\t", convertors[conv].Data.xname, " <- inputData(",
                                   convertors[convertors[conv].Data.xname].Data.xname, ", '",
                                   convertors[conv].Data.xname, "')\n"])
                ff.writelines(["\t", conv, " <- inputData(", convertors[conv].Data.xname, ", '", conv, "')\n"])
                convT2.append(conv)
            else:
                ff.writelines(["\t", conv, " <- inputData(t, '", conv, "')\n"])
                convT2.append(conv)

    for conv in convT2: convlist.remove(conv)
    # parameters (with "plain" numerical/simple values) and GRAPH (data) removed from convlist now

    initialized = convT + convT2 + Eqs_init
    # ------
    ff.write("###CONVERTORS & FLOWS###\n")
    flowlist = list(flows.keys())
    convsflows = convlist + flowlist
    while convsflows:
        for fl in convsflows:
            if fl in flowlist:
                dependents = flows[fl].in_flows + flows[fl].in_convertors
            elif fl in convlist:
                dependents = convertors[fl].in_convertors
            flowWrite = False
            if len([i for i in dependents if i in initialized]) < len(dependents) and [i for i in dependents if
                                                                                       i in convsflows]:
                flowWrite = False
            else:
                flowWrite = True
            if (flowWrite):
                if fl in flowlist:
                    if flows[fl].isIf: flows[fl].Eq = if_extract(flows, fl)
                    converted = flows[fl]
                elif fl in convlist:
                    if convertors[fl].isIf: convertors[fl].Eq = if_extract(convertors, fl)
                    converted = convertors[fl]
                ff.writelines(["\t", fl, " <- ", str(converted.Eq), "\n"])
                initialized.append(fl)
                convsflows.remove(fl)

    ff.writelines(["\n"])
    if (len(list(additional_lines.keys())) > 0):
        ff.writelines(["\n  ###------ The following lines have not been translated!!\n"])
        for i in range(0, len(list(additional_lines.keys()))):
            if ('\r' in additional_lines[list(additional_lines.keys())[i]]): additional_lines[
                list(additional_lines.keys())[i]] = additional_lines[list(additional_lines.keys())[i]].replace('\r',
                                                                                                               " ")
            ff.writelines(["\t#--- ", additional_lines[list(additional_lines.keys())[i]], "\n"])
    ff.writelines(["  ###-------------\n"])
    # ------
    rank = 1
    Eqs = list(models.keys())
    loop = True
    EqsL = []
    while (loop):
        EqsT = []

        for eq in Eqs:
            if (models[eq].rank == rank):
                ff.writelines(["\n\t d", eq, " = "])
                if (len(models[eq].inflows) > 0):
                    ff.writelines([models[eq].inflows[0], " "])
                    if (len(models[eq].inflows) > 1):
                        for j in range(1, len(models[eq].inflows)):
                            ff.writelines([" + ", models[eq].inflows[j], " "])
                if (len(models[eq].outflows) > 0):
                    for j in range(0, len(models[eq].outflows)):
                        ff.writelines([" - ", models[eq].outflows[j], " "])
                rank += 1
                EqsT.append(eq)
                EqsL.append(eq)
        for eq in EqsT: Eqs.remove(eq)
        if len(Eqs) == 0: loop = False
    # ----
    ff.writelines(["\n"])
    ff.writelines(["\t return(list(c(d", EqsL[0]])
    for i in range(1, len(EqsL)): ff.writelines([",\n d", EqsL[i]])
    ff.writelines([")))\n}"])
    ff.writelines(["\n##############################################\n"])
    ff.writelines(["##############################################\n"])
    ########################-----------------------------------------------------
    ff.writelines(["\n"])

    for eq in EqsL:
        if not is_number(models[eq].init):
            if models[eq].init in list(convertors.keys()):
                models[eq].init = "parms['" + models[eq].init + "']"

    convlist = list(convertors.keys())
    # convs[0], " = ",
    # convs[i], " = ",
    if len(convs) > 0:
        ff.writelines(["parms <- c(", str(convertors[convs[0]].value)])
        for i in range(1, len(convs)): ff.writelines([", \n", str(convertors[convs[i]].value)])
        ff.writelines([")\n"])

    ff.write('parm_names <- c("' + convs[0] + '"')
    for i in range(1, len(convs)): ff.write(',\n"' + convs[i] + '"')
    ff.writelines(")\n")
    ff.write("names(parms) <- parm_names\n")
    ff.writelines(["Y <- c(", EqsL[0], " = ", str(models[EqsL[0]].init)])
    for i in range(1, len(EqsL)): ff.writelines([",\n", EqsL[i], " = ", str(models[EqsL[i]].init)])
    ff.writelines([")\n"])

    # ------------------
    ## writing data & support functions

    convlist = list(convertors.keys())
    convs = []
    for conv in convlist:
        if (convertors[conv].isData): convs.append(conv)
    fs = open(outPath + "/" + outputName + "_functions.R", 'w')
    if len(convs) > 0:

        for i in range(0, len(convs)):
            fd = open(outputName + "/" + outputName + "_Data_" + convertors[convs[i]].Data.name + ".csv", 'w')
            fd.writelines([convertors[convs[i]].Data.xname, ",", convertors[convs[i]].Data.name])
            for j in range(0, len(convertors[convs[i]].Data.x)):
                fd.writelines(["\n", str(convertors[convs[i]].Data.x[j]), ",", str(convertors[convs[i]].Data.y[j])])
            fd.close()

        fs.writelines(["input.Data <- c()\n"])
        for i in range(0, len(convs)):
            fs.writelines([" temp <- read.csv('", outputName, "_Data_", convertors[convs[i]].Data.name, ".csv')\n"])
            fs.writelines([" temp <- list(", convertors[convs[i]].Data.name, " = temp)\n"])
            fs.writelines([" input.Data <- c(input.Data, temp)\n"])
        # fs.writelines(["}\n"])
        fs.writelines(["rm(temp)\n"])
        # ----
        fs.writelines(["\ninputData <- function(x,name,datalist=input.Data) {\n"])
        fs.writelines(["\tdf=datalist[[name]]\n\tminT <- min(df[,1],na.rm=T)\n\tmaxT <- max(df[,1],na.rm=T)\n"])
        fs.writelines([
                          "\tif (x < minT | x > maxT) {\n\t\tl <- lm(get(colnames(df)[2])~poly(get(colnames(df)[1]),3),data=df)\n\t\tdo <- data.frame(x); colnames(do) <- colnames(df)[1]\n\t\to <- predict(l,newdata=do)[[1]]"])
        fs.writelines(["\t} else {\n"])
        fs.writelines(
            ["\tt1 <- max(df[which(df[,1] <= x),1])\n\tt2 <- min(df[which(df[,1] >= x),1])\n\tif (t1 == t2) {\n"])
        fs.writelines(["\t\to <- df[t1,2]}\n"])
        fs.writelines([
                          "\telse {\n\t\tw1=1/abs(x-t1);w2=1/abs(x-t2)\n\to <- ((df[which( df[,1] == t1),2]*w1)+(df[which( df[,1] == t2),2]*w2)) / (w1+w2) } }\n  o }\n"])

    fs.writelines(["#----------------\nCOUNTER <- function(x,y) {\n"])
    fs.writelines(["\tif (Time == time[1]) COUNTER_TEMP <<- x\n"])
    fs.writelines(["\tif (!exists('COUNTER_TEMP')) COUNTER_TEMP <<- x\n"])
    fs.writelines(["\telse COUNTER_TEMP <- COUNTER_TEMP  + 1\n"])
    fs.writelines(["\tif (COUNTER_TEMP == y) COUNTER_TEMP  <<- x\n"])
    fs.writelines(["\treturn(COUNTER_TEMP)}\n"])
    fs.writelines(["#--------\nTREND <- function(x,y,z=0) {\n"])
    fs.writelines(["\tif (!exists('AVERAGE_INPUT')) AVERAGE_INPUT <<- z\n"])
    fs.writelines(["\tCHANGE_IN_AVERAGE <- (x - AVERAGE_INPUT) / y\n"])
    fs.writelines(["\tAVERAGE_INPUT <<- AVERAGE_INPUT + (DT * CHANGE_IN_AVERAGE)\n"])
    fs.writelines(["\tTREND_IN_INPUT <- (x - AVERAGE_INPUT) / (AVERAGE_INPUT * y)\n"])
    fs.writelines(["\tif (Time == time[length(time)]) rm(AVERAGE_INPUT,envir=environment(TREND))\n"])
    fs.writelines(["\tTREND_IN_INPUT}\n"])
    fs.writelines(["#-----------------\nDELAY <- function(x,y,z=NA) { x } # should be developed!\n"])
    fs.close()

    ff.writelines(["\nsource('", "test", "_functions.R')\n"])
    ff.writelines(["DT <- 0.25\n"])
    ff.writelines(["time <- seq(0.001,100,DT)\n"])
    ff.writelines(["out <- ode(func=model,y=Y,times=time,parms=parms,method='rk4')\n"])
    ff.writelines(["plot(out)\n"])
    ff.close()
    print("STELLA model is successfully translated into R!\n")
    print("Babak Naimi (naimi@itc.nl)\n")
    print("Alexey Voinov (voinov@itc.nl)\n")
    print("Jessica Gorzo (gorzo@wisc.edu)\n")


def main():
    if len(sys.argv) < 3:
        print("Usage: StellaR <input_stella.txt> <outname>\n")
        print("\t -- input_stella.txt is a text file exported from STELLA model\n")
        print(
            "\t -- outname is the name of R project where the main R script (outname.R) as well as data files and other functions are stored\n")
        sys.exit()

    fname1 = sys.argv[1]
    outputName = sys.argv[2]

    run(fname1=fname1, outputName=outputName)


if __name__ == '__main__':
    main()
