from tinamit.EnvolturaBF.en.SAHYSMOD import sahysmodIO as IO
import json
import numpy as np

print(IO.read_into_param_dic('D:\\Thesis\\pythonProject\\Tinamit\\tinamit\Calib\\459anew1.inp'))
# p_dict = IO.read_into_param_dic('D:\\Thesis\\pythonProject\\Tinamit\\tinamit\Calib\\459anew1.inp')
#
# with open('D:\\Thesis\\pythonProject\\Tinamit\\tinamit\Calib\\SA_algorithms\\poly_n4.inp', 'w') as f:
#     n1 = p_dict['TO_N1'].tolist()
#     n2 = p_dict['TO_N2'].tolist()
#     n3 = p_dict['TO_N3'].tolist()
#     n4 = p_dict['TO_N4'].tolist()
#     #print(n1)
#     poly_neighors = []
#     for i, n in enumerate(n1):
#         poly_neighors.append([n, n2[i], n3[i], n4[i]])
#         f.write('{},\n'.format(json.dumps([n, n2[i], n3[i], n4[i]])))
#         f.flush()
# f.close()

