from flask import render_template, request, Blueprint, redirect, current_app, flash, url_for
from flask_login import login_required, current_user
import pandas as pd
import os
from os import listdir
from os.path import isfile, join
import numpy as np
import secrets
import plotly
import plotly.express as px
from werkzeug.utils import secure_filename
from STATQ.program.forms import UploadFileForm, ProcesFileForm
from STATQ.program.utils import (parse_data, 
                                        plotly_hydro, plotly_kemi, plotly_season)
from STATQ import s3
import io
import boto3

program = Blueprint('program', __name__)

@program.route('/StatQ/dine-filer/', methods=['GET', 'POST'])
@login_required
def upload_file():
    s3_resource = boto3.resource('s3')
    my_bucket = s3_resource.Bucket(os.environ.get('S3_BUCKET_NAME'))
    files = my_bucket.objects.filter(Prefix=str(current_user.username)+"/")
    filenames=[]
    for objects in files:
        obj = objects.key
        obj = obj.removeprefix(str(current_user.username)+'/')
        filenames.append(obj)
    user_folder = current_user.username+'/'

    if request.files:
        file = request.files['myFile']
        if file.filename == "":
            flash("Filen skal have et navn", 'danger')
            return redirect(request.url)

        if not allowed_filetype(file.filename):
            flash("Filtype er ikke understøttet", 'danger')
            return redirect(request.url)

        else:
            filename = secure_filename(file.filename)
        try:
            s3.upload_fileobj(file, 'statq-bucket', str(user_folder)+str(filename))
        except Exception as e:
            flash("Noget gik galt: "+e, 'danger')
        #s3_resource.meta.client.upload_file(str(file.filename), 'statq-bucket',str(user_folder)+str(filename))
        flash("Fil er uploadet", 'success')
        return redirect(url_for('program.your_files'))

    return render_template('program/proces_file.html', files=files, filenames=filenames)

@program.route('/StatQ/dine-filer/', methods=['GET', 'POST'])
@login_required
def your_files():
    s3_resource = boto3.resource('s3')
    my_bucket = s3_resource.Bucket(os.environ.get('S3_BUCKET_NAME'))
    files = my_bucket.objects.filter(Prefix=str(current_user.username)+"/")
    return render_template('program/proces_file.html', files=files, filepaths=filepaths)


@program.route('/StatQ/dine-filer/<string:filename>/slet-fil')
@login_required
def delete_file(filename):
    s3.delete_object(Bucket=os.environ.get('S3_BUCKET_NAME'), Key=str(current_user.username)+'/'+str(filename))
    flash(str(filename)+" er blevet slettet", 'success')
    return redirect(url_for('program.your_files'))   

@program.route('/StatQ/dine-filer/<string:filename>', methods=['GET', 'POST'])
@login_required
def proces_file(filename):
    form=ProcesFileForm
    file = s3.get_object(Bucket=os.environ.get('S3_BUCKET_NAME'), Key=str(current_user.username)+'/'+str(filename))
    df = parse_data(io.BytesIO(file['Body'].read()))
    if isinstance(df, str):
        flash(df, 'danger')
        return redirect(url_for('program.your_files'))
    sub_df = df.head(1)
    sub_df.pop("Resultat")
    #parameters = str(set(df['Parameter']))
    #sub_df['Parameter'] = parameters
    headings = list(sub_df.columns)
    information = list(sub_df.iloc[0])

    infolist = zip(headings, information)
    string_test = str(df['Parameter'].iloc[0])
    cond1 = 'Vandføring'
    cond2 = 'Vandstand'
    if string_test == cond1 or string_test == cond2:
        graphJSONseason = plotly_season(df)
        graphJSONraw = plotly_hydro(df)
    elif string_test != cond1 and string_test != cond2:
        graphJSONseason = None
        graphJSONraw = plotly_kemi(df)

    return render_template('program/file_results.html', graphJSONraw = graphJSONraw, graphJSONseason = graphJSONseason, form=form, infolist=infolist, filename = filename)


@program.route('/StatQ/kom-godt-i-gang')
def kom_godt_i_gang():
    return render_template('program/kom-godt-i-gang.html')

@program.route('/StatQ/hjaelp')
@login_required
def help():
    return render_template('program/help.html')

def allowed_filetype(filename):
    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in current_app.config["ALLOWED_FILE_EXTENSIONS"]:
        return True

    else:
        return False