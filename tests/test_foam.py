from app.pyfoam import foam


domain_dict = {
    "xMax":100,
    "zMax": 50,
        } 


def test_baseFoam():
    test_list = ["xMax","zMax"]
    basefoam = foam.BaseFoam()
    assert basefoam.check_dictkey_existance(test_list,domain_dict) == True



def test_blockMesh():
    # TO-DO: added testing and utils for delentin the files after
    # creation
    blockMesh = foam.BlockMesh()
    blockMesh.set_domain(domain_dict)
    blockMesh.create_file()
