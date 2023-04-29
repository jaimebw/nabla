from werkzeug.security import generate_password_hash,check_password_hash
from app import db,login
from flask_login import UserMixin
from app.utils import get_zip_directory_structure
import zipfile
import io
import os
import datetime


class User(UserMixin,db.Model):
    """
    User mode for the db.

    TO-DO:
        * Add name, lastname and affilations(student, proffesor, professional)
    """
    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String(64),index = True, unique = True)
    email = db.Column(db.String(120), index = True, unique = True)
    password_hash = db.Column(db.String(128))

    def __repr__(self) -> str:
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class OpenFoamDictData(db.Model):
    """
    Class for the Open Foam data table that will input the User
    data into the database

    TO-DO: 
        * Add dict parse to see if the dict would work - Implemented in routes
        need to add method here
    Parameters
    ----------

    id: unique id for the OF dictionary
    name: Custom name for the OF dictionary
    date: Date in which the simulation is added
    dict_class: tells what kind of dictionary it is, for example, blockMeshDict or systemDict
    description: Optional description of the dictionary
    dict_data: Actual dictionary that will be uploaded to the database
    is_validated: Validate thats the file works in Open Foam


    """
    id = db.Column(db.Integer,primary_key = True)
    fname = db.Column(db.String(64),index = True )
    date = db.Column(db.Date)
    dict_class = db.Column(db.String(64))
    description = db.Column(db.String(120),nullable = True)
    fdata = db.Column(db.Text)
    is_validated = db.Column(db.Boolean)
    
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def __repr__(self) -> str:
        return '<OpenFoamDict {}>'.format(self.name)
    def validate(self,is_validated):
        """
        Set if the dictionary data is valid
        """
        self.is_validated = is_validated
    def set_userid(self,user_id):
        """
        Set the user id as the foregin key
        """
        self.user_id = user_id

class OpenFoamSimData(db.Model):
    """
    Class for the Open Foam simulations tables that will input the User
    data into the database

    Parameters
    ----------

    id: unique id for the OF simulation 
    name: Custom name for the OF simulation
    date: Date in which the simulation is added
    description: Optional description of the dictionary
    fdata: Binary data of the simulation, must a be .zip file
    dir_tree: Directory tree of the simulation 
    

    """
    id = db.Column(db.Integer,primary_key = True)
    fname = db.Column(db.String(64),index = True )
    date = db.Column(db.Date)
    description = db.Column(db.String(120),nullable = True)
    fdata = db.Column(db.LargeBinary)
    dir_tree= db.Column(db.LargeBinary)


    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    sim_history = db.relationship('SimulationHistoryData', backref='sim', cascade='all, delete-orphan', passive_deletes=True)

    def __repr__(self) -> str:
        return '<OpenFoamSim {}>'.format(self.name)

    def set_dir_tree(self,zip_file) -> None:
        """
        """
        self.dir_tree= get_zip_directory_structure(zip_file).encode('utf-8')

    def set_userid(self,user_id)->None:
        """
        Set the user id as the foregin key
        """
        self.user_id = user_id

    def unzip(self):
        """
        Extracts the zip file in a directory with the same id as the sim


        TODO:
            * Add option to add more dir inside the dir file so 
            you can run multiple simulatons out of only one
        """
        dir_name = str(self.id)
        dir_path = os.path.join(os.getcwd(), dir_name)
        os.makedirs(dir_path, exist_ok=True)

        zip_file = io.BytesIO(self.fdata)
        with zipfile.ZipFile(zip_file, "r") as zf:
            zf.extractall(dir_path)

class SimulationHistoryData(db.Model):
    """
    Contains the simulation history for the user
    """
    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    fname = db.Column(db.String(64))
    run_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    results = db.Column(db.LargeBinary)

    # Camel case changes to _ in sqlalchemy
    sim_id = db.Column(db.Integer, db.ForeignKey('open_foam_sim_data.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))

    def __repr__(self) -> str:
        return '<SimulationHistoryData {} {}>'.format(self.sim_id, self.run_date)

    def add_results(self, results):
        self.results = results




@login.user_loader
def load_user(id):
    return User.query.get(int(id))
