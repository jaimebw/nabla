from pathlib import Path
import os
from typing import Tuple
import shutil
import subprocess
from functools import partial


# run subprocess as I want
run_shell = partial(subprocess.run,shell = True,capture_output=True) 

class CheckBaseClass:
    """
    Base class for the checking classes.
    Implements common methods for the rest of the clasess.
    """
    def __init__(self,dict_data:str,dict_type:str)->None:
        self.dict_data = dict_data
        self.dict_type = dict_type
        self.path = Path(f"{dict_type}_test").resolve()
        self.system_path = self.path/"system"

    def _generate_system_dir(self)->None:
        """
        Generate the system dir to save the sim files
        """
        self.path.mkdir()
        self.system_path.mkdir()

    def _generate_controlDict(self):
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

    def _delete_sim(self)->None:
        """
        Delete the simulation dir and everything inside
        """
        shutil.rmtree(self.path.resolve())

    @staticmethod
    def _move_to_dir(path_to_move)->None:
        os.chdir(path_to_move)


class CheckBlocMeshDict(CheckBaseClass):
    """
    Checks that the blockMeshDict works without issues
    """
    def __init__(self,dict_data:str) ->None:
        super().__init__(dict_data,"blockMesh")
        self.dict_type = "blockMesh"
    def __generate_blockMeshDict(self)->None:
        dict_data = self.dict_data.replace(
            "convertToMeters", f"convertToMeters 1 {str(self.path)}"
        )
        fpath = str(self.system_path/"blockMeshDict")
        with open(fpath,"w") as f:
            f.write(dict_data)

        
    def __run_util(self)->subprocess.CompletedProcess:
        """
        Runs the blockMesh command

        """
        other = 'su'
        command_text = other + "&&" + "blockMesh"
        result = run_shell(args = command_text)
        return result


    def check_dict(self)->Tuple[int,str]:
        """
        Checks that the blocMeshDict runs by running a the blockMesh application.
        """
        self._generate_system_dir()
        self._generate_controlDict()
        self.__generate_blockMeshDict()
        self._move_to_dir(str(self.path))
        result = self.__run_util()
        self._delete_sim()
        if not result.returncode:
            return (1,result.stdout.decode("utf-8"))
        else:
            error = result.stderr.decode("utf-8")
            return (0,error)



class CheckDecomposeParDict(CheckBaseClass):
    """
    Checks that the decomposeParDict works without issues
    """
    def __init__(self,dict_data:str) ->None:
        super().__init__(dict_data,"decomposePar")
        self.dict_type = "decomposePar"

    def __generate_decomposeParDict(self)->None:
        fpath = str(self.system_path/"decomposeParDict")
        with open(fpath,"w") as f:
            f.write(self.dict_data)

    def __run_util(self)->subprocess.CompletedProcess:
        """
        Runs the decomposePar command

        """
        other = 'su'
        command_text = other + "&&" + "decomposePar"
        result = run_shell(args = command_text)
        return result

    def check_dict(self)->Tuple[int,str]:
        """
        Checks that the decomposePar runs by running a the decmomposePar application.
        """
        self._generate_system_dir()
        self._generate_controlDict()
        self.__generate_decomposeParDict()
        self._move_to_dir(str(self.path))
        result = self.__run_util()
        self._delete_sim()
        if not result.returncode:
            return (1,result.stdout.decode("utf-8"))
        else:
            error = result.stderr.decode("utf-8")
            return (0,error)
