from pathlib import Path 
import os


class FoamInstallationError(Exception):
    """
    Error class for Foam Installation Error
    """
    pass

class FoamDictError(Exception):
    """
    Error class for Foam keys that are not avalable
    """
    pass


def check_installation()->bool:
    """
    Check if Open Foam is installed in the system

    """
    path_to_foam = Path("/openfoam")
    if not path_to_foam.exists():
        raise FoamInstallationError("Open Foam is not installed in your system")
    else:
        return True

def generate_directory_tree()->None:
    """
    Generate the directory tree for the simulation
    """
    current_path = Path("")
    dir_names = ["0","constant","system","dynamicCode"]
    
    for i in dir_names:
        Path(current_path/i).mkdir()

