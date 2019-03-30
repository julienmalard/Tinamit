from tinamit.envolt.mds import VarAuxiliar


class VarAuxiliarVensim(VarAuxiliar):
    def __init__(símismo, nombre, unid, editable, ec, hijos, parientes, líms=None, info=''):
        super().__init__(nombre, unid, ec=ec, hijos=hijos, parientes=parientes, líms=líms, info=info)

        símismo.editable = editable
