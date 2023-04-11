from werkzeug.security import generate_password_hash,check_password_hash
from app import db,login
from flask_login import UserMixin



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
    Class for the Open Foam data table that will input the User
    data into the database

    Parameters
    ----------

    id: unique id for the OF dictionary
    name: Custom name for the OF dictionary
    date: Date in which the simulation is added
    description: Optional description of the dictionary

    

    """
    id = db.Column(db.Integer,primary_key = True)
    fname = db.Column(db.String(64),index = True )
    date = db.Column(db.Date)
    description = db.Column(db.String(120),nullable = True)
    fdata = db.Column(db.LargeBinary)
    
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def __repr__(self) -> str:
        return '<OpenFoamSim {}>'.format(self.name)
    def validate(self):
        """
        Validate the file(needs to be .zip file)
        """
        pass
    def get_files(self) -> str:
        """
        Uncompress the simulation file
        """
        pass
    def set_userid(self,user_id):
        """
        Set the user id as the foregin key
        """
        self.user_id = user_id


    

        

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
