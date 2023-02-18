import subprocess as sp
from .utils import FoamDictError
from pathlib import Path
from typing import List,Dict



class BaseFoam:
    """
    Parent class for the OpenFoam simulations classes
    """
    def __init__(self)->None:
        pass
    def create_file(self, file_name: str, content: str) -> None:
        """
        Creates the cpp file for the simulation
        """
        with open(file_name, 'w') as f:
            f.write(content)
    @staticmethod
    def format_dict(params_dict:Dict)->Dict:
        """
        Format the params dict to as the foam file
        """
        for key in params_dict:
            params_dict[key] = "\t"+key+"  "+params_dict[key]+";"
        return params_dict
        
    @staticmethod
    def check_dictkey_existance(foam_keys:List[str],params:Dict)->bool:
        """
        Check if any of the introduced parametes contains non possible keys for the Open Foam file
        """
        if (set(params) - set(foam_keys) == set()):
            return True
        else:
            raise FoamDictError("One or multiples parameter are not listed in the possible Open Fom dict")
        
    @staticmethod
    def dict_header()->str:
        """
        Returns the header dict of all the Open Foam files
        """
        return r"""/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
    \\  /    A nd           | Version:  9
     \\/     M anipulation  | NABLA UI
\*---------------------------------------------------------------------------*/
"""
    @staticmethod
    def dict_params(dict_type)->str:
        """
        Parameters for the type of file
        """
        return r"""FoamFile
{
    format      ascii;
    class       dictionary;
    object      %s;
}
""" %dict_type
    
    

class BlockMesh(BaseFoam):
    """
    BlockMesh class
    """
    def __init__(self) -> None:
        self.dict_type = "blockMeshDict"

    def __content(self)->str:
        """
        Generate the file content
        """
        header = super().dict_header()
        params = super().dict_params(self.dict_type)
        return header + params + self.domain_string


    def create_file(self) -> None:
        """
        Creates the blockMeshDict file
        
        TO-DO: 
            * Add the spatial varibles to the BlockMesh file
        """
        super().create_file(f"{self.dict_type}", self.__content())


    def set_domain(self,params:Dict):
        """
        Definition of the domain for the simulation
        """
        domain_keys = [
                "xMax",
                "yMax",
                "zMax",
                "xMin",
                "yMin",
                "zMin",
                "xCells",
                "yCells",
                "zCells",
                "xUCells",
                "xMCells",
                "xDCells",
                "yUCells",
                "yMCells",
                "yDCells",
                "zUCells",
                "zMCells",
                "zDCells",
                "xGrading",
                "xUgrading",
                "xMgrading",
                "xDgrading",
                "yGrading",
                "yUgrading",
                "yMgrading",
                "yDgrading",
                "zGrading",
                "zUgrading",
                "zMgrading",
                "zDgrading",
                "leadGrading"
                ]
        super().check_dictkey_existance(domain_keys,params)

        self.domain_string = "domain\n{\n"
        for key in params: 
            self.domain_string = self.domain_string+ "\t"+key+"  "+str(params[key])+";\n"
        self.domain_string = self.domain_string + "}"
        self.domain_params = params

