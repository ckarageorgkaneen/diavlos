from services.src.helper import DataUtil

data_util = DataUtil(__file__)
IN_FILES = data_util.files_with_extension('in', 'yaml')
INOUT_FILES = data_util.files_with_extension('inout', 'pickle')
