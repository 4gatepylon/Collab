# import module
import openpyxl
from enum import Enum
from entity import Cell
import yaml

from openpyxl import load_workbook
from openpyxl import Workbook
from openpyxl.utils import FORMULAE

import pprint as _pp
pp = _pp.PrettyPrinter(indent=4)
def pprint(string):
    pp.pprint(string)

# Yaml Declarations
__SOURCES = "Sources"
__SOURCE = "Source"
__TYPE = "Type"
__PATH = "Path"
__NAME = "Name"         # Optional
__ENTITIES = "Entities" # Optional
_ID = "Id"
# __NAME                # Optional
__LOC = "CellLocation"  # Optional
__CACHE = "CachedVal"   # Optional
__VAL = "FuncVal"       # Optional
__GROUPS = "Groups"     # Optional
__META = "Metadata"     # Optional
__CHILDREN = "Children"

# Source Type
__PYTHON_STDOUT_FILE = "PYTHON_STDOUT_FILE"
__EXCEL_FILE = "EXCEL_FILE"
########################################################### Deserialization
# def deserialize(filename):
#     wb = load_workbook(filename=filename)
#     yaml = {}
#     yaml["sheets"] = []
#     for sheet_name in wb.sheetnames:
#         sheet = deserialize_sheet(wb[sheet_name])
#         sheet["Type"] = "Sheet"
#         sheet["Name"] = sheet_name
#         yaml["sheets"].append(sheet)
#     return yaml

# # Note that coords start at 1 instead of 0
# # def cell_name2coords(cell_name):
# #     pass

# # do not support merged cells for now
# def deserialize_sheet(sheet):
#     yaml = {}
#     yaml["cells"] = []
#     # Max containing data
#     for column in range(sheet.min_column, sheet.max_column + 1):
#         for row in range(sheet.min_row, sheet.max_row + 1):
#             cell = sheet.cell(row, column)
#             if cell.value != None:
#                 yaml["cells"].append({
#                     "Type": "Cell",
#                     "Name": cell.coordinate,
#                     "FuncValue": cell.value,
#                 })
#     return yaml

def deserialize(excel_path, yaml_path):
   pass

########################################################### Serialization
class EntityType(Enum):
   EXCEL = 1
   CELL = 2
   FUNCTION = 3
   PLOT = 4

def map_number_to_letter(number) -> str:
   '''
   1 -> A
   '''
   return chr(ord('@')+number)

def serialize_excel_yaml(filename):
# load excel with its path
   try:
      wrkbk = openpyxl.load_workbook(filename)
   except:
      return ValueError(f'{filename} is not a valid path to an excel file')
   
   sheet = wrkbk.active
   entities = []
   yaml_obj = {'Source': {'Type': 'EXCEL', 'Path': filename, 'Entities': entities}}

   # iterate through excel and display data
   for row in range(1, sheet.max_row+1):         
      for col in range(1, sheet.max_column+1):
         col_letter = map_number_to_letter(col)
         cell_obj = sheet.cell(row=row, column=col)
         entity = {'Entity': {'type': 'cell', 'value': cell_obj.value, 'location': f'{col_letter}{row}'}}
         entities.append(entity)
         # print(cell_obj.value, end=" ")

   with open(f'{filename}.yaml', 'w') as file:
      yaml.dump(yaml_obj, file)

if __name__ == "__main__":
   # d = deserialize("ex.xlsx")
   deserialize("output.xslx", "input.yaml")
   # pprint(d)
   # print("Serializing into test_output.yaml")
   # serialize_excel_yaml()