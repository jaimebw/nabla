from zipfile import  ZipFile
import json
from app import app, db
import asyncio
from datetime import date
from datetime import datetime
from flask import jsonify, render_template, flash, redirect, url_for, request, make_response
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse
from app.pyfoam.utils import check_foam_installation
from app.models import *
from app.forms import *
from .utils import extract_file_name, is_systemfile, run_command
import json
import sys
from io import BytesIO

# Submodule import
sys.path.append("app/foam_linter")
from foam_linter import FoamLinter


@app.route("/")
@app.route("/index")
@login_required
def index():
    """
    Routes to the index template
    """
    if not check_foam_installation():
        app.logger.debug("Open Foam not installed")
        flash(
            "WARNING: Open Foam is not installed in your system. Some functionalities won't be available",
            "info",
        )
    sim_hist = SimulationHistoryData.query.filter_by(user_id=current_user.id).all()
    return render_template("index.html", sim_hist=sim_hist)


@app.route("/about")
def about():
    """
    Routes to the about page.

    """
    app.logger.debug("About pagge accesed")
    return render_template(
        "about.html",
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Routes to the loging template
    """
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        app.logger.debug(f"Loged user with id:{user}")
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(
            url_for("index")
        )  # ojo, si usamos esto pilla funcion de routes en vez de la template
    return render_template("login.html", title="Sign in", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("You have been registered")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/user/<username>")
@login_required
def user(username):
    """
    Routing to the user page.

    PARAMETERS
    ----------

    username: username id of the logged person
    """
    user = User.query.filter_by(username=username).first_or_404()
    sim_files = OpenFoamSimData.query.filter_by(user_id=user.id).all()

    return render_template(
        "user.html", user=user, sim_files=sim_files,
    )


@app.route("/add_sim", methods=["POST"])
@login_required
def add_sim():
    """
    Routing for adding a new dictionary to the database


    TODO:
        * Add to the form to check the file so there are no errors.
        * Add a way to check the file and see if it is valid.(fucntion from utils(check_systemfile))
    """
    sim_form = OpenFoamSimForm()
    if sim_form.validate_on_submit():
        zipdata = request.files[sim_form.fdata.name]
        sim = OpenFoamSimData(
            fname=sim_form.fname.data,
            date=date.today(),
            description=sim_form.description.data,
        )
        sim.set_userid(current_user.id)
        db.session.add(sim)
        db.session.commit() # Need to commit to generate id
        zipdata = ZipFile(BytesIO(zipdata.getvalue()))
        for file in zipdata.infolist():
            app.logger.debug(f"File to unzip: {file.filename}")

            if (not file.is_dir())and not is_systemfile(file.filename):
                simfile = SimFile(
                        fname = extract_file_name(file.filename),# Error raro diciendo que esto no es un zip file
                        pathdata = file.filename,
                        )
                simfile_hist = SimFileHistory(
                        fdata = zipdata.read(file.filename),
                        comment = "Initial commit",
                        )
                simfile.set_simid(sim.id)
                db.session.add(simfile)
                db.session.commit()
                simfile_hist.set_simfileid(simfile.id)
                db.session.add(simfile_hist)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template(
        "simulations.html", title="Simulations", sim_form=sim_form
    )

@app.route("/edit_simfile/<simfile_id>", methods=["GET"])
def edit_simfile(simfile_id):
    app.logger.debug(f"Simfile id: {simfile_id}")

    sim_file = SimFileHistory.query.filter_by(simfile_id=simfile_id).order_by(SimFileHistory.mod_date.desc()).first_or_404()
    app.logger.debug(sim_file.fdata)
    sim_file_details = SimFile.query.filter_by(id=simfile_id).first_or_404()
    sim_file = sim_file.as_dict()
    sim_file_details = sim_file_details.as_dict()
    
   

    return render_template("edit_simfile.html", file=json.dumps(sim_file),\
                           file_details = sim_file_details)

@app.route("/update_simfile", methods=["POST"])
def update_simfile():
    data = request.json
    data['fdata'] = data['fdata'].encode('utf-8')
    app.logger.debug("update_simfile POST request")
    app.logger.debug(data)
    new_sim_file = SimFileHistory(
        fdata=data["fdata"], comment=data["comment"], simfile_id=data["simfile_id"])
    db.session.add(new_sim_file)
    db.session.commit()
    return jsonify({"status": "ok"})





@app.route("/add_simulations", methods=["GET", "POST"])
@login_required
def add_simulations_page():
    """
    Routing for the simulations page

    PARAMETERS
    ---------
    """
    sim_form = OpenFoamSimForm()
    return render_template(
        "simulations.html", title="Simulations",  sim_form=sim_form
    )


@app.route("/sim_page/<sim_id>", methods=["GET", "POST"])
@login_required
def sim_page(sim_id):
    """
    Routing for running the simulations 
 
    PARAMETERS
    ----------
    sim_id: the simuation_id of the file
    """
    if not check_foam_installation():
        flash(
            "WARNING: Open Foam is not installed in your system. Some functionalities won't be available",
            "info",
        )
    app.logger.debug(f"Id of simulaton to be run:{sim_id}")
    sim = OpenFoamSimData.query.filter_by(id=sim_id).first_or_404()
    files = SimFile.query.filter_by(sim_id=sim_id).all()

    file_list = [{"id":file.id, "fname":file.fname, "pathdata":file.pathdata,"date":file.date.strftime("%m/%d/%Y, %H:%M:%S")} for file in files]
    app.logger.debug(file_list)

    return render_template(
        "simulation_run.html", files = jsonify(file_list).json ,sim = sim
    )

@app.route("/run_sim", methods=["GET", "POST"])
@login_required
async def run_sim():
    """
    Routing for running the simualation on anothe thread

    NOTE:
        Deprecated. Need to be done in a different way.

    """
    if not check_foam_installation():
        flash("The simulation couldnt be executed", "error")
    sim_id = request.form.get("sim_id")
    sim_entrie = OpenFoamSimData.query.filter_by(id=sim_id).first_or_404()
    sim_hist = SimulationHistoryData(
        fname=sim_entrie.fname, sim_id=sim_id, user_id=sim_entrie.user_id
    )
    app.logger.debug(f"New simulation added to the history with id:{sim_hist.id}")
    app.logger.debug(f"Staring to run the simulation in another thread:{sim_id}")

    command = [f"cd {sim_id}/test_case/", "chmod +x ./Allrun", "./Allrun"]
    app.logger.debug(command)
    sim_output = await run_command(command)
    sim_results = await zip_dir(f"{sim_id}/test_case")

    sim_hist.add_results(sim_results)
    db.session.add(sim_hist)
    db.session.commit()

    app.logger.debug(f"Sim output:{sim_output}")

    return render_template(
        "simulation_run.html",
        file=sim_entrie,
        dir_tree=json.dumps(eval(sim_entrie.dir_tree)),
        sim_output=sim_output,
    )


@app.route("/download_sim", methods=["POST"])
@login_required
async def download_sim():
    """
    Route for downloading a dict file
    NOTE:
        This route does not work

    TODO:
        * Upgrade to the new models, use the SimFile model

    """
    id = request.form.get("id")
    app.logger.debug(f"Id of the dictionary that is downloaded:{id}")
    file = OpenFoamSimData.query.filter_by(id=id).first_or_404()
    app.logger.debug(file.fname)
    response = make_response(file.fdata)
    response.headers.set(
        "Content-Disposition", "attachment", filename=f"{file.fname}.zip"
    )
    return response


@app.route("/download_results", methods=["POST"])
@login_required
async def download_sim_results():
    """
    Route for downloading a simulation result
    """
    id = request.form.get("id")
    app.logger.debug(f"Id of the results that is downloaded:{id}")
    file = SimulationHistoryData.query.filter_by(id=id).first_or_404()
    response = make_response(file.results)
    response.headers.set(
        "Content-Disposition", "attachment", filename=f"{file.run_date}.zip"
    )
    return response


@app.route("/delete_sim_results", methods=["POST"])
@login_required
def delete_sim_results():
    """
    Route for deleting simulation results from the database
    """
    del_id = request.form.get("id")
    app.logger.debug(f"Deleted simulation results with id:{id}")
    file = SimulationHistoryData.query.filter_by(id=del_id).first_or_404()
    db.session.delete(file)
    db.session.commit()
    sim_hist = SimulationHistoryData.query.filter_by(user_id=current_user.id).all()
    return render_template("index.html", sim_hist=sim_hist)


@app.route("/delete_sim",methods=["POST"])
@login_required
def delete_sim():
    """
    Route for deleting simulations from the database
    WIP
    """
    del_id = request.form.get("id")
    app.logger.debug(f"Deleted simulations with id:{id}")
    file = OpenFoamSimData.query.filter_by(id=del_id).first_or_404()
    db.session.delete(file)
    db.session.commit()
    return redirect(url_for("user",username = current_user.username))




