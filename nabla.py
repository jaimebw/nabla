from app import app,db
from app.models import *

@app.shell_context_processor
def make_shell_context():
    return {'db':db,'User':User,'Open Foam Data':OpenFoamDictData}

if __name__ == "__main__":
        app.run(debug = True, host = '0.0.0.0')
