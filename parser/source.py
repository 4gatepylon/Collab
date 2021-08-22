import enum

class SourceType(enum.Enum):
    PYTHON_FILE = "PYTHON_FILE"
    EXCEL_FILE = "EXCEL_FILE"

# Sources are source files, though in the future they may also be source directories.
class Source():
    def __init__(self, path, name=None):
        self.path = path
        self.name = path if name == None else name
        
    def Type(self):
        raise Exception("Entity with name %s and path %s has no source".format(self.name, self.path))

class PythonFile(Source):
    def Type(self):
        return SourceType.PYTHON_FILE

class ExcelFile(Source):
    def Type(self):
        return SourceType.EXCEL_FILE