import ghpythonlib.treehelpers as ght

urscript_list = ght.tree_to_list(x)

def flatten_list(nested_list):
    flat_list = []
    for item in nested_list:
        if isinstance(item, list) or isinstance(item, tuple):
            flat_list.extend(flatten_list(item))
        else:
            flat_list.append(item)
    return flat_list

flat_gcode_list = flatten_list(urscript_list)

file_path = r"C:\Users\andre\Desktop\TU DELFT\Y2Q1\RoboPopsRepository_git\RoboAndreas\URscript.txt"
with open(file_path, "w") as file:
    for path in x.Paths:
        branch = x.Branch(path)
        for item in branch:
            file.write(str(item) + "\n")
        file.write("\n")