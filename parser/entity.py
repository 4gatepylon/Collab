import uuid

# YAML Might look like:
# Source (list of these)
# - Type [EXCEL | PYTHON_STDOUT]
# - Path
# - symbol
#
#
# Entity (list of these)
# - Type [Excel, Cell | Plot | Func | ... ]
# - LocStr [| None]
# - FuncStr [| None]
# - ValStr [| None]
# - Groups

# Everything in an excel spreadsheet is called an Entity. The root entity is an Excel.
# Inside Excels there are sheets. Inside sheets there are cells. Cells can be Funcs
# or StaticValues or DynamicValues. Inside sheets there can also be plots.

# Each entity can belong to a Group. Groups are sets of entities that share characteristics,
# but in implementation they are treated as traits. An example is a table.

# Functions have codes and function inputs. Function inputs are tree structures that have other entities
# which are (colloquially speaking) the dependencies of the function. Note that Func includes implicit functions
# like 1 + 2 + A1 / (A2 * A3 + A4).

############################################################################ Groups
class Group():
    # TODO
    pass

############################################################################ High Level Entities
class Entity():
    pass

class Excel(Entity):
    # TODO
    pass # contains all the entities inside an excell

class Sheet(Entity):
    # TODO
    pass # all the sheets in the excel

# A value should be something that can be read as the input to a function
class Value(Entity):
    @staticmethod
    def FromStr(string):
        # TODO detect what type of value this is
        return Func.FromFuncStr(string)
    pass

class Cell(Value):
    @staticmethod
    def ParseCellLoc(locStr):
        # Assume format is col, row like A1 or AB23
        i = 1
        while not locStr[i].isdigit():
            i += 1
        return locStr[:i], int(locStr[i:])
    
    def __init__(self, locStr, deps=None):
        self.col, self.row = Cell.ParseCellLoc(loc)
        self.deps = deps if deps != None else []
        self.id = uuid.uuid4()

############################################################################ Simple Entities

# A static value encodes a constant like `hello` or `2`
class StaticValue(Value):
    def __init__(self, val):
        self.val = val

class Plot(Entity):
    # TODO
    def __init__(self):
        raise Exception("Not implemented!")

############################################################################ Functions

# FuncInputs are a tree that encodes the inputs to a function, which may be multiple
# and may have other entities (i.e. Funcs or Cells, etc...).
class FuncInputs():
    @staticmethod
    def FromFuncInputsStr(funcInputsStr):
        inputs = []
        start = 0
        end = 0
        nestLevel = 0
        while end < len(funcInputsStr):
            if funcInputsStr[end] == "(":
                nestLevel += 1
            elif funcInputsStr[end] == ")":
                nestLevel -= 1
            elif funcInputsStr[end] == "," and nestLevel == 0:
                # Remove spaces at the end of the entity pointed to
                realEnd = end - 1
                while funcInputsStr[realEnd] == " ":
                    realEnd -= 1
                # TODO this might not be a function, but instead a cell
                inputs.append(Value.FromStr(funcInputsStr[start : realEnd + 1]))
                # Remove spaces at the start of the next entity
                nextStart = end + 1
                while nextStart < len(funcInputsStr) and funcInputsStr[start] == " ":
                    nextStart += 1
                start = nextStart
                end = nextStart
            elif nestLevel < 0:
                raise Exception("nestLevel is %d".format(nestLevel))
            end += 1
        if nestLevel != 0:
            raise Exception("nestLevel terminated on %d".format(nestLevel))
        return FuncInputs(inputs)
    
    # The list inputs is a list of entities (probably StaticCells, DynamicCells, or Funcs)
    def __init__(self, inputs):
        self.inputs = inputs

    # This should return the entity dependencies (TODO)
    def Deps(self):
        raise Exception("Not Implemented!")

class Func(Value):
    ADD_DELIMETER = "+"
    SUB_DELIMITER = "-"
    MULT_DELIMITER = "*"
    DIV_DELIMITER = "/"
    AGG_DELIMITERS = set([
        Func.ADD_DELIMITER,
        Func.SUB_DELIMITER,
        Func.MULT_DELIMITER,
        Func.DIV_DELIMITER,
    ])

    ADD = "ADD"
    SUB = "SUB"
    MULT = "MULT"
    DIV = "DIV"
    AGG_DELIMITER_TO_CODE = {
        Func.ADD_DELIMETER: Func.ADD,
        Func.SUB_DELIMITER: Func.SUB,
        Func.MULT_DELIMITER: Func.MULT,
        Func.DIV_DELIMITER: Func.DIV,
    }

    @staticmethod
    def FromFuncStr(funcStr):
        funcStr = funcStr.strip()
        # i stores the first index after the code/type if this is NOT an implicit/agg function (like +)
        # and the index of the implicit function type (i.e. the agg delimiter) if it's an agg function
        i = 0
        isAgg = False
        isList = False
        while i < len(funcStr) and funcStr[i] != "(":
            if funcStr[i] == ",":
                isList = True
                break
            if funcStr[i] in FuncInputs.AGG_DELIMITERS:
                isAgg = True
                break
            i += 1
        if isList:
            raise Exception("List in Func.FromFuncStr: Should be in FuncInputs.FromFuncInputsStr")
        if i == 0:
            # deal with the case (1 + ...)
            isAgg = True
        if not isAgg:
            j = i
            while j < len(funcStr) and funcStr[j] != ")":
                j += 1
            if j != len(funcStr):
                isAgg = True
        # now we recursively parse the inputs of the function, which, if it's an agg
        # are the element before the agg delimiter and after and otherwise is the comma-seperated
        # list between the first and last `(` and `)`
        if isAgg:
            return Func(AGG_DELIMITER_TO_CODE[funcStr[i]], Func.FromFuncStr(funcStr[i + 1:]))
        else:
            return Func(funcStr[:i], FuncInputs.FromFuncInputsStr(funcStr[i + 1 : -1]))
    
    def __init__(self, code, funcInputs):
        self.code = code
        self.funcInputs = funcInputs

############################################################################ Dynamic Value Entities

# A dynamic value encodes an output from a black box
class DynamicValue(Value):
    # TODO
    def Val(self):
        if self.val is None:
            raise Exception("Has no val")
        else:
            return self.val

class PythonStdOut(DynamicValue):
    # TODO
    pass

# TODO some testing of our object model
if __name__ == "__main__":
    pass