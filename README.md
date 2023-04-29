## CS 588 Capstone project

## Docker notes
Actually, it is better to use:
* ```docker build -t open-foam .```: this will build following the Dockerfile
* ```docker run -it open-foam``` : this will rund the commands
To build the container: ```docker compose build```
To run the app: ```docker compose up```

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
