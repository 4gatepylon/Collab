import yaml
from glob import glob

from serialization import pprint
from serialization import serialize_to_mp, fetch_or_fail, is_eq, deserialize_loc, serialize_loc
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
                    # print(dps)
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

def iscap(ch):
    return ord(ch) >= ord("A") and ord(ch) <= ord("Z")

def end_of_coord(start_idx, eq_str, colon_ok=False):
    i = start_idx
    while i < len(eq_str) and iscap(eq_str[i]):
        i += 1
    if i == start_idx:
        return False, start_idx + 1
    if i < len(eq_str) and not eq_str[i].isdigit():
        return False, start_idx + 1 # could be more efficient
    inc = False
    while i < len(eq_str) and eq_str[i].isdigit():
        i += 1
        inc = True
    if not inc:
        return False, start_idx + 1
    ok = set(["+", "-", "/", "*", ",", ")", ";", " "])
    if colon_ok:
        ok.add(":")
    if i < len(eq_str) and not eq_str[i] in ok:
        return False, start_idx + 1
    return True, i

def end_of_range(start_idx, eq_str):
    is_cord, j = end_of_coord(start_idx, eq_str, colon_ok=True)
    if not is_cord:
        return False, j
    if j >= len(eq_str) or eq_str[j] != ":":
        return False, j
    else:
        return end_of_coord(j + 1, eq_str)
    raise NotImplementedError # TODO should return the next index to check or the end + 1 of the range

def cells_in_range(range_str):
    cells = []
    cs = range_str.split(":")
    if len(cs) > 2:
        raise Exception("Ranges have one colon")
    cl, cr = cs
    col_start, row_start = deserialize_loc(cl)
    col_end, row_end = deserialize_loc(cr)
    for i in range(col_start, col_end + 1):
        for j in range(row_start, row_end + 1):
            cells.append(serialize_loc(i, j))
    return cells


def parse_deps_from_eq(eq_str):
    # print(eq_str)
    deps = []
    i = 0
    while i < len(eq_str):
        is_range, j = end_of_range(i, eq_str)
        # print(is_range, j)
        if is_range:
            deps += cells_in_range(eq_str[i : j])
        else:
            is_cord, j = end_of_coord(i, eq_str)
            if is_cord:
                deps.append(eq_str[i : j])
        i = j
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


def diff_excel(old_dict_path="master.yaml", source_filenames=None, with_header=False):
    y = None
    with open(old_dict_path) as f:
        y = yaml.load(f, yaml.loader.SafeLoader)
    if y is None:
        raise Exception("Failed to load YAML")
    d = diff(y, serialize_to_mp(filenames=source_filenames))
    if with_header:
        d = "DIFF\n" + d
    return d

if __name__ == "__main__":
    # print(end_of_coord(0, "AB2)"))
    # print(end_of_coord(5, "=SUM(AB2 :CCCC10)"), "=SUM(AB2 :CCCC10)"[4:10])
    # print(end_of_range(5, "=SUM(AB2:CCCC10)"))
    print(diff_excel(source_filenames=["../fibs.xlsx"] + glob("../*.py"), with_header=True))