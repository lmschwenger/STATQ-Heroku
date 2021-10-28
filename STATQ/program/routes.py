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
program = Blueprint('program', __name__)
from STATQ import s3
import boto3


# @program.route('/StatQ/dine-filer/', methods=['GET', 'POST'])
# @login_required
# def upload_file():
#     datakilder = ['Vandportalen', 'Oda for alle', 'Danmarks Miljøportal']
#     user_path = current_app.root_path+'/static/files/'+current_user.username+'/'
#     files = [f for f in listdir(user_path) if isfile(join(user_path, f))]
#     filepaths = [(user_path+f) for f in listdir(user_path) if isfile(join(user_path+'/', f))]
#     if request.files:
#         file = request.files['myFile']
#         if file.filename == "":
#             flash("Filen skal have et navn", 'danger')
#             return redirect(request.url)

#         if not allowed_filetype(file.filename):
#             flash("Filtype er ikke understøttet", 'danger')
#             return redirect(request.url)

#         else:
#             filename = secure_filename(file.filename)

#         random_hex = secrets.token_hex(8)
#         _, f_ext = os.path.splitext(file.filename)
#         file_fn = random_hex + f_ext
#         user_path = current_app.root_path+'/static/files/'+current_user.username+'/'
#         if os.path.exists(user_path):
#             file_path = os.path.join(user_path, filename)
#             file.save(file_path)
#         else:
#             os.mkdir(user_path)
#             file_path = os.path.join(user_path, filename)
#             file.save(file_path)

#         flash("Fil er uploadet", 'success')
#         files = [f for f in listdir(user_path) if isfile(join(user_path, f))]
#         filepaths = [(user_path+f) for f in listdir(user_path) if isfile(join(user_path+'/', f))]
#         return redirect(url_for('program.your_files'))

#     return render_template('program/proces_file.html', datakilder=datakilder, files=files)

@program.route('/StatQ/dine-filer/', methods=['GET', 'POST'])
@login_required
def upload_file():
    # s3_resource = boto3.resource('s3')
    # my_bucket = s3_resource.Bucket(os.environ.get('S3_BUCKET_NAME'))
    # files = my_bucket.objects.filter(Prefix=str(current_user.username)+"/")

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

    return render_template('program/proces_file.html', files=files)
@program.route('/StatQ/dine-filer/', methods=['GET', 'POST'])
@login_required
def your_files():
    s3_resource = boto3.resource('s3')
    my_bucket = s3_resource.Bucket(os.environ.get('S3_BUCKET_NAME'))
    files = my_bucket.objects.filter(Prefix=str(current_user.username)+"/")
    return render_template('program/proces_file.html', files=files, filepaths=filepaths)

@program.route('/StatQ/dine-filer/', methods=['GET', 'POST'])
@login_required
def your_files():
    current_user.username+'/'
    if not os.path.exists(user_path):
        os.mkdir(user_path)        
    files = [f for f in listdir(user_path) if isfile(join(user_path, f))]
    filepaths = [(user_path+f) for f in listdir(user_path) if isfile(join(user_path+'/', f))]
    return render_template('program/proces_file.html', files=files, filepaths=filepaths)




@program.route('/StatQ/dine-filer/<string:filename>/slet-fil')
@login_required
def delete_file(filename):
    filepath = current_app.root_path+'/static/files/'+current_user.username+'/'+filename
    #filepath=os.path.join(user_path,filename)
    os.remove(filepath)
    flash(str(filename)+" er blevet slettet", 'success')
    return redirect(url_for('program.your_files'))   

@program.route('/StatQ/dine-filer/<string:filename>', methods=['GET', 'POST'])
@login_required
def proces_file(filename):
    form=ProcesFileForm
    s3_resource = boto3.resource('s3')
    my_bucket = s3_resource.Bucket(os.environ.get('S3_BUCKET_NAME'))
    file = my_bucket.objects.filter(Prefix=str(current_user.username)+"/"+str(filename))
    # if os.path.getsize(file) == 0:
    #     flash('Filen ser ud til at være tom (Fejlkode 0)', 'danger')
    #     return redirect(url_for('program.your_files'))
    df = parse_data(file)
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
@login_required
def kom_godt_i_gang():
    return render_template('program/kom-godt-i-gang.html')

@program.route('/StatQ/hjaelp')
@login_required
def help():
    return render_template('program/help.html')


@program.route('/StatQ/plot', methods=['GET', 'POST'])
def watch_plot():
    plotstr = plot_rawdata([1,2,3],[5,10,15])
    return plotstr


def allowed_filetype(filename):
    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in current_app.config["ALLOWED_FILE_EXTENSIONS"]:
        return True

    else:
        return False