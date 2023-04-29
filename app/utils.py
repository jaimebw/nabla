from pathlib import Path
import zipfile
import asyncio
import json
from app import app



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


async def run_command(commands):
    """
    Async command running on Flask. Called in various method.

    PARAMETERS
    ----------
    commands: str or List[str]: command or list of commands
    """
    if type(commands) == str:
        commands = [commands]
    
    results = []
    # Run subprocess and capture output
    commands = " && ".join(commands)
    process = await asyncio.create_subprocess_shell(
        commands,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    output, outerror = await process.communicate()

    # Convert bytes to string
    output_str = output.decode('utf-8').split("\n")
    output_str = {"command":commands,
                  "output":output_str,
                  "error_code":outerror.decode('utf-8')}
    results.append(output_str)
    # Convert bytes to string
    output_str = {"data":results}
    app.logger.debug(type(output_str))
    app.logger.debug(output_str)
    return output_str



