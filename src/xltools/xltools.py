import openpyxl


class XLToolsError(Exception):
    pass


def read_rows(filename, sheetname, columns, rowoffset=None):
    try:
        wb = openpyxl.load_workbook(filename=filename, data_only=True)
        column_lists = []
        for col in columns:
            col_list = []
            for cell in wb[sheetname][col]:
                if cell.value is None:
                    col_list.append('')
                else:
                    col_list.append(str(cell.value).replace('"', '""'))
            column_lists.append(col_list)
    except Exception as e:
        raise XLToolsError(e) from e
    rows = list(zip(*column_lists))[0 if rowoffset is None else rowoffset - 1:]
    return [row for row in rows if not all(val == '' for val in row)]
