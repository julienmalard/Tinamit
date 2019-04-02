from tinamit.envolt.mds import VarAuxiliar


class VarAuxiliarVensim(VarAuxiliar):
    def __init__(símismo, nombre, unid, editable, ec, parientes, dims, líms=None, info=''):
        super().__init__(nombre, unid, ec=ec, parientes=parientes, dims=dims, líms=líms, info=info)

        símismo.editable = editable
