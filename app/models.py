from werkzeug.security import generate_password_hash,check_password_hash
from app import db,login
from flask_login import UserMixin



class User(UserMixin,db.Model):
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


class OpenFoamData(db.Model):
    """
    Class for the Open Foam data table that will input the User
    data into the database

    TO-DO: 
        * Add date when the dict is added
        * Add dict parse to see if the dict would work
    Parameters
    ----------

    id: unique id for the OF dictionary
    name: Custom name for the OF dictionary
    dict_class: tells what kind of dictionary it is, for example, blockMeshDict or systemDict
    description: Optional description of the dictionary
    dict_data: Actual dictionary that will be uploaded to the database

    

    """
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(64),index = True )
    dict_class = db.Column(db.String(64))
    description = db.Column(db.String(120),nullable = True)
    dict_data = db.Column(db.Text)
    
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def __repr__(self) -> str:
        return '<OpenFoamData {}>'.format(self.name)
    
    def set_userid(self,user_id):
        """
        Set the user id as the foregin key
        """
        self.user_id = user_id


#class Simulations(db.Model):
    

        

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
