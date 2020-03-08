class Conexión(object):
    def __init__(símismo, de, a, mod_de, mod_a, conv_unid, conv_dims):
        símismo.de = de
        símismo.a = a

        símismo.conv_unid = conv_unid
        símismo.conv_dims = conv_dims
        
    def conv(símismo, val):
        val *= símismo.conv_unid
        if símismo.conv_dims is None:
            return val
        