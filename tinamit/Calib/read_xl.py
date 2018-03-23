from xlrd import open_workbook


def read_xl_file(file_name='D:\\Thesis\\data\\observed water table depth and elevation_17112015.xlsx'):
    dw_90 = {}
    #{ 'n_poly' : [dw_90_pre, dw_90_post]}
    wb = open_workbook(file_name)
    water_table_depth = wb.sheets()[0]
    #print(water_table_depth)
    number_of_rows = water_table_depth.nrows
    #number_of_columns = water_table_depth.ncols

    for row in range(2, number_of_rows - 5):
        n_poly = water_table_depth.cell(row, 6).value
        dw_90_pre = water_table_depth.cell(row, 29).value
        dw_90_post = water_table_depth.cell(row, 30).value
        dw_90[n_poly] = [dw_90_pre, dw_90_post]
        #print(dw_90)
    return dw_90
#read_xl_file()
