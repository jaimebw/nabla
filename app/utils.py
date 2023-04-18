from pathlib import Path
import zipfile
import json

# TODO: Add test get_zip_directory_structure


def generate_id(name)->str:
    # Simple hash function
    return str(abs(hash(name)))


def get_zip_directory_structure(zip_file_path:str):
    """
    Gets the directory structure from a zip file and returns it as a JSON object
    in the format expected by jsTree. Ignores .DS_Store files and __MACOSX directories.


    TODO:
        Test this on Linux 

    PARAMETERS
    ----------
    zip_file_path: paht to the zip file

    """
    with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
        zip_contents = zip_file.namelist()
    nodes = []
    for item in zip_contents:
        if item.endswith(".DS_Store") or item.startswith("__MACOSX"):
            continue
        path = Path(item)
        if path.parents[0].name == "":
            node = {"id":generate_id(path.name),"parent":"#","text":path.name}
        else:
            node = {"id":generate_id(path.name),"parent":generate_id(path.parents[0].name),"text":path.name}
        nodes.append(node)
    return json.dumps(nodes)
