from app import app
from pathlib import Path
import asyncio


def generate_id(name) -> str:
    # Simple hash function
    return str(abs(hash(name)))

def extract_file_name(file_path: str) -> str:
    """
    NOTE: 
        For some weird reason, in add_sim route, an error raises if I do this
        directly. Like a BadFile Zip error.
    """
    return Path(file_path).name

def is_systemfile(file_name)->bool:
    """
    This function checks if the file is a system file. Like .DS_Store or __MACOSX.
    I need to add Linux support for this too
    """
    if file_name.endswith(".DS_Store") or file_name.startswith("__MACOSX"):
        return True
    else:
        return False


async def run_command(command_list):
    """
    Async command running on Flask. Called in various method.

    PARAMETERS
    ----------
    commands: str or List[str]: command or list of commands
    """

    results = []
    # Run subprocess and capture output
    commands = " && ".join(command_list)
    process = await asyncio.create_subprocess_shell(
        commands,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    output, outerror = await process.communicate()
    # Convert bytes to string
    output_str = output.decode("utf-8").split("\n")
    output_str = {
        "command": command_list,
        "output": output_str,
        "error_code": [outerror.decode("utf-8")],
    }
    results.append(output_str)
    # Convert bytes to string
    app.logger.debug(type(output_str))
    app.logger.debug(output_str)
    return results[0]
