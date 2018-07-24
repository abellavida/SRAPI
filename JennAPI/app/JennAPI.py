
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
from forms import APIKeyForm, GetCandForm
import flask_excel as excel


client = MongoClient()
db = client.srapi
##jpvals = db.job_properties
##dbjoint = client.joint_table

app = Flask(__name__)
app.config['SECRET_KEY'] = "quenoledigaquenolecuenten"
title = "Jenn API"
heading = "Jenn API"


@app.route('/')
@app.route('/index')
def index():
    SR_Delete()
    return render_template('index.html', title='Jenn''s API Work in Progress')

@app.route('/actions', methods=['GET', 'POST'])
def actions():
    form = APIKeyForm()

    if request.method == 'POST':
        apiKey=request.form['apiKey']
        SR_Get(apiKey)
        return redirect('/jpv_new')

    return render_template('actions.html', title='Action Page', form=form)

@app.route('/jobpropvalues')
def get_jpv():
    jpvs= db.job_prop_values.distinct('content')
    return render_template('jpvs.html', title='Job Property Values', jpvs=jpvs)

@app.route('/jprops')
def jprops():
    jprops = db.job_properties.distinct('content')
##        j=json.dumps(jprops)
    return render_template('job_properties.html', title='Job Properties', jprops=jprops)

@app.route('/jpv_id')
def jpv_id():
    jpvs= db.job_prop_values.distinct('content')
    return render_template('jpvs_2.html', title='Job Property Values', jpvs=jpvs)

@app.route('/jpv_new')
def jpv_new():
    jpnew= db.jpvs_new.find()
    return render_template('jpvs_new.html', title='JPV New DB', jpnew=jpnew)
##    return jpnew


@app.route('/jpv_json')
def jpv_json():
    jpvs = db.job_prop_values.distinct('content')
##    jpvs = db.jpv_new.find()
    j = json.dumps(jpvs)
    return j

@app.route("/export", methods=['GET'])
def doexport():
    jpnew= db.jpvs_new.find()
    j = []
    for i in jpnew:
        j.append(i)
    return excel.make_response_from_records(j,  ['jobprop_label', 'label'], "xlsx")

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5555, debug=True)
##    app.run()
