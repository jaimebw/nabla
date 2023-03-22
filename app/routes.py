from app import app,db
from datetime import date
from app.forms import *
from flask import  render_template,flash,redirect, url_for,request,make_response
from flask_login import current_user, login_required,login_user,logout_user
from app.models import *
from werkzeug.urls import url_parse
from app.pyfoam.run import CheckBlocMeshDict
from app.pyfoam.utils import check_foam_installation


@app.route('/')
@app.route('/index')
@login_required
def index():
    """
    Routes to the index template
    """
    if not check_foam_installation():
        app.logger.debug("Open Foam not installed")
        flash("WARNING: Open Foam is not installed in your system. Some functionalities won't be available")
    return render_template('index.html')


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
    files = OpenFoamData.query.filter_by(user_id = user.id).all()

    return render_template('user.html',user = user, files = files)



@app.route('/add_dict',methods = ['GET','POST'])
@login_required
def add_dict():
    """
    Routing for adding a new dictionary to the database

    PARAMETERS
    ---------
    username: username id of the logged person
    """
    form =  OpenFoamForm()
    if form.validate_on_submit():
        of_file = OpenFoamData(fname = form.fname.data,
                               date = date.today(),
                               dict_class = form.dict_class.data,
                               description = form.description.data,
                               fdata = request.files[form.fdata.name].read().decode("unicode_escape"))

        if check_foam_installation():
            of_file.validate(CheckBlocMeshDict(form.fdata.data).check_dict()[0])
        else:
            of_file.validate(False)
        of_file.set_userid(current_user.id)
        db.session.add(of_file)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('simulations.html',title = "Simulations",form = form)

@app.route('/download_dict',methods = ['POST'])
@login_required
def download_dict():
    """
    Route for downloading a dict file
    """
    id = request.form.get('id')
    app.logger.debug(f"Id of the dictionary that is downloaded:{id}")
    file = OpenFoamData.query.filter_by(id = id).first_or_404()
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
    file =  OpenFoamData.query.filter_by(id = del_id).first_or_404()
    db.session.delete(file)
    db.session.commit()
    user = User.query.filter_by(username = current_user.username).first_or_404()
    files = OpenFoamData.query.filter_by(user_id = current_user.get_id()).all()
    return render_template('user.html',user= user,files = files)


@app.route('/about')
def about():
    """
    Routes to the about page.

    TO-DO:
        * Add more info in the about page
        * add some cool images to make it work well
    """
    return render_template('about.html',)
