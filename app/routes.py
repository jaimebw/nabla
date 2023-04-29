from app import app,db
import asyncio
from datetime import date
from flask import  render_template,flash,redirect, url_for,request,make_response
from flask_login import current_user, login_required,login_user,logout_user
from werkzeug.urls import url_parse
from app.pyfoam.utils import check_foam_installation
from app.models import *
from app.forms import *
from .utils import run_command,zip_dir
import json
import sys
# Submodule import
sys.path.append("app/foam_linter")
from foam_linter import FoamLinter



@app.route('/')
@app.route('/index')
@login_required
def index():
    """
    Routes to the index template
    """
    if not check_foam_installation():
        app.logger.debug("Open Foam not installed")
        flash("WARNING: Open Foam is not installed in your system. Some functionalities won't be available","info")
    sim_hist = SimulationHistoryData.query.filter_by(user_id = current_user.id).all()
    return render_template('index.html',sim_hist = sim_hist)

@app.route('/about')
def about():
    """
    Routes to the about page.

    TO-DO:
        * Add more info in the about page
        * add some cool images to make it work well
    """
    app.logger.debug("About pagge accesed")
    return render_template('about.html',)

@app.route('/login',methods = ['GET','POST'])
def login():
    """
    Routes to the loging template
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for('login'))
        login_user(user,remember= form.remember_me.data)
        app.logger.debug(f"Loged user with id:{user}")
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(url_for('index')) # ojo, si usamos esto pilla funcion de routes en vez de la template
    return render_template('login.html',title = 'Sign in',form = form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register',methods = ['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username = form.username.data,email = form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("You have been registered")
        return redirect(url_for('login'))
    return render_template('register.html', title = 'Register',form = form)

@app.route('/user/<username>')
@login_required
def user(username):
    """
    Routing to the user page.

    PARAMETERS
    ----------

    username: username id of the logged person
    """
    user = User.query.filter_by(username = username).first_or_404()
    dict_files = OpenFoamDictData.query.filter_by(user_id = user.id).all()
    sim_files = OpenFoamSimData.query.filter_by(user_id = user.id).all()

    return render_template('user.html',user = user, sim_files = sim_files,
                           dict_files = dict_files)


@app.route('/add_dict',methods = ['POST'])
@login_required
def add_dict():
    """
    Routing for adding a new simulation to the dataset
    """
    dict_form =  OpenFoamDictForm()
    sim_form = OpenFoamSimForm()
    if dict_form.validate_on_submit():
        dict_file = OpenFoamDictData(fname = dict_form.fname.data,
                               date = date.today(),
                               dict_class = dict_form.dict_class.data,
                               description = dict_form.description.data,
                               fdata = request.files[dict_form.fdata.name].read().decode("unicode_escape"))
        linter = FoamLinter(dict_form.dict_class.data)
        dict_file.validate(linter.lint()[1])
        dict_file.set_userid(current_user.id)
        db.session.add(dict_file)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('simulations.html',title = "Simulations",
                           dict_form = dict_form, sim_form = sim_form)

@app.route('/add_sim',methods = ['POST'])
@login_required
def add_sim():
    """
    Routing for adding a new dictionary to the database


    TODO:
        * Add to the form to check the file so there are no errors.
    """
    dict_form =  OpenFoamDictForm()
    sim_form = OpenFoamSimForm()
    if sim_form.validate_on_submit():
        zipfile = request.files[sim_form.fdata.name]
        sim_file = OpenFoamSimData(fname = sim_form.fname.data,
                                   date  = date.today(),
                                   description = sim_form.description.data,
                                   fdata = zipfile.read())
        sim_file.set_userid(current_user.id)
        sim_file.set_dir_tree(zipfile)
        db.session.add(sim_file)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('simulations.html',title = "Simulations",
                           dict_form = dict_form, sim_form = sim_form)

@app.route('/simulations',methods = ['GET','POST'])
@login_required
def simulations():
    """
    Routing for the simulations page

    PARAMETERS
    ---------
    username: username id of the logged person
    """
    dict_form =  OpenFoamDictForm()
    sim_form = OpenFoamSimForm()
    return render_template('simulations.html',title = "Simulations",
                           dict_form = dict_form, sim_form = sim_form)

@app.route('/sim_page/<sim_id>',methods = ['GET','POST'])
@login_required
def run_sim_page(sim_id):
    """
    Routing for the simulation page

    PARAMETERS
    ----------
    sim_id: the simuation_id of the file
    """
    if not check_foam_installation():
        flash("WARNING: Open Foam is not installed in your system. Some functionalities won't be available","info")
    app.logger.debug(f"Id of simulaton to be run:{sim_id}")
    file = OpenFoamSimData.query.filter_by(id = sim_id).first_or_404()

    dir_tree = eval(file.dir_tree.decode('utf-8'))
    file.unzip()
    app.logger.debug(dir_tree)
    return render_template('simulation_run.html',file = file,
                           dir_tree = json.dumps(dir_tree))


@app.route('/run_sim',methods = ['GET','POST'])
@login_required
async def run_sim():
    """
    Routing for running the simualation on anothe thread

    """
    if not check_foam_installation():
        flash("The simulation couldnt be executed","error")
    sim_id = request.form.get('sim_id')
    sim_entrie = OpenFoamSimData.query.filter_by(id = sim_id).first_or_404()
    sim_hist= SimulationHistoryData(
            fname = sim_entrie.fname,
            sim_id = sim_id,
            user_id = sim_entrie.user_id
            )
    app.logger.debug(f"New simulation added to the history with id:{sim_hist.id}")
    app.logger.debug(f"Staring to run the simulation in another thread:{sim_id}")

    command = [
               f"cd {sim_id}/test_case/",
            "chmod +x ./Allrun",
            "./Allrun" ] 
    app.logger.debug(command)
    sim_output = await run_command(command)
    sim_results = await zip_dir(f"{sim_id}/test_case")

    sim_hist.add_results(sim_results)
    db.session.add(sim_hist)
    db.session.commit()
    

    app.logger.debug(f"Sim output:{sim_output}")

    #sim_hist = SimulationHistoryData.query.filter_by(user_id = current_user.id).all()
    return render_template('simulation_run.html',
                           file= sim_entrie,
                           dir_tree = json.dumps(eval(sim_entrie.dir_tree)),
                           sim_output = sim_output)

@app.route('/download_sim',methods = ['POST'])
@login_required
async def download_sim():
    """
    Route for downloading a dict file
    WIP
    """
    id = request.form.get('id')
    app.logger.debug(f"Id of the dictionary that is downloaded:{id}")
    file = OpenFoamSimData.query.filter_by(id = id).first_or_404()
    app.logger.debug(file.fname)
    response = make_response(file.fdata)
    response.headers.set('Content-Disposition', 'attachment', filename=f"{file.fname}.zip")
    return response

@app.route('/download_results',methods = ['POST'])
@login_required
async def download_sim_results():
    """
    Route for downloading a simulation result
    WIP
    """
    id = request.form.get('id')
    app.logger.debug(f"Id of the results that is downloaded:{id}")
    file = SimulationHistoryData.query.filter_by(id = id).first_or_404()
    response = make_response(file.results)
    response.headers.set('Content-Disposition', 'attachment', filename=f"{file.run_date}.zip")
    return response


@app.route('/delete_sim', methods=['POST'])
@login_required
def delete_sim():
    """
    Route for deleting dicts from the database
    WIP
    """
    del_id = request.form.get('id')
    app.logger.debug(f"Deleted dict with id:{id}")
    file =  OpenFoamSimData.query.filter_by(id = del_id).first_or_404()
    db.session.delete(file)
    db.session.commit()
    user = User.query.filter_by(username = current_user.username).first_or_404()

    sim_files = OpenFoamSimData.query.filter_by(user_id = current_user.get_id()).all()
    dict_files = OpenFoamDictData.query.filter_by(user_id = current_user.get_id()).all()

    return render_template('user.html',user= user,sim_files = sim_files
                           ,dict_files = dict_files)

@app.route('/download_dict',methods = ['POST'])
@login_required
async def download_dict():
    """
    Route for downloading a dict file
    """
    id = request.form.get('id')
    app.logger.debug(f"Id of the dictionary that is downloaded:{id}")
    file = OpenFoamDictData.query.filter_by(id = id).first_or_404()
    app.logger.debug(file.fdata)
    response = make_response(file.fdata)
    response.headers.set('Content-Disposition', 'attachment', filename=file.dict_class)
    return response


@app.route('/delete_dict', methods=['POST'])
@login_required
def delete_dict():
    """
    Route for deleting dicts from the database
    """
    del_id = request.form.get('id')
    app.logger.debug(f"Deleted dict with id:{id}")
    file =  OpenFoamDictData.query.filter_by(id = del_id).first_or_404()
    db.session.delete(file)
    db.session.commit()
    user = User.query.filter_by(username = current_user.username).first_or_404()
    files = OpenFoamDictData.query.filter_by(user_id = current_user.get_id()).all()
    sim_files = OpenFoamSimData.query.filter_by(user_id = current_user.get_id()).all()
    return render_template('user.html',user= user,sim_files = sim_files
                           ,dict_files = dict_files)

@app.route('/test',methods = ["GET","POST"])
def test():
    return render_template("test.html")

