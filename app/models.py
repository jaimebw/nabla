from werkzeug.security import generate_password_hash, check_password_hash
from dataclasses import dataclass
from app import db, login
from flask_login import UserMixin
import uuid
import datetime


class User(UserMixin, db.Model):
    """
    User model for the db.

    Parameters
    ----------
    id: unique id for the user
    username: username for the user
    email: user's email address 
    password_hash: hash of the password

    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self) -> str:
        return "<User {}>".format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


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

    id = db.Column(db.Integer, primary_key = True ,default=lambda: uuid.uuid4().int >> (128 - 32), unique=True)
    fname = db.Column(db.String(64), index=True)
    date = db.Column(db.Date)
    description = db.Column(db.String(120), nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"))

    sim_file = db.relationship(
        "SimFile",
        backref="parent_sim",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return "<OpenFoamSim {}>".format(self.name)


    def set_userid(self, user_id) -> None:
        """
        Set the user id as the foregin key
        """
        self.user_id = user_id

@dataclass
class SimFile(db.Model):
    """
    Contains the files for the simulation.
    """
    id: int
    fname: str
    date: str
    pathdata: str

    sim_id: int
    
    id = db.Column(db.Integer, primary_key = True ,default=lambda: uuid.uuid4().int >> (128 - 32), unique=True)
    fname = db.Column(db.String(64))
    date = db.Column(db.Date,default=datetime.datetime.utcnow)
    pathdata = db.Column(db.String(120), nullable=True)

    sim_id = db.Column(db.Integer, db.ForeignKey("open_foam_sim_data.id", 
                                                 ondelete="CASCADE"))
    sim_file_histories = db.relationship(
        "SimFileHistory",
        backref="parent_file",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return "<SimFile: {} SimID: {}>".format(self.fname,self.sim_id)

    def set_simid(self,sim_id):
        self.sim_id = sim_id
    def as_dict(self):
        return {
                "id": int(self.id),
                "fname": self.fname,
                "date": self.date.strftime("%Y-%m-%d"),
                "pathdata": self.pathdata,
                "sim_id": int(self.sim_id),
                }

@dataclass
class SimFileHistory(db.Model):
    """
    Contains the history of the files for the user.

    """
    id: int
    mod_date: str
    fdata: bytes
    comment: str

    simfile_id: int

    id = db.Column(db.Integer, primary_key = True ,default=lambda: uuid.uuid4().int >> (128 - 32), unique=True)
    mod_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    fdata = db.Column(db.LargeBinary)
    comment = db.Column(db.String(120), nullable=True)


    simfile_id = db.Column(db.Integer, db.ForeignKey("sim_file.id", ondelete="CASCADE"))




    def set_simfileid(self,simfile_id):
        self.simfile_id=simfile_id 

    def as_dict(self):
        return {
                "id": int(self.id),
                "mod_date": self.mod_date.strftime("%Y-%m-%d"),
                "comment": self.comment,
                "simfile_id": int(self.simfile_id),
                "fdata": self.fdata.decode("utf-8"),
                }

class SimulationHistoryData(db.Model):
    """
    #Contains the simulation history for the user

    #TODO:
    #    Change fuking name to something like SimulationREsults

    Parameters
    ----------

    id: unique id for the OF simulation
    fname: Custom name for the OF simulation
    run_date: Date in which the simulation is executed 
    results: results of the simulation

    sim_id: unique id of the simulation
    user_id: user id of the user that the simulation belogns to
"""

    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    fname = db.Column(db.String(64))
    run_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    results = db.Column(db.LargeBinary)

    # Camel case changes to _ in sqlalchemy
    sim_id = db.Column(
        db.Integer, db.ForeignKey("open_foam_sim_data.id", ondelete="CASCADE")
    )
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"))

    def __repr__(self) -> str:
        return "<SimulationHistoryData {} {}>".format(self.sim_id, self.run_date)

    def add_results(self, results):
        self.results = results


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
