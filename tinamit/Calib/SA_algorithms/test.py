from xlrd import open_workbook
import tinamit.Calib.ej.soil_class as SC


# print(IO.read_into_param_dic('D:\\Thesis\\pythonProject\\Tinamit\\tinamit\Calib\\459anew1.inp'))
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

def read_xls(filename):
    wb = open_workbook(filename)
    values = []
    for s in wb.sheets():
        # print 'Sheet:',s.name
        for row in range(1, s.nrows):
            col_names = s.row(0)
            col_value = []
            for name, col in zip(col_names, range(s.ncols - 1)):
                value = (s.cell(row, col).value)
                try:
                    value = str(int(value))
                except:
                    pass
                col_value.append((name.value, value))
            values.append(col_value)
    r_class = []
    for item in values:
        r_class.append(item[1][1])
    print(r_class)


# read_xls('D:\\Thesis\\data\\Book2.xlsx')
def find_overlap():
    H1 = []
    H2 = []
    H3 = []
    H4 = []
    M1 = []
    M2 = []
    M3 = []
    M4 = []
    T1 = []
    T2 = []
    T3 = []
    T4 = []
    for p in range(215):
        if SC.p_soil_class[p] == 1 and SC.p_riv_class[p] == 'head':
            H1.append(p)
        if SC.p_soil_class[p] == 2 and SC.p_riv_class[p] == 'head':
            H2.append(p)
        if SC.p_soil_class[p] == 3 and SC.p_riv_class[p] == 'head':
            H3.append(p)
        if SC.p_soil_class[p] == 4 and SC.p_riv_class[p] == 'head':
            H4.append(p)
        if SC.p_soil_class[p] == 1 and SC.p_riv_class[p] == 'middle':
            M1.append(p)
        if SC.p_soil_class[p] == 2 and SC.p_riv_class[p] == 'middle':
            M2.append(p)
        if SC.p_soil_class[p] == 3 and SC.p_riv_class[p] == 'middle':
            M3.append(p)
        if SC.p_soil_class[p] == 4 and SC.p_riv_class[p] == 'middle':
            M4.append(p)
        if SC.p_soil_class[p] == 1 and SC.p_riv_class[p] == 'Tail':
            T1.append(p)
        if SC.p_soil_class[p] == 2 and SC.p_riv_class[p] == 'Tail':
            T2.append(p)
        if SC.p_soil_class[p] == 3 and SC.p_riv_class[p] == 'Tail':
            T3.append(p)
        if SC.p_soil_class[p] == 4 and SC.p_riv_class[p] == 'Tail':
            T4.append(p)
    print('H1 =', H1)
    print('H2 =', H2)
    print('H3 =', H3)
    print('H4 =', H4)
    print('M1 =', M1)
    print('M2 =', M2)
    print('M3 =', M3)
    print('M4 =', M4)
    print('T1 =', T1)
    print('T2 =', T2)
    print('T3 =', T3)
    print('T4 =', T4)


import numpy as np

a = np.array([1, 2, 3, 4])
b = np.array([2, 3, 4, 5])
print(type(a))
print(a + b)
print((a + b) / 4)
