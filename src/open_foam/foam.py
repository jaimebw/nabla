import subprocess as sp
from pathlib import Path

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

    def __format_dict(self):
        pass
    def __check_existance(self):
        pass
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
\*---------------------------------------------------------------------------*/\n"""
    @staticmethod
    def dict_params(dict_type)->str:
        """
        Parameters for the type of file
        """
        return r"""FoamFile
{{
    format      ascii;
    class       dictionary;
    object      %s;
}}
""" %dict_type
    
    

class BlockMesh(BaseFoam):
    """
    BlockMesh class
    """
    def __init__(self) -> None:
        self.dict_type = "blockMeshDict"
    
    def create_file(self) -> None:
        """
        Creates the blockMeshDict file
        """
        header = super().dict_header()
        params = super().dict_params(self.dict_type)
        content = header + params
        super().create_file(f"{self.dict_type}", content)
