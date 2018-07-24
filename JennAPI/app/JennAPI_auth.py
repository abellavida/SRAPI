from flask_login import current_user, login_user, logout_user, login_required
from pymongo import MongoClient # Database connector
from bson.objectid import ObjectId # For ObjectId to work
from bson import Timestamp
import json
from bson.json_util import dumps
from datetime import datetime, timedelta
from SRDataActions import SR_Get, SR_Delete
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash # For flask implementation
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from forms import APIKeyForm, GetCandForm, LoginForm, RegistrationForm, EditProfileForm
import flask_excel as excel


client = MongoClient()
db = client.srapi
##jpvals = db.job_properties
##dbjoint = client.joint_table

app = Flask(__name__)
app.config['SECRET_KEY'] = "quenoledigaquenolecuenten"
title = "Jenn API"
heading = "Jenn API"

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))



@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = db.user.find_one(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != "":
			next_page = url_for('index')
		return redirect(next_page)
	return render_template('login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		db.user.insert_one(user)

		flash('Congratulations, you are now a registered user!')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
	user = db.user.find_one(username=username).first_or_404()
	return render_template('user.html', user=user, posts=posts)


@app.route('/edit_profile', methods=['GET','POST'])
@login_required
def edit_profile():
	form = EditProfileForm(current_user.username)
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.about_me = form.about_me.data
		db.user.update_one(current_user)
		flash('Your Changes have been saved')
		return redirect(url_for('edit_profile'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.about_me.data = current_user.about_me
	return render_template('edit_profile.html', title='Edit Profile', form=form)



@app.route('/')
@app.route('/index')
@login_required
def index():
    SR_Delete()
    return render_template('index.html', title='Jenn''s API Work in Progress')

@app.route('/actions', methods=['GET', 'POST'])
@login_required
def actions():
    form = APIKeyForm()

    if request.method == 'POST':
        apiKey=request.form['apiKey']
        SR_Get(apiKey)
        return redirect('/jpv_new')

    return render_template('actions.html', title='Action Page', form=form)

@app.route('/jobpropvalues')
@login_required
def get_jpv():
    jpvs= db.job_prop_values.distinct('content')
    return render_template('jpvs.html', title='Job Property Values', jpvs=jpvs)

@app.route('/jprops')
@login_required
def jprops():
    jprops = db.job_properties.distinct('content')
##        j=json.dumps(jprops)
    return render_template('job_properties.html', title='Job Properties', jprops=jprops)

@app.route('/jpv_id')
@login_required
def jpv_id():
    jpvs= db.job_prop_values.distinct('content')
    return render_template('jpvs_2.html', title='Job Property Values', jpvs=jpvs)

@app.route('/jpv_new')
@login_required
def jpv_new():
    jpnew= db.jpvs_new.find()
    return render_template('jpvs_new.html', title='JPV New DB', jpnew=jpnew)
##    return jpnew


@app.route('/jpv_json')
@login_required
def jpv_json():
    jpvs = db.job_prop_values.distinct('content')
##    jpvs = db.jpv_new.find()
    j = json.dumps(jpvs)
    return j

@app.route("/export", methods=['GET'])
@login_required
def doexport():
    jpnew= db.jpvs_new.find()
    j = []
    for i in jpnew:
        j.append(i)
    return excel.make_response_from_records(j,  ['jobprop_label', 'label'], "xlsx")

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5555, debug=True)
##    app.run()
