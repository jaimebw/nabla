## CS 588 Capstone project: NABLA 

This repo contains must of the work for NABLA. The OpenFoam linter can be found [here](https://github.com/jaimebw/foam_linter/tree/main).

## How to run and build

You will need Docker in your system to be able to get the full functionalities. Yet, it is possible to run without on your system(you only need Python 3)

### Docker(Reccomended)

1. Install Docker
2. Run ```make build```

Enjoy NABLA :)

### Python
1. Install Python
2. Create a virtualen
3. Install requirements
4. Run flask

```bash
virtualvenv venv
source venv/bin/activate
pip install -r requirements.txt
flask run 
```

All this has been tested on a Macbook Pro 2019 Intel Core i7 and a Lenovo Thinkpad with Ubunto and Windows 11.

## Other notes
### Db notes

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
