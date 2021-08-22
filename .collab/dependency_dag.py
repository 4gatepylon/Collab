import yaml
from glob import glob

from serialization import pprint
from serialization import serialize_to_mp, fetch_or_fail, is_eq
from serialization import (
    __SOURCES,
    __EXCEL_FILE,
    __TYPE,
    __ENTITIES,
    __PATH,
    __DEPS,
    __CELL_SOURCES,
    __CELL,
    __DYNAMIC,
    __VAL,
    __LOC,
)

# Not used
def find_dependencies_from_excel(filenames=None):
    return find_dependencies_from_yaml_map(serialize_to_mp(filenames=filenames))

# return a list of (source path, {COORD, set([COORDS IT DEPENDS ON])}) (very MVPish function we got going here)
# it presumes certain patterns (i.e. for the equations) and is very, very simple
def find_dependencies_from_yaml_map(dictionary):
    deps = {}
    for src in filter(lambda s: fetch_or_fail(s, __TYPE) == __EXCEL_FILE, fetch_or_fail(dictionary, __SOURCES)):
        ents = fetch_or_fail(src, __ENTITIES)
        depMap = {}
        deps[fetch_or_fail(src, __PATH)] = depMap
        recursively_fill_dep_map(depMap, ents)
    return deps

# might want to look at itertools instead
def stream_flatten(listoflists):
    if not listoflists is None:
        for l in listoflists:
            if not l is None:
                for e in l:
                    yield e

# this slightly a gimick, assume cells and dynamics are the underlying types
def recursively_fill_dep_map(coord2coords_dependencies, entity_list):
    for entity in entity_list:
        t = fetch_or_fail(entity, __TYPE)
        if t == __CELL or t == __DYNAMIC:
            dps = set()
            if t == __CELL:
                v = fetch_or_fail(entity, __VAL)
                if is_eq(v):
                    dps = parse_deps_from_eq(v)
            elif t == __DYNAMIC:
                dd = fetch_or_fail(entity, __DEPS)
                dps = set(stream_flatten(fetch_or_fail(dd, __CELL_SOURCES)))
            loc = fetch_or_fail(entity, __LOC)
            if loc in coord2coords_dependencies:
                raise Exception(f"Found location {loc} twice")
            coord2coords_dependencies[loc] = dps
        else:
            # deps are the "children" here
            recursively_fill_dep_map(coord2coords_dependencies, fetch_or_fail(entity, __DEPS))
        

def parse_deps_from_eq(eq_str):
    deps = []
    i = 0
    while i < len(eq_str):
        print("hi")
        print(eq_str)
    return deps

def diff(old_dict, new_dict):
    old_deps = find_dependencies_from_yaml_map(old_dict)
    new_deps = find_dependencies_from_yaml_map(new_dict)
    return diff_deps(old_deps, new_deps)

def top_n_space_sep(children, n=10):
    children = list(children)
    return " ".join(children[:min(n, len(children))]) + ("..." if len(children) > n else "")

# given two lists of coord, coord it depends on, find the difference between the two DAGs
# this is not a very smart diff, but it'll get the job done... in the future you'd want to do graph
# transformation or whatever it's called
def diff_deps(old, new):
    msg = []
    for f, deps in new.items():
        added_file_msg = False
        if f in old:
            of = old[f]
            for cell, children in deps.items():
                if not cell in of:
                    msg.append(f"\tADD CELL {cell}")
                    j = top_n_space_sep(children, n=8)
                    if len(j) > 0:
                        msg.append(f"\t\tDEPENDENCIES {j}")
                else:
                    oc = of[cell]
                    if oc != children:
                        msg.append(f"\tMODIFY CELL {cell}")
                        adds = [child for child in children if not child in oc]
                        removes = [child for child in oc if not child in children]
                        if len(adds) > 0:
                            ja = top_n_space_sep(adds, n=8)
                            msg.append(f"\t\tADD {ja}")
                        if len(removes) > 0:
                            jr = top_n_space_sep(removes, n=8)
                            msg.append(f"\t\tREMOVE {jr}")
        else:
            msg.append(f"ADD SOURCE {f}")
    return "\n".join(msg)


def diff_excel(old_dict_path="master.yaml", source_filenames=None):
    y = None
    with open(old_dict_path) as f:
        y = yaml.load(f, yaml.loader.SafeLoader)
    if y is None:
        raise Exception("Failed to load YAML")
    return diff(y, serialize_to_mp(filenames=source_filenames))

if __name__ == "__main__":
    print(diff_excel(source_filenames=["../fibs.xlsx"] + glob("../*.py")))