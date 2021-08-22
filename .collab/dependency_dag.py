import yaml

from serialization import pprint
from serialization import serialize_to_mp
from serialization import __SOURCES, __EXCEL_FILE, __TYPE, __ENTITIES, __PATH, __DEPS, __CELL_SOURCES, fetch_or_fail, is_eq

# Not used
def find_dependencies_from_excel(filenames=None):
    return find_dependencies_from_yaml_map(serialize_to_mp(filenames=filenames))

# return a list of (source path, {COORD, set([COORDS IT DEPENDS ON])}) (very MVPish function we got going here)
# it presumes certain patterns (i.e. for the equations) and is very, very simple
def find_dependencies_from_yaml_map(dictionary):
    deps = []
    for src in filter(lambda s: fetch_or_fail(s, __TYPE) == __EXCEL_FILE, fetch_or_fail(dictionary, __SOURCES)):
        ents = fetch_or_fail(src, __ENTITIES)
        depMap = {}
        deps.append((fetch_or_fail(src, __PATH), depMap))
        recursively_fill_dep_map(depMap, ents)
    return deps

# might want to look at itertools instead
def stream_flatten(listoflists):
    for l in listoflists:
        for e in l:
            yield e

# this slightly a gimick, assume cells and dynamics are the underlying types
def recursively_fill_dep_map(coord2coords_dependencies, entity_list):
    for entity in entity_list:
        t = fetch_or_fail(entity, __TYPE)
        if t == __CELL or t == __DYNAMIC:
            dps = set()
            if t == __CELL:
                v = fetch_or_fail(entire, __VAL)
                if is_eq(v):
                    dps = parse_deps_from_eq(v)
            elif t == __DYNAMIC:
                dps = set(stream_flatten(fetch_or_fail(fetch_or_fail(entity, __DEPS), __CELL_SOURCES)))
            loc = fetch_or_fail(entity, __LOC)
            if loc in coord2coords_dependencies:
                raise Exception(f"Found location {loc} twice")
            coord2coords_dependencies[loc] = dps
        else:
            # deps are the "children" here
            recursively_fill_dep_map(coord2coords_dependencies, fetch_or_fail(entity, __DEPS))
        

def parse_deps_from_eq(eq_str):
    # return a set please
    raise NotImplementedError # TODO

def diff(old_dict, new_dict):
    old_deps = find_dependencies_from_yaml_map(old_dict_path)
    new_deps = find_dependencies_from_yaml_map(new_dict_path)
    return diff_deps(old_deps, new_deps)

# given two lists of coord, coord it depends on, find the difference between the two DAGs
def diff_deps(old, new):
    pprint(old)
    pprint(new)
    raise NotImplementedError
    pass # TODO

def diff_excel(old_dict_path="master.yaml", source_filenames=None):
    y = None
    with open(yaml_path) as f:
        y = yaml.load(f, yaml.loader.SafeLoader)
    if y is None:
        raise Exception("Failed to load YAML")
    return diff(y, serialize_to_mp(filenames=source_filenames))

if __name__ == "__main__":
    pass