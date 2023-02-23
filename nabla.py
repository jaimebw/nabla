from app import app,db
from app.models import User, OpenFoamData

@app.shell_context_processor
def make_shell_context():
    return {'db':db,'User':User,'Open Foam Data':OpenFoamData}

if __name__ == "__main__":
        app.run(debug = True, host = '0.0.0.0')
