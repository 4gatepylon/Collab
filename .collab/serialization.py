import re
import openpyxl
from enum import Enum
import yaml
from enum import Enum
from openpyxl import load_workbook
from openpyxl import Workbook
from openpyxl.utils import FORMULAE

import subprocess
from subprocess import Popen, PIPE
from glob import glob

# Helpful for debugging
import pprint as _pp
pp = _pp.PrettyPrinter(indent=4)
def pprint(string):
    pp.pprint(string)

# Any process you call in your build cannot take longer than 5 seconds to run
PROC_TIMEOUT = 5

# Yaml Structure is
# A list of sources with a type, path, and entities (if it's an excel file)
__SOURCES = "Sources"
__TYPE = "Type"
__PATH = "Path"
__ENTITIES = "Entities" # Optional

# Entity Structure
__LOC = "CellLocation"
__VAL = "Value"
__GROUPS = "Groups"

# Deps is a list or dependencies, for a dynamic type it is instead a singleton
# string with the filename of a single source
__DEPS = "Dependencies"

# Source Type
__PYTHON_STDOUT_FILE = "PYTHON_STDOUT_FILE"
__EXCEL_FILE = "EXCEL_FILE"

# Entity Types
__SHEET = "Sheet"
__CELL = "Cell"
__DYNAMIC = "DynamicCell"

py_re = re.compile(".*\.py$")
excel_re = re.compile(".*\.xlsx$")

# Turn Excel into Yaml
def serialize(filenames=None, yaml_path="master.yaml", TESTONLY=False):
   TESTONLY_PREPEND = ""
   if TESTONLY:
      TESTONLY_PREPEND = "TEST_"
   if filenames is None:
      filenames = glob("../*.py") + glob("../*.xlsx")
   serialized = {}
   sources = []
   serialized[__SOURCES] = sources
   for filename in filenames:
      matches_py = py_re.match(filename)
      matches_excel = excel_re.match(filename)
      if not matches_py and not matches_excel:
         raise Exception("Cannot parse Non-py or excel file. Found: " + filename)

      entities = []
      source = {
         __TYPE: __EXCEL_FILE if matches_excel else __PYTHON_STDOUT_FILE,
         __PATH: filename,
         __ENTITIES: entities
      }
      if matches_excel:
         wb = load_workbook(filename=filename)
         serialize_entities(entities, wb)
      sources.append(source)
   try:
      yp, yfp = yaml_path.rsplit("/", 1)
      yp = yp + "/"
   except ValueError:
      yp = ""
      yfp = yaml_path
   with open(yp + TESTONLY_PREPEND + yfp, "w") as yf:
      yaml.dump(serialized, yf)

def serialize_entities(entities, wb):
   for sheet_name in wb.sheetnames:
      print("Found sheet with name " + sheet_name)
      sheet = wb[sheet_name]
      deps = []
      entities.append({
         __TYPE: __SHEET,
         __VAL: sheet_name,
         __DEPS: deps,
      })
      for column in range(sheet.min_column, sheet.max_column + 1):
         for row in range(sheet.min_row, sheet.max_row + 1):
            cell = sheet.cell(row, column)
            if cell.value != None:
               deps.append({
                  __TYPE: __CELL,
                  __LOC: cell.coordinate,
                  __VAL: cell.value,
               })

# I'm fairly sure this is correct, but I'm too tired to prove it,
# and it's not actually just plain numbering because there is no 0
# i.e. A = 1 not 0, and there does not exist A0, so every time you go up,
# you also shift up...
num_letters = ord("Z") - ord("A") + 1
def letter2number(letter):
   if ord(letter) < ord("A") or ord(letter) > ord("Z"):
      raise Exception("Must be uppercase letter!")
   # A => 1, B => 2, ...
   return ord(letter) - ord("A") + 1
def letters2number(letters):
   # A = 1, B = 2, ...
   # AA = 26 + 1 = 27, BB = 2 * (26) + 2
   acc = 0
   for letter in letters:
      acc *= num_letters
      acc += letter2number(letter)
   return acc
