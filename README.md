## CS 588 Capstone project: NABLA

## How to build and run

The reccomended setup is using Docker as it will install OpenFoam, and Python in the vm.
It is possible to run NABLA just with Python3 and Flask

### Docker(reccomended)
1. Install Docker and open the terminal
2. Run ```make build```
3. Enjoy NABLA :)

### Python3
1. Install Python in your system
2. Open the terminal and run:
```bash
pip install -r requirements.txt
flask run
```

You might need to create a virtualenv.



## Db notes
To modify the sqlite database, you should use the Flask shell:
```bash
flask shell
```
### Adding entries from the flask shell
And the run the next Python code:
```python3
from app.model import *
whatever_opp
db.session.commit()
```

### Migrating the database
You should use the next command after making any changes on the ```models.py``` file.
```bash
flask db migrate -m "Your comment for the migration"
flask db upgrade
```
