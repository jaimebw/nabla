from pathlib import Path
import os
from typing import Tuple
import shutil
import subprocess
from functools import partial

run_shell = partial(subprocess.run,shell = True,capture_output=True) # run subprocess as I want


class CheckBlocMeshDict:
    """
    Checks that the blockMeshDict works without issues
    """
    def __init__(self,dict_data:str) ->None:
        self.dict_data = dict_data
        self.path = Path("blockMesh_test").resolve()
        self.system_path = self.path/"system"

    def __generate_system_dir(self)->None:
        """
        Generate the system dir to save the sim files
        """
        self.path.mkdir()
        self.system_path.mkdir()
        

    def __generate_controlDict(self):
        """
        Generate the controlDict(its neccesary to run blockMesh).

        PARAMETERS
        ----------
        controlDict_str:string: the minimal data to run the blockMesh using this controlDict

        """

        controlDict_str = r"""/*--------------------------------*- C++ -*----------------------------------*\
          =========                 |
          \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
           \\    /   O peration     | Website:  https://openfoam.org
            \\  /    A nd           | Version:  9
             \\/     M anipulation  |
        \*---------------------------------------------------------------------------*/
        FoamFile
        {
            format      ascii;
            class       dictionary;
            object      controlDict;
        }
        // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

        application     rhoSimpleFoam;

        startFrom       latestTime;

        startTime       0;

        stopAt          endTime;

        endTime         1000;

        deltaT          1;

        writeControl    timeStep;

        writeInterval   50;

        purgeWrite      0;

        writeFormat     ascii;

        writePrecision   10;

        writeCompression off;

        timeFormat      general;

        timePrecision   6;

        runTimeModifiable true;
        // ************************************************************************* //"""
        fpath = str(self.system_path/"controlDict")

        with open(fpath,"w") as f:
            f.write(controlDict_str)


    def __generate_blockMeshDict(self)->None:
        dict_data = self.dict_data.replace(
            "convertToMeters", f"convertToMeters 1 {str(self.path)}"
        )
        fpath = str(self.system_path/"blockMeshDict")
        with open(fpath,"w") as f:
            f.write(dict_data)

    def __delete_sim(self)->None:
        """
        Delete the simulation dir and everything inside
        """
        shutil.rmtree(self.path.resolve())
        
    def __run_blockMesh(self)->subprocess.CompletedProcess:
        """
        Runs the blockMesh command

        """
        other = 'su'
        #dirpath = "cd "+ str(self.path.resolve())
        command_text = other + "&&" + "blockMesh"
        result = run_shell(args = command_text)
        return result

    @staticmethod
    def __move_to_dir(path_to_move)->None:
        os.chdir(path_to_move)

    def check_dict(self)->Tuple[int,str]:
        """
        Checks that the blocMeshDict runs by running a the blockMesh application.
        """
        self.__generate_system_dir()
        self.__generate_controlDict()
        self.__generate_blockMeshDict()
        self.__move_to_dir(str(self.path))
        result = self.__run_blockMesh()
        self.__delete_sim()
        if not result.returncode:
            return (1,result.stdout.decode("utf-8"))
        else:
            error = result.stderr.decode("utf-8")
            return (0,error)

