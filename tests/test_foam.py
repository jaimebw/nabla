from app.pyfoam import foam, run
from app.pyfoam.utils import check_foam_installation
from pathlib import Path
import pytest
import os


# this docker path, be careful if you use it in local
of_test_dir = Path("../app/tests/test_case") 

domain_dict = {
    "xMax":100,
    "zMax": 50,
        } 

@pytest.mark.skipif(check_foam_installation() == False,reason= "OF not installed in system")
def test_baseFoam():
    test_list = ["xMax","zMax"]
    basefoam = foam.BaseFoam()
    assert basefoam.check_dictkey_existance(test_list,domain_dict) == True


@pytest.mark.skipif(check_foam_installation() == False,reason= "OF not installed in system")
def test_blockMesh():
    # TO-DO: added testing and utils for delentin the files after
    # creation
    blockMesh = foam.BlockMesh()
    blockMesh.set_domain(domain_dict)
    blockMesh.create_file()

@pytest.mark.skipif(check_foam_installation() == False,reason= "OF not installed in system")
def test_runDecomposePar():
    """
    Runs the decomposePar checker
    """
    fdecomposepar= of_test_dir/"system"/"decomposeParDict"


    with open(str(fdecomposepar),"r") as f:
        dict_str = f.read()

    checker = run.CheckDecomposeParDict(dict_str)
    
    test_tuple = checker.check_dict()
    print(test_tuple[1])
    assert 1 == test_tuple[0]