def number2letters(number):
   if number <= 26:
      return chr(ord("A") - 1 + number)
   return number2letters(number // 26) + number2letters(number % 26)
# these two expect/return in the column, row format
def deserialize_loc(loc):
   i = 0
   while i < len(loc) and not loc[i].isdigit():
      i += 1
   return letters2number(loc[:i]), int(loc[i:])
def serialize_loc(col, row):
   return number2letters(col) + str(row)

def fetch_or_fail(maplike, key):
   if not key in maplike:
      raise Exception("Could not find " + key)
   return maplike[key]

def deserialize(yaml_path="master.yaml", TESTONLY=False):
   TESTONLY_PREPEND = ""
   if TESTONLY:
      TESTONLY_PREPEND = "TEST_"
   # Load the YAML that we want to deserialize from
   y = None
   with open(yaml_path) as f:
      y = yaml.load(f, yaml.loader.SafeLoader)
   if y is None:
      raise Exception("Failed to load YAML")
   # Deserialize  from the YAML
   srcs = fetch_or_fail(y, __SOURCES)
   for y_source in srcs:
      fname = fetch_or_fail(y_source, __PATH)
      if excel_re.match(fname):
         wb = Workbook()
         # Quick Hack to remove trash that is automatically generated
         for trash in wb.sheetnames:
            wb.remove_sheet(wb[trash])
         print("sheetnames is " + str(wb.sheetnames))
         ents = fetch_or_fail(y_source, __ENTITIES)
         # Deserialize sheets (only top level entities for now)
         for y_entity in ents:
            t = fetch_or_fail(y_entity, __TYPE)
            if t == __SHEET:
               ws = wb.create_sheet(title=y_entity[__VAL])
               dps = fetch_or_fail(y_entity, __DEPS)
               # Deserialize Cells (only sub top level entities for now)
               for y_dep in dps:
                  column, row = deserialize_loc(y_dep[__LOC])
                  # Deserialize cells
                  subt = fetch_or_fail(y_dep, __TYPE)
                  if subt == __CELL:
                     d = y_dep[__DEPS] if __DEPS in y_dep else None
                     if not d is None and len(d) > 0:
                        raise Exception("Tracking cross-cell dependencies not yet supported")
                     _ = ws.cell(column=column, row=row, value=y_dep[__VAL])
                  ############################################################## Dynamic Deserialization
                  elif subt == __DYNAMIC:
                     if not __VAL is None:
                        raise Exception("Non-null values not supported for dynamic types: ", __VAL)
                     file2output = y_dep[__DEPS]
                     # Here is the gimmick we expect
                     folder, pyfile = file2output.rsplit("/", 1)
                     # Create a string for our variable name that they cannot hit
                     nohit = "check_" + str(uuid.uuid4()).replace("-", "_")
                     # Check that it is a valid value to insert into a cell (bool not supported since)
                     # you can create it by passing, say, a positive vs. negative number with an if statement
                     nohit_check = "type(nohit) == str or type(nohit) == int or type(nohit) == float"
                     # Print nohit to standard out so we can catch with subprocess or error out
                     print2stdout = "print(nohit if " + nohit_check + " else raise Exception(\"Bad Value\"), end=\"\")"
                     cmd = [
                        # Invoke python and run it inline
                        "python3",
                        "-c",
                        # import the file, expecting there to be a main (otherwise it will fail)
                        "from " + pyfile + " import main; " + nohit + " = main(); " + print2stdout,
                     ]
                     # This can raise a TimeoutExpired `https://docs.python.org/3/library/subprocess.html#subprocess.Popen.communicate`
                     outs, errs = Popen(cmd, stdout=PIPE, stderr=PIPE, cwd=folder).communicate(timeout=PROC_TIMEOUT)
                     if errs is None or len(errs) == 0 and len(outs) > 0:
                        out = None
                        # Quick hack, but not ideal... it may be better to have them specify in the YAML directly
                        try:
                           out = int(outs)
                        except:
                           try:
                              out = float(outs)
                           except:
                              out = str(outs)
                        if out is None:
                           raise Exception("Failed to initialize output from stdout")
                        _ = ws.cell(column=column, row=row, value=out)
                     else:
                        raise Exception("Failure running subprocess " + file2output + " with error `" + str(errs) + "`")
                  ############################################################## END (Dynamic Deserialization)
            else:
               raise Exception("Top level entities MUST be sheet, but found type " + t)
         yp = fetch_or_fail(y_source, __PATH)
         try:
            yf, yfl = yp.rsplit("/", 1)
            yf = yf + "/"
         except ValueError:
            yf = ""
            yfl = yp
         wb.save(filename=yf + TESTONLY_PREPEND + yfl)
      # Recall, fname is the name defined above the previous if
      elif not py_re.match(fname):
         p = y_source[__PATH] if __PATH in y_source else "UnknownPath"
         raise Exception("Trying to deserialize with unknown file type: " + p)
      # Ignore python files
   

########################################################### Serialization (old and deprecated)
class EntityType(Enum):
   EXCEL = 1
   CELL = 2
   FUNCTION = 3
   PLOT = 4

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
         col_letter = number2letters(col)
         cell_obj = sheet.cell(row=row, column=col)
         entity = {'Entity': {'type': 'cell', 'value': cell_obj.value, 'location': f'{col_letter}{row}'}}
         entities.append(entity)
         # print(cell_obj.value, end=" ")

   with open(f'{filename}.yaml', 'w') as file:
      yaml.dump(yaml_obj, file)

if __name__ == "__main__":
   # These go through master.yaml
   d = serialize()
   deserialize(TESTONLY=True)
   # pprint(d)
   # print("Serializing into test_output.yaml")
   # serialize_excel_yaml()