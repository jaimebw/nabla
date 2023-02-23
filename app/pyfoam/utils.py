from pathlib import Path 
import os

FOAM_DIR = Path(os.environ.get('FOAM_DIR'))

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


def check_foam_installation()->bool:
    """
    Check if Open Foam is installed in the system

    """
    path_to_foam = FOAM_DIR
    if path_to_foam.exists():
        return True
    else:
        return False

def generate_directory_tree()->None:
    """
    Generate the directory tree for the simulation
    """
    current_path = Path("")
    dir_names = ["0","constant","system","dynamicCode"]
    
    for i in dir_names:
        Path(current_path/i).mkdir()

