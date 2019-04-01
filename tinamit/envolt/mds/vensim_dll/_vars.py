from tinamit.envolt.mds import VarAuxiliar


class VarAuxiliarVensim(VarAuxiliar):
    def __init__(símismo, nombre, unid, editable, ec, parientes, líms=None, info=''):
        super().__init__(nombre, unid, ec=ec, parientes=parientes, líms=líms, info=info)

        símismo.editable = editable
